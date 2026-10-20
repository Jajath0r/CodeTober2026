# CodeTober 2026 — J15 : Parallel Universe 🐍

**Notion :** concurrence pour des opérations I/O indépendantes  
**Durée visée :** 1 h 30 à 2 h 30, tests compris  
**Départ :** petit programme autonome. Tu réutilises tes acquis du J13/J14, **pas besoin de refactoriser l'ETL**.

## 🎯 Objectif

Cinq fournisseurs proposent des catalogues indépendants. Un fournisseur peut échouer ; les autres doivent continuer. Récupère les catalogues **concurremment** tout en limitant le nombre de requêtes simultanées.

Le défi est de **piloter des appels indépendants et récupérer leurs résultats**, pas de construire une vraie API ni un système de files d'attente.

## 📥 Fichiers fournis

| Fichier | Usage |
|---|---|
| `simulator.py` | Simule des appels bloquants avec des durées variables et des erreurs ; **ne pas modifier** |
| `data/providers.json` | 5 fournisseurs dont `gamma` qui échoue |
| `data/providers_all_ok.json` | Les 5 fournisseurs réussissent |
| `data/providers_fast.json` | 4 fournisseurs rapides pour les tests |

### Comment utiliser le simulateur

```python
from simulator import SupplierSimulator, ProviderError

source = SupplierSimulator("data/providers.json")
print(source.provider_ids)  # noms à traiter
products = source.fetch("alpha")  # liste de produits (appel bloquant)
```

Lève `ProviderError` pour les fournisseurs configurés avec `fail: true`. **Conserve la même instance** de `SupplierSimulator` pour tout un run : elle mesure les appels simultanés. Cette simulation ne nécessite aucun accès réseau.

Le simulateur expose aussi :
- `source.max_active_calls` : maximum réel d'appels simultanément en cours ;
- `source.active_calls` : appels actuellement en cours ;
- `source.call_count` : appels réalisés par fournisseur ;
- `source.finished_order` : ordre réel de fin des appels (indicatif, peut varier).

## ✅ Obligatoire — 4/5

1. **Exécution concurrente.** Récupérer tous les fournisseurs avec plusieurs appels potentiellement en cours simultanément. Test attendu : `max_active_calls > 1` sur `providers.json` lorsque la limite demandée est de 2 ou plus.
2. **Résultats associés aux bons fournisseurs.** Retourner une structure exploitable associant chaque `provider_id` soit à ses produits, soit à son erreur. Aucune confusion même lorsque l'ordre de fin est différent de celui du fichier.
3. **Échec isolé.** Une erreur d'un fournisseur ne bloque pas les autres : `gamma` échoue dans `providers.json`, les quatre autres réussissent. Ne pas masquer cet échec en succès.
4. **Concurrence plafonnée.** Le programme permet de choisir une limite (au moins **1** et **2**) **sans modifier le code source** : un paramètre de fonction suffit. Vérifier que `source.max_active_calls <= limit`.

**Contrat du résultat :** tu choisis son format exact, mais il doit être possible d'identifier pour chacun des cinq fournisseurs son nom, son statut `SUCCESS` ou `FAILED`, ses produits en cas de succès et une information d'erreur en cas d'échec. Un fournisseur doit être appelé **une seule fois** pendant un run.

## ⭐ Bonus — 5/5

**Résultats déterministes et preuve testable de la concurrence.** Pour deux runs sur le même fichier avec la même limite, la présentation des résultats doit suivre le **même ordre stable** (par exemple l'ordre des `provider_id`), même si les appels se terminent différemment. Les tests doivent vérifier **sans mesure de durée** :

- la limite maximale d'appels simultanés ;
- qu'au moins deux appels se sont chevauchés quand la limite est de 2 ou plus ;
- que les résultats restent associés aux bons fournisseurs.

Tu es libre de choisir l'outil Python. Aucun mécanisme précis n'est imposé.

## 🧪 Résultats de référence

Pour `data/providers.json` (5 fournisseurs) :

| Fournisseur | Statut | Produits attendus |
|---|---|---:|
| `alpha` | `SUCCESS` | 2 |
| `beta` | `SUCCESS` | 1 |
| `gamma` | `FAILED` | — |
| `delta` | `SUCCESS` | 2 |
| `epsilon` | `SUCCESS` | 1 |

**Total : 4 succès, 1 échec, 6 produits récupérés.**

Avec `providers_all_ok.json` : **5 succès, 0 échec, 6 produits**. Avec `providers_fast.json` : **4 succès, 0 échec, 5 produits**.

**Cas de contrôle recommandés :** limite 1 (aucun chevauchement), limite 2 (chevauchement sans dépasser 2), un fournisseur en panne, association correcte des produits, ordre final stable (bonus).

## ⏱️ Mesurer le gain réel (sans critère chronométrique)

Tu peux mesurer le temps du même dataset avec une limite de 1 puis de 2 ou 4. Note tes résultats et explique ce qui change. Les temps varieront selon ta machine : **aucune durée maximale n'est imposée**, et les assertions de tests ne doivent pas dépendre d'un chronomètre.

## ♻️ Périmètre

Les fichiers d'entrée sont des **fixtures**, pas des données métier à nettoyer. Tu ne dois pas ajouter de base SQLite, de retry, d'orchestrateur DAG, de validation qualité complexe, ni de traitement des produits.

Tu peux écrire `main.py` et `concurrent_fetch.py` si cela t'aide, mais aucune organisation de fichiers n'est exigée. Le résultat attendu est **un programme simple, testable, qui traite les cinq fournisseurs**.
