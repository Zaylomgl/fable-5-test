/**
 * Boucle de notification (semaine 6) : pour chaque abonné dont c'est l'heure
 * d'envoi, construit le digest des CVE qui touchent SA stack et qu'il n'a
 * JAMAIS reçues, l'envoie via un transport injecté, journalise dans sent_log.
 *
 * Découpage testable :
 *  - shouldSendNow / buildSubscriberDigests : purs, couverts par les tests
 *  - runNotify : glue D1 + transport (transport injecté → testable aussi)
 *
 * Choix produit assumés :
 *  - digest vide → pas d'email (le silence EST la proposition de valeur) ;
 *  - envoi quotidien au run de 06:15 UTC, hebdo le lundi même run ;
 *  - en cas d'échec d'envoi, le curseur n'avance pas : on retente au run
 *    suivant, sent_log empêche les doublons pour ceux déjà partis.
 */

import { matchStack } from "./match.js";
import { renderDigest } from "./digest.js";

/** L'heure d'envoi de cet abonné est-elle maintenant ? (cron : 00/06/12/18 UTC) */
export function shouldSendNow(frequency, now) {
  const hour = now.getUTCHours();
  if (frequency === "daily") return hour === 6;
  if (frequency === "weekly") return now.getUTCDay() === 1 && hour === 6;
  return false;
}

const display = (s) =>
  `${s.vendor}/${s.product}`.replace(/_/g, " ").replace(/\\&/g, "&");

/**
 * cves : [{ id, cvss_score, in_kev, epss_score, configurations }]
 * subscribers : [{ id, email, frequency, products: [{vendor,product,version}],
 *                  alreadySent: Set<cveId> }]
 * → [{ subscriber, entries }] (abonnés avec ≥ 1 nouveauté uniquement)
 */
export function buildSubscriberDigests(cves, subscribers) {
  const out = [];
  for (const sub of subscribers) {
    const entries = [];
    for (const cve of cves) {
      if (sub.alreadySent.has(cve.id)) continue;
      const hits = matchStack(sub.products, cve.configurations ?? []);
      if (hits.length === 0) continue;
      entries.push({
        id: cve.id,
        cvss_score: cve.cvss_score ?? null,
        in_kev: cve.in_kev ? 1 : 0,
        epss_score: cve.epss_score ?? null,
        matched: hits.map((h) => ({ display: display(h) })),
      });
    }
    if (entries.length > 0) out.push({ subscriber: sub, entries });
  }
  return out;
}

/** Glue worker : lit D1, envoie via `transport.send`, journalise. */
export async function runNotify(env, transport, now = new Date()) {
  const subsRows = (
    await env.DB.prepare("SELECT id, email, frequency FROM subscribers WHERE active=1").all()
  ).results ?? [];
  const due = subsRows.filter((s) => shouldSendNow(s.frequency, now));
  if (due.length === 0) return { sent: 0, failed: 0 };

  // Fenêtre : CVE modifiées depuis le dernier envoi réussi (défaut : 7 jours).
  const cursorRow = await env.DB.prepare(
    "SELECT cursor FROM sync_state WHERE source='notify'"
  ).first();
  const since = cursorRow?.cursor ?? new Date(now.getTime() - 7 * 864e5).toISOString();

  const cveRows = (
    await env.DB.prepare(
      `SELECT id, cvss_score, in_kev, epss_score, cpe_json FROM cves
       WHERE last_modified > ?1 ORDER BY last_modified LIMIT 1000`
    ).bind(since).all()
  ).results ?? [];
  const cves = cveRows.map((r) => ({ ...r, configurations: JSON.parse(r.cpe_json || "[]") }));

  const subscribers = [];
  for (const s of due) {
    const products = (
      await env.DB.prepare(
        "SELECT vendor, product, version FROM subscriber_products WHERE subscriber_id=?1"
      ).bind(s.id).all()
    ).results ?? [];
    const sent = (
      await env.DB.prepare("SELECT cve_id FROM sent_log WHERE subscriber_id=?1").bind(s.id).all()
    ).results ?? [];
    subscribers.push({ ...s, products, alreadySent: new Set(sent.map((r) => r.cve_id)) });
  }

  let sentCount = 0, failed = 0;
  for (const { subscriber, entries } of buildSubscriberDigests(cves, subscribers)) {
    const digest = renderDigest(entries, {
      period: subscriber.frequency === "weekly" ? "weekly" : "daily",
    });
    try {
      await transport.send({
        to: subscriber.email,
        subject: digest.subject,
        html: digest.html,
        text: digest.text,
      });
      for (const e of entries) {
        await env.DB.prepare(
          "INSERT OR IGNORE INTO sent_log (subscriber_id, cve_id) VALUES (?1, ?2)"
        ).bind(subscriber.id, e.id).run();
      }
      sentCount++;
    } catch (err) {
      failed++;
      console.error(`notify: échec d'envoi à ${subscriber.email}: ${err.message}`);
    }
  }

  // Le curseur n'avance que si tout est parti (sinon retry au run suivant).
  if (failed === 0) {
    await env.DB.prepare(
      `INSERT INTO sync_state (source, cursor, updated_at) VALUES ('notify', ?1, ?1)
       ON CONFLICT(source) DO UPDATE SET cursor=?1, updated_at=?1`
    ).bind(now.toISOString()).run();
  }
  return { sent: sentCount, failed };
}

/** Transport Resend (https://resend.com/docs — TODO vérifier le payload exact). */
export function resendTransport(apiKey, from) {
  return {
    async send({ to, subject, html, text }) {
      const res = await fetch("https://api.resend.com/emails", {
        method: "POST",
        headers: { Authorization: `Bearer ${apiKey}`, "Content-Type": "application/json" },
        body: JSON.stringify({ from, to, subject, html, text }),
      });
      if (!res.ok) throw new Error(`Resend HTTP ${res.status}`);
    },
  };
}
