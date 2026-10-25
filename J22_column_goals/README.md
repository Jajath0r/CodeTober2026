# CodeTober 2026 — J22 : Column Goals 🏛️

**Thème :** Parquet, stockage colonnaire, types, compression, partitionnement physique.  
**Durée indicative :** 1 h 30 à 2 h 30.  
**Dépendance conseillée :** `duckdb` (déjà découvert au J21). Aucune dépendance Docker.

## Contexte

L'équipe reçoit chaque jour un export CSV de transactions commerciales. Les analystes souhaitent des données typées, compactes et organisées pour pouvoir consulter seulement un mois et un pays, sans devoir toujours reparcourir toutes les transactions.

Le fichier fourni, `data/sales.csv`, contient **1 200 transactions** réparties sur deux mois et trois pays. Chaque ligne est une transaction indépendante (identifiant unique). Les valeurs monétaires sont exprimées en centimes.

| Champ | Signification | Type logique attendu dans Parquet |
|---|---|---|
| `transaction_id` | Identifiant de transaction | texte |
| `order_date` | Date de la transaction | date (pas une simple chaîne) |
| `country` | Code pays | texte |
| `product_id` | Identifiant produit | texte |
| `status` | `completed`, `pending`, `cancelled` | texte |
| `quantity` | Quantité | entier |
| `unit_price_cents` | Prix unitaire en centimes | entier |

## Mission — 4/5 (fonctionnel)

Construire une commande exécutable, par exemple :

```bash
python main.py --input data/sales.csv --output-dir output --month 2026-10 --country FR
```

La commande doit :

1. **Ingestion et validation.** Lire le CSV, vérifier que les colonnes obligatoires sont présentes et que les données essentielles sont convertibles aux types attendus. Une erreur bloquante doit arrêter la commande clairement, plutôt que produire un résultat silencieusement incohérent.
2. **Stockage colonne.** Écrire les données dans `output/lake/` au format **Parquet compressé**, avec les types logiques ci-dessus. Le jeu complet, y compris les statuts non `completed`, doit être préservé.
3. **Partitionnement physique.** Organiser les fichiers Parquet selon **deux dimensions : mois de la transaction (`order_month`, format `YYYY-MM`) et `country`**. Les données de plusieurs mois/pays doivent résider dans des partitions physiquement distinctes ; un CSV renommé `.parquet` ou un fichier unique ne suffit pas. La colonne de partition `order_month` est dérivée de `order_date`.
4. **Synthèse analytique.** Générer `output/monthly_summary.csv` avec les colonnes exactement dans cet ordre : `order_month,country,transactions_count,items_sold,revenue_cents`. Une ligne par couple (mois, pays), triée par mois puis pays croissants. **Seules les transactions `completed`** contribuent à cette synthèse ; `revenue_cents = somme(quantity × unit_price_cents)`.
5. **Lecture ciblée.** Générer `output/selected_sales.csv`, contenant **toutes les transactions** correspondant à `--month` et `--country`, quels que soient leurs statuts. Colonnes dans l'ordre du CSV source, tri par `transaction_id` croissant. Ces résultats doivent être lus **depuis les fichiers Parquet produits**, pas directement depuis `sales.csv`. Une combinaison mois/pays sans données produit uniquement l'en-tête.
6. **Relançabilité.** Deux exécutions avec les mêmes paramètres et le même fichier doivent produire les mêmes lignes, sans dupliquer les transactions dans le lac.

Le dossier de sortie doit être créé si nécessaire. La solution peut rester organisée en modules (`extract`, `transform`, `load`, `main`) mais ce découpage n'est pas obligatoire.

## Bonus — 5/5 (exigences annoncées dès maintenant)

Démontrer par **tests automatisés** les trois propriétés suivantes :

1. **Fidélité des types et valeurs :** après aller-retour CSV → Parquet → lecture, les dates restent des dates, les nombres des nombres, et les identifiants/montants sont inchangés (y compris des lignes non `completed`).
2. **Sélectivité physique :** une requête ciblée sur un mois et un pays n'a pas besoin de lire les fichiers d'une partition étrangère au filtre. Le test doit apporter une preuve observable de cette indépendance, et pas seulement vérifier que le résultat final est filtré.
3. **Idempotence :** une relance ne crée ni doublons métier ni écarts de synthèse et n'accumule pas de versions superflues des mêmes transactions.

**Barème fixé :** 4/5 si tous les critères fonctionnels sont respectés ; 5/5 si les trois propriétés ci-dessus sont en plus démontrées automatiquement. Les tests de bonus ne doivent pas dépendre des fichiers préexistants de ton dossier `output/`.

## Livrables

- Scripts Python exécutables et éventuel `requirements.txt`.
- `output/lake/` contenant les partitions Parquet compressées.
- `output/monthly_summary.csv` et `output/selected_sales.csv`.
- Pour le bonus : tests pytest exécutables.

## Quelques questions pour guider ton exploration (sans imposer l'implémentation)

- Pourquoi est-il intéressant d'avoir une colonne `DATE` plutôt qu'une chaîne ISO ?
- Quelle différence entre une **partition physique** et un simple `WHERE` SQL ?
- Comment éviter que `pending`/`cancelled` contaminent la synthèse sans les supprimer du lac ?
- Comment vérifier que les fichiers produits sont vraiment au format Parquet et compressés ?

Le défi porte sur les **propriétés obtenues**, pas sur le choix d'une API spécifique.
