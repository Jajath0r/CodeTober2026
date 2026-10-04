# 🎃 CodeTober 2026 — Jour 4

## 🔗 Join Me If You Can

**Thème :** jointures, enrichissement de données et intégrité référentielle  
**Temps cible :** 45 min à 2 h  
**Technologie principale :** Python

---

## 📖 Contexte

Deux systèmes alimentent ton pipeline.

Le premier fournit un référentiel clients :

`customers.csv`

Le second fournit les commandes passées :

`orders.csv`

On souhaite produire un dataset de commandes enrichies avec les informations du client correspondant.

Évidemment, les deux systèmes ne sont pas parfaitement synchronisés.

---

## 📥 Données

### `customers.csv`

| Champ | Description |
|---|---|
| `customer_id` | Identifiant du client |
| `name` | Nom |
| `country` | Pays |
| `segment` | Segment commercial |

### `orders.csv`

| Champ | Description |
|---|---|
| `order_id` | Identifiant de commande |
| `customer_id` | Client ayant passé la commande |
| `order_date` | Date de commande |
| `amount` | Montant |

---

## 🎯 Mission

Construire un programme qui rapproche les deux sources à partir de `customer_id`.

Il doit produire :

```text
output/
├── enriched_orders.csv
├── unmatched_orders.csv
├── customers_without_orders.csv
└── join_report.json
```

### `enriched_orders.csv`

Toutes les commandes pour lesquelles un client correspondant a été trouvé.

Chaque ligne doit contenir :

- les informations de la commande ;
- `name` ;
- `country` ;
- `segment`.

### `unmatched_orders.csv`

Les commandes dont le `customer_id` n'existe pas dans le référentiel clients.

Elles ne doivent **pas disparaître silencieusement** du pipeline.

### `customers_without_orders.csv`

Les clients du référentiel pour lesquels aucune commande n'a été trouvée.

### `join_report.json`

Il doit contenir au minimum :

- nombre de clients ;
- nombre de commandes ;
- nombre de commandes enrichies ;
- nombre de commandes sans client correspondant ;
- nombre de clients sans commande ;
- montant total des commandes enrichies ;
- montant total des commandes non rapprochées.

La structure exacte reste libre.

---

## ⚠️ Contraintes

### 1. Pas de pandas

Oui, je te vois venir. 😇

Le but aujourd'hui est de comprendre ce qui se passe réellement lors d'une jointure, pas d'écrire :

`merge(...)`

et de rentrer à la maison.

Tu peux utiliser la bibliothèque standard Python.

### 2. Pas de recherche naïve ligne par ligne

Une solution consistant, pour **chaque commande**, à reparcourir l'intégralité de `customers.csv` pour retrouver son client est hors sujet.

Imagine que demain tu reçoives :

```text
5 000 000 commandes
500 000 clients
```

Ton architecture doit éviter ce type de recherche répétitive.

### 3. Une source peut être chargée en mémoire

Contrairement au J2, tu as le droit de charger **l'une des deux sources** en mémoire si ton architecture le nécessite.

À toi de déterminer laquelle et sous quelle forme.

L'autre doit pouvoir être traitée progressivement.

### 4. Les anomalies font partie du résultat

Une absence de correspondance n'est pas une exception Python et ne doit pas faire planter le traitement.

C'est une situation métier à identifier et à reporter.

---

## 🏁 Definition of Done

Le défi est terminé lorsque :

- les commandes rapprochées sont correctement enrichies ;
- les commandes orphelines sont conservées séparément ;
- les clients sans commande sont identifiés ;
- le rapport contient les métriques demandées ;
- aucune recherche complète du référentiel n'est effectuée pour chaque commande ;
- ton programme fonctionnerait selon le même principe avec des fichiers beaucoup plus volumineux.

---

## 🧠 Objectifs pédagogiques

Ce défi vise notamment à travailler :

- les stratégies de jointure ;
- la différence entre une recherche séquentielle et un accès indexé ;
- les notions de clé et d'intégrité référentielle ;
- la conservation des lignes non appariées ;
- le choix des structures de données ;
- le raisonnement sur la complexité d'un traitement.

Tu connais déjà les jointures.

Le défi est de construire toi-même le mécanisme qui se cache derrière.

**CodeTober 2026 — Data Engineering with Python 🐍🎃**