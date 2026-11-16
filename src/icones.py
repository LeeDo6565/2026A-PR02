import os
# Pour construire des chemins de fichiers
import struct
# Pour fabriquer des octets bruts (le fichier du curseur est un format binaire)
import tempfile
# Pour trouver le dossier temporaire de l'ordinateur
import tkinter as tk
# Tkinter : on s'en sert pour créer les images (tk.PhotoImage)

import theme
# Notre fichier de couleurs : les icônes utilisent les mêmes couleurs que le reste

# ---------------------------------------------------------------------------
# Chaque icône est un petit dessin en « pixels », écrit avec des lettres :
# une lettre = une couleur, et « . » = transparent (on voit le fond derrière).
# La PALETTE dit à quelle couleur correspond chaque lettre.
# ---------------------------------------------------------------------------
PALETTE = {"#": theme.NOIR, "r": "#F58FA8", "j": "#FFC93C", "o": theme.ORANGE,
           "b": theme.BLANC, "v": theme.BARRE_ALT, "c": "#2FA8E8", "e": "#EB4A3C"}
# #  contour bleu nuit   r  rose   j  jaune   o  orange   b  blanc
# v  rose foncé (barre)   c  bleu clair   e  rouge

# Le dictionnaire des dessins : « nom de l'icône » -> liste de lignes de pixels.
# Toutes les lignes d'un même dessin ont la même largeur (un test le vérifie).
MOTIFS = {
    # Un cœur rose (11 pixels de large, 10 de haut), avec un petit reflet blanc
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
    # Une étoile jaune à cinq branches ; pour une étoile « vide », on change le jaune en blanc
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
    # Un visage jaune qui sourit
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
    # Un dossier : onglet orange en haut, corps jaune
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
    # Une bulle de message rose avec un cœur rouge dedans (et sa petite queue en bas à gauche)
    "bulle": [
        ".#############.",
        "#rrrrrrrrrrrrr#",
        "#rrrr##r##rrrr#",
        "#rrr#ee#ee#rrr#",
        "#rr#eeeeeee#rr#",
        "#rr#eeeeeee#rr#",
        "#rrr#eeeee#rrr#",
        "#rrrr#eee#rrrr#",
        "#rrrrr#e#rrrrr#",
        "#rrrrrr#rrrrrr#",
        "#rrrrrrrrrrrrr#",
        ".##rr#########.",
        "..#r#..........",
        "..##...........",
    ],
    # Un rond blanc avec un triangle bleu : le bouton « lecture »
    "lecture": [
        "....#####....",
        "..##bbbbb##..",
        ".#bbbbbbbbb#.",
        ".#bbbcbbbbb#.",
        "#bbbbccbbbbb#",
        "#bbbbcccbbbb#",
        "#bbbbccccbbb#",
        "#bbbbcccbbbb#",
        "#bbbbccbbbbb#",
        ".#bbbcbbbbb#.",
        ".#bbbbbbbbb#.",
        "..##bbbbb##..",
        "....#####....",
    ],
    # Un rond blanc avec deux barres bleues : le bouton « pause »
    "pause": [
        "....#####....",
        "..##bbbbb##..",
        ".#bbbbbbbbb#.",
        ".#bbccbccbb#.",
        "#bbbccbccbbb#",
        "#bbbccbccbbb#",
        "#bbbccbccbbb#",
        "#bbbccbccbbb#",
        "#bbbccbccbbb#",
        ".#bbccbccbb#.",
        ".#bbbbbbbbb#.",
        "..##bbbbb##..",
        "....#####....",
    ],
    # Un rond blanc avec un disque bleu : le bouton « enregistrement »
    "enregistrer": [
        "....#####....",
        "..##bbbbb##..",
        ".#bbbbbbbbb#.",
        ".#bbbcccbbb#.",
        "#bbbcccccbbb#",
        "#bbcccccccbb#",
        "#bbcccccccbb#",
        "#bbcccccccbb#",
        "#bbbcccccbbb#",
        ".#bbbcccbbb#.",
        ".#bbbbbbbbb#.",
        "..##bbbbb##..",
        "....#####....",
    ],
    # Un disque vinyle rouge avec un trou bleu au centre
    "disque": [
        "...#####...",
        "..#eeeee#..",
        ".#eeeeeee#.",
        "#eeeeeeeee#",
        "#eeeccceee#",
        "#eeecbceee#",
        "#eeeccceee#",
        "#eeeeeeeee#",
        ".#eeeeeee#.",
        "..#eeeee#..",
        "...#####...",
    ],
}

# Le dessin de la flèche de souris : X = contour bleu nuit, O = remplissage blanc
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
# Un curseur Windows tient dans un carré de 32 x 32 pixels


