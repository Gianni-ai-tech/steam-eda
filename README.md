# Steam – Analyse du marché du jeu vidéo avec PySpark (Jedha CDSD, bloc 2)

Analyse exploratoire de 55 690 jeux Steam pour Ubisoft : éditeurs, notes, sorties par année, prix et promotions, langues, restrictions d'âge, genres, plateformes, et facteurs associés au succès.

## Fichiers
- `steam_eda.ipynb` : notebook PySpark exécuté (préparation et agrégations en Spark, graphiques sur les résultats agrégés).
- `steam_eda.html` : le même notebook avec toutes ses sorties, lisible dans un navigateur.
- `captures/` : captures d'écran des sorties de chaque cellule. La publication des notebooks Databricks n'étant plus disponible, Jedha demande ces captures.
- `build_notebook.py` + `interpretations.py` : génèrent le notebook (code et commentaires).

## Données
`s3://full-stack-bigdata-datasets/Big_Data/Project_Steam/steam_game_output.json` (64 Mo), à placer dans `data/`.

## Lancer
```bash
pip install pyspark pandas matplotlib pyarrow jupyter
jupyter nbconvert --to notebook --execute steam_eda.ipynb
```
Le code tourne tel quel dans un notebook Databricks : l'objet `spark` y existe déjà, et `display(df)` remplace les graphiques matplotlib.

## Principaux résultats
- 8 000+ jeux sortis par an depuis 2020 (+19 % en 2020, année Covid).
- Prix médian 4,99 $, 14 % de jeux gratuits ; 4,5 % en promotion, −58 % en moyenne.
- Action est le genre au plus gros chiffre d'affaires estimé (59 Md$).
- Les jeux traduits en 10 langues et plus atteignent 100 000 propriétaires 4 fois plus souvent (30 % contre 7 %).
