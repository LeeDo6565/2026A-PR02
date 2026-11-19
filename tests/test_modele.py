import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import mean_squared_error

from modele import Modele, preparer_caracteristiques, rmse


# --- Fixture : un petit jeu de films inventés --------------------------------
@pytest.fixture
def films() -> pd.DataFrame:
    """60 films inventés, assez pour séparer entraînement et test."""
    generateur = np.random.default_rng(0)  # graine fixée : toujours les mêmes films
    n = 60
    return pd.DataFrame({
        "budget": generateur.uniform(1e5, 1e8, n),
        "runtime": generateur.uniform(80, 180, n),
        "annee": generateur.integers(1980, 2016, n),
        "original_language": generateur.choice(["en", "fr"], n),
        "genres": generateur.choice(["Action", "Drama", "Action Drama"], n),
        "vote_average": generateur.uniform(4, 8, n),
    })


# --- rmse (calcul vectorisé avec NumPy) ---------------------------------------
def test_rmse_egale_celle_de_scikit_learn():  # CAS USUEL : notre calcul = celui de scikit-learn
    y_reel = np.array([6.0, 7.5, 5.2, 8.1])
    y_predit = np.array([6.3, 7.0, 5.9, 7.8])
    attendu = np.sqrt(mean_squared_error(y_reel, y_predit))
    assert rmse(y_reel, y_predit) == pytest.approx(attendu)


def test_rmse_prediction_parfaite_vaut_zero():  # CAS LIMITE : aucune erreur
    assert rmse([5.0, 6.0], [5.0, 6.0]) == pytest.approx(0.0)


@pytest.mark.parametrize("y_reel, y_predit", [([], []), ([1.0, 2.0], [1.0])])
def test_rmse_tableaux_invalides(y_reel, y_predit):  # CAS D'ERREUR : vide ou tailles différentes
    with pytest.raises(ValueError):
        rmse(y_reel, y_predit)


# --- preparer_caracteristiques -------------------------------------------------
def test_preparer_cree_une_colonne_par_langue_et_par_genre():
    df = pd.DataFrame({"budget": [1e6], "runtime": [100], "annee": [2010],
                       "original_language": ["fr"], "genres": ["Drama Science Fiction"]})
    x = preparer_caracteristiques(df, ["en", "fr"], ["Action", "Drama", "Science-Fiction"])
    assert list(x.columns) == ["budget", "runtime", "annee", "langue_en", "langue_fr",
                               "genre_Action", "genre_Drama", "genre_Science-Fiction"]
    assert x.iloc[0].tolist() == [1e6, 100, 2010, 0, 1, 0, 1, 1]


# --- Modele ----------------------------------------------------------------------
def test_entrainer_renvoie_les_metriques(films):
    modele = Modele(["en", "fr"], ["Action", "Drama"])
    resultats = modele.entrainer(films)
    assert resultats["taille_test"] == 12  # 20 % de 60 films
    assert resultats["rmse_modele"] >= 0
    assert resultats["r2_reference"] <= 0.01  # la moyenne n'explique (presque) rien


def test_predire_renvoie_une_note_dans_l_intervalle_des_donnees(films):
    modele = Modele(["en", "fr"], ["Action", "Drama"])
    modele.entrainer(films)
    note = modele.predire({"budget": 5e6, "runtime": 120, "annee": 2000,
                           "original_language": "en", "genres": ["Drama"]})
    assert 4 <= note <= 8  # une forêt aléatoire ne sort jamais des notes vues


def test_tracer_avant_entrainement_leve_une_erreur(tmp_path):
    modele = Modele(["en"], ["Action"])
    with pytest.raises(RuntimeError):
        modele.tracer_predit_reel(str(tmp_path / "graphique.png"))
