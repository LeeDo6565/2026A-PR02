import os
import pandas as pd

chemin = os.path.join("donnees", "movies.csv")

if not os.path.exists(chemin):
    raise FileNotFoundError(f"Fichier introuvable : {chemin}")

df = pd.read_csv(chemin)
