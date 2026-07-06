#!/usr/bin/env python3
"""« On mange quoi ce soir ? » — le tirage au sort qui met tout le monde d'accord.

Usage :
  ./menu.py             # une idée de repas
  ./menu.py rapide      # prêt en moins de 20 minutes
  ./menu.py semaine     # planning de 7 repas d'un coup
"""

import random
import sys

PLATS = [
    "Pâtes carbonara", "Gratin dauphinois", "Poulet rôti et frites maison",
    "Bœuf bourguignon", "Lasagnes", "Blanquette de veau", "Ratatouille et riz",
    "Chili con carne", "Curry de légumes", "Couscous", "Paëlla", "Risotto aux champignons",
    "Tartiflette", "Raclette", "Hachis parmentier", "Quiche lorraine et salade",
    "Poisson pané et purée", "Saumon rôti et haricots verts", "Tajine de poulet",
    "Burger maison", "Pizza maison", "Fajitas", "Pad thaï", "Ramen", "Bibimbap",
]

RAPIDES = [
    "Omelette champignons-fromage", "Pâtes ail-huile d'olive-parmesan",
    "Croque-monsieur et salade", "Salade César", "Wrap poulet-crudités",
    "Œufs brouillés sur toast", "Riz sauté aux restes du frigo", "Quesadillas",
    "Soupe + tartines de chèvre", "Gnocchis poêlés au beurre de sauge",
    "Nouilles sautées aux légumes", "Taboulé express", "Tartine avocat-œuf poché",
]


def idee(rapide=False):
    return random.choice(RAPIDES if rapide else PLATS)


def semaine():
    pool = PLATS + RAPIDES
    return random.sample(pool, 7)


if __name__ == "__main__":
    args = sys.argv[1:]
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    if args[:1] == ["semaine"]:
        for jour, plat in zip(jours, semaine()):
            print(f"  {jour:<9} {plat}")
    elif args[:1] == ["rapide"]:
        print(f"🍳 {idee(rapide=True)} (moins de 20 min)")
    elif not args:
        print(f"🍽 {idee()}")
    else:
        print(__doc__.strip())
        sys.exit(1)
