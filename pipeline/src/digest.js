/**
 * Rendu des digests (semaine 6) — pur, testable, sans dépendance.
 * Entrée : liste de CVE matchées, chacune { id, description, cvss_score,
 * cvss_severity, in_kev, epss_score, matched: [{display}] }.
 * Sortie : { subject, text, html } prêts pour Resend/Brevo.
 *
 * Tri éditorial = la proposition de valeur : exploitation réelle d'abord
 * (KEV), puis probabilité d'exploitation (EPSS), puis CVSS. Le score de
 * sévérité seul est un mauvais signal de triage — c'est notre angle.
 */

export function sortForDigest(cves) {
  return [...cves].sort(
    (a, b) =>
      (b.in_kev ? 1 : 0) - (a.in_kev ? 1 : 0) ||
      (b.epss_score ?? -1) - (a.epss_score ?? -1) ||
      (b.cvss_score ?? -1) - (a.cvss_score ?? -1)
  );
}

const nvdLink = (id) => `https://nvd.nist.gov/vuln/detail/${id}`;

function line(c) {
  const products = c.matched.map((m) => m.display).join(", ");
  const tags = [
    c.in_kev ? "EXPLOITED IN THE WILD" : null,
    c.epss_score != null ? `EPSS ${(c.epss_score * 100).toFixed(1)}%` : null,
    c.cvss_score != null ? `CVSS ${c.cvss_score}` : null,
  ].filter(Boolean).join(" · ");
  return { products, tags };
}

export function renderDigest(cves, { period = "daily" } = {}) {
  const sorted = sortForDigest(cves);
  const kevCount = sorted.filter((c) => c.in_kev).length;

  const subject =
    sorted.length === 0
      ? `StackAlert: no new CVEs for your stack today`
      : `StackAlert: ${sorted.length} CVE${sorted.length > 1 ? "s" : ""} for your stack` +
        (kevCount ? ` (${kevCount} actively exploited)` : "");

  const textParts = [`Your ${period} StackAlert digest`, ""];
  const htmlParts = [
    `<h2 style="font-family:sans-serif">Your ${period} StackAlert digest</h2>`,
  ];

  if (sorted.length === 0) {
    textParts.push("Nothing matched your stack. Enjoy the quiet.");
    htmlParts.push(`<p>Nothing matched your stack. Enjoy the quiet.</p>`);
  }

  for (const c of sorted) {
    const { products, tags } = line(c);
    textParts.push(
      `${c.in_kev ? "[!] " : ""}${c.id} — ${products}`,
      `    ${tags}`,
      `    Action: review and patch ${products}. ${nvdLink(c.id)}`,
      ""
    );
    htmlParts.push(
      `<div style="font-family:sans-serif;margin:0 0 14px;padding:10px 12px;border-left:4px solid ${c.in_kev ? "#dc2626" : "#4ade80"};background:#f8fafc">` +
        `<b>${c.id}</b> — ${escapeHtml(products)}<br>` +
        `<small>${escapeHtml(tags)}</small><br>` +
        `<small>Action: review and patch. <a href="${nvdLink(c.id)}">NVD details</a></small>` +
        `</div>`
    );
  }

  return { subject, text: textParts.join("\n"), html: htmlParts.join("\n") };
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (ch) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch])
  );
}
