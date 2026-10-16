# CodeTober 2026 — J14 : DAG Nabbit

**Thème :** orchestration de tâches et gestion des dépendances (DAG)  
**Durée visée :** 1 h 30 à 2 h 30, tests compris  
**Point de départ :** ton code du **J13** (`main.py`, `extract.py`, `transform.py`, `load.py`, `models.py`, `simulator.py`).

## 🎯 Objectif

Jusqu'ici, `main.py` impose directement l'ordre des opérations. Aujourd'hui, construis un **mini-orchestrateur** : on lui donne des tâches, leurs dépendances et les fonctions correspondantes ; il décide quelles tâches peuvent être exécutées et dans quel ordre.

**La nouveauté principale est le graphe de dépendances.** Conserve les règles métier et le retry du J13. Ne réécris ni les transformations de ventes ni le chargement SQLite.

## 📦 Matériel fourni

```text
CodeTober_J14_DAG_Nabbit/
├── README.md
├── data/
│   ├── catalog.json
│   └── orders.csv
└── graphs/
    ├── 01_valid.json
    ├── 02_shuffled.json
    ├── 03_catalog_failure.json
    ├── 04_independent_branch.json
    ├── 05_unknown_dependency.json
    ├── 06_cycle.json
    └── 07_self_cycle.json
```

Les fichiers dans `data/` sont les **mêmes données métier que J13** : 12 commandes, 4 produits, **8 ventes** chargées pour un scénario nominal, total **27 100 centimes**. Tu peux donc reprendre tes modules et ton simulateur existants.

Les fichiers `graphs/*.json` sont des **fixtures de tests**, pas une architecture obligatoire. Ils fournissent des noms de tâches et leurs dépendances :

```json
{
  "tasks": [
    {"name": "extract_catalog", "depends_on": []},
    {"name": "extract_orders", "depends_on": []},
    {"name": "transform_sales", "depends_on": ["extract_catalog", "extract_orders"]},
    {"name": "load_sales", "depends_on": ["transform_sales"]}
  ]
}
```

`simulate_failure`, lorsqu'il est présent, est une **instruction de scénario pour tes tests** : la tâche indiquée doit échouer artificiellement. Ce n'est pas une clé que ton orchestrateur est obligé de comprendre. Tu peux construire les tâches directement en Python, convertir ces fichiers en tes propres structures, ou utiliser les JSON comme spécification de cas à reproduire.

## ✅ Obligatoire — 4/5

1. **Déclarer les tâches.** Chaque tâche a un **nom unique**, une fonction à appeler et **zéro ou plusieurs dépendances**. Leur ordre de déclaration ne doit pas être considéré comme un ordre d'exécution.
2. **Respecter les dépendances.** Exécuter chaque tâche admissible **une seule fois**, seulement après la réussite de toutes ses dépendances. L'exécution est **séquentielle** : pas de parallélisme aujourd'hui.
3. **Isoler les échecs.** Si une tâche échoue, les tâches qui en dépendent directement ou indirectement ne s'exécutent pas. Une branche indépendante peut, elle, poursuivre son exécution. Un échec ne doit pas être présenté comme un succès global.
4. **Valider avant d'exécuter.** Refuser un graphe comportant une dépendance inconnue ou un cycle (y compris une tâche dépendant d'elle-même), avec une erreur explicite, **sans exécuter aucune tâche**.

## ⭐ Bonus — 5/5

L'exécution doit être **déterministe et traçable** :

- deux déclarations du **même graphe** dans des ordres différents produisent exactement le **même ordre d'exécution** ;
- chaque tâche reçoit un état final explicite : `SUCCESS`, `FAILED` ou `SKIPPED` ;
- les états doivent permettre de distinguer une tâche qui a échoué d'une tâche non exécutée à cause d'une dépendance.

Les propriétés sont imposées ; **aucun algorithme ni structure de données n'est prescrit**.

## 🧪 Jeux d'essai

| Fichier | Intention du test | Attendu principal |
|---|---|---|
| `01_valid.json` | Pipeline standard | 4 tâches réussies ; dépendances respectées |
| `02_shuffled.json` | Même graphe, déclaration inversée | Même résultat métier ; pour 5/5, même ordre d'exécution que `01_valid` |
| `03_catalog_failure.json` | Échec simulé de `extract_catalog` | `transform_sales` et `load_sales` ne s'exécutent pas ; `extract_orders` reste exécutable |
| `04_independent_branch.json` | Échec du catalogue avec branche métriques indépendante | `refresh_metrics` et `publish_metrics` peuvent réussir malgré l'échec de l'autre branche |
| `05_unknown_dependency.json` | Dépendance inexistante | Rejet avant toute exécution |
| `06_cycle.json` | Cycle entre plusieurs tâches | Rejet avant toute exécution |
| `07_self_cycle.json` | Auto-dépendance | Rejet avant toute exécution |

Pour les scénarios d'échec, une simple fonction de test qui lève une exception suffit : **pas besoin de provoquer un incident réel** sur SQLite ou sur le catalogue. Pour la pipeline nominale réutilisant le traitement des ventes, la base reste idempotente comme au J13.

## ♻️ Ce que tu réutilises et ce que tu ajoutes

**À réutiliser :** les fichiers Python du J13, le retry de récupération du catalogue, le traitement des commandes et les transactions SQLite.

**À créer :** une couche d'orchestration qui associe des fonctions aux noms des tâches, respecte les dépendances, et expose le résultat de l'exécution. Tu es libre de choisir les nouveaux fichiers et l'interface de cette couche.

Les tâches `extract_catalog`, `extract_orders`, `transform_sales` et `load_sales` représentent les **étapes logiques** de ton ETL : tu peux t'appuyer sur tes fonctions existantes ou utiliser d'abord de petites fonctions fictives pour valider l'orchestrateur. Le passage de données entre ces étapes n'est **pas** le défi principal du jour. Garde cette partie simple.

## 🚫 Hors périmètre

Pas d'Airflow, pas de parallélisme, pas de scheduler horaire, pas de nouvelle politique de retry, pas de nouveau schéma de base de données. **Un graphe correct, des erreurs bien traitées et des tests ciblés suffisent.**

## 📏 Barème annoncé

- **4/5 :** les quatre exigences obligatoires sont satisfaites et vérifiées.
- **5/5 :** les quatre exigences **plus** les propriétés de déterminisme et de traçabilité sont satisfaites et vérifiées.

*Conseil de méthode : commence par deux ou trois fonctions factices qui enregistrent leur passage ; branche le véritable ETL seulement quand l'ordre et les échecs sont maîtrisés.*
