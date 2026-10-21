# CodeTober 2026 — J17 : Slowly but Surely

**Sujet :** Historisation de référentiel produit — Slowly Changing Dimension, type 2 (SCD2)  
**Durée indicative :** 1 h 30 à 2 h 30  
**Point de départ : J13 — Retry Me Maybe**, plus précisément ses modules d'extraction du catalogue et de chargement SQLite (`main.py`, `extract.py`, `load.py`, `models.py` selon ta version). **Ne repars ni du J15 ni du J16.**

## 1. Contexte métier

Ton ETL sait récupérer un catalogue de produits et utiliser une base SQLite. Jusqu'ici, chaque catalogue est traité comme une photographie de l'état courant. Dans un système analytique, ce n'est pas suffisant : si le prix ou le nom d'un produit change, on doit pouvoir expliquer les résultats historiques.

Aujourd'hui, plusieurs **instantanés datés du même catalogue** arrivent successivement. Tu dois maintenir dans SQLite l'historique des versions du référentiel, plutôt que remplacer les valeurs précédentes.

**Ce que tu réutilises du J13 :** la lecture du catalogue JSON, la connexion SQLite, la gestion transactionnelle, les fonctions de chargement quand elles sont pertinentes, et les tests `pytest`. Tu peux laisser l'ETL des commandes de côté pour cet exercice : **on ne refait pas la pipeline complète**. La logique de retry existante peut être conservée, mais aucun scénario de panne réseau n'est demandé.

## 2. Données fournies

Chaque fichier JSON conserve le format de ton catalogue J13 :

```json
{"products": [{"product_id": "P001", "name": "Clavier", "unit_price_cents": 4500}]}
```

Les quatre instantanés complets sont à appliquer **dans cet ordre** :

| Date d'effet | Fichier | Évolution principale |
|---|---|---|
| 2026-10-01 | `data/catalog_2026-10-01.json` | État initial : 4 produits |
| 2026-10-08 | `data/catalog_2026-10-08.json` | Hausse de prix de P001 |
| 2026-10-15 | `data/catalog_2026-10-15.json` | Renommage de P002, arrivée de P005 |
| 2026-10-20 | `data/catalog_2026-10-20.json` | Nouveau prix de P001 et baisse de P003 |

Les produits inchangés sont répétés d'un instantané à l'autre : **cela ne doit pas créer de nouvelle version**. Un produit absent d'un instantané n'est pas traité dans ce J17 (pas de suppression, désactivation ou disparition à historiser).

## 3. Contrat fonctionnel — 4/5

Le **4/5** est atteint quand les exigences suivantes sont correctement satisfaites :

1. **Chargement daté.** Ton programme accepte un fichier catalogue et sa date d'effet, et inscrit les versions dans une base SQLite persistante. Les quatre fichiers se chargent successivement dans la **même** base.
2. **Nouveau produit.** Pour chaque identifiant inconnu, créer une première version prenant effet à la date du catalogue.
3. **Produit inchangé.** Si les attributs suivis (`name`, `unit_price_cents`) ne changent pas, ne pas créer de version supplémentaire.
4. **Produit modifié.** Lorsqu'au moins un attribut suivi change, terminer la validité de la version précédente et créer la nouvelle version à la date d'effet.
5. **Consultation historique.** Permettre de retrouver **une seule version applicable** à une date demandée, pour un identifiant donné (une fonction Python ou une requête SQL suffit).
6. **Cohérence transactionnelle.** Un chargement d'instantané doit réussir entièrement ou être annulé. Une erreur ne doit pas laisser un produit à moitié mis à jour.

### Convention temporelle obligatoire

- `valid_from` : **inclus**.
- `valid_to` : **exclu**.
- `valid_to = NULL` : version en cours, sans date de fin connue.
- On suit uniquement les changements de `name` et `unit_price_cents` ; `product_id` est la clé métier.
- Les dates des instantanés sont distinctes et fournies dans un ordre chronologique. **Les corrections rétroactives et les changements multiples le même jour sont hors périmètre**.

> Exemple : une version valide du 1er au 8 octobre s'applique le 7 octobre, mais plus le 8 octobre.

