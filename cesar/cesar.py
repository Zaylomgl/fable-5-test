#!/usr/bin/env python3
"""Chiffre de César — pour jouer aux messages secrets (pas pour tes vrais secrets !).

Usage :
  ./cesar.py code "rendez-vous a midi" 3      # décale de 3
  ./cesar.py lis "uhqghc-yrxv d plgl" 3       # déchiffre
  ./cesar.py casse "uhqghc-yrxv d plgl"       # essaie les 25 décalages
"""

import sys


def decaler(texte, n):
    resultat = []
    for c in texte:
        if c.isalpha() and c.isascii():
            base = ord("A") if c.isupper() else ord("a")
            resultat.append(chr((ord(c) - base + n) % 26 + base))
        else:
            resultat.append(c)
    return "".join(resultat)


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["code"] and len(args) == 3:
        print(decaler(args[1], int(args[2])))
    elif args[:1] == ["lis"] and len(args) == 3:
        print(decaler(args[1], -int(args[2])))
    elif args[:1] == ["casse"] and len(args) == 2:
        for n in range(1, 26):
            print(f"  {n:>2} : {decaler(args[1], -n)}")
    else:
        print(__doc__.strip())
        sys.exit(1)
