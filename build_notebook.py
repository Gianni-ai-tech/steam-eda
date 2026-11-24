"""Construit steam_eda.ipynb. Les interprétations viennent de interpretations.py (rédigées après lecture des résultats)."""
import nbformat as nbf
import importlib.util, os

INTERP = {}
if os.path.exists("interpretations.py"):
    spec = importlib.util.spec_from_file_location("interp", "interpretations.py")
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    INTERP = mod.INTERP

nb = nbf.v4.new_notebook()
C = []
md = lambda s: C.append(nbf.v4.new_markdown_cell(s.strip()))
code = lambda s: C.append(nbf.v4.new_code_cell(s.strip()))
lecture = lambda k: md(INTERP.get(k, f"**Lecture.** _à rédiger ({k})_"))

md("""
# Steam – Le marché du jeu vidéo vu par 55 000 jeux (PySpark)

**Contexte.** Ubisoft prépare un nouveau jeu et veut comprendre l'écosystème Steam : quels facteurs jouent sur la popularité et les ventes d'un jeu, et quelles sont les tendances du marché.

**Données.** Export de l'API Steam/SteamSpy : un document JSON par jeu, avec un schéma imbriqué (`data.platforms`, `data.tags`, listes de catégories, genres et langues en texte).

**Outil.** Toute la préparation et les agrégations sont faites en **PySpark** (DataFrame API, `explode`, `split`, `getField`, fonctions de date et de texte, `groupBy`). Seuls les résultats agrégés, de quelques dizaines de lignes, passent en pandas pour les graphiques.

> Ce notebook a été exécuté sur un Spark local. Il tourne tel quel dans Databricks, où l'objet `spark` existe déjà ; on peut y remplacer les graphiques matplotlib par `display(df)` et l'outil de visualisation Databricks. La publication des notebooks Databricks n'étant plus disponible, les sorties de cellules sont fournies en captures (`captures/`) et en export HTML.

**Plan.** 1. Chargement et nettoyage · 2. Vue macro · 3. Genres · 4. Plateformes · 5. Ce qui fait un jeu populaire · 6. Conclusions pour Ubisoft
""")

code("""
import warnings
warnings.filterwarnings("ignore")
from pyspark.sql import SparkSession, functions as F, Window
import pandas as pd
import matplotlib.pyplot as plt

spark = (SparkSession.builder.master("local[*]").appName("steam-eda")
         .config("spark.driver.memory", "4g").config("spark.ui.showConsoleProgress", "false").getOrCreate())
spark.sparkContext.setLogLevel("ERROR")
plt.rcParams.update({"figure.dpi": 110, "axes.grid": True, "grid.alpha": 0.3})

def barh(pdf, x, y, title, xlabel="", color="#4c72b0", fmt="{:,.0f}"):
    \"\"\"Barres horizontales triées, valeurs affichées.\"\"\"
    pdf = pdf.iloc[::-1]
    fig, ax = plt.subplots(figsize=(8, 0.38 * len(pdf) + 1))
    ax.barh(pdf[y].astype(str), pdf[x], color=color)
    for i, v in enumerate(pdf[x]):
        ax.text(v, i, " " + fmt.format(v), va="center", fontsize=9)
    ax.set(title=title, xlabel=xlabel)
    plt.show()

raw = spark.read.json("data/steam_game_output.json")
raw.printSchema()
""")

md("## 1. Chargement et nettoyage")