def creer_icone(nom: str, zoom: int = 3, remplacements: dict | None = None) -> tk.PhotoImage:
    """Dessine l'icône « nom » pixel par pixel et l'agrandit de « zoom » fois.

    « remplacements » change des couleurs (par ex. {"j": "#FFFFFF"} pour une étoile vide).
    Il faut garder une référence à l'image renvoyée, sinon Tkinter l'efface.
    """
    motif = MOTIFS[nom]
    # Va chercher le dessin demandé (par exemple la liste de lignes du cœur)
    palette = {**PALETTE, **(remplacements or {})}
    # Fusionne la palette normale avec les couleurs à remplacer (« ** » déballe un dictionnaire)
    image = tk.PhotoImage(width=len(motif[0]), height=len(motif))
    # Crée une image vide, de la taille du dessin (largeur = longueur d'une ligne)
    for y, ligne in enumerate(motif):
        # Pour chaque ligne du dessin, avec son numéro y (0 = tout en haut)
        for x, symbole in enumerate(ligne):
            # Pour chaque lettre de la ligne, avec sa position x (0 = tout à gauche)
            if symbole in palette:
                # Si la lettre correspond à une couleur (donc pas un « . » transparent)...
                image.put(palette[symbole], to=(x, y))
                # ...on peint ce pixel de la bonne couleur
    return image.zoom(zoom)
    # Agrandit l'image : chaque pixel devient un carré de 3 x 3 pixels, pour qu'elle soit visible


def nombre_etoiles(note: float) -> int:
    """Convertit une note sur 10 en nombre d'étoiles pleines (de 0 à 5)."""
    return max(0, min(5, int(note / 2 + 0.5)))
    # note / 2 : une note sur 10 devient une note sur 5 ; + 0.5 puis int : arrondi au plus proche
    # (par exemple 7.0 -> 3.5 -> 4 étoiles) ; min(5, ...) et max(0, ...) : reste entre 0 et 5


def ecrire_curseur(chemin: str) -> None:
    """Écrit un fichier curseur Windows (.cur) en forme de flèche, point chaud en haut à gauche."""
    taille = TAILLE_CURSEUR
    couleurs = {"X": (0x2E, 0x1B, 0x1E, 255), "O": (255, 255, 255, 255)}  # (B, G, R, alpha)
    # Chaque pixel = 4 nombres (bleu, vert, rouge, opacité de 0 à 255). Ce format est celui de Windows
    lignes = [[(0, 0, 0, 0)] * taille for _ in range(taille)]
    # Une grille de 32 x 32 pixels entièrement transparents (opacité 0)
    for y, ligne in enumerate(MOTIF_CURSEUR):
        for x, symbole in enumerate(ligne):
            if symbole in couleurs:
                lignes[y][x] = couleurs[symbole]
    # Recopie le dessin de la flèche dans le coin en haut à gauche de la grille

    pixels = b""   # l'image, ligne du bas en premier (c'est le format BMP)
    masque = b""   # 1 = transparent
    for ligne in reversed(lignes):
        # Le format demande les lignes de bas en haut, d'où « reversed »
        pixels += b"".join(struct.pack("BBBB", *p) for p in ligne)
        # Transforme les 4 nombres de chaque pixel en 4 octets et les colle les uns après les autres
        bits = "".join("1" if p[3] == 0 else "0" for p in ligne)
        # Le « masque » : un 1 pour chaque pixel transparent, un 0 pour chaque pixel visible
        masque += int(bits, 2).to_bytes(taille // 8, "big")
        # Regroupe ces 32 bits en 4 octets

    entete_image = struct.pack("<IiiHHIIiiII", 40, taille, taille * 2, 1, 32, 0, 0, 0, 0, 0, 0)
    # L'en-tête de l'image : largeur, hauteur (doublée : le format compte l'image + le masque),
    # 32 bits par pixel... Ces nombres suivent la norme du format, il suffit de les recopier
    donnees = entete_image + pixels + masque
    entete = struct.pack("<HHH", 0, 2, 1)  # type 2 = curseur, 1 image
    # L'en-tête du fichier : « c'est un curseur, et il contient une image »
    entree = struct.pack("<BBBBHHII", taille, taille, 0, 0, 0, 0, len(donnees), 22)
    # La description de l'image : sa taille, le point « actif » du curseur (0, 0 = la pointe
    # de la flèche, en haut à gauche), la taille des données et leur position dans le fichier
    with open(chemin, "wb") as f:
        # « wb » : écrire en binaire ; « with » referme le fichier tout seul
        f.write(entete + entree + donnees)


def appliquer_curseur(racine: tk.Tk) -> None:
    """Remplace le curseur de la souris par la flèche rétro (Windows seulement).

    Si ça échoue (autre système, chemin inhabituel), le curseur normal est gardé.
    """
    chemin = os.path.join(tempfile.gettempdir(), "estimateur_curseur.cur")
    # Le fichier du curseur est écrit dans le dossier temporaire de l'ordinateur
    try:
        ecrire_curseur(chemin)
        # Fabrique le fichier...
        racine.configure(cursor="@{" + chemin.replace("\\", "/") + "}")
        # ...et dit à Tkinter de l'utiliser (« @ » = « charge un fichier » ; les accolades
        # protègent un chemin qui contient des espaces)
    except (OSError, tk.TclError):
        # Si ça échoue (autre système que Windows, dossier impossible à écrire...)
        pass
        # on ne fait rien : l'application garde simplement le curseur normal