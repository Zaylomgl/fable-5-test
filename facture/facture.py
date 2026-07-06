#!/usr/bin/env python3
"""Générateur de factures et de devis — HTML propre, imprimable en PDF (Ctrl+P).

Usage :
  1. Copie exemple.json et remplis tes infos + les lignes de prestation
  2. ./facture.py ma_facture.json            # facture
     ./facture.py ma_facture.json --devis    # devis (à envoyer avant la mission)
  3. Ouvre le HTML généré dans un navigateur → Imprimer → Enregistrer en PDF
"""

import html as html_mod
import json
import sys
from datetime import date
from pathlib import Path

GABARIT = """<!doctype html>
<html lang="fr">
<meta charset="utf-8">
<title>{titre} {numero}</title>
<style>
  body {{ font-family: -apple-system, "Segoe UI", Roboto, sans-serif; color: #1a1a1a;
         max-width: 760px; margin: 3rem auto; padding: 0 1.5rem; line-height: 1.5; }}
  header {{ display: flex; justify-content: space-between; align-items: flex-start; }}
  h1 {{ font-size: 1.6rem; margin: 0; }}
  .num {{ color: #666; }}
  .blocs {{ display: flex; justify-content: space-between; margin: 2.5rem 0; gap: 2rem; }}
  .bloc h2 {{ font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em;
              color: #888; margin: 0 0 0.4rem; }}
  table {{ width: 100%; border-collapse: collapse; margin: 1rem 0 2rem; }}
  th {{ text-align: left; font-size: 0.75rem; text-transform: uppercase;
        letter-spacing: 0.08em; color: #888; padding: 0.5rem 0.6rem;
        border-bottom: 2px solid #1a1a1a; }}
  td {{ padding: 0.6rem; border-bottom: 1px solid #e5e5e5; }}
  .r {{ text-align: right; }}
  .total td {{ border-bottom: none; font-weight: 700; font-size: 1.1rem; padding-top: 1rem; }}
  footer {{ margin-top: 3rem; font-size: 0.85rem; color: #666;
            border-top: 1px solid #e5e5e5; padding-top: 1rem; }}
  @media print {{ body {{ margin: 0 auto; }} }}
</style>
<body>
<header>
  <h1>{titre}</h1>
  <div class="num">N° {numero}<br>Date : {date}<br>{libelle_echeance} : {echeance}</div>
</header>
<div class="blocs">
  <div class="bloc"><h2>Émetteur</h2>{emetteur}</div>
  <div class="bloc"><h2>Client</h2>{client}</div>
</div>
<table>
  <tr><th>Prestation</th><th class="r">Qté</th><th class="r">Prix unitaire</th><th class="r">Total</th></tr>
  {lignes}
  <tr class="total"><td colspan="3" class="r">{libelle_total}</td><td class="r">{total} €</td></tr>
</table>
<footer>
  {paiement}<br>
  {mentions}
</footer>
</body>
</html>
"""


def esc(texte):
    return html_mod.escape(str(texte))


def bloc_adresse(d):
    champs = [d.get("nom", ""), d.get("adresse", ""), d.get("email", ""), d.get("siret", "")]
    return "<br>".join(esc(c) for c in champs if c)


def generer(chemin_json, devis=False):
    data = json.loads(Path(chemin_json).read_text(encoding="utf-8"))
    lignes_html, total = [], 0.0
    for l in data["lignes"]:
        montant = l["quantite"] * l["prix_unitaire"]
        total += montant
        lignes_html.append(
            f'<tr><td>{esc(l["description"])}</td><td class="r">{l["quantite"]:g}</td>'
            f'<td class="r">{l["prix_unitaire"]:.2f} €</td><td class="r">{montant:.2f} €</td></tr>'
        )
    html = GABARIT.format(
        titre="DEVIS" if devis else "FACTURE",
        libelle_echeance="Validité" if devis else "Échéance",
        libelle_total="Total du devis" if devis else "Total à payer",
        numero=esc(data.get("numero", date.today().strftime("%Y%m%d-01"))),
        date=esc(data.get("date", date.today().strftime("%d/%m/%Y"))),
        echeance=esc(data.get("echeance", "30 jours")),
        emetteur=bloc_adresse(data["emetteur"]),
        client=bloc_adresse(data["client"]),
        lignes="\n  ".join(lignes_html),
        total=f"{total:.2f}",
        paiement=esc(data.get("paiement", "")),
        mentions=esc(data.get("mentions", "TVA non applicable, art. 293 B du CGI.")),
    )
    suffixe = ".devis.html" if devis else ".html"
    sortie = Path(chemin_json).with_suffix(suffixe)
    sortie.write_text(html, encoding="utf-8")
    doc = "Devis généré" if devis else "Facture générée"
    print(f"✓ {doc} : {sortie}  (total {total:.2f} €)")
    print("  Ouvre dans un navigateur puis Ctrl+P → Enregistrer en PDF")
    return sortie, total


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--devis"]
    if len(args) != 1:
        print("Usage : facture.py <fichier.json> [--devis]   (voir exemple.json)")
        sys.exit(1)
    generer(args[0], devis="--devis" in sys.argv)
