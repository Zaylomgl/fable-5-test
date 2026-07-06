#!/usr/bin/env python3
"""La citation du jour — la même toute la journée, une nouvelle chaque matin.

Usage :
  ./citation.py             # celle du jour
  ./citation.py hasard      # une au hasard

Astuce : ajoute `python3 .../citation.py` à ton ~/.bashrc pour démarrer motivé.
"""

import random
import sys
from datetime import date

CITATIONS = [
    ("Le meilleur moment pour planter un arbre était il y a vingt ans. "
     "Le deuxième meilleur moment, c'est maintenant.", "proverbe chinois"),
    ("Ils ne savaient pas que c'était impossible, alors ils l'ont fait.", "Mark Twain"),
    ("Le succès, c'est tomber sept fois et se relever huit.", "proverbe japonais"),
    ("La chance sourit aux esprits préparés.", "Louis Pasteur"),
    ("Fais de ta vie un rêve, et d'un rêve, une réalité.", "Antoine de Saint-Exupéry"),
    ("Un voyage de mille lieues commence toujours par un premier pas.", "Lao Tseu"),
    ("Ce n'est pas parce que les choses sont difficiles que nous n'osons pas, "
     "c'est parce que nous n'osons pas qu'elles sont difficiles.", "Sénèque"),
    ("La simplicité est la sophistication suprême.", "Léonard de Vinci"),
    ("Choisissez un travail que vous aimez et vous n'aurez pas à travailler "
     "un seul jour de votre vie.", "Confucius"),
    ("L'avenir appartient à ceux qui croient à la beauté de leurs rêves.", "Eleanor Roosevelt"),
    ("Il n'y a qu'une façon d'échouer, c'est d'abandonner avant d'avoir réussi.",
     "Georges Clemenceau"),
    ("Que tu penses être capable ou incapable, tu as raison.", "Henry Ford"),
    ("La meilleure façon de prédire l'avenir, c'est de le créer.", "Peter Drucker"),
    ("Le talent, ça n'existe pas. Le talent, c'est d'avoir envie de faire quelque chose.",
     "Jacques Brel"),
    ("Rien n'est permanent, sauf le changement.", "Héraclite"),
    ("On ne subit pas l'avenir, on le fait.", "Georges Bernanos"),
    ("La persévérance, c'est ce qui rend l'impossible possible, le possible "
     "probable et le probable réalisé.", "Léon Trotsky"),
    ("Commencez par faire le nécessaire, puis le possible, et soudain vous "
     "réaliserez l'impossible.", "François d'Assise"),
    ("Un pessimiste voit la difficulté dans chaque opportunité, un optimiste "
     "voit l'opportunité dans chaque difficulté.", "Winston Churchill"),
    ("Le doute est le commencement de la sagesse.", "Aristote"),
]


def du_jour(quand=None):
    quand = quand or date.today()
    return CITATIONS[quand.toordinal() % len(CITATIONS)]


if __name__ == "__main__":
    if sys.argv[1:2] == ["hasard"]:
        texte, auteur = random.choice(CITATIONS)
    else:
        texte, auteur = du_jour()
    print(f"« {texte} »")
    print(f"   — {auteur}")
