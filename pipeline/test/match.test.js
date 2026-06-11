import { test } from "node:test";
import assert from "node:assert/strict";
import { parseCpe, compareVersions, matchStack } from "../src/match.js";

// Fixture à la forme exacte du champ `configurations` de l'API NVD 2.0.
const fortiosRange = [
  {
    nodes: [
      {
        operator: "OR",
        negate: false,
        cpeMatch: [
          {
            vulnerable: true,
            criteria: "cpe:2.3:o:fortinet:fortios:*:*:*:*:*:*:*:*",
            versionStartIncluding: "7.2.0",
            versionEndExcluding: "7.2.7",
          },
          {
            vulnerable: false,
            criteria: "cpe:2.3:h:fortinet:fortigate:-:*:*:*:*:*:*:*",
          },
        ],
      },
    ],
  },
];

test("parseCpe extrait part/vendor/product/version", () => {
  assert.deepEqual(
    parseCpe("cpe:2.3:o:fortinet:fortios:7.2.1:*:*:*:*:*:*:*"),
    { part: "o", vendor: "fortinet", product: "fortios", version: "7.2.1" }
  );
  assert.equal(parseCpe("garbage"), null);
});

test("compareVersions gère le numérique multi-segments", () => {
  assert.equal(compareVersions("1.0.9", "1.0.10"), -1); // pas un tri lexical
  assert.equal(compareVersions("7.2", "7.2.0"), 0);
  assert.equal(compareVersions("10.1", "9.9"), 1);
});

test("version dans la plage vulnérable → match", () => {
  const hits = matchStack(
    [{ vendor: "fortinet", product: "fortios", version: "7.2.1" }],
    fortiosRange
  );
  assert.equal(hits.length, 1);
});

test("version hors plage (borne excluante) → pas de match", () => {
  const hits = matchStack(
    [{ vendor: "fortinet", product: "fortios", version: "7.2.7" }],
    fortiosRange
  );
  assert.equal(hits.length, 0);
});

test("vendor/product différents → pas de match", () => {
  const hits = matchStack(
    [{ vendor: "cisco", product: "ios", version: "15.2" }],
    fortiosRange
  );
  assert.equal(hits.length, 0);
});

test("cpeMatch vulnerable:false jamais matché", () => {
  const hits = matchStack([{ vendor: "fortinet", product: "fortigate" }], fortiosRange);
  assert.equal(hits.length, 0);
});

test("stack sans version → match vendor/product (assumé)", () => {
  const hits = matchStack([{ vendor: "fortinet", product: "fortios" }], fortiosRange);
  assert.equal(hits.length, 1);
});

test("version exacte dans le critère CPE", () => {
  const exact = [
    {
      nodes: [
        {
          operator: "OR",
          cpeMatch: [
            {
              vulnerable: true,
              criteria: "cpe:2.3:a:veeam:backup:12.1.0:*:*:*:*:*:*:*",
            },
          ],
        },
      ],
    },
  ];
  assert.equal(
    matchStack([{ vendor: "veeam", product: "backup", version: "12.1.0" }], exact).length,
    1
  );
  assert.equal(
    matchStack([{ vendor: "veeam", product: "backup", version: "12.0.0" }], exact).length,
    0
  );
});
