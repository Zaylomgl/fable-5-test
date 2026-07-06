#!/usr/bin/env python3
"""Générateur de mails de relance pour facture impayée — 3 niveaux de fermeté.

Réutilise le JSON de tes factures (voir facture/exemple.json).

Usage :
  ./relance.py ../facture/ma_facture.json            # niveau 1 : rappel courtois
  ./relance.py ../facture/ma_facture.json --niveau 2 # relance ferme
  ./relance.py ../facture/ma_facture.json --niveau 3 # dernier avis avant recouvrement

Copie-colle le texte dans ton mail. Envoie le niveau 1 à J+7 après l'échéance,
le niveau 2 à J+21, le niveau 3 à J+35.
"""

import argparse
import json
from pathlib import Path

MODELES = {
    1: """Objet : Rappel — facture n° {numero}

Bonjour {client},

Sauf erreur de ma part, la facture n° {numero} du {date}, d'un montant de
{total:.2f} €, reste à ce jour impayée alors que son échéance est dépassée.

Il s'agit certainement d'un oubli : vous trouverez mes coordonnées de
paiement sur la facture. Si le règlement a été effectué entre-temps,
merci de ne pas tenir compte de ce message.

Bien cordialement,
{emetteur}""",
    2: """Objet : Relance — facture n° {numero} impayée

Bonjour {client},

Malgré mon précédent rappel, la facture n° {numero} du {date}, d'un montant
de {total:.2f} €, demeure impayée.

Je vous remercie de procéder au règlement sous 8 jours. À défaut, des
pénalités de retard seront appliquées conformément aux mentions de la
facture (article L441-10 du Code de commerce).

Cordialement,
{emetteur}""",
    3: """Objet : Dernier avis avant recouvrement — facture n° {numero}

Madame, Monsieur,

Malgré mes relances, la facture n° {numero} du {date}, d'un montant de
{total:.2f} €, reste impayée à ce jour.

Sans règlement intégral sous 8 jours à compter de ce message, je me verrai
contraint(e) d'engager une procédure de recouvrement (injonction de payer),
dont les frais seront à votre charge, en sus des pénalités de retard et de
l'indemnité forfaitaire de recouvrement de 40 € (article D441-5 du Code de
commerce).

Je reste disponible pour trouver une solution rapide.

{emetteur}""",
}


def generer(chemin_json, niveau=1):
    data = json.loads(Path(chemin_json).read_text(encoding="utf-8"))
    total = sum(l["quantite"] * l["prix_unitaire"] for l in data["lignes"])
    return MODELES[niveau].format(
        numero=data.get("numero", "?"),
        date=data.get("date", "?"),
        total=total,
        client=data["client"].get("nom", ""),
        emetteur=data["emetteur"].get("nom", ""),
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Mails de relance de facture")
    p.add_argument("facture", help="fichier JSON de la facture")
    p.add_argument("--niveau", type=int, choices=[1, 2, 3], default=1)
    args = p.parse_args()
    print(generer(args.facture, args.niveau))
