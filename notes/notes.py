#!/usr/bin/env python3
"""Notes rapides en CLI — jeter une idée sans ouvrir d'app.

Usage :
  ./notes.py "Idée : appeler le proprio pour la caution"
  ./notes.py                    # tout relire
  ./notes.py cherche caution    # filtrer
  ./notes.py rm 2               # supprimer la note n° 2
"""

import json
import sys
from datetime import date
from pathlib import Path

FICHIER = Path(__file__).parent / "notes.json"


def charger():
    if not FICHIER.exists():
        return []
    return json.loads(FICHIER.read_text(encoding="utf-8"))


def sauver(notes):
    FICHIER.write_text(json.dumps(notes, ensure_ascii=False, indent=2), encoding="utf-8")


def afficher(notes):
    if not notes:
        print("Aucune note. Écris : notes.py \"mon idée\"")
        return
    for i, n in enumerate(notes, 1):
        print(f"  {i:>3}. [{n['date']}] {n['texte']}")


if __name__ == "__main__":
    args = sys.argv[1:]
    notes = charger()
    if not args:
        afficher(notes)
    elif args[0] == "cherche" and len(args) > 1:
        terme = " ".join(args[1:]).lower()
        afficher([n for n in notes if terme in n["texte"].lower()])
    elif args[0] == "rm" and len(args) == 2 and args[1].isdigit():
        i = int(args[1])
        if not 1 <= i <= len(notes):
            print(f"✗ pas de note n° {i}")
            sys.exit(1)
        supprimee = notes.pop(i - 1)
        sauver(notes)
        print(f"✓ Supprimée : {supprimee['texte']}")
    else:
        texte = " ".join(args)
        notes.append({"date": date.today().isoformat(), "texte": texte})
        sauver(notes)
        print(f"✓ Note n° {len(notes)} enregistrée")
