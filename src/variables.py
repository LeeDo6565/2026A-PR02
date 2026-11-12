# héritage et polymorphisme


from abc import ABC, abstractmethod

from exceptions import DonneeInvalideError

def _fmt(x: float)-> str:
    return str(int(x))if float(x).is_integer else str(x)# Affiche 380000000 plutôt que 3.8e+08.

class Variable(ABC):    

    def __init__(self,nom: str, libelle: str):
        self._nom= nom  # Nom technique de la colonne 
        self._libelle= libelle # attribut protégé car ils doivent pas être changé en cours de route. ex "budget" doit correspondre exactement à une colonne 
        #Texte affiché à l'utilisateur (ex. « Budget ($) »)

    @property
    def nom(self):   # @property permet d'écrire variable.nom (sans parenthèses) pour lire l'attribut
        return self.nom

    @property
    def libelle(self):
        return self.libelle 

    @abstractmethod
    def valider(self, saisie):#Méthode abstraite : chaque classe enfant DOIT la redéfinir à sa façon
        """Renvoie la valeur validée, ou lève DonneeInvalideError."""

    def __str__(self):
        return f"{self.libelle} ({self.nom})"  # Exemple : « Budget ($) (budget)



class VariableNumerique(Variable): #Hérite de Variable : elle reprend nom, libelle et __str__
    def __init__(self, nom : str, libelle:str, minimum: float, maximum: float):
        super().__init__(nom, libelle) # Appelle le constructeur de la classe parente pour ranger nom et libelle
        self._minimum = minimum
        self._maximum = maximum

    def valider(self, saisie : str):
        texte= str(saisie).strip().replace(",", ".") # Convertit en texte, retire les espaces autour, et accepte la virgule décimale (« 7,5 »)
        if texte=="":
            raise DonneeInvalideError(f"{self._libelle} : le champ est vide") # Champ vide : lève l'exception

        try: 
            valeur =float(texte) # Essaie de convertir le texte en nombre

        except ValueError: ## Si ce n'est pas un nombre (« abc »), Python lève ValueError
            raise DonneeInvalideError(f"{self._libelle} : « {saisie} » n'est pas un nombre.")


        if not self._minimum <= valeur <= self._maximum:   # Vérifie que la valeur est dans l'intervalle (min ≤ valeur ≤ max)
            raise DonneeInvalideError(f"{self._libelle} : la valeur doit être entre "
                                    f"{_fmt(self._minimum)} et {_fmt(self._maximum)}.") ## Hors intervalle : message qui indique les bornes


        return valeur 


class VariableCategorielle(Variable):
    """Un choix unique parmi une liste de valeurs."""
    def __init__(self, nom : str, libelle: str, valeurs :list[str]):
        super().__init__(nom, libelle)
        self._valeurs = list(valeurs)   # garde un copue de la liste des choix possibles 

        @property
        def valeurs(self)-> list[str]:
            return list(self._valeurs ) #ne renvoie pas la liste d'origine, mais une copie 

        def valider(self,saisie: str):
            if saisie not in self._valeurs:
                raise DonneeInvalideError(f"{self._libelle} : choississez une valeur dans la liste")  # Si le choix n'est pas dans la liste (ou est vide), erreur claire
            return saisie



class VariableMultiple(VariableCategorielle):  # Enfant de VariableCategorielle : même liste de valeurs, mais plusieurs choix possibles
    """Un ou plusieurs choix parmi une liste de valeurs (cases à cocher)."""

    def valider(self,saisie: list[str]): ## Redéfinit valider : ici la saisie est une liste (les cases cochées)
        if not saisie:
            raise DonneeInvalideError(f"{self._libelle}: cochez au moins une case.")# liste vide: aucune case cochée

        for valeur in saisie:
            if valeur not in self._valeurs: 
                raise DonneeInvalideError(f"{self._libelle}: « {valeur} » est inconnu.") # Vérifie chaque case cochée contre la liste des valeurs permises

        return list(saisie)


"""fonction qui assemble tout"""
def creer_variables(metadonnees: dict):
    m = metadonnees  # Raccourci pour écrire m[...] au lieu de metadonnees[...]
    return[
        VariableNumerique("budget", "Budget ($)", m["budget_min"], m["budget_max"]),# Une variable numérique dont les bornes viennent du fichier JSON
        VariableNumerique("runtime", "Durée (minutes)", m["runtime_min"], m["runtime_max"]),
        VariableNumerique("annee", "Année de sortie", m["annee_min"], m["annee_max"]),
        VariableCategorielle("original_language", "Langue d'origine", m["langues"]),  # Une liste déroulante : un seul choix parmi les langues
        VariableMultiple("genres", "Genres", m["genres"]),# Des cases à cocher : plusieurs choix parmi les genres

    ]

