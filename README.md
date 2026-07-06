# Boîte à outils perso

Neuf outils concrets, en français, **zéro dépendance** (Python 3 standard uniquement).
Aucune installation : clone le repo et lance les scripts.

| Outil | À quoi ça sert |
|---|---|
| 💶 `facture/` | Factures et devis pro pour tes missions freelance |
| 📧 `relance/` | Mails de relance pour factures impayées (3 niveaux) |
| 📈 `tjm/` | Calcule le tarif journalier à facturer selon le revenu visé |
| 📊 `budget/` | Suivi de dépenses/revenus, bilan mensuel |
| 💸 `abonnements/` | Coût réel de tes abonnements + prélèvements à venir |
| 📉 `veille-prix/` | Alerte quand un prix baisse |
| 🤝 `partage/` | Partage de dépenses entre potes/coloc (façon Tricount) |
| 🔐 `motdepasse/` | Mots de passe et phrases de passe sécurisés |
| 📅 `rappels/` | Anniversaires et échéances, avec compte à rebours |

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

## Tests

```bash
python3 -m unittest discover tests
```

Les tests tournent aussi automatiquement en CI (GitHub Actions) à chaque push.

## Notes

- Tes données (opérations, historiques de prix, factures générées) restent en local
  et sont ignorées par git (`.gitignore`) — seul le code est versionné.
- Testé avec Python 3.8+.
