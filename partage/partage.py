#!/usr/bin/env python3
"""Partage de dépenses entre amis / coloc — façon Tricount, en local.

Usage :
  ./partage.py add "Alice" 30 "Courses"                    # partagé entre tous
  ./partage.py add "Bob" 45 "Essence" --pour Alice Bob     # partagé entre certains
  ./partage.py list                                        # toutes les dépenses
  ./partage.py solde                                       # qui est en + / en −
  ./partage.py regle                                       # qui rembourse qui (minimum de virements)
  ./partage.py reset                                       # nouveau départ (archive l'ancien)
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

FICHIER = Path(__file__).parent / "depenses.json"


def charger():
    if not FICHIER.exists():
        return []
    return json.loads(FICHIER.read_text(encoding="utf-8"))


def sauver(depenses):
    FICHIER.write_text(json.dumps(depenses, ensure_ascii=False, indent=2), encoding="utf-8")


def participants(depenses):
    noms = set()
    for d in depenses:
        noms.add(d["qui"])
        noms.update(d.get("pour") or [])
    return sorted(noms)


def soldes(depenses):
    """Solde net par personne : payé − part due. Positif = on lui doit."""
    tous = participants(depenses)
    net = {n: 0.0 for n in tous}
    for d in depenses:
        beneficiaires = d.get("pour") or tous
        part = d["montant"] / len(beneficiaires)
        net[d["qui"]] += d["montant"]
        for b in beneficiaires:
            net[b] -= part
    return net


def reglements(net):
    """Liste (débiteur, créancier, montant) minimisant les virements (glouton)."""
    debiteurs = sorted([(n, -s) for n, s in net.items() if s < -0.005], key=lambda x: -x[1])
    crediteurs = sorted([(n, s) for n, s in net.items() if s > 0.005], key=lambda x: -x[1])
    virements = []
    i = j = 0
    debiteurs = [list(d) for d in debiteurs]
    crediteurs = [list(c) for c in crediteurs]
    while i < len(debiteurs) and j < len(crediteurs):
        montant = min(debiteurs[i][1], crediteurs[j][1])
        virements.append((debiteurs[i][0], crediteurs[j][0], montant))
        debiteurs[i][1] -= montant
        crediteurs[j][1] -= montant
        if debiteurs[i][1] < 0.005:
            i += 1
        if crediteurs[j][1] < 0.005:
            j += 1
    return virements


def cmd_add(args):
    depenses = charger()
    depenses.append({
        "date": date.today().isoformat(),
        "qui": args.qui,
        "montant": args.montant,
        "description": args.description,
        "pour": args.pour,
    })
    sauver(depenses)
    entre = f" (entre {', '.join(args.pour)})" if args.pour else ""
    print(f"✓ {args.qui} a payé {args.montant:.2f} € — {args.description}{entre}")


def cmd_list(args):
    depenses = charger()
    if not depenses:
        print("Aucune dépense. Ajoute : partage.py add \"Alice\" 30 \"Courses\"")
        return
    total = 0.0
    for d in depenses:
        pour = f" → {', '.join(d['pour'])}" if d.get("pour") else ""
        print(f"{d['date']}  {d['qui']:<10} {d['montant']:>8.2f} €  {d['description']}{pour}")
        total += d["montant"]
    print(f"\nTotal du groupe : {total:.2f} €")


def cmd_solde(args):
    depenses = charger()
    if not depenses:
        print("Aucune dépense.")
        return
    for nom, s in sorted(soldes(depenses).items(), key=lambda x: -x[1]):
        etat = "on lui doit" if s > 0.005 else ("doit au groupe" if s < -0.005 else "à l'équilibre"
)
        print(f"  {nom:<12} {s:>+9.2f} €  ({etat})")


def cmd_regle(args):
    depenses = charger()
    if not depenses:
        print("Aucune dépense.")
        return
    virements = reglements(soldes(depenses))
    if not virements:
        print("Tout le monde est à l'équilibre 🎉")
        return
    print("Pour tout solder :")
    for deb, cred, montant in virements:
        print(f"  {deb} → {cred} : {montant:.2f} €")


def cmd_reset(args):
    if not FICHIER.exists():
        print("Rien à archiver.")
        return
    archive = FICHIER.with_name(f"depenses-{date.today().isoformat()}.json")
    FICHIER.rename(archive)
    print(f"✓ Dépenses archivées dans {archive.name} — nouveau départ !")


def main():
    p = argparse.ArgumentParser(description="Partage de dépenses")
    sub = p.add_subparsers(dest="cmd", required=True)

    pa = sub.add_parser("add")
    pa.add_argument("qui")
    pa.add_argument("montant", type=float)
    pa.add_argument("description")
    pa.add_argument("--pour", nargs="+", help="bénéficiaires (défaut : tout le groupe)")
    pa.set_defaults(func=cmd_add)

    for nom, fonc in [("list", cmd_list), ("solde", cmd_solde),
                      ("regle", cmd_regle), ("reset", cmd_reset)]:
        sp = sub.add_parser(nom)
        sp.set_defaults(func=fonc)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
