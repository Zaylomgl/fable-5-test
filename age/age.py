#!/usr/bin/env python3
"""Ton âge exact, en années, mois, jours… et le compte à rebours avant l'anniv.

Usage :
  ./age.py 2006-04-12
"""

import sys
from datetime import date


def age_exact(naissance, aujourd_hui=None):
    auj = aujourd_hui or date.today()
    annees = auj.year - naissance.year - (
        (auj.month, auj.day) < (naissance.month, naissance.day)
    )
    jours_vecus = (auj - naissance).days
    try:
        prochain = naissance.replace(year=auj.year)
    except ValueError:  # né un 29 février
        prochain = date(auj.year, 3, 1)
    if prochain < auj:
        try:
            prochain = naissance.replace(year=auj.year + 1)
        except ValueError:
            prochain = date(auj.year + 1, 3, 1)
    return {
        "annees": annees,
        "jours_vecus": jours_vecus,
        "prochain_anniv": prochain,
        "jours_avant_anniv": (prochain - auj).days,
    }


if __name__ == "__main__":
    try:
        naissance = date.fromisoformat(sys.argv[1])
    except (IndexError, ValueError):
        print(__doc__.strip())
        sys.exit(1)
    r = age_exact(naissance)
    def fmt(n):
        return f"{n:,}".replace(",", " ")

    print(f"Tu as {r['annees']} ans — soit {fmt(r['jours_vecus'])} jours vécus")
    print(f"≈ {fmt(r['jours_vecus'] * 24)} heures, {fmt(r['jours_vecus'] // 7)} semaines")
    if r["jours_avant_anniv"] == 0:
        print("🎂 JOYEUX ANNIVERSAIRE !")
    else:
        print(f"Prochain anniversaire : {r['prochain_anniv'].strftime('%d/%m/%Y')} "
              f"(dans {r['jours_avant_anniv']} jours)")
