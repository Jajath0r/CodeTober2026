: # 🎃 CodeTober 2026 — Jour 2

## 📦 Chunk Me If You Can

**Thème :** traitement de gros volumes, streaming et agrégation  
**Temps cible :** 45 min à 2 h  
**Technologie principale :** Python

---

## 📖 Contexte

Le pipeline du Jour 1 fonctionnait très bien avec quelques dizaines de transactions.

Évidemment, quelqu'un a vu ça fonctionner et en a immédiatement conclu :

> « Super. On peut lui donner les logs de toute la plateforme alors. »

Tu récupères maintenant un export de logs d'appels API contenant plusieurs centaines de milliers de lignes.

Cette fois, une contrainte supplémentaire apparaît :

**tu ne dois pas charger l'intégralité du fichier en mémoire.**

Ton programme doit parcourir progressivement les données et construire des statistiques globales au fur et à mesure.

---

## 📥 Données d'entrée

Le fichier `api_logs.csv` contient :

| Colonne | Description |
|---|---|
| `timestamp` | Date et heure de la requête |
| `request_id` | Identifiant de la requête |
| `service` | Service appelé |
| `endpoint` | Endpoint appelé |
| `method` | Méthode HTTP |
| `status_code` | Code HTTP retourné |
| `response_time_ms` | Temps de réponse en millisecondes |
| `payload_size_bytes` | Taille de la réponse |

Pour ce défi, **considère le fichier comme valide** : pas besoin de refaire le travail de nettoyage du J1.

---

## 🎯 Mission

Écrire un programme Python qui analyse `api_logs.csv` **sans charger tout le fichier en mémoire** et produit :

```text
output/
└── report.json
```

Le rapport doit contenir au minimum :

### Statistiques générales

- nombre total de requêtes ;
- nombre de réponses `2xx` ;
- nombre de réponses `4xx` ;
- nombre de réponses `5xx` ;
- temps de réponse moyen global.

### Statistiques par service

Pour chaque service :

- nombre de requêtes ;
- temps de réponse moyen ;
- nombre de réponses `5xx`.

### Top 10 des requêtes les plus lentes

Pour chacune :

- `request_id` ;
- service ;
- endpoint ;
- temps de réponse.

Le classement doit aller de la requête la plus lente à la moins lente.

---

## ⚠️ Contrainte principale

Le fichier ne doit **jamais être chargé intégralement en mémoire**.

Autrement dit, une approche consistant à faire quelque chose comme :

```python
rows = list(reader)
```

puis à traiter `rows` est hors sujet.

Même principe si tu utilises une bibliothèque : lire tout le DataFrame d'un coup contournerait le problème au lieu de le résoudre.

Ton programme doit pouvoir, conceptuellement, traiter de la même manière un fichier de plusieurs gigaoctets.

---

## 🏁 Definition of Done

Le défi est terminé lorsque :

- le fichier est traité progressivement ;
- les statistiques globales sont correctes ;
- les statistiques par service sont correctes ;
- le top 10 est correct ;
- `report.json` est produit ;
- la quantité de mémoire nécessaire au traitement ne croît pas proportionnellement au nombre de lignes du fichier.

### Bonus

Permettre :

```bash
python main.py api_logs.csv output/
```

Et si tu veux aller plus loin après avoir terminé le cœur du défi, tu pourras mesurer ou comparer différentes stratégies de traitement.

Mais ce n'est pas nécessaire pour considérer le J2 terminé.

---

## 🧠 Objectifs pédagogiques

Ce défi vise notamment à travailler :

- le traitement incrémental de données ;
- la différence entre stockage et agrégation ;
- la consommation mémoire d'un pipeline ;
- le calcul de métriques sans conserver toutes les données sources ;
- les structures de données adaptées aux agrégations ;
- la réflexion sur la scalabilité d'un traitement.

**CodeTober 2026 — Data Engineering with Python 🐍🎃**