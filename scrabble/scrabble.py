#!/usr/bin/env python3
"""Score d'un mot au Scrabble (barème français).

Usage :
  ./scrabble.py maison             # → 8 points
  ./scrabble.py whisky jazz        # plusieurs mots d'un coup
"""

import sys
import unicodedata

POINTS = {}
for lettres, pts in [("eainorstul", 1), ("dgm", 2), ("bcp", 3), ("fhv", 4),
                     ("jq", 8), ("kwxyz", 10)]:
    for lettre in lettres:
        POINTS[lettre] = pts


def score(mot):
    sans_accents = unicodedata.normalize("NFKD", mot).encode("ascii", "ignore").decode()
    return sum(POINTS.get(c, 0) for c in sans_accents.lower())


if __name__ == "__main__":
    mots = sys.argv[1:]
    if not mots:
        print(__doc__.strip())
        sys.exit(1)
    for mot in sorted(mots, key=score, reverse=True):
        print(f"  {mot:<15} {score(mot):>3} points")
