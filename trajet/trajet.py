#!/usr/bin/env python3
"""Coût réel d'un trajet en voiture — et part de chaque passager.

Usage :
  ./trajet.py 450                              # 450 km, valeurs par défaut
  ./trajet.py 450 --conso 6.5 --prix 1.85      # conso L/100km, prix du litre
  ./trajet.py 450 --peage 35 --passagers 3     # partagé entre 3 personnes

Le conducteur compte comme un passager : --passagers 3 = le coût divisé par 3.
"""

import argparse


def calculer(km, conso=6.5, prix_litre=1.80, peage=0.0, passagers=1, usure=0.10):
    """usure : €/km d'entretien+pneus+décote (0 pour ne compter que l'essence)."""
    carburant = km * conso / 100 * prix_litre
    entretien = km * usure
    total = carburant + peage + entretien
    return {
        "carburant": carburant,
        "peage": peage,
        "entretien": entretien,
        "total": total,
        "par_personne": total / max(passagers, 1),
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Coût d'un trajet en voiture")
    p.add_argument("km", type=float, help="distance en km")
    p.add_argument("--conso", type=float, default=6.5, help="L/100 km (défaut 6.5)")
    p.add_argument("--prix", type=float, default=1.80, help="€/litre (défaut 1.80)")
    p.add_argument("--peage", type=float, default=0.0, help="péages en €")
    p.add_argument("--passagers", type=int, default=1,
                   help="personnes qui partagent (conducteur inclus)")
    p.add_argument("--usure", type=float, default=0.10,
                   help="€/km d'usure du véhicule (défaut 0.10 ; 0 = essence seule)")
    args = p.parse_args()

    r = calculer(args.km, args.conso, args.prix, args.peage, args.passagers, args.usure)
    print(f"Trajet de {args.km:g} km :")
    print(f"  Carburant : {r['carburant']:>7.2f} €")
    if r["peage"]:
        print(f"  Péages    : {r['peage']:>7.2f} €")
    if r["entretien"]:
        print(f"  Usure     : {r['entretien']:>7.2f} €  (entretien, pneus, décote)")
    print(f"  Total     : {r['total']:>7.2f} €")
    if args.passagers > 1:
        print(f"\nÀ {args.passagers} : {r['par_personne']:.2f} € par personne")
