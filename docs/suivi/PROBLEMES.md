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

## P-22 — Une chaîne vide contournait la contrainte de cohérence catégorie de lieu / type de lieu partagé
**Date** 2026-09-03 · **Story** US-REF-03 · **État** : résolu
**Symptôme** — Trouvé à la relecture par le sous-agent `relecteur-conception`, avant commit : un rattachement de catégorie « Lieu partagé » sans type réel de lieu pouvait s'enregistrer silencieusement si le champ `type_lieu_partage` arrivait au service comme chaîne vide `''` plutôt que `None` — exactement ce que produit un `forms.ChoiceField(required=False)` resté sur une option vide.
**Cause** — `ServiceReferentiel._donnees_coherentes` (`app/referentiel/services/referentiel.py`) ne normalisait `type_lieu_partage` à `None` que dans un sens : quand la catégorie n'était **pas** « lieu partagé ». Rien ne traitait le cas inverse — catégorie « lieu partagé » avec un `type_lieu_partage` valant `''`. Deux verrous censés l'arrêter se sont révélés inopérants sur ce cas précis : `valider_instance` (`full_clean`) ne signale rien, `type_lieu_partage` étant `blank=True` — Django saute la validation des `choices` dès que la valeur est dans `empty_values`, ce qui inclut `''` ; et la contrainte en base `ck_element_referentiel_type_lieu_coherent` teste `type_lieu_partage__isnull`, or `''` n'est **pas** `NULL` — la contrainte est donc satisfaite à tort.
**Résolution** — `_donnees_coherentes` normalise désormais `''` en `None` **avant** de tester la catégorie (`donnees["type_lieu_partage"] = donnees.get("type_lieu_partage") or None`), puis lève `ErreurValidation` explicitement si la catégorie est « lieu partagé » et que `type_lieu_partage` reste `None` après normalisation — un message clair, au lieu de compter sur la contrainte en base (qui, elle, aurait fini par refuser un rattachement `categorie_lieu=lieu_partage, type_lieu_partage=None`, mais avec un `IntegrityError` mal traduit par le service, qui l'aurait pris pour un doublon RG-06). Quatre tests ajoutés, dont un qui prouve que la contrainte en base seule ne suffit pas (`test_categorie_lieu_partage_avec_type_chaine_vide_n_est_pas_arretee_par_la_contrainte`).
**Risque concerné** — aucun du registre ; défaut fonctionnel réel mais rattrapé avant tout commit, donc jamais exposé.
**Leçon** — Une contrainte de cohérence en base qui teste `IS NULL` ne suffit pas si le champ est aussi `blank=True` : un formulaire HTML peut soumettre `''`, jamais `NULL` directement. Toute normalisation de ce genre doit couvrir explicitement la chaîne vide, pas seulement `None` — et le test qui le prouve doit écrire `''`, pas `None`, pour être probant.

## P-21 — Un compte créé via l'écran de gestion n'avait en réalité aucune permission
**Date** 2026-09-03 · **Story** US-REF-02 (découvert avant l'étape 0, en testant l'accès de la cellule pédagogique posé à US-REF-01) · **État** : résolu
**Symptôme** — Un compte créé avec le profil « Cellule pédagogique » via l'écran *Créer un compte* ne voit pas l'onglet *Référentiel* dans le bandeau de navigation, alors que la matrice d'habilitations (écran *Habilitations*) donne bien `referentiel_lecture`/`referentiel_ecriture` à ce groupe.
**Cause** — `ServiceCompte.creer`/`modifier` (`app/administration/services/comptes.py`) enregistrent le champ `profil` sur le compte, mais ne l'ont jamais rattaché au groupe Django correspondant (`compte.groups`). Or RG-02 bis fait reposer tous les contrôles d'accès sur les groupes (`Utilisateur.has_perm`, donc `noyau.habilitations.a_permission`), jamais sur `profil` — un simple champ d'affichage/journalisation sans effet sur les droits réels. L'écran *Habilitations* configure la matrice groupe × domaine, pas l'appartenance d'un compte à un groupe : rien dans le code applicatif ne faisait ce lien. Le défaut était invisible en test parce que toutes les fixtures de test (`redacteur`, `administrateur`, etc.) rattachent le compte à son groupe **manuellement**, contournant le service — masquant que le service lui-même ne le fait jamais.
**Résolution** — `administration/constantes.py` : ajout de `PROFIL_VERS_GROUPE`, qui associe chaque valeur de `Profil` au nom du groupe correspondant dans `GROUPES`. `ServiceCompte._synchroniser_groupe(compte)` (nouvelle méthode privée) appelle `compte.groups.set([...])` — un compte n'appartient jamais qu'à un seul groupe métier, celui de son profil courant. Appelée dans `creer()` et `modifier()`, à l'intérieur de la même transaction que l'écriture. Deux tests ajoutés (`test_creation_rattache_le_compte_au_groupe_du_profil`, `test_changement_de_profil_deplace_le_compte_vers_le_nouveau_groupe`).
**Risque concerné** — aucun du registre ; risque fonctionnel majeur non catalogué (tout compte créé depuis le déploiement d'US-ADM-02 jusqu'à ce correctif est concerné, y compris en environnement réel si le socle a déjà servi hors développement).
**Leçon** — Une fixture de test qui fait « à la main » ce que le service devrait faire lui-même masque un défaut au lieu de le révéler : `redacteur`/`administrateur` faisaient exactement ce que `ServiceCompte.creer` aurait dû faire. Un test qui exerce le service réel (pas seulement `create_user()` + rattachement manuel) aurait détecté l'absence dès US-ADM-02. À vérifier pour tout futur mécanisme où un champ métier (`profil`) est censé avoir un effet technique (permissions) : un test doit prouver l'effet, pas seulement la valeur du champ.

## P-20 — Plus aucune connexion à la base après une mise en veille : deux causes empilées
**Date** 2026-09-03 · **Story** US-REF-01 · **État** : résolu
**Symptôme** — `python manage.py runserver` échouait avec « FATAL: password authentication failed for user "pfe_cit_app" », alors que la même configuration fonctionnait quelques heures plus tôt. Après une première correction, une deuxième tentative échouait différemment, en timeout de connexion pur — et l'extension PostgreSQL de VS Code échouait elle aussi, écartant une cause propre à Django.
**Cause** — Deux causes indépendantes, découvertes l'une après l'autre. (1) Le rôle `pfe_cit_app` (et `pfe_cit_migration`) portait en base un mot de passe différent de celui documenté dans `.env.exemple`/`infra/postgres/init/01_roles.sql` — le script d'initialisation est idempotent (`CREATE ROLE ... IF NOT EXISTS`) et ne s'exécute qu'une fois par volume Docker : un mot de passe changé un jour dans le script ne se répercute jamais sur un volume déjà initialisé. (2) Le conteneur avait redémarré de lui-même (`database system was interrupted` dans les journaux, ~25 min avant le diagnostic — vraisemblablement une mise en veille de Windows/WSL2), et Docker Desktop avait perdu la redirection host→conteneur du port 5432 : `docker inspect` montrait `HostConfig.PortBindings` correctement configuré mais `NetworkSettings.Ports` vide — la configuration existait sans être réellement appliquée. Un simple `docker compose restart` ne rétablissait pas la redirection.
**Résolution** — (1) `ALTER ROLE pfe_cit_app PASSWORD '...'` et `ALTER ROLE pfe_cit_migration PASSWORD '...'` exécutés directement en base via `docker exec`, sans perte de données. (2) `docker compose down` (sans `-v`, le volume nommé `donnees_pfe_cit` est conservé) puis `docker compose up -d` : recrée le conteneur et rétablit la redirection de port dès la création — un `restart` seul ne suffit pas dans ce cas précis.
**Risque concerné** — aucun risque du registre ; risque local de poste de développement, pas de la cible de déploiement (le poste CIT n'exécute pas Docker, voir `docker-compose.yml`, en-tête).
**Leçon** — Après une longue interruption de session (nuit, mise en veille, redémarrage Docker Desktop), vérifier `docker inspect <conteneur> --format '{{json .NetworkSettings.Ports}}'` avant de soupçonner l'application : un port « configuré » dans `docker ps`/`HostConfig` n'est pas nécessairement « appliqué ». Et un échec d'authentification qui suit un problème réseau résolu peut cacher une deuxième cause distincte (ici, un mot de passe de rôle jamais resynchronisé avec le script d'init) — ne pas s'arrêter à la première explication qui fait disparaître le symptôme immédiat.

## P-19 — `ModelForm.is_valid()` validait déjà la contrainte d'unicité, avant le service
**Date** 2026-09-03 · **Story** US-REF-00 · **État** : résolu
**Symptôme** — Créer un type « officiers » alors que « Officiers » existait déjà affichait un message Django générique et technique — « La contrainte « uq_type_formation_intitule » n'est pas respectée. » — au lieu du message construit par `ServiceGestion._erreur_unicite` (§ 5 : « désignation de l'élément existant »).
**Cause** — `ModelForm._post_clean()` (Django) appelle `self.instance.full_clean(exclude=exclude, validate_unique=False)` **sans** préciser `validate_constraints` — qui vaut `True` par défaut depuis Django 4.1. `formulaire.is_valid()` valide donc déjà `Meta.constraints` (dont `uq_type_formation_intitule`) avant même que la vue n'appelle `ServiceTypeFormation.creer()` : le service, censé être seul juge d'E2 par contrainte en base (§ 5, « pas d'un contrôle préalable »), ne voit jamais passer la violation.
**Résolution** — `noyau/forms.py::FormulaireGestion(forms.ModelForm)`, base commune du patron : `_post_clean` réécrit à l'identique de la version Django (y compris l'appel à `construct_instance`, sans quoi `full_clean` validerait une instance encore vierge — piège trouvé en cours de correction, une première version incomplète cassait toutes les créations), à un seul paramètre près : `validate_constraints=False`. `FormulaireTypeFormation` en hérite désormais au lieu de `forms.ModelForm` directement.
**Risque concerné** — aucun.
**Leçon** — `ModelForm._post_clean()` n'est pas un détail interne neutre : elle porte sa propre politique de validation, distincte de celle qu'on écrit soi-même côté service. Un patron générique qui promet « le message remonte de la contrainte, pas d'un contrôle préalable » doit vérifier ce que le framework valide déjà avant d'atteindre le service — pas seulement ce que le service valide lui-même.

