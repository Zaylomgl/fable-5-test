/**
 * StackAlert — ingestion worker (SKELETON, semaine 4 de la roadmap).
 *
 * Cron (toutes les 6h) :
 *   1. NVD  — CVE modifiées depuis le dernier passage (sync incrémental)
 *   2. KEV  — catalogue CISA des vulnérabilités exploitées (JSON complet, petit)
 *   3. EPSS — scores pour les CVE nouvellement vues (API FIRST, par lots)
 *
 * Contrainte free tier : ~10 ms CPU / invocation sur Workers Free (l'attente
 * réseau ne compte pas, le parsing JSON si). D'où : petites pages NVD et un
 * lot par invocation. PLAN B si la limite CPU bloque : déplacer ce même code
 * dans un cron GitHub Actions (2 000 min/mois gratuites en privé) qui écrit
 * dans D1 via l'API HTTP Cloudflare — la logique reste identique.
 *
 * TODO avant prod : vérifier les limites exactes de l'API EPSS (taille des
 * lots), gérer la pagination NVD > 1 page, retry/backoff sur 503 NVD.
 */

import { runNotify, resendTransport } from "./notify.js";
import { matchStack } from "./match.js";
import { sortForDigest } from "./digest.js";

const NVD_API = "https://services.nvd.nist.gov/rest/json/cves/2.0";
const KEV_URL =
  "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json";
const EPSS_API = "https://api.first.org/data/v1/epss";
const NVD_PAGE_SIZE = 200; // pages volontairement petites (budget CPU)
const NVD_MAX_PAGES_PER_RUN = 3; // ~18 s de wall time max (6 s entre pages)
const NVD_PAGE_DELAY_MS = 6000; // cadence recommandée par la NVD

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/** fetch avec retry/backoff — la NVD renvoie 403/503 en cas de surcharge. */
async function fetchWithRetry(url, opts = {}, tries = 3) {
  let res;
  for (let i = 0; i < tries; i++) {
    res = await fetch(url, opts);
    if (res.ok) return res;
    if (![403, 429, 503].includes(res.status) || i === tries - 1) break;
    await sleep(2000 * 2 ** i);
  }
  throw new Error(`${String(url).split("?")[0]} -> HTTP ${res.status}`);
}

export default {
  async scheduled(event, env, ctx) {
    ctx.waitUntil(runIngestion(env));
  },

  // GET /run : ingestion manuelle (test sans attendre le cron)
  // GET /api/matches?stack=vendor:product[:version],… : CVE matchées (30 j)
  async fetch(req, env) {
    const url = new URL(req.url);
    if (url.pathname === "/run") {
      await runIngestion(env);
      return new Response("ingestion done\n");
    }
    if (url.pathname === "/api/matches") {
      return apiMatches(url, env);
    }
    return new Response("stackalert-ingest\n");
  },
};

async function runIngestion(env) {
  const kevIds = await syncKev(env);
  const newCveIds = await syncNvd(env);
  await syncEpss(env, newCveIds);
  await markKev(env, kevIds);
  // Envoi des digests — silencieusement sauté tant que RESEND_API_KEY n'est
  // pas configurée (beta-safe : l'ingestion tourne sans le mailing).
  if (env.RESEND_API_KEY) {
    const transport = resendTransport(
      env.RESEND_API_KEY,
      env.DIGEST_FROM ?? "StackAlert <digest@example.invalid>"
    );
    const r = await runNotify(env, transport);
    if (r.sent || r.failed) console.log(`notify: ${r.sent} envoyés, ${r.failed} échecs`);
  }
}

/**
 * API de matching pour la future UI (et les démos curl) :
 *   /api/matches?stack=fortinet:fortios:7.2.1,vmware:esxi
 * Borné à 30 jours / 2000 lignes / 50 résultats pour rester sous la limite
 * CPU du free tier. CORS ouvert : lecture seule, données publiques.
 */
async function apiMatches(url, env) {
  const headers = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
  };
  const stackArg = url.searchParams.get("stack") ?? "";
  const stack = stackArg
    .split(",")
    .map((s) => {
      const [vendor, product, version] = s.trim().split(":");
      return { vendor, product, version: version || undefined };
    })
    .filter((s) => s.vendor && s.product);
  if (stack.length === 0) {
    return new Response(JSON.stringify({ error: "stack parameter required" }), {
      status: 400,
      headers,
    });
  }

  const since = new Date(Date.now() - 30 * 864e5).toISOString();
  const rows =
    (
      await env.DB.prepare(
        `SELECT id, cvss_score, in_kev, epss_score, description, cpe_json FROM cves
         WHERE last_modified > ?1 ORDER BY last_modified DESC LIMIT 2000`
      )
        .bind(since)
        .all()
    ).results ?? [];

  const matches = [];
  for (const r of rows) {
    const hits = matchStack(stack, JSON.parse(r.cpe_json || "[]"));
    if (hits.length === 0) continue;
    matches.push({
      id: r.id,
      cvss_score: r.cvss_score,
      in_kev: r.in_kev,
      epss_score: r.epss_score,
      description: (r.description ?? "").slice(0, 300),
      matched: hits.map((h) => ({ display: `${h.vendor}/${h.product}` })),
    });
  }
  const body = {
    window_days: 30,
    scanned: rows.length,
    matches: sortForDigest(matches).slice(0, 50),
  };
  return new Response(JSON.stringify(body), { headers });
}

