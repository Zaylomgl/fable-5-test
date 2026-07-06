#!/usr/bin/env python3
"""Pointeuse freelance — mesure ton temps par projet, pour facturer juste.

Usage :
  ./tempo.py start "Site vitrine Dupont"   # début de session
  ./tempo.py stop                          # fin de session
  ./tempo.py statut                        # session en cours ?
  ./tempo.py bilan                         # total d'heures par projet
  ./tempo.py bilan --tjm 350               # + montant à facturer (base 7 h/j)
"""

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path

DOSSIER = Path(__file__).parent
EN_COURS = DOSSIER / "en_cours.json"
SESSIONS = DOSSIER / "sessions.csv"


def cmd_start(args):
    if EN_COURS.exists():
        actif = json.loads(EN_COURS.read_text(encoding="utf-8"))
        print(f"✗ Session déjà en cours sur « {actif['projet']} » — fais d'abord : tempo.py stop")
        return 1
    EN_COURS.write_text(
        json.dumps({"projet": args.projet, "debut": datetime.now().isoformat()}),
        encoding="utf-8",
    )
    print(f"▶ Session démarrée sur « {args.projet} »")
    return 0


def cmd_stop(args):
    if not EN_COURS.exists():
        print("✗ Aucune session en cours.")
        return 1
    actif = json.loads(EN_COURS.read_text(encoding="utf-8"))
    debut = datetime.fromisoformat(actif["debut"])
    fin = datetime.now()
    heures = (fin - debut).total_seconds() / 3600
    nouveau = not SESSIONS.exists()
    with SESSIONS.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date", "projet", "heures"])
        if nouveau:
            w.writeheader()
        w.writerow({"date": debut.date().isoformat(), "projet": actif["projet"],
                    "heures": f"{heures:.2f}"})
    EN_COURS.unlink()
    print(f"⏹ {heures:.2f} h enregistrées sur « {actif['projet']} »")
    return 0


def cmd_statut(args):
    if not EN_COURS.exists():
        print("Aucune session en cours.")
        return 0
    actif = json.loads(EN_COURS.read_text(encoding="utf-8"))
    debut = datetime.fromisoformat(actif["debut"])
    heures = (datetime.now() - debut).total_seconds() / 3600
    print(f"▶ « {actif['projet']} » depuis {debut.strftime('%H:%M')} ({heures:.2f} h)")
    return 0


def totaux_par_projet():
    if not SESSIONS.exists():
        return {}
    totaux = {}
    with SESSIONS.open(newline="", encoding="utf-8") as f:
        for ligne in csv.DictReader(f):
            totaux[ligne["projet"]] = totaux.get(ligne["projet"], 0.0) + float(ligne["heures"])
    return totaux


def cmd_bilan(args):
    totaux = totaux_par_projet()
    if not totaux:
        print("Aucune session enregistrée. Lance : tempo.py start \"Mon projet\"")
        return 0
    for projet, heures in sorted(totaux.items(), key=lambda x: -x[1]):
        ligne = f"  {projet:<30} {heures:>7.2f} h  ({heures / 7:.1f} j)"
        if args.tjm:
            ligne += f"  → {heures / 7 * args.tjm:>9.2f} €"
        print(ligne)
    total = sum(totaux.values())
    print(f"\nTotal : {total:.2f} h ({total / 7:.1f} jours)")
    if args.tjm:
        print(f"À facturer (TJM {args.tjm:g} €) : {total / 7 * args.tjm:.2f} €")
    return 0


def main():
    p = argparse.ArgumentParser(description="Pointeuse freelance")
    sub = p.add_subparsers(dest="cmd", required=True)

    ps = sub.add_parser("start")
    ps.add_argument("projet")
    ps.set_defaults(func=cmd_start)

    for nom, fonc in [("stop", cmd_stop), ("statut", cmd_statut)]:
        sp = sub.add_parser(nom)
        sp.set_defaults(func=fonc)

    pb = sub.add_parser("bilan")
    pb.add_argument("--tjm", type=float, help="tarif journalier pour chiffrer")
    pb.set_defaults(func=cmd_bilan)

    args = p.parse_args()
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
