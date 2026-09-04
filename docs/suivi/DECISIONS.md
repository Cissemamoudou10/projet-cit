# Décisions de développement

Toute décision qui **s'écarte de la conception arrêtée en phase 4**, ou qui la
complète sur un point qu'elle ne traitait pas.

**Pourquoi ce fichier existe.** Le mémoire décrit la conception ; le code décrira
la réalité. Sans trace des écarts, les deux divergent et la traçabilité —
`OSn → BF → US → CU → RG → SEQ → CLS` — se rompt. Un jury vérifie cette chaîne.

**Ce qui n'entre pas ici** : les choix d'implantation sans effet sur le modèle ni
sur une règle métier. Le nom d'une variable n'est pas une décision.

**Ce qui entre ici** : toute modification d'une règle métier, d'une cardinalité,
d'un attribut, d'un état, d'une responsabilité de service. Et toute règle
nouvelle découverte en développant.

## Format

Une entrée par décision, la plus récente en tête.

```
## D-nn — Titre court
**Date** · **Story** · **Auteur**
**Contexte** — la situation qui a imposé de trancher.
**Décision** — ce qui a été retenu, sans ambiguïté.
**Alternative écartée** — et pourquoi.
**Impact sur les livrables** — quelle règle, quelle classe, quel diagramme est à
reprendre. **Cette ligne n'est jamais vide.**
**Reporté au livrable** — oui / non, avec la date.
```

---

## D-52 — `Qualification` vit dans `ressources` ; `referentiel` compte par relation inverse, jamais par import
**Date** 2026-09-04 · **Story** US-INS-02 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — `tests/architecture/test_couches.py::DEPENDANCES_AUTORISEES` fixe un sens unique : `ressources` peut dépendre de `referentiel`, jamais l'inverse. `Qualification` porte des clés étrangères vers les deux (`Instructeur`, `ressources` ; `Matiere`, `referentiel`), donc elle ne peut vivre que dans `ressources` — confirmé par le prompt lui-même (`Meta.db_table = "ressources_qualification"`). Restait à résoudre deux écrans qui en dépendent depuis l'autre côté : l'entrée par matière (§ 7.3, A1, normalement accrochée à la fiche matière de `referentiel`) et le signalement du critère 4 sur `formation_referentiel.html` (§ 7.4, aussi dans `referentiel`).
**Décision** — Les deux vues symétriques (entrée instructeur, entrée matière) vivent toutes les deux dans `ressources/views/qualification.py`, sur des URLs `ressources:...` ; `matiere_detail.html` (`referentiel`) ne porte qu'un lien `{% url %}` vers cet écran — un gabarit n'est pas scanné par le test d'architecture, qui ne porte que sur les imports Python. Pour le signalement du critère 4, `Qualification.matiere` porte `related_name="qualifications"` : `ServiceReferentiel.lister` annote `Count("matiere__qualifications", distinct=True)`, une chaîne de caractères résolue par l'ORM Django au moment de la requête, jamais un `import ressources` — même motif que `Count("formations")`, déjà utilisé par `ServiceTypeFormation._queryset`.
**Alternative écartée** — Une vue de `referentiel` important `ServiceQualification` pour l'entrée par matière : aurait violé le sens de dépendance et fait échouer `test_ordre_des_dependances_entre_applications`, qui scanne aussi les fichiers de tests, pas seulement `services.py`/`views.py`. Un service de comptage dans `ressources` appelé depuis `referentiel` : même violation, dans l'autre sens.
**Impact sur les livrables** — aucun sur la conception ; note de méthode pour toute future association entre deux applications dans ce sens de dépendance (le paquetage organisation en aura probablement besoin).
**Reporté au livrable** — non, à faire au prochain relevé du mémoire.

