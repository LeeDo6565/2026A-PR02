import json
import os
import tkinter as tk  #bibliothèque graphique 
from tkinter import messagebox, ttk
from typing import Callable  # sert aux annotations de type 

from exceptions import DonneeInvalideError
from variables import (Variable, VariableCategorielle, VariableMultiple,creer_variables)


COLONNES_GENRES = 3    # Nombre de colonnes pour afficher les cases à cocher des genres (modifiable)                  


class Application:
    """Fenêtre principale : formulaire, résultat, graphique et historique."""

    def __init__(self, racine: tk.Tk, metadonnees: dict,
                 predire: Callable[[dict], float]) -> None: # Constructeur : reçoit la fenêtre, les métadonnées et la fonction de prédiction
        self._racine = racine # Garde la fenêtre principale (attribut protégé)
        self._predire = predire #  Garde la fonction de prédiction : provisoire aujourd'hui, le vrai modèle plus tard
        self._variables = creer_variables(metadonnees) # Crée les cinq variables (budget, durée, année, langue, genres) depuis le JSON
        self._champs: dict = {}  # Dictionnaire : nom de variable -> les objets Tkinter qui contiennent sa saisie
        self._texte_resultat = tk.StringVar(value="Note estimée : —") # Texte du résultat : quand on le change, le label à l'écran se met à jour tout seul

        racine.title("Estimateur de note de film") # Titre dans la barre de la fenêtre
        racine.columnconfigure(1, weight=1)  
        racine.columnconfigure(2, weight=1)
        # Les colonnes du milieu et de droite s'agrandissent avec la fenêtre

        self._construire_titre()
        self._construire_formulaire()
        self._construire_centre()
        self._construire_graphique()
        self._construire_historique()
        # Construit chaque zone de la maquette, l'une après l'autre



    def _construire_titre(self) -> None:
        ttk.Label(self._racine, text="Estimateur de note de film",
                  font=("Arial", 20, "bold")).grid(row=0, column=0, columnspan=3, pady=(12, 4)) # Titre en gros caractères, ligne 0, étalé sur les trois colonnes

    def _construire_formulaire(self) -> None:
        cadre = ttk.LabelFrame(self._racine, text="Caractéristiques du film", padding=10)  # Un cadre avec un titre qui regroupe les champs
        cadre.grid(row=1, column=0, sticky="n", padx=10, pady=10)  # Le place à gauche (colonne 0, ligne 1), collé en haut (« n » = nord)
        for ligne, variable in enumerate(self._variables): # Pour chaque variable, avec son numéro de ligne (0, 1, 2...)
            ttk.Label(cadre, text=variable.libelle).grid(row=ligne, column=0, sticky="nw", pady=4) #Affiche son libellé à gauche (ex. « Budget ($) »)
            self._champs[variable.nom] = self._creer_champ(cadre, variable, ligne) # Crée le champ adapté et mémorise sa saisie sous le nom de la variable

    def _creer_champ(self, parent: ttk.Frame, variable: Variable, ligne: int):
        """Crée le widget adapté au type de la variable."""
        if isinstance(variable, VariableMultiple):  # avant Categorielle : c'est son enfant. En d'autre termes, VariableMultiple est un cas particulier de VariableCategorielle, donc on teste d'abord le cas particulier     
            # Cas 1 : plusieurs choix possibles : on crée un cadre avec plusieurs cases à cocher
            # à tester en premier, car VariableMultiple est aussi une VariableCategorielle 
            cadre = ttk.Frame(parent)
            cadre.grid(row=ligne, column=1, sticky="w", padx=(10, 0))
            #un petit cadre pour contenir les cases à cocher, à droite du libellé(Genres)
            cases = {} #dictionnaire : nom de genre -> case cochée( vrai) ou non (faux)

            for i, valeur in enumerate(variable.valeurs): # pour chque genre avec son numéro i 

                cases[valeur] = tk.BooleanVar()    # une variable vrai/faux qui suit l'état de la case

                ttk.Checkbutton(cadre, text=valeur, variable=cases[valeur]).grid(
                    row=i // COLONNES_GENRES, column=i % COLONNES_GENRES, sticky="w", padx=4)
            return cases
        if isinstance(variable, VariableCategorielle):
            saisie = tk.StringVar()
            ttk.Combobox(parent, textvariable=saisie, values=variable.valeurs,
                         state="readonly").grid(row=ligne, column=1, sticky="w", padx=(10, 0))
            return saisie
        saisie = tk.StringVar()  # VariableNumerique
        ttk.Entry(parent, textvariable=saisie).grid(row=ligne, column=1, sticky="w", padx=(10, 0))
        return saisie

    def _construire_centre(self) -> None:
        """Colonne du milieu : le résultat en haut, le bouton Prédire en dessous."""
        cadre = ttk.Frame(self._racine)
        cadre.grid(row=1, column=1, sticky="n", padx=10, pady=10)
        zone = ttk.LabelFrame(cadre, text="Résultat", padding=20)
        zone.pack(fill="x")
        ttk.Label(zone, textvariable=self._texte_resultat,
                  font=("Arial", 16, "bold")).pack()
        ttk.Button(cadre, text="Prédire", command=self._on_predire).pack(pady=20)

    def _construire_graphique(self) -> None:
        """Colonne de droite : emplacement du graphique (ajouté à l'étape suivante)."""
        self._cadre_graphique = ttk.LabelFrame(
            self._racine, text="Distribution des notes", padding=10)
        self._cadre_graphique.grid(row=1, column=2, sticky="nsew", padx=10, pady=10)
        ttk.Label(self._cadre_graphique,
                  text="Le graphique apparaîtra ici.").pack(expand=True)

    def _construire_historique(self) -> None:
        """Bandeau du bas : historique des prédictions (ajouté à l'étape suivante)."""
        cadre = ttk.LabelFrame(self._racine, text="Historique des prédictions", padding=10)
        cadre.grid(row=2, column=0, columnspan=3, sticky="ew", padx=10, pady=(0, 10))
        ttk.Button(cadre, text="Afficher",
                   command=self._on_afficher_historique).pack(side="right")
        ttk.Label(cadre, text="Tableau des prédictions").pack(side="left")

    def _lire_saisies(self) -> dict:
        """Lit et valide tous les champs. Lève DonneeInvalideError au premier problème."""
        valeurs = {}
        for variable in self._variables:
            champ = self._champs[variable.nom]
            if isinstance(variable, VariableMultiple):
                saisie = [nom for nom, coche in champ.items() if coche.get()]
            else:
                saisie = champ.get()
            valeurs[variable.nom] = variable.valider(saisie)
        return valeurs

    def _on_predire(self) -> None:
        try:
            valeurs = self._lire_saisies()
        except DonneeInvalideError as erreur:
            messagebox.showerror("Saisie invalide", str(erreur))
            return
        note = self._predire(valeurs)
        self._texte_resultat.set(f"Note estimée : {note:.1f} / 10")

    def _on_afficher_historique(self) -> None:
        messagebox.showinfo("Historique", "L'historique n'est pas encore disponible.")


def predire_provisoire(valeurs: dict) -> float:
    """À remplacer par la vraie prédiction quand le modèle sera prêt."""
    return 6.0


def lancer_application() -> None:
    """Charge les métadonnées et ouvre la fenêtre."""
    chemin = os.path.join(os.path.dirname(__file__), "..", "modeles", "metadonnees.json")
    with open(chemin, encoding="utf-8") as f:
        metadonnees = json.load(f)
    racine = tk.Tk()
    Application(racine, metadonnees, predire_provisoire)
    racine.mainloop()

