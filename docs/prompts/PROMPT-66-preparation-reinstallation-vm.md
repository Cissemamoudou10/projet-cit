# Prompt 66 — Préparer la réinstallation à la lettre de la VM

Contexte : phase 7. Code gelé au tag `recette-phase-6-c11`. Je vais rejouer
l'installation sur une VM Debian 12 neuve, hors ligne, puis tester
sauvegarde et restauration. Procédure : `docs/recette/REINSTALLATION-VM.md`
(lis-la en premier). Tu prépares ; tu ne touches jamais à la VM.

1. **Vérifier que le code à empaqueter est le code gelé** :
   `git diff recette-phase-6-c11 HEAD -- app Dockerfile requirements.txt compose`
   doit être vide. Sinon, arrête-toi et rends compte.

2. **Combler l'écart trouvé à la préparation** : `INSTALLATION.md` ne cite
   jamais `initialiser_gabarits_documents` (catalogue de référence requis en
   production, voir sa docstring). Ajoute un § 8 ter, au bon endroit dans
   l'ordre des dépendances (vérifie dans le code s'il exige un compte
   administrateur, comme les grilles). Consigne-le dans `PROBLEMES.md` sous
   le numéro suivant, et remplace `P-xx` dans la procédure. Vérifie aussi
   qu'aucune autre commande d'initialisation nécessaire en production
   n'est absente de `INSTALLATION.md`.

3. **Vérifier que `charger_jeu_demonstration` s'exécute avec
   `config.settings.production`** (aucune dépendance de développement,
   aucun garde-fou qui le refuse). Si ce n'est pas le cas, ne modifie pas le
   code : propose dans le compte rendu un autre moyen de charger des
   données fictives, et adapte le § 3.1 de la procédure.

4. **Écrire `verification-restauration/releve.sql`** et le faire copier
   dans le paquet par `scripts/constituer-paquet.sh`. Sortie stable et
   triée, pour un `diff` direct : une ligne `table|nombre_de_lignes` par
   table du schéma `public` (comptage exact, pas les statistiques), puis le
   résultat de `has_table_privilege` du rôle applicatif sur
   `administration_entree_journal` pour UPDATE et DELETE (attendu : `f`),
   puis le nombre de migrations appliquées. Teste le script sur une base
   locale **en lecture seule**, sans réinitialiser aucune base.

5. **Reconstruire le paquet** avec `scripts/constituer-paquet.sh` (version
   par défaut `hors-ligne`, celle que cite la doc). Ajoute au paquet un
   `MANIFESTE.txt` : commit, tag, date, ID des deux images, SHA-256 de
   chaque `.tar`, taille totale. Si le script échoue (versions épinglées
   devenues introuvables, par exemple), arrête-toi et rends compte : ne
   change aucune version sans mon accord.

6. **Commit** (doc, script, procédure, prompt) ; le paquet reste hors
   versionnement.

Règles permanentes : ne tue aucun processus ; ne réinitialise ni ne
supprime aucune base ; un seul processus pytest/PostgreSQL à la fois ;
ne modifie pas tes propres permissions.

Compte rendu attendu : écarts trouvés, numéro P attribué, taille et
empreintes du paquet, durée de la construction.
