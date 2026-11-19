"""Entraîne le modèle une seule fois et sauvegarde tout ce dont l'interface a besoin.

Lancer depuis la racine du dépôt : python src/entrainer.py
Produit : modeles/modele.joblib, modeles/metadonnees.json et figures/predit_reel.png
"""
import os
# Pour construire les chemins de fichiers

from donnees import (charger_donnees, construire_metadonnees, nettoyer_donnees,
                     sauvegarder_metadonnees)
# fonctions pour lire, nettoyer les données et écrire les métadonnées
from modele import Modele
# la classe qui entraîne, évalue et sauvegarde la forêt aléatoire 

RACINE = os.path.join(os.path.dirname(__file__), "..")
# Le dossier du projet : os.path.dirname(__file__) donne le dossier de ce fichier (src),
# et ".." remonte d'un niveau *DOSSIER PARENT*. 
CHEMIN_CSV = os.path.join(RACINE, "donnees", "movies.csv")
# jeu de données brut
CHEMIN_MODELE = os.path.join(RACINE, "modeles", "modele.joblib")
# Où enregistrer le modèle entraîné (fichier binaire lu par l'interface)
CHEMIN_META = os.path.join(RACINE, "modeles", "metadonnees.json")
# Où enregistrer les métadonnées (bornes, listes de choix, colonnes, métriques)
CHEMIN_GRAPHIQUE = os.path.join(RACINE, "figures", "predit_reel.png")
# Où enregistrer le graphique « prédit contre réel »


def main() -> None:
    """Nettoie les données, entraîne, évalue, puis sauvegarde le modèle et ses métadonnées.

    Ne reçoit rien et ne renvoie rien : affiche les résultats dans le terminal.
    Lève FileNotFoundError si movies.csv est introuvable.
    """
    films = nettoyer_donnees(charger_donnees(CHEMIN_CSV))
    # Lit le CSV, puis garde seulement les films exploitables (3 514 films)
    meta = construire_metadonnees(films)
    # Calcule les bornes des champs numériques et les listes de langues et de genres
    meta["colonnes"] = ["budget", "runtime", "annee", "original_language", "genres"]  # Les noms des colonnes d'entrée (exigé par l'énoncé), dans l'ordre du formulaire

    modele = Modele(meta["langues"], meta["genres"])
    # Crée le modèle avec les mêmes langues et genres que l'interface : une colonne 0/1 pour chacun
    resultats = modele.entrainer(films)
    # Sépare entraînement/test, entraîne la forêt et la référence, puis renvoie les métriques
    # (le décorateur @chronometrer affiche aussi le temps d'entraînement)

    meta.update(resultats)  # la métrique obtenue va aussi dans le JSON (exigé par l'énoncé)
    # update ajoute les clés de « resultats » (rmse_modele, r2_modele...) au dictionnaire « meta »
    sauvegarder_metadonnees(meta, CHEMIN_META)
    # Écrit le JSON que l'interface lit pour construire le formulaire
    modele.sauvegarder(CHEMIN_MODELE)
    # Enregistre le modèle entraîné : l'interface le charge sans ré-entraîner
    modele.tracer_predit_reel(CHEMIN_GRAPHIQUE)
    # Enregistre le graphique qui compare les notes prédites aux vraies notes de l'ensemble de test

    print(f"Films utilisés : {len(films)} "
          f"({resultats['taille_entrainement']} entraînement, {resultats['taille_test']} test)")
    # Affiche combien de films ont servi à l'entraînement (80 %) et au test (20 %)
    print(f"RMSE modèle    : {resultats['rmse_modele']:.3f}   R² : {resultats['r2_modele']:.3f}")
    print(f"RMSE référence : {resultats['rmse_reference']:.3f}   R² : {resultats['r2_reference']:.3f}")
    # Compare le modèle à la référence ; « :.3f » = 3 décimales


if __name__ == "__main__":
    # Vrai seulement quand on lance ce fichier directement (python src/entrainer.py),
    # faux quand un autre fichier l'importe : l'entraînement ne se lance pas par accident
    main()