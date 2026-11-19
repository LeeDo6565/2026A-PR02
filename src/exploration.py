"""Exploration du jeu de données (volet 2, étape 1) : résumé et graphiques.

Lancer depuis la racine du dépôt : python src/exploration.py
"""
import os

import matplotlib.pyplot as plt
import pandas as pd

from donnees import charger_donnees, nettoyer_donnees

RACINE = os.path.join(os.path.dirname(__file__), "..")
# Dossier du projet, peu importe d'où on lance le programme
CHEMIN_CSV = os.path.join(RACINE, "donnees", "movies.csv")
DOSSIER_FIGURES = os.path.join(RACINE, "figures")


def resumer(df: pd.DataFrame) -> dict:
    """Renvoie un petit résumé du DataFrame : nombre de lignes et de colonnes,
    et nombre de valeurs manquantes par colonne (seulement celles qui en ont).
    """
    manquantes = df.isna().sum()
    return {"lignes": len(df), "colonnes": df.shape[1],
            "manquantes": manquantes[manquantes > 0].to_dict()}


def tracer_distribution_notes(df: pd.DataFrame, chemin: str) -> None:
    """Trace l'histogramme des notes (vote_average) et l'enregistre dans « chemin »."""
    moyenne = df["vote_average"].mean()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(df["vote_average"], bins=30, color="#FFA94D", edgecolor="#2B2D6E")
    ax.axvline(moyenne, color="#E4577F", linewidth=2, label=f"Moyenne : {moyenne:.2f}")
    # Ligne verticale à la moyenne : c'est la prédiction du modèle de référence
    ax.set_title("Distribution des notes des films (après nettoyage)")
    ax.set_xlabel("Note moyenne du public (sur 10)")
    ax.set_ylabel("Nombre de films")
    ax.legend()
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    fig.savefig(chemin, dpi=120, bbox_inches="tight")
    plt.close(fig)


def tracer_budget_note(df: pd.DataFrame, chemin: str) -> None:
    """Trace la note en fonction du budget (échelle logarithmique) et l'enregistre."""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(df["budget"], df["vote_average"], s=8, alpha=0.4, color="#2B2D6E")
    ax.set_xscale("log")
    # Échelle log : les budgets vont de 10 000 $ à 380 M$, sinon tout serait écrasé à gauche
    ax.set_title("Note du public selon le budget du film")
    ax.set_xlabel("Budget ($, échelle logarithmique)")
    ax.set_ylabel("Note moyenne (sur 10)")
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    fig.savefig(chemin, dpi=120, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    brut = charger_donnees(CHEMIN_CSV)
    print("Avant nettoyage :", resumer(brut))
    print("Budgets à 0 :", (brut["budget"] == 0).sum())
    print("Budgets entre 1 $ et 9 999 $ :", brut["budget"].between(1, 9_999).sum())

    films = nettoyer_donnees(brut)
    print("Après nettoyage :", resumer(films))
    print(films["original_language"].value_counts())
    print(films.describe().round(2))

    tracer_distribution_notes(films, os.path.join(DOSSIER_FIGURES, "distribution_notes.png"))
    tracer_budget_note(films, os.path.join(DOSSIER_FIGURES, "budget_note.png"))
    print("Graphiques enregistrés dans le dossier figures/.")
