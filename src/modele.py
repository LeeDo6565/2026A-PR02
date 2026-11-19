"""Préparation des caractéristiques, entraînement, évaluation et sauvegarde du modèle."""
import os
import time
from functools import wraps
from typing import Callable

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split

from donnees import extraire_genres

GRAINE = 42  # graine aléatoire fixée : les résultats sont reproductibles
COLONNES_NUMERIQUES = ["budget", "runtime", "annee"]


# --- Outil du chapitre 7 : décorateur -------------------------------------
def chronometrer(fonction: Callable) -> Callable:
    """Décorateur qui affiche le temps d'exécution de la fonction décorée."""
    @wraps(fonction)  # garde le nom et la docstring de la fonction d'origine
    def enveloppe(*args, **kwargs):
        debut = time.perf_counter()
        resultat = fonction(*args, **kwargs)
        print(f"{fonction.__name__} : {time.perf_counter() - debut:.2f} s")
        return resultat
    return enveloppe


# --- Calcul vectorisé (chapitre 12) ----------------------------------------
def rmse(y_reel: np.ndarray, y_predit: np.ndarray) -> float:
    """Renvoie la racine de l'erreur quadratique moyenne, sans boucle Python.

    Reçoit deux tableaux de même taille (notes réelles et notes prédites).
    Lève ValueError si les tableaux sont vides ou de tailles différentes.
    """
    y_reel = np.asarray(y_reel, dtype=float)
    y_predit = np.asarray(y_predit, dtype=float)
    if y_reel.shape != y_predit.shape or y_reel.size == 0:
        raise ValueError("Les tableaux doivent être non vides et de même taille.")
    return float(np.sqrt(np.mean((y_reel - y_predit) ** 2)))


# --- Préparation des caractéristiques --------------------------------------
def preparer_caracteristiques(df: pd.DataFrame, langues: list[str],
                              genres: list[str]) -> pd.DataFrame:
    """Transforme des films en tableau de nombres compréhensible par le modèle.

    Reçoit un DataFrame avec budget, runtime, annee, original_language et
    genres (texte du type « Action Drama »). Renvoie les 3 colonnes numériques,
    une colonne 0/1 par langue et une colonne 0/1 par genre, toujours dans le
    même ordre. Lève KeyError si une de ces colonnes manque.
    """
    x = df[COLONNES_NUMERIQUES].astype(float).copy()
    for langue in langues:
        x[f"langue_{langue}"] = (df["original_language"] == langue).astype(int)
    listes = df["genres"].apply(extraire_genres)  # « Action Drama » -> ["Action", "Drama"]
    for genre in genres:
        x[f"genre_{genre}"] = listes.apply(lambda liste: genre in liste).astype(int)
    return x


# --- Classe Modele ----------------------------------------------------------
class Modele:
    """Une forêt aléatoire qui estime la note d'un film, et sa référence (la moyenne)."""

    def __init__(self, langues: list[str], genres: list[str]) -> None:
        self._langues = list(langues)
        self._genres = list(genres)
        self._regresseur = RandomForestRegressor(
            n_estimators=100, min_samples_leaf=5, random_state=GRAINE)
        # min_samples_leaf=5 : chaque feuille contient au moins 5 films (arbres moins détaillés,
        # donc un fichier beaucoup plus léger et moins de surapprentissage)
        self._reference = DummyRegressor(strategy="mean")
        self._y_test = np.array([])
        self._y_predit = np.array([])
        self._resultats: dict = {}

    @property
    def resultats(self) -> dict:
        """Copie des métriques calculées par entrainer() (vide avant l'entraînement)."""
        return dict(self._resultats)

    @chronometrer
    def entrainer(self, df: pd.DataFrame, taille_test: float = 0.2) -> dict:
        """Sépare les données, entraîne le modèle et la référence, puis les évalue.

        Reçoit les films nettoyés (avec la colonne vote_average). L'évaluation
        se fait uniquement sur l'ensemble de test, jamais sur les données qui ont
        servi à l'entraînement. Renvoie les métriques (RMSE et R²) du modèle et
        de la référence.
        """
        x = preparer_caracteristiques(df, self._langues, self._genres)
        y = df["vote_average"].to_numpy(dtype=float)
        x_train, x_test, y_train, y_test = train_test_split(
            x, y, test_size=taille_test, random_state=GRAINE)

        self._regresseur.fit(x_train, y_train)
        self._reference.fit(x_train, y_train)
        self._y_test = y_test
        self._y_predit = self._regresseur.predict(x_test)
        y_reference = self._reference.predict(x_test)

        self._resultats = {
            "rmse_modele": rmse(y_test, self._y_predit),
            "rmse_reference": rmse(y_test, y_reference),
            "r2_modele": float(r2_score(y_test, self._y_predit)),
            "r2_reference": float(r2_score(y_test, y_reference)),
            "taille_entrainement": len(y_train),
            "taille_test": len(y_test),
        }
        return self.resultats

    def predire(self, valeurs: dict) -> float:
        """Prédit la note d'un film à partir des valeurs validées par l'interface.

        « valeurs » contient budget, runtime, annee, original_language et
        genres (une liste, ex. ["Action", "Drama"]). Renvoie une note sur 10.
        """
        ligne = pd.DataFrame([{**valeurs, "genres": " ".join(valeurs["genres"])}])
        # Remet les genres sous forme de texte, comme dans le CSV, pour réutiliser la même préparation
        x = preparer_caracteristiques(ligne, self._langues, self._genres)
        return float(self._regresseur.predict(x)[0])

    def tracer_predit_reel(self, chemin: str) -> None:
        """Enregistre le graphique « prédit contre réel » de l'ensemble de test.

        Lève RuntimeError si le modèle n'a pas encore été entraîné.
        """
        if self._y_test.size == 0:
            raise RuntimeError("Entraînez le modèle avant de tracer ce graphique.")
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.scatter(self._y_test, self._y_predit, s=10, alpha=0.5, color="#2B2D6E",
                   label="Films de l'ensemble de test")
        bornes = [min(self._y_test.min(), self._y_predit.min()),
                  max(self._y_test.max(), self._y_predit.max())]
        ax.plot(bornes, bornes, color="#E4577F", linewidth=2, label="Prédiction parfaite")
        ax.set_title("Note prédite contre note réelle")
        ax.set_xlabel("Note réelle (sur 10)")
        ax.set_ylabel("Note prédite (sur 10)")
        ax.legend()
        os.makedirs(os.path.dirname(chemin), exist_ok=True)
        fig.savefig(chemin, dpi=120, bbox_inches="tight")
        plt.close(fig)

    def sauvegarder(self, chemin: str) -> None:
        """Enregistre le modèle entraîné avec joblib (pas besoin de ré-entraîner)."""
        os.makedirs(os.path.dirname(chemin), exist_ok=True)
        joblib.dump(self, chemin)

    def __repr__(self) -> str:
        return (f"Modele(forêt aléatoire, {len(self._langues)} langues, "
                f"{len(self._genres)} genres)")


def charger_modele(chemin: str) -> Modele:
    """Charge un modèle sauvegardé. Lève FileNotFoundError si le fichier n'existe pas."""
    if not os.path.exists(chemin):
        raise FileNotFoundError(f"Modèle introuvable : {chemin}. Lancez d'abord src/entrainer.py.")
    return joblib.load(chemin)
