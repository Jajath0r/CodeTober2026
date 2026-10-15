# CodeTober 2026 — J11 : Pipe Dreams 🐍

**Thème :** pipeline Extract → Transform → Load (ETL)  
**Temps visé :** environ 2 h (3 h maximum visées, tests compris)  
**Compétence principale :** séparer les étapes d'un traitement pour pouvoir les tester et les modifier indépendamment.

## 🎯 Objectif

Une boutique te fournit un fichier de commandes et un catalogue produits. Tu dois construire un petit pipeline qui **extrait** ces deux sources, **transforme** les commandes payées en ventes enrichies, puis **charge** les résultats dans une base SQLite.

**L'enjeu du jour n'est pas de refaire le moteur de qualité du J10 : c'est la séparation des étapes de l'ETL.**

## 📥 Entrées et sortie

| Fichier | Rôle |
|---|---|
| `data/orders.csv` | Commandes à traiter |
| `data/catalog.json` | Catalogue avec les prix unitaires en centimes |
| `sales.db` | Base SQLite **à produire** |

Tu peux choisir librement l'organisation de ton code et la façon de fournir les chemins (constantes, paramètres de fonction ou CLI). **Aucune interface CLI n'est exigée.**

La table cible `sales` doit contenir exactement les colonnes suivantes :

| Colonne | Type SQLite | Sens |
|---|---|---|
| `order_id` | `TEXT PRIMARY KEY` | Identifiant unique de la commande |
| `order_date` | `TEXT` | Date source (format `YYYY-MM-DD`) |
| `product_id` | `TEXT` | Référence produit |
| `product_name` | `TEXT` | Nom provenant du catalogue |
| `quantity` | `INTEGER` | Quantité commandée |
| `unit_price_cents` | `INTEGER` | Prix unitaire provenant du catalogue |
| `total_cents` | `INTEGER` | Montant total de la ligne, en centimes |

## ✅ Travail demandé — 4/5

1. **Extract :** lire `orders.csv` et `catalog.json`. La lecture des sources doit pouvoir être utilisée indépendamment des étapes suivantes.
2. **Transform :** ne conserver que les commandes dont `status == "paid"` ; pour chacune, enrichir la commande avec `product_name` et `unit_price_cents` issus du catalogue et calculer `total_cents = quantity × unit_price_cents`.
3. **Load :** enregistrer les ventes transformées dans la table SQLite `sales`, avec les colonnes et types indiqués ci-dessus.
4. **Séparation des responsabilités :** les étapes extraction, transformation et chargement doivent être suffisamment indépendantes pour que tu puisses tester la transformation **sans ouvrir de fichier ni de base de données**.
5. **Rejouabilité :** réexécuter le pipeline sur les mêmes sources ne doit ni ajouter de lignes en double ni changer le résultat final.

**Données garanties pour ce défi :** les fichiers existent, leurs structures sont correctes, les dates sont au bon format, les quantités sont des entiers strictement positifs, les `order_id` sont uniques et tous les `product_id` sont présents dans le catalogue. Tu n'as **aucune règle de validation métier supplémentaire** à implémenter.

## ⭐ Contrainte supplémentaire — 5/5

**Consommation mémoire bornée côté commandes :** ton traitement doit rester utilisable avec un fichier de commandes très volumineux, sans conserver simultanément en mémoire toutes les commandes extraites ou toutes les ventes transformées. Le catalogue peut, lui, être chargé en mémoire.

La propriété est imposée, **pas la manière de l'obtenir**.

## 🧪 Contrôles rapides

| Vérification | Résultat attendu |
|---|---:|
| Commandes source | 16 |
| Commandes payées chargées dans `sales` | 12 |
| Commandes écartées (`cancelled` ou `pending`) | 4 |
| `SUM(total_cents)` dans `sales` | 65 460 |
| Lignes dans `sales` après une deuxième exécution identique | 12 |

Deux exemples de transformation :

| Entrée (`orders.csv`) | Résultat dans `sales` |
|---|---|
| `ORD-001`, `P-101`, quantité `2`, `paid` | `product_name = Notebook`, `unit_price_cents = 850`, `total_cents = 1700` |
| `ORD-003`, `P-102`, quantité `3`, `cancelled` | Aucune ligne chargée |

**Tests minimaux conseillés :** une commande payée bien enrichie, une commande non payée écartée, et deux exécutions successives donnant le même état final. Tu peux utiliser `pytest` ou d'autres assertions : aucune bibliothèque de test particulière n'est obligatoire.

## 🔧 Réutilisation autorisée

Tu peux reprendre sans restriction tes fonctions de lecture CSV/JSON, de connexion SQLite, de création de table ou tes utilitaires de test des jours précédents. **Aucun recodage de ces briques n'est demandé.**

Tu peux aussi choisir librement les noms de tes fonctions, ton arborescence et tes structures de données intermédiaires. Je n'évaluerai pas une architecture cachée : je vérifierai les cinq propriétés du 4/5 ci-dessus, puis la contrainte du 5/5 si tu la tentes.

## Hors périmètre

Pas de gestion de lots, de quarantaine, de rapport JSON, de seuils de qualité, d'API, de journalisation avancée, de reprise après crash ni de gestion des produits inconnus. **Ces fonctionnalités ne sont pas attendues pour le J11.**
