#!/usr/bin/env python3
"""Rappels de dates importantes — anniversaires, échéances, rendez-vous.

Usage :
  ./rappels.py add "Anniv Maman" 03-14              # tous les ans le 14 mars
  ./rappels.py add "Rendre le rapport" 2026-09-30   # date unique
  ./rappels.py list                                 # tout, trié par urgence
  ./rappels.py bientot                              # dans les 14 prochains jours
  ./rappels.py rm "Anniv Maman"

Astuce : lance `bientot` au démarrage de ton terminal (~/.bashrc) pour ne rien rater.
"""

import json
import sys
from datetime import date
from pathlib import Path

FICHIER = Path(__file__).parent / "rappels.json"


def charger():
    if not FICHIER.exists():
        return []
    return json.loads(FICHIER.read_text(encoding="utf-8"))


def sauver(rappels):
    FICHIER.write_text(json.dumps(rappels, ensure_ascii=False, indent=2), encoding="utf-8")


def prochaine_occurrence(quand, aujourd_hui=None):
    """quand = 'MM-JJ' (annuel) ou 'AAAA-MM-JJ' (unique). None si passé (unique)."""
    auj = aujourd_hui or date.today()
    if len(quand) == 5:  # MM-JJ, tous les ans
        mois, jour = int(quand[:2]), int(quand[3:])
        try:
            occurrence = date(auj.year, mois, jour)
        except ValueError:  # 29 février hors année bissextile
            occurrence = date(auj.year, 3, 1)
        if occurrence < auj:
            try:
                occurrence = date(auj.year + 1, mois, jour)
            except ValueError:
                occurrence = date(auj.year + 1, 3, 1)
        return occurrence
    unique = date.fromisoformat(quand)
    return unique if unique >= auj else None


def valider(quand):
    try:
        if len(quand) == 5:
            date(2024, int(quand[:2]), int(quand[3:]))  # 2024 bissextile : accepte 02-29
        else:
            date.fromisoformat(quand)
        return True
    except ValueError:
        return False


def cmd_add(nom, quand):
    if not valider(quand):
        print("✗ Format attendu : MM-JJ (annuel) ou AAAA-MM-JJ (unique)")
        sys.exit(1)
    rappels = charger()
    rappels.append({"nom": nom, "quand": quand})
    sauver(rappels)
    genre = "tous les ans" if len(quand) == 5 else "une fois"
    print(f"✓ « {nom} » ({quand}, {genre}) ajouté")


def afficher(rappels, horizon=None):
    auj = date.today()
    lignes = []
    for r in rappels:
        occ = prochaine_occurrence(r["quand"], auj)
        if occ is None:
            continue
        dans = (occ - auj).days
        if horizon is not None and dans > horizon:
            continue
        lignes.append((dans, occ, r["nom"]))
    if not lignes:
        print("Rien à signaler." if horizon else "Aucun rappel à venir.")
        return
    for dans, occ, nom in sorted(lignes):
        quand = "AUJOURD'HUI 🎉" if dans == 0 else ("demain" if dans == 1 else f"dans {dans} jours")
        print(f"  {occ.strftime('%d/%m/%Y')}  {nom:<30} {quand}")


def cmd_rm(nom):
    rappels = charger()
    restants = [r for r in rappels if r["nom"].lower() != nom.lower()]
    if len(restants) == len(rappels):
        print(f"✗ « {nom} » introuvable")
        sys.exit(1)
    sauver(restants)
    print(f"✓ « {nom} » supprimé")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["add"] and len(args) == 3:
        cmd_add(args[1], args[2])
    elif args[:1] == ["list"]:
        afficher(charger())
    elif args[:1] == ["bientot"]:
        afficher(charger(), horizon=14)
    elif args[:1] == ["rm"] and len(args) == 2:
        cmd_rm(args[1])
    else:
        print(__doc__.strip())
        sys.exit(1)
