#!/usr/bin/env python3
"""Objectif d'épargne — combien mettre de côté chaque mois, tout simplement.

Usage :
  ./epargne.py 3000 2027-06-01                 # 3000 € pour juin 2027
  ./epargne.py 3000 2027-06-01 --deja 500      # j'ai déjà 500 € de côté
  ./epargne.py 3000 2027-06-01 --taux 3        # sur un livret à 3 % (Livret A…)
"""

import argparse
from datetime import date


def mois_restants(objectif_date, aujourd_hui=None):
    auj = aujourd_hui or date.today()
    return max((objectif_date.year - auj.year) * 12 + objectif_date.month - auj.month, 1)


def mensualite(objectif, mois, deja=0.0, taux_annuel=0.0):
    """Versement mensuel pour atteindre `objectif` en `mois` mois.
    Intérêts composés mensuellement au taux annuel donné (0 = sans intérêts)."""
    restant = objectif - deja
    if restant <= 0:
        return 0.0
    if taux_annuel == 0:
        return restant / mois
    t = taux_annuel / 100 / 12
    # le capital déjà placé fructifie aussi
    futur_deja = deja * (1 + t) ** mois
    restant = objectif - futur_deja
    if restant <= 0:
        return 0.0
    # valeur future d'une annuité : v * ((1+t)^n - 1) / t
    return restant * t / ((1 + t) ** mois - 1)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Objectif d'épargne")
    p.add_argument("objectif", type=float, help="montant visé en €")
    p.add_argument("date", help="date cible AAAA-MM-JJ")
    p.add_argument("--deja", type=float, default=0.0, help="déjà épargné (€)")
    p.add_argument("--taux", type=float, default=0.0, help="taux annuel du placement en %%")
    args = p.parse_args()

    cible = date.fromisoformat(args.date)
    mois = mois_restants(cible)
    v = mensualite(args.objectif, mois, args.deja, args.taux)
    print(f"Objectif : {args.objectif:.0f} € pour le {cible.strftime('%d/%m/%Y')} "
          f"({mois} mois)")
    if args.deja:
        print(f"Déjà de côté : {args.deja:.0f} €")
    if v == 0:
        print("🎉 Objectif déjà atteint (ou atteint par les intérêts seuls) !")
    else:
        print(f"→ Mets de côté {v:.2f} €/mois"
              + (f" (placé à {args.taux:g} %/an)" if args.taux else ""))
        print(f"  soit environ {v / 4.33:.2f} € par semaine")