code("""
df = (raw.select("data.*")
      .filter(F.col("type") == "game")                                   # 1 « hardware » écarté
      .withColumn("price_usd", F.expr("try_cast(price AS double)") / 100)        # prix stocké en cents, en texte
      .withColumn("initial_usd", F.expr("try_cast(initialprice AS double)") / 100)
      .withColumn("discount", F.expr("try_cast(discount AS int)"))
      .withColumn("required_age", F.expr(r"try_cast(regexp_extract(required_age, '(\\\\d+)', 1) AS int)"))
      .withColumn("release", F.coalesce(F.expr("try_to_date(release_date, 'yyyy/M/d')"),   # formats mixtes : jour absent
                                         F.expr("try_to_date(release_date, 'yyyy/M')")))
      .withColumn("year", F.year("release"))
      # owners = "20,000 .. 50,000" -> bornes numériques et milieu de fourchette
      .withColumn("owners_low", F.regexp_replace(F.split("owners", r" \\.\\. ").getItem(0), ",", "").try_cast("long"))
      .withColumn("owners_high", F.regexp_replace(F.split("owners", r" \\.\\. ").getItem(1), ",", "").try_cast("long"))
      .withColumn("owners_mid", (F.col("owners_low") + F.col("owners_high")) / 2)
      .withColumn("reviews", F.col("positive") + F.col("negative"))
      .withColumn("positive_ratio", F.when(F.col("reviews") > 0, F.col("positive") / F.col("reviews")))
      .withColumn("genres", F.array_remove(F.split(F.coalesce("genre", F.lit("")), r",\\s*"), ""))
      .withColumn("langs", F.array_remove(F.split(F.regexp_replace(F.coalesce("languages", F.lit("")), r"\\[b\\]\\*\\[/b\\]|\\*", ""), r",\\s*"), ""))
      .withColumn("n_langs", F.size("langs"))
      .withColumn("windows", F.col("platforms").getField("windows"))
      .withColumn("mac", F.col("platforms").getField("mac"))
      .withColumn("linux", F.col("platforms").getField("linux"))
      .withColumn("n_platforms", F.col("windows").cast("int") + F.col("mac").cast("int") + F.col("linux").cast("int"))
      .withColumn("est_revenue", F.col("owners_mid") * F.col("price_usd"))   # proxy grossier : propriétaires × prix actuel
      .cache())

n = df.count()
print(f"{n:,} jeux")
qual = df.select(
    F.round(F.avg(F.col("release").isNull().cast("int")) * 100, 2).alias("% date illisible"),
    F.round(F.avg((F.col("publisher") == "").cast("int")) * 100, 2).alias("% sans éditeur"),
    F.round(F.avg((F.size("genres") == 0).cast("int")) * 100, 2).alias("% sans genre"),
    F.round(F.avg((F.col("reviews") == 0).cast("int")) * 100, 2).alias("% sans avis"))
qual.show()
df.select("name", "price_usd", "owners", "owners_mid", "year", "genres", "n_langs", "n_platforms", "positive_ratio").show(5, truncate=40)
""")
lecture("qualite")

md("## 2. Vue macro")
md("### 2.1 Quels éditeurs publient le plus ?")
code("""
pub = (df.filter(F.col("publisher") != "").groupBy("publisher")
         .agg(F.count("*").alias("jeux"), F.round(F.avg("positive_ratio") * 100, 1).alias("% avis positifs"))
         .orderBy(F.desc("jeux")).limit(15))
pub_pd = pub.toPandas()
barh(pub_pd, "jeux", "publisher", "Éditeurs ayant publié le plus de jeux", "nombre de jeux")
pub_pd
""")
lecture("editeurs")

md("### 2.2 Les jeux les mieux notés")
code("""
best = (df.filter(F.col("reviews") >= 10000)
          .select("name", "publisher", "year", "reviews", F.round(F.col("positive_ratio") * 100, 1).alias("% positifs"))
          .orderBy(F.desc("% positifs"), F.desc("reviews")).limit(15))
best.toPandas()
""")
lecture("meilleurs")

md("### 2.3 Les sorties par année (et l'effet Covid)")
code("""
years = (df.filter(F.col("year").between(2006, 2022)).groupBy("year").count().orderBy("year"))
y_pd = years.toPandas()
fig, ax = plt.subplots(figsize=(9, 3.8))
ax.bar(y_pd.year, y_pd["count"], color=["#c44e52" if y in (2020, 2021) else "#4c72b0" for y in y_pd.year])
ax.set(title="Jeux sortis par année (2020-2021 en rouge ; 2022 arrêté au 11 novembre)", xlabel="année", ylabel="jeux")
plt.show()
y_pd.set_index("year").T
""")
lecture("annees")

md("### 2.4 Prix et réductions")
code("""
buckets = (df.withColumn("tranche", F.when(F.col("price_usd") == 0, "gratuit")
                                   .when(F.col("price_usd") < 5, "< 5 $")
                                   .when(F.col("price_usd") < 10, "5-10 $")
                                   .when(F.col("price_usd") < 20, "10-20 $")
                                   .when(F.col("price_usd") < 40, "20-40 $")
                                   .otherwise("≥ 40 $"))
             .groupBy("tranche").count())
order = ["gratuit", "< 5 $", "5-10 $", "10-20 $", "20-40 $", "≥ 40 $"]
b_pd = buckets.toPandas().set_index("tranche").loc[order]
b_pd["%"] = (b_pd["count"] / n * 100).round(1)

remise = df.select(
    F.round(F.avg((F.col("discount") > 0).cast("int")) * 100, 1).alias("% de jeux en promotion"),
    F.round(F.avg(F.when(F.col("discount") > 0, F.col("discount"))), 1).alias("remise moyenne (%)"),
    F.round(F.expr("percentile_approx(price_usd, 0.5)"), 2).alias("prix médian ($)"),
    F.round(F.avg("price_usd"), 2).alias("prix moyen ($)"))
remise.show()

fig, ax = plt.subplots(figsize=(8, 3.5))
ax.bar(b_pd.index, b_pd["%"], color="#4c72b0")
for i, v in enumerate(b_pd["%"]):
    ax.text(i, v + 0.5, f"{v} %", ha="center")
ax.set(title="Répartition des prix", ylabel="% des jeux")
plt.show()
""")
lecture("prix")

