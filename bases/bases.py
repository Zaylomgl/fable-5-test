#!/usr/bin/env python3
"""Conversions décimal / binaire / hexadécimal / octal — pour les cours et le code.

Usage :
  ./bases.py 255            # décimal → tout
  ./bases.py 0xff           # hexadécimal → tout
  ./bases.py 0b1010         # binaire → tout
  ./bases.py 0o777          # octal → tout
"""

import sys


def convertir(texte):
    n = int(texte, 0)  # détecte 0x/0b/0o tout seul
    return {
        "decimal": str(n),
        "binaire": bin(n),
        "hexadecimal": hex(n),
        "octal": oct(n),
    }


if __name__ == "__main__":
    try:
        r = convertir(sys.argv[1])
    except (IndexError, ValueError):
        print(__doc__.strip())
        sys.exit(1)
    print(f"  Décimal      : {r['decimal']}")
    print(f"  Binaire      : {r['binaire']}")
    print(f"  Hexadécimal  : {r['hexadecimal']}")
    print(f"  Octal        : {r['octal']}")
