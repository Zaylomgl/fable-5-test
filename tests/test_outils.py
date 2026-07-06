"""Tests des outils — lance : python3 -m unittest discover tests"""

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

RACINE = Path(__file__).parent.parent


def charger_module(chemin, nom):
    spec = importlib.util.spec_from_file_location(nom, RACINE / chemin)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


veille = charger_module("veille-prix/veille.py", "veille")
facture = charger_module("facture/facture.py", "facture")
abos = charger_module("abonnements/abos.py", "abos")
partage = charger_module("partage/partage.py", "partage")
mdp = charger_module("motdepasse/mdp.py", "mdp")
rappels = charger_module("rappels/rappels.py", "rappels")
tjm = charger_module("tjm/tjm.py", "tjm")
relance = charger_module("relance/relance.py", "relance")
trajet = charger_module("trajet/trajet.py", "trajet")
epargne = charger_module("epargne/epargne.py", "epargne")
resiliation = charger_module("resiliation/resiliation.py", "resiliation")


class TestVeillePrix(unittest.TestCase):
    def test_prix_virgule(self):
        self.assertEqual(veille.extraire_prix("Prix : 299,99 €"), 299.99)

    def test_prix_point(self):
        self.assertEqual(veille.extraire_prix("only 19.99 € today"), 19.99)

    def test_symbole_avant(self):
        self.assertEqual(veille.extraire_prix("€ 45,00"), 45.0)

    def test_prix_le_plus_frequent(self):
        html = "ancien 349,00 € — promo 299,99 € — bouton 299,99 € — méta 299,99 €"
        self.assertEqual(veille.extraire_prix(html), 299.99)

    def test_aucun_prix(self):
        self.assertIsNone(veille.extraire_prix("<html>rien ici</html>"))

    def test_milliers_point(self):
        self.assertEqual(veille.extraire_prix("promo 1.299 €"), 1299.0)

    def test_milliers_espace(self):
        self.assertEqual(veille.extraire_prix("promo 1 299,00 €"), 1299.0)

    def test_milliers_insecable(self):
        self.assertEqual(veille.extraire_prix("promo 1 299 €"), 1299.0)


class TestFacture(unittest.TestCase):
    def _donnees(self):
        return {
            "numero": "TEST-1",
            "emetteur": {"nom": "Moi"},
            "client": {"nom": "Client"},
            "lignes": [
                {"description": "Presta A", "quantite": 2, "prix_unitaire": 100.0},
                {"description": "Presta B", "quantite": 1, "prix_unitaire": 50.5},
            ],
        }

    def test_total_facture(self):
        with tempfile.TemporaryDirectory() as d:
            j = Path(d) / "f.json"
            j.write_text(json.dumps(self._donnees()), encoding="utf-8")
            sortie, total = facture.generer(j)
            self.assertEqual(total, 250.5)
            html = sortie.read_text(encoding="utf-8")
            self.assertIn("FACTURE", html)
            self.assertIn("250.50 €", html)

    def test_echappement_html(self):
        donnees = self._donnees()
        donnees["lignes"][0]["description"] = "Maintenance <serveur> & suivi"
        with tempfile.TemporaryDirectory() as d:
            j = Path(d) / "f.json"
            j.write_text(json.dumps(donnees), encoding="utf-8")
            sortie, _ = facture.generer(j)
            html = sortie.read_text(encoding="utf-8")
            self.assertIn("Maintenance &lt;serveur&gt; &amp; suivi", html)
            self.assertNotIn("<serveur>", html)

    def test_mode_devis(self):
        with tempfile.TemporaryDirectory() as d:
            j = Path(d) / "f.json"
            j.write_text(json.dumps(self._donnees()), encoding="utf-8")
            sortie, _ = facture.generer(j, devis=True)
            html = sortie.read_text(encoding="utf-8")
            self.assertIn("DEVIS", html)
            self.assertIn("Validité", html)
            self.assertTrue(sortie.name.endswith(".devis.html"))


class TestAbonnements(unittest.TestCase):
    def test_cout_mensuel(self):
        self.assertEqual(abos.cout_mensuel({"prix": 13.49, "periode": "mensuel"}), 13.49)
        self.assertEqual(abos.cout_mensuel({"prix": 120.0, "periode": "annuel"}), 10.0)

    def test_echeance_mensuelle_a_venir(self):
        abo = {"periode": "mensuel", "jour": 20}
        self.assertEqual(
            abos.prochaine_echeance(abo, date(2026, 7, 6)), date(2026, 7, 20)
        )

    def test_echeance_mensuelle_passee_bascule_mois_suivant(self):
        abo = {"periode": "mensuel", "jour": 2}
        self.assertEqual(
            abos.prochaine_echeance(abo, date(2026, 7, 6)), date(2026, 8, 2)
        )

    def test_echeance_decembre(self):
        abo = {"periode": "mensuel", "jour": 1}
        self.assertEqual(
            abos.prochaine_echeance(abo, date(2026, 12, 15)), date(2027, 1, 1)
        )

    def test_jour_31_plafonne_a_28(self):
        abo = {"periode": "mensuel", "jour": 31}
        self.assertEqual(
            abos.prochaine_echeance(abo, date(2026, 2, 10)), date(2026, 2, 28)
        )

    def test_echeance_annuelle(self):
        abo = {"periode": "annuel", "date": "2025-09-01"}
        self.assertEqual(
            abos.prochaine_echeance(abo, date(2026, 7, 6)), date(2026, 9, 1)
        )


