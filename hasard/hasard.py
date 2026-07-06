#!/usr/bin/env python3
"""Le hasard qui tranche — pile ou face, dés, tirage au sort.

Usage :
  ./hasard.py pile                          # pile ou face
  ./hasard.py de                            # un dé à 6 faces
  ./hasard.py de 20                         # un dé à 20 faces
  ./hasard.py entre 1 100                   # un nombre entre 1 et 100
  ./hasard.py choisis "pizza" "sushi" "kebab"   # tranche pour toi
  ./hasard.py melange "Alice" "Bob" "Chloé"     # ordre de passage aléatoire
"""

import random
import sys


def pile_ou_face():
    return random.choice(["PILE", "FACE"])


def de(faces=6):
    return random.randint(1, faces)


def entre(a, b):
    return random.randint(a, b)


def choisis(options):
    return random.choice(options)


def melange(options):
    resultat = list(options)
    random.shuffle(resultat)
    return resultat


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["pile"]:
        print(f"🪙 {pile_ou_face()} !")
    elif args[:1] == ["de"]:
        faces = int(args[1]) if len(args) > 1 else 6
        print(f"🎲 {de(faces)} (dé à {faces} faces)")
    elif args[:1] == ["entre"] and len(args) == 3:
        print(entre(int(args[1]), int(args[2])))
    elif args[:1] == ["choisis"] and len(args) > 1:
        print(f"👉 {choisis(args[1:])}")
    elif args[:1] == ["melange"] and len(args) > 1:
        for i, x in enumerate(melange(args[1:]), 1):
            print(f"  {i}. {x}")
    else:
        print(__doc__.strip())
        sys.exit(1)
