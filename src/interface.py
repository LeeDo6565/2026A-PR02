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

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# Le « pont » entre Matplotlib et Tkinter : il affiche une figure dans une fenêtre Tkinter
from matplotlib.figure import Figure
# Une figure Matplotlib (on n'utilise pas pyplot dans une interface Tkinter)

import icones
# Nos icônes dessinées en pixels, le curseur et les étoiles
import theme
# Nos couleurs, nos polices et nos fonctions qui créent les widgets rétro
from exceptions import DonneeInvalideError
# Notre exception personnalisée, levée quand une saisie est invalide
from historique import Historique
# L'historique des prédictions (fichier CSV)
from modele import charger_modele
# Charge le modèle entraîné (modele.joblib)
from variables import (Variable, VariableCategorielle, VariableMultiple,
                       creer_variables)
# Les classes de variables et la fonction qui les construit depuis les métadonnées

COLONNES_GENRES = 3
# Nombre de colonnes pour ranger les cases à cocher des genres (modifiable)
RACINE_PROJET = os.path.join(os.path.dirname(__file__), "..")
CHEMIN_META = os.path.join(RACINE_PROJET, "modeles", "metadonnees.json")
CHEMIN_MODELE = os.path.join(RACINE_PROJET, "modeles", "modele.joblib")
CHEMIN_HISTORIQUE = os.path.join(RACINE_PROJET, "historique", "predictions.csv")
# Les chemins sont calculés à partir de l'emplacement de ce fichier : ça marche
# peu importe le dossier d'où on lance le programme


class Application:
    """Fenêtre principale : formulaire, résultat, graphique et historique."""

    def __init__(self, racine: tk.Tk, metadonnees: dict, predire: Callable[[dict], float],
                 notes: np.ndarray, historique: Historique) -> None:
        # Le constructeur reçoit la fenêtre, les métadonnées, la fonction de prédiction,
        # les notes d'entraînement (pour le graphique) et l'historique
        self._racine = racine
        # Garde la fenêtre principale (le _ devant = attribut protégé)
        self._predire = predire
        # Garde la fonction de prédiction (la méthode predire du modèle entraîné)
        self._notes = notes
        self._historique = historique
        # Composition : l'application contient l'historique, les variables et utilise le modèle
        self._marge = metadonnees.get("rmse_modele")
        # La RMSE du modèle sert d'indice de confiance : l'erreur habituelle, en points
        self._variables = creer_variables(metadonnees)
        # Crée les cinq variables (budget, durée, année, langue, genres) depuis le JSON
        self._champs: dict = {}  # nom de variable -> variable(s) Tkinter
        # Dictionnaire qui retient, pour chaque variable, l'objet Tkinter qui contient sa saisie
        self._texte_resultat = tk.StringVar(value="Note estimée : —")
        # Le texte du résultat : quand on le change avec .set(), l'écran se met à jour tout seul
        self._texte_explication = tk.StringVar(
            value="Remplissez le formulaire,\npuis cliquez sur « Prédire ».")
        # Une phrase simple sous la note, pour un utilisateur non informaticien

        racine.title("Estimateur de note de film")
        # Le titre dans la barre de la vraie fenêtre
        theme.appliquer_theme(racine)
        # Applique le fond pêche et le style des listes déroulantes
        icones.appliquer_curseur(racine)
        # Met le curseur de souris rétro (sans effet si ça ne marche pas)
        self._creer_images()
        # Dessine toutes les icônes (il faut le faire après la création de la fenêtre)
        racine.columnconfigure(1, weight=0, minsize=340) #La colonne du milieu garde ainsi toujours au moins 340 pixels, et seul le graphique s’adapte quand on change la taille de la fenêtre.
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
                 font=("Courier New", 16, "bold"), wraplength= 300, justify= "center", relief="solid", bd=2,
                 padx=16, pady=12).pack()
        # Le texte de la note, dans un encadré blanc. textvariable = lié à self._texte_resultat :
        # il change quand on fait .set(...)
        tk.Label(corps, textvariable=self._texte_explication, bg=corps.cget("bg"),
                 fg=theme.NOIR, font=theme.POLICE_PETITE, justify="center",
                 wraplength=300).pack(pady=(8, 0))
        # L'explication en mots simples (wraplength : retour à la ligne après 300 pixels)
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
        """Colonne de droite : histogramme des notes, avec la prédiction en surbrillance."""
        conteneur, corps = theme.creer_fenetre(
            self._racine, "Distribution des notes", theme.BARRE, self._img_etoile)
        conteneur.grid(row=1, column=2, sticky="nsew", padx=14, pady=10)
        # Colonne 2 (à droite) ; « nsew » = la fenêtre remplit tout l'espace disponible
        self._figure = Figure(figsize=(4.6, 3.4), dpi=100, facecolor=theme.FENETRE)
        self._axes = self._figure.add_subplot()
        # Une figure Matplotlib avec un seul graphique (les « axes »)
        self._canevas = FigureCanvasTkAgg(self._figure, master=corps)
        self._canevas.get_tk_widget().pack(fill="both", expand=True)
        # Le canevas transforme la figure en widget Tkinter, placé dans la fenêtre rétro
        self._tracer_graphique(None)
        # Premier dessin : la distribution seule, sans prédiction

    def _tracer_graphique(self, note: float | None) -> None:
        """Redessine l'histogramme des notes ; ajoute une ligne pour « note » si elle est donnée."""
        ax = self._axes
        ax.clear()
        # Efface l'ancien dessin avant de redessiner
        ax.hist(self._notes, bins=25, color=theme.ORANGE, edgecolor=theme.NOIR,
                label="Films d'entraînement")
        ax.axvline(float(np.mean(self._notes)), color=theme.NOIR, linestyle="--",
                   linewidth=1.5, label="Moyenne des films")
        if note is not None:
            ax.axvline(note, color=theme.BARRE_ALT, linewidth=3, label="Votre film")
        ax.set_title("Où se situe votre film ?", fontsize=10)
        ax.set_xlabel("Note du public (sur 10)", fontsize=9)
        ax.set_ylabel("Nombre de films", fontsize=9)
        ax.tick_params(labelsize=8)
        ax.set_facecolor(theme.BLANC)
        ax.legend(fontsize=7, loc="upper left")
        self._figure.tight_layout()
        self._canevas.draw()
        # Demande à Tkinter de réafficher la figure

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
        # Tout est valide : appelle le modèle
        self._texte_resultat.set(f"Note estimée : {note:.1f} / 10")
        # Met à jour le texte du résultat, avec une décimale (6.4)
        self._texte_explication.set(self._expliquer(note))
        self._afficher_etoiles(note)
        self._tracer_graphique(note)
        # Remplit les étoiles et place le film sur le graphique
        try:
            self._historique.ajouter(valeurs, note)
        except OSError as erreur:
            # Le fichier n'a pas pu être écrit (dossier protégé, fichier ouvert dans Excel...)
            messagebox.showwarning("Historique", f"La prédiction n'a pas pu être enregistrée :\n{erreur}")

    def _expliquer(self, note: float) -> str:
        """Phrase en mots simples qui accompagne la note (avec l'indice de confiance)."""
        moyenne = float(np.mean(self._notes))
        if note >= moyenne + 0.3:
            position = "au-dessus de la moyenne des films"
        elif note <= moyenne - 0.3:
            position = "sous la moyenne des films"
        else:
            position = "proche de la moyenne des films"
        phrase = f"Le public donnerait environ {note:.1f}/10 à ce film, {position} ({moyenne:.1f})."
        if self._marge is not None:
            phrase += (f"\nEn moyenne, l'estimation se trompe d'environ ± {self._marge:.1f} point.")
        return phrase

    def _on_afficher_historique(self) -> None:
        """Ouvre une petite fenêtre qui liste les prédictions, la plus récente en premier."""
        lignes = self._historique.lire()
        if not lignes:
            messagebox.showinfo("Historique", "Aucune prédiction pour l'instant.")
            return
        fenetre = tk.Toplevel(self._racine)
        # Toplevel : une deuxième fenêtre, qui dépend de la fenêtre principale
        fenetre.title("Historique des prédictions")
        fenetre.configure(bg=theme.FOND)
        texte = tk.Text(fenetre, width=95, height=15, font=theme.POLICE_PETITE,
                        bg=theme.BLANC, fg=theme.NOIR, relief="solid", bd=2)
        texte.pack(padx=12, pady=12, fill="both", expand=True)
        texte.insert("end", f"{'Date':<20}{'Budget ($)':>14}{'Durée':>8}{'Année':>7}"
                            f"{'Langue':>8}  {'Note':>5}  Genres\n")
        # Ligne d'en-tête : « :<20 » aligne à gauche sur 20 caractères, « :>14 » à droite sur 14
        for ligne in lignes:
            texte.insert("end", f"{ligne['date']:<20}{float(ligne['budget']):>14,.0f}"
                                f"{float(ligne['runtime']):>8.0f}{float(ligne['annee']):>7.0f}"
                                f"{ligne['original_language']:>8}  {ligne['note']:>5.1f}  "
                                f"{ligne['genres']}\n")
        texte.configure(state="disabled")
        # Lecture seule : l'utilisateur ne peut pas modifier l'historique affiché


