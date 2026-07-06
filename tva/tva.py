#!/usr/bin/env python3
"""TVA : HT ↔ TTC en une commande.

Usage :
  ./tva.py ttc 100            # 100 € HT → TTC (20 %)
  ./tva.py ht 120             # 120 € TTC → HT (20 %)
  ./tva.py ttc 100 --taux 5.5 # taux réduit (10, 5.5, 2.1…)
"""

import argparse


def vers_ttc(ht, taux=20.0):
    return ht * (1 + taux / 100)


def vers_ht(ttc, taux=20.0):
    return ttc / (1 + taux / 100)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Calculs de TVA")
    p.add_argument("sens", choices=["ttc", "ht"])
    p.add_argument("montant", type=float)
    p.add_argument("--taux", type=float, default=20.0)
    args = p.parse_args()
    if args.sens == "ttc":
        ttc = vers_ttc(args.montant, args.taux)
        print(f"{args.montant:.2f} € HT = {ttc:.2f} € TTC "
              f"(TVA {args.taux:g} % : {ttc - args.montant:.2f} €)")
    else:
        ht = vers_ht(args.montant, args.taux)
        print(f"{args.montant:.2f} € TTC = {ht:.2f} € HT "
              f"(TVA {args.taux:g} % : {args.montant - ht:.2f} €)")
