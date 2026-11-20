"""Historique des prédictions, enregistré dans un fichier CSV (chapitre 5)."""
import csv
import os
from datetime import datetime

COLONNES = ["date", "budget", "runtime", "annee", "original_language", "genres", "note"]
# L'ordre des colonnes dans le fichier CSV


class Historique:
    """Ajoute chaque prédiction à un fichier CSV et permet de les relire."""

    def __init__(self, chemin: str) -> None:
        self._chemin = chemin  # chemin du fichier CSV (attribut protégé)

    @property
    def chemin(self) -> str:
        return self._chemin

    def ajouter(self, valeurs: dict, note: float) -> dict:
        """Ajoute une prédiction à la fin du fichier et renvoie la ligne écrite.

        « valeurs » contient les saisies validées (genres = liste de genres).
        Crée le fichier (avec sa ligne d'en-tête) et son dossier s'ils
        n'existent pas encore. Lève OSError si le fichier ne peut pas être écrit.
        """
        ligne = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), #transforme en annnée-mois-jour-heures heures:minutes:secondes 
            "budget": valeurs["budget"],
            "runtime": valeurs["runtime"],
            "annee": valeurs["annee"],
            "original_language": valeurs["original_language"],
            "genres": " ; ".join(valeurs["genres"]),  # la liste devient un seul texte
            "note": round(note, 2),
        }
        dossier = os.path.dirname(self._chemin)
        if dossier:
            os.makedirs(dossier, exist_ok=True)
        nouveau = not os.path.exists(self._chemin)
        # Si le fichier n'existe pas encore, il faudra écrire la ligne d'en-tête
        with open(self._chemin, "a", newline="", encoding="utf-8") as f:
            # « a » = append : on ajoute à la fin sans effacer les anciennes prédictions
            ecrivain = csv.DictWriter(f, fieldnames=COLONNES)
            if nouveau:
                ecrivain.writeheader()
            ecrivain.writerow(ligne)
        return ligne

    def lire(self) -> list[dict]:
        """Renvoie toutes les prédictions, de la plus récente à la plus ancienne.

        Renvoie une liste vide si le fichier n'existe pas encore.
        La note est convertie en nombre (float).
        """
        if not os.path.exists(self._chemin):
            return []
        with open(self._chemin, newline="", encoding="utf-8") as f:
            lignes = list(csv.DictReader(f)) # lit le fichier comme un dictionnaire 
        for ligne in lignes:
            ligne["note"] = float(ligne["note"]) # convertit chaque note en décimal 
        return sorted(lignes, key=lambda ligne: ligne["date"], reverse=True)
        # lambda (chapitre 7) : la clé de tri est la date ; reverse=True = la plus récente d'abord

    def __len__(self) -> int:
        """Nombre de prédictions enregistrées (permet d'écrire len(historique))."""
        return len(self.lire())
