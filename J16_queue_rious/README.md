# CodeTober 2026 — J16 : Queue-rious (version fil rouge J13)

**Sujet : Producer / Consumer · file bornée · arrêt propre · erreurs partielles**  
**Temps cible : 1 h 30–2 h 30**  
**4/5 : toutes les contraintes obligatoires. 5/5 : bonus explicite à la fin.**

## Point de départ : ton J13, pas un nouveau projet

**Copie ton dossier J13 « Retry Me Maybe » dans un dossier J16.** Conserve tes modules existants (`main.py`, `extract.py`, `transform.py`, `load.py`, `models.py`, `simulator.py`) et leurs responsabilités : extraction du catalogue, `get_catalog()` et retry, validation du schéma des commandes, construction d'une ligne de vente, insertion idempotente dans `sales` (SQLite).

Tu disposes maintenant de **deux fichiers de commandes indépendants** par scénario, au lieu d'un. Les producteurs lisent chacun un fichier et alimentent une file commune. Des consommateurs traitent les commandes, tandis que l'écriture dans SQLite est **centralisée** après leur traitement.

**Important :** plusieurs threads ne doivent **pas** partager directement la connexion SQLite de ton J13. La partie chargement SQLite reste dans un seul thread, après la fin du traitement concurrent. C'est un choix de périmètre du J16 : pas de seconde file ni de writer concurrent à développer. Tu pourras réutiliser `create_sales_table()` et `insert_row_in_sales()`.

Le catalogue demeure unique et commun à tous les fichiers ; tu peux le charger **une seule fois**, avant les traitements, avec le mécanisme du J13. Le scénario du simulateur à utiliser pour ce défi est `ok`/le scénario de succès de **ton propre** `SimulatedCatalogSource` : adapte seulement son nom si nécessaire. **Aucun retry, fournisseur en panne ni orchestration DAG à ajouter au J16.**

## Schéma de la chaîne

`CSV source A ──┐`  
`              ├── producteurs → file bornée → consommateurs (validation + transformation) → résultats en mémoire → chargement SQLite (1 thread)`  
`CSV source B ──┘`

Production et consommation doivent **se chevaucher** : une solution qui lit d'abord tous les CSV puis commence à consommer ne répond pas à l'objectif du jour. La file doit constituer le tampon borné entre producteurs et consommateurs ; pas de liste géante préchargée.

## Règles métier (compatibles avec J13)

Chaque CSV utilise les colonnes `order_id,order_date,product_id,quantity,status` ; toutes les commandes de ces scénarios sont `paid`. Les quatre `product_id` figurent dans le catalogue fourni. Une commande valide devient une ligne `sales` au format J13 :

`order_id, order_date, product_id, product_name, quantity, unit_price_cents, total_cents`.

Tu réutilises `create_sales_row()` pour le calcul de `total_cents = quantity * unit_price_cents` et `insert_row_in_sales()` pour l'écriture idempotente. **Une validation supplémentaire est demandée au niveau de l'événement :** `quantity` doit être un entier strictement positif (pas de valeur vide, texte invalide, zéro ni négatif). Les lignes invalides donnent un résultat `FAILED` avec une erreur explicite ; elles ne doivent pas être insérées dans SQLite. Une exception lors du traitement d'une ligne ne doit pas arrêter les autres.

Aucune obligation de préserver l'ordre des lignes pendant le traitement ; SQLite est ta source de vérité pour les ventes valides.

## Obligatoire — 4/5

