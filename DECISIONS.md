# Fiche de décisions — Projet 2 INF1007

Une ligne par choix important, remplie au fil du projet. Après chaque validation avec l'auxiliaire, inscrire la date et noter si le choix a été maintenu ou modifié (et pourquoi).

| Choix | Options envisagées | Choix retenu et justification | Validé par l'auxiliaire (date) |
|---|---|---|---|
| **Domaine** | Cinéma ; animation japonaise (anime) ; jeu d'échec ; jeux vidéos | **Cinéma.** L'application permet d'estimer la note donnée à un film selon différents critères tels que; son budget, sa durée, son année de sortie, sa langue et son genre. Domaine non sensible : aucun avertissement de type santé/finance n'est requis. | 2026-11-06 |
| **Jeu de données** | `movies.csv` (TMDB, 4 803 films, 24 colonnes) ; `anime.csv` (12 294 anime, 7 colonnes) | **`movies.csv`** : 3 643 films après nettoyage (entre 500 et 50 000), au moins 5 caractéristiques (budget, durée, année, langue, genres), variables numériques et catégorielles, aucune donnée personnelle. **`anime.csv` rejeté** : seulement 4 caractéristiques utilisables (`genre`, `type`, `episodes`, `members`) et la colonne `episodes` contient du texte (« Unknown » sur 340 lignes). Source et licence : *à compléter (page Kaggle)*. | 2026-11-06 |
| **Nettoyage des données** | Garder toutes les lignes ; remplacer les valeurs manquantes ; retirer les lignes problématiques | Retirer les films non sortis (`status` ≠ « Released »), ceux avec moins de 10 votes (note peu fiable), un budget ou une durée à 0 (valeur inconnue), et les budgets aberrants sous 10 000 $ (21 films, probablement saisis en millions). Garder seulement les langues ayant au moins 20 films (en, es, fr) pour que le modèle corresponde aux choix offerts dans l'interface. | — |
| **Cible et métrique** | Exactitude / F1 (classification) ; MAE ; RMSE ; R² | **Cible : `vote_average`** (note sur 10) → problème de **régression**. Exactitude et F1 rejetées : la cible n'est pas une catégorie. **RMSE** comme métrique principale : exprimée en points sur 10, donc facile à interpréter, et elle pénalise les grosses erreurs. **R²** en complément pour mesurer le gain par rapport à la référence. | À faire — AAAA-MM-JJ |
| **Modèle** | Moyenne ; médiane | **Moyenne des notes** de l'ensemble d'entraînement (`DummyRegressor`) : RMSE attendue d'environ 0,88 (écart-type de la note), R² d'environ 0. | — |
| **Modèle** | Régression linéaire ; k plus proches voisins ; arbre de décision ; forêt aléatoire | *À compléter : modèle retenu et pourquoi (ex. interprétabilité, performance sur l'ensemble de test, importance des variables utilisable dans le graphique).* | À faire — AAAA-MM-JJ |
| **Encodage des genres** | Garder seulement le premier genre ; une colonne 0/1 par genre | **Une colonne 0/1 par genre** : un film peut avoir plusieurs genres, et l'interface les offre en cases à cocher (`VariableMultiple`). | — |
| **Technologie d'interface** | Tkinter ; Streamlit ; PySide6 ; Gradio | **Tkinter** : inclus avec Python (rien à installer), fonctionne en local, et permet d'intégrer un graphique Matplotlib. *Ajouter ici la maquette papier présentée.* | À faire — AAAA-MM-JJ |
| **Format de saisie numérique** | Accepter « 1 000 » (espace des milliers) ; le refuser | *À compléter : choix retenu et justification.* Actuellement refusé, avec un message d'erreur clair. | — |
| **Outil du chapitre 7** | Décorateur (chronométrer l'entraînement) ; générateur (lecture par blocs) ; lambda (clé de tri) | *À compléter.* | — |
| *Autre choix important* | | | |
 *Autre choix important* | | | |
  *Autre choix important* | | | |
