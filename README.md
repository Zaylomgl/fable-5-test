# Boîte à outils perso

Vingt-quatre outils, en français, **zéro dépendance** (Python 3 standard uniquement).
Aucune installation : clone le repo et lance les scripts.

**Gagner de l'argent (freelance / petits boulots) :**

| Outil | À quoi ça sert |
|---|---|
| 💶 `facture/` | Factures et devis pro |
| 📧 `relance/` | Mails de relance pour factures impayées (3 niveaux) |
| 📈 `tjm/` | Le tarif journalier à facturer selon le revenu visé |
| ⏱ `tempo/` | Pointeuse par projet — facture tes heures au juste prix |

**Gérer ton argent :**

| Outil | À quoi ça sert |
|---|---|
| 📊 `budget/` | Suivi de dépenses/revenus, bilan mensuel |
| 💸 `abonnements/` | Coût réel de tes abonnements + prélèvements à venir |
| ✂️ `resiliation/` | Lettre de résiliation d'abonnement prête à envoyer |
| 📉 `veille-prix/` | Alerte quand un prix baisse |
| 🎯 `epargne/` | Combien mettre de côté par mois pour ton objectif |
| 🤝 `partage/` | Dépenses entre potes/coloc (façon Tricount) |
| 🚗 `trajet/` | Coût réel d'un trajet en voiture, part par passager |

**Quotidien :**

| Outil | À quoi ça sert |
|---|---|
| 🔐 `motdepasse/` | Mots de passe et phrases de passe sécurisés |
| 📅 `rappels/` | Anniversaires et échéances, avec compte à rebours |
| 🛒 `courses/` | Liste de courses en CLI |
| 🍅 `pomodoro/` | Minuteur focus/pause dans le terminal |
| ☀️ `meteo/` | Météo en CLI (via wttr.in, sans clé API) |
| 🍽 `menu/` | « On mange quoi ce soir ? » — tirage au sort de repas |
| 📝 `texte/` | Compteur de mots, slugs, majuscules/minuscules |

**Gadgets utiles :**

| Outil | À quoi ça sert |
|---|---|
| 🎲 `hasard/` | Pile ou face, dés, tirage au sort, mélange d'ordre |
| ➗ `pourcentage/` | Remises, hausses, évolutions — sans se tromper |
| 📏 `conversion/` | km/miles, °C/°F, kg/lbs, litres/gallons… |
| ⚖️ `sante/` | IMC et hydratation (indicatif) |
| 🎂 `age/` | Ton âge exact en jours/heures + compte à rebours anniv |
| 💬 `citation/` | La citation du jour (pour le `.bashrc`) |
| 🎮 `jeu/` | Devine le nombre, pour tuer 2 minutes |

Exemples rapides :

```bash
python3 hasard/hasard.py choisis "pizza" "sushi" "kebab"   # 👉 kebab
python3 pourcentage/pct.py remise 25 80                    # 80 € −25 % = 60 €
python3 conversion/conv.py 10 km miles                     # 6.214 miles
python3 age/age.py 2006-04-12                              # âge exact + jours avant l'anniv
python3 menu/menu.py semaine                               # 7 repas planifiés
python3 pomodoro/pomodoro.py 50 10 -c 2                    # 2 × (50 min focus + 10 pause)
python3 meteo/meteo.py Paris                               # météo du moment
python3 jeu/devine.py 1000                                 # devine le nombre
```

## 💶 `facture/` — Factures et devis

Pour facturer tes missions freelance ou petits boulots avec un rendu pro.

```bash
cp facture/exemple.json facture/ma_facture.json   # remplis tes infos et tes prestations
python3 facture/facture.py facture/ma_facture.json           # facture
python3 facture/facture.py facture/ma_facture.json --devis   # devis (avant la mission)
```

Ça génère un HTML propre → ouvre-le dans un navigateur → `Ctrl+P` → Enregistrer en PDF.
Le total est calculé automatiquement, les mentions légales micro-entrepreneur
(TVA non applicable, art. 293 B du CGI) sont incluses par défaut.

## 📊 `budget/` — Suivi de budget

Pour savoir où part ton argent, sans app ni compte à créer. Données dans un simple CSV local.

```bash
python3 budget/budget.py add 12.50 courses "Carrefour"     # dépense
python3 budget/budget.py add 850 revenu "Salaire" --in     # revenu
python3 budget/budget.py list                              # dernières opérations
python3 budget/budget.py mois                              # bilan du mois (entrées/sorties/solde)
python3 budget/budget.py cat                               # dépenses par catégorie, avec graphe
```

## 📉 `veille-prix/` — Surveillance de prix

Suit le prix de produits en ligne et signale les baisses. Utile pour acheter au bon
moment, ou repérer des affaires à revendre (Vinted, leboncoin…).

```bash
python3 veille-prix/veille.py add "PS5 occasion" "https://site.fr/produit"
python3 veille-prix/veille.py check    # relève les prix et compare au relevé précédent
python3 veille-prix/veille.py histo    # historique et prix minimum observé
```

Le prix est détecté automatiquement dans la page (format `299,99 €`).
Pour un relevé quotidien automatique, ajoute une ligne cron :