md("### 2.5 Les langues les plus représentées")
code("""
langs = (df.select(F.explode("langs").alias("langue"))
           .withColumn("langue", F.trim("langue"))
           .groupBy("langue").count().orderBy(F.desc("count")).limit(15))
l_pd = langs.toPandas()
l_pd["% des jeux"] = (l_pd["count"] / n * 100).round(1)
barh(l_pd, "% des jeux", "langue", "Langues disponibles (% des jeux)", "% des jeux", fmt="{:.1f} %")
""")
lecture("langues")

md("### 2.6 Les restrictions d'âge")
code("""
age = (df.withColumn("classe", F.when(F.col("required_age") >= 18, "18 ans et +")
                               .when(F.col("required_age") >= 16, "16-17 ans")
                               .when(F.col("required_age") > 0, "moins de 16 ans")
                               .otherwise("aucune restriction"))
         .groupBy("classe").count().orderBy(F.desc("count")))
a_pd = age.toPandas()
a_pd["%"] = (a_pd["count"] / n * 100).round(2)
a_pd
""")
lecture("age")

md("## 3. Les genres")
md("### 3.1 Genres les plus représentés et les mieux notés")
code("""
g = df.select("appid", "positive_ratio", "reviews", "owners_mid", "est_revenue", "price_usd", "publisher",
              "windows", "mac", "linux", F.explode("genres").alias("genre"))
gstats = (g.groupBy("genre")
           .agg(F.count("*").alias("jeux"),
                F.round(F.avg("positive_ratio") * 100, 1).alias("% avis positifs (moy.)"),
                F.round(F.expr("percentile_approx(owners_mid, 0.5)")).alias("propriétaires médians"),
                F.round(F.sum("est_revenue") / 1e9, 2).alias("CA estimé (Md$)"),
                F.round(F.expr("percentile_approx(price_usd, 0.5)"), 2).alias("prix médian ($)"))
           .filter(F.col("jeux") >= 200).orderBy(F.desc("jeux")))
gs_pd = gstats.toPandas()
barh(gs_pd.head(15), "jeux", "genre", "Genres les plus représentés (un jeu peut en avoir plusieurs)", "nombre de jeux")
gs_pd
""")
lecture("genres")

code("""
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
r = gs_pd.sort_values("% avis positifs (moy.)", ascending=False)
axes[0].barh(r.genre[::-1], r["% avis positifs (moy.)"][::-1], color="#55a868")
axes[0].set(title="Part d'avis positifs moyenne par genre", xlim=(50, 90))
c = gs_pd.sort_values("CA estimé (Md$)", ascending=False)
axes[1].barh(c.genre[::-1], c["CA estimé (Md$)"][::-1], color="#dd8452")
axes[1].set(title="Chiffre d'affaires estimé par genre (Md$)")
plt.tight_layout()
plt.show()
""")
lecture("genres_qualite")

md("### 3.2 Les éditeurs ont-ils des genres favoris ?")
code("""
top_pub = [r.publisher for r in pub.limit(8).collect()]
pg = (g.filter(F.col("publisher").isin(top_pub)).groupBy("publisher", "genre").count())
w = Window.partitionBy("publisher").orderBy(F.desc("count"))
tot = df.filter(F.col("publisher").isin(top_pub)).groupBy("publisher").agg(F.count("*").alias("total"))
fav = (pg.withColumn("rang", F.row_number().over(w)).filter("rang <= 2").join(tot, "publisher")
         .withColumn("% des jeux de l'éditeur", F.round(F.col("count") / F.col("total") * 100, 1))
         .orderBy("publisher", "rang"))
fav.toPandas()
""")
lecture("editeurs_genres")

