#!/usr/bin/env python3
"""Veille de prix — surveille des pages produit et signale les baisses.

Utile pour acheter au bon moment, ou repérer des affaires à revendre.

Usage :
  ./veille.py add "PS5 occasion" "https://exemple.fr/produit"   # suivre un produit
  ./veille.py check                                             # relever les prix
  ./veille.py histo                                             # historique + tendance

Le prix est détecté automatiquement dans la page (motifs type "299,99 €").
Lance `check` régulièrement (à la main ou en cron) pour bâtir l'historique.
"""

import csv
import json
import re
import sys
import urllib.request
from datetime import date
from pathlib import Path

DOSSIER = Path(__file__).parent
PRODUITS = DOSSIER / "produits.json"
HISTORIQUE = DOSSIER / "historique.csv"

_NOMBRE = r"\d{1,3}(?:[ \u00a0\u202f.]\d{3})+(?:,\d{2})?|\d{1,4}(?:[.,]\d{2})?"
MOTIF_PRIX = re.compile(rf"({_NOMBRE})\s*\u20ac|\u20ac\s*({_NOMBRE})")
_ESPACES = re.compile(r"[ \u00a0\u202f]")
_MILLIERS_POINT = re.compile(r"^\d{1,3}(?:\.\d{3})+(?:,\d{2})?$")


def _en_float(brut):
    """\u00ab 1\u202f299,00 \u00bb \u2192 1299.0 ; \u00ab 1.299 \u00bb \u2192 1299.0 ; \u00ab 19.99 \u00bb \u2192 19.99"""
    brut = _ESPACES.sub("", brut)
    if _MILLIERS_POINT.match(brut):
        brut = brut.replace(".", "")
    return float(brut.replace(",", "."))


def charger_produits():
    if not PRODUITS.exists():
        return []
    return json.loads(PRODUITS.read_text(encoding="utf-8"))


def cmd_add(nom, url):
    produits = charger_produits()
    produits.append({"nom": nom, "url": url})
    PRODUITS.write_text(json.dumps(produits, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✓ « {nom} » suivi ({len(produits)} produit(s) au total)")


def extraire_prix(html):
    """Renvoie le prix le plus fréquent trouvé dans la page (le prix affiché
    apparaît en général plusieurs fois : titre, bouton, méta…)."""
    prix = []
    for m in MOTIF_PRIX.finditer(html):
        try:
            prix.append(_en_float(m.group(1) or m.group(2)))
        except ValueError:
            continue
    if not prix:
        return None
    return max(set(prix), key=prix.count)


def dernier_prix(nom):
    if not HISTORIQUE.exists():
        return None
    dernier = None
    with HISTORIQUE.open(newline="", encoding="utf-8") as f:
        for ligne in csv.DictReader(f):
            if ligne["nom"] == nom:
                dernier = float(ligne["prix"])
    return dernier


def cmd_check():
    produits = charger_produits()
    if not produits:
        print("Aucun produit suivi. Ajoute-en un avec : veille.py add \"nom\" \"url\"")
        return
    nouveau = not HISTORIQUE.exists()
    with HISTORIQUE.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date", "nom", "prix"])
        if nouveau:
            w.writeheader()
        for p in produits:
            req = urllib.request.Request(p["url"], headers={"User-Agent": "Mozilla/5.0"})
            try:
                html = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", "ignore")
            except Exception as e:
                print(f"✗ {p['nom']} : erreur réseau ({e})")
                continue
            prix = extraire_prix(html)
            if prix is None:
                print(f"? {p['nom']} : aucun prix détecté sur la page")
                continue
            precedent = dernier_prix(p["nom"])
            w.writerow({"date": date.today().isoformat(), "nom": p["nom"], "prix": f"{prix:.2f}"})
            if precedent is None:
                print(f"• {p['nom']} : {prix:.2f} € (premier relevé)")
            elif prix < precedent:
                print(f"↓ {p['nom']} : {prix:.2f} € (−{precedent - prix:.2f} € — BAISSE !)")
            elif prix > precedent:
                print(f"↑ {p['nom']} : {prix:.2f} € (+{prix - precedent:.2f} €)")
            else:
                print(f"= {p['nom']} : {prix:.2f} € (stable)")


def cmd_histo():
    if not HISTORIQUE.exists():
        print("Pas encore d'historique. Lance : veille.py check")
        return
    with HISTORIQUE.open(newline="", encoding="utf-8") as f:
        lignes = list(csv.DictReader(f))
    par_produit = {}
    for l in lignes:
        par_produit.setdefault(l["nom"], []).append(l)
    for nom, releves in par_produit.items():
        premier, dernier = float(releves[0]["prix"]), float(releves[-1]["prix"])
        mini = min(float(r["prix"]) for r in releves)
        print(f"{nom} — {len(releves)} relevé(s), min {mini:.2f} €, "
              f"{premier:.2f} € → {dernier:.2f} €")
        for r in releves[-5:]:
            print(f"    {r['date']}  {float(r['prix']):>8.2f} €")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["add"] and len(args) == 3:
        cmd_add(args[1], args[2])
    elif args[:1] == ["check"]:
        cmd_check()
    elif args[:1] == ["histo"]:
        cmd_histo()
    else:
        print(__doc__.strip())
        sys.exit(1)
