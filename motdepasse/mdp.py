#!/usr/bin/env python3
"""Générateur de mots de passe sécurisés (module secrets, aléa cryptographique).

Usage :
  ./mdp.py                    # mot de passe de 20 caractères
  ./mdp.py gen -l 32          # longueur au choix
  ./mdp.py gen --simple       # sans symboles (sites capricieux)
  ./mdp.py phrase             # phrase de passe : 5 mots français faciles à retenir
  ./mdp.py pin                # code PIN 6 chiffres
"""

import argparse
import secrets
import string

MOTS = (
    "arbre avion badge bague banane barque bateau bijou bison bouche bougie "
    "brume cactus camion canard carte castor cerise chaise chaton cheval chien "
    "citron cloche coeur colline comete corde coton crabe crayon cristal cuivre "
    "dauphin desert domino dragon eclair ecole encre epice etoile falaise farine "
    "fenetre fleur flocon foret fourmi fraise fusee galet gant gateau girafe "
    "glace grange guitare hibou horizon huitre igloo jardin jetee jungle kayak "
    "lampe lapin lavande lezard licorne lilas lionne livre losange loutre lune "
    "maison manoir marbre marmite melon menthe meteore miel miroir montagne "
    "moulin muguet murier navire neige noyau nuage ocean oiseau ombre onyx "
    "orage orange orchidee ourson panda panier papier parfum perle phare piano "
    "pierre pinceau pirate plage plume pomme pont prairie prune puzzle quartz "
    "radis rainette rameau recif renard riviere rocher rosee rubis sable safran "
    "saphir sapin savane sirop soleil source souris sucre tambour tigre tilleul "
    "tomate tortue toupie tresor trompette tulipe vague vallee vanille velours "
    "verger violon volcan voyage wagon xylophone yaourt zebre zenith"
).split()


def gen(longueur=20, simple=False):
    alphabet = string.ascii_letters + string.digits
    if not simple:
        alphabet += "!#$%&*+-=?@_"
    while True:
        mdp = "".join(secrets.choice(alphabet) for _ in range(longueur))
        # garantit au moins une minuscule, une majuscule et un chiffre
        if (any(c.islower() for c in mdp) and any(c.isupper() for c in mdp)
                and any(c.isdigit() for c in mdp)):
            return mdp


def phrase(nb_mots=5, separateur="-"):
    mots = [secrets.choice(MOTS) for _ in range(nb_mots)]
    # un chiffre à la fin pour les sites qui l'exigent
    return separateur.join(mots) + separateur + str(secrets.randbelow(100))


def pin(longueur=6):
    return "".join(secrets.choice(string.digits) for _ in range(longueur))


def main():
    p = argparse.ArgumentParser(description="Générateur de mots de passe")
    sub = p.add_subparsers(dest="cmd")

    pg = sub.add_parser("gen", help="mot de passe aléatoire")
    pg.add_argument("-l", "--longueur", type=int, default=20)
    pg.add_argument("--simple", action="store_true", help="sans symboles")

    pp = sub.add_parser("phrase", help="phrase de passe mémorisable")
    pp.add_argument("-n", "--mots", type=int, default=5)

    pi = sub.add_parser("pin", help="code PIN")
    pi.add_argument("-l", "--longueur", type=int, default=6)

    args = p.parse_args()
    if args.cmd == "phrase":
        print(phrase(args.mots))
    elif args.cmd == "pin":
        print(pin(args.longueur))
    else:
        longueur = getattr(args, "longueur", 20)
        simple = getattr(args, "simple", False)
        print(gen(longueur, simple))


if __name__ == "__main__":
    main()
