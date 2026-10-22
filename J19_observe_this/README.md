# CodeTober 2026 — J19 : Observe This

**Sujet :** observabilité d’une pipeline ETL — logs, métriques et diagnostic d’exécution  
**Durée indicative :** 1 h 30 à 2 h 30  
**Point de départ : ton code J17 — Slowly but Surely**, pas un nouvel ETL.

## 1. Situation métier

Ta pipeline d’historisation SCD2 fonctionne. Mais, quand un chargement échoue ou n’apporte aucune modification, un collègue ne doit pas avoir besoin de lire `main.py` ni d’inspecter directement les tables pour comprendre ce qui s’est passé.

Aujourd’hui, tu dois rendre **chaque exécution observable** : quelle source a été traitée, quand, combien de produits ont été lus, combien de versions ont changé, quelles étapes ont eu lieu, et si la transaction s’est terminée avec succès ou par un échec.

**On réutilise** ton `main.py`, `extract.py` et `load.py` du J17, ainsi que ses données et sa base SQLite. Aucun besoin de revenir au traitement des commandes, de construire une interface Web ni d’ajouter un serveur de monitoring.

## 2. Données

Le dossier `data/` fournit :

- Les quatre instantanés valides du J17 (01, 08, 15, 20 octobre).
- `catalog_2026-10-20_bad_price.json` : même instantané que celui du 20 octobre, mais un prix volontairement invalide sur **P003**, destiné à provoquer une erreur *pendant* le chargement.
- `reference_history.csv` : historique final de référence du J17.

**Attention :** pour le scénario d’échec, donne au programme la date d’effet **2026-10-20**, même si le fichier comporte le suffixe `_bad_price`. Ton extraction actuelle de la date depuis le nom du fichier pourrait donc demander une petite adaptation ; tu es libre de choisir une interface.

## 3. Contrat fonctionnel — 4/5

Tu obtiens **4/5** en respectant les propriétés suivantes :

1. **Identité de run :** chaque lancement porte un identifiant distinct, présent dans les informations d’observabilité qui lui correspondent.
2. **Traçabilité des étapes :** les traces permettent d’identifier au moins le début, l’extraction, le chargement et la fin de l’exécution (ou l’étape qui a échoué). Chaque trace est horodatée et indique un niveau de gravité approprié.
3. **Métriques métier :** un bilan par run indique au minimum le nombre de produits lus, le nombre de nouvelles versions insérées, le nombre d’anciennes versions clôturées, et la durée totale. Les valeurs doivent refléter **ce qui est réellement validé en base** ; sur un run annulé, il ne faut pas présenter des écritures annulées comme validées.
4. **Statut final :** chaque exécution permet de connaître son état final (`SUCCESS` ou `FAILED`). En cas d’échec, le diagnostic identifie la nature de l’erreur et l’étape concernée, sans avaler l’exception ni valider une transaction partielle.
5. **Persistance exploitable :** les traces et le bilan restent accessibles **après la fin du programme**, y compris après une erreur. Le format et les fichiers sont libres, mais doivent permettre d’identifier les événements d’un même run sans ambiguïté.
6. **Non-régression :** le comportement métier SCD2 du J17 ne doit pas changer : les quatre chargements réussis conservent neuf versions et les rechargements sans modification n’en créent aucune.

> Il n’est pas demandé d’ajouter de la télémétrie à chaque produit, ni de journaliser toutes les colonnes métier. L’enjeu est l’exploitation d’un run, pas le volume des logs.

## 4. Bonus d’ingénierie — 5/5

Le **5/5** exige le contrat fonctionnel **et** les deux propriétés suivantes, prouvées par des **tests automatisés** :

- **Bilan final fiable, même sur erreur :** chaque run produit **exactement un** bilan terminal exploitable. Après une exception survenue en cours de chargement, le bilan indique `FAILED`, renseigne l’étape en échec et ne revendique aucune modification *validée* en base ; l’historique SQLite reste inchangé.
- **Corrélation et isolation :** plusieurs exécutions successives, réussies ou échouées, conservent des identifiants distincts et leurs traces/bilans ne se mélangent pas. Les tests peuvent retrouver pour chaque identifiant le statut, les métriques et les étapes associées.

Aucune technique particulière n’est imposée : l’important est la vérifiabilité de ces propriétés, pas la bibliothèque de logging choisie.

## 5. Scénarios de vérification

Utilise un nouveau dossier de sortie / une base vide au départ, puis exécute les scénarios ci-dessous **dans l’ordre**, sur la même base. Le fichier `expected_runs.csv` résume les volumes métier attendus ; ce sont les **modifications validées** et non les opérations SQL tentées.

| Run | Source | Statut attendu | Produits lus | Versions insérées | Versions clôturées | Total versions en base |
|---|---|---|---:|---:|---:|---:|
| 1 | `catalog_2026-10-01.json` | SUCCESS | 4 | 4 | 0 | 4 |
| 2 | `catalog_2026-10-08.json` | SUCCESS | 4 | 1 | 1 | 5 |
| 3 | `catalog_2026-10-15.json` | SUCCESS | 5 | 2 | 1 | 7 |
| 4 | `catalog_2026-10-20_bad_price.json` (date 20/10) | FAILED | 5 | 0 validée | 0 validée | 7 |
| 5 | `catalog_2026-10-20.json` | SUCCESS | 5 | 2 | 2 | 9 |
| 6 | Rejouer `catalog_2026-10-20.json` | SUCCESS | 5 | 0 | 0 | 9 |

**Précision :** en cas d’échec en cours de traitement, le compteur « produits lus » peut représenter les produits extraits avant le chargement (ici 5). Tu peux aussi distinguer « lus », « examinés » et « validés » ; documente clairement leur sens. La durée n’a pas de valeur fixe attendue : elle doit seulement être mesurable et cohérente.

## 6. Livrables

- Ton code Python instrumenté, basé sur J17.
- Les traces persistées et un bilan consultable pour chaque exécution (format libre).
- Une courte explication de la lecture de ces artefacts : comment diagnostiquer le run 4 sans ouvrir le code ?
- Pour le 5/5 : tests automatisés des propriétés de la section 4.

## 7. Limites de périmètre

- Pas de service externe (Grafana, Prometheus, ELK, etc.).
- Pas de multithreading à ajouter.
- Pas de changement imposé à la structure de la table métier `catalog`.
- Pas d’architecture préconçue : commence par décrire les informations qu’un opérateur doit pouvoir retrouver, puis choisis ton organisation.

**Question de départ :** aujourd’hui, si ton chargement du 20 octobre échoue au troisième produit, quelles informations te manquent pour comprendre *quel run*, *à quelle étape*, et *avec quel impact sur la base* ?
