import pytest

icones = pytest.importorskip("icones")  # ignoré si tkinter n'est pas installé


@pytest.mark.parametrize("note, attendu", [
    (0, 0), (1.2, 1), (3.0, 2), (5.0, 3), (7.0, 4), (9.9, 5), (10, 5), (-1, 0), (12, 5),
])
def test_nombre_etoiles(note, attendu):
    assert icones.nombre_etoiles(note) == attendu


def test_motifs_ont_des_lignes_de_meme_largeur():
    for nom, motif in icones.MOTIFS.items():
        assert len({len(ligne) for ligne in motif}) == 1, nom


def test_ecrire_curseur_cree_un_fichier_cur_valide(tmp_path):
    chemin = tmp_path / "curseur.cur"
    icones.ecrire_curseur(str(chemin))
    contenu = chemin.read_bytes()
    assert contenu[:6] == b"\x00\x00\x02\x00\x01\x00"  # en-tête : type « curseur », une image
    assert len(contenu) == 22 + 40 + 32 * 32 * 4 + 32 * 4