class TestBudget(unittest.TestCase):
    def test_cycle_complet_via_cli(self):
        with tempfile.TemporaryDirectory() as d:
            script = Path(d) / "budget.py"
            script.write_text(
                (RACINE / "budget/budget.py").read_text(encoding="utf-8"),
                encoding="utf-8",
            )

            def run(*args):
                return subprocess.run(
                    [sys.executable, str(script), *args],
                    capture_output=True, text=True, check=True,
                ).stdout

            run("add", "12.50", "courses", "Test")
            run("add", "100", "revenu", "Test", "--in")
            bilan = run("mois")
            self.assertIn("100.00", bilan)
            self.assertIn("12.50", bilan)
            self.assertIn("87.50", bilan)
            cat = run("cat")
            self.assertIn("courses", cat)


class TestPartage(unittest.TestCase):
    def test_soldes_equilibre(self):
        depenses = [
            {"qui": "Alice", "montant": 30.0, "pour": None},
            {"qui": "Bob", "montant": 30.0, "pour": None},
        ]
        net = partage.soldes(depenses)
        self.assertAlmostEqual(net["Alice"], 0.0)
        self.assertAlmostEqual(net["Bob"], 0.0)

    def test_soldes_simple(self):
        depenses = [{"qui": "Alice", "montant": 30.0, "pour": ["Alice", "Bob"]}]
        net = partage.soldes(depenses)
        self.assertAlmostEqual(net["Alice"], 15.0)
        self.assertAlmostEqual(net["Bob"], -15.0)

    def test_reglements(self):
        virements = partage.reglements({"Alice": 20.0, "Bob": -20.0})
        self.assertEqual(virements, [("Bob", "Alice", 20.0)])

    def test_reglements_conserve_les_totaux(self):
        net = {"A": 50.0, "B": -30.0, "C": -20.0, "D": 0.0}
        virements = partage.reglements(net)
        recus = sum(m for _, c, m in virements if c == "A")
        self.assertAlmostEqual(recus, 50.0)
        self.assertLessEqual(len(virements), 2)


class TestMotDePasse(unittest.TestCase):
    def test_longueur_et_classes(self):
        m = mdp.gen(24)
        self.assertEqual(len(m), 24)
        self.assertTrue(any(c.islower() for c in m))
        self.assertTrue(any(c.isupper() for c in m))
        self.assertTrue(any(c.isdigit() for c in m))

    def test_simple_sans_symboles(self):
        m = mdp.gen(30, simple=True)
        self.assertTrue(all(c.isalnum() for c in m))

    def test_phrase(self):
        ph = mdp.phrase(4)
        self.assertEqual(len(ph.split("-")), 5)  # 4 mots + chiffre final

    def test_pin(self):
        p = mdp.pin(6)
        self.assertEqual(len(p), 6)
        self.assertTrue(p.isdigit())


class TestRappels(unittest.TestCase):
    def test_annuel_a_venir(self):
        self.assertEqual(
            rappels.prochaine_occurrence("09-15", date(2026, 7, 6)), date(2026, 9, 15)
        )

    def test_annuel_passe_bascule_annee_suivante(self):
        self.assertEqual(
            rappels.prochaine_occurrence("03-14", date(2026, 7, 6)), date(2027, 3, 14)
        )

    def test_date_unique_passee(self):
        self.assertIsNone(rappels.prochaine_occurrence("2026-01-01", date(2026, 7, 6)))

    def test_29_fevrier_annee_non_bissextile(self):
        self.assertEqual(
            rappels.prochaine_occurrence("02-29", date(2026, 1, 10)), date(2026, 3, 1)
        )

    def test_validation(self):
        self.assertTrue(rappels.valider("03-14"))
        self.assertTrue(rappels.valider("2026-12-31"))
        self.assertFalse(rappels.valider("13-45"))
        self.assertFalse(rappels.valider("n'importe quoi"))


class TestTjm(unittest.TestCase):
    def test_calcul(self):
        r = tjm.calculer(2000, jours_par_mois=15, taux_charges=22.0)
        self.assertAlmostEqual(r["ca_mensuel"], 2000 / 0.78, places=2)
        self.assertAlmostEqual(r["tjm"], 2000 / 0.78 / 15, places=2)
        self.assertFalse(r["depasse_micro"])

    def test_seuil_micro(self):
        r = tjm.calculer(6000, jours_par_mois=18, taux_charges=22.0)
        self.assertTrue(r["depasse_micro"])


