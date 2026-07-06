#!/usr/bin/env python3
"""Addition au resto : pourboire et partage en un coup d'œil.

Usage :
  ./pourboire.py 84.50                      # addition seule, partage à 1
  ./pourboire.py 84.50 --tip 10 --pers 4    # +10 % de pourboire, à 4
"""

import argparse


def calculer(addition, tip_pct=0.0, personnes=1):
    pourboire = addition * tip_pct / 100
    total = addition + pourboire
    return {"pourboire": pourboire, "total": total,
            "par_personne": total / max(personnes, 1)}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Pourboire et partage d'addition")
    p.add_argument("addition", type=float)
    p.add_argument("--tip", type=float, default=0.0, help="pourboire en %%")
    p.add_argument("--pers", type=int, default=1, help="nombre de personnes")
    args = p.parse_args()
    r = calculer(args.addition, args.tip, args.pers)
    if args.tip:
        print(f"  Pourboire ({args.tip:g} %) : {r['pourboire']:.2f} €")
    print(f"  Total : {r['total']:.2f} €")
    if args.pers > 1:
        print(f"  À {args.pers} : {r['par_personne']:.2f} € chacun")
