#!/usr/bin/env python3
"""Suivi d'abonnements — sais ce que tes abonnements te coûtent vraiment.

Usage :
  ./abos.py add "Netflix" 13.49 mensuel --jour 15    # prélevé le 15 de chaque mois
  ./abos.py add "Assurance" 120 annuel --date 2026-09-01
  ./abos.py list                                     # tout + coût mensuel/annuel total
  ./abos.py prochains                                # prélèvements dans les 30 jours
  ./abos.py rm "Netflix"                             # résilié ? on le retire
"""

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path

FICHIER = Path(__file__).parent / "abonnements.json"


def charger():
    if not FICHIER.exists():
        return []
    return json.loads(FICHIER.read_text(encoding="utf-8"))


def sauver(abos):
    FICHIER.write_text(json.dumps(abos, ensure_ascii=False, indent=2), encoding="utf-8")


def cout_mensuel(abo):
    return abo["prix"] if abo["periode"] == "mensuel" else abo["prix"] / 12


def prochaine_echeance(abo, aujourd_hui=None):
    auj = aujourd_hui or date.today()
    if abo["periode"] == "mensuel":
        jour = min(abo.get("jour", 1), 28)
        echeance = auj.replace(day=jour)
        if echeance < auj:
            mois, annee = (echeance.month % 12) + 1, echeance.year + (echeance.month == 12)
            echeance = echeance.replace(year=annee, month=mois)
        return echeance
    echeance = date.fromisoformat(abo["date"])
    while echeance < auj:
        echeance = echeance.replace(year=echeance.year + 1)
    return echeance


def cmd_add(args):
    abos = charger()
    abo = {"nom": args.nom, "prix": args.prix, "periode": args.periode}
    if args.periode == "mensuel":
        abo["jour"] = args.jour or 1
    else:
        abo["date"] = args.date or date.today().isoformat()
    abos.append(abo)
    sauver(abos)
    print(f"✓ {args.nom} ajouté ({args.prix:.2f} €/{'mois' if args.periode == 'mensuel' else 'an'})")


def cmd_list(args):
    abos = charger()
    if not abos:
        print("Aucun abonnement suivi. Ajoute : abos.py add \"Netflix\" 13.49 mensuel --jour 15")
        return
    total_mensuel = sum(cout_mensuel(a) for a in abos)
    for a in sorted(abos, key=cout_mensuel, reverse=True):
        unite = "mois" if a["periode"] == "mensuel" else "an"
        print(f"  {a['nom']:<20} {a['prix']:>8.2f} €/{unite:<4}  "
              f"(≈ {cout_mensuel(a):.2f} €/mois)")
    print(f"\nTotal : {total_mensuel:.2f} €/mois — soit {total_mensuel * 12:.2f} €/an")


def cmd_prochains(args):
    abos = charger()
    if not abos:
        print("Aucun abonnement suivi.")
        return
    auj = date.today()
    horizon = auj + timedelta(days=30)
    a_venir = [(prochaine_echeance(a), a) for a in abos]
    a_venir = [(e, a) for e, a in a_venir if e <= horizon]
    if not a_venir:
        print("Aucun prélèvement dans les 30 prochains jours.")
        return
    print("Prélèvements à venir (30 jours) :")
    for echeance, a in sorted(a_venir):
        dans = (echeance - auj).days
        quand = "aujourd'hui" if dans == 0 else f"dans {dans} j"
        print(f"  {echeance.strftime('%d/%m')}  {a['nom']:<20} {a['prix']:>8.2f} €  ({quand})")
    print(f"\nTotal sur la période : {sum(a['prix'] for _, a in a_venir):.2f} €")


def cmd_rm(args):
    abos = charger()
    restants = [a for a in abos if a["nom"].lower() != args.nom.lower()]
    if len(restants) == len(abos):
        print(f"✗ « {args.nom} » introuvable")
        sys.exit(1)
    sauver(restants)
    print(f"✓ {args.nom} retiré — pense à vérifier que la résiliation est bien effective !")


def main():
    p = argparse.ArgumentParser(description="Suivi d'abonnements")
    sub = p.add_subparsers(dest="cmd", required=True)

    pa = sub.add_parser("add", help="ajouter un abonnement")
    pa.add_argument("nom")
    pa.add_argument("prix", type=float)
    pa.add_argument("periode", choices=["mensuel", "annuel"])
    pa.add_argument("--jour", type=int, help="jour de prélèvement (mensuel)")
    pa.add_argument("--date", help="prochaine échéance AAAA-MM-JJ (annuel)")
    pa.set_defaults(func=cmd_add)

    pl = sub.add_parser("list", help="tous les abonnements + coût total")
    pl.set_defaults(func=cmd_list)

    pp = sub.add_parser("prochains", help="prélèvements dans les 30 jours")
    pp.set_defaults(func=cmd_prochains)

    pr = sub.add_parser("rm", help="retirer un abonnement")
    pr.add_argument("nom")
    pr.set_defaults(func=cmd_rm)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
