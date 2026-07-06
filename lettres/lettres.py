#!/usr/bin/env python3
"""Nombre en toutes lettres (français) — pratique pour les chèques et contrats.

Usage :
  ./lettres.py 1234        # → mille-deux-cent-trente-quatre
  ./lettres.py 80          # → quatre-vingts

Gère les subtilités : 71 → soixante-et-onze, 80 → quatre-vingts,
200 → deux-cents, 201 → deux-cent-un… (orthographe rectifiée : traits d'union partout)
"""

import sys

UNITES = ["zéro", "un", "deux", "trois", "quatre", "cinq", "six", "sept",
          "huit", "neuf", "dix", "onze", "douze", "treize", "quatorze",
          "quinze", "seize", "dix-sept", "dix-huit", "dix-neuf"]
DIZAINES = {20: "vingt", 30: "trente", 40: "quarante", 50: "cinquante", 60: "soixante"}


def _moins_de_cent(n):
    if n < 20:
        return UNITES[n]
    if n < 70:
        d, r = n // 10 * 10, n % 10
        if r == 0:
            return DIZAINES[d]
        if r == 1:
            return f"{DIZAINES[d]}-et-un"
        return f"{DIZAINES[d]}-{UNITES[r]}"
    if n < 80:
        return "soixante-et-onze" if n == 71 else f"soixante-{UNITES[n - 60]}"
    if n == 80:
        return "quatre-vingts"
    return f"quatre-vingt-{UNITES[n - 80]}"


def _moins_de_mille(n):
    if n < 100:
        return _moins_de_cent(n)
    c, r = n // 100, n % 100
    if c == 1:
        prefixe = "cent"
    else:
        prefixe = f"{UNITES[c]}-cent"
    if r == 0:
        return prefixe + ("s" if c > 1 else "")
    return f"{prefixe}-{_moins_de_cent(r)}"


def en_lettres(n):
    if not 0 <= n < 1_000_000:
        raise ValueError("nombre entre 0 et 999 999")
    if n < 1000:
        return _moins_de_mille(n)
    m, r = n // 1000, n % 1000
    prefixe = "mille" if m == 1 else f"{_moins_de_mille(m)}-mille"
    if r == 0:
        return prefixe
    return f"{prefixe}-{_moins_de_mille(r)}"


if __name__ == "__main__":
    try:
        n = int(sys.argv[1])
        print(en_lettres(n))
    except (IndexError, ValueError) as e:
        print(f"✗ {e}" if isinstance(e, ValueError) and sys.argv[1:] else __doc__.strip())
        sys.exit(1)
