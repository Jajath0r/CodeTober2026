# CodeTober 2026 — J10 : Quality Control

**Thème :** Data Quality Gates · **Niveau :** Data Engineering · **Objectif :** 4/5 ou 5/5

## Contexte

Tu maintiens une ingestion quotidienne de commandes e-commerce. Les données ont déjà été extraites et doivent être contrôlées **avant** leur chargement en base. Un lot de mauvaise qualité ne doit pas contaminer la table cible ; les enregistrements incorrects doivent rester auditables.

Tu disposes de :

- `orders.csv` : 90 commandes réparties en trois lots (`batch_id`) ;
- `customers.csv` : référentiel de clients et de leur statut ;
- `quality_config.json` : paramètres du contrôle qualité.

Tu peux utiliser la bibliothèque standard Python, SQLite et pytest. Aucune bibliothèque externe n'est imposée.

## Mission — exigences obligatoires (4/5)

Écris un programme exécutable qui examine chaque lot **indépendamment** et applique les règles suivantes.

### Règles de qualité

1. **Structure :** les colonnes obligatoires du fichier d'entrée doivent être présentes. En cas de colonne absente, l'exécution échoue explicitement : ne pas produire de résultat trompeur.
2. **Identifiants :** `batch_id`, `order_id` et `customer_id` ne doivent pas être vides.
3. **Unicité :** un `order_id` ne peut apparaître qu'une fois **dans un même lot**. En cas de répétition, la première occurrence reste candidate à la validation ; chaque occurrence suivante est invalide.
4. **Référentiel :** `customer_id` doit exister dans `customers.csv` et correspondre à un client `active`.
5. **Date :** `order_date` doit être une vraie date ISO `YYYY-MM-DD` et appartenir au mois d'octobre 2026.
6. **Quantité :** `quantity` doit être un entier strictement positif.
7. **Prix :** `unit_price_cents` doit être un entier supérieur ou égal à zéro.
8. **Devise :** `currency` doit appartenir aux devises autorisées par la configuration.

**Important :** une ligne peut enfreindre plusieurs règles. Toutes les anomalies détectables de cette ligne doivent être conservées ; elle n'est cependant comptée qu'une fois parmi les lignes invalides.

### Décision par lot

Pour chaque `batch_id`, calcule :

- le nombre total de lignes ;
- le nombre de lignes valides et invalides ;
- le taux d'invalidité `invalid_rows / total_rows` ;
- le nombre d'occurrences de chaque type d'anomalie.

Un lot est **ACCEPTED** si son taux d'invalidité est **inférieur ou égal** à `max_invalid_ratio`. Sinon il est **REJECTED**. Un lot rejeté ne doit fournir **aucune commande** à la sortie destinée au chargement, même si certaines de ses lignes sont individuellement valides.

### Livrables du programme

Pour chaque exécution, produis dans un répertoire de sortie :

- `accepted_orders.csv` : uniquement les lignes valides des lots acceptés, avec les colonnes d'origine ;
- `quarantine.csv` : toutes les lignes individuellement invalides, y compris celles des lots rejetés, avec une colonne `error_codes` contenant **tous** leurs codes d'erreur ;
- `quality_report.json` : un rapport par lot (statut, volumes, taux, anomalies), ainsi que des totaux globaux ;
- `rejected_batches.csv` : les identifiants des lots rejetés et leur taux d'invalidité.

Les lignes valides d'un lot rejeté ne figurent **ni dans `accepted_orders.csv` ni dans `quarantine.csv`** : elles sont exclues du chargement par décision de lot. Le rapport doit permettre de connaître leur nombre.

Choisis des codes d'erreur stables et documentés (ex. `INVALID_QUANTITY`). L'ordre des lignes en sortie n'est pas imposé ; les résultats doivent être déterministes pour un même jeu de données.

### Comportement attendu

Le programme doit permettre de spécifier les chemins des entrées et du répertoire de sortie, sans modifier le code source. Une seconde exécution sur les mêmes données et dans le même répertoire ne doit pas accumuler de doublons dans les livrables.

## Bonus ingénierie — contrainte 5/5

**La décision de publication d'un lot doit être indivisible et résister à une interruption.** Si le traitement est interrompu à n'importe quel moment, une relance doit permettre d'obtenir des sorties cohérentes : jamais un rapport indiquant `ACCEPTED` alors que les commandes correspondantes ne sont publiées qu'en partie, ni un mélange de fichiers de deux exécutions différentes.

Tu es libre de choisir les mécanismes techniques. Tu devras expliquer les garanties apportées, leurs limites et montrer au moins un test simulant une interruption à un moment critique.

## Tests à prévoir

Couvre au minimum : ligne valide, plusieurs anomalies sur une ligne, doublon dans un lot, même identifiant dans deux lots différents, client inexistant, client suspendu, date invalide, quantité/prix invalides, seuil exactement atteint, lot refusé et relance identique. Pour le 5/5, ajoute un scénario d'interruption.

## Indices de vérification (sans dévoiler la solution)

Avec les données fournies et les règles ci-dessus :

- il y a **3 lots de 30 lignes** ;
- exactement **un lot doit être rejeté** ;
- une commande possède **deux anomalies simultanées** ;
- les anomalies ne se confondent pas avec le nombre de lignes invalides.

Le reste des métriques est à déterminer par ton programme.

## Ce que j'évaluerai

**4/5 :** règles correctement appliquées, séparation des trois destinations logiques, décisions de lots justes, métriques cohérentes, relance sans doublons et tests pertinents.

**5/5 :** tous les critères du 4/5, **plus** la garantie d'indivisibilité et de reprise explicitée ci-dessus, démontrée par un test.

> Le but n'est pas de multiplier les `if` pour le plaisir : il s'agit de construire une barrière de qualité compréhensible, vérifiable et exploitable avant un chargement en production.
