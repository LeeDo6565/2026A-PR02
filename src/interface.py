import json
import os
import tkinter as tk
from tkinter import messagebox
from typing import Callable

import icones
import theme
from exceptions import DonneeInvalideError
from variables import (Variable, VariableCategorielle, VariableMultiple,
                       creer_variables)

COLONNES_GENRES = 3


class Application:
    """Fenêtre principale : formulaire, résultat, graphique et historique."""

    def __init__(self, racine: tk.Tk, metadonnees: dict,
                 predire: Callable[[dict], float]) -> None:
        self._racine = racine
        self._predire = predire
        self._variables = creer_variables(metadonnees)
        self._champs: dict = {}  # nom de variable -> variable(s) Tkinter
        self._texte_resultat = tk.StringVar(value="Note estimée : —")

        racine.title("Estimateur de note de film")
        theme.appliquer_theme(racine)
        icones.appliquer_curseur(racine)
        self._creer_images()
        racine.columnconfigure(1, weight=1)
        racine.columnconfigure(2, weight=1)
        self._construire_titre()
        self._construire_formulaire()
        self._construire_centre()
        self._construire_graphique()
        self._construire_historique()

    def _creer_images(self) -> None:
        """Dessine les icônes (il faut les garder dans des attributs, sinon Tkinter les efface)."""
        self._img_coeur = icones.creer_icone("coeur")
        self._img_etoile = icones.creer_icone("etoile")
        self._img_sourire = icones.creer_icone("sourire")
        self._img_dossier = icones.creer_icone("dossier")
        self._img_etoile_vide = icones.creer_icone("etoile", remplacements={"j": theme.BLANC})

    def _construire_titre(self) -> None:
        tk.Label(self._racine, text="Estimateur de note de film", bg=theme.FOND,
                 fg=theme.BLANC, font=theme.POLICE_TITRE).grid(
                     row=0, column=0, columnspan=3, pady=(14, 6))

    def _construire_formulaire(self) -> None:
        conteneur, corps = theme.creer_fenetre(
            self._racine, "Caractéristiques du film", theme.BARRE, self._img_coeur)
        conteneur.grid(row=1, column=0, sticky="n", padx=14, pady=10)
        for ligne, variable in enumerate(self._variables):
            theme.creer_etiquette(corps, variable.libelle).grid(
                row=ligne, column=0, sticky="nw", pady=5)
            self._champs[variable.nom] = self._creer_champ(corps, variable, ligne)

    def _creer_champ(self, parent: tk.Misc, variable: Variable, ligne: int):
        """Crée le widget adapté au type de la variable."""
        if isinstance(variable, VariableMultiple):  # avant Categorielle : c'est son enfant
            cadre = tk.Frame(parent, bg=parent.cget("bg"))
            cadre.grid(row=ligne, column=1, sticky="w", padx=(12, 0))
            cases = {}
            for i, valeur in enumerate(variable.valeurs):
                cases[valeur] = tk.BooleanVar()
                theme.creer_case(cadre, valeur, cases[valeur]).grid(
                    row=i // COLONNES_GENRES, column=i % COLONNES_GENRES, sticky="w", padx=4)
            return cases
        if isinstance(variable, VariableCategorielle):
            saisie = tk.StringVar()
            theme.creer_liste(parent, saisie, variable.valeurs).grid(
                row=ligne, column=1, sticky="w", padx=(12, 0))
            return saisie
        saisie = tk.StringVar()  # VariableNumerique
        theme.creer_champ_texte(parent, saisie).grid(
            row=ligne, column=1, sticky="w", padx=(12, 0))
        return saisie

    def _construire_centre(self) -> None:
        """Colonne du milieu : le résultat en haut, le bouton Prédire en dessous."""
        conteneur, corps = theme.creer_fenetre(
            self._racine, "Résultat", theme.BARRE_ALT, self._img_sourire)
        conteneur.grid(row=1, column=1, sticky="n", padx=14, pady=10)
        tk.Label(corps, textvariable=self._texte_resultat, bg=theme.BLANC, fg=theme.NOIR,
                 font=("Courier New", 16, "bold"), relief="solid", bd=2,
                 padx=16, pady=12).pack()
        self._construire_etoiles(corps)
        theme.creer_bouton(corps, "Prédire", self._on_predire).pack(pady=(14, 4))

    def _construire_etoiles(self, parent: tk.Misc) -> None:
        """Rangée de cinq étoiles qui se remplissent selon la note estimée."""
        cadre = tk.Frame(parent, bg=parent.cget("bg"))
        cadre.pack(pady=(12, 0))
        self._etoiles = []
        for _ in range(5):
            etoile = tk.Label(cadre, image=self._img_etoile_vide, bg=parent.cget("bg"))
            etoile.pack(side="left", padx=2)
            self._etoiles.append(etoile)

    def _afficher_etoiles(self, note: float) -> None:
        pleines = icones.nombre_etoiles(note)
        for i, etoile in enumerate(self._etoiles):
            etoile.configure(image=self._img_etoile if i < pleines else self._img_etoile_vide)

    def _construire_graphique(self) -> None:
        """Colonne de droite : emplacement du graphique (ajouté à l'étape suivante)."""
        conteneur, self._cadre_graphique = theme.creer_fenetre(
            self._racine, "Distribution des notes", theme.BARRE, self._img_etoile)
        conteneur.grid(row=1, column=2, sticky="nsew", padx=14, pady=10)
        theme.creer_etiquette(self._cadre_graphique,
                              "Le graphique apparaîtra ici.").pack(expand=True)

    def _construire_historique(self) -> None:
        """Bandeau du bas : historique des prédictions (ajouté à l'étape suivante)."""
        conteneur, corps = theme.creer_fenetre(
            self._racine, "Historique des prédictions", theme.BARRE_ALT, self._img_dossier)
        conteneur.grid(row=2, column=0, columnspan=3, sticky="ew", padx=14, pady=(4, 14))
        theme.creer_bouton(corps, "Afficher", self._on_afficher_historique).pack(side="right")
        theme.creer_etiquette(corps, "Tableau des prédictions").pack(side="left")

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
        self._afficher_etoiles(note)

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