md("## 4. Les plateformes")
code("""
plat = df.select(*[F.round(F.avg(F.col(p).cast("int")) * 100, 1).alias(p) for p in ["windows", "mac", "linux"]])
plat.show()
gp = (g.groupBy("genre").agg(F.count("*").alias("jeux"),
                             F.round(F.avg(F.col("mac").cast("int")) * 100, 1).alias("% Mac"),
                             F.round(F.avg(F.col("linux").cast("int")) * 100, 1).alias("% Linux"))
        .filter("jeux >= 500").orderBy(F.desc("% Mac")))
gp_pd = gp.toPandas()
ax = gp_pd.set_index("genre")[["% Mac", "% Linux"]].plot.barh(figsize=(8, 6))
ax.invert_yaxis(); ax.set(title="Disponibilité Mac et Linux par genre (genres ≥ 500 jeux)", xlabel="% des jeux du genre")
plt.show()
gp_pd
""")
lecture("plateformes")

md("""
## 5. Qu'est-ce qui fait un jeu populaire ?

On mesure la popularité par le **nombre de propriétaires** (milieu de la fourchette SteamSpy) et on regarde, pour chaque facteur, la **part de jeux qui atteignent au moins 100 000 propriétaires** (12 % des jeux). Ce sont des associations, pas des causes.
""")
code("""
df2 = df.withColumn("succes", (F.col("owners_low") >= 100000).cast("int"))
print(f"Jeux à ≥ 100 000 propriétaires : {df2.agg(F.avg('succes')).first()[0]:.1%}")

def taux(col_expr, nom, ordre=None):
    t = (df2.withColumn(nom, col_expr).groupBy(nom)
            .agg(F.count("*").alias("jeux"), F.round(F.avg("succes") * 100, 1).alias("% ≥ 100k propriétaires")).toPandas())
    if ordre: t = t.set_index(nom).loc[ordre].reset_index()
    return t

t_lang = taux(F.when(F.col("n_langs") <= 1, "1 langue").when(F.col("n_langs") <= 4, "2-4").when(F.col("n_langs") <= 9, "5-9").otherwise("10 et +"),
              "langues", ["1 langue", "2-4", "5-9", "10 et +"])
t_plat = taux(F.col("n_platforms").cast("string"), "plateformes", ["1", "2", "3"])
t_prix = taux(F.when(F.col("price_usd") == 0, "gratuit").when(F.col("price_usd") < 10, "< 10 $").when(F.col("price_usd") < 30, "10-30 $").otherwise("≥ 30 $"),
              "prix", ["gratuit", "< 10 $", "10-30 $", "≥ 30 $"])
t_early = taux(F.when(F.array_contains("genres", "Early Access"), "Early Access").when(F.array_contains("genres", "Indie"), "Indé (hors EA)").otherwise("Autres"), "statut")

fig, axes = plt.subplots(1, 4, figsize=(15, 3.6), sharey=True)
for ax, (t, nom) in zip(axes, [(t_lang, "langues"), (t_plat, "plateformes"), (t_prix, "prix"), (t_early, "statut")]):
    ax.bar(t[nom], t["% ≥ 100k propriétaires"], color="#8172b3")
    ax.set(title=f"Selon : {nom}", ylabel="% de jeux ≥ 100 000 propriétaires" if nom == "langues" else "")
    ax.tick_params(axis="x", rotation=20)
plt.tight_layout()
plt.show()
pd.concat({"langues": t_lang.set_index("langues"), "plateformes": t_plat.set_index("plateformes"),
           "prix": t_prix.set_index("prix"), "statut": t_early.set_index("statut")})
""")
lecture("popularite")

code("""
corr = df.filter(F.col("reviews") >= 50).select(
    F.corr(F.log1p("owners_mid"), F.col("n_langs")).alias("log(propriétaires) ~ langues"),
    F.corr(F.log1p("owners_mid"), F.col("n_platforms")).alias("log(propriétaires) ~ plateformes"),
    F.corr(F.log1p("owners_mid"), F.col("price_usd")).alias("log(propriétaires) ~ prix"),
    F.corr(F.col("positive_ratio"), F.log1p("owners_mid")).alias("avis positifs ~ log(propriétaires)"))
corr.select([F.round(c, 2).alias(c) for c in corr.columns]).show(truncate=False)
""")
lecture("correlations")

md("## 6. Conclusions pour Ubisoft")
lecture("conclusions")

nb["cells"] = C
nb["metadata"]["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
nbf.write(nb, "steam_eda.ipynb")
print("ok", len(C), "cellules")
