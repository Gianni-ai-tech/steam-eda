INTERP = {
"qualite": """
**Lecture.** 55 690 jeux (un matériel écarté). Les données sont propres : moins de 0,3 % de dates illisibles, d'éditeurs ou de genres manquants. Trois transformations étaient nécessaires :
- le **prix** est stocké en centimes, sous forme de texte ;
- le **nombre de propriétaires** est une fourchette (« 20,000 .. 50,000 ») : on garde les deux bornes et le milieu ;
- les **genres et les langues** sont des listes dans une chaîne de caractères : `split` puis `explode` pour les compter.
""",
"editeurs": """
**Lecture.** Le marché est très fragmenté : le premier éditeur, **Big Fish Games** (jeux casual), ne publie que 422 jeux sur 55 690, soit moins de 1 %. **Ubisoft arrive 9e avec 127 jeux** et 77,6 % d'avis positifs, dans la moyenne. Parmi les gros éditeurs, Sekai Project (86,5 %) et SEGA (85,6 %) sont les mieux notés ; Strategy First le moins bien (56,2 %).
""",
"meilleurs": """
**Lecture.** Parmi les jeux qui ont au moins 10 000 avis, les mieux notés dépassent tous 98 % d'avis positifs. On y trouve **surtout des studios indépendants** (A Short Hike, Vampire Survivors, ULTRAKILL, Hades) aux côtés de Valve (Portal 2, Half-Life: Alyx). La qualité perçue ne dépend pas de la taille de l'éditeur.
""",
"annees": """
**Lecture.** Les sorties explosent à partir de 2014 (ouverture de Steam aux indépendants avec Greenlight puis Direct) : de 471 jeux en 2013 à 6 017 en 2017. **La période Covid marque un nouveau record** : 8 305 jeux en 2020, +19 % par rapport à 2019, puis 8 823 en 2021. 2022 n'est pas complète (données arrêtées au 11 novembre) : 7 455 jeux en 10 mois et demi, soit un rythme proche de 2021.
""",
"prix": """
**Lecture.** Steam est un marché de **petits prix** : prix médian 4,99 $, 14 % de jeux gratuits, 78,5 % à moins de 10 $ (gratuits compris), seulement 5,3 % à 20 $ et plus. Au moment de l'export, **4,5 % des jeux étaient en promotion**, avec une remise moyenne élevée (−58 %) : les soldes sont rares mais profondes.
""",
"langues": """
**Lecture.** L'anglais est quasi universel (99 %). Viennent ensuite **l'allemand (25 %), le français (24 %), le russe (23 %), le chinois simplifié (23 %) et l'espagnol (22 %)**, puis le japonais (19 %). Les trois quarts des jeux ne sont donc pas traduits dans les grandes langues européennes ou asiatiques.
""",
"age": """
**Lecture.** **98,8 % des jeux n'ont aucune restriction d'âge** déclarée sur Steam. Les jeux interdits aux moins de 16 ou 18 ans sont marginaux : 0,55 % au total (306 jeux). Le champ est souvent laissé vide par les éditeurs, donc ce chiffre sous-estime probablement les contenus adultes.
""",
"genres": """
**Lecture.** **« Indie » est présent sur 71 % des jeux** (39 681), suivi d'Action (43 %), Casual (40 %) et Adventure (38 %). Un jeu ayant en moyenne plusieurs genres, les totaux dépassent 100 %. Le jeu médian a 10 000 propriétaires (la fourchette la plus basse) quel que soit le genre, sauf **Free to Play et Massively Multiplayer (35 000)** : la gratuité élargit l'audience.
""",
"genres_qualite": """
**Lecture.**
- **Ratio d'avis positifs** : les écarts entre genres sont faibles (69 à 74 %), avec Casual, Indie et Adventure en tête. **Massively Multiplayer est nettement en dessous (63 %, contre 74 % tous jeux confondus)** : les jeux en ligne massifs déçoivent davantage.
- **Chiffre d'affaires estimé** (propriétaires × prix actuel, une approximation grossière) : **Action domine (59 Md$)**, devant Adventure (37 Md$), Indie (32 Md$) et RPG (27 Md$). Les Free to Play apparaissent à 0 car leurs revenus viennent des achats en jeu, absents des données : ce n'est pas un genre non rentable.
""",
"editeurs_genres": """
**Lecture.** Oui, la plupart des gros éditeurs sont spécialisés : **Big Fish Games, 8floor et HH-Games publient presque exclusivement du Casual** (99 à 100 %), **Choice of Games du RPG textuel** (99 %). Les éditeurs « AAA » sont plus diversifiés : SEGA et Square Enix ont environ la moitié de leurs jeux en Action, Square Enix autant en RPG.
""",
"plateformes": """
**Lecture.** **100 % des jeux tournent sous Windows**, seulement 23 % sur Mac et 15 % sur Linux. La compatibilité varie peu selon le genre : Strategy (28 % Mac) et Indie (25 %) sont les mieux portés, Early Access (15 %) et Utilities les moins. Un jeu en accès anticipé se concentre d'abord sur Windows.
""",
"popularite": """
**Lecture.** 12 % des jeux atteignent au moins 100 000 propriétaires. Ce taux varie fortement selon :
- **les langues** : 7 % pour un jeu en 1 langue, **30 % à partir de 10 langues**. C'est l'écart le plus net ;
- **les plateformes** : 10 % sur Windows seul, **21 % sur les trois plateformes** ;
- **le prix** : 7 % sous 10 $, 20 % pour les gratuits, **35 % à 30 $ et plus**. Un prix élevé n'attire pas en soi : il signale un jeu à gros budget, mieux marketé ;
- **le statut** : les jeux en Early Access réussissent moins (8 %) que les autres jeux non indépendants (18 %).

Ce sont des associations, pas des causes : un gros studio traduit plus, porte sur plus de plateformes et vend plus cher.
""",
"correlations": """
**Lecture.** Sur les jeux d'au moins 50 avis, **le nombre de langues est le facteur le plus lié au nombre de propriétaires** (r = 0,22), loin devant les plateformes et le prix (≈ 0,1). La qualité perçue n'est presque pas liée à la popularité (r = 0,07) : un jeu très apprécié peut rester confidentiel.
""",
"conclusions": """
| Constat | Chiffre clé | Recommandation pour Ubisoft |
| --- | --- | --- |
| Marché saturé, très fragmenté | 55 690 jeux, 8 000+ sorties par an depuis 2020 | Se différencier par la visibilité, pas par le volume |
| La traduction est le facteur le plus lié au succès | 30 % de succès à 10 langues et +, contre 7 % à 1 langue | Sortir en 10 langues au moins : allemand, français, russe, chinois, espagnol, japonais en priorité |
| La compatibilité multi-plateforme aide | 21 % sur 3 plateformes, contre 10 % sur Windows seul | Prévoir Mac et Linux (ou Steam Deck) dès la sortie |
| Action reste le genre le plus lucratif | 59 Md$ de CA estimé | Viser Action, éventuellement Action-RPG (27 Md$ pour RPG) |
| Les jeux très bien notés sont souvent indépendants | > 98 % d'avis positifs | La qualité et l'originalité priment sur le budget |
| Les MMO déçoivent | 63 % d'avis positifs contre 74 % en moyenne | Éviter le massivement multijoueur, ou investir fortement dans le service |
| Les soldes sont rares mais fortes | 4,5 % en promo, −58 % en moyenne | Prévoir des promotions ponctuelles et profondes |

**Limites.** Le nombre de propriétaires est une fourchette SteamSpy, le chiffre d'affaires une estimation (prix actuel × milieu de fourchette, hors achats en jeu), et les données s'arrêtent en novembre 2022.
""",
}
