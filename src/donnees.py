import os

import pandas as pd

import json

def charger_donnees(chemin: str) -> pd.DataFrame: # Reçoit le chemin du fichier, renvoie un DataFrame
    """Lit le fichier CSV des films et le renvoie sous forme de DataFrame.

    Reçoit le chemin du fichier CSV. Renvoie un DataFrame pandas avec une
    ligne par film. Lève FileNotFoundError si le fichier n'existe pas.
    """
    if not os.path.exists(chemin):
        raise FileNotFoundError(f"Fichier introuvable: {chemin}")
    return pd.read_csv(chemin) # ouvre le fichier CSV situé à ce chemin et le transforme en tableau pandas(dataframe)

def nettoyer_donnees(df:pd.DataFrame, votes_min: int = 10, films_min_langue: int = 20)-> pd.DataFrame:
    """Garde les films exploitables et les colonnes utiles au modèle.

    Reçoit le DataFrame brut de movies.csv. Retire les films non sortis, ceux
    avec moins de « votes_min » votes, un budget inconnu ou aberrant (10 000 $
    ou moins), une durée à 0, et les films dont la langue compte moins de
    « films_min_langue » films. Renvoie un nouveau DataFrame avec la colonne
    « annee » ajoutée. Lève KeyError si une colonne attendue manque.
    """
    films = df[(df["status"] == "Released") #condition 1: le film est sortie
               & (df["vote_count"] >= votes_min) # Condition 2 : au moins 10 votes, sinon la note n'est pas fiable
               & (df["budget"] > 10_000) # Condition 3 : budget connu et réaliste (0 = inconnu ; quelques dollars = saisi en millions)
               & (df["runtime"] > 0)].copy() # Condition 4 : durée connue; .copy() crée un nouveau tableau indépendant

    films["annee"] = pd.to_datetime(films["release_date"]).dt.year #Transforme le texte de la date en vraie date, puis garde seulement l'année
    films = films.dropna(subset=["genres", "annee"]) # retire les lignes où les genres ou l'année manquent
    films["annee"] = films["annee"].astype(int) #Convertit l'année en nombre entier(2010 et non 2010.0)
    comptes = films["original_language"].value_counts() # nombre de films par langue
    langues = comptes[comptes >= films_min_langue].index # langues avec au moins 20 films
    films = films[films["original_language"].isin(langues)] # garde seulement les films de ces langues (les mêmes que dans l'interface)
    return films[["title", "budget", "runtime", "annee",
                  "original_language", "genres", "vote_average"]] #renvoie le tableau avec seulement les colonnes utiles


def extraire_genres(chaine:str)-> list[str]:
    """Découpe le texte des genres d'un film en liste de genres.

    Reçoit un texte comme « Action Science Fiction ». Renvoie une liste comme
    ["Action", "Science-Fiction"] : les genres en deux mots sont d'abord
    réunis par un tiret. Lève AttributeError si « chaine » n'est pas un texte.
    """
    texte= chaine.replace("Science Fiction", "Science-Fiction").replace("TV Movie", "TV-Movie") #met Action Science Fiction en ['Action', 'Science-Fiction'] -> dans le but de faire un seul mot(on peut appliquer split)
    return texte.split()# renvoie une liste de mots ["Action", "Science-Fiction"]

def construire_metadonnees(df: pd.DataFrame, films_min_langue: int=20) -> dict: # les langues ayant au moins 20 films sont conservées
    """Construit les métadonnées dont l'interface a besoin pour se construire.

    Reçoit les films nettoyés. Renvoie un dictionnaire avec les bornes
    (minimum et maximum) du budget, de la durée et de l'année, la liste triée
    des langues ayant au moins « films_min_langue » films et la liste triée
    des genres. Lève KeyError si une colonne attendue manque.
    """
    comptes= df["original_language"].value_counts() # Compte les films par langue : un tableau du genre en → 3000, fr → 60, ...
    langues = sorted(comptes[comptes >= films_min_langue].index) #Garde les langues avec au moins 20 films, prend leurs noms et trie
    genres= sorted({g for ligne in df["genres"] for g in extraire_genres(ligne)})# Parcourt chaque film, découpe ses genres, et garde chaque genre une seule fois, trié()
    return {"budget_min": int(df["budget"].min()), "budget_max": int(df["budget"].max()), # Le plus petit et le plus grand budget des données
            "runtime_min": int(df["runtime"].min()), "runtime_max": int(df["runtime"].max()), # idem pour la durée
            "annee_min": int(df["annee"].min()), "annee_max": int(df["annee"].max()), # idem pour l'année de sortie
            "langues": langues, "genres": genres,} # les deux listes de choix possible

def sauvegarder_metadonnees(meta: dict, chemin: str) -> None:
    """Enregistre les métadonnées dans un fichier JSON lisible.

    Reçoit le dictionnaire des métadonnées et le chemin du fichier JSON.
    Crée le dossier s'il n'existe pas. Ne renvoie rien. Lève OSError si le
    fichier ne peut pas être écrit, et TypeError si une valeur n'est pas
    convertible en JSON.
    """
    os.makedirs(os.path.dirname(chemin), exist_ok=True) # Crée le dossier du fichier (ex. « modeles ») s'il n'existe pas déjà
    #os.path.dirname récupère le dossier parent d'un chemin de fichier. Alors chemin vaut "modeles/metadonnees.json" et  os.path.dirname(chemin) renvoie "modeles"
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2) #indent=2 veut dire que le JSON enregistré sera indenté avec deux espaces par niveau
