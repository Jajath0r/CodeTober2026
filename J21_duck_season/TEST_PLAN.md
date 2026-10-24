# J21 — Plan de vérification (sans solution SQL)

## Démarrage

1. Installer `duckdb` dans l'environnement Python utilisé pour CodeTober.
2. Lancer le programme sur `data/`, avec un `output/` vierge.
3. Comparer les trois CSV produits aux trois fichiers `reference/` : schéma, valeurs, ordre des lignes.
4. Relancer sans nettoyer `output/` et vérifier que les fichiers restent identiques.

## Contrôles particulièrement importants

- Les trois rapports doivent être calculés sur **les mêmes ventes éligibles** (`completed` uniquement).
- Les commandes `O9001`, `O9002` et `O9003` servent d'indices : `O9001` a deux lignes de vente ; `O9002` est annulée malgré un montant très élevé ; `O9003` est en attente.
- Le 14 octobre 2026 doit tenir compte de `O9001` **une seule fois** dans son nombre de commandes, mais inclure ses trois unités.
- Dans `top_products.csv`, l'ordre en cas d'égalité doit être stable.
- Le prix catalogue n'est pas nécessairement une vérité historique ; calculer sur les prix des lignes.

## Bonus automatisé

Créer de petites données de test isolées, puis vérifier les trois invariants explicités dans `README.md`. Pour tester l'égalité de rang, construire deux produits à chiffre d'affaires identique et permuter l'ordre d'entrée des lignes.

Ne pas se contenter d'assertions qui vérifient seulement que les fichiers ont été créés : contrôler leur **contenu**.