## P-18 — `cree_par`/`modifie_par` refusaient toute création via `full_clean`
**Date** 2026-09-03 · **Story** US-REF-00 · **État** : résolu
**Symptôme** — `ServiceTypeFormation.creer(agissant, {"intitule": "Officiers"})` refusait systématiquement, avec le message « Ce champ ne peut pas être vide. Ce champ ne peut pas être vide. » — alors que `intitule` était bien renseigné. Reproduit directement au shell, hors navigateur, pour écarter tout artefact de saisie.
**Cause** — `ServiceGestion._valider` (patron générique, nouveau dans cette story) appelle `instance.full_clean(validate_unique=False, validate_constraints=False)` pour E1, **avant** que `ServiceBase.creer` ne pose `cree_par`/`modifie_par`. `ModeleHorodate` déclarait ces deux champs `null=True` mais pas `blank=True` : deux préoccupations distinctes en Django, la première pour la base (une valeur NULL est acceptée en écriture SQL), la seconde pour la validation de formulaire (`full_clean`/`ModelForm`, qui traite un champ comme obligatoire dès qu'il n'est pas explicitement `blank=True`, quel que soit `null`). Aucun service précédent n'appelait `full_clean()` sur une instance : le défaut restait invisible depuis quatre stories.
**Résolution** — `blank=True` ajouté aux deux champs dans `ModeleHorodate` (`app/noyau/models.py`) : ils ne sont jamais saisis par un formulaire, toujours posés après coup par la couche services, `blank=True` est donc la description exacte de leur usage, pas un contournement. Sans effet sur la base (aucune différence de SQL), mais Django exige tout de même une migration pour l'état de chaque modèle concerné — générées et appliquées : `administration/migrations/0010_entree_journal_auteur_blank.py`, `referentiel/migrations/0002_type_formation_auteur_blank.py`.
**Risque concerné** — aucun.
**Leçon** — `null=True` ne suffit pas à rendre un champ réellement facultatif dès qu'un service appelle `full_clean()` : vérifier `blank=True` en même temps que `null=True` sur tout champ jamais saisi par un formulaire, avant d'introduire la première validation générique qui en dépend.

