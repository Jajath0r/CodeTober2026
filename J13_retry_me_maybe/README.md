# CodeTober 2026 — J13 : Retry Me Maybe

**Thème :** résilience aux erreurs transitoires  
**Durée visée :** 1 h 30 à 2 h 30, tests compris  
**Point de départ :** ta pipeline ETL du J12 (`main.py`, `extract.py`, `transform.py`, `load.py`, `models.py`).

## 🎯 Objectif

Le catalogue produits de ton ETL ne vient plus d'un fichier lu directement par ton code : il est récupéré via une **source simulée** qui peut subir des interruptions temporaires ou refuser définitivement l'accès. Le traitement doit récupérer le catalogue quand c'est possible, sans réessayer indéfiniment ni masquer les erreurs.

**Seule nouveauté du jour :** une stratégie de reprise pour l'acquisition du catalogue. **Ne réécris pas** les transformations ni le chargement du J12.

## 📥 Matériel fourni

| Fichier | Rôle |
|---|---|
| `simulator.py` | Source de catalogue simulée, prête à importer ; ne pas la modifier |
| `data/catalog.json` | Catalogue utilisé par le simulateur |
| `data/orders.csv` | 12 commandes, schéma `quantity` du J12 |

Utilisation du simulateur (contrat d'interface, pas une solution au défi) :

```python
from simulator import SimulatedCatalogSource, TransientSourceError, PermanentSourceError

source = SimulatedCatalogSource("data/catalog.json", scenario="two_outages")
catalog_data = source.fetch()  # objet JSON décodé : {"products": [...]}
print(source.calls)            # nombre de tentatives effectuées
```

**Important :** conserve **la même instance** de `source` pendant toutes les tentatives. `fetch()` peut lever une des deux exceptions annoncées. Le dictionnaire retourné a le même format que celui de ton ancien `get_catalog()` avant construction de l'index par `product_id`.

Tu peux choisir librement comment sélectionner le scénario (argument CLI, paramètre d'une fonction, etc.). Le nom du scénario doit pouvoir changer **sans modifier le code source**.

## ✅ Obligatoire — 4/5

1. **Distinguer les erreurs.** En cas de `TransientSourceError`, une nouvelle tentative est autorisée. En cas de `PermanentSourceError`, interrompre immédiatement le traitement et signaler l'erreur.
2. **Limiter les tentatives.** Au maximum **3 appels à `fetch()` au total**, premier appel compris. Si les 3 échouent temporairement, le traitement échoue explicitement.
3. **Préserver le chargement.** En cas d'échec définitif de récupération du catalogue, **aucune nouvelle vente** ne doit être enregistrée. Si le catalogue est obtenu, la pipeline conserve les résultats et la rejouabilité du J12.
4. **Tester les scénarios.** Vérifier les cinq scénarios ci-dessous, notamment le nombre d'appels et le contenu de `sales`.

## ⭐ Bonus — 5/5

Les nouvelles tentatives après une panne temporaire ne doivent **pas être immédiates** : leurs délais doivent être **progressifs et plafonnés à 1 seconde**. Les tests automatisés doivent pouvoir vérifier la progression et le plafond **sans subir de véritables pauses**. Ne pas attendre avant la première tentative ni après l'ultime échec.

*Les propriétés sont imposées, pas le mécanisme de mise en œuvre.*

## 🧪 Scénarios et résultats attendus

| Scénario | Comportement de la source | Nombre d'appels à `fetch()` | Résultat de la pipeline |
|---|---|---:|---|
| `healthy` | Fonctionne immédiatement | 1 | Succès |
| `one_outage` | 1 échec temporaire puis succès | 2 | Succès |
| `two_outages` | 2 échecs temporaires puis succès | 3 | Succès |
| `unavailable` | Toujours en échec temporaire | 3 | Échec explicite, aucun nouveau chargement |
| `access_denied` | Échec définitif | 1 | Échec immédiat, aucun nouveau chargement |

Pour **chaque scénario**, partir d'une base `sales` vide afin de vérifier le résultat de façon indépendante. Pour les scénarios réussis :

- **8 ventes** dans `sales` ;
- **27 100 centimes** pour `SUM(total_cents)` ;
- en rejouant avec le même scénario sur la même base, toujours **8 ventes** et **27 100 centimes**.

Pour les scénarios en échec : **0 vente nouvelle**. Dans une base contenant déjà des ventes, celles-ci ne doivent pas disparaître.

L'ordre, le nommage et les autres détails d'implémentation restent libres. Les tests peuvent simuler les erreurs avec l'objet fourni ; aucune connexion réseau n'est nécessaire.

## ♻️ À réutiliser

- Ton `create_sales_row()` et ta validation des schémas J12.
- Ta table SQLite `sales` et `insert_row_in_sales()`.
- Ta séparation en modules et ta gestion des transactions.

Tu peux adapter la fonction d'extraction du catalogue pour utiliser la source simulée. **Pas de nouveaux exports, métriques d'audit, règles de qualité ou orchestrateur à développer.**

## 💡 Point d'attention

Un retry ne doit pas changer le résultat métier : il sert à faire aboutir une opération temporairement indisponible, pas à répéter aveuglément tout le chargement. Le simulateur couvre seulement la récupération du catalogue ; inutile d'étendre la gestion des pannes à SQLite pour ce défi.
