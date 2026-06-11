import { test } from "node:test";
import assert from "node:assert/strict";
import { shouldSendNow, buildSubscriberDigests, runNotify } from "../src/notify.js";

// ---------- shouldSendNow ----------

const at = (iso) => new Date(iso);

test("daily : envoie au run de 06h UTC uniquement", () => {
  assert.equal(shouldSendNow("daily", at("2026-06-11T06:15:00Z")), true);
  assert.equal(shouldSendNow("daily", at("2026-06-11T12:15:00Z")), false);
});

test("weekly : lundi 06h UTC uniquement", () => {
  assert.equal(shouldSendNow("weekly", at("2026-06-15T06:15:00Z")), true); // lundi
  assert.equal(shouldSendNow("weekly", at("2026-06-11T06:15:00Z")), false); // jeudi
  assert.equal(shouldSendNow("weekly", at("2026-06-15T12:15:00Z")), false);
});

// ---------- buildSubscriberDigests ----------

const fortiosCve = {
  id: "CVE-2026-2222",
  cvss_score: 9.8,
  in_kev: 1,
  epss_score: 0.9,
  configurations: [
    {
      nodes: [
        {
          operator: "OR",
          cpeMatch: [
            { vulnerable: true, criteria: "cpe:2.3:o:fortinet:fortios:*:*:*:*:*:*:*:*" },
          ],
        },
      ],
    },
  ],
};

const sub = (over = {}) => ({
  id: 1,
  email: "a@b.c",
  frequency: "daily",
  products: [{ vendor: "fortinet", product: "fortios" }],
  alreadySent: new Set(),
  ...over,
});

test("abonné touché → un digest avec l'entrée", () => {
  const out = buildSubscriberDigests([fortiosCve], [sub()]);
  assert.equal(out.length, 1);
  assert.equal(out[0].entries[0].id, "CVE-2026-2222");
  assert.equal(out[0].entries[0].in_kev, 1);
});

test("CVE déjà envoyée → pas de re-notification (dédoublonnage)", () => {
  const out = buildSubscriberDigests(
    [fortiosCve],
    [sub({ alreadySent: new Set(["CVE-2026-2222"]) })]
  );
  assert.equal(out.length, 0); // aucune nouveauté → pas d'email du tout
});

test("stack non concernée → abonné absent du résultat", () => {
  const out = buildSubscriberDigests(
    [fortiosCve],
    [sub({ products: [{ vendor: "vmware", product: "esxi" }] })]
  );
  assert.equal(out.length, 0);
});

// ---------- runNotify (D1 et transport factices) ----------

/** Faux D1 minimal : routé par préfixe de requête SQL. */
function fakeDb(state) {
  return {
    prepare(sql) {
      const q = { sql, params: [] };
      return {
        bind(...params) {
          q.params = params;
          return this;
        },
        async first() {
          if (sql.includes("sync_state")) return state.cursorRow;
          return null;
        },
        async all() {
          if (sql.includes("FROM subscribers")) return { results: state.subscribers };
          if (sql.includes("FROM cves")) return { results: state.cveRows };
          if (sql.includes("FROM subscriber_products"))
            return { results: state.productsBySub[q.params[0]] ?? [] };
          if (sql.includes("FROM sent_log"))
            return { results: state.sentBySub[q.params[0]] ?? [] };
          return { results: [] };
        },
        async run() {
          if (sql.startsWith("INSERT OR IGNORE INTO sent_log"))
            state.sentInserts.push(q.params);
          if (sql.includes("INSERT INTO sync_state")) state.cursorWrites.push(q.params[0]);
          return {};
        },
      };
    },
  };
}

const baseState = () => ({
  cursorRow: null,
  subscribers: [{ id: 1, email: "msp@example.com", frequency: "daily" }],
  cveRows: [
    {
      id: "CVE-2026-2222",
      cvss_score: 9.8,
      in_kev: 1,
      epss_score: 0.9,
      cpe_json: JSON.stringify(fortiosCve.configurations),
    },
  ],
  productsBySub: { 1: [{ vendor: "fortinet", product: "fortios", version: null }] },
  sentBySub: {},
  sentInserts: [],
  cursorWrites: [],
});

test("runNotify : envoie, journalise sent_log, avance le curseur", async () => {
  const state = baseState();
  const sent = [];
  const transport = { send: async (m) => sent.push(m) };
  const r = await runNotify({ DB: fakeDb(state) }, transport, at("2026-06-11T06:15:00Z"));
  assert.equal(r.sent, 1);
  assert.equal(sent[0].to, "msp@example.com");
  assert.match(sent[0].subject, /1 CVE/);
  assert.deepEqual(state.sentInserts, [[1, "CVE-2026-2222"]]);
  assert.equal(state.cursorWrites.length, 1);
});

test("runNotify : échec d'envoi → curseur non avancé (retry au run suivant)", async () => {
  const state = baseState();
  const transport = { send: async () => { throw new Error("boom"); } };
  const r = await runNotify({ DB: fakeDb(state) }, transport, at("2026-06-11T06:15:00Z"));
  assert.equal(r.failed, 1);
  assert.equal(state.sentInserts.length, 0);
  assert.equal(state.cursorWrites.length, 0);
});

test("runNotify : hors créneau d'envoi → rien ne part", async () => {
  const state = baseState();
  const sent = [];
  const r = await runNotify(
    { DB: fakeDb(state) },
    { send: async (m) => sent.push(m) },
    at("2026-06-11T12:15:00Z")
  );
  assert.deepEqual(r, { sent: 0, failed: 0 });
  assert.equal(sent.length, 0);
});
