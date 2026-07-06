#!/usr/bin/env python3
"""Calculateur de tarif freelance — du revenu que tu vises au tarif à facturer.

Usage :
  ./tjm.py 2000                          # je veux 2000 € net/mois
  ./tjm.py 2000 --jours 12               # en facturant 12 jours/mois
  ./tjm.py 2000 --charges 26.1           # taux de cotisations personnalisé

Par défaut : 15 jours facturés/mois (le reste part en prospection, admin,
congés) et 22 % de cotisations (micro-entreprise, prestations de services —
vérifie le taux en vigueur sur urssaf.fr, il évolue chaque année).
"""

import argparse

SEUIL_MICRO_BNC = 77_700  # plafond CA micro-entreprise prestations (2026)


def calculer(net_mensuel, jours_par_mois=15, taux_charges=22.0):
    """Renvoie un dict : CA mensuel/annuel, TJM, taux horaire."""
    ca_mensuel = net_mensuel / (1 - taux_charges / 100)
    tjm = ca_mensuel / jours_par_mois
    return {
        "ca_mensuel": ca_mensuel,
        "ca_annuel": ca_mensuel * 12,
        "tjm": tjm,
        "horaire": tjm / 7,
        "depasse_micro": ca_mensuel * 12 > SEUIL_MICRO_BNC,
    }


def main():
    p = argparse.ArgumentParser(description="Calculateur de tarif freelance")
    p.add_argument("net", type=float, help="revenu net mensuel visé (€)")
    p.add_argument("--jours", type=float, default=15,
                   help="jours facturés par mois (défaut : 15)")
    p.add_argument("--charges", type=float, default=22.0,
                   help="taux de cotisations en %% (défaut : 22)")
    args = p.parse_args()

    r = calculer(args.net, args.jours, args.charges)
    print(f"Pour {args.net:.0f} € net/mois, {args.jours:g} jours facturés, "
          f"{args.charges:g} % de cotisations :")
    print(f"  CA à réaliser  : {r['ca_mensuel']:>9.0f} €/mois  ({r['ca_annuel']:.0f} €/an)")
    print(f"  TJM à facturer : {r['tjm']:>9.0f} €/jour")
    print(f"  Taux horaire   : {r['horaire']:>9.0f} €/h (base 7 h/jour)")
    if r["depasse_micro"]:
        print(f"\n⚠ CA annuel > {SEUIL_MICRO_BNC:,} € : au-delà du plafond micro-entreprise,"
              .replace(",", " "))
        print("  il faudra passer en société (EURL, SASU…) — anticipe avec un comptable.")
    print("\nRappel : le net affiché est avant impôt sur le revenu.")


if __name__ == "__main__":
    main()
