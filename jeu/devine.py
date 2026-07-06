#!/usr/bin/env python3
"""Devine le nombre — le jeu classique, pour tuer 2 minutes.

Usage :
  ./devine.py           # entre 1 et 100
  ./devine.py 1000      # entre 1 et 1000
"""

import math
import random
import sys


def partie(maximum=100, entree=input, sortie=print):
    secret = random.randint(1, maximum)
    optimal = math.ceil(math.log2(maximum))
    sortie(f"J'ai choisi un nombre entre 1 et {maximum}. Trouve-le !")
    essais = 0
    while True:
        try:
            n = int(entree("> "))
        except (ValueError, EOFError):
            sortie("Un nombre, s'il te plaît !")
            continue
        essais += 1
        if n < secret:
            sortie("C'est plus ⬆")
        elif n > secret:
            sortie("C'est moins ⬇")
        else:
            sortie(f"🎉 Trouvé en {essais} essai(s) ! "
                   f"(l'optimal par dichotomie : ~{optimal})")
            return essais


if __name__ == "__main__":
    maximum = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    try:
        partie(maximum)
    except KeyboardInterrupt:
        print("\nAbandon 😏")
