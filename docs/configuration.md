# Guide de configuration — de zéro à un système qui tourne

Tout est sur free tier sauf mention contraire. Temps total estimé : **~45 min**
(hors création de comptes). Les parties A et C suffisent pour la phase de
validation ; la partie B peut attendre la semaine 4.

## Prérequis

| Quoi | Où | Coût |
|---|---|---|
| Node.js ≥ 20 | nodejs.org (tu l'as déjà) | 0 € |
| Compte Netlify | app.netlify.com (déjà créé et connecté) | 0 € |
| Compte Cloudflare | dash.cloudflare.com | 0 € |
| Clé API NVD | https://nvd.nist.gov/developers/request-an-api-key (email → lien d'activation) | 0 € |

---

## A. Landing + waitlist (Netlify) — ~10 min

Le `netlify.toml` à la racine fait déjà le travail (publie `landing/`, aucun
build). Il reste les clics côté interface :

1. **app.netlify.com → Add new project → Import an existing project →
   GitHub → `fable-5-test`** (ou le repo renommé). Ne touche à rien : les
   réglages viennent du `netlify.toml`. Deploy.
2. **Activer la détection des formulaires** : Project → Forms → *Enable form
   detection*, puis **redéploie une fois** (Deploys → Trigger deploy). La
   détection se fait au moment du déploiement — sans ça, le formulaire
   `waitlist` n'apparaîtra pas.
3. **Notifications** : Project → Forms → Notifications → *Email notification*
   → ton adresse. C'est ce qui te permet de répondre à chaque inscrit dans
   l'heure (ça compte pour la validation).
4. **Anti-spam** : le honeypot est déjà dans le HTML (`bot-field`). Si du spam
   passe quand même, active reCAPTCHA dans le même écran Forms.
5. **Analytics (optionnel mais recommandé)** : dash.cloudflare.com → Web
   Analytics → Add site (fonctionne même si le site est chez Netlify) → copie
   le token → décommente le snippet en bas de `landing/index.html`, colle le
   token, commit, push.
6. **Test de bout en bout** : ouvre l'URL `*.netlify.app`, soumets le
   formulaire avec une vraie adresse → tu dois voir la soumission dans
   Forms **et** recevoir l'email de notification.

> Ne pas faire maintenant : acheter un domaine. Le sous-domaine netlify.app
> suffit pour valider (critères go/no-go dans `docs/positionnement.md`).

---

## B. Pipeline d'ingestion (Cloudflare Workers + D1) — ~20 min

Depuis **ta machine** (le login ouvre un navigateur) :

```bash
cd pipeline
npm install -g wrangler        # ou npx wrangler pour éviter le -g
wrangler login                 # OAuth navigateur

# 1. Créer la base D1
wrangler d1 create stackalert
# → copie le database_id affiché dans wrangler.toml (remplace REPLACE_ME)

# 2. Créer les tables, puis charger le catalogue produits
wrangler d1 execute stackalert --remote --file=schema.sql
wrangler d1 execute stackalert --remote --file=seed_products.sql

# 3. Clé NVD (gratuite, demandée par email — voir Prérequis)
wrangler secret put NVD_API_KEY     # colle la clé quand demandé

# 4. Déployer
wrangler deploy
```

**Vérifier que ça tourne :**

```bash
# Déclencher une ingestion à la main (sans attendre le cron de 6 h)
curl https://stackalert-ingest.<ton-sous-domaine>.workers.dev/run

# Compter ce qui est arrivé en base
wrangler d1 execute stackalert --remote \
  --command "SELECT COUNT(*) AS cves, SUM(in_kev) AS kev FROM cves"

# Voir les logs en direct (utile au premier run)
wrangler tail
```

Comportement attendu : le premier run ne remonte que **7 jours** d'historique
(c'est voulu — le backfill complet se fait plus tard, hors worker). Le cron
(`15 */6 * * *`, défini dans `wrangler.toml`) prend le relais ensuite. Le
curseur de sync est en table `sync_state` : si un run est interrompu, le
suivant reprend la même fenêtre sans rien perdre (upserts idempotents).

**Si le worker dépasse la limite CPU du plan gratuit (~10 ms/invocation)** —
visible dans `wrangler tail` ou le dashboard : plan B documenté dans
`src/index.js` → exécuter la même logique dans un cron GitHub Actions
(2 000 min/mois gratuites en privé) qui écrit dans D1 via l'API HTTP
Cloudflare. Ne le construis que si le problème se présente.

---

## C. Tests locaux + démo de bout en bout — ~5 min

Aucun compte requis :

```bash
cd pipeline
npm test          # 17 tests : matching CPE, rendu des digests, glue démo
node --check src/index.js
```

**Démo avec de vraies données live** (NVD + KEV + EPSS → matching → digest
imprimé) — à lancer depuis ta machine (réseau normal requis) :

```bash
node scripts/demo.js                                   # stack de démo, 7 jours
node scripts/demo.js --days 14 --stack "fortinet:fortios,vmware:esxi:8.0"
NVD_API_KEY=ta-clé node scripts/demo.js                # plus rapide avec la clé
```

Le script imprime le digest exactement comme il partirait par email, plus le
ratio signal/bruit (CVE retenues / CVE publiées). Utile aussi comme matériel
de démo pour les conversations de validation (semaine 3).

---

## D. Quotas free tier à surveiller

| Service | Limite gratuite | Alerte quand |
|---|---|---|
| Workers | 100 000 req/jour, ~10 ms CPU/invocation, 5 crons | erreurs CPU dans `wrangler tail` |
| D1 | 5 GB, 5 M lignes lues/jour, 100 k écrites/jour | dashboard D1 > 70 % |
| Netlify | 100 GB bande passante/mois, crédits limités (site **en pause** si dépassés) | email Netlify de seuil |
| NVD API | 50 req/30 s avec clé | les retries 403/503 se multiplient dans les logs |
| Resend (plus tard) | 3 000 emails/mois, **100/jour** | ~80 abonnés en digest quotidien → passer à Brevo (300/jour) ou Resend Pro (20 $/mois) |

---

## E. Plus tard — au moment du lancement payant (semaine 9–10, pas avant)

Dans cet ordre, parce que le légal conditionne l'encaissement :

1. **Légal (Belgique)** : inscription BCE via guichet agréé (111,50 €),
   statut étudiant-indépendant, identification TVA (franchise < 25 000 €).
   Détails et seuils 2026 : voir le plan (réponse consultant) — tout vérifier
   auprès d'INASTI/SPF Finances/guichet.
2. **Paiement** : compte Paddle ou Polar.sh (Merchant of Record, 5 % + 0,50 $,
   0 € de fixe, TVA mondiale gérée). KYC = avoir le statut légal d'abord.
3. **Email de production** : acheter le domaine (vérifier la marque avant !),
   configurer Resend dessus avec SPF + DKIM + DMARC dès le premier envoi —
   la délivrabilité est vitale pour un produit qui EST un email.

---

## Dépannage rapide

| Symptôme | Cause probable | Fix |
|---|---|---|
| Formulaire absent de l'onglet Forms | Détection désactivée ou pas de redéploiement | A.2 : activer puis redéployer |
| `binding DB not found` au deploy | `database_id` resté sur `REPLACE_ME` | B.1 : coller l'id de `d1 create` |
| HTTP 403/503 répétés sur NVD | Cadence dépassée ou clé absente | vérifier `wrangler secret list` ; les retries/backoff sont déjà dans le code |
| `/run` timeout | fenêtre de sync trop grosse (1er run après longue pause) | relancer : le curseur fait reprendre là où c'était ; les runs suivants sont incrémentaux |
| Site Netlify « paused » | crédits du mois épuisés | attendre le 1er du mois ou migrer la landing sur Cloudflare Pages |
