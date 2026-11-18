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
    resultat= nettoyer_donnees(df)  # on transmet le tableau à nettoyer_donnees(df) 
    assert list(resultat["title"])== ["B"] # on vérifie que le résultat ne contient que la titre B, car A n'est pas accepté(budget)