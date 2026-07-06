#!/usr/bin/env python3
"""Météo dans le terminal — via wttr.in, sans clé API.

Usage :
  ./meteo.py Paris              # météo courte
  ./meteo.py Paris --complet    # prévisions 3 jours (ASCII art)
  ./meteo.py "Lyon" --demain

Nécessite une connexion internet.
"""

import argparse
import urllib.parse
import urllib.request


def meteo(ville, format_court=True):
    v = urllib.parse.quote(ville)
    url = (f"https://wttr.in/{v}?format=%l+:+%c+%t+(ressenti+%f)+%h+vent+%w&lang=fr"
           if format_court else f"https://wttr.in/{v}?lang=fr&T")
    req = urllib.request.Request(url, headers={"User-Agent": "curl/8.0"})
    return urllib.request.urlopen(req, timeout=15).read().decode("utf-8")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Météo en CLI")
    p.add_argument("ville")
    p.add_argument("--complet", action="store_true", help="prévisions 3 jours")
    args = p.parse_args()
    try:
        print(meteo(args.ville, format_court=not args.complet))
    except Exception as e:
        print(f"✗ Impossible de joindre wttr.in ({e}) — vérifie ta connexion.")
        raise SystemExit(1)
