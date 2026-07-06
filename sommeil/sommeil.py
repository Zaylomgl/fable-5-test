#!/usr/bin/env python3
"""À quelle heure se coucher ? — basé sur les cycles de sommeil de 90 minutes.

Usage :
  ./sommeil.py lever 07:00     # je dois me lever à 7h → heures de coucher idéales
  ./sommeil.py coucher 23:30   # je me couche maintenant → heures de réveil idéales

Compte ~15 min pour s'endormir. Se réveiller en fin de cycle = moins de brouillard.
"""

import sys
from datetime import datetime, timedelta

CYCLE = timedelta(minutes=90)
ENDORMISSEMENT = timedelta(minutes=15)


def heures_de_coucher(lever, cycles=(6, 5, 4)):
    """Heures de coucher pour se lever à `lever` en finissant un cycle."""
    return [(lever - n * CYCLE - ENDORMISSEMENT, n) for n in cycles]


def heures_de_reveil(coucher, cycles=(4, 5, 6)):
    return [(coucher + ENDORMISSEMENT + n * CYCLE, n) for n in cycles]


def _parse(hhmm):
    return datetime.strptime(hhmm, "%H:%M")


if __name__ == "__main__":
    args = sys.argv[1:]
    try:
        cmd, quand = args[0], _parse(args[1])
    except (IndexError, ValueError):
        print(__doc__.strip())
        sys.exit(1)
    if cmd == "lever":
        print(f"Pour te lever à {args[1]} en pleine forme, couche-toi à :")
        for h, n in heures_de_coucher(quand):
            heures = n * 1.5
            print(f"  {h.strftime('%H:%M')}  ({n} cycles ≈ {heures:g} h de sommeil)"
                  + ("  ← idéal" if n == 5 else ""))
    elif cmd == "coucher":
        print(f"Si tu te couches à {args[1]}, règle ton réveil à :")
        for h, n in heures_de_reveil(quand):
            print(f"  {h.strftime('%H:%M')}  ({n} cycles ≈ {n * 1.5:g} h de sommeil)"
                  + ("  ← idéal" if n == 5 else ""))
    else:
        print(__doc__.strip())
        sys.exit(1)
