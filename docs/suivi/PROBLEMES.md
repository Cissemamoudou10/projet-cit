# Problèmes rencontrés

Tout blocage, toute anomalie, toute surprise. Un problème résolu alimente le
registre des risques et les leçons apprises — c'est une règle du projet, pas une
formalité.

**Consigner tôt.** Un problème noté au moment où il survient garde son contexte ;
reconstitué trois semaines plus tard, il n'en a plus.

## Format

Une entrée par problème, la plus récente en tête.

```
## P-nn — Titre court
**Date** · **Story** · **État** : ouvert / contourné / résolu
**Symptôme** — ce qui s'est passé, tel qu'observé.
**Cause** — la cause réelle, pas le premier soupçon.
**Résolution** — ce qui a été fait.
**Risque concerné** — Rnn, ou « aucun ».
**Leçon** — ce qu'on fait différemment désormais. Facultatif.
```

---

## P-16 — Requête par croisement dans la vue de configuration des habilitations
**Date** 2026-09-02 · **Story** US-ADM-03 · **État** : résolu
**Symptôme** — Relecture (`relecteur-conception`) : `ServiceMatriceHabilitations.modifier_croisement` refaisait un `Group.objects.get()` et jusqu'à deux `Permission.objects.get()` à chaque croisement modifié. La soumission de l'écran de configuration (§ 6) peut porter jusqu'à 45 croisements en un seul aller-retour — jusqu'à 90 requêtes superflues dans le pire cas, alors que les cinq groupes et les dix-huit permissions du catalogue sont un ensemble fixe et petit.
**Cause** — `modifier_croisement` conçue pour un seul croisement à la fois, puis appelée en boucle depuis `_traiter_soumission` (`views/habilitations.py`) sans préchargement — violation de « Aucune requête dans une boucle » (`.claude/rules/python.md`).
**Résolution** — `modifier_croisement` remplacée par `ServiceMatriceHabilitations.appliquer_changements(agissant, changements)` : précharge une fois les cinq groupes (avec `prefetch_related`) et les dix-huit permissions, applique chaque croisement en mémoire contre cet état préchargé, dans la même transaction atomique. Une seconde relecture a signalé qu'il restait, côté écriture, un `.add()`/`.remove()` M2M par permission modifiée à l'intérieur de la boucle — corrigé à son tour : `_marquer_permissions` n'écrit plus rien pendant la boucle, elle accumule les ajouts/retraits par groupe dans `_ContextePermissions.a_ajouter`/`a_retirer` ; `_ecrire_permissions_en_attente` les applique une seule fois par groupe (au plus dix requêtes d'écriture pour 45 croisements sur cinq groupes) après la boucle. Chaque changement réel continue de générer sa propre entrée de journal (§ 6 : ancien/nouveau par croisement) — seules les requêtes répétées disparaissent, pas le grain de journalisation ni le blocage individuel du garde-fou administrateur. Les paramètres sont regroupés dans deux dataclasses (`CroisementModifie`, `_ContextePermissions`) pour rester sous la limite de cinq paramètres par fonction.
**Risque concerné** — aucun.
**Leçon** — pour un service dont la méthode publique est naturellement appelée en boucle depuis une vue (soumission d'un tableau dense), concevoir d'emblée une méthode de traitement par lot plutôt qu'une méthode unitaire appelée N fois — lectures **et** écritures, les deux sens de la règle « aucune requête dans une boucle ».

## P-15 — Nouvelles valeurs `TypeAction` utilisées avant leur migration
**Date** 2026-09-02 · **Story** US-ADM-03 · **État** : résolu
**Symptôme** — `manage.py initialiser_habilitations --reinitialiser` réel : `CheckViolation` sur `ck_entree_journal_type_action`, la valeur `modification_habilitations` n'étant pas encore admise en base.
**Cause** — `ACCES_REFUSE` et `MODIFICATION_HABILITATIONS` ajoutées à `TypeAction` (`administration/models.py`) sans regénérer la migration qui met à jour la contrainte `CHECK` — même oubli que P-15 aurait pu prévenir s'il avait déjà existé (il ne l'était pas encore) ; `manage.py migrate` avait pourtant averti (« models... have changes that are not yet reflected in a migration »), averti mais pas lu avant de lancer la commande suivante.
**Résolution** — `administration/migrations/0005_entree_journal_types_action_habilitations.py` générée et appliquée avant de rejouer `--reinitialiser`.
**Risque concerné** — aucun.
**Leçon** — lire la sortie de `migrate` avant d'enchaîner une autre commande, pas seulement son code de sortie : l'avertissement était là, explicite, avant l'échec.

