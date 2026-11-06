import os 

import pandas as pd

def charger_donnees(chemin: str) -> pd.DataFrame: # Reçoit le chemin du fichier, renvoie un DataFrame
    if not os.path.exists(chemin):
        raise FileNotFoundError(f"Fichier introuvable: {chemin}") 
    return pd.read_csv(chemin) # ouvre le fichier CSV situé à ce chemin et le transforme en tableau pandas(dataframe)

def nettoyer_donnees(df:pd.DataFrame, votes_min: int = 10)-> pd.DataFrame:
    """Garde les films exploitables et les colonnes utiles au modèle.

    Retire les films non sortis, ceux avec peu de votes, un budget ou une
    durée à 0 (valeurs manquantes) et ajoute la colonne « annee ».
    """
    films = df[(df["status"] == "Released") #condition 1: le film est sortie
               & (df["vote_count"] >= votes_min) # Condition 2 : au moins 10 votes, sinon la note n'est pas fiable
               & (df["budget"] > 0) # Condition 3 : budget connu (0 voulait dire « inconnu »)
               & (df["runtime"] > 0)].copy() # Condition 4 : durée connue; .copy() crée un nouveau tableau indépendant
    
    films["annee"] = pd.to_datetime(films["release_date"]).dt.year #Transforme le texte de la date en vraie date, puis garde seulement l'année 
    films = films.dropna(subset=["genres", "annee"]) # retire les lignes où les genres ou l'année manquent 
    films["annee"] = films["annee"].astype(int) #Convertit l'année en nombre entier(2010 et non 2010.0)
    return films[["title", "budget", "runtime", "annee",
                  "original_language", "genres", "vote_average"]] #renvoie le tableau avec seulement les colonnes utiles 