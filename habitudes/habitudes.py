#!/usr/bin/env python3
"""Suivi d'habitudes — coche chaque jour, garde ta série (streak).

Usage :
  ./habitudes.py add "Sport"          # nouvelle habitude
  ./habitudes.py fait "Sport"         # coché pour aujourd'hui
  ./habitudes.py statut               # séries en cours
  ./habitudes.py rm "Sport"
"""

import json
import sys
from datetime import date, timedelta
from pathlib import Path

FICHIER = Path(__file__).parent / "habitudes.json"


def charger():
    if not FICHIER.exists():
        return {}
    return json.loads(FICHIER.read_text(encoding="utf-8"))


def sauver(h):
    FICHIER.write_text(json.dumps(h, ensure_ascii=False, indent=2), encoding="utf-8")


def serie(jours_faits, aujourd_hui=None):
    """Longueur de la série se terminant aujourd'hui ou hier."""
    auj = aujourd_hui or date.today()
    faits = {date.fromisoformat(j) for j in jours_faits}
    depart = auj if auj in faits else auj - timedelta(days=1)
    n = 0
    while depart in faits:
        n += 1
        depart -= timedelta(days=1)
    return n


def cmd_fait(nom):
    h = charger()
    if nom not in h:
        print(f"✗ « {nom} » inconnue — crée-la : habitudes.py add \"{nom}\"")
        sys.exit(1)
    auj = date.today().isoformat()
    if auj not in h[nom]:
        h[nom].append(auj)
        sauver(h)
    s = serie(h[nom])
    print(f"✓ {nom} — série de {s} jour(s) {'🔥' if s >= 7 else ''}")


def cmd_statut():
    h = charger()
    if not h:
        print("Aucune habitude. Crée : habitudes.py add \"Sport\"")
        return
    auj = date.today().isoformat()
    for nom, jours in sorted(h.items()):
        s = serie(jours)
        coche = "✓" if auj in jours else "·"
        feu = " 🔥" if s >= 7 else ""
        print(f"  [{coche}] {nom:<20} série : {s} jour(s){feu}  (total {len(jours)})")


if __name__ == "__main__":
    args = sys.argv[1:]
    h = charger()
    if args[:1] == ["add"] and len(args) == 2:
        h.setdefault(args[1], [])
        sauver(h)
        print(f"✓ Habitude « {args[1]} » créée")
    elif args[:1] == ["fait"] and len(args) == 2:
        cmd_fait(args[1])
    elif args[:1] == ["statut"]:
        cmd_statut()
    elif args[:1] == ["rm"] and len(args) == 2:
        if h.pop(args[1], None) is None:
            print(f"✗ « {args[1]} » introuvable")
            sys.exit(1)
        sauver(h)
        print(f"✓ « {args[1]} » supprimée")
    else:
        print(__doc__.strip())
        sys.exit(1)
