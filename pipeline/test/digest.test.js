import { test } from "node:test";
import assert from "node:assert/strict";
import { sortForDigest, renderDigest } from "../src/digest.js";

const cves = [
  {
    id: "CVE-2026-0001",
    cvss_score: 9.8,
    in_kev: 0,
    epss_score: 0.02,
    matched: [{ display: "Fortinet FortiOS" }],
  },
  {
    id: "CVE-2026-0002",
    cvss_score: 7.5,
    in_kev: 1,
    epss_score: 0.91,
    matched: [{ display: "VMware ESXi" }],
  },
  {
    id: "CVE-2026-0003",
    cvss_score: 8.1,
    in_kev: 0,
    epss_score: 0.4,
    matched: [{ display: "Veeam Backup" }],
  },
];

test("tri : KEV d'abord, puis EPSS, puis CVSS — pas le CVSS seul", () => {
  const ids = sortForDigest(cves).map((c) => c.id);
  assert.deepEqual(ids, ["CVE-2026-0002", "CVE-2026-0003", "CVE-2026-0001"]);
});

test("sujet : compte total + compte KEV", () => {
  const { subject } = renderDigest(cves);
  assert.match(subject, /3 CVEs/);
  assert.match(subject, /1 actively exploited/);
});

test("digest vide : sujet calme, pas d'alarmisme", () => {
  const { subject, text } = renderDigest([]);
  assert.match(subject, /no new CVEs/);
  assert.match(text, /Enjoy the quiet/);
});

test("le texte contient l'action et le lien NVD", () => {
  const { text } = renderDigest(cves);
  assert.match(text, /Action: review and patch/);
  assert.match(text, /nvd\.nist\.gov\/vuln\/detail\/CVE-2026-0002/);
});

test("le HTML échappe le contenu", () => {
  const { html } = renderDigest([
    { id: "CVE-2026-0009", in_kev: 0, matched: [{ display: "<script>x</script>" }] },
  ]);
  assert.ok(!html.includes("<script>x"));
  assert.ok(html.includes("&lt;script&gt;"));
});
