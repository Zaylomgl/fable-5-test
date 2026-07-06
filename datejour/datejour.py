#!/usr/bin/env python3
"""Tout sur une date — numéro de semaine, jour de l'année, bissextile…

Usage :
  ./datejour.py                 # aujourd'hui
  ./datejour.py 2026-12-25      # une autre date
"""

import calendar
import sys
from datetime import date

JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]


def infos(d):
    total = 366 if calendar.isleap(d.year) else 365
    jour_annee = d.timetuple().tm_yday
    return {
        "libelle": f"{JOURS[d.weekday()]} {d.day} {MOIS[d.month - 1]} {d.year}",
        "semaine_iso": d.isocalendar()[1],
        "jour_annee": jour_annee,
        "jours_restants": total - jour_annee,
        "bissextile": calendar.isleap(d.year),
        "trimestre": (d.month - 1) // 3 + 1,
    }


if __name__ == "__main__":
    try:
        d = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()
    except ValueError:
        print(__doc__.strip())
        sys.exit(1)
    r = infos(d)
    print(f"  {r['libelle'].capitalize()}")
    print(f"  Semaine ISO n° {r['semaine_iso']}, {r['trimestre']}ᵉ trimestre")
    print(f"  {r['jour_annee']}ᵉ jour de l'année — il en reste {r['jours_restants']}")
    print(f"  Année bissextile : {'oui' if r['bissextile'] else 'non'}")
