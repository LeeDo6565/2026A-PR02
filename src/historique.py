"""Historique des prédictions, enregistré dans un fichier CSV (chapitre 5)."""
import csv
# Le module csv : pour lire et écrire des fichiers CSV correctement (virgules, guillemets...)
import os
# ^pour vérifier si le fichier existe et créer son dossier
from datetime import datetime
# our obtenir la date et l'heure de chaque prédiction

COLONNES = ["date", "budget", "runtime", "annee", "original_language", "genres", "note"]
# l'ordre des colonnes dans le fichier CSV


class Historique:
    """Ajoute chaque prédiction à un fichier CSV et permet de les relire."""

    def __init__(self, chemin: str) -> None:
        self._chemin = chemin  # chemin du fichier CSV 
        # le constructeur ne crée pas encore le fichier. Il sera créé à la première prédiction

    @property
    def chemin(self) -> str:
        """Chemin du fichier CSV (en lecture seule : pas de setter)."""
        return self._chemin

    def ajouter(self, valeurs: dict, note: float) -> dict:
        """Ajoute une prédiction à la fin du fichier et renvoie la ligne écrite.

        « valeurs » contient les saisies validées (genres = liste de genres).
        Crée le fichier (avec sa ligne d'en-tête) et son dossier s'ils
        n'existent pas encore. Lève OSError si le fichier ne peut pas être écrit.
        """
        ligne = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            # date et l'heure actuelles changées en texte : « 2026-11-19 14:21:44 »
            "budget": valeurs["budget"],
            "runtime": valeurs["runtime"],
            "annee": valeurs["annee"],
            "original_language": valeurs["original_language"],
            # Les saisies de l'utilisateur déjà validées par les classes Variable
            "genres": " ; ".join(valeurs["genres"]),  # la liste devient un seul texte
            # ["Action", "Drama"] devient « Action ; Drama » (une case de CSV ne contient qu'un texte)
            "note": round(note, 2),
            # La note prédite, arrondie à 2 décimales
        }
        dossier = os.path.dirname(self._chemin)
        # Le dossier du fichier 
        if dossier:
            os.makedirs(dossier, exist_ok=True)
            # Crée le dossier s'il n'existe pas ; « if dossier » évite une erreur quand le
            # chemin n'a pas de dossier
        nouveau = not os.path.exists(self._chemin)
        # Si le fichier n'existe pas encore, il faudra écrire la ligne d'en-tête
        with open(self._chemin, "a", newline="", encoding="utf-8") as f:
            # « a » = append : on ajoute à la fin sans effacer les anciennes prédictions
            # newline="" : évite les lignes vides en trop sous Windows (recommandé par le module csv)
            ecrivain = csv.DictWriter(f, fieldnames=COLONNES)
            # Un « écrivain » qui transforme un dictionnaire en ligne de CSV, dans l'ordre de COLONNES
            if nouveau:
                ecrivain.writeheader()
                # Écrit la ligne des noms de colonnes, une seule fois (au tout début du fichier)
            ecrivain.writerow(ligne)
            # Écrit la prédiction
        return ligne
        # Renvoie la ligne écrite (utile pour les tests)

    def lire(self) -> list[dict]:
        """Renvoie toutes les prédictions, de la plus récente à la plus ancienne.

        Renvoie une liste vide si le fichier n'existe pas encore.
        La note est convertie en nombre (float). Lève OSError si le fichier
        existe mais ne peut pas être lu, et ValueError si une note n'est pas un nombre.
        """
        if not os.path.exists(self._chemin):
            return []
            # Aucune prédiction encore : pas d'erreur, simplement une liste vide
        with open(self._chemin, newline="", encoding="utf-8") as f:
            lignes = list(csv.DictReader(f))
            # DictReader lit chaque ligne comme un dictionnaire {nom de colonne: valeur} ;
            # list(...) les rassemble toutes avant que « with » referme le fichier
        for ligne in lignes:
            ligne["note"] = float(ligne["note"])
            # Dans un CSV, tout est du texte : on reconvertit la note en nombre
        return sorted(lignes, key=lambda ligne: ligne["date"], reverse=True)
        # lambda (chapitre 7) : la clé de tri est la date ; reverse=True = la plus récente d'abord
        # (le format « AAAA-MM-JJ HH:MM:SS » se trie correctement comme du texte)

    def __len__(self) -> int:
        """Nombre de prédictions enregistrées (permet d'écrire len(historique))."""
        return len(self.lire())
        # Méthode spéciale : Python l'appelle quand on écrit len(historique)



