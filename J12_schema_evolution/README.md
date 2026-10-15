# CodeTober 2026 — J12 : Schema Evolution

**Concept :** faire évoluer le schéma d’entrée d’une pipeline ETL sans faire évoluer le schéma de sortie.  
**Temps visé :** 1 h 30 à 2 h 30, tests inclus.  
**Point de départ :** ton code du J11 (*Pipe Dreams*). Réutilisation autorisée et encouragée.

## 🎯 Objectif

Le fournisseur de commandes a renommé une colonne. Ta pipeline J11 doit accepter **deux versions compatibles** de `orders.csv`, produire **exactement le même schéma `sales`** dans SQLite et **refuser explicitement** les schémas qu'elle ne comprend pas.

Ce défi porte sur la **compatibilité de schéma**, pas sur la qualité des valeurs de chaque ligne.

## 📥 Entrées et sorties

| Fichier fourni | Usage |
|---|---|
| `data/catalog.json` | Référentiel produits, identique au J11 |
| `data/orders_v1.csv` | Version historique : colonne `quantity` |
| `data/orders_v2.csv` | Nouvelle version : colonne `units` au lieu de `quantity`, et colonne supplémentaire `sales_channel` |
| `data/orders_incompatible.csv` | Ni `quantity` ni `units` : incompatible |
| `data/orders_ambiguous.csv` | `quantity` **et** `units` : incompatible par convention, même si les valeurs coïncident |
| `data/orders_v3_bonus.csv` | Version destinée au 5/5 : `items_count` remplace la quantité et `campaign` est supplémentaire |

**Sortie :** une base SQLite contenant la table `sales` du J11, avec **exactement** ces 7 colonnes :

`order_id, order_date, product_id, product_name, quantity, unit_price_cents, total_cents`

La colonne `quantity` de sortie doit rester un **entier**, quelle que soit la version d’entrée. Les colonnes supplémentaires des sources ne sont pas chargées.

## ✅ Obligatoire — 4/5

1. **Deux schémas compatibles.** Accepter `orders_v1.csv` (`quantity`) et `orders_v2.csv` (`units`), sans modifier le nom ni les types attendus dans la table `sales`. Le reste de la logique J11 reste inchangé : seules les commandes `paid` dont le produit existe dans le catalogue sont chargées ; le prix vient du catalogue.
2. **Une seule interprétation par fichier.** Déterminer les colonnes disponibles avant de traiter ses commandes. Les champs `order_id`, `order_date`, `product_id`, `status` sont obligatoires ; **exactement un** des noms `quantity` ou `units` doit être présent. Les colonnes supplémentaires sont acceptées et ignorées.
3. **Échec explicite si incompatible.** Sur `orders_incompatible.csv` ou `orders_ambiguous.csv`, lever une erreur compréhensible, avec un code de sortie non nul ; **aucune vente de ce fichier ne doit être insérée**. Ce n'est pas une quarantaine ligne par ligne.
4. **Régression et rejouabilité.** Pour les versions v1 et v2, retrouver le même nombre de ventes et le même montant que sur le J11. Une seconde exécution sur les mêmes entrées ne doit pas créer de doublons.

**Liberté d'interface :** tu peux choisir un argument pour le fichier CSV, ou un répertoire avec un nom standard. Ne réécris pas un CLI complexe pour cet exercice.

## ⭐ Bonus 5/5 — Une troisième évolution, sans modifier le cœur ETL

Faire accepter `orders_v3_bonus.csv`, où `quantity` / `units` a été remplacé par `items_count`, **en ne modifiant qu'une définition centralisée de correspondances entre noms de colonnes** (dans le code ou dans un fichier de configuration). Il ne doit être nécessaire de modifier ni la transformation métier des ventes, ni la fonction de chargement SQLite, ni la boucle d'orchestration.

Les autres règles du 4/5 continuent de s'appliquer : il faut **exactement un nom de colonne quantité reconnu** par fichier ; les noms inconnus ne doivent pas être interprétés au hasard.

L'énoncé définit la propriété attendue ; à toi de choisir comment organiser la correspondance des schémas.

## 🧪 Exemples et résultats de contrôle

Pour chaque fichier **compatible**, exécute sur une base vide (ou vérifie l'état de la base après une relance sur les mêmes commandes). Les versions v1, v2 et v3 contiennent les mêmes commandes métier :

| Contrôle SQL / fonctionnel | Valeur attendue |
|---|---:|
| Lignes sources | 16 |
| `SELECT COUNT(*) FROM sales;` | 12 |
| `SELECT SUM(total_cents) FROM sales;` | 65 460 |
| Deuxième exécution sur la même source | 12 ventes, total inchangé |

**Exemple de correspondance :** si une commande comporte `units=2` en v2, la vente chargée doit contenir `quantity=2` en entier. `sales_channel` n'apparaît pas en sortie.

**Fichiers incompatibles :** l'erreur doit survenir sur le schéma, avant le chargement de la moindre commande du fichier. Pas de résultat partiel imputable à ce fichier.

## ♻️ Ce que tu peux reprendre du J11

- `get_catalog()`, `create_sales_table()` et `insert_row_in_sales()` ;
- la lecture progressive avec `csv.DictReader` ;
- le filtrage `status == "paid"`, la vérification du produit et les calculs de vente ;
- tes tests SQLite en mémoire et le contrôle de rejouabilité.

**Hors périmètre :** nouvelles règles de qualité, migration de la table cible, historique des versions, fichiers de rejet, logs et performance avancée. Aucun de ces éléments n'est requis pour le 4/5 ou le 5/5.

## 🧩 Idées de tests (à écrire toi-même)

- v1 et v2 produisent les mêmes ventes ;
- une colonne supplémentaire n'affecte pas le résultat ;
- les deux schémas incompatibles échouent sans insertion ;
- pour le 5/5, v3 produit aussi le même résultat sans modification de la transformation ni du chargement.