```
0 9 * * * cd /chemin/vers/le/repo && python3 veille-prix/veille.py check
```

## 📧 `relance/` — Mails de relance de facture

Un client ne paie pas ? Génère le mail de relance adapté, à copier-coller.

```bash
python3 relance/relance.py facture/ma_facture.json              # J+7 : rappel courtois
python3 relance/relance.py facture/ma_facture.json --niveau 2   # J+21 : relance ferme
python3 relance/relance.py facture/ma_facture.json --niveau 3   # J+35 : dernier avis
```

## 📈 `tjm/` — Calculateur de tarif freelance

Combien facturer pour gagner ce que tu veux ? Réponse en une commande.

```bash
python3 tjm/tjm.py 2000                # je veux 2000 € net/mois
python3 tjm/tjm.py 2000 --jours 12     # en facturant 12 jours/mois
```

Affiche le CA à réaliser, le TJM, le taux horaire, et prévient si tu
dépasses le plafond micro-entreprise.

## 🤝 `partage/` — Dépenses de groupe

Vacances, coloc, resto : qui doit combien à qui, avec le minimum de virements.

```bash
python3 partage/partage.py add "Alice" 30 "Courses"                 # partagé entre tous
python3 partage/partage.py add "Bob" 45 "Essence" --pour Alice Bob  # entre certains
python3 partage/partage.py solde    # qui est en + / en −
python3 partage/partage.py regle    # « Bob → Alice : 10.00 € »
python3 partage/partage.py reset    # archive et repart de zéro
```

## 🔐 `motdepasse/` — Générateur de mots de passe

Aléa cryptographique (module `secrets`), jamais stocké nulle part.

```bash
python3 motdepasse/mdp.py               # 20 caractères robustes
python3 motdepasse/mdp.py gen -l 32     # plus long
python3 motdepasse/mdp.py phrase        # « noyau-lune-canard-badge-piano-65 »
python3 motdepasse/mdp.py pin           # code PIN 6 chiffres
```

## 📅 `rappels/` — Dates importantes

Anniversaires (annuels) et échéances (uniques), triés par urgence.

```bash
python3 rappels/rappels.py add "Anniv Maman" 03-14             # tous les ans
python3 rappels/rappels.py add "Rendre le rapport" 2026-09-30  # une fois
python3 rappels/rappels.py list      # tout
python3 rappels/rappels.py bientot   # dans les 14 jours — à mettre dans ~/.bashrc
```

## 💸 `abonnements/` — Suivi d'abonnements

Sais enfin ce que tes abonnements te coûtent vraiment, et vois venir les prélèvements.

```bash
python3 abonnements/abos.py add "Netflix" 13.49 mensuel --jour 15
python3 abonnements/abos.py add "Assurance" 120 annuel --date 2026-09-01
python3 abonnements/abos.py list        # coût total €/mois et €/an
python3 abonnements/abos.py prochains   # prélèvements dans les 30 jours
python3 abonnements/abos.py rm "Netflix"
```

## ⏱ `tempo/` — Pointeuse freelance

Mesure ton temps réel par projet pour facturer juste (et prouver tes heures).

```bash
python3 tempo/tempo.py start "Site Dupont"   # au début du travail
python3 tempo/tempo.py stop                  # à la fin
python3 tempo/tempo.py bilan --tjm 350       # heures + montant à facturer
```

## ✂️ `resiliation/` — Lettre de résiliation

Génère la lettre recommandée pour résilier un abonnement (salle, box, assurance…).

```bash
python3 resiliation/resiliation.py "Salle FitPlus" --numero C-12345 \
    --nom "Ton Nom" --adresse "12 rue Exemple, 75000 Paris"
python3 resiliation/resiliation.py "Salle FitPlus" --motif demenagement ...  # résiliation anticipée
```

## 🎯 `epargne/` — Objectif d'épargne

```bash
python3 epargne/epargne.py 3000 2027-06-01              # 3000 € pour juin 2027
python3 epargne/epargne.py 3000 2027-06-01 --deja 500 --taux 3   # Livret A à 3 %
```

Donne le versement mensuel (et hebdo), intérêts composés inclus si tu places l'argent.

## 🚗 `trajet/` — Coût d'un trajet en voiture

```bash
python3 trajet/trajet.py 450 --peage 35 --passagers 3
```

Carburant + péages + usure du véhicule, et la juste part de chaque passager
(pratique pour fixer un prix de covoiturage honnête).

## 🛒 `courses/` — Liste de courses

```bash
python3 courses/courses.py add "pâtes" "tomates" "parmesan"
python3 courses/courses.py               # afficher
python3 courses/courses.py done "pâtes"  # coché
python3 courses/courses.py clear         # retire ce qui est coché
```

## Tests

```bash
python3 -m unittest discover tests
```

Les tests tournent aussi automatiquement en CI (GitHub Actions) à chaque push.

## Notes

- Tes données (opérations, historiques de prix, factures générées) restent en local
  et sont ignorées par git (`.gitignore`) — seul le code est versionné.
- Testé avec Python 3.8+.
