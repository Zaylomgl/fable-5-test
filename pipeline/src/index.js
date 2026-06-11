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

const NVD_API = "https://services.nvd.nist.gov/rest/json/cves/2.0";
const KEV_URL =
  "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json";
const EPSS_API = "https://api.first.org/data/v1/epss";
const NVD_PAGE_SIZE = 200; // pages volontairement petites (budget CPU)

export default {
  async scheduled(event, env, ctx) {
    ctx.waitUntil(runIngestion(env));
  },

  // Endpoint manuel pour tester sans attendre le cron : GET /run
  async fetch(req, env) {
    const url = new URL(req.url);
    if (url.pathname === "/run") {
      await runIngestion(env);
      return new Response("ingestion done\n");
    }
    return new Response("stackalert-ingest\n");
  },
};

async function runIngestion(env) {
  const kevIds = await syncKev(env);
  const newCveIds = await syncNvd(env);
  await syncEpss(env, newCveIds);
  await markKev(env, kevIds);
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

  const params = new URLSearchParams({
    lastModStartDate: since,
    lastModEndDate: now,
    resultsPerPage: String(NVD_PAGE_SIZE),
  });
  const headers = env.NVD_API_KEY ? { apiKey: env.NVD_API_KEY } : {};
  const res = await fetch(`${NVD_API}?${params}`, { headers });
  if (!res.ok) throw new Error(`NVD ${res.status}`);
  const data = await res.json();

  const ids = [];
  for (const item of data.vulnerabilities ?? []) {
    const c = item.cve;
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
    ids.push(c.id);
  }
  // TODO: si data.totalResults > NVD_PAGE_SIZE, boucler avec startIndex
  // (en respectant ~6 s entre requêtes recommandés par la NVD).

  await env.DB.prepare(
    `INSERT INTO sync_state (source, cursor, updated_at) VALUES ('nvd', ?1, ?1)
     ON CONFLICT(source) DO UPDATE SET cursor=?1, updated_at=?1`
  )
    .bind(now)
    .run();
  return ids;
}

/** KEV : le catalogue complet est petit, on le relit en entier. */
async function syncKev(env) {
  const res = await fetch(KEV_URL);
  if (!res.ok) throw new Error(`KEV ${res.status}`);
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
