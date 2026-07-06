#!/usr/bin/env python3
"""Compter les jours — entre deux dates, ou à partir d'aujourd'hui.

Usage :
  ./jours.py entre 2026-07-06 2026-12-25    # combien de jours entre deux dates
  ./jours.py dans 90                        # quelle date dans 90 jours ?
  ./jours.py avant 2026-12-25               # combien de jours avant cette date ?
"""

import sys
from datetime import date, timedelta


def entre(d1, d2):
    return abs((d2 - d1).days)


def dans(n, depuis=None):
    return (depuis or date.today()) + timedelta(days=n)


if __name__ == "__main__":
    args = sys.argv[1:]
    try:
        if args[:1] == ["entre"] and len(args) == 3:
            d1, d2 = date.fromisoformat(args[1]), date.fromisoformat(args[2])
            j = entre(d1, d2)
            print(f"{j} jours ({j // 7} semaines et {j % 7} jours)")
        elif args[:1] == ["dans"] and len(args) == 2:
            cible = dans(int(args[1]))
            print(f"Dans {args[1]} jours : {cible.strftime('%d/%m/%Y')}")
        elif args[:1] == ["avant"] and len(args) == 2:
            j = (date.fromisoformat(args[1]) - date.today()).days
            print(f"{j} jours" if j >= 0 else f"date passée depuis {-j} jours")
        else:
            print(__doc__.strip())
            sys.exit(1)
    except ValueError:
        print(__doc__.strip())
        sys.exit(1)