def _verifier_fichiers(*chemins: str) -> str | None:
    """Renvoie un message d'erreur si un des fichiers n'existe pas, sinon None."""
    manquants = [os.path.basename(c) for c in chemins if not os.path.exists(c)]
    if manquants:
        return (f"Fichier(s) introuvable(s) : {', '.join(manquants)}.\n"
                "Lancez d'abord : python src/entrainer.py")
    return None


def lancer_application() -> None:
    """Vérifie les fichiers, charge les métadonnées et le modèle, puis ouvre la fenêtre."""
    racine = tk.Tk()
    # Crée la fenêtre principale (vide pour l'instant)
    probleme = _verifier_fichiers(CHEMIN_META, CHEMIN_MODELE)
    if probleme:
        racine.withdraw()  # cache la fenêtre vide, on montre seulement le message
        messagebox.showerror("Démarrage impossible", probleme)
        racine.destroy()
        return
    with open(CHEMIN_META, encoding="utf-8") as f:
        metadonnees = json.load(f)
        # Ouvre et lit le fichier de métadonnées ; « with » le referme automatiquement
    modele = charger_modele(CHEMIN_MODELE)
    # Le modèle déjà entraîné : il n'est pas ré-entraîné à chaque lancement
    Application(racine, metadonnees, modele.predire, modele.notes_entrainement,
                Historique(CHEMIN_HISTORIQUE))
    # Construit toute l'interface ; on donne la méthode predire du modèle (sans parenthèses)
    racine.mainloop()
    # Lance la boucle qui garde la fenêtre ouverte et attend les clics