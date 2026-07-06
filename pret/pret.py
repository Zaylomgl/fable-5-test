#!/usr/bin/env python3
"""Simulateur de crédit — mensualité et coût total d'un emprunt.

Usage :
  ./pret.py 10000 4.5 60      # 10 000 € à 4,5 % sur 60 mois
"""

import sys


def mensualite(capital, taux_annuel, mois):
    if taux_annuel == 0:
        return capital / mois
    t = taux_annuel / 100 / 12
    return capital * t / (1 - (1 + t) ** -mois)


if __name__ == "__main__":
    try:
        capital, taux, mois = float(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3])
    except (IndexError, ValueError):
        print(__doc__.strip())
        sys.exit(1)
    m = mensualite(capital, taux, mois)
    total = m * mois
    print(f"Emprunt de {capital:,.0f} € à {taux:g} % sur {mois} mois :".replace(",", " "))
    print(f"  Mensualité      : {m:>10.2f} €")
    print(f"  Total remboursé : {total:>10.2f} €")
    print(f"  Coût du crédit  : {total - capital:>10.2f} €  "
          f"({(total - capital) / capital * 100:.1f} % du capital)")
