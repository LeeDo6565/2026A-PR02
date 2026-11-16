import tkinter as tk # Tkinter : la bibliothèque qui crée les fenêtres, les boutons, les champs...
from tkinter import ttk # ttk : une variante plus moderne de certains widgets (on s'en sert pour la liste déroulante)
from typing import Callable # Sert seulement à décrire le type d'une fonction dans les annotations

# Palette « vieux système » douce : pêche, crème, barres orange-rouge, contours bleu nuit
FOND = "#F8D3B8"         # fond du bureau (pêche)
FENETRE = "#FFF6EA"      # fond des fenêtres (crème)
BARRE = "#F4623A"        # barre de titre (orange-rouge)
BARRE_ALT = "#E4577F"    # barre de titre (variante rose)
ORANGE = "#FFA94D"       # boutons
NOIR = "#2B2D6E"         # contours et texte (bleu nuit)
BLANC = "#FFFFFF"
OMBRE_COULEUR = "#E9A98C"  # ombre douce

# Les polices(nom de la police, taille, style) : Courier New est une police à chasse fixe (tous les caractères ont la même largeur)
POLICE = ("Courier New", 11, "bold") # taille normal
POLICE_PETITE = ("Courier New", 10, "bold") #petit texte (case à cocher, boutons de barre)
POLICE_TITRE = ("Courier New", 24, "bold")  #gros titre
OMBRE = 5                # décalage de l'ombre, en pixels (pour créer l'illusion)


def appliquer_theme(racine: tk.Tk) -> None:
    """Règle le fond de la fenêtre et le style des listes déroulantes."""
    racine.configure(bg=FOND) # colore le fond de la fenêtre principale (le bureau) en pêche

    style = ttk.Style(racine)  # l'objet qui permet de  personnaliser les widgets ttk (ici la liste déroulante)

    style.theme_use("clam") # le thème «clam» accepte les couleurs personnalisées( celui de Windows ne le fait pas)
    style.configure("Retro.TCombobox", fieldbackground=BLANC, background=ORANGE,
                    foreground=NOIR, bordercolor=NOIR, arrowcolor=NOIR,
                    lightcolor=NOIR, darkcolor=NOIR, padding=4)
    # crée un style nommé «Retro.TCombobox» :fond blanc, bouton orange, contours bleu nuit 
    
    style.map("Retro.TCombobox", fieldbackground=[("readonly", BLANC)],
              selectbackground=[("readonly", BLANC)],
              selectforeground=[("readonly", NOIR)])
    # Garde le fond blanc et le texte bleh nuit même quand la liste est ouverte (sinon le thème clam mettrait un fond bleu et un texte blanc)
    
    racine.option_add("*TCombobox*Listbox.font", POLICE)
    racine.option_add("*TCombobox*Listbox.background", BLANC)
    racine.option_add("*TCombobox*Listbox.selectBackground", BARRE)
    racine.option_add("*TCombobox*Listbox.selectForeground", BLANC)
    # Style du menu qui s'ouvre quand on clique sur la liste : police, fond, et couleur 
    # de l'élément sélectionné (sinon le thème clam mettrait un fond bleu et un texte blanc)


