# 🎃 CodeTober 2026 — Jour 5

## 🗂️ Divide & Conquer

**Thème :** partitionnement de données  
**Temps cible :** 45 min à 2 h  
**Technologie principale :** Python standard

---

## 📖 Contexte

Ton pipeline reçoit quotidiennement un fichier contenant des événements de commandes provenant de plusieurs régions.

Le volume commence à augmenter et les consommateurs downstream n'ont pas tous besoin de l'intégralité du dataset.

L'équipe décide donc de stocker les données sous forme **partitionnée**, afin de pouvoir cibler uniquement les données pertinentes lors des traitements suivants.

Ton fichier d'entrée contient notamment :

- un timestamp ;
- une région ;
- les informations de la commande.

Ton objectif est de construire toi-même un petit mécanisme de partitionnement.

---

## 📥 Données

Le fichier `orders_raw.csv` contient :

| Champ | Description |
|---|---|
| `order_id` | Identifiant de commande |
| `customer_id` | Identifiant client |
| `event_timestamp` | Timestamp de l'événement |
| `amount` | Montant |
| `currency` | Devise |
| `status` | Statut de la commande |
| `region` | Région source |
| `channel` | Canal de commande |

---

## 🎯 Mission

À partir du fichier source, produire un dataset partitionné selon :

**date → région**

Une ligne :

`2026-10-02 14:32:17 | eu-west`

doit donc être stockée dans la partition correspondant au **2 octobre 2026** et à la région **eu-west**.

La manière exacte d'organiser les répertoires et de nommer les fichiers fait partie de tes choix d'implémentation.

---

## ⚠️ Contraintes

### Une seule lecture du fichier source

Le fichier d'entrée ne doit être parcouru qu'une seule fois.

Il est donc hors sujet de faire :

`je parcours le fichier pour eu-west`, puis `je le reparcours pour eu-central`, etc.

### Pas de chargement complet en mémoire

Les lignes doivent pouvoir être traitées progressivement.

### Pas de doublons dans les données finales

Le fichier contient quelques lignes parfaitement dupliquées.

Une même ligne ne doit apparaître qu'une fois dans le dataset partitionné.

### Ne pas coder les partitions en dur

Ton programme ne connaît pas à l'avance :

- les dates présentes ;
- les régions présentes ;
- le nombre de partitions nécessaires.

Si demain apparaît :

`2026-10-17 | ca-east`

le pipeline doit pouvoir créer la partition correspondante sans modification du code.

---

## 📊 Rapport

Produire également :

`partition_report.json`

contenant au minimum :

- nombre de lignes lues ;
- nombre de doublons ignorés ;
- nombre de lignes écrites ;
- nombre total de partitions créées ;
- nombre de lignes par partition.

La représentation des partitions dans le JSON est libre.

---

## 🏁 Definition of Done

Le défi est terminé lorsque :

- le fichier source n'est lu qu'une fois ;
- les lignes sont réparties dans les bonnes partitions ;
- les partitions sont découvertes dynamiquement ;
- les doublons sont éliminés ;
- le fichier complet n'est jamais chargé en mémoire ;
- le rapport est généré ;
- l'ajout d'une nouvelle date ou région ne nécessite aucune modification du programme.

---

## 🧠 Objectifs pédagogiques

Ce défi vise notamment à explorer :

- le **partitionnement physique des données** ;
- la différence entre organisation logique et stockage physique ;
- le routage dynamique des lignes ;
- la gestion de plusieurs destinations pendant un traitement ;
- la déduplication dans un traitement streaming ;
- les compromis entre mémoire, I/O et organisation des données.

Tu construis aujourd'hui avec des CSV un mécanisme très simple, mais le concept derrière sera réutilisable lorsque nous irons vers des formats et outils beaucoup plus typiques du Data Engineering.

**CodeTober 2026 — Data Engineering with Python 🐍🎃**