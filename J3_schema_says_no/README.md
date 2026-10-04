# 🎃 CodeTober 2026 — Jour 3

## 🚫 Schema Says No

**Thème :** data contracts, validation de schéma et événements  
**Temps cible :** 45 min à 2 h  
**Technologie principale :** Python  
**Bibliothèques :** libres, à condition qu'elles soient gratuites et installables dans ton environnement

---

## 📖 Contexte

Ton équipe commence à recevoir des événements provenant de plusieurs applications.

Tous arrivent dans le même flux et partagent une structure générale, mais ils ne représentent pas les mêmes objets métier.

Trois types d'événements sont actuellement autorisés :

- `order_created`
- `payment_received`
- `customer_updated`

Jusqu'ici, les producteurs se contentaient d'envoyer « quelque chose qui ressemble au bon format ».

Étonnamment, ça finit mal.

Ton objectif est donc de mettre en place un **contrat de données explicite** permettant de déterminer si chaque événement peut entrer dans le pipeline.

---

## 📥 Données

Le fichier `events.csv` contient les colonnes :

| Champ | Description |
|---|---|
| `event_id` | Identifiant unique de l'événement |
| `event_type` | Type d'événement |
| `event_version` | Version du contrat |
| `timestamp` | Date de création |
| `customer_id` | Client concerné |
| `amount` | Montant éventuel |
| `currency` | Devise éventuelle |
| `country` | Pays éventuel |
| `metadata` | Métadonnées JSON |

Toutes les colonnes existent dans le CSV, mais **toutes ne sont pas obligatoires pour tous les événements**.

---

## 📜 Contrat commun

Tout événement doit respecter les règles suivantes :

- `event_id` : chaîne non vide ;
- `event_type` : l'un des trois types autorisés ;
- `event_version` : entier `1` ou `2` ;
- `timestamp` : format `YYYY-MM-DD HH:MM:SS` ;
- `customer_id` : chaîne non vide ;
- `metadata` : JSON valide représentant un objet.

---

## 📦 `order_created`

En plus du contrat commun :

- `amount` est obligatoire ;
- `amount` doit être un nombre strictement positif ;
- `currency` est obligatoire et doit être `EUR`, `USD` ou `GBP` ;
- `country` est obligatoire et doit être un code sur exactement deux lettres.

---

## 💳 `payment_received`

Même contrat métier que `order_created` pour :

- `amount` ;
- `currency` ;
- `country`.

---

## 👤 `customer_updated`

Pour cet événement :

- `amount` peut être vide ;
- `currency` peut être vide ;
- `country` peut être vide.

Ces champs ne doivent pas provoquer de rejet lorsqu'ils sont absents.

---

## 🎯 Mission

Construire un programme capable de valider chaque événement par rapport au contrat correspondant à son `event_type`.

Le programme doit produire :

```text
output/
├── valid_events.csv
├── rejected_events.csv
└── validation_report.json
```

### `valid_events.csv`

Contient les événements respectant leur contrat.

### `rejected_events.csv`

Contient les événements rejetés ainsi qu'une colonne :

```text
validation_errors
```

Un événement peut violer plusieurs règles : **toutes les erreurs détectées doivent être reportées**.

### `validation_report.json`

Il doit contenir au minimum :

- nombre total d'événements ;
- nombre d'événements valides ;
- nombre d'événements rejetés ;
- nombre d'événements par `event_type` ;
- nombre d'erreurs par règle ou champ.

La structure exacte du JSON est libre.

---

## ⚠️ Contraintes

Cette fois, l'objectif n'est pas simplement d'écrire une succession de `if`.

Le **contrat doit être identifiable dans ton architecture** : en lisant ton projet, on doit pouvoir comprendre quelles règles définissent un événement valide sans devoir reconstituer mentalement toute la logique du pipeline.

La manière de représenter ce contrat fait partie du défi.

Tu peux utiliser uniquement Python standard ou chercher une bibliothèque adaptée si tu penses que cela améliore ta solution.

Il n'y a pas de choix technologique imposé.

---

## 🏁 Definition of Done

Le défi est terminé lorsque :

- chaque événement est confronté au contrat correspondant ;
- plusieurs erreurs peuvent être détectées sur une même ligne ;
- les événements valides et invalides sont séparés ;
- le rapport de validation est généré ;
- ajouter ou modifier une règle métier ne nécessite pas de réécrire tout le pipeline.

### Bonus

Écrire les tests **pendant le développement**, voire expérimenter sur une partie du projet le cycle :

```text
RED → GREEN → REFACTOR
```

Le TDD est une expérimentation proposée, pas une contrainte du défi.

---

## 🧠 Objectifs pédagogiques

Ce défi vise notamment à explorer :

- les data contracts ;
- la validation de schémas ;
- les règles conditionnelles selon le type de données ;
- la séparation entre contrat, validation et traitement ;
- la gestion structurée des erreurs ;
- l'évolutivité d'un système de validation.

**CodeTober 2026 — Data Engineering with Python 🐍🎃**