#!/usr/bin/env python3
"""Jours fériés français — calculés, aucune donnée externe.

Usage :
  ./feries.py               # les fériés de l'année, prochains en évidence
  ./feries.py 2027          # ceux d'une autre année
  ./feries.py prochain      # juste le prochain (et dans combien de jours)
"""

import sys
from datetime import date, timedelta


def paques(annee):
    """Dimanche de Pâques (algorithme de Butcher-Meeus)."""
    a, b, c = annee % 19, annee // 100, annee % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mois = (h + l - 7 * m + 114) // 31
    jour = (h + l - 7 * m + 114) % 31 + 1
    return date(annee, mois, jour)


def jours_feries(annee):
    p = paques(annee)
    return sorted({
        date(annee, 1, 1): "Jour de l'an",
        p + timedelta(days=1): "Lundi de Pâques",
        date(annee, 5, 1): "Fête du Travail",
        date(annee, 5, 8): "Victoire 1945",
        p + timedelta(days=39): "Ascension",
        p + timedelta(days=50): "Lundi de Pentecôte",
        date(annee, 7, 14): "Fête nationale",
        date(annee, 8, 15): "Assomption",
        date(annee, 11, 1): "Toussaint",
        date(annee, 11, 11): "Armistice 1918",
        date(annee, 12, 25): "Noël",
    }.items())


def prochain(aujourd_hui=None):
    auj = aujourd_hui or date.today()
    for annee in (auj.year, auj.year + 1):
        for jour, nom in jours_feries(annee):
            if jour >= auj:
                return jour, nom
    raise RuntimeError("introuvable")


JOURS_SEMAINE = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]

if __name__ == "__main__":
    args = sys.argv[1:]
    auj = date.today()
    if args[:1] == ["prochain"]:
        jour, nom = prochain()
        dans = (jour - auj).days
        quand = "aujourd'hui 🎉" if dans == 0 else f"dans {dans} jours"
        print(f"Prochain férié : {nom}, {JOURS_SEMAINE[jour.weekday()]} "
              f"{jour.strftime('%d/%m/%Y')} ({quand})")
    else:
        annee = int(args[0]) if args else auj.year
        for jour, nom in jours_feries(annee):
            marqueur = "  ← prochain" if annee == auj.year and jour >= auj and \
                (prochain()[0] == jour) else ""
            weekend = " (week-end 😞)" if jour.weekday() >= 5 else ""
            print(f"  {jour.strftime('%d/%m')}  {JOURS_SEMAINE[jour.weekday()]:<9} "
                  f"{nom}{weekend}{marqueur}")