## D-51 — Report d'E1 (US-INS-02) vers US-PLAN-03, mécanisme posé quand même
**Date** 2026-09-04 · **Story** US-INS-02 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — E1 (« l'instructeur est affecté à des séances futures de cette matière ») suppose `Seance`/l'affectation, qui appartiennent à US-PLAN-03, sprint 3 — même famille de report que D-23, D-30, D-35, D-39, D-45 pour les paquetages précédents.
**Décision** — `ServiceQualification.seances_futures(qualification)` rend `[]` aujourd'hui, sans changer de signature quand US-PLAN-03 la remplira. L'écran de confirmation de retrait affiche déjà l'énumération (vide) et le message d'E1, comme demandé au § 3.2 du Prompt 13 : rien à récrire à l'écran quand la source de données existera.
**Alternative écartée** — Ne rien écrire avant US-PLAN-03 : aurait reporté aussi le travail d'écran, alors que le Prompt 13 demande explicitement de le faire maintenant pour que seule la source de données manque plus tard.
**Impact sur les livrables** — note pour US-PLAN-03 : remplir `seances_futures` sans changer sa signature ni l'écran qui l'appelle.
**Reporté au livrable** — non applicable, dette de développement déjà identifiée par le Prompt 13 lui-même (§ 3.2).

## D-50 — Le report D-30 (US-REF-02) est refermé sur ses deux volets — le premier l'était déjà, sans l'avoir consigné
**Date** 2026-09-04 · **Story** US-INS-02 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — D-30 (US-REF-02) attendait deux sources pour rendre le critère 5 (« une matière utilisée ne peut être supprimée ») réellement testable : le référentiel (`ElementReferentiel`, US-REF-03) et la matrice de qualification (`Qualification`, cette story). En explorant à l'étape 0, `ElementReferentiel.matiere` s'est révélé déjà porté en `PROTECT` depuis US-REF-03, avec un test qui le prouve déjà (`test_suppression_d_une_matiere_rattachee_est_refusee`, `referentiel/tests/test_referentiel.py`) — mais personne ne l'avait signalé comme refermant D-30, à la différence de D-40 qui avait explicitement refermé la source équivalente côté prérequis.
**Décision** — `Qualification.matiere` en `PROTECT` referme le second et dernier volet, sans code nouveau dans `ServiceMatiere` (mécanisme générique du patron, `ProtectedError` + `decrire_opposants`). Testé dans `ressources/tests/test_qualification.py::test_suppression_d_une_matiere_qualifiee_est_refusee` — seule application autorisée à importer les deux côtés pour l'exercer. D-30 est donc entièrement refermé par cette entrée : les deux sources bloquent réellement la suppression d'une matière du catalogue.
**Alternative écartée** — Aucune ; cette entrée constate une fermeture déjà acquise plutôt que d'en décider une nouvelle pour le premier volet.
**Impact sur les livrables** — aucun sur la conception ; D-30 peut être considéré clos dans la matrice de traçabilité suivie en revue de sprint.
**Reporté au livrable** — non applicable, referme un report déjà consigné.

## D-49 — `Qualification` n'hérite pas du mixin d'archivage : second retrait réel du patron, après `ObjectifPedagogique`
**Date** 2026-09-04 · **Story** US-INS-02 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — Le Prompt 13, § 3.1, écarte explicitement l'archivage pour `Qualification` : une qualification retirée disparaît, rien ne la référence — les séances futures portent un instructeur et une matière, jamais la qualification elle-même. RG-22 protège l'intégrité en amont (refus du retrait s'il casserait une affectation), pas en aval par un historique.
**Décision** — `Qualification` n'hérite que de `ModeleHorodate`, pas de `ModeleArchivable`. `ServiceQualification.retirer` exécute un `DELETE` réel après vérification d'E1, journalisé avec `TypeAction.SUPPRESSION_ELEMENT_GESTION` (nature déjà posée par D-38 pour `ObjectifPedagogique`, réutilisée telle quelle). Testé par un test de non-présence (même patron que `test_n_a_pas_de_champ_d_archivage` pour `ObjectifPedagogique`, D-37).
**Alternative écartée** — Archiver comme les entités du patron `ServiceGestion` : contredirait le point de conception du § 2 (aucune anticipation) et le § 3.1, qui motive explicitement l'exception par l'absence de toute référence à conserver.
**Impact sur les livrables** — aucun sur la conception ; deuxième exception documentée à la convention d'archivage du patron, après D-37.
**Reporté au livrable** — non applicable.

## D-48 — Matricule de l'instructeur : obligatoire et unique pour un militaire du centre, facultatif sinon
**Date** 2026-09-04 · **Story** US-INS-01 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — § 2 du Prompt 12 : le critère 1 énumère identité, grade, spécialité, statut, mais oublie le matricule que le critère 3 exige pourtant en recherche — omission de rédaction, pas une ambiguïté. Restait à trancher si le matricule est obligatoire et unique, sachant qu'un militaire du centre en a nécessairement un, alors qu'un vacataire ou un civil n'est pas nécessairement enregistré dans le système d'information du centre.
**Décision** — `matricule` nullable ; `UniqueConstraint(matricule)` simple (PostgreSQL n'unicise jamais deux `NULL` entre eux, donc plusieurs instructeurs sans matricule coexistent) ; `CheckConstraint` (`ck_instructeur_matricule_militaire`) exigeant `matricule` non nul quand `statut = militaire_du_centre`. Les trois contraintes vérifiées en base, contournant l'ORM (`test_matricule_obligatoire_pour_un_militaire_du_centre_impose_en_base`, `test_deux_vacataires_sans_matricule_coexistent`, `test_matricule_duplique_est_refuse_en_base`).
**Alternative écartée** — Matricule obligatoire pour les trois statuts : aurait forcé une valeur inventée pour tout vacataire ou civil non enregistré ailleurs, un matricule fictif étant pire qu'une absence assumée.
**Impact sur les livrables** — le critère 1 du backlog v7 (US-INS-01) est à corriger pour y ajouter le matricule, comme le signale déjà le Prompt 12, § 2.
**Reporté au livrable** — oui, correction de rédaction du backlog v7, critère 1 d'US-INS-01.

## D-47 — `DOMAINE` d'`Instructeur` corrigé au catalogue ; `CHAMP_UNICITE` distinct du champ réellement unique
**Date** 2026-09-04 · **Story** US-INS-01 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — Deux écarts trouvés à l'étape 0, avant tout code. (1) Le Prompt 12, § 7, écrit `ServiceInstructeur.DOMAINE = "instructeurs"`, mais `tests/architecture/test_couches.py::DOMAINES_CATALOGUE` (source `docs/suivi/HABILITATIONS.md`, § 11.2) ne connaît que `"instructeurs_qualifications"` — un domaine unique pour US-INS-01 et US-INS-02. `"instructeurs"` seul aurait fait échouer `test_toute_classe_de_service_declare_un_domaine`. (2) `ServiceGestion` suppose un unique champ (`CHAMP_UNICITE`) qui sert à la fois de tri par défaut, d'identifiant de journal et de champ interrogé par `_erreur_unicite` — or la seule contrainte d'unicité réelle d'`Instructeur` porte sur `matricule`, nul pour deux statuts sur trois. Poser `CHAMP_UNICITE = "matricule"` aurait fait apparaître « None » comme identifiant de journal pour tout vacataire ou civil sans matricule — exactement le défaut déjà corrigé en P-24 (`docs/suivi/PROBLEMES.md`).
**Décision** — `DOMAINE = "instructeurs_qualifications"`, conforme au catalogue. `CHAMP_UNICITE = "nom"` (toujours renseigné, tri alphabétique raisonnable pour un annuaire) ; `ServiceInstructeur._erreur_unicite` surchargée pour désigner explicitement `matricule`, la seule contrainte d'unicité réelle.
**Alternative écartée** — Garder `DOMAINE = "instructeurs"` et corriger `DOMAINES_CATALOGUE` : écarté, la matrice § 11.2 traite déjà instructeurs et qualifications comme un seul domaine d'habilitation (US-INS-02 partage la même permission), et c'est le catalogue qui fait foi. `CHAMP_UNICITE = "matricule"` sans surcharge : écarté pour la raison P-24 ci-dessus.
**Impact sur les livrables** — aucun sur la conception ; le Prompt 12, § 7, est à corriger (`DOMAINE`).
**Reporté au livrable** — non, à faire au prochain relevé du mémoire.

## D-46 — `noyau/gestion/formulaire.html` généralisé aux formulaires à deux colonnes (§ 3.24)
**Date** 2026-09-04 · **Story** US-INS-01 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — § 8 du Prompt 12 demande un formulaire à deux colonnes (Identité / Rattachement), mais le gabarit générique du patron (`noyau/gestion/formulaire.html`, posé à US-REF-00) ne rend qu'un unique groupe de champs en une colonne — aucune des cinq stories précédentes du patron n'avait eu besoin de deux groupes.
**Décision** — Le gabarit accepte désormais un contexte optionnel `groupes` (liste de `{legende, champs}`) : s'il est fourni, deux `<fieldset>` sont rendus côte à côte, chacun filtrant `form.visible_fields` sur son sous-ensemble de noms de champs (`{% if champ.name in groupe.champs %}`, comparaison de chaînes, aucun filtre de gabarit personnalisé nécessaire) ; sinon, le rendu à une colonne existant est inchangé — les cinq formulaires du référentiel n'y touchent pas. Le balisage d'un champ (étiquette, obligatoire, erreurs, aide) est extrait dans `noyau/gestion/_champ_generique.html`, inclus dans les deux branches plutôt que dupliqué.
**Alternative écartée** — Un gabarit dédié `instructeur_formulaire.html` référençant `{{ form.nom }}`, `{{ form.matricule }}`, etc. explicitement : plus simple à écrire une fois, mais réintroduit un gabarit par entité pour une variation purement visuelle que le patron doit au contraire absorber — la prochaine entité à deux colonnes (une séance, par exemple, citée en exemple à la charte § 3.24) réutilisera `groupes` tel quel.
**Impact sur les livrables** — aucun sur la conception ; `docs/suivi/PATRON-GESTION.md` complété.
**Reporté au livrable** — non applicable.

## D-45 — Critère 4 d'US-INS-01 reporté à US-PLAN-03 ; deux remontées de matrice consignées sans arbitrage
**Date** 2026-09-04 · **Story** US-INS-01 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — Critère 4 (« un instructeur affecté à un programme en cours ne peut être supprimé ») suppose `LigneProgramme`/l'affectation, qui appartiennent à US-PLAN-03, sprint 3 — même famille de report que D-23, D-30, D-35 pour le référentiel. Par ailleurs, le Prompt 12, § 4, signale deux tensions sur la matrice § 11.2 sans demander de les résoudre ici : (1) la cellule examens n'a aucun accès au domaine `instructeurs_qualifications`, alors que CU-P6-04 (désignation des surveillants, sprint 4, RG-53) en aura besoin ; (2) `Instructeur.specialite` est un second champ texte libre, à côté de `Formation.specialite` (US-REF-01, question déjà ouverte, D-25 et voisines) — la question de savoir s'il s'agit de la même nomenclature devient plus pressante avec deux entités qui filtrent dessus.
**Décision** — Critère 4 : même traitement que D-23/D-30/D-35 — le mécanisme générique du patron (`ServiceGestion.supprimer`, `ProtectedError` intercepté) suffit déjà, testé pour ne rien trouver aujourd'hui (`test_methode_d_enumeration_des_bloquants_existe_et_ne_trouve_rien`). Les deux remontées du § 4 : consignées ici telles quelles, la matrice appliquée sans modification (`test_cellule_examens_n_a_aucun_acces_ni_lecture_ni_ecriture`, commenté pour signaler qu'il doit tomber si l'arbitrage change), la spécialité restant un texte libre filtré sur les valeurs distinctes réellement enregistrées (`ServiceInstructeur.valeurs_specialite_distinctes`).
**Alternative écartée** — Anticiper l'arbitrage de la cellule examens en lui donnant la lecture dès maintenant : écarté, la matrice fait foi tant qu'elle n'a pas été révisée formellement — l'anticiper ici créerait un écart entre le code et le document qui a servi à le construire.
**Impact sur les livrables** — note pour US-PLAN-03 (critère 4) ; note pour CU-P6-04/sprint 4 (accès examens) ; note pour une future story qui déciderait d'une nomenclature commune de spécialité entre `Formation` et `Instructeur`.
**Reporté au livrable** — non applicable, dette de développement déjà identifiée par le Prompt 12 lui-même (§ 3.3, § 4).

## D-44 — Écart backlog/matrice sur US-REF-07 : la Direction de Formation lit aussi le référentiel
**Date** 2026-09-04 · **Story** US-REF-07 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — Le critère 1 du backlog v7 ne nomme que les cellules planification et examens pour la consultation en lecture seule du référentiel. La fiche générique et la matrice de permissions § 11.2 (celle qui a servi à construire le catalogue des habilitations d'US-ADM-03) accordent la même lecture à la Direction de Formation. Le Prompt 11, § 1, signalait déjà l'écart et demandait de le consigner sans en faire une affaire.
**Décision** — La matrice fait foi : les trois profils (planification, examens, Direction de Formation) lisent le référentiel, aucun n'écrit. Le test de masquage (`test_masquage_ecriture.py`) et le test de refus (`test_refus_ecriture_direct.py`) couvrent les trois. Traité comme une omission de rédaction du backlog, pas comme une contradiction de fond à trancher.
**Alternative écartée** — Restreindre la consultation aux deux seules cellules citées par le critère 1 : aurait contredit la matrice déjà en vigueur depuis US-ADM-03 et retiré un accès qu'un profil a déjà, sans qu'aucune règle ne le justifie.
**Impact sur les livrables** — le critère 1 du backlog v7 est à corriger pour nommer les trois cellules, comme la matrice § 11.2 le fait déjà.
**Reporté au livrable** — oui, correction de rédaction du backlog v7, critère 1 d'US-REF-07.

## D-43 — Écran consolidé en sections plutôt qu'en onglets, masquage par `perms.` natif de Django
**Date** 2026-09-04 · **Story** US-REF-07 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — Le Prompt 11, § 3, laissait le choix entre onglets (§ 3.42 de la charte) et sections pour l'écran de consultation consolidé. Le composant § 3.42 tel qu'écrit dans la charte navigue par changement d'URL (chaque onglet est un lien vers une page distincte), ce qui aurait multiplié les routes et les vues pour un écran que le critère d'acceptation ne demande qu'en une seule pièce.
**Décision** — Quatre sections empilées sur une seule URL (`referentiel:consultation_formation`), assemblées depuis cinq fragments d'inclusion déjà utilisés par les écrans existants (`identification_formation.html`, `statistique_volume.html`, `cellules_matiere_volume_lecture.html`, `objectifs_lecture.html`, `tableau_prerequis.html`). Le masquage des commandes d'écriture, dans les quatre écrans existants, emploie directement `{% if perms.noyau.referentiel_ecriture %}` — le mécanisme natif de Django (`django.contrib.auth.context_processors.auth`, déjà enregistré), silencieux comme `noyau.habilitations.a_permission` et sans code nouveau. Premier usage de `perms.` dans un gabarit du projet.
**Alternative écartée** — Onglets à la lettre du § 3.42 (une route par section) : aurait ajouté quatre routes et quatre vues pour un gain nul sur les deux points de la story, et cassé la garantie du § 2.2 du prompt (aucun cache, aucune copie de travail) en tentant de partager un contexte entre plusieurs vues. Un gabarit tag personnalisé enrobant `a_permission` pour le masquage : écarté, `perms.` fait exactement la même chose sans code à maintenir.
**Impact sur les livrables** — aucun sur la conception ; § 3.42 de la charte gagnerait une note précisant qu'il suppose une page par onglet, pour qu'une future story sache quand il s'applique tel quel.
**Reporté au livrable** — non, à faire au prochain relevé du mémoire.

## D-42 — RG-09 (même référentiel) vit en couche services, jamais en base — écart assumé
**Date** 2026-09-04 · **Story** US-REF-06 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — `RG-09` : un prérequis ne peut lier que deux matières appartenant au référentiel de la **même** formation. `Prerequis` porte sur `ElementReferentiel`, jamais sur `Matiere` (CLS-01, § 3.4) — chaque extrémité désigne ainsi un couple (formation, matière) précis. Le document de conception affirme que cette association « porte RG-09 structurellement », mais ce n'est vrai qu'à moitié : elle garantit que chaque extrémité pointe vers un couple formation-matière déterminé, **pas** que les deux extrémités partagent la même formation — rien, dans le schéma, n'empêche de lier un `ElementReferentiel` de la formation A à un de la formation B. RG-09 resterait exprimable en base par une clé étrangère composée vers `(id, formation)` de `ElementReferentiel`, mais Django ne sait pas déclarer une clé étrangère composée : il faudrait une migration en SQL brut, avec un modèle dont l'ORM ignorerait la contrainte.
**Décision** — RG-09 vit en couche services : `_verifier_couple` (`referentiel/services/prerequis.py`) compare explicitement `element.formation_id` et `element_prerequis.formation_id` avant tout enregistrement, et lève `ErreurValidation` (E2) sinon. Testé (`test_matiere_d_un_autre_referentiel_est_refusee`, `test_la_liste_deroulante_n_offre_ni_la_matiere_elle_meme_ni_un_autre_referentiel`).
**Alternative écartée** — Dénormaliser `formation` sur `Prerequis` et poser une clé étrangère composée en SQL brut : le coût en lisibilité et en maintenance (un modèle Django qui ne reflète pas fidèlement les contraintes réelles de sa table) dépasse le gain d'une garantie supplémentaire en base, pour une propriété que la couche services vérifie de toute façon avant tout autre contrôle (auto-prérequis, cycle).
**Impact sur les livrables** — nuance à apporter à `docs/conception/13-diagramme-classes.md`, § 3.4 : l'association réflexive sur `ElementReferentiel` limite la portée d'une violation de RG-09 (elle ne peut jamais porter sur un simple couple de matières hors de tout contexte de formation), mais ne la rend pas structurellement impossible.
**Reporté au livrable** — oui, nuance à apporter au mémoire sur la portée exacte de l'association réflexive.

## D-41 — Ordre topologique : départage déterministe par l'intitulé de la matière
**Date** 2026-09-04 · **Story** US-REF-06 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — A2 demande *un* ordre topologique admissible ; l'algorithme de Kahn en choisit un selon l'ordre dans lequel il dépile les sommets sans prédécesseur restant, et plusieurs ordres sont généralement valides pour un même graphe. Sans règle de départage explicite, deux exécutions sur les mêmes données pourraient rendre des ordres différents (l'ordre naturel d'itération d'un `dict`/`set` Python n'est pas garanti indépendant de l'historique des insertions/suppressions) — instable pour les tests, et incompréhensible pour la cellule planification si la génération du sprint 3 produisait un programme différent à données identiques.
**Décision** — Parmi les éléments sans prérequis restant, celui dont `element.matiere.intitule` est le plus petit (ordre alphabétique) sort en premier (`_inserer_trie`, `referentiel/services/prerequis.py`). L'unicité du catalogue (`uq_matiere_intitule`) garantit qu'aucune égalité ne peut se produire entre deux éléments d'un même référentiel. Testé (`test_le_meme_graphe_rend_deux_fois_le_meme_ordre`, `test_graphe_sans_aucun_lien_rend_l_ordre_par_la_regle_de_departage`).
**Alternative écartée** — Départager par l'identifiant technique (`pk`) : plus simple à implanter, mais sans signification pour la cellule pédagogique consultant l'écran — l'ordre d'insertion en base n'a aucun rapport avec la progressivité pédagogique, contrairement à l'intitulé qui, à défaut de mieux, reste au moins lisible.
**Impact sur les livrables** — aucun sur la conception ; signature à retrouver telle quelle par le moteur de génération du sprint 3 (§ 3.2 bis) : `ordre_topologique(formation) -> list[ElementReferentiel]`, pure, sans effet de bord.
**Reporté au livrable** — non applicable.

## D-40 — Fermeture de la première source de D-35 : RG-07 refuse désormais réellement un retrait bloqué par un prérequis
**Date** 2026-09-04 · **Story** US-REF-06 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — D-35 (US-REF-03) constatait qu'aucune des trois sources de RG-07 (prérequis, séance programmée, évaluation) n'existait encore, et que `ServiceReferentiel.retirer` ne pouvait donc **jamais** être réellement bloqué — le mécanisme d'énumération des opposants existait, mais ne trouvait rien. `Prerequis` (cette story) est la première des trois sources à exister.
**Décision** — `ServiceReferentiel.retirer` appelle désormais `ServicePrerequis.elements_lies(element)` avant toute suppression et refuse, avec l'énumération des matières concernées, si la liste n'est pas vide. **Ce contrôle est explicite, pas une interception de `ProtectedError`** : `Prerequis.element`/`element_prerequis` sont en `CASCADE`, pas en `PROTECT` (Prompt 10, § 6 — « la cascade n'est qu'un filet, le refus est la règle »), à la différence de ce que D-35 anticipait (« dès qu'une future story poseront un `on_delete=PROTECT` »). Testé (`test_retrait_d_une_matiere_liee_par_un_prerequis_est_refuse`, `test_retrait_refuse_meme_cote_prerequis`, `test_retrait_par_la_vue_est_refuse_et_affiche_les_liens`, et la preuve que la cascade reste un vrai filet : `test_suppression_directe_d_un_element_efface_ses_liens_par_cascade`, qui contourne délibérément le service).
**Alternative écartée** — Poser `on_delete=models.PROTECT` comme D-35 l'anticipait, pour réutiliser tel quel le mécanisme `ProtectedError`/`decrire_opposants` déjà en place : écarté parce que le Prompt 10 impose `CASCADE` explicitement (« retirer un élément du référentiel emporte les liens qui le concernent »), un retrait devant rester possible une fois le contrôle métier levé (prérequis retirés un par un), sans qu'un administrateur ait à nettoyer manuellement des `Prerequis` orphelins au préalable.
**Impact sur les livrables** — aucun sur la conception ; D-35 reste valide pour les deux sources encore reportées (séance programmée, sprint 3 ; évaluation, sprint 4).
**Reporté au livrable** — non applicable, referme un report déjà consigné.

## D-39 — Critères 3 et 4 d'US-REF-06 reportés à US-PLAN-04 et US-PLAN-05 (sprint 3)
**Date** 2026-09-04 · **Story** US-REF-06 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — Critère 3 (« les prérequis sont exploitables comme contrainte dure lors de la génération du programme ») et critère 4 (« une violation de prérequis lors d'une saisie manuelle est signalée explicitement ») décrivent un comportement du moteur de génération et de la saisie manuelle du programme, tous deux au sprint 3 (US-PLAN-04 — RG-36 —, US-PLAN-05), qui n'existent pas encore.
**Décision** — Cette story pose seulement ce que le moteur consommera plus tard : le modèle `Prerequis` et **deux fonctions de service pures et déjà exploitables telles quelles**, `trouver_chemin(depart, arrivee, formation)` et `ordre_topologique(formation)` (`referentiel/services/prerequis.py`), volontairement écrites au niveau du module plutôt que comme méthodes de `ServicePrerequis` pour rester importables depuis `planification` sans aucun contexte d'écran (§ 3.2 bis du Prompt 10). Un test le prouve (`test_les_deux_fonctions_de_graphe_sont_appelables_sans_contexte_d_ecran`).
**Alternative écartée** — Anticiper un stub du moteur qui « respecte » les prérequis sur un cas trivial : aurait engagé une conception du moteur hors du périmètre de cette story, avec le risque de devoir la défaire à US-PLAN-04.
**Impact sur les livrables** — aucun sur la conception actuelle ; les critères 3 et 4 restent à vérifier explicitement à US-PLAN-04/US-PLAN-05, qui devront réutiliser `trouver_chemin`/`ordre_topologique` telles quelles plutôt que de les récrire.
**Reporté au livrable** — non applicable, dette de développement déjà identifiée par le Prompt 10 lui-même (§ 1, § 10).

## D-38 — `TypeAction.SUPPRESSION_ELEMENT_GESTION` : quatrième nature du patron de gestion, le patron lui-même ne journalisait aucune suppression
**Date** 2026-09-03 · **Story** US-REF-05 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — `ServiceGestion.supprimer()` (le patron dont héritent cinq stories du référentiel) n'a jamais journalisé une suppression : les quatre entités qui en héritaient jusqu'ici (`TypeFormation`, `Formation`, `Matiere`, et implicitement `ElementReferentiel` par un service voisin) archivent au lieu de supprimer réellement — `.claude/rules/modeles.md` n'impose `CASCADE`/suppression réelle qu'en composition stricte. `ObjectifPedagogique` (§ 2.3 du Prompt 09) est la première entité du patron à supprimer réellement, et le Prompt 09 exige explicitement une suppression journalisée. Aucune valeur de `TypeAction` n'existait pour cette nature.
**Décision** — Ajout de `TypeAction.SUPPRESSION_ELEMENT_GESTION` (migration `administration/0011`, extension de la contrainte `ck_entree_journal_type_action`), et surcharge de `ServiceObjectifPedagogique.supprimer` (n'appelle pas `super()` : le patron ne journalise pas, donc rien à réutiliser sur ce point précis) pour capturer l'état avant suppression et journaliser avec cette nature. Compte, comme les trois autres natures génériques du patron, pour une seule extension au sens de RG-26 (voir D-18/D-27/D-32) : elles se distinguent par `objet_type`, pas par nature d'action.
**Alternative écartée** — Réutiliser `MODIFICATION_ELEMENT_GESTION` pour la suppression, en la distinguant seulement par `valeur_apres=None` : écarté parce qu'une entrée de journal doit désigner la nature de l'action par son `type_action`, pas par l'absence d'une valeur — un filtre du journal sur « suppression » n'aurait alors rien pu isoler.
**Impact sur les livrables** — aucun sur la conception ; note pour toute future entité du patron qui supprimerait réellement plutôt que d'archiver : la nature existe déjà, pas besoin d'une nouvelle migration.
**Reporté au livrable** — non applicable.

## D-37 — `ObjectifPedagogique` n'hérite pas de `ModeleArchivable` : seule entité du patron à supprimer réellement
**Date** 2026-09-03 · **Story** US-REF-05 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — Le Prompt 09, § 2.3, écarte explicitement l'archivage pour `ObjectifPedagogique` au profit d'une suppression réelle : un objectif pédagogique retiré d'une matière n'a pas vocation à réapparaître dans un historique consultable, contrairement à une matière ou une formation archivée qui reste une référence pour les formations passées.
**Décision** — `ObjectifPedagogique` ne porte pas `ModeleArchivable` ; `ServiceObjectifPedagogique` n'expose ni `archiver` ni `desarchiver`, et son `supprimer` (voir D-38) exécute un `DELETE` réel plutôt qu'un marquage. Testé par un test de non-présence (`test_n_a_pas_de_champ_d_archivage`) qui vérifie qu'aucun des deux champs du mixin n'apparaît sur le modèle.
**Alternative écartée** — Archiver comme les quatre autres entités du patron, par cohérence stricte : écarté parce que le Prompt 09 le demande explicitement, et qu'un objectif archivé traînerait indéfiniment dans une liste que rien, dans le cas d'usage CU-P2-06, n'a besoin de consulter après coup.
**Impact sur les livrables** — aucun sur la conception ; à signaler au mémoire comme l'unique exception documentée à la convention d'archivage du patron `ServiceGestion`.
**Reporté au livrable** — non applicable.

## D-36 — `coefficient`, `poidsFormatif`, `poidsCertificatif` : trois attributs de CLS-01 absents d'`ElementReferentiel`, non implantés dans cette story
**Date** 2026-09-03 · **Story** US-REF-03 (découverte à la relecture par le sous-agent `relecteur-conception`) · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — `docs/conception/13-diagramme-classes.md`, CLS-01, § 3.3, donne à `ElementReferentiel` **cinq** attributs propres, aucun marqué `[0..1]` (donc tous obligatoires) : `volumeHorairePrescrit`, `coefficient` (`decimal = 1`), `categorieLieuRequise`, `poidsFormatif` (`decimal`), `poidsCertificatif` (`decimal`) — confirmé par la note d'implémentation, § 4.1 (« portant … et les cinq attributs propres »). La note qui accompagne la classe dans le diagramme précise leur rôle : « Les deux poids règlent la part du formatif et du certificatif dans la note du module ». `PROMPT_08_US-REF-03_04_referentiel.md`, § 3.1, ne donne pourtant que trois attributs propres à implanter (`volume_horaire_prescrit`, `categorie_lieu`, `type_lieu_partage`) — `coefficient` et les deux poids n'y figurent pas, et rien dans le prompt ne signale cet écart avec CLS-01.
**Décision** — Implanté strictement selon le Prompt 08 : `coefficient`, `poidsFormatif`, `poidsCertificatif` **absents** du modèle `ElementReferentiel` posé ici. Les deux poids qualifient une note (formatif/certificatif), donc relèvent du domaine des évaluations — probablement une story du paquetage évaluations, sprint 4, plutôt que du référentiel. `coefficient` pondère vraisemblablement la même moyenne. Cette entrée consigne l'écart avec CLS-01 pour qu'il ne reste pas silencieux, sans trancher à quelle story il revient — ce n'est pas à cette story de le faire.
**Alternative écartée** — Ajouter les trois attributs maintenant, par fidélité stricte à CLS-01 : écarté parce que le Prompt 08 ne les demande pas, que leur usage réel (pondération de notes) dépend d'un domaine — évaluations — pas encore conçu en détail dans ce sprint, et qu'un attribut ajouté sans règle métier qui l'exploite est le genre d'ajout que `.claude/rules/modeles.md` décourage.
**Impact sur les livrables** — écart entre le code et CLS-01 à documenter au mémoire ; la story qui composera les évaluations (sprint 4) devra soit ajouter ces trois attributs à `ElementReferentiel` par migration, soit expliquer pourquoi ils vivent ailleurs.
**Reporté au livrable** — oui.

## D-35 — Critère 6 d'US-REF-03 et RG-07 : reportés à US-REF-06/US-PLAN/sprint 4, mécanisme déjà en place
**Date** 2026-09-03 · **Story** US-REF-03 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — RG-07 : une matière ne peut être retirée du référentiel si elle est référencée par un prérequis, une séance programmée ou une évaluation. Aucune des trois sources n'existe encore : prérequis vient avec US-REF-06 (ce sprint), séance programmée avec le sprint 3, évaluation avec le sprint 4. Le critère 6 d'US-REF-03 (« matière déjà programmée dans une session en cours ne peut être retirée ») n'est qu'un cas particulier de RG-07 via les séances. La table de tests du Prompt 08, § 7, liste pourtant une ligne « Retrait d'une matière bloquée → énumération des opposants » comme si elle était exerçable aujourd'hui.
**Décision** — Même traitement qu'à D-23 (US-REF-01) et D-30 (US-REF-02) : `ServiceReferentiel.retirer` réutilise le mécanisme générique (`ProtectedError` intercepté, `noyau.services.gestion.decrire_opposants` — extrait du patron à cette occasion, voir D-32) plutôt que d'écrire un contrôle RG-07 spécifique. Le test écrit prouve que la méthode existe et **ne trouve rien aujourd'hui** (`test_methode_d_enumeration_des_bloquants_existe_et_ne_trouve_rien`), pas qu'un retrait est effectivement bloqué — aucune donnée ne peut aujourd'hui produire ce blocage, faute des trois modèles sources. Dès qu'US-REF-06 (prérequis), une future story de séance ou d'évaluation poseront un `on_delete=PROTECT` vers `ElementReferentiel`, le retrait sera automatiquement refusé et les opposants énumérés, sans une ligne de code supplémentaire ici.
**Alternative écartée** — Construire un modèle factice dans un référentiel de test (sur le patron d'`essai_patron_gestion`) pour exercer un vrai blocage : aurait dupliqué la preuve déjà apportée une fois par `noyau/tests/test_service_gestion.py::test_element_reference_empeche_la_suppression_avec_enumeration`, sur un mécanisme strictement identique et déjà générique.
**Impact sur les livrables** — aucun sur la conception ; note pour US-REF-06, et pour les futures stories de séance/évaluation : poser `on_delete=models.PROTECT` vers `ElementReferentiel` suffit à rendre RG-07 et le critère 6 vrais et testables.
**Reporté au livrable** — non applicable, dette de développement déjà identifiée par le Prompt 08. Huitième report du paquetage référentiel — tous à vérifier avant la clôture du sprint (§ 3.3 du Prompt 08).

## D-34 — Critères 3 et 4 d'US-REF-04 reportés à US-PLAN-01 (moteur de génération, sprint 3)
**Date** 2026-09-03 · **Story** US-REF-04 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — Critères 3 (« les matières sans lieu requis ne consomment aucune ressource de salle ») et 4 (« la catégorie est exploitée comme contrainte par le moteur de génération ») décrivent un comportement du moteur de génération du programme hebdomadaire, qui appartient au sprint 3 (US-PLAN-01) et n'existe pas encore.
**Décision** — Cette story pose seulement la donnée que le moteur consommera plus tard : `ElementReferentiel.categorie_lieu` (trois valeurs : salle attitrée, lieu partagé, aucun lieu) et `type_lieu_partage`, tous deux exprimés en `TextChoices` avec les libellés exacts du centre (BNF-08). Aucun code de contrainte de génération n'est écrit ici — il n'y a rien à générer avant US-PLAN-01.
**Alternative écartée** — Anticiper un stub de moteur de génération qui « respecte » ces catégories sur un cas trivial : aurait engagé une conception du moteur hors du périmètre de cette story, avec le risque de devoir la défaire à US-PLAN-01.
**Impact sur les livrables** — aucun sur la conception actuelle ; les critères 3 et 4 restent à vérifier explicitement à la story du moteur de génération.
**Reporté au livrable** — non applicable, dette de développement déjà identifiée par le Prompt 08 lui-même (§ 1.7).

## D-33 — Deux paramètres BNF-13 provisoires pour comparer le référentiel à la durée de la formation
**Date** 2026-09-03 · **Story** US-REF-03 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — Le critère 5 d'US-REF-03 compare la somme des volumes prescrits (en heures) à la durée de la formation (en semaines, arbitrage D-25). Rien, dans aucun livrable, ne dit combien d'heures d'instruction compte une semaine au CIT, ni à partir de quel écart l'avertissement (non bloquant) doit se déclencher. La grille horaire, qui porterait la vraie réponse à la première question, appartient au paquetage P4 et arrive au sprint 2.
**Décision** — Deux paramètres dans `config/settings/base.py`, lus par `ServiceReferentiel.ecart()`, jamais codés en dur : `VOLUME_HORAIRE_HEBDOMADAIRE_REFERENCE` (30 h/semaine, provisoire) convertit la durée en volume attendu ; `SEUIL_ECART_VOLUME_REFERENTIEL_POURCENT` (10 %, provisoire) fixe le seuil de déclenchement, exprimé en pourcentage du volume attendu plutôt qu'en heures absolues pour rester pertinent aussi bien sur une formation de deux semaines que de cinquante-deux. L'avertissement (§ 3.30 de la charte) n'empêche jamais l'enregistrement — testé explicitement.
**Alternative écartée** — Un seuil en heures absolues : plus simple, mais un même seuil n'aurait aucun sens comparé à une formation courte ou longue — dix heures d'écart pèsent différemment sur deux semaines que sur cinquante-deux.
**Impact sur les livrables** — aucun sur la conception ; les deux valeurs sont à confirmer avec le chef de bureau pédagogique, et `VOLUME_HORAIRE_HEBDOMADAIRE_REFERENCE` est destiné à être remplacé par la grille horaire réelle dès le sprint 2 (US-RES, paquetage P4).
**Reporté au livrable** — oui, question pour le terrain sur les deux valeurs.

## D-32 — Deux extensions du patron `ServiceGestion` remontées pour `ServiceReferentiel`, qui n'en hérite pas
**Date** 2026-09-03 · **Story** US-REF-03 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — `ElementReferentiel` n'est pas une entité de gestion CRUD autonome mais une sous-ressource composée depuis l'écran d'une formation : `ServiceReferentiel` (`.claude/rules/services.md`, table des huit services) n'hérite donc pas de `ServiceGestion`, à la différence des quatre stories précédentes du référentiel. Il a pourtant exactement les mêmes besoins que le patron sur deux points : traduire un `ValidationError` Django en `ErreurValidation` métier (E2, volume non conforme), et énumérer les opposants à une suppression protégée (E3, RG-07) — la seconde occurrence exacte de chacun de ces deux motifs dans le projet.
**Décision** — Extraits de `ServiceGestion` vers deux fonctions libres au niveau du module `noyau/services/gestion.py` : `decrire_opposants(instance, opposants)` et `valider_instance(instance)`. `ServiceGestion._valider`/`.supprimer` délèguent désormais à ces fonctions plutôt que de porter la logique en interne ; `ServiceReferentiel` les appelle directement. Testé : la suite complète du patron (`noyau/tests/test_service_gestion.py`) passe sans modification après l'extraction, preuve que rien n'a régressé.
**Alternative écartée** — Dupliquer les deux motifs dans `ServiceReferentiel` : c'est exactement le genre de code « qui n'a rien de propre au référentiel » que les prompts successifs (06, 07, 08) demandent de remonter plutôt que de dupliquer — et la duplication aurait laissé deux implémentations du message E3 à maintenir en cohérence.
**Impact sur les livrables** — aucun sur la conception ; note d'implémentation pour tout futur service qui a besoin de valider un modèle ou d'énumérer des opposants sans hériter du patron de gestion.
**Reporté au livrable** — non applicable.

## D-31 — `TypeFormation.code` : attribut de CLS-01 jamais implémenté depuis US-REF-00, découvert à la relecture d'US-REF-02
**Date** 2026-09-03 · **Story** US-REF-02 (découverte ; l'écart lui-même remonte à US-REF-00) · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — En vérifiant D-28 (`Matiere.code`) contre `docs/conception/13-diagramme-classes.md`, CLS-01 porte aussi, sur `TypeFormation` : `code : texte {unique}` — sans `[0..1]`, donc obligatoire. Le modèle `TypeFormation` réellement posé à US-REF-00 (`app/referentiel/models.py`) ne porte que `intitule` : **le champ `code` n'existe pas du tout**, et aucune entrée de `DECISIONS.md` ne consigne cet écart depuis US-REF-00 — il n'avait jamais été repéré avant cette relecture.
**Décision** — **Ne pas toucher au modèle maintenant.** `TypeFormation` est déjà utilisé par `Formation` (US-REF-01, clé étrangère `PROTECT`) : y ajouter un champ pose la même question qu'à D-28 (format réel des codes, terrain non consulté), avec un risque supplémentaire — des types de formation sont potentiellement déjà créés en base de développement, donc une contrainte d'unicité sur un champ nouvellement ajouté doit être pensée comme celle de `Matiere` (facultative, partielle) plutôt qu'ajoutée à la légère. Cette entrée consigne l'écart pour qu'il ne soit plus « perdu », sans trancher son traitement.
**Alternative écartée** — Corriger immédiatement, par cohérence avec `Matiere.code` fraîchement ajouté : écarté parce que c'est un changement de modèle hors périmètre du Prompt 07 (qui porte sur `Matiere`, pas `TypeFormation`), qui mérite sa propre story ou au moins sa propre décision explicite plutôt qu'un ajout en passant.
**Impact sur les livrables** — écart entre CLS-01 et le code, antérieur à cette story, à documenter au mémoire au même titre que D-28 ; à traiter avant la clôture du sprint ou explicitement reporté à un sprint ultérieur — à la charge du binôme de décider quand.
**Reporté au livrable** — oui.

## D-30 — Critères 3 et 5 d'US-REF-02 reportés à US-REF-03 et US-INS-02, mécanisme déjà en place
**Date** 2026-09-03 · **Story** US-REF-02 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — Critère 3 : « La fiche d'une matière indique les formations qui l'utilisent dans leur référentiel. » Critère 5 : « Une matière utilisée dans au moins un référentiel ou une matrice de qualification ne peut être supprimée. » Les deux supposent des entités hors périmètre de cette story — `ElementReferentiel` (US-REF-03) et `Qualification` (US-INS-02) — toutes deux dans ce sprint, mais pas encore construites.
**Décision** — Comme pour le critère 4 d'US-REF-01 (D-23), aucun code spécifique : le mécanisme générique du patron (`ServiceGestion.supprimer`, `ProtectedError` intercepté et énumération des opposants) suffit déjà à E3, et se comportera correctement dès que les deux modèles cités poseront un `on_delete=PROTECT` vers `Matiere` — sans une ligne de code supplémentaire dans `referentiel`. La fiche de la matière (`matiere_detail.html`) réserve dès maintenant l'emplacement « Formations utilisatrices », vide et commenté, pour que son remplissage à US-REF-03 soit un ajout de contenu, pas une refonte d'écran.
**Alternative écartée** — Écrire une méthode dédiée `Matiere.formations_utilisatrices()` par anticipation d'un modèle (`ElementReferentiel`) non encore conçu : même risque qu'à D-23, une structure de données devinée à refaire.
**Impact sur les livrables** — aucun sur la conception ; note pour US-REF-03 et US-INS-02 : poser `on_delete=models.PROTECT` sur les clés étrangères vers `Matiere` suffit à rendre le critère 5 vrai et testable, et à remplir l'emplacement du critère 3 sur la fiche.
**Reporté au livrable** — non applicable, dette de développement déjà identifiée par le Prompt 07. Cinquième et sixième report du paquetage référentiel (après les critères 2 et 4 d'US-REF-00/01, D-22, D-23) — **à vérifier tous ensemble avant la clôture du sprint**, comme demandé au § 5 du Prompt 07.

## D-29 — Le référentiel référencera la matière, il ne la recopiera jamais — contrainte posée pour US-REF-03
**Date** 2026-09-03 · **Story** US-REF-02 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — Critère 6 du backlog v7 : « Toute modification d'une matière du catalogue est répercutée pour l'ensemble des formations concernées. » Le Prompt 07 (§ 2) est explicite : ce critère ne demande aucun mécanisme de propagation, il est satisfait par construction **si et seulement si** US-REF-03 fait de `ElementReferentiel` une référence vers `Matiere` (clé étrangère), jamais une copie de son intitulé.
**Décision** — Rien à coder ici ; la contrainte est purement documentaire, mais engageante pour la story suivante. Consignée pour qu'US-REF-03 ne recopie jamais `Matiere.intitule` (ni `Matiere.code`) dans un champ propre à `ElementReferentiel` — ce serait exactement le genre de raccourci qui semble anodin au moment de l'écrire et qui invalide le critère 6 trois sprints plus tard, silencieusement.
**Alternative écartée** — Aucune, cette entrée ne tranche rien de nouveau ; elle rend explicite une contrainte déjà donnée par le Prompt 07 pour qu'elle survive au `/clear` avant US-REF-03.
**Impact sur les livrables** — aucun sur la conception actuelle ; contrainte de conception à vérifier explicitement à la relecture d'US-REF-03.
**Reporté au livrable** — non applicable.

## D-28 — Code de matière implémenté facultatif, alors que CLS-01 le prévoit obligatoire — écart de cardinalité assumé
**Date** 2026-09-03 · **Story** US-REF-02 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — Corrige une erreur de fait de la première rédaction de cette entrée, trouvée à la relecture par le sous-agent `relecteur-conception` : contrairement à ce qui était écrit ici, `docs/conception/13-diagramme-classes.md` (CLS-01) porte déjà `code : texte {unique}` sur `Matiere` — **sans** la marque `[0..1]` (§ 1.2 : facultatif), donc obligatoire dans le modèle de référence. Le Prompt 07 § 4 (« Aucun livrable n'en prévoit ») et ma première rédaction de cette entrée (« absent du modèle conceptuel de référence ») étaient l'un et l'autre inexacts — je n'avais pas vérifié CLS-01 avant d'écrire l'une ou l'autre affirmation. La vraie question n'a jamais été « faut-il ajouter cet attribut », mais « connaît-on déjà le format réel des codes du CIT », qui reste entière : aucun livrable ne le précise, et le terrain a peut-être un système de codification en usage qu'il faudrait reprendre, pas concurrencer.
**Décision** — Implémenté malgré tout **facultatif** : `Matiere.code` — `CharField(max_length=20, blank=True)`, unique si renseigné, `UniqueConstraint(Upper("code"), condition=~Q(code=""), name="uq_matiere_code")`. Rendre le champ obligatoire comme CLS-01 le prévoit forcerait à saisir une valeur à chaque création sans connaître le format attendu par le terrain — au risque de coder en dur une numérotation inventée, qu'il faudrait ensuite migrer si elle ne correspond pas à l'usage réel. Le facultatif absorbe cette incertitude sans bloquer la création de matières en attendant la réponse du chef de bureau pédagogique.
**Alternative écartée** — Suivre CLS-01 à la lettre (champ obligatoire) : plus fidèle formellement à la conception de référence, mais aurait imposé une valeur inventée à toute matière créée d'ici la réponse du terrain, avec le risque de devoir toutes les corriger ensuite.
**Impact sur les livrables** — **écart de cardinalité assumé entre le code et CLS-01**, à documenter explicitement au mémoire (`Matiere.code` : `[0..1]` en réalité, `{unique}` conservé côté implémentation via une contrainte partielle plutôt qu'une contrainte simple). Le diagramme de référence, lui, n'est pas à corriger : c'est l'implémentation qui s'en écarte temporairement, pas une erreur de conception à reprendre.
**Reporté au livrable** — oui, pour le format réel du code (question terrain, qui déterminera si le champ redevient obligatoire) ; non pour l'écart de cardinalité lui-même, qui est à consigner dès maintenant.

## D-27 — Deux extensions génériques remontées au patron `ServiceGestion`
**Date** 2026-09-03 · **Story** US-REF-01 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — US-REF-01 a besoin (a) de filtrer la liste des formations par type, (b) d'afficher le nombre de formations rattachées sur la liste des types sans une requête par ligne. Aucun des deux besoins n'est propre aux formations : le patron `ServiceGestion` (posé à US-REF-00) ne prévoyait qu'un filtre d'état et une recherche texte libre, et construisait son queryset de base en dur (`MODELE.objects.all()`), sans point d'extension pour un `select_related` ou une annotation.
**Décision** — Deux ajouts génériques à `noyau/services/gestion.py`, testés sur `essai_patron_gestion` (pas sur `Formation` — un patron testé à travers un seul usage n'est pas un patron, cf. Prompt 05 § 7) : `CHAMPS_FILTRABLES`, tuple de noms de champs filtrés par égalité dans `lister()` (filtre ignoré si absent ou vide) ; `_queryset()`, classmethod appelée par `lister()` à la place du littéral `MODELE.objects.all()`, surchargée par `ServiceFormation` (`select_related("type_formation")`) et par `ServiceTypeFormation` (`annotate(nombre_formations=Count("formations"))`).
**Alternative écartée** — Écrire le filtre par type et l'annotation directement dans `ServiceFormation.lister()`/`ServiceTypeFormation.lister()`, en dupliquant le corps de la méthode du patron : c'est exactement le genre de code « qui n'a rien de propre aux formations » que le Prompt 06 demande de remonter plutôt que de dupliquer — trois autres stories du référentiel (US-REF-02, 05, 07) héritent du même patron et auront vraisemblablement le même besoin.
**Impact sur les livrables** — aucun sur la conception ; note d'implémentation pour toute future story de gestion qui a besoin d'un filtre par relation ou d'une colonne calculée par agrégation.
**Reporté au livrable** — non applicable.

## D-26 — Contradiction backlog v7 / fiche CU-P2-02 sur l'unicité de l'intitulé — tranchée en faveur de la fiche
**Date** 2026-09-03 · **Story** US-REF-01 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — Le backlog v7 dit « l'intitulé est unique » (sans plus de précision) ; la fiche des cas d'utilisation v4 (CU-P2-02) dit « l'intitulé est unique au sein d'un type de formation ». Les deux documents portent la même date. Ce n'est pas une nuance de rédaction : le premier interdit deux formations homonymes dans tout le centre, le second les autorise dès lors qu'elles s'adressent à des publics différents — une *Formation initiale* pour officiers et une *Formation initiale* pour sous-officiers sont deux objets légitimement distincts.
**Décision** — Implanté selon la fiche des cas d'utilisation, la plus précise : contrainte composite `uq_formation_type_intitule` sur `(type_formation_id, UPPER(intitule))`, posée en base (`UniqueConstraint` avec `F("type_formation")` et `Upper("intitule")`, cohérent avec l'insensibilité à la casse déjà retenue pour `TypeFormation`, D-21). `ServiceFormation._erreur_unicite` est surchargée pour désigner le doublon dans le bon type, le patron `ServiceGestion._erreur_unicite` ne connaissant qu'une unicité à un seul champ.
**Alternative écartée** — Suivre le backlog v7 littéralement (intitulé unique dans tout le centre) : plus simple à poser (le patron l'aurait couvert sans surcharge), mais aurait interdit un cas d'usage réel et légitime du CIT — deux formations de même nom pour deux publics différents.
**Impact sur les livrables** — le backlog v7 devra être corrigé pour reprendre la formulation de la fiche des cas d'utilisation, ou l'arbitrage inversé si le chef de bureau pédagogique en décide autrement. **Question pour le terrain, non tranchée définitivement ici.**
**Reporté au livrable** — oui, à la prochaine revue avec le chef de bureau pédagogique.

## D-25 — Unité de la durée d'une formation : la semaine, proposée et non confirmée
**Date** 2026-09-03 · **Story** US-REF-01 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — Aucun livrable ne dit si la durée d'une formation s'exprime en semaines, en jours ou en heures. Elle n'est pas dérivable : le volume horaire prescrit appartient au futur référentiel (US-REF-03), et les dates appartiennent à la session (US-SES-01, sprint 2).
**Décision** — `duree_semaines`, entier strictement positif (`PositiveSmallIntegerField` + `MinValueValidator(1)` côté Python, contrainte `ck_formation_duree_positive` en base). Le nom du champ porte l'unité pour rester lisible sans documentation ; le formulaire l'affiche accolée (§ 3.18 de la charte). Choix motivé par la cohérence avec le programme hebdomadaire, unité de travail du centre — mais **c'est une proposition, pas une donnée du terrain**.
**Alternative écartée** — Un couple (valeur, unité) au choix de l'utilisateur : plus flexible, mais aurait ajouté une complexité (conversion, affichage) que rien dans les livrables ne justifie, et aurait retardé la story pour un besoin non confirmé.
**Impact sur les livrables** — aucune classe ni règle du diagramme de classes à reprendre si la semaine est confirmée ; à renommer et migrer si le terrain répond « jours » ou « heures ».
**Reporté au livrable** — oui, question ouverte pour le terrain, à trancher avec la cellule pédagogique.

## D-24 — Spécialité de formation : texte libre, non une entité du modèle
**Date** 2026-09-03 · **Story** US-REF-01 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — Aucun livrable ne dit si la spécialité d'une formation est un texte libre ou une valeur d'une liste fermée, et aucune entité *Spécialité* n'existe au diagramme de classes (`docs/conception/13-diagramme-classes.md`, CLS-01).
**Décision** — `CharField` texte libre. Une énumération inventée maintenant serait fausse (aucune source ne liste les valeurs possibles), et une entité créée sans besoin confirmé alourdirait le modèle sans bénéfice démontré. La spécialité qualifie la formation, jamais la brigade — la brigade reste un outil de séparation des effectifs, pas une spécialité pédagogique (ne pas confondre les deux dans une future story).
**Alternative écartée** — Une énumération `TextChoices` à valeurs devinées : aurait figé une liste sans source, à corriger dès le premier retour du terrain — plus coûteux qu'un texte libre migré vers une entité si le besoin se confirme.
**Impact sur les livrables** — aucun sur le diagramme de classes actuel ; à revoir si le terrain confirme un besoin de liste fermée (nouvelle entité `Specialite`, migration de données).
**Reporté au livrable** — oui, question ouverte pour le terrain.

## D-23 — Critère 4 d'US-REF-01 (suppression bloquée par une session ouverte) : reporté à US-SES-01, mécanisme posé dès maintenant
**Date** 2026-09-03 · **Story** US-REF-01 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — Critère 4 du backlog v7 : « Une formation disposant de sessions ouvertes ne peut être supprimée. » `Session` appartient au paquetage P3, sprint 2 (US-SES-01) : ni créable ni testable ici.
**Décision** — Aucun code spécifique écrit pour ce critère : le mécanisme générique du patron (`ServiceGestion.supprimer`, qui intercepte `ProtectedError` et énumère les opposants — voir D-20) suffit déjà à ce qu'exige E3 de la fiche générique. Dès qu'US-SES-01 posera `Session.formation` avec `on_delete=PROTECT`, la suppression d'une formation portant une session ouverte sera automatiquement refusée et les sessions énumérées, **sans une ligne de code supplémentaire dans `referentiel`**. Aujourd'hui, `ServiceFormation.supprimer` (hérité, non surchargé) ne bloque que sur un futur `ElementReferentiel` protégé (US-REF-03) — aucune donnée ne le référence encore, le critère 4 reste donc non vérifié par un test tant qu'aucun des deux modèles n'existe.
**Alternative écartée** — Écrire une méthode dédiée `Formation.a_des_sessions_ouvertes()` par anticipation : aurait anticipé une structure de données (`Session`, son état) non encore conçue, avec un risque élevé de devoir la refaire à US-SES-01.
**Impact sur les livrables** — aucun sur la conception ; note pour US-SES-01 : poser `on_delete=models.PROTECT` sur la clé étrangère vers `Formation` suffit à rendre le critère 4 vrai et testable.
**Reporté au livrable** — non applicable, dette de développement déjà identifiée par le Prompt 06.

## D-22 — Critères 2 et 4 reportés à US-REF-01, comme annoncé
**Date** 2026-09-03 · **Story** US-REF-00 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — Backlog v7, critères d'acceptation de US-REF-00 : « Une formation est rattachée à un type et un seul » (2) et « Les listes de formations sont filtrables par type » (4) supposent l'entité Formation, hors périmètre de cette story (elle arrive avec US-REF-01). Le Prompt 05 l'annonçait déjà lui-même en § 1 et le demandait consigné.
**Décision** — Consigné ici formellement : les critères 2 et 4 ne sont pas vérifiés par cette story, ni par aucun test. US-REF-01 les portera, avec la clé étrangère `Formation.type` (`on_delete=PROTECT`) qui rendra aussi le critère 3 (suppression refusée si utilisé) réellement exerçable — cette story-ci n'a pu le prouver que sur le modèle de test dédié du patron (`essai_patron_gestion`), pas sur un `TypeFormation` réellement référencé.
**Alternative écartée** — Écrire des tests factices simulant une Formation pour « couvrir » ces critères maintenant : aurait testé un modèle qui n'existe pas encore, sans valeur, et à refaire entièrement dès que le vrai modèle Formation apparaît.
**Impact sur les livrables** — aucun sur la conception ; trace explicite pour la revue de sprint du 12 septembre.
**Reporté au livrable** — non applicable, dette de développement déjà identifiée par le prompt.

## D-21 — Unicité de l'intitulé insensible à la casse
**Date** 2026-09-03 · **Story** US-REF-00 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — § 5 du Prompt 05 demandait un arbitrage motivé en deux phrases : deux types nommés *Officiers* et *officiers* doivent-ils coexister ?
**Décision** — Non : contrainte insensible à la casse, `UniqueConstraint(Upper("intitule"), name="uq_type_formation_intitule")`. Deux intitulés qui ne diffèrent que par la casse désignent le même public aux yeux d'un utilisateur ; les laisser coexister ouvrirait la porte à des doublons accidentels indiscernables à l'écran. L'intitulé affiché garde la casse choisie à la création — seule la comparaison d'unicité est insensible à la casse, pas la valeur stockée.
**Alternative écartée** — Unicité sensible à la casse (contrainte simple `unique=True` sur `intitule`) : plus simple à poser, mais n'empêche pas le doublon accidentel que l'arbitrage cherche justement à éviter.
**Impact sur les livrables** — aucun sur la conception ; fixe la sémantique d'unicité pour toute future entité du référentiel qui reprendrait le même patron.
**Reporté au livrable** — non, à faire au prochain relevé du mémoire.

## D-20 — E3 du patron ne protège que la suppression, pas l'archivage — écart avec le libellé du Prompt 05, § 7
**Date** 2026-09-03 · **Story** US-REF-00 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — § 2.3 du Prompt 05 est sans ambiguïté : « Archiver | Toujours possible » contre « Supprimer | Seulement si jamais référencé ». La table de tests du patron, § 7, porte pourtant la ligne : « Élément référencé → **archivage** refusé, éléments opposants énumérés | E3 » — en contradiction directe avec § 2.3. La définition générique d'E3 (§ 1, fiche générique) couvre elle-même « archivage **ou** suppression refusé », ce qui explique l'origine du libellé sans lever la contradiction avec la règle concrète posée en § 2.3 pour ce patron précis.
**Décision** — Implanté et testé selon § 2.3, qui fait foi (règle concrète et motivée) sur § 7 (table de tests, susceptible d'une coquille de transcription) : `ServiceGestion.archiver` n'a aucune condition, `ServiceGestion.supprimer` seule intercepte `ProtectedError` et lève E3. Le test correspondant (`noyau/tests/test_service_gestion.py::test_element_reference_empeche_la_suppression_avec_enumeration`) porte sur la suppression, avec un commentaire renvoyant à cette décision.
**Alternative écartée** — Bloquer aussi l'archivage d'un élément référencé : contredirait directement § 2.3 et la règle générale de la fiche générique (« L'archivage remplace la suppression dès qu'un élément est référencé » — un élément référencé doit au contraire pouvoir être archivé, c'est précisément le mécanisme prévu pour lui).
**Impact sur les livrables** — Prompt 05, § 7 (ou le dossier de cas d'utilisation dont il dérive) à corriger : « archivage refusé » devrait lire « suppression refusée ».
**Reporté au livrable** — non, à faire au prochain relevé du mémoire — signalement prioritaire, la contradiction est dans la conception source elle-même.

## D-19 — `ServiceGestion` : la dépendance à `administration` s'injecte, elle ne s'importe pas
**Date** 2026-09-03 · **Story** US-REF-00 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — § 2.1 du Prompt 05 impose `ServiceGestion` dans `app/noyau/services/gestion.py`. Il doit vérifier l'habilitation (`verifier_habilitation`, qui journalise) et journaliser créations/modifications/archivages (`ServiceJournal`) — les deux vivent dans `administration`. Le précédent D-14 (import différé, à l'intérieur d'une méthode) a été essayé en premier, par analogie : il échoue ici, car `test_ordre_des_dependances_entre_applications` (`tests/architecture/test_couches.py`) parcourt l'arbre syntaxique du **fichier entier** et signale tout `ImportFrom` vers une application non autorisée, **sans distinguer un import en tête de module d'un import à l'intérieur d'une fonction** — contrairement à D-14, qui ne franchissait aucune frontière d'application (`administration.habilitations` important `administration.services.journal`, la même application).
**Décision** — Injection par attributs de classe. `ServiceGestion` déclare `PERMISSION_LECTURE`/`PERMISSION_ECRITURE`, `VERIFIER_HABILITATION`, `ENREGISTRER_JOURNAL`, `DONNEES_JOURNAL`, `NATURE_CREATION`/`MODIFICATION`/`ARCHIVAGE` à `None`, sans jamais importer `administration`. La sous-classe (`ServiceTypeFormation`, dans `referentiel`, autorisée à dépendre d'`administration`) les renseigne : `VERIFIER_HABILITATION = staticmethod(verifier_habilitation)`, `ENREGISTRER_JOURNAL = staticmethod(ServiceJournal.enregistrer_detaillee)`, etc. `noyau/services/gestion.py` n'importe rien d'`administration`, ni en tête de fichier ni ailleurs — vérifié réellement par `pytest tests/architecture`.
**Alternative écartée** — Des méthodes-crochets (`_verifier_habilitation`, `_journaliser`) que chaque sous-classe redéfinit entièrement : aurait dupliqué la même poignée de lignes cinq fois (une par story du patron) au lieu de les injecter une fois comme valeurs. L'injection par attributs porte le même principe (la sous-classe fournit ce que `noyau` ne peut pas importer) avec moins de code répété.
**Impact sur les livrables** — aucun sur la conception ; note d'implémentation pour toute future méthode de `ServiceGestion` qui aurait besoin d'`administration`.
**Reporté au livrable** — non applicable.

## D-18 — Trois natures génériques pour le patron de gestion, pas une par entité
**Date** 2026-09-03 · **Story** US-REF-00 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — § 2.6 du Prompt 05 : les créations, modifications et archivages du référentiel sont journalisés dès maintenant. Cinq stories (US-REF-00, 01, 02, 05, 07) partagent le même patron `ServiceGestion`. Une nature `TypeAction` par action **et par entité** aurait posé quinze valeurs (3 × 5) au fil des stories, pour un même mécanisme générique.
**Décision** — Trois valeurs seulement : `CREATION_ELEMENT_GESTION`, `MODIFICATION_ELEMENT_GESTION`, `ARCHIVAGE_ELEMENT_GESTION`, réutilisées par toutes les entités du patron. L'entité concernée se distingue par `objet_type` (`"type_formation"`, etc.), pas par la nature de l'action — exactement à quoi sert ce couple, posé en D-15.
**Alternative écartée** — Une nature par entité (`creation_type_formation`, `creation_matiere`, …) : distinguerait l'action ET l'entité au même endroit, redondant avec `objet_type` qui porte déjà cette distinction, et ferait grossir l'énumération à chaque nouvelle story du patron.
**Impact sur les livrables** — Le prompt annonce que ce sera « la troisième extension » à RG-26 ; c'est inexact depuis D-16 (`MODIFICATION_HABILITATIONS` en était déjà une troisième, non signalée en son temps) — avec ces trois valeurs-ci, c'est la **quatrième** extension, comptée comme un seul bloc (trois valeurs, un seul fait générateur : le patron de gestion).
**Reporté au livrable** — non, à faire au prochain relevé du mémoire.

## D-16 — Trois natures hors RG-26, pas deux : `MODIFICATION_HABILITATIONS` retrouvée
**Date** 2026-09-03 · **Story** US-ADM-04 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — § 2.5 du Prompt 04 annonçait deux extensions à RG-26 à signaler : `ACCES_REFUSE` et `CONSULTATION_JOURNAL`. En construisant l'énumération complète (voir D-17 plus bas), `MODIFICATION_HABILITATIONS` (posée en US-ADM-03) s'est révélée être une **troisième** extension, jamais signalée en son temps — recherche faite dans `DECISIONS.md`/`HABILITATIONS.md`, aucune trace.
**Décision** — Signaler les trois, pas deux : `ACCES_REFUSE` (US-ADM-03), `MODIFICATION_HABILITATIONS` (US-ADM-03, oubli corrigé ici), `CONSULTATION_JOURNAL` (US-ADM-04). Les trois sont hors RG-26, à porter au cahier des charges.
**Alternative écartée** — Ne signaler que les deux annoncées par le prompt et laisser l'oubli de `MODIFICATION_HABILITATIONS` tel quel : aurait perpétué une rupture de traçabilité déjà identifiée comme un risque par le prompt lui-même (« une nature journalisée sans règle d'origine »).
**Impact sur les livrables** — RG-26 (ou son commentaire associé) à compléter de trois natures hors énoncé, pas deux.
**Reporté au livrable** — non, à faire au prochain relevé du mémoire.

## D-17 — `TypeAction` porte l'énumération complète de RG-26, y compris les natures pas encore atteignables
**Date** 2026-09-03 · **Story** US-ADM-04 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — § 2.5 du Prompt 04 : RG-26 énumère cinq natures ; trois portent sur des objets qui n'existent pas encore (note, programme, sujet) et n'avaient donc aucune valeur `TypeAction`. Le prompt demande de déclarer l'énumération complète dès maintenant, pour que les stories des sprints 2 à 4 s'y rattachent sans ajouter de valeur — première lecture du plan avait manqué ce point, corrigé en cours d'implantation.
**Décision** — Cinq valeurs ajoutées : `SAISIE_NOTE`, `MODIFICATION_NOTE` (« saisie et modification d'une note »), `VALIDATION_PROGRAMME`, `REJET_PROGRAMME` (« validation ou rejet d'un programme »), `SELECTION_SUJET` (« sélection d'un sujet d'examen »). Granularité alignée sur le précédent des actions de compte (US-ADM-02) : un verbe RG-26 qui couvre plusieurs sous-actions distinctes reçoit une valeur par sous-action.
**Alternative écartée** — Une seule valeur composite par bullet RG-26 (ex. `ACTION_NOTE` au lieu de deux) : aurait contredit le patron déjà posé pour les comptes (`CREATION_COMPTE`/`MODIFICATION_COMPTE`/... — cinq valeurs pour un seul bullet RG-26), source d'incohérence entre les deux familles.
**Impact sur les livrables** — migration `0008_entree_journal_natures_rg26_completes` ; aucune de ces cinq valeurs n'est encore atteignable depuis un service ou une vue (RG-26 lui-même le prévoit : objets hors périmètre).
**Reporté au livrable** — non, à faire au prochain relevé du mémoire.

## D-15 — `objet_type`/`objet_identifiant`, additifs à `cible`, jamais un remplacement
**Date** 2026-09-03 · **Story** US-ADM-04 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — CU-P1-03 exige un filtre par objet concerné, structuré en couple type/identifiant. `.claude/rules/migrations.md` anticipait déjà ces deux noms de colonnes depuis le socle (voir D-04), jamais posés faute d'écran de consultation. `cible` (posé en US-ADM-01 sans définition claire, voir D-04) porte aujourd'hui des choses différentes selon l'appelant, et **plusieurs tests des trois stories précédentes lisent `.cible`/`cible=` directement** (`test_authentification.py`, `test_comptes.py`, `test_journal.py`) — le renommer casserait la non-régression exigée par le Prompt 04, § 7.
**Décision** — `objet_type`/`objet_identifiant` ajoutés comme deux champs **nouveaux**, `cible` intact. Retrofit additif (nouveaux paramètres seulement) sur les points d'appel existants qui ont un objet naturel : comptes (`objet_type="utilisateur"`), refus d'habilitation (`"permission"`), commande et croisement d'habilitations (`"groupe_habilitation"`/`"croisement_habilitation"`). `authentification.py` non touché : aucun objet réel quand le compte visé n'existe pas.
**Alternative écartée** — Renommer `cible` en `objet_identifiant` : correspond mieux à l'intention d'origine de `migrations.md`, mais casse cinq assertions de tests déjà committés dans trois stories antérieures.
**Impact sur les livrables** — `.claude/rules/migrations.md` corrigée sur `idx_journal_objet` → en réalité `idx_journal_nature_auteur` posé (voir Prompt 04, § 5 : l'index composé demandé porte sur nature/auteur, pas objet_type/objet_identifiant).
**Reporté au livrable** — non, à faire au prochain relevé du mémoire.

## D-14 — Import différé dans `ServiceJournal.consulter` pour éviter un cycle avec `administration.habilitations`
**Date** 2026-09-03 · **Story** US-ADM-04 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — `ServiceJournal.consulter` doit vérifier `noyau.administration_lecture`, donc appeler `administration.habilitations.verifier_habilitation`. Mais `administration/habilitations.py` importe déjà `ServiceJournal` en tête de module (pour journaliser un refus, voir D-09) : un import de `verifier_habilitation` en tête de `journal.py` créerait un cycle d'import — vérifié réellement, `ImportError: cannot import name 'ServiceJournal' from partially initialized module`.
**Décision** — Import différé (à l'intérieur de la méthode `consulter`, pas en tête de module) côté `journal.py` : le cycle n'existe qu'au moment du chargement des modules, plus une fois les deux modules complètement chargés.
**Alternative écartée** — Déplacer l'import de `ServiceJournal` dans `habilitations.py` en import différé à la place : symétriquement valable, mais `verifier_habilitation` y est appelée par bien plus de points d'entrée que `consulter` ne l'est ici — modifier le point le plus récent et le moins sollicité limite la portée du contournement.
**Impact sur les livrables** — aucun sur la conception ; note d'implémentation pour toute future méthode de service qui aurait besoin des deux côtés de cette frontière.
**Reporté au livrable** — non applicable.

## D-13 — `pfe_cit_app` regreffé sur `test_pfe_cit` : la seconde connexion de test ne fonctionnait pas
**Date** 2026-09-03 · **Story** US-ADM-04 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — § 2.2 du Prompt 04 demande un test RG-27 sous une seconde connexion, avec le rôle applicatif `pfe_cit_app`, distincte de la connexion `pfe_cit_migration` de la suite de tests. Vérifié réellement avant d'écrire quoi que ce soit : `has_table_privilege('pfe_cit_app', 'administration_entree_journal', 'SELECT')` retourne `false` sur `test_pfe_cit` — `pfe_cit_app` n'y a **aucun** privilège, INSERT et SELECT compris. Cause : `ALTER DEFAULT PRIVILEGES` (posé dans `01_roles.sql`, une fois, contre la base `pfe_cit`) ne se propage pas à `test_pfe_cit`, une base distincte créée après coup par `pfe_cit_migration`. Un test d'UPDATE-refusé écrit naïvement aurait donc prouvé l'absence totale de droits, pas la révocation ciblée par RG-27.
**Décision** — `conftest.py` à la racine du dépôt, qui étend le fixture `django_db_setup` de pytest-django : une fois la base de test migrée, regreffe `GRANT SELECT, INSERT, UPDATE, DELETE ... TO pfe_cit_app` sur `test_pfe_cit`, puis rejoue immédiatement la révocation ciblée de la migration 0007 (`REVOKE UPDATE, DELETE`). L'état final de `test_pfe_cit` reproduit exactement celui de `pfe_cit`.
**Alternative écartée** — Étendre `01_roles.sql` pour viser aussi `test_pfe_cit` : impossible, cette base n'existe pas encore au moment où le script Docker s'exécute (elle est créée à la demande par pytest-django, potentiellement avec `--reuse-db`).
**Impact sur les livrables** — aucun sur la conception ; corrige un vrai défaut de la configuration de test du socle, pas seulement de cette story.
**Reporté au livrable** — non applicable.

## D-12 — `GROUPES`/`MATRICE` déplacées vers `administration/constantes.py`
**Date** 2026-09-02 · **Story** US-ADM-03 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — Relecture (`relecteur-conception`) : `services/matrice_habilitations.py` importait `GROUPES`/`MATRICE` depuis `management/commands/initialiser_habilitations.py` — un service qui dépend d'une commande d'administration est à l'envers du sens naturel des couches (la commande est un point d'entrée, censé consommer des constantes, pas les définir).
**Décision** — `GROUPES` et `MATRICE` déménagées dans `administration/constantes.py`, conformément à `.claude/rules/python.md` (« `constantes.py` : valeurs de domaine »). La commande et le service l'importent désormais tous deux depuis ce module commun.
**Alternative écartée** — Laisser la dépendance en l'état : aucun test d'architecture ne l'interdit (les deux modules sont dans la même application), mais la charge de compréhension future ne le justifiait pas.
**Impact sur les livrables** — aucun sur la conception.
**Reporté au livrable** — non applicable.

## D-11 — Noms de domaine composés : `instructeurs_qualifications`, `lieux_calendrier`
**Date** 2026-09-02 · **Story** US-ADM-03 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — Le catalogue (§ 2.1 du prompt) demande des codes de domaine dérivés de § 11.2, sur le motif `referentiel`, `programme_validation`. Deux lignes de la matrice portent un libellé à deux notions : « Instructeurs et qualifications », « Lieux et calendrier ».
**Décision** — Codes composés, dérivés littéralement du libellé : `instructeurs_qualifications`, `lieux_calendrier`. Pas de raccourci (`instructeurs` seul, `lieux` seul) qui aurait pu laisser croire à un domaine plus étroit que ce que la ligne couvre réellement.
**Alternative écartée** — Scinder chaque ligne en deux domaines distincts (`instructeurs`/`qualifications`, `lieux`/`calendrier`) : aurait doublé le catalogue à 22 permissions sans que la matrice § 11.2 ne distingue jamais les deux à l'intérieur d'une même ligne — aucune cellule ne les sépare.
**Impact sur les livrables** — aucun sur la conception ; fixe la terminologie du catalogue pour toutes les stories des sprints 2 à 4.
**Reporté au livrable** — non, à faire au prochain relevé du mémoire.

## D-10 — Un seul attribut de classe pour § 2.4, pas deux
**Date** 2026-09-02 · **Story** US-ADM-03 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — § 2.4 du prompt annonce « chaque classe de service porte deux attributs de classe », mais n'en montre qu'un (`DOMAINE`), et le test d'architecture décrit à la même section ne vérifie que la présence d'un domaine.
**Décision** — Un seul attribut implanté : `DOMAINE`. Écart signalé, pas résolu par une invention de ma part — c'est la même famille d'incohérence que les comptes d'icônes de la charte (§ 1.11, `docs/suivi/CHARTE-INTEGRATION.md`) : un texte d'introduction qui ne correspond pas exactement à ce qui suit.
**Alternative écartée** — Ajouter un second attribut de mon invention (ex. un niveau minimal requis) : rien dans le prompt ne le définit, l'inventer aurait été plus risqué que de le signaler.
**Impact sur les livrables** — aucun.
**Reporté au livrable** — non applicable.

## D-09 — Le mécanisme d'habilitation qui journalise vit dans `administration`, pas `noyau`
**Date** 2026-09-02 · **Story** US-ADM-03 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — § 2.2 exige que `verifier_habilitation` journalise désormais chaque refus (RG-26). Journaliser passe par `ServiceJournal`, qui vit dans `administration`. Or `verifier_habilitation` (et les deux mécanismes de présentation qui en dépendent, `exige_habilitation` et `HabilitationMixin`) vivait dans `noyau`, qui ne doit dépendre d'aucune application — même mur que l'intergiciel d'US-ADM-02 (D-08). La commande `initialiser_habilitations` du socle, elle aussi posée dans `noyau`, doit désormais journaliser son option `--reinitialiser` (§ 5) : même contrainte, même conclusion.
**Décision** — Répartition en deux temps, cohérente avec D-08 :
- `noyau/habilitations.py` ne garde que `a_permission(utilisateur, permission)` — silencieuse, sans journal, utilisable partout y compris par le processeur de contexte du noyau lui-même.
- `administration/habilitations.py` (nouveau) porte `verifier_habilitation`, `exige_habilitation`, `HabilitationMixin` — les trois exigent le journal.
- La commande `initialiser_habilitations` déménage de `noyau/management/commands/` vers `administration/management/commands/` — `noyau/management/` est retiré, devenu vide.
**Alternative écartée** — Un registre d'injection : `noyau` exposerait un point d'enregistrement vide, qu'`administration` remplirait au démarrage (`AppConfig.ready()`). Respecte la lettre du prompt (ces symboles restent nommément dans `noyau`), mais introduit un état global mutable pour un gain resté conceptuel — le projet demande la simplicité avant la habileté (« cleverness »).
**Impact sur les livrables** — aucun sur la conception ; à noter pour toute story future qui présumerait que ces trois symboles vivent encore dans `noyau`.
**Reporté au livrable** — non, à faire au prochain relevé du mémoire.

## D-08 — L'intergiciel de changement de mot de passe vit dans `administration`, pas `noyau`
**Date** 2026-09-02 · **Story** US-ADM-02 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — Le prompt place l'intergiciel dans `app/noyau/middleware.py` et veut qu'il consulte « une méthode du service » (§ 2.2 : « il redirige, il ne décide pas »). Mais la règle (`ServiceCompte.doit_changer_mot_de_passe`) vit dans `administration`, et `noyau` ne doit dépendre d'aucune application — invariant testé par `tests/architecture/test_couches.py::test_ordre_des_dependances_entre_applications`.
**Décision** — L'intergiciel vit dans `app/administration/middleware.py`, pas `noyau`. Il appelle réellement `ServiceCompte.doit_changer_mot_de_passe`, respectant la lettre du § 2.2 sur ce point.
**Alternative écartée** — Garder l'intergiciel dans `noyau` et lire `request.user.doit_changer_mot_de_passe` (l'attribut brut) plutôt que la méthode du service : respecte le chemin de fichier du prompt, mais contourne exactement ce que le § 2.2 demande d'éviter — que la règle soit autre chose qu'« une méthode du service ». Écartée sur arbitrage explicite.
**Impact sur les livrables** — aucun sur la conception ; `MIDDLEWARE` dans `config/settings/base.py` référence `administration.middleware...` et non `noyau.middleware...`.
**Reporté au livrable** — non, à faire au prochain relevé du mémoire.

## D-07 — Deux règles de garde-fou, absentes de tout livrable — à porter au cahier des charges
**Date** 2026-09-02 · **Story** US-ADM-02 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — Rien dans les livrables n'empêche un administrateur de désactiver son propre compte, ou de désactiver (ou changer de profil) le dernier compte administrateur actif du système. Le résultat serait un système dont plus personne ne peut créer ni gérer de compte — irrécupérable sans intervention directe en base.
**Décision** — Deux contrôles posés dans `ServiceCompte` (`_interdire_autodesactivation`, `_interdire_perte_du_dernier_administrateur`) :
1. Un administrateur ne peut pas désactiver son propre compte.
2. Le dernier compte administrateur actif ne peut être ni désactivé, ni voir son profil changé vers autre chose qu'administrateur.

**À porter au cahier des charges comme règles métier nouvelles, avec leur code RG**, à l'initiative du binôme — ce n'est pas à moi de leur attribuer un numéro RG.
**Alternative écartée** — Ne rien contrôler et compter sur la vigilance humaine : le prompt de la story juge le risque trop élevé (« irrécupérable sans intervention en base »).
**Impact sur les livrables** — deux règles métier à ajouter au référentiel `RG-*`, avec renvoi vers `docs/conception/13-diagramme-classes.md` si elles affectent le diagramme d'états du compte.
**Reporté au livrable** — **non**, action attendue du binôme, pas automatique.

## D-06 — Le sens de `auteur` dépend du `type_action`
**Date** 2026-09-02 · **Story** US-ADM-02 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — RG-26 exige que la création et la modification d'un compte soient journalisées « avec auteur ». Contrairement à un échec d'authentification (D-03 : un seul compte en jeu, celui visé), une action de gestion de compte met en jeu **deux comptes distincts** — l'administrateur agissant et le compte créé/modifié/désactivé. `EntreeJournal.auteur` ne peut porter que l'un des deux.
**Décision** — Pour `creation_compte`, `modification_compte`, `changement_profil`, `desactivation_compte`, `reactivation_compte` : `auteur` porte **l'administrateur agissant**. Le compte visé va dans `cible` (son identifiant). Pour `echec_authentification` (US-ADM-01) : `auteur` reste **le compte visé** — il n'y a pas d'acteur authentifié, c'est le seul candidat sensé.
**Alternative écartée** — Garder `auteur` uniformément « le compte concerné », comme US-ADM-01 : aurait rendu RG-26 « avec auteur » incapable de désigner qui a agi pour cette story, alors que c'est précisément l'information que la règle demande de tracer.
**Impact sur les livrables** — le sens de `auteur` dépend donc du `type_action` — documenté dans la docstring d'`EntreeJournal`. À garder en tête pour l'écran de consultation (US-ADM-04) : une même colonne ne signifie pas la même chose sur toutes les lignes.
**Reporté au livrable** — non, à faire au prochain relevé du mémoire.

## D-05 — Page d'accueil technique, placeholder du redirecteur post-connexion
**Date** 2026-09-02 · **Story** US-ADM-01 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — Critère 1 de CU-P1-01 : « accède à la page d'accueil correspondant à son profil ». Aucun écran métier n'existe encore (hors périmètre explicite de la story), donc `LOGIN_REDIRECT_URL` n'a nulle part où pointer, et rien ne permet de vérifier que le contenu diffère par profil.
**Décision** — `noyau/accueil.html` + une vue minimale (`noyau/views.py::accueil`), affichant seulement `Bienvenue, {{ user.grade }} {{ user.last_name }}` et `Profil : {{ user.get_profil_display }}`. Aucune rubrique de navigation, aucune logique métier — juste assez pour que la connexion mène quelque part et que le critère 1 soit vérifiable.
**Alternative écartée** — Rediriger vers `/admin/` : aurait évité de créer un gabarit, mais n'aurait rien démontré sur le profil de l'utilisateur, et aurait exposé l'admin Django comme page d'atterrissage par défaut de tous les profils, y compris ceux qui ne devraient pas y accéder.
**Impact sur les livrables** — aucun sur la conception ; à remplacer par le vrai tableau de bord dès qu'une story en construit un.
**Reporté au livrable** — non applicable.

## D-04 — `EntreeJournal.cible` et index différés à US-ADM-04
**Date** 2026-09-02 · **Story** US-ADM-01 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — Le prompt US-ADM-01 liste `cible` parmi les champs minimaux d'`EntreeJournal` sans la définir ; ni RG-26 ni CU-P1-01 ne la mentionnent. Par ailleurs, `.claude/rules/migrations.md` anticipait des index (`idx_journal_horodatage`, `idx_journal_objet`) sur des colonnes (`horodatage`, `objet_type`, `objet_identifiant`) qui ne correspondent pas aux champs réellement posés (`cree_le`, `type_action`, `cible`).
**Décision** — `cible` peuplée avec la valeur littérale `"authentification"` pour cette story (la ressource visée, distincte de `auteur`, l'acteur) — générique pour que de futures actions sensibles s'y insèrent sans changer le sens du champ. Les deux index ne sont pas posés ici : rien dans US-ADM-01 n'interroge le journal, et les vrais motifs de filtre ne seront connus qu'à la construction de l'écran de consultation.
**Alternative écartée** — Poser les index tout de suite sur des noms de colonnes devinés : aurait figé un choix sans le vérifier contre l'usage réel.
**Impact sur les livrables** — `.claude/rules/migrations.md` reste à jour avec des noms de colonnes qui ne correspondent plus au modèle réel ; à corriger au moment d'US-ADM-04.
**Reporté au livrable** — non, à faire au prochain relevé du mémoire.

## D-03 — `EntreeJournal.auteur` distinct de `cree_par`/`modifie_par`
**Date** 2026-09-02 · **Story** US-ADM-01 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — `ModeleHorodate` (socle) porte `cree_par`/`modifie_par` pour toute entité — qui a créé/modifié la ligne. RG-26 exige que le journal porte son propre « auteur » : le compte concerné par l'action journalisée, nullable si l'identifiant saisi ne correspond à aucun compte.
**Décision** — Les deux mécanismes cohabitent avec des rôles distincts. `cree_par`/`modifie_par` restent `None` sur toute entrée de journal : aucun utilisateur authentifié ne « crée » techniquement une entrée générée par le système lors d'une tentative de connexion. `auteur` porte le sens métier — le compte visé, pas l'auteur technique de l'écriture.
**Alternative écartée** — Réutiliser `cree_par` comme porteur du compte concerné : aurait fait porter deux sens différents (auteur technique de la ligne / sujet métier de l'action) au même champ, source de confusion dès qu'un vrai utilisateur authentifié écrira un jour dans le journal pour une autre action sensible.
**Impact sur les livrables** — aucun sur la conception ; précise l'usage de `ModeleHorodate` pour toute future entité de type journal.
**Reporté au livrable** — non, à faire au prochain relevé du mémoire.

## D-02 — Révocation RG-27 différée à US-ADM-04
**Date** 2026-09-02 · **Story** Socle technique (PROMPT_00) · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — RG-27 (immuabilité du journal) porte sur `administration_entree_journal`, qui n'existe pas encore : elle est hors périmètre du socle, `entree_journal` vient avec US-ADM-04.
**Décision** — Aucune révocation de privilège n'est posée dans `infra/postgres/init/01_roles.sql`. La révocation UPDATE/DELETE sur `administration_entree_journal` sera portée par une migration SQL explicite et réversible dans US-ADM-04, accompagnée d'un test ouvrant une connexion dédiée avec le rôle `pfe_cit_app` pour vérifier le refus.
**Alternative écartée** — Poser la révocation par anticipation : impossible techniquement (`REVOKE` sur une table absente échoue), et aurait dispersé une règle de sécurité loin de la migration qui crée la table qu'elle protège.
**Impact sur les livrables** — aucun sur la conception ; c'est la seule ligne du schéma où la sécurité repose sur les privilèges et non sur une contrainte déclarative — dette identifiée et datée, à traiter dès US-ADM-04, pas un oubli.
**Reporté au livrable** — non applicable, dette de développement, pas un écart de conception.

## D-01 — Deux rôles de connexion PostgreSQL (migration / application)
**Date** 2026-09-02 · **Story** Socle technique (PROMPT_00) · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — RG-27 exige la révocation d'UPDATE/DELETE sur `administration_entree_journal` pour le rôle applicatif ; poser l'extension `btree_gist` (RG-24) exige un rôle capable de `CREATE EXTENSION`. Un rôle de connexion unique aurait fini par cumuler ces deux besoins contradictoires.
**Décision** — Deux rôles PostgreSQL distincts dès le développement : `pfe_cit_migration` (propriétaire de la base, exécute les migrations, `CREATEDB` pour que pytest-django puisse créer/détruire la base de test) et `pfe_cit_app` (rôle applicatif restreint, aucun privilège de création, lecture/écriture accordée par `ALTER DEFAULT PRIVILEGES`). Vérifié empiriquement sur un conteneur PostgreSQL 16 : `btree_gist` étant une extension « trusted » depuis PostgreSQL 13, être propriétaire de la base suffit à `pfe_cit_migration` pour l'installer — aucun superutilisateur nécessaire, ce qui évite d'avoir à en demander un sur le poste du CIT.
**Alternative écartée** — Un rôle unique superutilisateur : plus simple à démarrer, mais rend la révocation RG-27 sans objet (un superutilisateur contourne toute révocation de privilège) et exigerait une élévation de droits sur le poste cible, potentiellement refusée en environnement militaire.
**Impact sur les livrables** — note d'implémentation §5.4 (immuabilité du journal) à compléter : elle mentionne la révocation mais pas le partage en deux rôles qui la rend possible sans bloquer les migrations. `infra/postgres/init/01_roles.sql` matérialise la décision ; `config/settings/local.py` pointe `pfe_cit_app` par défaut, `config/settings/test.py` pointe `pfe_cit_migration`.
**Reporté au livrable** — non, à faire au prochain relevé du mémoire.
