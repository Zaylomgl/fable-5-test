#!/usr/bin/env python3
"""Générateur de lettre de résiliation d'abonnement — à envoyer en recommandé.

Usage :
  ./resiliation.py "Salle de sport FitPlus" --numero "C-12345" \\
      --nom "Théo Gyssens" --adresse "12 rue Exemple, 75000 Paris"

Options :
  --motif legal    résiliation « loi Chatel / échéance » (défaut)
  --motif demenagement | sante | emploi   motifs légitimes (résiliation anticipée)
"""

import argparse
from datetime import date

MOTIFS = {
    "legal": "Conformément aux conditions générales de mon contrat, je souhaite "
             "ne pas le reconduire à sa prochaine échéance.",
    "demenagement": "En raison de mon déménagement (justificatif joint), je vous "
                    "demande la résiliation anticipée de mon contrat, ce motif "
                    "légitime étant prévu par vos conditions générales.",
    "sante": "Pour raison médicale (certificat joint), je vous demande la "
             "résiliation anticipée de mon contrat.",
    "emploi": "En raison d'un changement de situation professionnelle "
              "(justificatif joint), je vous demande la résiliation anticipée "
              "de mon contrat.",
}

LETTRE = """{nom}
{adresse}

{service}
(adresse du service client — à compléter)

Objet : Résiliation de mon abonnement{ref}
Lettre recommandée avec accusé de réception

{ville_date}

Madame, Monsieur,

Par la présente, je vous informe de ma décision de résilier mon abonnement
« {service} »{ref_long}.

{motif}

Je vous remercie de bien vouloir m'adresser une confirmation écrite de cette
résiliation, en précisant sa date d'effet, et de cesser tout prélèvement
au-delà de cette date. Tout prélèvement postérieur ferait l'objet d'une
demande de remboursement.

Veuillez agréer, Madame, Monsieur, mes salutations distinguées.

{nom}
(signature)
"""


def generer(service, nom, adresse, numero=None, motif="legal", quand=None):
    ref = f" (contrat n° {numero})" if numero else ""
    return LETTRE.format(
        nom=nom,
        adresse=adresse,
        service=service,
        ref=ref,
        ref_long=f", contrat n° {numero}" if numero else "",
        ville_date=f"Le {(quand or date.today()).strftime('%d/%m/%Y')}",
        motif=MOTIFS[motif],
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Lettre de résiliation d'abonnement")
    p.add_argument("service", help="nom du service à résilier")
    p.add_argument("--nom", required=True)
    p.add_argument("--adresse", required=True)
    p.add_argument("--numero", help="numéro de contrat/client")
    p.add_argument("--motif", choices=sorted(MOTIFS), default="legal")
    args = p.parse_args()
    print(generer(args.service, args.nom, args.adresse, args.numero, args.motif))
