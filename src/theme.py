import tkinter as tk
from tkinter import ttk
from typing import Callable

# Palette « vieux système » douce : pêche, crème, barres orange-rouge, contours bleu nuit
FOND = "#F8D3B8"         # fond du bureau (pêche)
FENETRE = "#FFF6EA"      # fond des fenêtres (crème)
BARRE = "#F4623A"        # barre de titre (orange-rouge)
BARRE_ALT = "#E4577F"    # barre de titre (variante rose)
ORANGE = "#FFA94D"       # boutons
NOIR = "#2B2D6E"         # contours et texte (bleu nuit)
BLANC = "#FFFFFF"
OMBRE_COULEUR = "#E9A98C"  # ombre douce

POLICE = ("Courier New", 11, "bold")
POLICE_PETITE = ("Courier New", 10, "bold")
POLICE_TITRE = ("Courier New", 24, "bold")
OMBRE = 5                # décalage de l'ombre, en pixels


def appliquer_theme(racine: tk.Tk) -> None:
    """Règle le fond de la fenêtre et le style des listes déroulantes."""
    racine.configure(bg=FOND)
    style = ttk.Style(racine)
    style.theme_use("clam")
    style.configure("Retro.TCombobox", fieldbackground=BLANC, background=ORANGE,
                    foreground=NOIR, bordercolor=NOIR, arrowcolor=NOIR,
                    lightcolor=NOIR, darkcolor=NOIR, padding=4)
    style.map("Retro.TCombobox", fieldbackground=[("readonly", BLANC)],
              selectbackground=[("readonly", BLANC)],
              selectforeground=[("readonly", NOIR)])
    racine.option_add("*TCombobox*Listbox.font", POLICE)
    racine.option_add("*TCombobox*Listbox.background", BLANC)
    racine.option_add("*TCombobox*Listbox.selectBackground", BARRE)
    racine.option_add("*TCombobox*Listbox.selectForeground", BLANC)


def creer_fenetre(parent: tk.Misc, titre: str, couleur: str = BARRE,
                  icone: tk.PhotoImage | None = None) -> tuple[tk.Frame, tk.Frame]:
    """Crée une fausse fenêtre rétro (barre de titre, contour, ombre douce décalée).

    Renvoie (conteneur, corps) : on place le conteneur dans la grille,
    et on met les widgets dans le corps. « icone » s'affiche avant le titre.
    """
    conteneur = tk.Frame(parent, bg=parent.cget("bg"))
    ombre = tk.Frame(conteneur, bg=OMBRE_COULEUR)
    ombre.place(x=OMBRE, y=OMBRE, relwidth=1, relheight=1)  # décalée vers le bas et la droite
    fenetre = tk.Frame(conteneur, bg=FENETRE, highlightbackground=NOIR, highlightthickness=2)
    fenetre.pack(fill="both", expand=True, padx=(0, OMBRE), pady=(0, OMBRE))

    barre = tk.Frame(fenetre, bg=couleur)
    barre.pack(fill="x")
    if icone is not None:
        etiquette_icone = tk.Label(barre, image=icone, bg=couleur)
        etiquette_icone.image = icone  # garde une référence, sinon l'image disparaît
        etiquette_icone.pack(side="left", padx=(8, 0), pady=2)
    tk.Label(barre, text=titre, bg=couleur, fg=BLANC, font=POLICE).pack(side="left", padx=8, pady=3)
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