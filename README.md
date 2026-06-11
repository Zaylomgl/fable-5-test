# StackAlert (nom de travail)

Alertes CVE filtrées par stack pour petites équipes IT et MSP — digest email/Slack
priorisé KEV/EPSS/CVSS, uniquement pour les produits que tu utilises vraiment.

> Statut : **phase de validation** (semaines 1–3 de la roadmap 90 jours).
> Rien n'est encaissé, aucun statut légal requis à ce stade.

## Contenu du dépôt

| Dossier | Rôle | Semaine roadmap |
|---|---|---|
| `docs/positionnement.md` | Doc de positionnement 1 page + critères go/no-go | S1 |
| `docs/configuration.md` | **Guide de config pas-à-pas (Netlify, Cloudflare, NVD, quotas)** | — |
| `landing/` | Landing de validation statique (waitlist, 0 build minute) | S2 |
| `pipeline/` | Ingestion NVD/KEV/EPSS → D1 + moteur de matching + digests (testés) | S4–S6 |

## Déployer la landing (0 €)

Option la plus simple — **Netlify** (les formulaires y sont gratuits et illimités) :

1. Connecter ce dépôt sur app.netlify.com → "Add new site".
2. Base directory : `landing` — **pas de commande de build** (HTML statique pur,
   donc 0 minute de build consommée).
3. Le formulaire `waitlist` est détecté automatiquement (`data-netlify="true"`).
   Les inscriptions arrivent dans l'onglet Forms + notification email.

Alternative : Cloudflare Pages (mais il faudra une Pages Function pour le
formulaire — à ne faire que si Netlify pose problème).

À faire à la main après déploiement :
- [ ] Activer la notification email sur soumission de formulaire (Netlify → Forms → Notifications).
- [ ] Ajouter Cloudflare Web Analytics (gratuit, sans cookies) : décommenter le
      snippet en bas de `landing/index.html` et y coller ton token.
- [ ] Ne PAS acheter de domaine avant le GO de la semaine 3 (le sous-domaine
      `*.netlify.app` suffit pour valider).

## Lancer le pipeline (plus tard, semaine 4)

```bash
cd pipeline
npm create cloudflare@latest   # ou : npm i -g wrangler
wrangler d1 create stackalert && wrangler d1 execute stackalert --file=schema.sql
wrangler secret put NVD_API_KEY   # clé gratuite : https://nvd.nist.gov/developers/request-an-api-key
wrangler deploy
```

Contrainte connue : le plan gratuit Workers limite le CPU à ~10 ms/invocation.
Si l'ingestion NVD dépasse, plan B documenté dans `pipeline/src/index.js` :
exécuter l'ingestion via un cron GitHub Actions (2 000 min/mois gratuites en
privé) qui écrit dans D1 via l'API HTTP Cloudflare.

## Critères GO/NO-GO de la validation (J+14 après mise en ligne)

- GO : ≥ 150 visiteurs, ≥ 30 emails (conversion ≥ 15 %), ≥ 5 réponses
  qualitatives, ≥ 3 intentions de paiement explicites.
- NO-GO : < 10 inscrits ou 0 intention de paiement → pivot (produit digital
  sysadmin ou autre niche), sans écrire le produit.
