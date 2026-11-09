import os 

import pandas as pd

import json

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


def extraire_genres(chaine:str)-> list[str]:
    texte= chaine.replace("Science Fiction", "Science-Fiction").replace("TV Movie", "TV-Movie") #met Action Science Fiction en ['Action', 'Science-Fiction']
    return texte 

def construire_metadonnees(df: pd.DataFrame, films_min_langue: int=20) -> dict:
    comptes= df["original_language"].value_counts() # Compte les films par langue : un tableau du genre en → 3000, fr → 60, ...
    langues = sorted(comptes[comptes >= films_min_langue].index) #Garde les langues avec au moins 20 films, prend leurs noms et trie
    genres= sorted({g for ligne in df["genres"] for g in extraire_genres(ligne)})# Parcourt chaque film, découpe ses genres, et garde chaque genre une seule fois, trié
    return {"budget_min": int(df["budget"].min()), "budget_max": int(df["budget"].max()), # Le plus petit et le plus grand budget des données
            "runtime_min": int(df["runtime"].min()), "runtime_max": int(df["runtime"].max()), # idem pour la durée
            "annee_min": int(df["annee"].min()), "annee_max": int(df["annee"].max()), # idem pour l'année de sortie 
            "langues": langues, "genres": genres,} # les deux listes de choix possible 

def sauvegarder_metadonnees(meta: dict, chemin: str):
    os.makedirs(os.path.dirname(chemin), exist_ok=True) # Crée le dossier du fichier (ex. « modeles ») s'il n'existe pas déjà
    with open(chemin, "w", encoding="utf-8") as f:           
        json.dump(meta, f, ensure_ascii=False, indent=2)