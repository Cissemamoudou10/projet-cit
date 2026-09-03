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
