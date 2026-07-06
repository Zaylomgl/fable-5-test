#!/usr/bin/env python3
"""Chiffres romains ↔ arabes.

Usage :
  ./romain.py 2026        # → MMXXVI
  ./romain.py MCMXCIV     # → 1994
"""

import sys

VALEURS = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"),
           (90, "XC"), (50, "L"), (40, "XL"), (10, "X"), (9, "IX"),
           (5, "V"), (4, "IV"), (1, "I")]
LETTRES = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}


def vers_romain(n):
    if not 1 <= n <= 3999:
        raise ValueError("nombre entre 1 et 3999")
    resultat = []
    for valeur, lettres in VALEURS:
        while n >= valeur:
            resultat.append(lettres)
            n -= valeur
    return "".join(resultat)


def vers_arabe(romain):
    romain = romain.upper()
    if not romain or any(c not in LETTRES for c in romain):
        raise ValueError(f"chiffre romain invalide : {romain}")
    total = 0
    for i, c in enumerate(romain):
        v = LETTRES[c]
        if i + 1 < len(romain) and LETTRES[romain[i + 1]] > v:
            total -= v
        else:
            total += v
    if vers_romain(total) != romain:
        raise ValueError(f"chiffre romain mal formé : {romain}")
    return total


if __name__ == "__main__":
    try:
        arg = sys.argv[1]
    except IndexError:
        print(__doc__.strip())
        sys.exit(1)
    try:
        print(vers_romain(int(arg)) if arg.isdigit() else vers_arabe(arg))
    except ValueError as e:
        print(f"✗ {e}")
        sys.exit(1)
