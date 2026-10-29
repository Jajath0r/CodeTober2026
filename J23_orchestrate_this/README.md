# CodeTober 2026 — J23 · Orchestrate This

## Contexte
Une équipe possède six tâches métier exécutables individuellement, mais ses traitements échouent dès qu'une tâche démarre trop tôt ou qu'une exécution est interrompue. Réalise un **mini-orchestrateur local** : le code métier fourni dans `jobs.py` ne doit pas être réécrit.

## Contrat d'entrée
- `config/pipeline.json` décrit les tâches par `id`, `depends_on` et `max_attempts` (nombre total de tentatives, première comprise).
- `jobs.execute(task_id, project_root, work_dir, run_id)` exécute une tâche, renvoie des métriques (dict), ou lève `TransientJobError` / `PermanentJobError`.
- Toutes les tâches d'un run doivent partager le **même** `work_dir`, dont le contenu doit être conservé pour une reprise.
- Les données métier sont dans `data/`. Les résultats intermédiaires sont produits par `jobs.py`.

## Commande attendue
Choisis un point d'entrée Python (par exemple `main.py`) offrant au minimum :

`python main.py --config config/pipeline.json --output-dir output`

et une commande de reprise explicite, par exemple :

`python main.py --config config/pipeline.json --output-dir output --resume <run_id>`

Le format exact du paramètre de reprise peut varier, mais il doit être documenté.

## Exigences obligatoires — 4/5
1. **DAG** : vérifier l'unicité des IDs, l'existence des dépendances et l'absence de cycle, avant toute tâche métier. Ne lancer une tâche que lorsque ses dépendances ont réussi. Un ordre séquentiel valide suffit (pas de parallélisme imposé).
2. **États** : pour chaque run, permettre d'identifier les tâches en attente, prêtes, en cours, réussies, échouées et bloquées par un échec amont. Ces états doivent être compréhensibles dans les résultats du run.
3. **Retry borné** : une erreur transitoire autorise une nouvelle tentative dans la limite de `max_attempts`. Une erreur permanente ne doit pas être relancée automatiquement. En cas d'épuisement, la tâche échoue et ses descendants ne sont pas exécutés.
4. **État durable et reprise** : conserver l'historique d'un run sur disque. Après interruption, reprendre le même run sans réexécuter ses tâches déjà réussies. Une tâche interrompue sans confirmation de succès peut être rejouée ; les tâches du kit sont prévues pour cela. Garder les artefacts intermédiaires du run.
5. **Observabilité** : produire par run un compte rendu lisible par programme (JSON par exemple) indiquant `run_id`, statut final, horaires de début/fin, tâches et leurs statuts, nombre de tentatives, erreurs et métriques retournées par les tâches. Enregistrer aussi des événements horodatés permettant de reconstituer le déroulement.
6. **Résultat** : sans panne, obtenir `sales_by_category.csv` (écrit par `publish`) et un run réussi. En cas de panne, signaler explicitement un échec, sans déclarer le run réussi.

## Contraintes d'ingénierie annoncées pour 5/5
Automatiser des tests démontrant **simultanément** :
- Un DAG invalide (dépendance inconnue ou cycle) est rejeté **avant tout effet métier**.
- Une panne transitoire injectée sur `aggregate` entraîne une reprise bornée et un résultat identique au cas nominal ; une panne permanente bloque `aggregate` et `publish` sans lancer `publish`.
- Une interruption à un point contrôlé suivie d'une reprise conserve les tâches déjà réussies **sans les rejouer**, avec un historique cohérent (pas de succès fantôme ni de comptage d'essais incorrect).

Aucune architecture de stockage, bibliothèque de DAG ou structure de classes n'est imposée. Le mécanisme et les tests sont à concevoir.

## Pannes d'essai fournies
Les tâches peuvent être forcées à échouer via des variables d'environnement :
- `J23_FAIL_ONCE=aggregate` : `aggregate` échoue une fois **par dossier de travail** avec `TransientJobError`, puis réussit.
- `J23_FAIL_ALWAYS=aggregate` : `aggregate` échoue avec `PermanentJobError` à chaque appel.

Les marqueurs de simulation sont conservés sous `work_dir` : une reprise doit réutiliser ce dossier.

## Repère de sortie nominale (sans panne)
`category,orders,items,revenue_cents` avec les lignes `books,3,8,5400` et `electronics,1,1,3500` (hors en-tête).

## Hors périmètre
Pas de parallélisme, d'interface graphique, de planification horaire, de service cloud, d'ordonnanceur tiers ou de changement dans `jobs.py` requis.
