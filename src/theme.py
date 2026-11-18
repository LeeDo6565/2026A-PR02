import tkinter as tk # fournit les widget classiques 
#crée les fenêtres, les boutons, les champs...
from tkinter import ttk # fournit les widget thématisés
# variante plus moderne de certains widgets (on s'en sert pour la liste déroulante)
from typing import Callable
# Sert seulement à décrire le type d'une fonction dans les annotations


FOND = "#F8D3B8"         # fond du bureau (pêche)
FENETRE = "#FFF6EA"      # fond des fenêtres (crème)
BARRE = "#F4623A"        # barre de titre (orange-rouge)
BARRE_ALT = "#E4577F"    # barre de titre (variante rose)
ORANGE = "#FFA94D"       # boutons
NOIR = "#2B2D6E"         # contours et texte (bleu nuit, malgré le nom !)
BLANC = "#FFFFFF"
OMBRE_COULEUR = "#E9A98C"  # ombre douce



# Les polices : (nom de la police, taille, style)
POLICE = ("Courier New", 11, "bold")          # texte normal
POLICE_PETITE = ("Courier New", 10, "bold")   # petit texte (cases à cocher, boutons de barre)
POLICE_TITRE = ("Courier New", 24, "bold")    # gros titre
OMBRE = 5                # décalage de l'ombre, en pixels


def appliquer_theme(racine: tk.Tk) -> None: # racine: tk.Tk ->  représente la fenêtre principal
    """Règle le fond de la fenêtre et le style des listes déroulantes."""
    racine.configure(bg=FOND)
    # Colore le fond (background) de la fenêtre principale
    style = ttk.Style(racine)
    #Style pour choisir le theme( permet d'utiliser "clam")
    #L'objet qui permet de personnaliser les widgets « ttk », comme les listes déroulantes
    #racine dans les parenthèse indique à Tkinter qquelle fenêtre à utiliser
    
    style.theme_use("clam")
    # Le thème « clam » accepte les couleurs personnalisées (celui de Windows les ignore)
    
    style.configure("Retro.TCombobox", fieldbackground=BLANC, background=ORANGE,
                    foreground=NOIR, bordercolor=NOIR, arrowcolor=NOIR,
                    lightcolor=NOIR, darkcolor=NOIR, padding=4)
    # Crée un style nommé « Retro.TCombobox » : fond blanc, bouton orange, contours bleu nuit
    style.map("Retro.TCombobox", fieldbackground=[("readonly", BLANC)],
              selectbackground=[("readonly", BLANC)],
              selectforeground=[("readonly", NOIR)])
    # Garde le fond blanc et le texte bleu nuit même quand la liste est en lecture seule
    racine.option_add("*TCombobox*Listbox.font", POLICE)
    racine.option_add("*TCombobox*Listbox.background", BLANC)
    racine.option_add("*TCombobox*Listbox.selectBackground", BARRE)
    racine.option_add("*TCombobox*Listbox.selectForeground", BLANC)
    # Style du menu qui s'ouvre quand on clique sur la liste : police, fond, et couleur
    # de l'élément survolé (orange-rouge avec du texte blanc)


def creer_fenetre(parent: tk.Misc, titre: str, couleur: str = BARRE,
                  icone: tk.PhotoImage | None = None) -> tuple[tk.Frame, tk.Frame]:
    """Crée une fausse fenêtre rétro (barre de titre, contour, ombre douce décalée).

    Renvoie (conteneur, corps) : on place le conteneur dans la grille,
    et on met les widgets dans le corps. « icone » s'affiche avant le titre.
    """
    conteneur = tk.Frame(parent, bg=parent.cget("bg"))
    # Un cadre invisible (même couleur que le parent) qui contiendra la fenêtre ET son ombre
    ombre = tk.Frame(conteneur, bg=OMBRE_COULEUR)
    ombre.place(x=OMBRE, y=OMBRE, relwidth=1, relheight=1)  # décalée vers le bas et la droite
    # Un rectangle de la couleur de l'ombre, aussi grand que le conteneur, mais décalé de 5 pixels
    fenetre = tk.Frame(conteneur, bg=FENETRE, highlightbackground=NOIR, highlightthickness=2)
    # La vraie fenêtre : fond crème, avec un contour bleu nuit de 2 pixels
    fenetre.pack(fill="both", expand=True, padx=(0, OMBRE), pady=(0, OMBRE))
    # Elle est créée après l'ombre, donc affichée par-dessus. La marge à droite et en bas
    # laisse dépasser l'ombre : c'est ce qui donne l'effet « ombre décalée »

    barre = tk.Frame(fenetre, bg=couleur)
    barre.pack(fill="x")
    # La barre de titre colorée, sur toute la largeur de la fenêtre
    if icone is not None:
        # Si on a donné une icône...
        etiquette_icone = tk.Label(barre, image=icone, bg=couleur)
        # ...on l'affiche dans un Label (un Label peut montrer du texte OU une image)
        etiquette_icone.image = icone  # garde une référence, sinon l'image disparaît
        # Astuce de Tkinter : sans cette ligne, Python « oublie » l'image et le Label devient vide
        etiquette_icone.pack(side="left", padx=(8, 0), pady=2)
    tk.Label(barre, text=titre, bg=couleur, fg=BLANC, font=POLICE).pack(side="left", padx=8, pady=3)
    # Le titre de la fenêtre, en blanc, à gauche (après l'icône s'il y en a une)
    for symbole in ("x", "o", "_"):  # décoratif : imite les boutons d'une vieille fenêtre
        # Trois petits carrés à droite. On les range de droite à gauche : x, puis o, puis _
        tk.Label(barre, text=symbole, bg=FENETRE, fg=NOIR, font=POLICE_PETITE,
                 width=2, relief="solid", bd=1).pack(side="right", padx=2, pady=3)
        # Ils ne font rien : c'est seulement de la décoration

    corps = tk.Frame(fenetre, bg=FENETRE, padx=12, pady=12)
    corps.pack(fill="both", expand=True)
    # La zone sous la barre, où l'on mettra les champs, le texte, etc.
    return conteneur, corps
    # On renvoie les deux : le conteneur pour placer la fenêtre, le corps pour la remplir


