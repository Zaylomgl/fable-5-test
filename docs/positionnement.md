# Positionnement — StackAlert (nom de travail, disponibilité à vérifier)

## Problème

Les petites équipes IT (1–10 admins) et les MSP n'ont ni SIEM ni budget
threat-intel. Les sources existantes sont soit brutes et bruyantes (NVD publie
des centaines de CVE/semaine), soit non filtrées par stack (alertes email
CISA), soit enterprise et hors budget. Résultat : veille vulnérabilités faite
« quand on a le temps », c'est-à-dire mal — et une exposition réelle aux CVE
activement exploitées.

## Cible

1. **MSP** (cible prioritaire) : multi-clients = multi-stacks = valeur
   démultipliée ; leur temps est facturable, donc 9–29 €/mois est trivial.
2. Sysadmins de PME (10–250 postes), marché anglophone (US/UK/EU).

## Proposition de valeur (message clé)

> **"CVE alerts for your stack. Nothing else."**
> Declare the products you run. Get one short digest — only the CVEs that hit
> your stack, ranked by real-world exploitation (CISA KEV + EPSS), with one
> action line each. Zero noise, zero maintenance.

## Différenciation

| Alternative | Faiblesse exploitée |
|---|---|
| Alertes email CISA (gratuit) | Non filtrées par stack → bruit |
| OpenCVE (open source / SaaS) | Self-host = maintenance ; orienté analystes sécurité, pas MSP |
| SecAlerts (commercial) | Positionnement plus large ; nous : ultra-simple, prix plancher, angle MSP multi-clients |
| Outils enterprise (TI platforms) | Prix et complexité hors de portée PME/MSP |

Notre pari : la valeur n'est pas dans la donnée (gratuite : NVD, OSV, KEV,
EPSS) mais dans le **filtrage par stack déclarée + la priorisation + le format
digest actionnable**.

## Pricing (hypothèse à tester, pas un fait)

- Free : 1 produit suivi, digest hebdo.
- Pro 9 €/mois : stacks illimitées, digest quotidien, Slack.
- MSP 29 €/mois : multi-clients, Teams, rapport par client.
- Annuel = 2 mois offerts. Encaissement via Merchant of Record (Paddle ou
  Polar, 5 % + 0,50 $, 0 € fixe, TVA mondiale gérée par le MoR).

## Validation (semaine 3) — canaux et règles

- Posts « recherche de problème » (pas d'autopromo) : r/sysadmin, r/msp,
  r/cybersecurity — sous pseudo, en respectant les règles de chaque sub
  (lire le wiki des règles AVANT de poster, contribuer d'abord).
- 10 conversations email/DM avec des inscrits ; poser explicitement :
  « paierais-tu 10–20 €/mois pour ça ? ».
- Show HN réservé au lancement réel (S10), pas à la waitlist.

## Go/No-Go (J+14)

GO : ≥ 150 visiteurs, ≥ 30 emails (≥ 15 % conversion), ≥ 5 réponses
qualitatives, ≥ 3 intentions de paiement. NO-GO : < 10 inscrits ou 0 intention
de paiement → pivot.

## Décisions en attente (ne pas trancher avant le GO)

- Nom définitif + domaine (~10–15 €/an, hypothèse) — vérifier collision de
  marque avec produits existants avant achat.
- Catalogue initial de produits suivis (~200–500 produits bien mappés, pas
  « tout NVD »).
- Résumés LLM (API Anthropic, payante) : seulement en phase 2 ; au lancement,
  résumés template-based à 0 €.
