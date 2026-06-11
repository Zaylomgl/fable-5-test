import { test } from "node:test";
import assert from "node:assert/strict";
import { toDigestEntry } from "../scripts/demo.js";

// Item à la forme exacte d'une entrée `vulnerabilities[].cve` de l'API NVD 2.0.
const nvdCve = {
  id: "CVE-2026-1111",
  published: "2026-06-09T10:00:00.000",
  lastModified: "2026-06-10T10:00:00.000",
  descriptions: [{ lang: "en", value: "RCE in FortiOS SSL-VPN." }],
  metrics: {
    cvssMetricV31: [{ cvssData: { baseScore: 9.8, baseSeverity: "CRITICAL" } }],
  },
  configurations: [
    {
      nodes: [
        {
          operator: "OR",
          negate: false,
          cpeMatch: [
            {
              vulnerable: true,
              criteria: "cpe:2.3:o:fortinet:fortios:*:*:*:*:*:*:*:*",
              versionStartIncluding: "7.0.0",
              versionEndExcluding: "7.0.15",
            },
          ],
        },
      ],
    },
  ],
};

const stack = [{ vendor: "fortinet", product: "fortios", version: "7.0.3" }];

test("CVE NVD brute → entrée de digest complète", () => {
  const entry = toDigestEntry(nvdCve, stack, new Set(["CVE-2026-1111"]));
  assert.equal(entry.id, "CVE-2026-1111");
  assert.equal(entry.cvss_score, 9.8);
  assert.equal(entry.in_kev, 1);
  assert.deepEqual(entry.matched, [{ display: "fortinet/fortios" }]);
});

test("CVE hors KEV → in_kev=0", () => {
  const entry = toDigestEntry(nvdCve, stack, new Set());
  assert.equal(entry.in_kev, 0);
});

test("CVE qui ne touche pas la stack → null (filtrée du digest)", () => {
  const entry = toDigestEntry(
    nvdCve,
    [{ vendor: "vmware", product: "esxi" }],
    new Set()
  );
  assert.equal(entry, null);
});

test("CVE sans métrique CVSS → score null, pas de crash", () => {
  const { metrics, ...noMetrics } = nvdCve;
  const entry = toDigestEntry(noMetrics, stack, new Set());
  assert.equal(entry.cvss_score, null);
});