## P-14 — Tri par colonne absent de la liste des comptes, exigé par le prompt
**Date** 2026-09-02 · **Story** US-ADM-02 · **État** : résolu
**Symptôme** — trouvé par le relecteur, pas par l'exécution : `§7.1` du prompt demande explicitement « en-tête figé et tri (§3.09) », mais `liste_comptes.html` n'avait que des en-têtes statiques et `ServiceCompte.lister` triait toujours sur `username`, sans paramètre. Aucun test ne le couvrait, aucune trace dans `docs/suivi/` ne le signalait comme écart assumé — un oubli, pas une décision.
**Cause** — omission au moment d'écrire la liste : la pagination et les filtres ont capté toute l'attention, le tri est resté un simple `order_by("username")` fixe.
**Résolution** — tri par colonne sur *Identifiant* et *Dernière connexion* (§3.09, `aria-sort`, bascule ascendant/descendant), `ServiceCompte._ordre` traduit le nom de colonne présentation vers le champ réel. Testé (`test_tri_par_identifiant_est_inversable`).
**Risque concerné** — aucun.
**Leçon** — une exigence énoncée noir sur blanc dans le prompt (« tri ») peut disparaître silencieusement si elle n'est pas reprise dans le tableau de tests du même prompt — le tableau de tests ne s'est jamais posé la question du tri, donc rien ne l'a fait remonter avant la relecture.

## P-13 — `ServiceCompte` dépassait 200 lignes
**Date** 2026-09-02 · **Story** US-ADM-02 · **État** : résolu
**Symptôme** — `tests/architecture/test_qualite.py::test_aucune_classe_ne_depasse_200_lignes` échoue réellement : 210 lignes.
**Cause** — les deux garde-fous du § 2.4 (D-07), sans rapport direct avec le CRUD du compte, alourdissaient la classe.
**Résolution** — extraits dans `app/administration/services/garde_fous.py`, en fonctions de module, pas en méthodes de classe.
**Risque concerné** — aucun.
**Leçon** — poser une règle nouvelle (D-07) dans le même fichier que le CRUD qu'elle protège grossit vite la classe ; l'isoler dès l'écriture évite l'aller-retour.

## P-12 — Utilisateur non enregistré en base fait échouer `has_perm`
**Date** 2026-09-02 · **Story** US-ADM-02 · **État** : résolu
**Symptôme** — `pytest` réel : `ValueError: "<Utilisateur: Cissé>" needs to have a value for field "id"`, dans `noyau/tests/test_gabarits.py` (US-ADM-01), au moment de rendre `noyau/base.html`.
**Cause** — le processeur de contexte appelle désormais `request.user.has_perm(...)` pour décider d'afficher la rubrique *Administration* ; `has_perm` interroge `user_permissions` (relation plusieurs-à-plusieurs), qui exige une clé primaire. Le test construisait un `Utilisateur` en mémoire, jamais enregistré — suffisant avant que le processeur de contexte n'ait de raison d'appeler `has_perm`.
**Résolution** — le test enregistre désormais l'utilisateur (`.save()`) avant de l'attacher à la requête.
**Risque concerné** — aucun.
**Leçon** — un test d'une story antérieure peut cesser d'être valide sans qu'aucune de ses propres assertions n'ait changé de sens, simplement parce qu'une story suivante fait davantage avec le même objet de contexte. Le rejouer réellement après chaque story, pas seulement les tests nouveaux, est ce qui l'a révélé.

