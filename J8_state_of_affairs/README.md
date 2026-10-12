# J8 — State of Affairs

**Thème :** persistance locale, cohérence des écritures et transactions.  
**Durée indicative :** 45–120 min pour le socle ; approfondissement libre.  
**Stack :** Python, bibliothèque standard suffisante, pytest conseillé. Aucune infrastructure externe.

## Contexte

Tu reçois des fichiers d'opérations sur un portefeuille de comptes fictifs. Chaque opération demande un transfert d'un montant entier (en centimes) d'un compte source vers un compte destinataire. Ton application doit conserver durablement les soldes et l'historique des transferts entre deux exécutions indépendantes.

Les comptes initiaux sont dans `accounts.csv`. Chaque fichier `transfers_XX.csv` représente une livraison successive du même flux. Les identifiants d'opérations sont uniques dans les jeux de données fournis ; **la gestion des rejouements et des doublons sera le sujet de J9**, pas de J8.

## Contrat des fichiers

`accounts.csv` : `account_id,initial_balance_cents`.  
`transfers_XX.csv` : `transfer_id,source_account,destination_account,amount_cents`.

Les montants sont des entiers strictement positifs. Tous les comptes référencés existent. Les fichiers de transfert ne contiennent pas de ligne structurellement invalide. Les comptes ne peuvent pas devenir débiteurs. Les transferts sont traités **dans l'ordre du fichier**.

## Objectif — 4/5

Écrire un programme CLI qui :

1. Initialise **une seule fois** un stockage local persistant à partir de `accounts.csv`, sans réinitialiser les soldes aux exécutions suivantes.
2. Applique une livraison de transferts au stockage persistant.
3. Pour chaque transfert, débite le compte source et crédite le compte destinataire du même montant. Si le solde source est insuffisant, le transfert est **refusé intégralement**, sans changement des soldes.
4. Conserve un historique durable des transferts acceptés et refusés, avec leur identifiant, les deux comptes, le montant et le statut (`accepted` ou `rejected`).
5. Produit `balances.csv` (soldes à la fin de l'exécution) et `report.json` (statistiques du batch) dans un dossier de sortie.
6. Permet de relancer le programme sur un **nouveau batch** en réutilisant les soldes et l'historique précédents.

Rapport attendu : `batch`, `nb_read`, `nb_accepted`, `nb_rejected`, `total_balance_before_cents`, `total_balance_after_cents`. La somme totale des soldes doit être conservée après chaque batch. Un batch normal se termine avec `nb_read = nb_accepted + nb_rejected`.

**Périmètre :** pas de concurrence entre deux processus, pas de comptes créés en cours de route, pas de gestion de rejouement d'un même batch. L'historique est conservé dans le stockage persistant ; il n'est pas nécessaire de l'exporter en CSV.

## Contrainte d'ingénierie — 5/5

**Chaque transfert est une unité indivisible de modification durable.** Si l'exécution échoue entre ses différentes écritures, la reprise doit retrouver soit l'état *avant* le transfert, soit l'état *après* le transfert — **jamais un compte débité sans son crédit correspondant, ni un historique indiquant un transfert accepté dont les soldes ne reflètent pas l'effet**.

La propriété doit être démontrée par un test d'échec provoqué à un moment pertinent de l'application d'un transfert. Tu choisis toi-même où placer la frontière de réussite, comment assurer l'indivisibilité et comment vérifier l'état persistant après l'échec. **Il n'est pas demandé de reprendre automatiquement un batch interrompu :** on inspecte le stockage après le crash, puis on peut poursuivre avec un autre batch.

## Jeux de données

- `accounts.csv` : quatre comptes avec des soldes initiaux différents.
- `transfers_01.csv` : scénario nominal et refus pour fonds insuffisants.
- `transfers_02.csv` : second batch dépendant des soldes du premier.
- `transfers_stress.csv` : 3000 opérations pour vérifier les invariants à plus grande échelle ; **à lancer sur un stockage initialisé séparément**.
- `transfers_crash.csv` : petit scénario pour injecter une panne contrôlée ; **à lancer sur un stockage initialisé séparément**.

Les fichiers ne contiennent pas de résultats attendus tout faits : calcule quelques soldes à la main et écris des tests de référence.

## Vérifications conseillées

- Initialisation puis seconde exécution : les soldes ne sont pas réinitialisés.
- Refus pour fonds insuffisants : aucun des deux soldes ne change, et l'historique porte `rejected`.
- Deux batches successifs : le second utilise les soldes du premier.
- Après chaque transfert réussi : somme des soldes inchangée.
- Test de panne 5/5 : inspecter soldes **et** historique après l'échec, pas seulement le report.

## Questions à te poser avant de coder

Quelles données constituent la vérité durable ? Quelles modifications appartiennent à une même opération métier ? À quel instant un transfert devient-il définitivement accepté ? Et si le programme s'arrête exactement entre deux écritures ?

**Livrables :** `main.py`, tests automatisés, README court avec commandes d'exécution et description du crash-test. Pas de framework imposé.
