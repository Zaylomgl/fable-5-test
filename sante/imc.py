#!/usr/bin/env python3
"""IMC et besoins en eau — indicatif seulement, pas un avis médical.

Usage :
  ./imc.py 70 1.78          # poids (kg), taille (m)
"""

import sys


def imc(poids, taille):
    return poids / taille ** 2


def categorie(valeur):
    if valeur < 18.5:
        return "insuffisance pondérale"
    if valeur < 25:
        return "corpulence normale"
    if valeur < 30:
        return "surpoids"
    return "obésité"


if __name__ == "__main__":
    try:
        poids, taille = float(sys.argv[1]), float(sys.argv[2])
    except (IndexError, ValueError):
        print(__doc__.strip())
        sys.exit(1)
    v = imc(poids, taille)
    print(f"IMC : {v:.1f} — {categorie(v)} (fourchette normale : 18.5 à 25)")
    print(f"Eau conseillée : ≈ {poids * 0.033:.1f} L/jour")
    print("(repères OMS indicatifs — parles-en à un médecin si besoin)")
