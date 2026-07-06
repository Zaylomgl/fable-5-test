# Boîte à outils perso

Quatre outils concrets, en français, **zéro dépendance** (Python 3 standard uniquement).
Aucune installation : clone le repo et lance les scripts.

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
