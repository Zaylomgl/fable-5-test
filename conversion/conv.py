#!/usr/bin/env python3
"""Conversions d'unités courantes.

Usage :
  ./conv.py 10 km miles        ./conv.py 72 f c          ./conv.py 3 h min
  ./conv.py 80 kg lbs          ./conv.py 1.5 l oz        ./conv.py 100 m2 ft2

Unités : km/miles/m/ft/cm/in — kg/lbs/g/oz — l/gal/ml — c/f — h/min/s — m2/ft2
"""

import sys

# facteurs vers l'unité pivot de chaque famille
FAMILLES = {
    "longueur": {"km": 1000.0, "m": 1.0, "cm": 0.01, "miles": 1609.344, "ft": 0.3048, "in": 0.0254},
    "poids": {"kg": 1000.0, "g": 1.0, "lbs": 453.59237, "oz": 28.349523},
    "volume": {"l": 1.0, "ml": 0.001, "gal": 3.785411784},
    "temps": {"h": 3600.0, "min": 60.0, "s": 1.0},
    "surface": {"m2": 1.0, "ft2": 0.09290304},
}


def convertir(valeur, depuis, vers):
    depuis, vers = depuis.lower(), vers.lower()
    if {depuis, vers} <= {"c", "f"}:
        if depuis == vers:
            return valeur
        return valeur * 9 / 5 + 32 if depuis == "c" else (valeur - 32) * 5 / 9
    for unites in FAMILLES.values():
        if depuis in unites and vers in unites:
            return valeur * unites[depuis] / unites[vers]
    raise ValueError(f"conversion {depuis} → {vers} inconnue")


if __name__ == "__main__":
    try:
        valeur, depuis, vers = float(sys.argv[1]), sys.argv[2], sys.argv[3]
        print(f"{valeur:g} {depuis} = {convertir(valeur, depuis, vers):.4g} {vers}")
    except (IndexError, ValueError) as e:
        if isinstance(e, ValueError) and "inconnue" in str(e):
            print(f"✗ {e}")
        else:
            print(__doc__.strip())
        sys.exit(1)
