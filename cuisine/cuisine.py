#!/usr/bin/env python3
"""Conversions de cuisine — cuillères, tasses, grammes, sans balance.

Usage :
  ./cuisine.py 3 cas ml               # cuillères à soupe → ml
  ./cuisine.py 250 ml tasse           # ml → tasses
  ./cuisine.py 2 tasse g farine       # volumes → grammes (farine, sucre, beurre, riz…)
"""

import sys

VOLUMES_ML = {"ml": 1.0, "cl": 10.0, "l": 1000.0, "cac": 5.0, "cas": 15.0,
              "tasse": 250.0, "verre": 200.0, "bol": 350.0}
# densité approximative en g/ml
DENSITES = {"eau": 1.0, "lait": 1.03, "farine": 0.55, "sucre": 0.85,
            "sucre_glace": 0.56, "beurre": 0.91, "huile": 0.92, "riz": 0.85,
            "miel": 1.4, "cacao": 0.52, "sel": 1.2}


def convertir(valeur, depuis, vers, ingredient=None):
    depuis, vers = depuis.lower(), vers.lower()
    if depuis in VOLUMES_ML and vers in VOLUMES_ML:
        return valeur * VOLUMES_ML[depuis] / VOLUMES_ML[vers]
    if depuis in VOLUMES_ML and vers == "g":
        if not ingredient or ingredient not in DENSITES:
            raise ValueError(f"précise l'ingrédient : {', '.join(sorted(DENSITES))}")
        return valeur * VOLUMES_ML[depuis] * DENSITES[ingredient]
    if depuis == "g" and vers in VOLUMES_ML:
        if not ingredient or ingredient not in DENSITES:
            raise ValueError(f"précise l'ingrédient : {', '.join(sorted(DENSITES))}")
        return valeur / DENSITES[ingredient] / VOLUMES_ML[vers]
    raise ValueError(f"conversion {depuis} → {vers} inconnue")


if __name__ == "__main__":
    try:
        valeur, depuis, vers = float(sys.argv[1]), sys.argv[2], sys.argv[3]
        ingredient = sys.argv[4].lower() if len(sys.argv) > 4 else None
        r = convertir(valeur, depuis, vers, ingredient)
        extra = f" de {ingredient}" if ingredient else ""
        print(f"{valeur:g} {depuis}{extra} = {r:.4g} {vers}")
    except ValueError as e:
        print(f"✗ {e}")
        sys.exit(1)
    except IndexError:
        print(__doc__.strip())
        sys.exit(1)
