# CodeTober 2026 — J21 : Duck Season 🦆

**Thème :** exploration analytique locale avec DuckDB  
**Durée indicative :** 1 h 30 à 2 h 30  
**Objectif :** traiter des données multi-tables avec un moteur SQL analytique, sans convertir l’intégralité des CSV en objets Python.

## Contexte

Tu travailles sur un export de commandes d’une boutique B2B. L’équipe commerciale veut trois rapports fiables à partir des commandes, des lignes de commande et d’un référentiel produits. Le traitement doit être relançable sur un nouveau jeu de fichiers sans modifier la logique de calcul.

## Fichiers fournis

- `data/orders.csv` : `order_id`, `order_date` (YYYY-MM-DD), `country`, `status` ; une ligne par commande.
- `data/order_items.csv` : `item_id`, `order_id`, `product_id`, `quantity`, `unit_price_cents` ; plusieurs lignes possibles par commande.
- `data/products.csv` : `product_id`, `product_name`, `category`, `unit_price_cents` ; prix catalogue indicatif.

Les clés sont cohérentes dans les fichiers fournis. Les montants sont des **centimes entiers**. **Le prix de vente à utiliser est `order_items.unit_price_cents`, jamais le prix courant de `products`.**

## Mission — 4/5 (fonctionnel)

Construire une commande exécutable, par exemple :

```bash
python main.py --data-dir data --output-dir output
```

Le nom du script et les options peuvent varier, mais le programme doit prendre un répertoire d'entrée et un répertoire de sortie en paramètres et produire ces trois fichiers CSV :

1. **`daily_sales.csv`** : colonnes `order_date,orders_count,items_sold,revenue_cents`. Une ligne par journée ayant au moins une vente. Trier les dates dans l'ordre croissant. `orders_count` = nombre de **commandes distinctes** ; `items_sold` = somme des quantités ; `revenue_cents` = somme de `quantity × unit_price_cents`.
2. **`category_sales.csv`** : colonnes `category,items_sold,revenue_cents`. Une ligne par catégorie vendue. Trier par `revenue_cents` décroissant puis `category` croissant.
3. **`top_products.csv`** : colonnes `product_id,product_name,items_sold,revenue_cents`. Les **5 produits** générant le plus de chiffre d'affaires, triés par chiffre d'affaires décroissant puis `product_id` croissant.

**Règles communes :**

- Seules les commandes de statut `completed` comptent. `cancelled` et `pending` sont exclus **dans les trois rapports**.
- Une commande avec plusieurs lignes ne doit être comptée qu'une fois dans `orders_count`.
- Les montants doivent rester des entiers en centimes, sans arrondi flottant.
- Utiliser **DuckDB et SQL comme moteur de calcul** ; ne pas reconstruire les jointures / agrégations en parcourant toutes les lignes CSV avec des boucles Python, pandas ou dictionnaires d'agrégation.
- Les CSV de sortie doivent contenir les en-têtes exacts ci-dessus. Créer le dossier de sortie si nécessaire. Une seconde exécution sur les mêmes entrées doit réécrire des résultats identiques, sans doublons accumulés.
- Écrire `NOTES.md` (quelques paragraphes) expliquant **deux différences concrètes** entre ce travail sous DuckDB et un traitement équivalent en Python, dont une portant sur la circulation ou le chargement des données.

Les résultats attendus sur les fixtures fournies figurent dans `reference/`. Ils servent à vérifier les valeurs, pas à dicter les requêtes.

## Bonus — 5/5 (exigences annoncées dès maintenant)

Démontrer par **tests automatisés** les propriétés suivantes, en plus du fonctionnel :

- Une commande possédant plusieurs lignes reste comptée **une fois** par jour, sans perdre ses quantités ni son montant.
- Les commandes `cancelled` et `pending` n'affectent **aucun** des trois rapports, même si leurs lignes ont des montants très élevés.
- Un ex æquo sur le chiffre d'affaires des produits ne rend pas l'ordre des résultats dépendant de l'ordre physique des lignes d'entrée.

Tu choisis le mécanisme de test et la façon de créer de petites fixtures adversariales. **Le bonus porte sur les propriétés vérifiées, pas sur un outil ni une architecture imposés.**

## Contraintes et limites

- Python 3.11+ ; bibliothèque externe **`duckdb`** (`python -m pip install duckdb`).
- Pas de Docker, pas de serveur SQL, pas de pandas requis.
- Tu peux conserver le reste en bibliothèque standard.
- Pas besoin de conserver une base DuckDB sur disque : le besoin est un calcul local reproductible.
- L'objectif est la compréhension, pas une performance chronométrée ; les données sont modestes, mais l'architecture doit laisser les opérations tabulaires au moteur SQL.

## Questions de réflexion (pas de note supplémentaire)

1. Pourquoi un `JOIN` entre commandes et lignes peut-il gonfler artificiellement le nombre de commandes ?
2. Pourquoi conserver un prix sur la ligne de commande alors qu'il existe déjà dans la table produits ?
3. Dans quels cas préférerais-tu DuckDB à SQLite, et inversement, sur les défis J17–J21 ?

**Le 4/5 est obtenu en satisfaisant la mission. Le 5/5 exige en plus les tests des trois propriétés annoncées.** Aucune autre contrainte bonus ne sera ajoutée en cours de route.
