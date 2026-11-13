# Prompt 64 — Lot d'ergonomie (epic E9) et US-EVAL-12, avant RECETTE-05

**Contexte.** Dernier lot fonctionnel du projet : après lui, plus aucune évolution (R32). Les quatre stories sont décrites, avec leurs critères d'acceptation, dans `docs/livrables/04_Backlog_produit_v12_2026-11-08.md` (§ 10 bis pour US-IHM-01 à 03, § Évaluations pour US-EVAL-12) : **lis-les d'abord, ils font foi**. Travaille dans un **worktree**. Aucune remise à zéro de `pfe_cit_recette`, aucun arrêt de processus, aucune modification de tes propres permissions.

Temps 0 : une ligne dans `heures-phase-6.md`, estimation par story. **Temps limité : 6 heures.** Si tu le dépasses, arrête-toi après la story en cours et dis-moi ce qui reste.

## Ordre de réalisation

1. **US-IHM-02 — Identité visuelle et barre de navigation** (2 pts).
   - Logo : **je fournis le fichier**. S'il n'est pas dans `app/noyau/static/images/logo.png` quand tu commences, utilise un emplacement neutre (sigle « CIT » en texte, couleurs de la charte), avec un seul point de remplacement. **N'invente ni ne télécharge aucun emblème.**
   - Le logo apparaît sur la page de connexion, dans la barre de navigation et comme favicon.
   - Déconnexion et changement de mot de passe dans un menu déroulant du compte (nom et profil de l'utilisateur affichés).
   - La barre ne se déforme pas d'une rubrique à l'autre : vérifie-le par un test en navigateur réel (`-m navigateur`).
2. **US-IHM-03 — Rechercher, filtrer et trier les listes de stagiaires** (3 pts). Listes des moyennes et des procès-verbaux : pagination, recherche, filtre, tri, avec **le même composant** que les autres listes. Saisie des notes : recherche et filtre **sans pagination** ; prouve par un test qu'aucune note saisie n'est perdue quand on filtre.
3. **US-EVAL-12 — Détailler la moyenne d'un stagiaire** (3 pts). **Aucun second calcul** : le détail réutilise exactement les fonctions de `ServiceMoyenne` ; ajoute un test d'architecture `test_calcul_unique_moyenne.py` sur le patron des trois existants. Le détail doit permettre de retrouver à la main la moyenne et le rang affichés.
4. **US-IHM-01 — Tableau de bord d'accueil** (5 pts). Page d'arrivée après connexion. Chaque bloc est filtré par habilitation (un profil ne voit jamais un chiffre qu'il ne peut pas consulter ailleurs) : test par profil. Les chiffres proviennent des services existants, jamais recalculés dans la vue. **Nombre de requêtes constant**, prouvé par un test avec témoin : même page, deux volumes de données, même nombre de requêtes.
5. **Hors story, deux petits points :**
   - `PLAFOND_HEBDOMADAIRE_COEFFICIENT` transmis au conteneur application dans `docker-compose.production.yml`, ajouté à `.env.exemple` avec la valeur 1.5, et procédure de modification documentée dans `docs/exploitation/EXPLOITATION.md` (modifier `.env`, redémarrer le conteneur application).
   - L'addendum du 12 novembre en tête de `docs/suivi/CONTRAINTES-SOLVEUR.md` est déjà écrit dans le répertoire principal : intègre-le tel quel dans ton commit de documentation.

## Fin

- Relecture `relecteur-conception` de chaque story.
- Suite complète **seule** sur la machine (P-51), `-m pdf` en conteneur, `-m navigateur`.
- Un commit par story, puis un commit de documentation (suivi, `DECISIONS.md` si une décision est prise, `ECARTS-LIVRABLES-PHASE-6.md`). Fusion dans `master`, étiquette **`recette-phase-6-c10`**.
- Donne-moi : le nombre de tests, `git describe --tags`, les écarts aux critères d'acceptation s'il y en a, et **la liste des écrans modifiés**, pour que j'ajoute les contrôles correspondants à RECETTE-05.
