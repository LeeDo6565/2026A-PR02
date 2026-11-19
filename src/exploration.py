"""Exploration du jeu de données (volet 2, étape 1) : résumé et graphiques.

Lancer depuis la racine du dépôt : python src/exploration.py
"""
import os
# construit les chemins de fichiers et créer le dossier des figures

import matplotlib.pyplot as plt
# pyplot : pour tracer les graphiques (chapitre 13)
import pandas as pd
# pandas : pour manipuler le tableau des films (DataFrame)

from donnees import charger_donnees, nettoyer_donnees
# fonctions de lecture et de nettoyage

RACINE = os.path.join(os.path.dirname(__file__), "..")
# Dossier du projet (même concept que dans entrainer.py)
CHEMIN_CSV = os.path.join(RACINE, "donnees", "movies.csv")
# Le jeu de données brut
DOSSIER_FIGURES = os.path.join(RACINE, "figures")
# Le dossier où les graphiques seront enregistrés


def resumer(df: pd.DataFrame) -> dict:
    """Renvoie un petit résumé du DataFrame : nombre de lignes et de colonnes,
    et nombre de valeurs manquantes par colonne (seulement celles qui en ont).

    Reçoit n'importe quel DataFrame. Renvoie un dictionnaire avec les clés
    « lignes », « colonnes » et « manquantes ». Ne lève pas d'exception.
    """
    manquantes = df.isna().sum()
    # isna() met True là où une valeur manque ; sum() compte les True de chaque colonne
    return {"lignes": len(df), "colonnes": df.shape[1],
            "manquantes": manquantes[manquantes > 0].to_dict()}
    # df.shape[1] = nombre de colonnes ; garde seulement les colonnes qui ont des valeurs
    # manquantes, puis to_dict() les transforme en dictionnaire {colonne: nombre}


def tracer_distribution_notes(df: pd.DataFrame, chemin: str) -> None:
    """Trace l'histogramme des notes (vote_average) et l'enregistre dans « chemin ».

    Reçoit les films nettoyés et le chemin de l'image à créer. Ne renvoie rien.
    Lève KeyError si la colonne vote_average manque, et OSError si l'image
    ne peut pas être écrite.
    """
    moyenne = df["vote_average"].mean()
    # note moyenne de tous les films
    fig, ax = plt.subplots(figsize=(8, 5))
    # Crée une figure de 8 x 5 pouces avec un seul graphique (ax)
    ax.hist(df["vote_average"], bins=30, color="#FFA94D", edgecolor="#2B2D6E")
    # Histogramme : les notes sont regroupées en 30 intervalles ; la hauteur de chaque barre
    # est le nombre de films dans cet intervalle. Couleurs reprises du thème de l'interface
    ax.axvline(moyenne, color="#E4577F", linewidth=2, label=f"Moyenne : {moyenne:.2f}")
    # Ligne verticale à la moyenne : c'est la