/** NVD : CVE modifiées depuis le curseur stocké (max 120 jours d'écart). */
async function syncNvd(env) {
  const now = new Date().toISOString();
  const row = await env.DB.prepare(
    "SELECT cursor FROM sync_state WHERE source='nvd'"
  ).first();
  // Premier run : on ne remonte que 7 jours — le backfill historique se fait
  // une fois, hors cron (script local), pas dans le worker.
  const since =
    row?.cursor ?? new Date(Date.now() - 7 * 864e5).toISOString();

  const headers = env.NVD_API_KEY ? { apiKey: env.NVD_API_KEY } : {};
  const ids = [];
  let startIndex = 0;
  let complete = false;

  for (let page = 0; page < NVD_MAX_PAGES_PER_RUN; page++) {
    const params = new URLSearchParams({
      lastModStartDate: since,
      lastModEndDate: now,
      resultsPerPage: String(NVD_PAGE_SIZE),
      startIndex: String(startIndex),
    });
    const res = await fetchWithRetry(`${NVD_API}?${params}`, { headers });
    const data = await res.json();

    for (const item of data.vulnerabilities ?? []) {
      await upsertCve(env, item.cve);
      ids.push(item.cve.id);
    }

    startIndex += data.vulnerabilities?.length ?? 0;
    if (startIndex >= (data.totalResults ?? 0)) {
      complete = true;
      break;
    }
    await sleep(NVD_PAGE_DELAY_MS); // cadence NVD entre deux pages
  }

  // Curseur avancé seulement si la fenêtre est entièrement traitée. Sinon le
  // prochain run reprend la même fenêtre — les upserts sont idempotents, on
  // retraite sans risque plutôt que de perdre des CVE.
  if (complete) {
    await env.DB.prepare(
      `INSERT INTO sync_state (source, cursor, updated_at) VALUES ('nvd', ?1, ?1)
       ON CONFLICT(source) DO UPDATE SET cursor=?1, updated_at=?1`
    )
      .bind(now)
      .run();
  }
  return ids;
}

async function upsertCve(env, c) {
  const metric =
    c.metrics?.cvssMetricV31?.[0]?.cvssData ??
    c.metrics?.cvssMetricV40?.[0]?.cvssData;
  await env.DB.prepare(
    `INSERT INTO cves (id, published, last_modified, cvss_score, cvss_severity, description, cpe_json)
     VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7)
     ON CONFLICT(id) DO UPDATE SET
       last_modified=?3, cvss_score=?4, cvss_severity=?5, description=?6, cpe_json=?7`
  )
    .bind(
      c.id,
      c.published,
      c.lastModified,
      metric?.baseScore ?? null,
      metric?.baseSeverity ?? null,
      c.descriptions?.find((d) => d.lang === "en")?.value ?? "",
      JSON.stringify(c.configurations ?? [])
    )
    .run();
}

/** KEV : le catalogue complet est petit, on le relit en entier. */
async function syncKev(env) {
  const res = await fetchWithRetry(KEV_URL);
  const data = await res.json();
  return (data.vulnerabilities ?? []).map((v) => ({
    id: v.cveID,
    dateAdded: v.dateAdded,
  }));
}

async function markKev(env, kevEntries) {
  for (const { id, dateAdded } of kevEntries) {
    await env.DB.prepare(
      "UPDATE cves SET in_kev=1, kev_date_added=?2 WHERE id=?1 AND in_kev=0"
    )
      .bind(id, dateAdded)
      .run();
  }
}

/** EPSS : scores par lots pour les CVE nouvellement ingérées. */
async function syncEpss(env, cveIds) {
  const BATCH = 50; // prudent — TODO vérifier la limite réelle de l'API FIRST
  for (let i = 0; i < cveIds.length; i += BATCH) {
    const batch = cveIds.slice(i, i + BATCH);
    const res = await fetch(`${EPSS_API}?cve=${batch.join(",")}`);
    if (!res.ok) continue; // EPSS est un enrichissement, pas un bloquant
    const data = await res.json();
    for (const row of data.data ?? []) {
      await env.DB.prepare(
        "UPDATE cves SET epss_score=?2, epss_fetched_at=datetime('now') WHERE id=?1"
      )
        .bind(row.cve, Number(row.epss))
        .run();
    }
  }
}
