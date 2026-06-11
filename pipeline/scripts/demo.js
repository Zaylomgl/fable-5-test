/**
 * Démo de bout en bout, sans aucun compte ni base de données :
 * NVD (CVE récentes) + CISA KEV + EPSS → matching stack → digest imprimé.
 *
 *   node scripts/demo.js
 *   node scripts/demo.js --days 14 --stack "fortinet:fortios,vmware:esxi:8.0"
 *
 * Format --stack : "vendor:product[:version]" séparés par des virgules
 * (segments CPE en minuscules). Sans version → match vendor/product (bruyant,
 * assumé — voir src/match.js).
 *
 * Sert aussi de smoke test du matcher contre la VRAIE forme de l'API NVD 2.0
 * (les tests unitaires utilisent des fixtures).
 */

import { pathToFileURL } from "node:url";
import { matchStack } from "../src/match.js";
import { renderDigest } from "../src/digest.js";

const NVD_API = "https://services.nvd.nist.gov/rest/json/cves/2.0";
const KEV_URL =
  "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json";
const EPSS_API = "https://api.first.org/data/v1/epss";
const PAGE_SIZE = 2000; // max NVD — en local on minimise le nombre de requêtes
const MAX_PAGES = 3;

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function parseArgs() {
  const args = process.argv.slice(2);
  const get = (flag, dflt) => {
    const i = args.indexOf(flag);
    return i >= 0 ? args[i + 1] : dflt;
  };
  const days = Number(get("--days", "7"));
  // Stack de démo par défaut : produits très exposés → digest rarement vide.
  const stackArg = get(
    "--stack",
    "fortinet:fortios,vmware:esxi,microsoft:exchange_server,cisco:ios_xe,atlassian:confluence_server,veeam:veeam_backup_\\&_replication,ivanti:connect_secure,citrix:netscaler_application_delivery_controller"
  );
  const stack = stackArg.split(",").map((s) => {
    const [vendor, product, version] = s.trim().split(":");
    return { vendor, product, version: version || undefined };
  });
  return { days, stack };
}

async function fetchJson(url, headers = {}) {
  const res = await fetch(url, { headers });
  if (!res.ok) throw new Error(`${String(url).split("?")[0]} -> HTTP ${res.status}`);
  return res.json();
}

async function fetchRecentCves(days) {
  const end = new Date();
  const start = new Date(end.getTime() - days * 864e5);
  const headers = process.env.NVD_API_KEY ? { apiKey: process.env.NVD_API_KEY } : {};
  const all = [];
  let startIndex = 0;
  for (let page = 0; page < MAX_PAGES; page++) {
    const params = new URLSearchParams({
      pubStartDate: start.toISOString(),
      pubEndDate: end.toISOString(),
      resultsPerPage: String(PAGE_SIZE),
      startIndex: String(startIndex),
    });
    process.stderr.write(`NVD page ${page + 1}…\n`);
    const data = await fetchJson(`${NVD_API}?${params}`, headers);
    all.push(...(data.vulnerabilities ?? []).map((v) => v.cve));
    startIndex += data.vulnerabilities?.length ?? 0;
    if (startIndex >= (data.totalResults ?? 0)) break;
    await sleep(6000);
  }
  return all;
}

async function fetchKevIds() {
  const data = await fetchJson(KEV_URL);
  return new Set((data.vulnerabilities ?? []).map((v) => v.cveID));
}

async function fetchEpss(ids) {
  const scores = new Map();
  for (let i = 0; i < ids.length; i += 50) {
    const batch = ids.slice(i, i + 50);
    try {
      const data = await fetchJson(`${EPSS_API}?cve=${batch.join(",")}`);
      for (const row of data.data ?? []) scores.set(row.cve, Number(row.epss));
    } catch {
      /* enrichissement best-effort */
    }
  }
  return scores;
}

const display = (s) =>
  `${s.vendor}/${s.product}`.replace(/_/g, " ").replace(/\\&/g, "&");

/**
 * Transforme une CVE NVD 2.0 brute en entrée de digest si elle touche la
 * stack, sinon null. Exportée pour être testée (test/demo.test.js).
 */
export function toDigestEntry(cve, stack, kevIds) {
  const hits = matchStack(stack, cve.configurations ?? []);
  if (hits.length === 0) return null;
  const metric =
    cve.metrics?.cvssMetricV31?.[0]?.cvssData ?? cve.metrics?.cvssMetricV40?.[0]?.cvssData;
  return {
    id: cve.id,
    cvss_score: metric?.baseScore ?? null,
    in_kev: kevIds.has(cve.id) ? 1 : 0,
    epss_score: null,
    matched: hits.map((h) => ({ display: display(h) })),
  };
}

async function main() {
  const { days, stack } = parseArgs();
  console.error(
    `Stack (${stack.length} produits) : ${stack.map(display).join(", ")}\n` +
      `Fenêtre : CVE publiées sur ${days} jours\n`
  );

  const [cves, kevIds] = await Promise.all([fetchRecentCves(days), fetchKevIds()]);
  console.error(`${cves.length} CVE publiées, catalogue KEV : ${kevIds.size} entrées\n`);

  const matched = [];
  for (const c of cves) {
    const entry = toDigestEntry(c, stack, kevIds);
    if (entry) matched.push(entry);
  }

  const epss = await fetchEpss(matched.map((m) => m.id));
  for (const m of matched) m.epss_score = epss.get(m.id) ?? null;

  const digest = renderDigest(matched, { period: "weekly" });
  console.log("=".repeat(64));
  console.log(`SUBJECT: ${digest.subject}`);
  console.log("=".repeat(64));
  console.log(digest.text);
  console.error(
    `Signal/bruit : ${matched.length} CVE retenues sur ${cves.length} publiées ` +
      `(${cves.length ? ((matched.length / cves.length) * 100).toFixed(1) : 0} %)`
  );
}

// N'exécute main() que lancé directement (pas à l'import par les tests).
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main().catch((e) => {
    console.error(`Erreur : ${e.message}`);
    process.exit(1);
  });
}
