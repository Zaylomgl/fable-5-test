#!/usr/bin/env python3
"""Calculs de pourcentages sans se tromper.

Usage :
  ./pct.py de 20 150            # 20 % de 150 → 30
  ./pct.py remise 25 80         # 80 € avec −25 % → 60 €
  ./pct.py hausse 10 1200       # 1200 € +10 % → 1320 €
  ./pct.py part 30 120          # 30 est quel % de 120 ? → 25 %
  ./pct.py evolution 80 100     # de 80 à 100 → +25 %
"""

import sys


def de(pct, valeur):
    return valeur * pct / 100


def remise(pct, valeur):
    return valeur * (1 - pct / 100)


def hausse(pct, valeur):
    return valeur * (1 + pct / 100)


def part(x, total):
    return x / total * 100


def evolution(avant, apres):
    return (apres - avant) / avant * 100


if __name__ == "__main__":
    args = sys.argv[1:]
    try:
        cmd, a, b = args[0], float(args[1]), float(args[2])
    except (IndexError, ValueError):
        print(__doc__.strip())
        sys.exit(1)
    if cmd == "de":
        print(f"{a:g} % de {b:g} = {de(a, b):g}")
    elif cmd == "remise":
        print(f"{b:g} avec −{a:g} % = {remise(a, b):g}  (tu économises {de(a, b):g})")
    elif cmd == "hausse":
        print(f"{b:g} avec +{a:g} % = {hausse(a, b):g}")
    elif cmd == "part":
        print(f"{a:g} représente {part(a, b):.1f} % de {b:g}")
    elif cmd == "evolution":
        e = evolution(a, b)
        print(f"de {a:g} à {b:g} : {e:+.1f} %")
    else:
        print(__doc__.strip())
        sys.exit(1)
