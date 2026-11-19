import pytest 

from exceptions import DonneeInvalideError

from variables import (VariableCategorielle, VariableMultiple,
                       VariableNumerique, creer_variables)

# --- Fixtures : des objets préparés, réutilisables par plusieurs tests -----
@pytest.fixture   #marque une fonction qui prépare un objet réutilisable par plusieurs tests, pour ne pas le recréer à la main dans chacun.
def budget() -> VariableNumerique: #Quand un test écrit budget dans ses paramètres, pytest appelle cette fonction avant le test et lui passe le résultat
    return VariableNumerique("budget", "Budget ($)", 1, 380_000_000)


@pytest.fixture
def langue() -> VariableCategorielle:
    return VariableCategorielle("original_language", "Langue d'origine", ["en", "fr", "es"])



@pytest.fixture
def genres() -> VariableMultiple:
    return VariableMultiple("genres", "Genres", ["Action", "Drama", "Science-Fiction"])


# --- VariableNumerique ---------------------------------------------------
def test_numerique_valeur_usuelle(budget): # CAS USUEL : un budget normal est accepté et converti en nombre (fonction valider)
    assert budget.valider("5000000") == pytest.approx(5_000_000) # # pytest.approx compare des nombres à virgule sans être trompé par les arrondis( _ pour représenter les espaces--> facultatif)


def test_numerique_virgule_decimale_et_espaces():
    duree = VariableNumerique("runtime", "Durée (minutes)", 40, 300) # # Ici on crée la variable dans le test : on a besoin de bornes différentes (40 à 300)
    assert duree.valider("  120,5 ") == pytest.approx(120.5) ## Les espaces autour sont retirés et la virgule est lue comme un point décimal


@pytest.mark.parametrize("saisie", ["1", "380000000"]) #ça fait tourner le même test plusieurs fois, une fois par valeur de la liste. Avec ["1", "380000000"], pytest crée deux test
def test_numerique_bornes_acceptees(budget, saisie):
    assert budget.valider(saisie) == pytest.approx(float(saisie))


@pytest.mark.parametrize("saisie", ["", "   "])
def test_numerique_saisie_vide(budget, saisie):
    with pytest.raises(DonneeInvalideError):
        budget.valider(saisie)


@pytest.mark.parametrize("saisie", ["abc", "12abc", "1 000"])
def test_numerique_pas_un_nombre(budget, saisie):
    with pytest.raises(DonneeInvalideError):
        budget.valider(saisie)


@pytest.mark.parametrize("saisie", ["0", "-5", "380000001"])
def test_numerique_hors_intervalle(budget, saisie):
    with pytest.raises(DonneeInvalideError):
        budget.valider(saisie)


def test_numerique_message_mentionne_le_champ(budget):
    with pytest.raises(DonneeInvalideError, match="Budget"):
        budget.valider("")


# --- VariableCategorielle ------------------------------------------------

def test_categorielle_valeur_valide(langue):  # CAS USUEL : une langue de la liste est renvoyée telle quelle
    assert langue.valider("fr") == "fr"


@pytest.mark.parametrize("saisie", ["", "xx", "FR"])
def test_categorielle_valeur_invalide(langue, saisie): # CAS D'ERREUR : rien choisi, langue inconnue, et mauvaise casse (« FR » ≠ « fr »)
    with pytest.raises(DonneeInvalideError):
        langue.valider(saisie)


def test_categorielle_valeurs_est_une_copie(langue): # ENCAPSULATION : modifier la liste obtenue ne doit pas changer celle de l'objet
    choix = langue.valeurs
    choix.append("klingon")
    assert "klingon" not in langue.valeurs


# --- VariableMultiple ----------------------------------------------------

def test_multiple_valeurs_valides(genres): # CAS USUEL : deux cases cochées, toutes deux permises
    assert genres.valider(["Drama", "Science-Fiction"]) == ["Drama", "Science-Fiction"]


def test_multiple_aucune_case_cochee(genres): # CAS D'ERREUR : liste vide
    with pytest.raises(DonneeInvalideError):
        genres.valider([])


def test_multiple_genre_inconnu(genres):# CAS D'ERREUR : un des genres cochés n'existe pas
    with pytest.raises(DonneeInvalideError):
        genres.valider(["Drama", "Western"])


# --- creer_variables et __str__ -----------------------------------------

def test_creer_variables_construit_les_cinq_champs(): # On fournit de petites métadonnées inventées (pas besoin du vrai fichier JSON)
    meta = {
        "budget_min": 1, "budget_max": 100, "runtime_min": 40, "runtime_max": 300,
        "annee_min": 1950, "annee_max": 2020,
        "langues": ["en", "fr"], "genres": ["Action", "Drama"],
    }
    variables = creer_variables(meta)  # Vérifie les noms, dans l'ordre : c'est l'ordre d'affichage dans le formulaire
   
    assert [v.nom for v in variables] == [
        "budget", "runtime", "annee", "original_language", "genres"]   #vérifie que creer_variables a bien fabriqué les cinq variables, dans le bon ordre. Il se lit en deux parties, de part et d’autre du ==
    
    assert [type(v) for v in variables] == [
        VariableNumerique, VariableNumerique, VariableNumerique,
        VariableCategorielle, VariableMultiple]


def test_str_affiche_libelle_et_nom(budget): ## Teste la méthode spéciale __str__ : ce que print(variable) affiche
    assert str(budget) == "Budget ($) (budget)"