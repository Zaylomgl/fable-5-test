#!/usr/bin/env python3
"""Minuteur Pomodoro dans le terminal — 25 min de focus, 5 min de pause.

Usage :
  ./pomodoro.py              # 25 min travail / 5 min pause, 4 cycles
  ./pomodoro.py 50 10        # sessions de 50 min, pauses de 10
  ./pomodoro.py 25 5 -c 2    # 2 cycles seulement

Ctrl+C pour arrêter. Bip à chaque transition (cloche du terminal).
"""

import argparse
import time


def compte_a_rebours(minutes, libelle):
    total = int(minutes * 60)
    for restant in range(total, 0, -1):
        m, s = divmod(restant, 60)
        print(f"\r{libelle}  {m:02d}:{s:02d} ", end="", flush=True)
        time.sleep(1)
    print(f"\r{libelle}  00:00 — terminé ! \a")


def main():
    p = argparse.ArgumentParser(description="Minuteur Pomodoro")
    p.add_argument("travail", nargs="?", type=float, default=25, help="minutes de focus")
    p.add_argument("pause", nargs="?", type=float, default=5, help="minutes de pause")
    p.add_argument("-c", "--cycles", type=int, default=4)
    args = p.parse_args()

    try:
        for cycle in range(1, args.cycles + 1):
            print(f"\n🍅 Cycle {cycle}/{args.cycles}")
            compte_a_rebours(args.travail, "  Focus ")
            if cycle < args.cycles:
                compte_a_rebours(args.pause, "  Pause ")
        print("\n✔ Série terminée, bien joué !")
    except KeyboardInterrupt:
        print("\n⏹ Arrêté.")


if __name__ == "__main__":
    main()
