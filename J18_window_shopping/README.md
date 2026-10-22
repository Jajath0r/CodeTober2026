# CodeTober 2026 — J18 : Window Shopping

**Sujet :** SQL analytique — fonctions fenêtre (*window functions*)  
**Durée indicative :** 1 h 30 à 2 h 30  
**Point de départ : J17 — Slowly but Surely.** Garde ta table `catalog` historisée et réutilise la base `catalog.db` que tu as construite. **Aucune nouvelle pipeline Python à développer.**

## 1. Contexte

Le référentiel produits du J17 conserve plusieurs versions de chaque produit. On te demande maintenant de produire des analyses **en SQL**, sans écraser l'historique ni ramener systématiquement les résultats à une seule ligne par produit.

Un collègue veut pouvoir classer les produits par prix, parcourir leurs versions chronologiques, calculer leurs évolutions cumulées et comparer chaque produit au prix moyen actuel.

**Nouveau concept du jour :** les fonctions fenêtre permettent d'effectuer des calculs sur un groupe de lignes **tout en conservant le détail de chaque ligne**.

## 2. Données et démarrage

- **Base recommandée :** ta base SQLite `catalog.db` du J17, après les quatre instantanés. Elle doit contenir **9 versions pour 5 produits**.
- **Alternative autonome :** `data/j18_catalog.db`, base SQLite déjà prête avec les **mêmes 9 lignes**. Aucun import nécessaire.
- `data/catalog_history.csv` : copie lisible du même historique.
- `data/schema.sql` : structure indicative de la table `catalog`.
- `reference/*.csv` : sorties attendues pour chaque requête, **sans les requêtes solutions**.

Colonnes : `product_id`, `name`, `unit_price_cents` (entier), `valid_from` (inclus), `valid_to` (exclu, `NULL` = version active).

Tu peux travailler directement dans ton client SQLite habituel. Pas de `main.py` obligatoire, pas de modification du J17.

## 3. Exigences fonctionnelles — 4/5

Écris **quatre requêtes SQL distinctes**, à enregistrer dans les fichiers `01_ranking.sql`, `02_previous.sql`, `03_cumulative.sql`, `04_average.sql`.

### A — Classement des prix actuels

Retourner **une ligne par produit actif**, avec : `product_id`, `name`, `unit_price_cents`, `price_position`.

- Trier du **plus cher au moins cher**.
- `price_position` numérote les positions de 1 à N.
- En cas d'égalité de prix, départager par `product_id` croissant.
- Ne pas classer les anciennes versions comme si elles étaient actives.

Référence : `reference/01_current_price_ranking.csv` (**5 lignes**).

### B — Versions et prix précédent

Pour **toutes les versions**, retourner : `product_id`, `valid_from`, `unit_price_cents`, `version_number`, `previous_price_cents`.

- Numéroter les versions de chaque produit dans l'ordre chronologique, en repartant de 1 à chaque nouveau produit.
- Récupérer le prix de la version immédiatement précédente du **même** produit.
- Pour une première version, `previous_price_cents` doit être `NULL`.
- Trier la sortie par produit puis date.

Référence : `reference/02_versions_and_previous_price.csv` (**9 lignes**).

### C — Évolution cumulée du prix

Pour **toutes les versions**, retourner : `product_id`, `valid_from`, `unit_price_cents`, `delta_cents`, `cumulative_delta_cents`.

- `delta_cents` = différence de prix avec la version précédente du même produit ; `NULL` pour la première version.
- `cumulative_delta_cents` = somme des différences depuis la première version jusqu'à la version courante ; la première version commence à **0**.
- Le cumul doit recommencer à zéro pour chaque produit.
- Trier par produit puis date.

Référence : `reference/03_cumulative_price_changes.csv` (**9 lignes**).

### D — Écart à la moyenne courante

Retourner **une ligne par produit actif**, avec : `product_id`, `name`, `unit_price_cents`, `mean_price_cents`, `difference_to_mean_cents`.

- La moyenne porte sur les **cinq versions actives**, pas sur les neuf versions de l'historique.
- Répéter la même moyenne pour chaque ligne, en conservant chaque produit.
- Écart = prix du produit moins moyenne.
- Arrondir la moyenne et l'écart à **une décimale**.
- Trier par `product_id`.

Référence : `reference/04_current_price_vs_average.csv` (**5 lignes**).

**Pour obtenir 4/5 :** les quatre requêtes respectent le contrat et reproduisent les références. Tu dois avoir utilisé de véritables fonctions fenêtre SQL pour les calculs analytiques, pas une reconstruction intégralement côté Python.

## 4. Extension d'ingénierie — 5/5

**Garantir un classement déterministe et une interprétation correcte des égalités de prix**, quelle que soit l'ordre physique d'insertion des lignes.

- Le classement actuel doit rester identique si les lignes sont insérées dans un ordre différent.
- Des prix égaux doivent avoir des positions reproductibles selon la règle annoncée (prix décroissant, puis `product_id` croissant).
- Dans un scénario contenant des produits ex æquo, distinguer explicitement dans une courte explication la **position unique** d'un produit et son **rang par prix** (qui peut être partagé). Pour ce bonus, produis les deux valeurs dans une requête de classement, sans perdre les lignes des produits ex æquo.
- Vérifier ce comportement par au moins **un test automatisé** (ou un script SQL d'assertions exécutable) comparant deux ordres d'insertion.

`data/bonus_ties.csv` fournit **deux produits fictifs supplémentaires**, P006 à 4 700 centimes et P007 à 1 800 centimes, à injecter **dans une copie** de la base J18. Ne modifie pas l'historique J17 de référence. Le bonus ne requiert pas de réécrire tes quatre requêtes du 4/5, seulement de prolonger le classement.

L'énoncé exige les **propriétés observables**, pas une structure SQL particulière.

## 5. Vérifications simples

- A : cinq produits actifs ; le plus cher en première position.
- B : neuf versions au total, première version de chaque produit sans prix précédent.
- C : pour P001, changements successifs **+400 puis −200 centimes**, cumul **0 → 400 → 200**.
- D : cinq produits et la **même moyenne courante** sur chaque ligne.
- Bonus : les égalités de prix ne perturbent ni la stabilité des positions ni la distinction position/rang.

Tu peux comparer les résultats exportés à `reference/*.csv`. **Les valeurs de référence ne sont pas des solutions SQL.**

## 6. Périmètre et critères de fin

Aucune nouvelle ingestion, aucune modification des modèles SCD2, aucun ETL concurrent. Le J18 est volontairement un défi **SQL**, pour bien comprendre `PARTITION BY`, `ORDER BY`, les calculs de ranking, la comparaison à la ligne précédente et les cumuls. Les sous-requêtes ou CTE sont autorisées, sans architecture imposée.

**4/5 :** quatre analyses exactes. **5/5 :** bonus d'égalité et de déterminisme démontré par test. Les contraintes sont fixées dès le départ.
