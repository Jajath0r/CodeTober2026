# CodeTober 2026 — J9 : Upsert or Shut Up

**Thème :** SQL, clés métier et rejouabilité  
**Durée indicative :** 45 à 120 minutes (possibilité de plusieurs séances)  
**Technos :** Python 3, SQLite (`sqlite3`), CSV, bibliothèque standard ; `pytest` facultatif.

## Contexte

Tu reçois régulièrement des exports de clients provenant d'un système source. Tu dois maintenir une table SQL `customers` représentant **la dernière version connue de chaque client**. Certains lots contiennent de nouveaux clients, d'autres des corrections de clients existants, et les lots peuvent être rejoués ou arriver dans le désordre.

## Données fournies

Tous les fichiers ont les colonnes :

| Colonne | Signification |
|---|---|
| `customer_id` | Identifiant métier stable d'un client |
| `full_name` | Nom complet |
| `email` | Adresse e-mail |
| `country` | Code pays |
| `updated_at` | Horodatage de dernière modification à la source, ISO `YYYY-MM-DDTHH:MM:SS` |

- `customers_01.csv` : chargement initial (5 lignes).
- `customers_02.csv` : nouveaux clients, mises à jour, doublon identique et version obsolète (6 lignes).
- `customers_03.csv` : nouvelles données et mises à jour supplémentaires (5 lignes).
- `customers_edge.csv` : cas limites pour pousser les tests (8 lignes).

## Mission

Écris un programme CLI qui accepte au minimum **un chemin vers un CSV**, **un chemin vers une base SQLite** et **un répertoire de sortie**. Le même fichier de base doit pouvoir être réutilisé sur plusieurs exécutions.

1. Créer la table cible `customers` si nécessaire, avec une contrainte garantissant l'unicité de la **clé métier pertinente**.
2. Lire le CSV et valider chaque ligne : `customer_id`, `full_name`, `email`, `country` non vides ; `updated_at` au format ISO indiqué. Une ligne invalide est rejetée sans bloquer les autres.
3. Pour chaque ligne valide :
   - **INSERT** si le client n'existe pas ;
   - **UPDATE** si le client existe et si `updated_at` est **strictement plus récent** que celui enregistré ;
   - **UNCHANGED** si le contenu et l'horodatage sont identiques, ou si la ligne est plus ancienne ;
   - **CONFLICT** si le même client possède le **même horodatage** mais des données différentes : ne pas modifier la cible et signaler le conflit.
4. Les doublons d'identifiant dans **un même fichier** sont traités dans leur ordre d'apparition, avec exactement les mêmes règles que les autres lignes.
5. Produire, après chaque exécution :
   - `customers_snapshot.csv` : contenu actuel de la table cible, trié par `customer_id`, avec les cinq colonnes d'entrée ;
   - `report.json` : `batch` (nom du fichier CSV sans extension), `nb_read`, `nb_inserted`, `nb_updated`, `nb_unchanged`, `nb_conflict`, `nb_rejected`, `nb_customers_after`.
6. Préserver les données déjà chargées entre deux exécutions. Le traitement d'un fichier déjà chargé ne doit créer ni doublons ni mises à jour inutiles.

**Règles de comptage :** chaque ligne d'entrée est comptée exactement une fois dans `nb_read` et exactement une fois dans l'une des cinq catégories `inserted`, `updated`, `unchanged`, `conflict`, `rejected`. Une ligne rejetée est invalide ; un conflit est valide mais contradictoire avec la version enregistrée.

## Parcours de test conseillé

1. Charger `customers_01.csv` sur une base neuve.
2. Charger `customers_02.csv` sur **la même base**.
3. Rejouer `customers_02.csv` et comparer les données cibles.
4. Charger `customers_03.csv`, puis rejouer `customers_01.csv` (lot plus ancien).
5. Enfin, tester `customers_edge.csv`.

Tu peux également tester une base neuve en chargeant `customers_03.csv` **avant** `customers_02.csv` puis `customers_01.csv` : l'état final doit être identique à celui obtenu dans l'ordre chronologique (hors éventuels cas de conflit à horodatage égal).

## Critères de validation

### 4/5 — Fonctionnel

- La clé métier est correctement choisie et contrainte en SQL.
- Insertions, mises à jour, versions obsolètes, lignes inchangées et conflits sont traités selon les règles ci-dessus.
- Les lignes invalides sont rejetées sans arrêter le lot.
- Le stockage persiste entre les lancements.
- Le snapshot et le rapport sont corrects.
- Le rejeu d'un lot n'ajoute pas de doublons et ne dégrade pas les données.

### 5/5 — Contrainte d'ingénierie supplémentaire (annoncée dès le départ)

**Garantir l'atomicité du chargement d'un lot au niveau de la base SQL :** si une erreur technique interrompt le traitement avant sa validation finale, aucune modification partielle de ce lot ne doit rester validée dans SQLite. Démontrer cette propriété avec un test d'interruption volontaire après plusieurs écritures, puis une relance réussie. Les rejets métier ordinaires, eux, n'interrompent pas le lot.

> À toi de choisir comment organiser les requêtes, les transactions, les fonctions et les tests. Aucun framework ni serveur de base de données n'est nécessaire.

## Indices de conception (sans solution imposée)

- Quelle colonne identifie durablement un client, même si son e-mail change ?
- Que se passe-t-il si tu relances exactement le même fichier ?
- Que se passe-t-il si une ancienne extraction arrive après une extraction récente ?
- Où placer la frontière entre une erreur métier et une erreur technique ?
