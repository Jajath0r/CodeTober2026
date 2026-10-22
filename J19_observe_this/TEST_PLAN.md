# J19 — Plan de vérification (sans solution technique)

## Contrat 4/5 — observations manuelles

- [ ] Partir d’une base vide et exécuter les six scénarios dans l’ordre du README.
- [ ] Retrouver pour chaque exécution son identifiant, sa source, sa date d’effet, ses étapes et sa durée.
- [ ] Comparer volumes et statut à `expected_runs.csv`.
- [ ] Sur le scénario 4, voir l’étape en échec et la cause, confirmer que la base est restée à 7 versions.
- [ ] Sur le scénario 5, confirmer que le chargement normal réussit après l’échec précédent.
- [ ] Sur le scénario 6, confirmer qu’aucune nouvelle version n’apparaît.
- [ ] Fermer le programme ; vérifier que le diagnostic est toujours consultable.

## Bonus 5/5 — propriétés à automatiser

- [ ] Vérifier automatiquement le nombre de bilans terminaux : un seul par identifiant de run.
- [ ] Forcer un échec *après* au moins une modification tentée ; vérifier `FAILED`, absence d’écriture validée et base inchangée.
- [ ] Faire plusieurs runs consécutifs, y compris un échec ; leurs identifiants sont distincts et les événements sont attribuables sans ambiguïté.
- [ ] Vérifier qu’un lancement échoué ne laisse pas une métrique ou un statut qui serait attribué au lancement suivant.

Les tests peuvent invoquer directement tes fonctions ou lancer ton programme en sous-processus. Tu choisis.