class TestRelance(unittest.TestCase):
    def test_niveaux(self):
        donnees = {
            "numero": "2026-042",
            "date": "01/06/2026",
            "emetteur": {"nom": "Moi"},
            "client": {"nom": "Client SARL"},
            "lignes": [{"description": "X", "quantite": 2, "prix_unitaire": 100.0}],
        }
        with tempfile.TemporaryDirectory() as d:
            j = Path(d) / "f.json"
            j.write_text(json.dumps(donnees), encoding="utf-8")
            for niveau, attendu in [(1, "Rappel"), (2, "Relance"), (3, "recouvrement")]:
                texte = relance.generer(j, niveau)
                self.assertIn(attendu, texte)
                self.assertIn("2026-042", texte)
                self.assertIn("200.00", texte)


class TestTrajet(unittest.TestCase):
    def test_calcul_complet(self):
        r = trajet.calculer(100, conso=6.0, prix_litre=2.0, peage=10, passagers=2, usure=0.10)
        self.assertAlmostEqual(r["carburant"], 12.0)
        self.assertAlmostEqual(r["entretien"], 10.0)
        self.assertAlmostEqual(r["total"], 32.0)
        self.assertAlmostEqual(r["par_personne"], 16.0)

    def test_essence_seule(self):
        r = trajet.calculer(200, conso=5.0, prix_litre=1.8, usure=0)
        self.assertAlmostEqual(r["total"], 18.0)


class TestEpargne(unittest.TestCase):
    def test_mois_restants(self):
        self.assertEqual(epargne.mois_restants(date(2027, 7, 6), date(2026, 7, 6)), 12)
        self.assertEqual(epargne.mois_restants(date(2026, 7, 20), date(2026, 7, 6)), 1)

    def test_sans_interets(self):
        self.assertAlmostEqual(epargne.mensualite(1200, 12), 100.0)
        self.assertAlmostEqual(epargne.mensualite(1200, 12, deja=200), 1000 / 12)

    def test_objectif_atteint(self):
        self.assertEqual(epargne.mensualite(1000, 12, deja=1500), 0.0)

    def test_avec_interets_moins_cher(self):
        sans = epargne.mensualite(10000, 24)
        avec = epargne.mensualite(10000, 24, taux_annuel=3)
        self.assertLess(avec, sans)
        # la valeur future des versements doit atteindre l'objectif
        t = 0.03 / 12
        futur = avec * ((1 + t) ** 24 - 1) / t
        self.assertAlmostEqual(futur, 10000, places=2)


class TestResiliation(unittest.TestCase):
    def test_lettre_complete(self):
        lettre = resiliation.generer(
            "FitPlus", "Théo", "12 rue X", numero="C-42",
            motif="demenagement", quand=date(2026, 7, 6),
        )
        self.assertIn("FitPlus", lettre)
        self.assertIn("contrat n° C-42", lettre)
        self.assertIn("déménagement", lettre)
        self.assertIn("06/07/2026", lettre)

    def test_sans_numero(self):
        lettre = resiliation.generer("Netflix", "Théo", "12 rue X")
        self.assertNotIn("contrat n°", lettre)
        self.assertIn("ne pas le reconduire", lettre)


class TestTempoEtCourses(unittest.TestCase):
    def _run_copie(self, source, dossier, *args):
        script = Path(dossier) / Path(source).name
        if not script.exists():
            script.write_text((RACINE / source).read_text(encoding="utf-8"), encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(script), *args],
            capture_output=True, text=True,
        )

    def test_tempo_cycle(self):
        with tempfile.TemporaryDirectory() as d:
            r = self._run_copie("tempo/tempo.py", d, "start", "Projet X")
            self.assertIn("démarrée", r.stdout)
            r = self._run_copie("tempo/tempo.py", d, "start", "Projet Y")
            self.assertEqual(r.returncode, 1)  # refuse deux sessions en même temps
            r = self._run_copie("tempo/tempo.py", d, "stop")
            self.assertIn("Projet X", r.stdout)
            r = self._run_copie("tempo/tempo.py", d, "bilan", "--tjm", "350")
            self.assertIn("Projet X", r.stdout)
            self.assertIn("À facturer", r.stdout)

    def test_courses_cycle(self):
        with tempfile.TemporaryDirectory() as d:
            self._run_copie("courses/courses.py", d, "add", "pâtes", "tomates")
            r = self._run_copie("courses/courses.py", d)
            self.assertIn("pâtes", r.stdout)
            self._run_copie("courses/courses.py", d, "done", "pâtes")
            self._run_copie("courses/courses.py", d, "clear")
            r = self._run_copie("courses/courses.py", d)
            self.assertNotIn("pâtes", r.stdout)
            self.assertIn("tomates", r.stdout)


if __name__ == "__main__":
    unittest.main()
