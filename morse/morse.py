#!/usr/bin/env python3
"""Texte ↔ morse.

Usage :
  ./morse.py code "sos on arrive"      # texte → morse
  ./morse.py lis "... --- ..."         # morse → texte  (/ entre les mots)
"""

import sys
import unicodedata

TABLE = {
    "a": ".-", "b": "-...", "c": "-.-.", "d": "-..", "e": ".", "f": "..-.",
    "g": "--.", "h": "....", "i": "..", "j": ".---", "k": "-.-", "l": ".-..",
    "m": "--", "n": "-.", "o": "---", "p": ".--.", "q": "--.-", "r": ".-.",
    "s": "...", "t": "-", "u": "..-", "v": "...-", "w": ".--", "x": "-..-",
    "y": "-.--", "z": "--..",
    "0": "-----", "1": ".----", "2": "..---", "3": "...--", "4": "....-",
    "5": ".....", "6": "-....", "7": "--...", "8": "---..", "9": "----.",
    ".": ".-.-.-", ",": "--..--", "?": "..--..", "!": "-.-.--", "'": ".----.",
}
INVERSE = {v: k for k, v in TABLE.items()}


def coder(texte):
    sans_accents = unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode()
    mots = sans_accents.lower().split()
    return " / ".join(
        " ".join(TABLE[c] for c in mot if c in TABLE) for mot in mots
    )


def decoder(morse):
    mots = morse.strip().split(" / ")
    return " ".join(
        "".join(INVERSE.get(symbole, "?") for symbole in mot.split()) for mot in mots
    )


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["code"] and len(args) > 1:
        print(coder(" ".join(args[1:])))
    elif args[:1] == ["lis"] and len(args) > 1:
        print(decoder(" ".join(args[1:])))
    else:
        print(__doc__.strip())
        sys.exit(1)
