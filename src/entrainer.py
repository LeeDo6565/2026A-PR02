"""Entraîne le modèle une seule fois et sauvegarde tout ce dont l'interface a besoin.

Lancer depuis la racine du dépôt : python src/entrainer.py
Produit : modeles/modele.joblib, modeles/metadonnees.json et figures/predit_reel.png
"""
import os

from donnees import (charger_donnees, construire_metadonnees, nettoyer_donnees,
                     sauvegarder_metadonnees)
from modele import Modele

RACINE = os.path.join(os.path.dirname(__file__), "..")
CHEMIN_CSV = os.path.join(RACINE, "donnees", "movies.csv")
CHEMIN_MODELE = os.path.join(RACINE, "modeles", "modele.joblib")
CHEMIN_META = os.path.join(RACINE, "modeles", "metadonnees.json")
CHEMIN_GRAPHIQUE = os.path.join(RACINE, "figures", "predit_reel.png")


def main() -> None:
    """Nettoie les données, entraîne, évalue, puis sauvegarde le modèle et ses métadonnées."""
    films = nettoyer_donnees(charger_donnees(CHEMIN_CSV))
    meta = construire_metadonnees(films)

    modele = Modele(meta["langues"], meta["genres"])
    resultats = modele.entrainer(films)

    meta.update(resultats)  # la métrique obtenue va aussi dans le JSON (exigé par l'énoncé)
    sauvegarder_metadonnees(meta, CHEMIN_META)
    modele.sauvegarder(CHEMIN_MODELE)
    modele.tracer_predit_reel(CHEMIN_GRAPHIQUE)

    print(f"Films utilisés : {len(films)} "
          f"({resultats['taille_entrainement']} entraînement, {resultats['taille_test']} test)")
    print(f"RMSE modèle    : {resultats['rmse_modele']:.3f}   R² : {resultats['r2_modele']:.3f}")
    print(f"RMSE référence : {resultats['rmse_reference']:.3f}   R² : {resultats['r2_reference']:.3f}")


if __name__ == "__main__":
    main()
