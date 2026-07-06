#!/usr/bin/env python3
"""Conversions de couleurs hex ↔ RGB, avec aperçu dans le terminal.

Usage :
  ./couleur.py "#ff6600"        # hex → RGB + aperçu
  ./couleur.py 255 102 0        # RGB → hex + aperçu
  ./couleur.py hasard           # une couleur aléatoire
"""

import random
import sys


def hex_vers_rgb(code):
    code = code.lstrip("#")
    if len(code) == 3:
        code = "".join(c * 2 for c in code)
    if len(code) != 6:
        raise ValueError(f"code hex invalide : {code}")
    return tuple(int(code[i:i + 2], 16) for i in (0, 2, 4))


def rgb_vers_hex(r, g, b):
    for v in (r, g, b):
        if not 0 <= v <= 255:
            raise ValueError(f"composante hors 0-255 : {v}")
    return f"#{r:02x}{g:02x}{b:02x}"


def afficher(r, g, b):
    pave = f"\033[48;2;{r};{g};{b}m          \033[0m"
    print(f"  {pave}  {rgb_vers_hex(r, g, b)}  rgb({r}, {g}, {b})")


if __name__ == "__main__":
    args = sys.argv[1:]
    try:
        if args == ["hasard"]:
            afficher(*(random.randint(0, 255) for _ in range(3)))
        elif len(args) == 1:
            afficher(*hex_vers_rgb(args[0]))
        elif len(args) == 3:
            afficher(int(args[0]), int(args[1]), int(args[2]))
        else:
            print(__doc__.strip())
            sys.exit(1)
    except ValueError as e:
        print(f"✗ {e}")
        sys.exit(1)
