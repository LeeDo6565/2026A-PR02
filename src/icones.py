
import tkinter as tk

import theme
# Notre fichier de couleurs : les icônes utilisent les mêmes couleurs que le reste

# ---------------------------------------------------------------------------
# Chaque icône est un petit dessin en « pixels », écrit avec des lettres :
# une lettre = une couleur, et « . » = transparent (on voit le fond derrière).
# La PALETTE dit à quelle couleur correspond chaque lettre.
# ---------------------------------------------------------------------------
PALETTE = {"#": theme.NOIR, "r": "#F58FA8", "j": "#FFC93C", "o": theme.ORANGE,
           "b": theme.BLANC, "v": theme.BARRE_ALT, "c": "#2FA8E8", "e": "#EB4A3C"}



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


