/**
 * Moteur de matching stack → CVE (semaine 5). Pur, sans dépendance, testable
 * en local : `npm test` dans pipeline/.
 *
 * Entrées :
 *  - stack : [{ vendor, product, version? }]  (segments CPE en minuscules,
 *    ex. { vendor: "fortinet", product: "fortios", version: "7.2.1" })
 *  - configurations : champ `configurations` brut d'une CVE NVD 2.0
 *    (stocké tel quel dans cves.cpe_json par le worker d'ingestion).
 *
 * Simplifications assumées (documentées, à durcir avec le feedback beta) :
 *  - Les nœuds AND (combinaisons appli+OS) sont traités comme OR : on matche
 *    si N'IMPORTE QUEL cpeMatch vulnérable correspond. Faux positifs possibles
 *    sur les configs plateforme-dépendantes — préférable à un faux négatif.
 *  - `negate` est ignoré (rare) ; les ':' échappés dans les CPE sont ignorés.
 *  - Stack sans version → match sur vendor/product seul (plus bruyant ;
 *    l'UI poussera à renseigner la version).
 */

/** Parse une chaîne CPE 2.3 → { part, vendor, product, version }. */
export function parseCpe(criteria) {
  const seg = criteria.split(":");
  if (seg.length < 6 || seg[0] !== "cpe" || seg[1] !== "2.3") return null;
  return { part: seg[2], vendor: seg[3], product: seg[4], version: seg[5] };
}

/**
 * Compare deux versions "pragmatiques" (pas strictement semver : les versions
 * CPE sont arbitraires). Découpe en segments numériques/alpha ; compare
 * numériquement quand les deux segments sont numériques, sinon en chaîne.
 * Retourne -1 | 0 | 1.
 */
export function compareVersions(a, b) {
  const split = (v) => String(v).split(/[.\-_+]/).filter(Boolean);
  const sa = split(a), sb = split(b);
  const len = Math.max(sa.length, sb.length);
  for (let i = 0; i < len; i++) {
    const x = sa[i] ?? "0", y = sb[i] ?? "0";
    const nx = /^\d+$/.test(x), ny = /^\d+$/.test(y);
    if (nx && ny) {
      const d = Number(x) - Number(y);
      if (d !== 0) return d < 0 ? -1 : 1;
    } else if (x !== y) {
      return x < y ? -1 : 1;
    }
  }
  return 0;
}

/** Un cpeMatch NVD correspond-il à une entrée de stack ? */
export function cpeMatchHits(cpeMatch, item) {
  if (!cpeMatch.vulnerable) return false;
  const cpe = parseCpe(cpeMatch.criteria ?? "");
  if (!cpe) return false;
  if (cpe.vendor !== item.vendor || cpe.product !== item.product) return false;

  // Pas de version déclarée côté stack : match vendor/product (assumé bruyant).
  if (!item.version) return true;

  // Version exacte dans le critère CPE (ni '*' ni '-').
  if (cpe.version !== "*" && cpe.version !== "-") {
    return compareVersions(cpe.version, item.version) === 0;
  }

  // Bornes de plage NVD.
  const v = item.version;
  if (cpeMatch.versionStartIncluding && compareVersions(v, cpeMatch.versionStartIncluding) < 0) return false;
  if (cpeMatch.versionStartExcluding && compareVersions(v, cpeMatch.versionStartExcluding) <= 0) return false;
  if (cpeMatch.versionEndIncluding && compareVersions(v, cpeMatch.versionEndIncluding) > 0) return false;
  if (cpeMatch.versionEndExcluding && compareVersions(v, cpeMatch.versionEndExcluding) >= 0) return false;
  return true;
}

/**
 * Matche une stack complète contre le champ `configurations` d'une CVE.
 * Retourne la liste des entrées de stack touchées (vide = CVE non pertinente).
 */
export function matchStack(stack, configurations) {
  const hits = new Map();
  for (const config of configurations ?? []) {
    for (const node of config.nodes ?? []) {
      for (const cm of node.cpeMatch ?? []) {
        for (const item of stack) {
          const key = `${item.vendor}:${item.product}`;
          if (!hits.has(key) && cpeMatchHits(cm, item)) hits.set(key, item);
        }
      }
    }
  }
  return [...hits.values()];
}
