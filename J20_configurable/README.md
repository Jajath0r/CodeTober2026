# CodeTober 2026 — J20 · Configurable 🎃

**Thème :** pipeline pilotée par configuration.  
**Durée visée :** 1 h 30 à 2 h 30.  
**Base de départ :** ton ETL SCD2 du J17, enrichi de l'observabilité du J19.  
**Bibliothèques :** standard Python et SQLite suffisent ; une bibliothèque de validation est autorisée mais non imposée.

## Contexte

Ton ETL sait déjà historiser des catalogues et journaliser ses exécutions. En revanche, pour changer de source, de base de destination ou de stratégie face à une donnée invalide, tu dois encore adapter le code ou ses arguments. On veut maintenant décrire **quoi traiter et avec quelles règles** dans un fichier de configuration, sans modifier la logique métier.

Objectif : **un seul programme**, exécuté sur plusieurs configurations JSON, produisant les comportements attendus. Les configurations sont des *données déclaratives*, pas des instructions Python à exécuter.

## Contrat fonctionnel — 4/5

1. Le programme accepte **un chemin de configuration JSON** comme argument d'entrée. Toutes les informations nécessaires à l'exécution proviennent de ce fichier. Exemple d'interface possible : `python main.py configs/01_initial.json` (la commande est indicative).
2. Une configuration conforme possède **les trois blocs requis** `source`, `destination`, `behavior` avec les champs :
   - `source.path` : chemin du JSON catalogue ;
   - `destination.sqlite_path` : chemin de la base SQLite ;
   - `behavior.invalid_product` : `fail` ou `skip`.
3. Les chemins des fichiers figurant dans la configuration sont interprétés **relativement au dossier contenant la configuration**, et non relativement au répertoire depuis lequel le programme est lancé. Les dossiers nécessaires à la sortie sont créés si besoin.
4. Le chargement conserve le comportement SCD2 existant : dates `valid_from` inclusives, `valid_to` exclusives, aucune nouvelle version si le produit est inchangé, transaction métier atomique en mode `fail`.
5. Le mode `fail` est strict : au premier produit invalide, le chargement échoue, toute modification métier du *run* est annulée, et l'échec est journalisé. Le mode `skip` traite les autres produits valides et **ignore uniquement** les produits dont les données sont invalides ; les anomalies de configuration, de lecture du fichier ou de base SQLite restent des échecs. Un produit invalide est, pour ces fixtures, un prix qui ne peut pas être interprété comme entier. Pas de comportement de rattrapage supplémentaire requis.
6. L'observabilité du J19 reste présente : **un bilan terminal par tentative qui atteint le traitement**, statut, source, volumes et durée. Une erreur métier en mode `fail` ne doit pas effacer le bilan ; un produit ignoré en mode `skip` ne doit pas augmenter `nb_inserted_lines`. `nb_processed_lines` compte les produits valides traités complètement ; les produits ignorés ne sont pas inclus.
7. Les configurations invalides sont refusées **avant toute mutation du catalogue**, avec un message d'erreur compréhensible (clé obligatoire manquante, mauvais type, valeur de mode inconnue, JSON de configuration malformé). L'absence d'un fichier *source* valide demeure un échec d'exécution et doit être journalisée si l'environnement de journalisation est disponible.
8. Un rejeu identique n'ajoute pas de version SCD2. Deux configurations pointant vers des bases différentes ne doivent jamais partager accidentellement leur historique métier.

### Point d'attention

Le nom `catalog_2026-10-20_invalid.json` contient une date valide. Le suffixe `_invalid` n'est pas la date : l'exécution doit exploiter **la date `2026-10-20`**. Tu peux décider de ta méthode d'extraction ou de validation, mais elle doit fonctionner pour les noms fournis.

## Bonus d'ingénierie — 5/5 (explicite dès le départ)

En plus du contrat 4/5, ta configuration doit avoir un **contrat strict et prévisible**, démontré par **des tests automatisés** :

- Les champs inconnus (y compris au niveau racine) sont refusés au lieu d'être silencieusement ignorés ; aucune clé ne peut déclencher une action non prévue.
- Une configuration invalide ne doit créer **ni nouvelle base SQLite métier, ni historique de run**, même si le chemin de sortie désigne un dossier encore inexistant.
- Une même configuration exécutée depuis deux répertoires de travail différents doit produire **exactement la même destination et le même état métier**, sans doublons dus au répertoire courant.

Le bonus n'impose ni bibliothèque particulière, ni architecture précise : il porte sur les propriétés vérifiées, pas sur la solution technique.

## Données fournies

- `data/` : 5 instantanés JSON, dont un avec un prix invalide ; produits synthétiques, aucun appel réseau.
- `configs/01_...` à `08_...` : scénarios de réussite, rejeu, échec, `skip` et destination isolée.
- `configs/09_...` à `11_...` : configurations volontairement invalides à utiliser pour les tests.
- `TEST_PLAN.md` : séquence de vérification et invariants.
- `reference/expected_runs.csv` : compteurs et états métier attendus, **sans indiquer l'implémentation**.

## Limites volontaires du J20

Pas d'Airflow, Docker, moteur de templating, YAML obligatoire, moteur de règles configurable ni registre de plugins. On cherche un pilotage **simple, explicite et maintenable**. Réutilise tes fonctions existantes autant que possible, plutôt que de réécrire la SCD2.

## Rendu attendu

Ton code (`main.py`, `extract.py`, `load.py`, etc.), tes configurations de test si tu les ajustes, ainsi que les résultats de validation (captures, SQL de contrôle ou tests). Le correcteur vérifie le **résultat** et les garanties du barème, pas la forme des modules.

## Notation

- **4/5 :** exigences fonctionnelles ci-dessus respectées.
- **5/5 :** les trois propriétés du bonus sont démontrées automatiquement.
- Si les exigences fonctionnelles ne sont pas satisfaites, note inférieure à 4/5 selon les écarts constatés.

Bon CodeTober ! 🐍