1. **Deux producteurs simultanés** : chacun parcourt un des deux fichiers CSV progressivement et dépose les commandes dans une file partagée. Ils ne doivent pas attendre qu'une commande soit traitée pour produire la suivante, sauf lorsque la file est pleine.
2. **Deux consommateurs simultanés** : ils prélèvent les événements de la file et effectuent validation + transformation. Chaque commande lue reçoit **exactement un résultat** `SUCCESS` (ligne prête à insérer) ou `FAILED` (erreur explicite), même quand un autre événement échoue.
3. **File bornée configurable** : une capacité de **2** doit fonctionner. Lorsqu'elle est pleine, la production attend de la place ; aucune perte ou mémorisation illimitée de commandes en attente.
4. **Arrêt correct** : aucun consommateur ne doit s'arrêter simplement parce que la file est momentanément vide. À la fin, tous les événements ont un résultat, les producteurs et consommateurs sont terminés, sans blocage.
5. **Chargement SQLite centralisé et bilan** : à la fin du traitement concurrent, **un seul thread** écrit les ventes valides dans la table `sales` du J13. Les échecs ne sont jamais insérés. Affiche (ou écris dans un petit JSON) un bilan comportant `total`, `success`, `failed` et les `order_id` ayant échoué, avec un message par erreur. La sortie SQLite reste obligatoire.

### Résultats de référence (nouvelle base SQLite vide)

| Scénario | Lignes lues (`total`) | `success` | `failed` | Lignes finales dans `sales` | Commandes invalides |
|---|---:|---:|---:|---:|---|
| `01_nominal` | 12 | 12 | 0 | 12 | — |
| `02_partial_failure` | 12 | 10 | 2 | 10 | `O0004`, `O0011` |
| `03_pressure` | 40 | 36 | 4 | 36 | `O0007`, `O0018`, `O0029`, `O0037` |

Les IDs `order_id` sont uniques dans chaque scénario. **Pas de déduplication des événements à implémenter.** Ton `INSERT OR IGNORE` existant peut néanmoins rester pour la rejouabilité de la base.

**Règle de comptage :** `success` signifie « commande transformée avec succès pendant ce run » ; le nombre de lignes présentes en base est différent lors d'une relance sur une base déjà alimentée. Les nombres de la colonne `sales` supposent une base vide au début du scénario.

## Bonus d'ingénierie — 5/5

**Prouver automatiquement la complétude et la terminaison malgré une forte pression sur la file.** Avec `pytest` et `03_pressure`, **2 producteurs, 2 consommateurs et une capacité de file de 1 ou 2** :

- chaque `order_id` des CSV figure **une seule fois** parmi les résultats du run (succès ou échec) ;
- le nombre total de résultats est de 40, avec 36 succès et 4 échecs ;
- aucun événement n'est perdu quand les consommateurs sont artificiellement plus lents que les producteurs ;
- la file reste dans sa capacité maximale, et tous les threads terminent dans un délai de sécurité borné (sans blocage) ;
- une relance sur la même base ne crée aucune vente supplémentaire (idempotence du J13 conservée).

**Contrainte de testabilité :** les tests doivent pouvoir ralentir la consommation **sans modifier les CSV** ni faire de suppositions fragiles sur le temps total. Choisis la façon dont tu rends ce comportement configurable/testable. L'énoncé fixe les propriétés, pas le mécanisme.

## Fichiers du pack

```
data/
  catalog.json
  01_nominal_source_a.csv
  01_nominal_source_b.csv
  02_partial_failure_source_a.csv
  02_partial_failure_source_b.csv
  03_pressure_source_a.csv
  03_pressure_source_b.csv
```

Ce pack **ne remplace pas ton code J13** ; il fournit les nouveaux fichiers d'entrée et le contrat du J16. Ton simulateur J13, ton catalogue et ton chargement restent dans ton projet.

## Pour commencer, sans te donner l'architecture en code

Commence par faire fonctionner une file entre un producteur qui parcourt un CSV et un consommateur qui transforme les commandes ; ajoute ensuite le second producteur et le second consommateur. Puis résous l'arrêt des consommateurs et le bilan. Enfin seulement, teste la capacité minimale et le bonus.

**Hors périmètre :** orchestrateur du J14, récupération concurrente des fournisseurs du J15, partage d'une connexion SQLite entre threads, transaction complexe multi-thread, suivi d'état persistant de la file, nouveaux formats de données.