## P-17 — `{% querystring %}` déjà préfixé de `?` : les liens de retrait de filtre, tri et pagination ne fonctionnaient pas
**Date** 2026-09-03 · **Story** US-ADM-04 · **État** : résolu
**Symptôme** — Sur l'écran du journal, cliquer sur la croix d'un jeton de filtre actif ne retirait pas le filtre : après un aller-retour navigateur, les deux filtres restaient actifs et le tableau ne changeait pas de contenu. Le même patron (`href="?{% querystring ... %}"`) était déjà utilisé pour le tri et la pagination de `liste_comptes.html`, posé en US-ADM-02 — jamais repéré à l'époque.
**Cause** — Le tag natif Django `{% querystring %}` (5.1+) retourne déjà la chaîne préfixée d'un `?` (`return f"?{query_string}"`, source `django/template/defaulttags.py`) quand il y a des paramètres. Le gabarit ajoutait un second `?` littéral devant (`href="?{% querystring %}"`), produisant une URL du type `?objet_type=x??objet_identifiant=y`… en réalité `??objet_type=x`. Le second `?` n'est pas neutre : Django construit `request.GET` à partir de tout ce qui suit le **premier** `?` de l'URL, donc le premier caractère de la vraie chaîne de requête (`?objet_type=x`) devenait partie de la clé (`"?objet_type"` au lieu de `"objet_type"`) — `request.GET.get("objet_type")` retournait alors toujours `None`, silencieusement, sans erreur.
**Résolution** — `?{% querystring` → `{% querystring` dans les neuf occurrences de `journal.html` et les quatre de `liste_comptes.html` (`sed` ciblé, vérifié par grep qu'aucune occurrence du motif fautif ne subsiste dans `app/`). Revérifié réellement : lecture du DOM rendu (`href="?objet_type=utilisateur"`, un seul `?`), rendu serveur via `Client` Django, et navigation directe confirmant que le retrait de filtre, le tri et la pagination restreignent bien le résultat.
**Risque concerné** — aucun (pas de perte de données ; UX cassée silencieusement, sans erreur serveur).
**Leçon** — vérifier la valeur **réellement rendue** d'un attribut `href` construit par un tag natif avant de l'envelopper d'un caractère littéral, plutôt que de supposer sa forme depuis un exemple partiel. La bibliothèque de composants ne montre nulle part `{% querystring %}` : ce n'est pas un écart à la charte, c'est un patron introduit en développement et jamais vérifié bout en bout jusqu'à cette story.

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