def creer_etiquette(parent: tk.Misc, texte: str) -> tk.Label:
    # Un texte simple, avec les couleurs et la police du thème
    return tk.Label(parent, text=texte, bg=parent.cget("bg"), fg=NOIR, font=POLICE)
    # parent.cget("bg") : reprend la couleur de fond du parent pour que ça se fonde dedans


def creer_champ_texte(parent: tk.Misc, variable: tk.StringVar) -> tk.Entry:
    # Une zone où l'utilisateur tape du texte ; variable.get() renverra ce qu'il a tapé
    return tk.Entry(parent, textvariable=variable, font=POLICE, bg=BLANC, fg=NOIR,
                    relief="flat", bd=0, highlightthickness=2, highlightbackground=NOIR,
                    highlightcolor=NOIR, insertbackground=NOIR, width=18)
    # relief="flat" et bd=0 : pas de bordure par défaut ; highlight... : à la place, un
    # contour bleu nuit de 2 pixels ; insertbackground : couleur du curseur de texte ;
    # width=18 : largeur en nombre de caractères


def creer_liste(parent: tk.Misc, variable: tk.StringVar, valeurs: list[str]) -> ttk.Combobox:
    # Une liste déroulante : on choisit une valeur parmi celles proposées
    return ttk.Combobox(parent, textvariable=variable, values=valeurs, state="readonly",
                        style="Retro.TCombobox", font=POLICE, width=16)
    # state="readonly" : on ne peut pas taper autre chose que les valeurs de la liste ;
    # style : le style « Retro.TCombobox » défini plus haut


def creer_case(parent: tk.Misc, texte: str, variable: tk.BooleanVar) -> tk.Checkbutton:
    # Une case à cocher ; variable.get() renverra True (cochée) ou False
    return tk.Checkbutton(parent, text=texte, variable=variable, bg=parent.cget("bg"),
                          fg=NOIR, activebackground=parent.cget("bg"), selectcolor=BLANC,
                          font=POLICE_PETITE, anchor="w")
    # activebackground : fond quand la souris passe dessus (on garde le même, pour ne
    # pas qu'il change de couleur) ; selectcolor : fond du petit carré ; anchor="w" : texte à gauche


def creer_bouton(parent: tk.Misc, texte: str, commande: Callable[[], None],
                 couleur: str = ORANGE) -> tk.Frame:
    """Bouton avec contour et petite ombre. Renvoie le conteneur à placer."""
    conteneur = tk.Frame(parent, bg=parent.cget("bg"))
    # Même principe que pour les fenêtres : un conteneur qui contient le bouton et son ombre
    ombre = tk.Frame(conteneur, bg=OMBRE_COULEUR)
    ombre.place(x=4, y=4, relwidth=1, relheight=1)
    # L'ombre : un rectangle décalé de 4 pixels, placé derrière
    tk.Button(conteneur, text=texte, command=commande, bg=couleur, fg=NOIR,
              activebackground=BLANC, activeforeground=NOIR, font=POLICE,
              relief="flat", bd=0, highlightthickness=2, highlightbackground=NOIR,
              highlightcolor=NOIR, padx=14, pady=4, cursor="hand2").pack(
                  padx=(0, 4), pady=(0, 4))
    # Le bouton : command = la fonction appelée au clic (sans parenthèses !) ;
    # activebackground : couleur quand on appuie ; cursor="hand2" : curseur en main ;
    # padx/pady : espace intérieur ; le .pack(...) laisse dépasser l'ombre à droite et en bas
    return conteneur