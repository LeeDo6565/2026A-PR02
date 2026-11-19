"""Préparation des caractéristiques, entraînement, évaluation et sauvegarde du modèle."""
import os
# Pour les chemins et la création des dossiers
import time
# Pour mesurer le temps d'entraînement
from functools import wraps
# Petit outil pour bien écrire un décorateur
from typing import Callable
# Pour annoter « une fonction » comme type

import joblib
# Pour enregistrer le modèle dans un fichier et le recharger plus tard
import matplotlib.pyplot as plt
# Pour le graphique « prédit contre réel »
import numpy as np
# Pour les calculs sur des tableaux sans boucle (la RMSE)
import pandas as pd
# Pour manipuler le tableau des films
from sklearn.dummy import DummyRegressor
# Le modèle « bête » qui prédit toujours la moyenne : c'est notre référence
from sklearn.ensemble import RandomForestRegressor
# Notre vrai modèle : une forêt aléatoire (plein d'arbres de décision dont on fait la moyenne)
from sklearn.metrics import r2_score
# Le R², pour voir quelle part des différences entre les notes le modèle arrive à expliquer
from sklearn.model_selection import train_test_split
# Pour couper les films en deux groupes : entraînement et test

from donnees import extraire_genres
# Pour transformer « Action Drama » en ["Action", "Drama"]

GRAINE = 42  # graine aléatoire fixée : les résultats sont reproductibles
# Avec la même graine, le hasard tombe toujours pareil : mêmes groupes, mêmes résultats
COLONNES_NUMERIQUES = ["budget", "runtime", "annee"]
# Les trois colonnes qui sont déjà des nombres


# --- Outil du chapitre 7 : décorateur -------------------------------------
def chronometrer(fonction: Callable) -> Callable:
    """Décorateur qui affiche le temps d'exécution de la fonction décorée."""
    @wraps(fonction)  # garde le nom et la docstring de la fonction d'origine
    def enveloppe(*args, **kwargs):
        # La fonction qui « emballe » l'originale ; *args et **kwargs reçoivent tous ses arguments
        debut = time.perf_counter()
        # On note l'heure au départ
        resultat = fonction(*args, **kwargs)
        # On appelle la vraie fonction et on garde ce qu'elle renvoie
        print(f"{fonction.__name__} : {time.perf_counter() - debut:.2f} s")
        # On affiche combien de secondes ça a pris
        return resultat
        # Et on renvoie son résultat, comme si de rien n'était
    return enveloppe
    # Le décorateur renvoie la fonction emballée : c'est elle qui sera appelée à la place


# --- Calcul vectorisé (chapitre 12) ----------------------------------------
def rmse(y_reel: np.ndarray, y_predit: np.ndarray) -> float:
    """Renvoie la racine de l'erreur quadratique moyenne, sans boucle Python.

    Reçoit deux tableaux de même taille (notes réelles et notes prédites).
    Lève ValueError si les tableaux sont vides ou de tailles différentes.
    """
    y_reel = np.asarray(y_reel, dtype=float)
    y_predit = np.asarray(y_predit, dtype=float)
    # On s'assure d'avoir des tableaux NumPy de nombres (ça marche aussi si on reçoit des listes)
    if y_reel.shape != y_predit.shape or y_reel.size == 0:
        raise ValueError("Les tableaux doivent être non vides et de même taille.")
        # Impossible de comparer deux tableaux de tailles différentes, ou vides
    return float(np.sqrt(np.mean((y_reel - y_predit) ** 2)))
    # De l'intérieur vers l'extérieur : les erreurs, au carré, leur moyenne, puis la racine.
    # Tout se fait d'un coup sur le tableau entier, sans boucle for


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
    # On part des trois colonnes numériques, converties en nombres à virgule
    for langue in langues:
        x[f"langue_{langue}"] = (df["original_language"] == langue).astype(int)
        # Une colonne par langue : 1 si le film est dans cette langue, 0 sinon
        # (le modèle ne comprend que des nombres, pas le texte « fr »)
    listes = df["genres"].apply(extraire_genres)  # « Action Drama » -> ["Action", "Drama"]
    for genre in genres:
        x[f"genre_{genre}"] = listes.apply(lambda liste: genre in liste).astype(int)
        # Une colonne par genre : 1 si le film a ce genre, 0 sinon (un film peut en avoir plusieurs)
    return x


