import pandas as pd
import sys # module qui donne accès à certaines informations et fonctions liées à l'interpréteur, notamment la liste des dossiers où Python cherche les modules
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src")) 
# ajouter le dossier src a cette liste de dossiers, afin d'être capable d'importer donnees
from donnees import nettoyer_donnees

def test_nettoyer_retire_budget_zero():
    df = pd.DataFrame ({                    #Cree un tableau(DataFrame) avec deux films: A un budget de 0, B budget de 5_000_000
        "status" : ["Released","Released"],     
        "vote_count": [100, 100],
        "budget": [0, 5_000_000],
        "runtime": [100, 110],
        "genres": ["Action", "Drama"],
        "release_date": ["2010-05-01", "2012-07-15"],
        "title": ["A", "B"],
        "original_language": ["en", "en"],
        "vote_average": [6.0, 7.0],
    })
    resultat= nettoyer_donnees(df, films_min_langue=1)  # on transmet le tableau à nettoyer_donnees(df) 
    assert list(resultat["title"])== ["B"] # on vérifie que le résultat ne contient que la titre B, car A n'est pas accepté(budget)
    # AJOUT : ajout de films_min_langue = 1 , car sinon le test échoue. Le test est effectué avec 2 films à la fois,
    #   donc le critère pour les langues (20 minimum) ne peut jamais être respecté et le film est retiré, même si le critère de budget est respecté. 
    #   en ajoutant films_min_langue = 1, on "force" un minimum et seulement le budget est réellement testé.

def test_nettoyer_retire_budget_aberrant():  # un budget de 30 $ est une erreur de saisie
    df = pd.DataFrame({
        "status": ["Released", "Released"],
        "vote_count": [100, 100],
        "budget": [30, 5_000_000],
        "runtime": [100, 110],
        "genres": ["Action", "Drama"],
        "release_date": ["2010-05-01", "2012-07-15"],
        "title": ["A", "B"],
        "original_language": ["en", "en"],
        "vote_average": [6.0, 7.0],
    })
    resultat = nettoyer_donnees(df, films_min_langue=1)
    assert list(resultat["title"]) == ["B"]


def test_nettoyer_retire_langue_rare():  # 20 films en anglais (gardés), 1 en japonais (retiré)
    n = 21
    df = pd.DataFrame({
        "status": ["Released"] * n,
        "vote_count": [100] * n,
        "budget": [5_000_000] * n,
        "runtime": [100] * n,
        "genres": ["Drama"] * n,
        "release_date": ["2010-05-01"] * n,
        "title": [f"Film {i}" for i in range(n)],
        "original_language": ["en"] * 20 + ["ja"],
        "vote_average": [6.0] * n,
    })
    resultat = nettoyer_donnees(df)  # minimum par défaut : 20 films par langue
    assert set(resultat["original_language"]) == {"en"}
    assert len(resultat) == 20
