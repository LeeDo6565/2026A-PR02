import pytest

from historique import Historique

VALEURS = {"budget": 5_000_000.0, "runtime": 120.0, "annee": 2010.0,
           "original_language": "en", "genres": ["Action", "Drama"]}


def test_lire_sans_fichier_renvoie_liste_vide(tmp_path):  # CAS LIMITE : aucune prédiction encore
    historique = Historique(str(tmp_path / "historique.csv"))
    assert historique.lire() == []
    assert len(historique) == 0


def test_ajouter_cree_le_fichier_et_le_dossier(tmp_path):  # le dossier n'existe pas encore
    chemin = tmp_path / "sous_dossier" / "historique.csv"
    Historique(str(chemin)).ajouter(VALEURS, 6.4)
    assert chemin.exists()


def test_ajouter_puis_lire(tmp_path):  # CAS USUEL : ce qu'on écrit est ce qu'on relit
    historique = Historique(str(tmp_path / "historique.csv"))
    historique.ajouter(VALEURS, 6.4321)
    lignes = historique.lire()
    assert len(lignes) == 1
    assert lignes[0]["note"] == pytest.approx(6.43)  # arrondie à 2 décimales
    assert lignes[0]["genres"] == "Action ; Drama"
    assert lignes[0]["original_language"] == "en"


def test_plusieurs_ajouts_gardent_tout(tmp_path):  # « a » ajoute sans effacer, une seule en-tête
    historique = Historique(str(tmp_path / "historique.csv"))
    for note in (5.0, 6.0, 7.0):
        historique.ajouter(VALEURS, note)
    assert len(historique) == 3
    assert sorted(ligne["note"] for ligne in historique.lire()) == [5.0, 6.0, 7.0]