# --- Classe Modele ----------------------------------------------------------
class Modele:
    """Une forêt aléatoire qui estime la note d'un film, et sa référence (la moyenne)."""

    def __init__(self, langues: list[str], genres: list[str]) -> None:
        self._langues = list(langues)
        self._genres = list(genres)
        # On garde nos propres copies des listes : il faut toujours les mêmes colonnes
        # à l'entraînement et à la prédiction
        self._regresseur = RandomForestRegressor(
            n_estimators=100, min_samples_leaf=5, random_state=GRAINE)
        # min_samples_leaf=5 : chaque feuille contient au moins 5 films (arbres moins détaillés,
        # donc un fichier beaucoup plus léger et moins de surapprentissage)
        self._reference = DummyRegressor(strategy="mean")
        # La référence : elle prédit toujours la note moyenne
        self._notes_entrainement = np.array([])
        self._y_test = np.array([])
        self._y_predit = np.array([])
        self._resultats: dict = {}
        # Tout est vide tant que le modèle n'a pas été entraîné

    @property
    def resultats(self) -> dict:
        """Copie des métriques calculées par entrainer() (vide avant l'entraînement)."""
        return dict(self._resultats)
        # Une copie : modifier ce qu'on reçoit ne change pas les vrais résultats du modèle

    @property
    def notes_entrainement(self) -> np.ndarray:
        """Copie des notes de l'ensemble d'entraînement (pour le graphique de l'interface)."""
        return self._notes_entrainement.copy()

    @chronometrer
    def entrainer(self, df: pd.DataFrame, taille_test: float = 0.2) -> dict:
        """Sépare les données, entraîne le modèle et la référence, puis les évalue.

        Reçoit les films nettoyés (avec la colonne vote_average). L'évaluation
        se fait uniquement sur l'ensemble de test, jamais sur les données qui ont
        servi à l'entraînement. Renvoie les métriques (RMSE et R²) du modèle et
        de la référence.
        """
        x = preparer_caracteristiques(df, self._langues, self._genres)
        # Les caractéristiques : ce que le modèle reçoit en entrée
        y = df["vote_average"].to_numpy(dtype=float)
        # La cible : la note qu'on veut deviner
        x_train, x_test, y_train, y_test = train_test_split(
            x, y, test_size=taille_test, random_state=GRAINE)
        # On coupe au hasard : 80 % des films pour apprendre, 20 % gardés de côté pour tester

        self._regresseur.fit(x_train, y_train)
        self._reference.fit(x_train, y_train)
        # fit = entraîner. Les deux modèles apprennent seulement sur les films d'entraînement
        self._notes_entrainement = y_train
        self._y_test = y_test
        self._y_predit = self._regresseur.predict(x_test)
        y_reference = self._reference.predict(x_test)
        # On fait deviner les notes des films de test, que les modèles n'ont jamais vus

        self._resultats = {
            "rmse_modele": rmse(y_test, self._y_predit),
            "rmse_reference": rmse(y_test, y_reference),
            "r2_modele": float(r2_score(y_test, self._y_predit)),
            "r2_reference": float(r2_score(y_test, y_reference)),
            "taille_entrainement": len(y_train),
            "taille_test": len(y_test),
        }
        # On compare les vraies notes aux notes devinées, pour le modèle et pour la référence
        return self.resultats

    def predire(self, valeurs: dict) -> float:
        """Prédit la note d'un film à partir des valeurs validées par l'interface.

        « valeurs » contient budget, runtime, annee, original_language et
        genres (une liste comme ["Action", "Drama"]). Renvoie une note sur 10.
        """
        ligne = pd.DataFrame([{**valeurs, "genres": " ".join(valeurs["genres"])}])
        # Remet les genres sous forme de texte, comme dans le CSV, pour réutiliser la même préparation
        # (**valeurs recopie tout le dictionnaire ; on remplace juste « genres »)
        x = preparer_caracteristiques(ligne, self._langues, self._genres)
        # Le film devient une ligne de nombres, avec exactement les mêmes colonnes qu'à l'entraînement
        return float(self._regresseur.predict(x)[0])
        # predict renvoie un tableau (une note par film) ; on prend la seule note avec [0]

    def tracer_predit_reel(self, chemin: str) -> None:
        """Enregistre le graphique « prédit contre réel » de l'ensemble de test.

        Lève RuntimeError si le modèle n'a pas encore été entraîné.
        """
        if self._y_test.size == 0:
            raise RuntimeError("Entraînez le modèle avant de tracer ce graphique.")
            # Pas de notes de test = rien à dessiner
        fig, ax = plt.subplots(figsize=(6, 6))
        # Une figure carrée : les deux axes ont la même échelle
        ax.scatter(self._y_test, self._y_predit, s=10, alpha=0.5, color="#2B2D6E",
                   label="Films de l'ensemble de test")
        # Un point par film de test : sa vraie note en x, la note devinée en y
        bornes = [min(self._y_test.min(), self._y_predit.min()),
                  max(self._y_test.max(), self._y_predit.max())]
        ax.plot(bornes, bornes, color="#E4577F", linewidth=2, label="Prédiction parfaite")
        # La diagonale : si le modèle était parfait, tous les points seraient dessus
        ax.set_title("Note prédite contre note réelle")
        ax.set_xlabel("Note réelle (sur 10)")
        ax.set_ylabel("Note prédite (sur 10)")
        ax.legend()
        os.makedirs(os.path.dirname(chemin), exist_ok=True)
        fig.savefig(chemin, dpi=120, bbox_inches="tight")
        plt.close(fig)
        # On crée le dossier si besoin, on enregistre l'image et on ferme la figure

    def sauvegarder(self, chemin: str) -> None:
        """Enregistre le modèle entraîné avec joblib (pas besoin de ré-entraîner)."""
        os.makedirs(os.path.dirname(chemin), exist_ok=True)
        joblib.dump(self, chemin)
        # On enregistre l'objet Modele au complet : la forêt, les listes et les notes

    def __repr__(self) -> str:
        return (f"Modele(forêt aléatoire, {len(self._langues)} langues, "
                f"{len(self._genres)} genres)")
        # Méthode spéciale : ce qui s'affiche quand on fait print(modele)


def charger_modele(chemin: str) -> Modele:
    """Charge un modèle sauvegardé. Lève FileNotFoundError si le fichier n'existe pas."""
    if not os.path.exists(chemin):
        raise FileNotFoundError(f"Modèle introuvable : {chemin}. Lancez d'abord src/entrainer.py.")
        # Message clair qui dit quoi faire, au lieu d'une erreur incompréhensible
    return joblib.load(chemin)
    # Recrée l'objet Modele tel qu'il était au moment de la sauvegarde
