import json
# Pour lire le fichier de métadonnées (format JSON)
import os
# Pour construire le chemin vers ce fichier
import tkinter as tk
# Tkinter : la bibliothèque qui crée la fenêtre ; « tk » est un nom court
from tkinter import messagebox
# messagebox : les petites fenêtres de message (erreurs, informations)
from typing import Callable
# Sert seulement à décrire le type d'une fonction dans les annotations

import icones
# Nos icônes dessinées en pixels, le curseur et les étoiles
import theme
# Nos couleurs, nos polices et nos fonctions qui créent les widgets rétro
from exceptions import DonneeInvalideError
# Notre exception personnalisée, levée quand une saisie est invalide
from variables import (Variable, VariableCategorielle, VariableMultiple,
                       creer_variables)
# Les classes de variables et la fonction qui les construit depuis les métadonnées

COLONNES_GENRES = 3
# Nombre de colonnes pour ranger les cases à cocher des genres (modifiable)


class Application:
    """Fenêtre principale : formulaire, résultat, graphique et historique."""

    def __init__(self, racine: tk.Tk, metadonnees: dict,
                 predire: Callable[[dict], float]) -> None:
        # Le constructeur reçoit la fenêtre, les métadonnées et la fonction de prédiction
        self._racine = racine
        # Garde la fenêtre principale (le _ devant = attribut protégé)
        self._predire = predire
        # Garde la fonction de prédiction : provisoire aujourd'hui, le vrai modèle plus tard
        self._variables = creer_variables(metadonnees)
        # Crée les cinq variables (budget, durée, année, langue, genres) depuis le JSON
        self._champs: dict = {}  # nom de variable -> variable(s) Tkinter
        # Dictionnaire qui retient, pour chaque variable, l'objet Tkinter qui contient sa saisie
        self._texte_resultat = tk.StringVar(value="Note estimée : —")
        # Le texte du résultat : quand on le change avec .set(), l'écran se met à jour tout seul

        racine.title("Estimateur de note de film")
        # Le titre dans la barre de la vraie fenêtre
        theme.appliquer_theme(racine)
        # Applique le fond pêche et le style des listes déroulantes
        icones.appliquer_curseur(racine)
        # Met le curseur de souris rétro (sans effet si ça ne marche pas)
        self._creer_images()
        # Dessine toutes les icônes (il faut le faire après la création de la fenêtre)
        racine.columnconfigure(1, weight=1)
        racine.columnconfigure(2, weight=1)
        # Les colonnes du milieu et de droite s'agrandissent quand on agrandit la fenêtre
        self._construire_titre()
        self._construire_formulaire()
        self._construire_centre()
        self._construire_graphique()
        self._construire_historique()
        # Construit chaque zone de la maquette : titre, formulaire, résultat, graphique, historique

    def _creer_images(self) -> None:
        """Dessine les icônes (il faut les garder dans des attributs, sinon Tkinter les efface)."""
        # Chaque image est rangée dans self._img_... : si on la gardait seulement dans une
        # variable locale, Python la jetterait à la fin de la méthode et elle disparaîtrait
        self._img_coeur = icones.creer_icone("coeur")
        self._img_etoile = icones.creer_icone("etoile")
        self._img_sourire = icones.creer_icone("sourire")
        self._img_dossier = icones.creer_icone("dossier")
        self._img_etoile_vide = icones.creer_icone("etoile", remplacements={"j": theme.BLANC})
        # Une étoile « vide » : la même étoile, mais avec du blanc à la place du jaune
        self._img_bulle = icones.creer_icone("bulle")
        self._img_disque = icones.creer_icone("disque")
        self._img_lecture = icones.creer_icone("lecture")
        self._img_pause = icones.creer_icone("pause")
        self._img_enregistrer = icones.creer_icone("enregistrer")

    def _construire_titre(self) -> None:
        """Titre entouré de deux décorations : une bulle à gauche, un disque à droite."""
        cadre = tk.Frame(self._racine, bg=theme.FOND)
        # Un cadre invisible qui range les trois éléments du titre côte à côte
        cadre.grid(row=0, column=0, columnspan=3, pady=(14, 6))
        # Ligne 0 de la grille (tout en haut), étalé sur les trois colonnes
        tk.Label(cadre, image=self._img_bulle, bg=theme.FOND).pack(side="left", padx=14)
        # La bulle à gauche ; padx = espace de chaque côté
        tk.Label(cadre, text="Estimateur de note de film", bg=theme.FOND,
                 fg=theme.NOIR, font=theme.POLICE_TITRE).pack(side="left")
        # Le texte du titre au milieu
        tk.Label(cadre, image=self._img_disque, bg=theme.FOND).pack(side="left", padx=14)
        # Le disque à droite du texte

    def _construire_formulaire(self) -> None:
        conteneur, corps = theme.creer_fenetre(
            self._racine, "Caractéristiques du film", theme.BARRE, self._img_coeur)
        # Crée la fausse fenêtre : on récupère le conteneur (à placer) et le corps (à remplir)
        conteneur.grid(row=1, column=0, sticky="n", padx=14, pady=10)
        # La place à gauche (colonne 0, ligne 1), collée en haut (« n » = nord)
        for ligne, variable in enumerate(self._variables):
            # Pour chaque variable, avec son numéro de ligne (0, 1, 2...)
            theme.creer_etiquette(corps, variable.libelle).grid(
                row=ligne, column=0, sticky="nw", pady=5)
            # Écrit son libellé à gauche (par exemple « Budget ($) »)
            self._champs[variable.nom] = self._creer_champ(corps, variable, ligne)
            # Crée le champ adapté à droite et mémorise sa saisie sous le nom de la variable

    def _creer_champ(self, parent: tk.Misc, variable: Variable, ligne: int):
        """Crée le widget adapté au type de la variable."""
        if isinstance(variable, VariableMultiple):  # avant Categorielle : c'est son enfant
            # Cas 1 : plusieurs choix possibles -> des cases à cocher
            # (à tester en premier, car une VariableMultiple est aussi une VariableCategorielle)
            cadre = tk.Frame(parent, bg=parent.cget("bg"))
            cadre.grid(row=ligne, column=1, sticky="w", padx=(12, 0))
            # Un petit cadre qui contiendra toutes les cases
            cases = {}
            # Dictionnaire : nom du genre -> case (cochée ou non)
            for i, valeur in enumerate(variable.valeurs):
                # Pour chaque genre, avec son numéro i
                cases[valeur] = tk.BooleanVar()
                # Une variable vrai/faux qui suit l'état de la case
                theme.creer_case(cadre, valeur, cases[valeur]).grid(
                    row=i // COLONNES_GENRES, column=i % COLONNES_GENRES, sticky="w", padx=4)
                # Crée la case et la range en grille : « // » donne la ligne, « % » la colonne
            return cases
            # Renvoie le dictionnaire pour pouvoir lire les cases plus tard
        if isinstance(variable, VariableCategorielle):
            # Cas 2 : un seul choix parmi une liste -> liste déroulante
            saisie = tk.StringVar()
            # Une variable texte qui suivra le choix de l'utilisateur
            theme.creer_liste(parent, saisie, variable.valeurs).grid(
                row=ligne, column=1, sticky="w", padx=(12, 0))
            return saisie
        saisie = tk.StringVar()  # VariableNumerique
        # Cas 3 : un nombre -> une zone de saisie libre
        theme.creer_champ_texte(parent, saisie).grid(
            row=ligne, column=1, sticky="w", padx=(12, 0))
        return saisie

    def _construire_centre(self) -> None:
        """Colonne du milieu : le résultat en haut, le bouton Prédire en dessous."""
        conteneur, corps = theme.creer_fenetre(
            self._racine, "Résultat", theme.BARRE_ALT, self._img_sourire)
        conteneur.grid(row=1, column=1, sticky="n", padx=14, pady=10)
        # Colonne 1 (celle du milieu), collée en haut
        tk.Label(corps, textvariable=self._texte_resultat, bg=theme.BLANC, fg=theme.NOIR,
                 font=("Courier New", 16, "bold"), relief="solid", bd=2,
                 padx=16, pady=12).pack()
        # Le texte de la note, dans un encadré blanc. textvariable = lié à self._texte_resultat :
        # il change quand on fait .set(...)
        self._construire_etoiles(corps)
        # Les cinq étoiles juste en dessous
        theme.creer_bouton(corps, "Prédire", self._on_predire).pack(pady=(14, 4))
        # Le bouton ; la fonction appelée au clic est donnée SANS parenthèses
        self._construire_decor_media(corps)
        # La rangée décorative de ronds, tout en bas

    def _construire_decor_media(self, parent: tk.Misc) -> None:
        """Rangée décorative de trois ronds (lecture, pause, enregistrement)."""
        cadre = tk.Frame(parent, bg=parent.cget("bg"))
        cadre.pack(pady=(14, 0))
        for image in (self._img_lecture, self._img_pause, self._img_enregistrer):
            # Pour chacune des trois images...
            tk.Label(cadre, image=image, bg=parent.cget("bg")).pack(side="left", padx=4)
            # ...un Label qui l'affiche, rangé à gauche du précédent (donc côte à côte)

    def _construire_etoiles(self, parent: tk.Misc) -> None:
        """Rangée de cinq étoiles qui se remplissent selon la note estimée."""
        cadre = tk.Frame(parent, bg=parent.cget("bg"))
        cadre.pack(pady=(12, 0))
        self._etoiles = []
        # La liste des cinq Labels, gardée pour pouvoir changer leur image plus tard
        for _ in range(5):
            # Cinq fois (le « _ » veut dire : on n'a pas besoin du numéro)
            etoile = tk.Label(cadre, image=self._img_etoile_vide, bg=parent.cget("bg"))
            # Une étoile vide au départ
            etoile.pack(side="left", padx=2)
            self._etoiles.append(etoile)

    def _afficher_etoiles(self, note: float) -> None:
        pleines = icones.nombre_etoiles(note)
        # Combien d'étoiles doivent être pleines (par exemple 3 pour une note de 6)
        for i, etoile in enumerate(self._etoiles):
            # Pour chacune des cinq étoiles, avec son numéro i (0 à 4)
            etoile.configure(image=self._img_etoile if i < pleines else self._img_etoile_vide)
            # Pleine si son numéro est plus petit que le nombre d'étoiles pleines, vide sinon

    def _construire_graphique(self) -> None:
        """Colonne de droite : emplacement du graphique (ajouté à l'étape suivante)."""
        conteneur, self._cadre_graphique = theme.creer_fenetre(
            self._racine, "Distribution des notes", theme.BARRE, self._img_etoile)
        # On garde le corps de la fenêtre dans self._cadre_graphique : c'est là que
        # le graphique Matplotlib sera inséré plus tard
        conteneur.grid(row=1, column=2, sticky="nsew", padx=14, pady=10)
        # Colonne 2 (à droite) ; « nsew » = la fenêtre remplit tout l'espace disponible
        theme.creer_etiquette(self._cadre_graphique,
                              "Le graphique apparaîtra ici.").pack(expand=True)
        # Un texte provisoire, qui sera remplacé par le vrai graphique

    def _construire_historique(self) -> None:
        """Bandeau du bas : historique des prédictions (ajouté à l'étape suivante)."""
        conteneur, corps = theme.creer_fenetre(
            self._racine, "Historique des prédictions", theme.BARRE_ALT, self._img_dossier)
        conteneur.grid(row=2, column=0, columnspan=3, sticky="ew", padx=14, pady=(4, 14))
        # Ligne 2 (en bas), sur toute la largeur (3 colonnes)
        theme.creer_bouton(corps, "Afficher", self._on_afficher_historique).pack(side="right")
        # Le bouton « Afficher » à droite
        theme.creer_etiquette(corps, "Tableau des prédictions").pack(side="left")
        # Le texte à gauche

    def _lire_saisies(self) -> dict:
        """Lit et valide tous les champs. Lève DonneeInvalideError au premier problème."""
        valeurs = {}
        # Le dictionnaire des valeurs validées : nom de la variable -> valeur
        for variable in self._variables:
            # Pour chacune des cinq variables
            champ = self._champs[variable.nom]
            # Récupère les objets Tkinter de cette variable
            if isinstance(variable, VariableMultiple):
                saisie = [nom for nom, coche in champ.items() if coche.get()]
                # Cases à cocher : la liste des genres dont la case est cochée
            else:
                saisie = champ.get()
                # Autres champs : le texte saisi ou choisi
            valeurs[variable.nom] = variable.valider(saisie)
            # Valide la saisie (lève une exception si elle est invalide) et range la valeur convertie
        return valeurs

    def _on_predire(self) -> None:
        # Appelée quand on clique sur « Prédire »
        try:
            valeurs = self._lire_saisies()
            # Essaie de lire et de valider tous les champs
        except DonneeInvalideError as erreur:
            # Si une saisie est invalide...
            messagebox.showerror("Saisie invalide", str(erreur))
            # ...ouvre une fenêtre d'erreur avec un message clair (jamais de traceback)
            return
            # ...et s'arrête là : pas de prédiction
        note = self._predire(valeurs)
        # Tout est valide : appelle la fonction de prédiction
        self._texte_resultat.set(f"Note estimée : {note:.1f} / 10")
        # Met à jour le texte du résultat, avec une décimale (6.0)
        self._afficher_etoiles(note)
        # Et remplit les étoiles

    def _on_afficher_historique(self) -> None:
        # Appelée quand on clique sur « Afficher » (provisoire, en attendant l'historique)
        messagebox.showinfo("Historique", "L'historique n'est pas encore disponible.")


def predire_provisoire(valeurs: dict) -> float:
    """À remplacer par la vraie prédiction quand le modèle sera prêt."""
    return 6.0
    # Renvoie toujours 6.0, pour pouvoir tester l'interface sans modèle


def lancer_application() -> None:
    """Charge les métadonnées et ouvre la fenêtre."""
    chemin = os.path.join(os.path.dirname(__file__), "..", "modeles", "metadonnees.json")
    # Le chemin du JSON, calculé à partir de l'emplacement de ce fichier (donc ça marche
    # peu importe le dossier d'où on lance le programme)
    with open(chemin, encoding="utf-8") as f:
        metadonnees = json.load(f)
        # Ouvre et lit le fichier de métadonnées ; « with » le referme automatiquement
    racine = tk.Tk()
    # Crée la fenêtre principale (vide pour l'instant)
    Application(racine, metadonnees, predire_provisoire)
    # Construit toute l'interface dedans
    racine.mainloop()
    # Lance la boucle qui garde la fenêtre ouverte et attend les clics