## 4. Extension d'ingénierie — 5/5 (annoncée dès maintenant)

Pour le **5/5**, ton traitement doit garantir **ces deux propriétés**, avec des tests automatisés :

- **Rejouabilité / idempotence :** réappliquer un instantané déjà chargé, sans changement de contenu, ne doit ni ajouter de version ni modifier l'historique obtenu. Tu peux tester le rejeu immédiat d'un fichier, puis le rejeu de l'ensemble de la séquence initiale ; l'ordre chronologique des *nouveaux* chargements demeure la règle.
- **Intégrité temporelle :** pour un même `product_id`, deux versions ne doivent jamais être valides simultanément. Une requête « état au jour J » retourne au maximum une version par produit. Vérifie les frontières des dates de changement dans tes tests.

**Aucune technique n'est imposée :** choisis toi-même les structures, requêtes, contraintes et stratégies de vérification. Le bonus porte sur les propriétés observables, pas sur une solution particulière.

## 5. Résultats de référence

Après le chargement des quatre instantanés, la table d'historique doit contenir **9 versions** :

| Produit | Versions | Valeur courante après 2026-10-20 |
|---|---:|---|
| P001 | 3 | Clavier — 4 700 centimes |
| P002 | 2 | Souris ergonomique — 1 800 centimes |
| P003 | 2 | Ecran — 18 900 centimes |
| P004 | 1 | Cable USB — 900 centimes |
| P005 | 1 | Support ordinateur — 2 900 centimes |

**`reference_history.csv`** fournit toutes les versions attendues (colonnes métier et dates), pour vérifier le résultat **sans prescrire ton schéma technique** : tu peux ajouter un identifiant de version, des contraintes, etc.

Quelques requêtes attendues :

| Produit | Date interrogée | Prix attendu (centimes) | Nom attendu |
|---|---|---:|---|
| P001 | 2026-10-07 | 4500 | Clavier |
| P001 | 2026-10-08 | 4900 | Clavier |
| P001 | 2026-10-20 | 4700 | Clavier |
| P002 | 2026-10-14 | 1800 | Souris |
| P002 | 2026-10-15 | 1800 | Souris ergonomique |
| P005 | 2026-10-14 | — | Aucun résultat |
| P005 | 2026-10-15 | 2900 | Support ordinateur |

## 6. Tests minimaux

- Charger uniquement le premier instantané : **4 produits, 4 versions**.
- Charger ensuite le deuxième : **5 versions**, prix de P001 modifié.
- Charger les quatre : **5 produits distincts, 9 versions**, une version ouverte par produit.
- Vérifier le jour précédant et le jour même d'au moins deux changements.
- Vérifier qu'un instantané inchangé ne crée aucune version supplémentaire.
- Pour viser 5/5 : rejouer les instantanés, comparer l'historique avant/après et vérifier l'absence de chevauchement des périodes.

## 7. Interface et périmètre

Tu peux définir tes arguments CLI librement. Une interface possible, **non obligatoire**, serait :

```bash
python main.py data/catalog_2026-10-01.json 2026-10-01
python main.py data/catalog_2026-10-08.json 2026-10-08
python main.py data/catalog_2026-10-15.json 2026-10-15
python main.py data/catalog_2026-10-20.json 2026-10-20
```

Les dates figurent dans les noms des fichiers pour faciliter les tests, mais ton code **ne doit pas être obligé de déduire la date du nom**. La date d'effet peut être un argument ou une donnée explicitement transmise par le programme appelant.

**Hors périmètre :** concurrence, nouveaux retries, traitement des commandes, évolution du schéma produit, suppressions de produits, dates rétroactives, mises à jour partielles et gestion d'horodatages infrajournaliers. Pas de refonte intégrale de la pipeline J13.

## 8. Critère de fin

Le travail est terminé lorsque la même base SQLite permet de consulter l'ancienne et la nouvelle valeur de chaque produit à la bonne date, et que les tests prouvent les propriétés demandées pour la note visée.

**Tu codes la solution ; ce pack fournit l'énoncé, les entrées et les résultats de contrôle, pas un algorithme préécrit.**
