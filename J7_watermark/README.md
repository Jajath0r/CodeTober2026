# J7 — Watermark

## 🎯 Objectif

Jusqu'ici, chaque exécution de tes programmes pouvait considérer son fichier d'entrée comme un nouveau traitement complet.

À partir de maintenant, on change de logique.

Un système amont dépose régulièrement des exports contenant des événements. Deux exports successifs peuvent se chevaucher : une nouvelle livraison peut contenir à la fois des événements déjà couverts par un run précédent et de nouveaux événements.

Ton programme doit devenir **incrémental** : il doit savoir jusqu'où il est déjà allé et ne traiter que ce qui est réellement nouveau.

---

## 📥 Données d'entrée

Chaque fichier CSV contient les colonnes suivantes :

```text
event_id
event_timestamp
customer_id
event_type
amount
source
```

`event_timestamp` suit le format :

```text
YYYY-MM-DD HH:MM:SS
```

⚠️ Les lignes du fichier **ne sont pas garanties dans l'ordre chronologique**.

Certaines lignes peuvent contenir un `event_timestamp` invalide.

---

# ⭐ Objectif 4/5 — Ingestion incrémentale

Ton programme reçoit :

```text
input_csv
output_repository
```

Il doit maintenir entre les différentes exécutions un **watermark** représentant la frontière temporelle jusqu'à laquelle les données ont déjà été intégrées avec succès.

### Premier run

Lorsqu'aucun état précédent n'existe :

- toutes les lignes valides sont éligibles au traitement ;
- les lignes dont `event_timestamp` est invalide sont rejetées ;
- à la fin du traitement, le watermark doit représenter le timestamp valide le plus avancé couvert par ce run.

### Runs suivants

Lorsqu'un watermark existe déjà :

- seules les lignes **strictement nouvelles** par rapport au watermark doivent être traitées ;
- les anciennes lignes doivent être ignorées ;
- les lignes invalides doivent être rejetées ;
- une ligne invalide ne doit jamais faire progresser le watermark ;
- à la fin du run, le watermark doit être mis à jour.

L'ordre des lignes dans le fichier ne doit pas modifier le résultat.

---

## 📤 Sorties attendues

### `output.csv`

Contient uniquement les lignes effectivement traitées pendant **ce run**.

Le fichier conserve les colonnes du fichier source.

### `report.json`

Il contient au minimum :

```json
{
  "nb_read_lines": 0,
  "nb_invalid_lines": 0,
  "nb_processed_lines": 0,
  "nb_skipped_lines": 0,
  "watermark_before": null,
  "watermark_after": null
}
```

Tu peux ajouter d'autres métriques si elles te semblent pertinentes.

---

## 🔁 Relance et idempotence

Une fois un fichier traité avec succès, rejouer exactement la même entrée ne doit pas reproduire les données déjà couvertes.

De même, si deux livraisons se chevauchent, les anciennes données présentes dans la deuxième livraison ne doivent pas être retraitées.

Autrement dit :

```text
run 1
→ nouvelles données
→ traitement
→ watermark

run 2
→ anciennes données + nouvelles données
→ seules les nouvelles sont traitées
→ nouveau watermark
```

---

# ⭐⭐⭐⭐⭐ Objectif 5/5 — Watermark fiable

Ton pipeline doit respecter la propriété suivante :

> **Un run qui échoue avant d'avoir terminé ne doit jamais faire perdre des données au run suivant.**

L'état durable indiquant la progression du pipeline ne doit devenir le nouvel état de référence que lorsque le run peut être considéré comme **réussi**.

Exemple conceptuel :

```text
watermark existant
        ↓
début du nouveau run
        ↓
traitement partiel
        ↓
💥 erreur / interruption
        ↓
relance
```

La relance doit encore être capable de traiter **toutes les données qui n'avaient pas été intégrées avec succès avant l'échec**.

À toi de déterminer :

- quel état doit être conservé ;
- quand il peut être modifié ;
- ce que signifie exactement un « run réussi » ;
- comment empêcher un traitement incomplet de faire avancer définitivement la frontière d'ingestion.

Aucune architecture ni structure particulière ne t'est imposée.

La propriété attendue est donnée.

**Le mécanisme permettant de la garantir fait partie du défi.**

---

## 🧪 Tests attendus

Écris des tests unitaires sur les fonctions contenant ta logique métier.

Les scénarios importants doivent notamment te permettre de vérifier le comportement face à :

- une première ingestion ;
- des données antérieures au watermark ;
- des données postérieures au watermark ;
- un timestamp invalide ;
- des données non triées ;
- une relance.

Tu es libre de déterminer les autres cas pertinents.

---

## 📦 Jeux de données

Deux petits fichiers sont fournis pour raisonner rapidement :

```text
mini_run_01.csv
mini_run_02.csv
```

Puis trois livraisons constituent le scénario principal :

```text
events_run_01.csv
events_run_02.csv
events_run_03.csv
```

Elles doivent être exécutées **dans cet ordre**, en conservant l'état entre les runs.

Elles peuvent contenir :

- des périodes qui se chevauchent ;
- des timestamps non triés ;
- des événements déjà présents dans une livraison précédente ;
- quelques duplications ;
- des lignes invalides.

---

## 🧨 Validation du 5/5

Une fois ton implémentation fonctionnelle :

1. lance un traitement ;
2. provoque volontairement une erreur ou une interruption avant sa fin ;
3. observe l'état persistant ;
4. relance le programme ;
5. vérifie qu'aucune donnée qui devait encore être traitée n'est devenue invisible à cause de l'échec précédent.

---

## 🧠 Contraintes

- Python ;
- bibliothèque standard suffisante ;
- pas besoin de `pandas` ;
- tests unitaires avec `pytest` ;
- architecture libre.

Comme pour les défis précédents, **le 5/5 n'impose pas une solution technique cachée** : il impose une propriété supplémentaire à ton implémentation.

---

## 💡 Avant de coder

Pour celui-ci, commence par répondre sur papier à trois questions :

```text
Quel est mon état AVANT un run ?

Qu'est-ce qui peut changer PENDANT le run ?

Qu'est-ce que j'ai le droit de considérer comme acquis APRÈS un run réussi ?
```

Si ces trois états sont clairs, l'architecture devrait commencer à apparaître toute seule.

Bon courage. 😈