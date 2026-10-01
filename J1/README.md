# 🎃 CodeTober 2026 — Jour 1

## 🧹 The Dirty CSV

**Thème :** ingestion, nettoyage et qualité de données  
**Temps cible :** 45 min à 1 h 15  
**Temps maximum indicatif :** 2 h  
**Technologie principale :** Python

---

## 📖 Contexte

Une application interne exporte quotidiennement les transactions d'une plateforme sous forme de CSV.

Évidemment, puisque nous vivons dans le monde merveilleux de l'intégration de données, le fichier est *presque* propre.

Et « presque propre » est une autre manière de dire :

> Bienvenue dans ton problème.

L'objectif est de construire le premier maillon du pipeline CodeTober : un programme capable d'ingérer ce fichier, de nettoyer les données qui peuvent l'être sans ambiguïté, d'isoler les données invalides et de produire un rapport de qualité.

---

## 📥 Données d'entrée

Le fichier `transactions.csv` contient les colonnes suivantes :

| Colonne | Signification | Format attendu |
|---|---|---|
| `transaction_id` | Identifiant unique de transaction | chaîne non vide |
| `timestamp` | Date de transaction | `YYYY-MM-DD HH:MM:SS` |
| `customer_id` | Identifiant client | chaîne non vide |
| `country` | Pays | code ISO sur 2 lettres |
| `amount` | Montant | nombre décimal ≥ 0 |
| `currency` | Devise | `EUR`, `USD` ou `GBP` |
| `status` | État de la transaction | `SUCCESS`, `FAILED` ou `PENDING` |

Le fichier réel peut notamment contenir :

- des valeurs manquantes ;
- des doublons ;
- des espaces parasites ;
- des différences de casse ;
- des nombres mal formés ;
- des valeurs invalides.

Une ligne incorrecte ne doit jamais faire planter le traitement complet.

---

## 🎯 Mission

Écrire un programme Python prenant en entrée :

```text
transactions.csv
```

et produisant :

```text
output/
├── transactions_clean.csv
├── transactions_rejected.csv
└── quality_report.json
```

### `transactions_clean.csv`

Ce fichier contient uniquement les lignes valides.

Les données doivent être normalisées lorsque la correction est non ambiguë.

Exemples :

```text
" eur "     → "EUR"
"fr"        → "FR"
" success " → "SUCCESS"
```

Une donnée ambiguë ou réellement invalide ne doit pas être réparée arbitrairement.

---

### `transactions_rejected.csv`

Ce fichier contient les lignes refusées.

Les données rejetées ne doivent pas être perdues et une colonne supplémentaire doit indiquer la ou les raisons du rejet :

```text
rejection_reason
```

Une même ligne peut cumuler plusieurs motifs de rejet.

---

### `quality_report.json`

Le traitement doit également produire un rapport de qualité contenant au minimum :

```json
{
    "total_rows": 0,
    "valid_rows": 0,
    "rejected_rows": 0,
    "duplicate_rows": 0,
    "rejection_reasons": {}
}
```

Des métriques supplémentaires peuvent être ajoutées si elles semblent pertinentes.

---

## 🔁 Gestion des doublons

`transaction_id` doit être unique.

La première occurrence d'un identifiant est traitée normalement. Toute occurrence suivante du même `transaction_id` doit être rejetée comme doublon.

La détection doit être effectuée sur l'identifiant normalisé.

Exemple :

```text
TXN-123
" TXN-123 "
```

Ces deux valeurs représentent le même identifiant.

`duplicate_rows` représente le nombre de lignes rejetées comme doublons.

---

## ⚠️ Contraintes

1. Une ligne invalide doit être rejetée et non silencieusement corrigée lorsque la correction est ambiguë.
2. Une anomalie sur une ligne ne doit pas interrompre le traitement du fichier.
3. Le programme doit fonctionner avec un autre CSV respectant le même contrat.
4. Les différentes causes de rejet doivent pouvoir être identifiées.
5. L'architecture du programme est libre : fonctions, modules, classes, bibliothèque `csv`, `pandas`, etc.

---

## 🏁 Definition of Done

Le défi est terminé lorsqu'un lancement du programme sur le fichier brut produit sans erreur :

- un fichier contenant uniquement les transactions valides et normalisées ;
- un fichier contenant les transactions rejetées et leurs motifs de rejet ;
- un rapport JSON résumant la qualité des données.

### Bonus

Permettre l'exécution depuis la ligne de commande :

```bash
python main.py transactions.csv output/
```

---

## 🧠 Objectifs pédagogiques

Ce premier défi permet notamment de travailler :

- la lecture et l'écriture de CSV ;
- la validation de données ;
- la normalisation ;
- la gestion des erreurs ;
- la détection de doublons ;
- la séparation des responsabilités dans un petit pipeline ;
- la production de métriques de qualité.

L'objectif n'est pas de construire immédiatement un pipeline parfait ou « production ready », mais de proposer une solution fonctionnelle, compréhensible et améliorable.

---

**CodeTober 2026 — Data Engineering with Python 🐍🎃**