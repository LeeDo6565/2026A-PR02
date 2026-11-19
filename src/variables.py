# héritage et polymorphisme


from abc import ABC, abstractmethod

from exceptions import DonneeInvalideError

def _fmt(x: float)-> str:
    """Formate une borne pour un message d'erreur.

    Reçoit un nombre. Renvoie « 380000000 » plutôt que « 380000000.0 » ou
    « 3.8e+08 » si le nombre est entier, et garde les décimales sinon
    (« 120.5 »). Lève ValueError si « x » n'est pas convertible en nombre.
    """
    return str(int(x))if float(x).is_integer() else str(x)# Affiche 380000000 plutôt que 3.8e+08.

class Variable(ABC): # classe parente(hérite de ABC)
    """Classe parente abstraite d'une variable d'entrée du modèle.

    Chaque variable a un nom technique (la colonne du jeu de données) et un
    libellé affiché à l'utilisateur. Chaque classe enfant valide la saisie
    à sa façon (polymorphisme).
    """

    def __init__(self,nom: str, libelle: str) -> None:
        self._nom= nom  # Nom technique de la colonne
        self._libelle= libelle # attribut protégé car ils doivent pas être changé en cours de route. ex "budget" doit correspondre exactement à une colonne
        #Texte affiché à l'utilisateur (ex. « Budget ($) ») -> le nom sur l'interface

    @property
    def nom(self) -> str:   # @property permet d'écrire variable.nom (sans parenthèses) et non variable.nom()
        """Nom technique de la colonne (ex. « budget »)."""
        return self._nom

    @property
    def libelle(self) -> str:
        """Texte affiché à l'utilisateur (ex. « Budget ($) »)."""
        return self._libelle

    @abstractmethod #
    def valider(self, saisie: str | list[str]) -> float | str | list[str]:#Méthode abstraite : chaque classe enfant DOIT la redéfinir à sa façon
        """Renvoie la valeur validée, ou lève DonneeInvalideError."""

    def __str__(self) -> str:
        """Renvoie « libellé (nom) », par exemple « Budget ($) (budget) »."""
        return f"{self.libelle} ({self.nom})"  # Exemple : « Budget ($) (budget)» combine le libellé et le nom technique



class VariableNumerique(Variable): #Hérite de Variable : elle reprend nom, libelle et __str__, et redéfinit valider
    """Variable numérique saisie dans un champ texte, avec un intervalle permis."""

    def __init__(self, nom : str, libelle:str, minimum: float, maximum: float) -> None:
        super().__init__(nom, libelle) # Appelle le constructeur de la classe parente pour ranger nom et libelle
        self._minimum = minimum
        self._maximum = maximum
        #pour l'intervalle des données permises

    def valider(self, saisie : str) -> float: # on définit valider pour la class VariableNumérique
        """Convertit la saisie en nombre et vérifie qu'elle est dans l'intervalle.

        Reçoit le texte tapé par l'utilisateur (la virgule décimale et les
        espaces autour sont acceptés). Renvoie le nombre (float). Lève
        DonneeInvalideError si la saisie est vide, n'est pas un nombre ou
        est hors de l'intervalle [minimum, maximum].
        """
        texte= str(saisie).strip().replace(",", ".") # Convertit en texte, retire les espaces autour, et accepte la virgule décimale (« 7,5 »)
        if texte=="":
            raise DonneeInvalideError(f"{self._libelle} : le champ est vide") # Champ vide : lève l'exception

        try:
            valeur =float(texte) # Essaie de convertir le texte en nombre

        except ValueError: # Si ce n'est pas un nombre (« abc »), Python lève ValueError
            raise DonneeInvalideError(f"{self._libelle} : « {saisie} » n'est pas un nombre.")


        if not self._minimum <= valeur <= self._maximum:   # Vérifie que la valeur est dans l'intervalle (min ≤ valeur ≤ max)
            raise DonneeInvalideError(f"{self._libelle} : la valeur doit être entre "
                                    f"{_fmt(self._minimum)} et {_fmt(self._maximum)}.") # Hors intervalle : message qui indique les bornes


        return valeur


class VariableCategorielle(Variable):
    """Un choix unique parmi une liste de valeurs."""
    def __init__(self, nom : str, libelle: str, valeurs :list[str]) -> None:
        super().__init__(nom, libelle)
        self._valeurs = list(valeurs)   # garde un copie de la liste des choix possibles

    @property
    def valeurs(self)-> list[str]:
            """Copie de la liste des choix possibles (l'originale ne peut pas être modifiée)."""
            return list(self._valeurs ) #ne renvoie pas la liste d'origine, mais une copie

    def valider(self,saisie: str) -> str:
            """Vérifie que le choix fait partie de la liste.

            Reçoit le choix de la liste déroulante. Renvoie ce choix tel quel.
            Lève DonneeInvalideError si rien n'est choisi ou si la valeur
            n'est pas dans la liste (la casse compte : « FR » ≠ « fr »).
            """
            if saisie not in self._valeurs:
                raise DonneeInvalideError(f"{self._libelle} : choisissez une valeur dans la liste")  # Si le choix n'est pas dans la liste (ou est vide), erreur claire
            return saisie



class VariableMultiple(VariableCategorielle):  # Enfant de VariableCategorielle : même liste de valeurs, mais plusieurs choix possibles
    """Un ou plusieurs choix parmi une liste de valeurs (cases à cocher)."""

    def valider(self,saisie: list[str]) -> list[str]: # Redéfinit valider : ici la saisie est une liste (les cases cochées)
        """Vérifie qu'au moins une case est cochée et que chaque choix est permis.

        Reçoit la liste des valeurs cochées. Renvoie une copie de cette liste.
        Lève DonneeInvalideError si la liste est vide ou contient une valeur
        absente de la liste permise.
        """
        if not saisie:
            raise DonneeInvalideError(f"{self._libelle}: cochez au moins une case.")# liste vide: aucune case cochée

        for valeur in saisie:
            if valeur not in self._valeurs:
                raise DonneeInvalideError(f"{self._libelle}: « {valeur} » est inconnu.") # Vérifie chaque case cochée contre la liste des valeurs permises

        return list(saisie)


def creer_variables(metadonnees: dict) -> list[Variable]:
    """Fonction qui assemble tout : crée les cinq variables du formulaire.

    Reçoit les métadonnées lues dans le JSON. Renvoie la liste des variables,
    dans l'ordre d'affichage du formulaire. Lève KeyError si une clé attendue
    (ex. « budget_min ») manque dans les métadonnées.
    """
    m = metadonnees  # Raccourci pour écrire m[...] au lieu de metadonnees[...]
    return[
        VariableNumerique("budget", "Budget ($)", m["budget_min"], m["budget_max"]),# Une variable numérique dont les bornes viennent du fichier JSON
        VariableNumerique("runtime", "Durée (minutes)", m["runtime_min"], m["runtime_max"]),
        VariableNumerique("annee", "Année de sortie", m["annee_min"], m["annee_max"]),
        VariableCategorielle("original_language", "Langue d'origine", m["langues"]),  # Une liste déroulante : un seul choix parmi les langues
        VariableMultiple("genres", "Genres", m["genres"]),# Des cases à cocher : plusieurs choix parmi les genres

    ]
