# CodeTober 2026 — J6 : Checkpoint

## Contexte
Un même `event_id` peut apparaître plusieurs fois. Chaque ligne représente son état à un instant donné. L'ordre des lignes source n'est pas significatif.

## Exécution attendue
`python main.py input.csv output.csv`

## Objectif principal — 4/5
- Lire les événements du fichier source.
- Conserver une seule version par `event_id` : celle dont `updated_at` est la plus récente.
- Produire `output.csv` avec les mêmes colonnes que le fichier source.
- Fonctionner quel que soit l'ordre des lignes.
- Rejeter proprement un `event_id` vide.
- Rejeter proprement un `updated_at` ne respectant pas exactement `YYYY-MM-DD HH:MM:SS`.
- Produire un rapport JSON avec `nb_read_lines`, `nb_invalid_lines`, `nb_distinct_event_ids`, `nb_replaced_versions`.

Pour cette partie, le fichier peut être supposé tenir raisonnablement en mémoire.

`nb_replaced_versions` augmente lorsqu'un `event_id` déjà connu est rencontré avec un `updated_at` strictement plus récent et que l'état conservé est remplacé. Une version plus ancienne rencontrée après une version plus récente ne l'incrémente pas.

## Objectif 5/5 — reprise après interruption
Le programme doit pouvoir reprendre après une interruption sans recommencer tout le traitement depuis le début.

Contraintes :
- l'état nécessaire à la reprise survit à l'arrêt du programme ;
- au redémarrage, le programme détermine jusqu'où le fichier source avait déjà été traité ;
- une interruption ne doit pas laisser un état affirmant que des données ont été traitées alors qu'elles ne l'ont pas réellement été ;
- après reprise, le résultat final doit être identique à celui d'une exécution complète sans interruption ;
- éviter de gérer manuellement une multitude de petits fichiers techniques lorsqu'un mécanisme adapté permet de conserver un état structuré et durable.

Le choix de l'architecture, du mécanisme de persistance et du format de checkpoint fait partie du défi.

## Structure suggérée du dépôt
`README.md`, `input.csv`, `main.py`, `test.py`.

## Dataset fourni
Plusieurs centaines de lignes, 260 `event_id` valides distincts, 1 à 5 versions par événement, ordre mélangé, et quelques lignes invalides.
