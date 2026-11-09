import os

from donnees import (charger_donnees, nettoyer_donnees, construire_metadonnees, sauvegarder_metadonnees)

df = nettoyer_donnees(charger_donnees(os.path.join("donnees", "movies.csv")))
meta = construire_metadonnees(df)
sauvegarder_metadonnees(meta, os.path.join("modeles", "metadonnees.json"))
print("Métadonnées enregistrées.")

