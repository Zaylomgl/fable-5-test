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


if __name__ == "__main__":
    unittest.main()
