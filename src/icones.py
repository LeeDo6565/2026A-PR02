import os
import struct
import tempfile
import tkinter as tk

import theme

# Chaque icône est un petit dessin en « pixels » : une lettre = une couleur, « . » = transparent
PALETTE = {"#": theme.NOIR, "r": "#F58FA8", "j": "#FFC93C",
           "o": theme.ORANGE, "b": theme.BLANC, "v": theme.BARRE_ALT}
MOTIFS = {
    "coeur": [
        "..###.###..",
        ".#rrr#rrr#.",
        "#rrbrrrrrr#",
        "#rbrrrrrrr#",
        "#rrrrrrrrr#",
        ".#rrrrrrr#.",
        "..#rrrrr#..",
        "...#rrr#...",
        "....#r#....",
        ".....#.....",
    ],
    "etoile": [
        ".....#.....",
        "....#j#....",
        "....#j#....",
        "...#jjj#...",
        "###jjjjj###",
        "#jjjjjjjjj#",
        ".#jjjjjjj#.",
        "..#jjjjj#..",
        "..#jjjjj#..",
        ".#jjj#jjj#.",
        ".#jj#.#jj#.",
        "..##...##..",
    ],
    "sourire": [
        "...#####...",
        "..#jjjjj#..",
        ".#jjjjjjj#.",
        "#jj#jjj#jj#",
        "#jj#jjj#jj#",
        "#jjjjjjjjj#",
        "#j#jjjjj#j#",
        "#jj#####jj#",
        ".#jjjjjjj#.",
        "..#jjjjj#..",
        "...#####...",
    ],
    "dossier": [
        ".#####......",
        "#ooooo######",
        "#jjjjjjjjjj#",
        "#jjjjjjjjjj#",
        "#jjjjjjjjjj#",
        "#jjjjjjjjjj#",
        "#jjjjjjjjjj#",
        "############",
    ],
}

# Flèche de souris : X = contour noir, O = remplissage blanc
MOTIF_CURSEUR = [
    "X...........",
    "XX..........",
    "XOX.........",
    "XOOX........",
    "XOOOX.......",
    "XOOOOX......",
    "XOOOOOX.....",
    "XOOOOOOX....",
    "XOOOOOOOX...",
    "XOOOOOOOOX..",
    "XOOOOOOOOOX.",
    "XOOOOOOXXXXX",
    "XOOXOOX.....",
    "XOX.XOOX....",
    "XX..XOOX....",
    "X....XOOX...",
    ".....XOOX...",
    "......XX....",
]
TAILLE_CURSEUR = 32


def creer_icone(nom: str, zoom: int = 3, remplacements: dict | None = None) -> tk.PhotoImage:
    """Dessine l'icône « nom » pixel par pixel et l'agrandit de « zoom » fois.

    « remplacements » change des couleurs (par ex. {"j": "#FFFFFF"} pour une étoile vide).
    Il faut garder une référence à l'image renvoyée, sinon Tkinter l'efface.
    """
    motif = MOTIFS[nom]
    palette = {**PALETTE, **(remplacements or {})}
    image = tk.PhotoImage(width=len(motif[0]), height=len(motif))
    for y, ligne in enumerate(motif):
        for x, symbole in enumerate(ligne):
            if symbole in palette:
                image.put(palette[symbole], to=(x, y))
    return image.zoom(zoom)


def nombre_etoiles(note: float) -> int:
    """Convertit une note sur 10 en nombre d'étoiles pleines (de 0 à 5)."""
    return max(0, min(5, int(note / 2 + 0.5)))


def ecrire_curseur(chemin: str) -> None:
    """Écrit un fichier curseur Windows (.cur) en forme de flèche, point chaud en haut à gauche."""
    taille = TAILLE_CURSEUR
    couleurs = {"X": (0x2E, 0x1B, 0x1E, 255), "O": (255, 255, 255, 255)}  # (B, G, R, alpha)
    lignes = [[(0, 0, 0, 0)] * taille for _ in range(taille)]
    for y, ligne in enumerate(MOTIF_CURSEUR):
        for x, symbole in enumerate(ligne):
            if symbole in couleurs:
                lignes[y][x] = couleurs[symbole]

    pixels = b""   # l'image, ligne du bas en premier (c'est le format BMP)
    masque = b""   # 1 = transparent
    for ligne in reversed(lignes):
        pixels += b"".join(struct.pack("BBBB", *p) for p in ligne)
        bits = "".join("1" if p[3] == 0 else "0" for p in ligne)
        masque += int(bits, 2).to_bytes(taille // 8, "big")

    entete_image = struct.pack("<IiiHHIIiiII", 40, taille, taille * 2, 1, 32, 0, 0, 0, 0, 0, 0)
    donnees = entete_image + pixels + masque
    entete = struct.pack("<HHH", 0, 2, 1)  # type 2 = curseur, 1 image
    entree = struct.pack("<BBBBHHII", taille, taille, 0, 0, 0, 0, len(donnees), 22)
    with open(chemin, "wb") as f:
        f.write(entete + entree + donnees)


def appliquer_curseur(racine: tk.Tk) -> None:
    """Remplace le curseur de la souris par la flèche rétro (Windows seulement).

    Si ça échoue (autre système, chemin inhabituel), le curseur normal est gardé.
    """
    chemin = os.path.join(tempfile.gettempdir(), "estimateur_curseur.cur")
    try:
        ecrire_curseur(chemin)
        racine.configure(cursor="@{" + chemin.replace("\\", "/") + "}")
    except (OSError, tk.TclError):
        pass