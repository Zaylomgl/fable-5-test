#!/usr/bin/env python3
"""Outils texte : compter, nettoyer, transformer.

Usage :
  ./texte.py stats "Mon texte à analyser"     # mots, caractères, temps de lecture
  ./texte.py stats fichier.txt                # marche aussi sur un fichier
  ./texte.py slug "Mon Titre d'Article !"     # → mon-titre-d-article
  ./texte.py maj "bonjour"                    # → BONJOUR
  ./texte.py min "BONJOUR"                    # → bonjour
"""

import re
import sys
import unicodedata
from pathlib import Path


def stats(texte):
    mots = len(texte.split())
    return {
        "mots": mots,
        "caracteres": len(texte),
        "caracteres_sans_espaces": len(texte.replace(" ", "").replace("\n", "")),
        "lignes": texte.count("\n") + 1 if texte else 0,
        "minutes_lecture": max(round(mots / 200), 1) if mots else 0,
    }


def slug(texte):
    sans_accents = unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", sans_accents.lower()).strip("-")


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) < 2:
        print(__doc__.strip())
        sys.exit(1)
    cmd, contenu = args[0], " ".join(args[1:])
    if cmd == "stats" and Path(contenu).is_file():
        contenu = Path(contenu).read_text(encoding="utf-8")
    if cmd == "stats":
        s = stats(contenu)
        print(f"  Mots                 : {s['mots']}")
        print(f"  Caractères           : {s['caracteres']} ({s['caracteres_sans_espaces']} sans espaces)")
        print(f"  Lignes               : {s['lignes']}")
        print(f"  Lecture              : ≈ {s['minutes_lecture']} min")
    elif cmd == "slug":
        print(slug(contenu))
    elif cmd == "maj":
        print(contenu.upper())
    elif cmd == "min":
        print(contenu.lower())
    else:
        print(__doc__.strip())
        sys.exit(1)
