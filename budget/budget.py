#!/usr/bin/env python3
"""Suivi de budget perso — zéro dépendance, données en CSV local.

Usage :
  ./budget.py add 12.50 courses "Carrefour"     # ajouter une dépense
  ./budget.py add 850 revenu "Salaire" --in     # ajouter un revenu
  ./budget.py list                              # dernières opérations
  ./budget.py mois                              # bilan du mois en cours
  ./budget.py mois 2026-06                      # bilan d'un mois précis
  ./budget.py cat                               # dépenses par catégorie (mois en cours)
"""

import argparse
import csv
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

FICHIER = Path(__file__).parent / "operations.csv"
COLONNES = ["date", "montant", "categorie", "note"]


def charger():
    if not FICHIER.exists():
        return []
    with FICHIER.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def sauver_ligne(ligne):
    nouveau = not FICHIER.exists()
    with FICHIER.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLONNES)
        if nouveau:
            w.writeheader()
        w.writerow(ligne)


def cmd_add(args):
    montant = args.montant if args.entree else -args.montant
    ligne = {
        "date": args.date or date.today().isoformat(),
        "montant": f"{montant:.2f}",
        "categorie": args.categorie.lower(),
        "note": args.note or "",
    }
    sauver_ligne(ligne)
    sens = "revenu" if args.entree else "dépense"
    print(f"✓ {sens} de {abs(montant):.2f} € ({ligne['categorie']}) enregistré")


def cmd_list(args):
    ops = charger()[-args.n:]
    if not ops:
        print("Aucune opération. Ajoute-en une avec : budget.py add 12.50 courses")
        return
    for op in ops:
        m = float(op["montant"])
        print(f"{op['date']}  {m:>+10.2f} €  {op['categorie']:<12} {op['note']}")


def ops_du_mois(mois):
    return [op for op in charger() if op["date"].startswith(mois)]


def cmd_mois(args):
    mois = args.mois or date.today().isoformat()[:7]
    ops = ops_du_mois(mois)
    if not ops:
        print(f"Aucune opération en {mois}.")
        return
    entrees = sum(float(o["montant"]) for o in ops if float(o["montant"]) > 0)
    sorties = sum(-float(o["montant"]) for o in ops if float(o["montant"]) < 0)
    print(f"Bilan {mois}")
    print(f"  Entrées : {entrees:>9.2f} €")
    print(f"  Sorties : {sorties:>9.2f} €")
    print(f"  Solde   : {entrees - sorties:>9.2f} €")


def cmd_cat(args):
    mois = args.mois or date.today().isoformat()[:7]
    totaux = defaultdict(float)
    for op in ops_du_mois(mois):
        m = float(op["montant"])
        if m < 0:
            totaux[op["categorie"]] += -m
    if not totaux:
        print(f"Aucune dépense en {mois}.")
        return
    total = sum(totaux.values())
    print(f"Dépenses par catégorie — {mois} (total {total:.2f} €)")
    for cat, somme in sorted(totaux.items(), key=lambda x: -x[1]):
        barre = "█" * max(1, round(somme / total * 30))
        print(f"  {cat:<12} {somme:>9.2f} €  {barre}")


def main():
    p = argparse.ArgumentParser(description="Suivi de budget perso")
    sub = p.add_subparsers(dest="cmd", required=True)

    pa = sub.add_parser("add", help="ajouter une opération")
    pa.add_argument("montant", type=float)
    pa.add_argument("categorie")
    pa.add_argument("note", nargs="?", default="")
    pa.add_argument("--in", dest="entree", action="store_true", help="revenu (entrée d'argent)")
    pa.add_argument("--date", help="AAAA-MM-JJ (défaut : aujourd'hui)")
    pa.set_defaults(func=cmd_add)

    pl = sub.add_parser("list", help="dernières opérations")
    pl.add_argument("-n", type=int, default=20)
    pl.set_defaults(func=cmd_list)

    pm = sub.add_parser("mois", help="bilan mensuel")
    pm.add_argument("mois", nargs="?", help="AAAA-MM (défaut : mois en cours)")
    pm.set_defaults(func=cmd_mois)

    pc = sub.add_parser("cat", help="dépenses par catégorie")
    pc.add_argument("mois", nargs="?", help="AAAA-MM (défaut : mois en cours)")
    pc.set_defaults(func=cmd_cat)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    sys.exit(main())
