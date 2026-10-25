# J22 — Plan de tests (sans solution)

Utilise un dossier de sortie neuf, puis lance :

```bash
python main.py --input data/sales.csv --output-dir output --month 2026-10 --country FR
```

## Vérifications fonctionnelles

- Le lac contient bien des fichiers Parquet compressés et des partitions physiquement distinctes pour chaque combinaison présente de `order_month` et `country` (2 mois × 3 pays = **6 combinaisons**).
- Tous les **1 200** `transaction_id` de la source sont conservés **une seule fois** dans le lac, indépendamment du statut.
- Le schéma lu depuis le Parquet contient une vraie date et des colonnes quantitatives numériques.
- `monthly_summary.csv` est égal à `reference/expected_monthly_summary.csv` (6 lignes hors en-tête).
- `selected_sales.csv` est égal à `reference/expected_selected_sales_2026-10_FR.csv` (ordre et valeurs ; compare les dates de manière cohérente si ton lecteur les type automatiquement).
- Un autre couple valide, puis un couple sans donnée, donnent respectivement des résultats filtrés et un fichier avec en-tête seul.
- Une deuxième exécution avec la même destination ne crée pas de doublons.
- Une entrée invalide (colonne manquante, date erronée, quantité non numérique) est refusée explicitement.

## Bonus : stratégie de test

1. Conçois un petit CSV synthétique comprenant deux mois, deux pays et plusieurs statuts. Compare les données lues depuis Parquet aux originales **avec contrôle de types**.
2. Fais varier une partition non sélectionnée pour démontrer que la sélection demandée n'a pas besoin de son contenu. Un simple `WHERE` sur toute la donnée **n'est pas une preuve** de lecture sélective.
3. Lance deux fois l'ingestion vers une destination temporaire, puis compare identifiants, nombre total de transactions, rapports et organisation du lac.

Tu peux utiliser `pytest` et `tmp_path` comme au J20 et au J21.

## Note sur la référence

Le prix catalogue n'intervient pas ici. Le chiffre d'affaires est calculé exclusivement depuis `quantity` et `unit_price_cents` de chaque transaction `completed`.
