# Fiche de décisions — Projet 2 INF1007

Une ligne par choix important, remplie au fil du projet. Après chaque validation avec l'auxiliaire, inscrire la date et noter si le choix a été maintenu ou modifié (et pourquoi).

| CHOIX | OPTIONS ENVISAGÉES | CHOIX RETENU ET JUSTIFICATION | VALIDÉ PAR L'AUXILIAIRE (DATE) |


| **DOMAINE** | Cinéma ; animation japonaise (anime) ; *autre piste à compléter* | **Cinéma.** L'application permet à un utilisateur (cinéphile, étudiant en cinéma, petit producteur) d'estimer la note qu'un film recevrait du public selon son budget, sa durée, son année, sa langue et ses genres. Domaine non sensible : aucun avertissement de type santé/finance n'est requis. | À faire — AAAA-MM-JJ |


| **JEU DE DONNÉES** | `movies.csv` (TMDB, 4 803 films, 24 colonnes) ; `anime.csv` (12 294 anime, 7 colonnes) | **`movies.csv`** : 3 643 films après nettoyage (entre 500 et 50 000), au moins 5 caractéristiques (budget, durée, année, langue, genres), variables numériques et catégorielles, aucune donnée personnelle. **`anime.csv` rejeté** : seulement 4 caractéristiques utilisables (`genre`, `type`, `episodes`, `members`) et la colonne `episodes` contient du texte (« Unknown » sur 340 lignes). Source et licence : *à compléter (page Kaggle)*. | À faire — AAAA-MM-JJ |



| **CIBLE ET MÉTRIQUE** | Exactitude / F1 (classification) ; MAE ; RMSE ; R² | **Cible : `vote_average`** (note sur 10) → problème de **régression**. Exactitude et F1 rejetées : la cible n'est pas une catégorie. **RMSE** comme métrique principale : exprimée en points sur 10, donc facile à interpréter, et elle pénalise les grosses erreurs. **R²** en complément pour mesurer le gain par rapport à la référence. | À faire — AAAA-MM-JJ |



| **MODÈLE** | Moyenne ; médiane | **Moyenne des notes** de l'ensemble d'entraînement (`DummyRegressor`) : RMSE attendue d'environ 0,88 (écart-type de la note), R² d'environ 0. | — |
| **Modèle** (validation C) | Régression linéaire ; k plus proches voisins ; arbre de décision ; forêt aléatoire | *À compléter : modèle retenu et pourquoi (ex. interprétabilité, performance sur l'ensemble de test, importance des variables utilisable dans le graphique).* | À faire — AAAA-MM-JJ |


| **TECHNOLOGIE D'INTERFACE** | Tkinter ; Streamlit ; PySide6 ; Gradio | **Tkinter** : inclus avec Python (rien à installer), fonctionne en local, et permet d'intégrer un graphique Matplotlib. *Ajouter ici la maquette papier présentée.* | À faire — AAAA-MM-JJ |
| **Format de saisie numérique** | Accepter « 1 000 » (espace des milliers) ; le refuser | *À compléter : choix retenu et justification.* Actuellement refusé, avec un message d'erreur clair. | — |


| **AUTRE CHOIX** | BLA BLA BLA | BLA BLA BLA | BLA BLA BLA |


| **AUTRE CHOIX** | BLA BLA BLA | BLA BLA BLA | BLA BLA BLA |


| **AUTRE CHOIX** | BLA BLA BLA | BLA BLA BLA | BLA BLA BLA |

