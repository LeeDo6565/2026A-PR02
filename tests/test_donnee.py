import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from donnees import nettoyer_donnees

def test_nettoyer_retire_budget_zero():
    df = pd.DataFrame ({                    #Crée un DataFrame Pandas nommé df--> c'est le tableau qu'on va envoyer à la fonction nettoyer_donnees.
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
    resultat= nettoyer_donnees(df)
    assert list(resultat["title"])== ["B"]