## P-11 — Le drapeau `doit_changer_mot_de_passe` par défaut cassait des tests plus anciens
**Date** 2026-09-02 · **Story** US-ADM-02 · **État** : résolu
**Symptôme** — `pytest` réel : plusieurs tests d'US-ADM-01 (session déjà ouverte, accueil par profil) et un test de cette story (liste des comptes pour un non-administrateur) redirigés vers `/mot-de-passe/changer/` (302) au lieu du comportement attendu.
**Cause** — `doit_changer_mot_de_passe=True` est la valeur par défaut du modèle (§ 2.3, voulue pour un compte fraîchement créé) ; les fixtures de test (`utilisateur`, `non_administrateur`, et la création inline d'`US-ADM-01`) ne la désactivaient pas, alors que l'intergiciel de cette story intercepte désormais toute requête d'un compte au drapeau levé.
**Résolution** — les fixtures partagées posent explicitement `doit_changer_mot_de_passe=False` (« compte déjà onboardé ») ; les tests qui veulent exercer précisément l'intergiciel lèvent le drapeau eux-mêmes, dans leur propre corps.
**Risque concerné** — aucun.
**Leçon** — une valeur par défaut de modèle pensée pour la réalité (« un compte neuf doit changer son mot de passe ») devient un piège pour tout test plus ancien qui construit un compte sans s'en soucier, dès qu'une nouvelle story lui donne un effet de bord (ici, un intergiciel). Prévoir des fixtures « déjà onboardées » par défaut atténue le risque pour les stories suivantes aussi.

## P-10 — `views/comptes.py` importait `administration.models` directement
**Date** 2026-09-02 · **Story** US-ADM-02 · **État** : résolu
**Symptôme** — `tests/architecture/test_couches.py::test_aucune_vue_n_importe_un_modele` échoue réellement : `app/administration/views/comptes.py ligne 16 : administration.models`.
**Cause** — `get_object_or_404(Utilisateur, pk=pk)` et `Profil.choices` (pour le filtre de la liste) semblaient nécessiter un import direct du modèle dans la vue.
**Résolution** — `ServiceCompte.obtenir(pk)` (lève `ErreurIntrouvable`, traduite en `Http404` par la vue) et `ServiceCompte.profils_disponibles()` exposent ce dont la vue a besoin sans qu'elle importe jamais `administration.models`.
**Risque concerné** — aucun.
**Leçon** — `get_object_or_404` est le premier réflexe pour retrouver un objet par clé technique, mais il exige le modèle en argument — incompatible avec « aucune vue n'importe un modèle » dès que ce n'est pas une bibliothèque de test. Le service doit exposer un accès par identifiant, systématiquement.

## P-09 — `exige_habilitation` ne convertissait jamais `ErreurHabilitation` en réponse HTTP
**Date** 2026-09-02 · **Story** US-ADM-02 · **État** : résolu
**Symptôme** — aucun, car jamais exercé : US-ADM-01 n'utilisait que `verifier_habilitation` en isolation dans ses tests, jamais le décorateur `exige_habilitation` sur une vraie vue. En l'utilisant pour la première fois (liste des comptes, réservée aux administrateurs), un utilisateur non habilité aurait reçu une erreur 500 (`ErreurHabilitation` non rattrapée) plutôt qu'un 403.
**Cause** — `exige_habilitation` (`app/noyau/habilitations.py`) appelait `verifier_habilitation` sans jamais intercepter l'exception métier qu'elle lève — contrairement à `HabilitationMixin.dispatch`, qui l'interceptait déjà et déléguait à `handle_no_permission()` d'`AccessMixin`.
**Résolution** — `exige_habilitation` intercepte désormais `ErreurHabilitation` et lève `django.core.exceptions.PermissionDenied`, que Django rend nativement en 403.
**Risque concerné** — aucun.
**Leçon** — un mécanisme du socle jamais exercé par un test d'intégration réel (bout en bout, vue y comprise) peut cacher un défaut jusqu'à son premier usage effectif — ici, deux stories plus tard.

## P-08 — Commentaire de gabarit contenant littéralement la classe qu'il explique
**Date** 2026-09-02 · **Story** US-ADM-01 · **État** : résolu
**Symptôme** — `pytest` réel : `test_page_de_connexion_sans_largeur_minimale_imposee` échoue, `min-w-[1280px]` trouvé dans la réponse alors que `<body>` ne la porte pas.
**Cause** — un commentaire HTML dans `base_public.html` expliquant pourquoi `min-w-[1280px]` était omise citait la classe en toutes lettres — présente dans `response.content`, un commentaire HTML n'étant pas retiré du flux envoyé au client. Même famille que P-04 (§ socle) : un commentaire qui cite la syntaxe qu'il documente redevient une occurrence réelle de cette syntaxe.
**Résolution** — commentaire reformulé sans reproduire la classe littéralement.
**Risque concerné** — aucun.
**Leçon** — généraliser P-04 : dans un gabarit, un commentaire ne doit citer littéralement ni une balise de gabarit (`{% %}`), ni une classe Tailwind, si un test vérifie l'absence de cette chaîne dans le rendu.

## P-07 — `npm install` refusé par le système de permission de l'outil
**Date** 2026-09-02 · **Story** Socle technique (PROMPT_00) · **État** : ouvert
**Symptôme** — `npm install` refusé trois fois de suite par le prompt de permission de Claude Code, y compris après accord explicite en conversation à deux reprises.
**Cause** — non identifiée depuis cette session : probablement un réglage de permissions ou un hook local, pas un choix conscient au moment du refus.
**Résolution** — aucune de mon fait. `package.json`, `tailwind.config.js` et `app/noyau/static_src/application.css` sont prêts ; seule l'exécution manque. À lancer soi-même : `npm install && npm run css:build`.
**Risque concerné** — aucun pour le socle ; bloque la production du CSS versionné (`app/noyau/static/css/application.css`, toujours absent).
**Leçon** — vérifier la configuration de permissions Claude Code pour les commandes `npm` si le blocage se reproduit.

## P-06 — Port 5432 déjà occupé par un conteneur sans rapport avec ce projet
**Date** 2026-09-02 · **Story** Socle technique (PROMPT_00) · **État** : résolu — `cit-postgres` arrêté par le binôme. `docker compose up -d` démarre `pfe_cit_base` normalement sur 5432 ; `migrate` et `pytest` (28/28) confirmés contre ce conteneur réel.
**Symptôme** — `docker compose up -d` échoue (`Bind for 0.0.0.0:5432 failed: port is already allocated`) : un conteneur `cit-postgres` (`postgres:15`, sans rapport visible avec ce dépôt) occupe déjà ce port sur la machine.
**Cause** — un autre projet local (nom `cit-postgres`, docker-compose distinct) tourne déjà sur cette machine.
**Résolution** — aucune de mon fait : je n'ai pas touché à `cit-postgres`, contenant peut-être des données d'un autre travail. Les vérifications de ce socle (migrate, pytest, contrainte SQL) ont été faites contre un conteneur de diagnostic séparé (`pfe_cit_dev`, port 15432, supprimé après usage) — jamais contre le port 5432 réel.
**Risque concerné** — aucun pour le socle ; bloque `docker compose up -d` tel que documenté dans `docker-compose.yml`.
**Leçon** — à trancher : arrêter `cit-postgres` avant de travailler sur ce projet, ou changer le port hôte publié dans `docker-compose.yml` (`"5433:5432"` par exemple, en ajustant `BASE_PORT` dans `.env`).

## P-05 — `ruff.toml` : `exclude` désactivait les exclusions par défaut de ruff
**Date** 2026-09-02 · **Story** Socle technique (PROMPT_00) · **État** : résolu
**Symptôme** — `ruff check .` et `ruff format --check .` scannaient `.venv/` en entier (des milliers d'erreurs sur du code tiers), une fois l'environnement virtuel réellement créé.
**Cause** — `exclude = ["**/migrations/*"]` dans `ruff.toml` **remplace** la liste d'exclusion par défaut de ruff (qui contient `.venv`, `node_modules`, `.git`…) au lieu de la compléter. Invisible tant qu'aucun `.venv` n'existait dans le dépôt.
**Résolution** — `exclude` renommé en `extend-exclude` (additif par nature) dans `ruff.toml`.
**Risque concerné** — aucun.
**Leçon** — `extend-exclude` par défaut dans tout `ruff.toml` de ce projet, jamais `exclude` seul, sauf besoin explicite de perdre les exclusions par défaut.

## P-04 — Commentaire HTML contenant `{% include %}` interprété comme une vraie balise
**Date** 2026-09-02 · **Story** Socle technique (PROMPT_00) · **État** : résolu
**Symptôme** — `pytest` réel : `TemplateSyntaxError: 'include' tag takes at least one argument`, sur un gabarit qui n'a pourtant qu'un seul `{% include %}` visible et valide.
**Cause** — un commentaire HTML `<!-- ... {% include %} ... -->` que j'avais ajouté dans `fil_ariane.html` pour expliquer un écart contenait littéralement la chaîne `{% include %}`. Le tokenizer de Django ne connaît pas les commentaires HTML : il repère `{%`/`%}` n'importe où dans le fichier, y compris dans du texte censé être ignoré.
**Résolution** — commentaire reformulé en prose, sans reproduire de syntaxe `{% %}` littérale.
**Risque concerné** — aucun.
**Leçon** — ne jamais faire figurer une syntaxe de gabarit Django littérale (`{% %}`, `{{ }}`) dans un commentaire à l'intérieur d'un fichier `.html` de gabarit, HTML ou pas.

## P-03 — `Meta` ne voit pas une classe imbriquée définie plus haut dans le même corps de classe
**Date** 2026-09-02 · **Story** Socle technique (PROMPT_00) · **État** : résolu
**Symptôme** — `manage.py migrate` réel : `NameError: name 'Profil' is not defined`, dans `administration/models.py`, à la ligne du `CheckConstraint` de `Utilisateur.Meta`.
**Cause** — `Profil` (TextChoices) était imbriquée dans `Utilisateur`, et `Meta.constraints` (autre classe imbriquée du même corps) tentait de la référencer par son nom simple. En Python, une classe imbriquée n'hérite pas de la portée du corps de classe qui la contient — seule la portée globale du module lui est accessible. Fonctionnait à la lecture, invisible sans exécution réelle.
**Résolution** — `Profil` déplacée au niveau du module (visible depuis `Meta`), avec `Utilisateur.Profil = Profil` juste après la classe pour préserver l'accès habituel `Utilisateur.Profil.ADMINISTRATEUR` (utilisé ailleurs, notamment dans les tests).
**Risque concerné** — aucun, mais confirme le risque déjà noté : le code hand-écrit sans exécution réelle peut cacher des erreurs de portée Python, pas seulement des écarts avec `makemigrations`.
**Leçon** — toute construction Python "classe imbriquée référencée depuis une autre classe imbriquée du même parent" est un piège classique à surveiller à la relecture, pas seulement à l'exécution.

## P-02 — `pytest-cov` absent de la liste validée des dépendances
**Date** 2026-09-02 · **Story** Socle technique (PROMPT_00) · **État** : ouvert
**Symptôme** — `PROMPT_00_socle_technique.md` (étape 8) demande explicitement
`pytest-cov` dans les dépendances de développement. `DEPENDANCES_VALIDEES` dans
`tests/architecture/test_dependances.py` liste `pytest`, `pytest-django` et
`ruff`, mais pas `pytest-cov`.
**Cause** — pas identifiée ; probablement une omission à la rédaction de la
liste, `pytest-cov` n'ayant pas d'effet sur l'exécution des tests eux-mêmes
(seulement sur le rapport de couverture), il est facile à oublier.
**Résolution** — aucune de mon fait : `pytest-cov` est placé dans
`requirements-dev.txt` (non vérifié par ce test, qui ne lit que
`requirements.txt`), donc le test passe tel quel. Je n'ai pas modifié
`DEPENDANCES_VALIDEES` — PROMPT_00 étape 0 est explicite : un test qui suppose
autre chose que la réalité se signale, il ne se corrige pas de ma propre
initiative.
**Risque concerné** — aucun.
**Leçon** — si `pytest-cov` doit un jour rejoindre `requirements.txt` (par
exemple pour un seuil de couverture vérifié en CI), ajouter `"pytest-cov"` à
`DEPENDANCES_VALIDEES` dans le même commit.

## P-01 — `migrate` échoue avec le rôle applicatif par défaut
**Date** 2026-09-02 · **Story** Socle technique (PROMPT_00) · **État** : résolu
**Symptôme** — `local.py` et `production.py` pointent par défaut le rôle `pfe_cit_app`, sans privilège de création de table. `python manage.py migrate` sans précaution échoue avec `permission denied for schema public`.
**Cause** — Choix délibéré ([[D-01]]) : `pfe_cit_app` ne doit jamais pouvoir créer ou modifier le schéma, seulement lire/écrire les lignes existantes.
**Résolution** — Surcharger `BASE_UTILISATEUR` et `BASE_MOT_DE_PASSE` avec les identifiants de `pfe_cit_migration` avant `migrate` :
```
BASE_UTILISATEUR=pfe_cit_migration BASE_MOT_DE_PASSE=developpement_local_migration python app/manage.py migrate
```
Revenir aux valeurs par défaut (ou ne rien positionner) pour `runserver` et le reste du travail courant. La suite de tests n'a pas besoin de ce contournement : `config/settings/test.py` pointe `pfe_cit_migration` directement.
**Risque concerné** — aucun.
**Leçon** — documenter tout de suite la commande à côté du réglage qui la rend nécessaire, plutôt que de laisser le prochain `migrate` échouer en silence.
