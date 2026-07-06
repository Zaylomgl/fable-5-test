#!/usr/bin/env python3
"""Liste de courses en CLI — rapide, locale, sans app.

Usage :
  ./courses.py add "pâtes" "tomates" "parmesan"   # ajouter (plusieurs d'un coup)
  ./courses.py                                    # afficher la liste
  ./courses.py done "pâtes"                       # coché (acheté)
  ./courses.py clear                              # vider les articles cochés
"""

import json
import sys
from pathlib import Path

FICHIER = Path(__file__).parent / "liste.json"


def charger():
    if not FICHIER.exists():
        return []
    return json.loads(FICHIER.read_text(encoding="utf-8"))


def sauver(liste):
    FICHIER.write_text(json.dumps(liste, ensure_ascii=False, indent=2), encoding="utf-8")


def cmd_add(articles):
    liste = charger()
    existants = {a["nom"].lower() for a in liste}
    ajoutes = 0
    for nom in articles:
        if nom.lower() not in existants:
            liste.append({"nom": nom, "fait": False})
            ajoutes += 1
    sauver(liste)
    print(f"✓ {ajoutes} article(s) ajouté(s) — {sum(1 for a in liste if not a['fait'])} à acheter")


def cmd_afficher():
    liste = charger()
    if not liste:
        print("Liste vide. Ajoute : courses.py add \"pâtes\" \"tomates\"")
        return
    for a in liste:
        print(f"  [{'x' if a['fait'] else ' '}] {a['nom']}")
    restants = sum(1 for a in liste if not a["fait"])
    print(f"\n{restants} article(s) restant(s)")


def cmd_done(nom):
    liste = charger()
    for a in liste:
        if a["nom"].lower() == nom.lower():
            a["fait"] = True
            sauver(liste)
            print(f"✓ {a['nom']} coché")
            return
    print(f"✗ « {nom} » pas dans la liste")
    sys.exit(1)


def cmd_clear():
    liste = [a for a in charger() if not a["fait"]]
    sauver(liste)
    print(f"✓ Articles cochés supprimés — {len(liste)} restant(s)")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        cmd_afficher()
    elif args[0] == "add" and len(args) > 1:
        cmd_add(args[1:])
    elif args[0] == "done" and len(args) == 2:
        cmd_done(args[1])
    elif args[0] == "clear":
        cmd_clear()
    else:
        print(__doc__.strip())
        sys.exit(1)
