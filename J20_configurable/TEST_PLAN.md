# J20 — Plan de tests (sans solution)

Utilise un dossier `output/` vierge au départ. **Respecte l'ordre** de la séquence principale : les configurations 01 à 06 et 08 partagent la même base.

## Séquence principale

| Ordre | Configuration | Résultat attendu |
|---|---|---|
| 1 | `01_initial.json` | SUCCESS, 3 versions insérées, 3 traitées |
| 2 | `02_update.json` | SUCCESS, 2 versions insérées, 4 traitées |
| 3 | `03_rename.json` | SUCCESS, 2 versions insérées, 4 traitées |
| 4 | `04_replay.json` | SUCCESS, 0 version insérée, 4 traitées |
| 5 | `05_invalid_fail.json` | FAILED (`ValueError`), 0 insertion conservée, historique métier inchangé |
| 6 | `06_invalid_skip.json` | SUCCESS, 2 versions insérées, 4 produits valides traités ; 1 ignoré |
| 7 | `08_valid_followup.json` | SUCCESS, 0 nouvelle version insérée, 5 traités |

Après l'étape 4, la base métier doit contenir **7 versions** pour 4 produits ; après l'étape 5, toujours 7 ; après l'étape 6, **9 versions** pour 5 produits. Après l'étape 7, toujours 9 versions. Les changements invalides ne doivent jamais apparaître en base.

## Destination isolée

Exécute `07_isolated.json` séparément. La base `output/secondary/catalog.db` doit contenir 3 versions initiales et ne doit pas modifier la base principale.

## Configurations invalides

Teste `09_invalid_policy.json`, `10_unknown_key.json`, `11_missing_destination.json` sur une sortie vierge : erreurs explicites, **aucune mutation métier**. Crée aussi un fichier de configuration au JSON syntaxiquement invalide.

## Contrôles utiles

```sql
SELECT product_id, name, unit_price_cents, valid_from, valid_to
FROM catalog
ORDER BY product_id, valid_from;
```

```sql
SELECT status, source, nb_processed_lines, nb_inserted_lines, duration_ms
FROM logging
ORDER BY rowid;
```

La seconde requête suppose que tu conserves les noms de colonnes du J19 ; adapte-la à ton implémentation sans changer l'information attendue.

## Bonus

1. Injection d'un champ inconnu dans une configuration autrement correcte : refus.
2. Validation d'une configuration invalide dont la destination n'existe pas encore : aucune base ni ligne de run créées.
3. Exécution de la même configuration en changeant le `cwd` : résolution identique des chemins et état métier identique.

Utilise `pytest` si tu veux, mais n'écris pas les tests uniquement pour le cas heureux.
