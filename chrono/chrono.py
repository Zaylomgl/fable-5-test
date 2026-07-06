#!/usr/bin/env python3
"""Chronomètre avec tours — Entrée pour un tour, Ctrl+C (ou q) pour finir.

Usage :
  ./chrono.py
"""

import sys
import time


def format_duree(secondes):
    m, s = divmod(secondes, 60)
    h, m = divmod(int(m), 60)
    return f"{h:d}:{m:02d}:{s:05.2f}" if h else f"{m:02d}:{s:05.2f}"


if __name__ == "__main__":
    debut = time.monotonic()
    dernier = debut
    tours = []
    print("⏱ Chrono lancé — Entrée = tour, q puis Entrée (ou Ctrl+C) = stop")
    try:
        while True:
            saisie = input()
            maintenant = time.monotonic()
            if saisie.strip().lower() == "q":
                break
            tours.append(maintenant - dernier)
            print(f"  Tour {len(tours):>2} : {format_duree(tours[-1])}   "
                  f"(total {format_duree(maintenant - debut)})")
            dernier = maintenant
    except (KeyboardInterrupt, EOFError):
        pass
    total = time.monotonic() - debut
    print(f"\n⏹ Total : {format_duree(total)}")
    if tours:
        print(f"  Meilleur tour : {format_duree(min(tours))}")
        print(f"  Tour moyen    : {format_duree(sum(tours) / len(tours))}")
    sys.exit(0)
