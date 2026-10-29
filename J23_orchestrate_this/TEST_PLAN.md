# J23 — Plan de vérification (sans solution)

- Exécution nominale : 6 tâches réussies, ordre des dépendances respecté, résultat final conforme.
- DAG : ID dupliqué ; dépendance inconnue ; cycle de deux tâches ; aucune tâche métier exécutée.
- Retry transitoire : J23_FAIL_ONCE=aggregate : aggregate échoue puis réussit, 2 tentatives exactement ; publish réussit.
- Panne permanente : J23_FAIL_ALWAYS=aggregate : aggregate en échec après 1 tentative, publish bloqué et absent des événements d'exécution.
- Reprise : interrompre après que certaines tâches ont réussi, redémarrer avec le même run_id, contrôler le nombre de tentatives et l'historique des tâches réussies.
- Robustesse : lancement avec répertoire output neuf, puis reprise avec artefacts existants.
- Les 3 tests automatisés du README conditionnent le 5/5.