def creer_fenetre(parent: tk.Misc, titre: str, couleur: str = BARRE,
                  icone: tk.PhotoImage | None = None) -> tuple[tk.Frame, tk.Frame]:
    """Crée une fausse fenêtre rétro (barre de titre, contour, ombre douce décalée).

    Renvoie (conteneur, corps) : on place le conteneur dans la grille,
    et on met les widgets dans le corps. « icone » s'affiche avant le titre.
    """
    conteneur = tk.Frame(parent, bg=parent.cget("bg"))
    # Un cadre invisible (même couleur que le parent) qui contiendra la fenêtre ET son ombre

    ombre = tk.Frame(conteneur, bg=OMBRE_COULEUR)
    ombre.place(x=OMBRE, y=OMBRE, relwidth=1, relheight=1)  # décalée vers le bas et la droite(rectangle de la couleur de l'ombre, aussi grande que le conteneur, mais déclalée de 5 pixels vers le bas et la droite)
    fenetre = tk.Frame(conteneur, bg=FENETRE, highlightbackground=NOIR, highlightthickness=2) 
    #la vraie fenêtre : fond crème, contour bleu nuit de 2 pixels

    fenetre.pack(fill="both", expand=True, padx=(0, OMBRE), pady=(0, OMBRE))
     # Elle est créée après l'ombre, donc affichée par-dessus. La marge à droite et en bas
    # laisse dépasser l'ombre : c'est ce qui donne l'effet « ombre décalée »

    barre = tk.Frame(fenetre, bg=couleur)
    barre.pack(fill="x")
    #La barre de titre colorée,sur toute la largeur de la fenêtre (fill="x"). Le reste de la fenêtre est rempli par le corps (voir plus bas)
    if icone is not None: # si on a donné une icone ...
        etiquette_icone = tk.Label(barre, image=icone, bg=couleur) #on l'affiche dans un label (un label peut montrer du texte OU une image)
        etiquette_icone.image = icone  # garde une référence, sinon l'image disparaît
        # Astuce de Tkinter : sans cette ligne, Python oublie l'image et le label devient vide 
        etiquette_icone.pack(side="left", padx=(8, 0), pady=2) 

    tk.Label(barre, text=titre, bg=couleur, fg=BLANC, font=POLICE).pack(side="left", padx=8, pady=3)
    # Le titre de la fenêtre, en blanc, à gauche (après l'icône s'il y en a une)
    
    for symbole in ("x", "o", "_"):  # décoratif : imite les boutons d'une vieille fenêtre
        tk.Label(barre, text=symbole, bg=FENETRE, fg=NOIR, font=POLICE_PETITE,
                 width=2, relief="solid", bd=1).pack(side="right", padx=2, pady=3)

    corps = tk.Frame(fenetre, bg=FENETRE, padx=12, pady=12)
    corps.pack(fill="both", expand=True)
    return conteneur, corps


def creer_etiquette(parent: tk.Misc, texte: str) -> tk.Label:
    return tk.Label(parent, text=texte, bg=parent.cget("bg"), fg=NOIR, font=POLICE)


def creer_champ_texte(parent: tk.Misc, variable: tk.StringVar) -> tk.Entry:
    return tk.Entry(parent, textvariable=variable, font=POLICE, bg=BLANC, fg=NOIR,
                    relief="flat", bd=0, highlightthickness=2, highlightbackground=NOIR,
                    highlightcolor=NOIR, insertbackground=NOIR, width=18)


def creer_liste(parent: tk.Misc, variable: tk.StringVar, valeurs: list[str]) -> ttk.Combobox:
    return ttk.Combobox(parent, textvariable=variable, values=valeurs, state="readonly",
                        style="Retro.TCombobox", font=POLICE, width=16)


def creer_case(parent: tk.Misc, texte: str, variable: tk.BooleanVar) -> tk.Checkbutton:
    return tk.Checkbutton(parent, text=texte, variable=variable, bg=parent.cget("bg"),
                          fg=NOIR, activebackground=parent.cget("bg"), selectcolor=BLANC,
                          font=POLICE_PETITE, anchor="w")


def creer_bouton(parent: tk.Misc, texte: str, commande: Callable[[], None],
                 couleur: str = ORANGE) -> tk.Frame:
    """Bouton avec contour et petite ombre. Renvoie le conteneur à placer."""
    conteneur = tk.Frame(parent, bg=parent.cget("bg"))
    ombre = tk.Frame(conteneur, bg=OMBRE_COULEUR)
    ombre.place(x=4, y=4, relwidth=1, relheight=1)
    tk.Button(conteneur, text=texte, command=commande, bg=couleur, fg=NOIR,
              activebackground=BLANC, activeforeground=NOIR, font=POLICE,
              relief="flat", bd=0, highlightthickness=2, highlightbackground=NOIR,
              highlightcolor=NOIR, padx=14, pady=4, cursor="hand2").pack(
                  padx=(0, 4), pady=(0, 4))
    return conteneur