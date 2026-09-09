# Prompt 20 — US-SES-01 · Ouvrir une session de formation

Sprint 2, story 1 sur 12. Must, 5 points. Lot WBS 5.2.2.

## 0. Étape 0 — vérifications avant toute ligne de code

Ce prompt énonce des hypothèses. Le code réel fait foi. Avant d'écrire quoi que
ce soit, vérifie les cinq points suivants et consigne tout écart dans
`docs/suivi/DECISIONS.md` AVANT de coder — précédent D-47, où deux hypothèses
d'un prompt étaient fausses et auraient fait échouer les tests d'architecture.

1. `tests/architecture/test_couches.py::DOMAINES_CATALOGUE` contient-il bien un
   domaine pour le paquetage P3 ? Ce prompt suppose le code `organisation`
   (dérivé du libellé « P3 — Organisation » de la matrice § 11.2, même méthode
   que D-11). Si le catalogue en porte un autre, c'est le catalogue qui fait foi.
2. `DEPENDANCES_AUTORISEES` autorise-t-il `organisation` → `referentiel` et
   `organisation` → `administration` ? Sinon, ajoute-les : c'est l'ordre de
   dépendance des paquetages arrêté en phase 4, pas une entorse.
3. L'application `organisation` existe-t-elle déjà (squelette du sprint 1, sept
   applications) et figure-t-elle à `INSTALLED_APPS` ? Ne fais pas de `startapp`
   si elle est là.
4. Relis la signature réelle de `noyau/services/gestion.py` : attributs de
   classe attendus, signatures de `lister`, `creer`, `modifier`, `supprimer`,
   `_valider`, `_erreur_unicite`, `_queryset`, `CHAMPS_FILTRABLES`. Code d'après
   ce fichier, jamais d'après ce prompt.
5. Le patron dispose-t-il d'un mécanisme d'avertissement non bloquant ? Réponds
   explicitement oui ou non avant d'attaquer le § 5.

Prends aussi connaissance de l'application `ressources` (US-INS-01, US-PLAN-02) :
c'est l'exemple complet le plus récent du patron, et l'organisation de fichiers
d'`organisation` doit la reproduire.

## 1. Ce que porte cette story

Besoin BF-SES-01. Cas d'utilisation CU-P3-01. Règle RG-11. Classe Session
(CLS-00, paquetage P3). Acteur en écriture : cellule pédagogique.

Critères d'acceptation du backlog v8 :

1. Une session est rattachée à une formation et porte une date de début, une
   date de fin et un effectif attendu.
2. Le référentiel de la formation est repris automatiquement par la session.
3. Plusieurs sessions d'une même formation peuvent coexister sur des périodes
   différentes.
4. Une session ne peut être ouverte sur une formation archivée.
5. Les formations ouvertes sur ordre sont créées de la même façon, sans
   périodicité imposée.

Exceptions de la fiche CU-P3-01, toutes à implanter :

- E1 — date de fin antérieure ou égale à la date de début : refus.
- E2 — volume horaire total prescrit excédant les heures ouvrables de la
  période : AVERTISSEMENT, jamais refus. C'est RG-65.
- E3 — effectif attendu nul ou négatif : refus.
- E4 — référentiel de la formation vide : refus d'ouverture.

Enchaînement A1 : deux sessions d'une même formation PEUVENT se chevaucher dans
le temps. Le système ne s'y oppose pas ; le partage des instructeurs et des lieux
s'arbitre à la planification. Le critère 3 du backlog, moins précis, ne doit pas
être lu comme une interdiction de chevauchement — arbitrage identique à D-26,
à consigner dans `DECISIONS.md`.

Enchaînement A2 (modification des dates après ouverture, signalement des séances
hors de la nouvelle période) : HORS PÉRIMÈTRE, `Seance` n'existe pas. Voir § 10.

## 2. Le modèle

`app/organisation/models.py`, `Meta.db_table = "organisation_session"`.

`Session`, d'après CLS-00 :

- `formation` — clé étrangère vers `referentiel.Formation`, `on_delete=PROTECT`,
  `related_name="sessions"`. Le PROTECT n'est pas décoratif : c'est lui qui
  referme le critère 4 d'US-REF-01, reporté par D-23.
- `intitule` — texte court, obligatoire.
- `date_debut`, `date_fin` — date.
- `effectif_attendu` — entier, strictement positif.
- `etat` — `EtatSession` (TextChoices : `OUVERTE`, `CLOTUREE`), valeur initiale
  `OUVERTE`, JAMAIS modifiable par le formulaire de cette story. La clôture est
  US-SES-09, Should, sprint 4.
- `date_cloture` — date, facultative, nulle ici.

Hérite de la classe de base d'horodatage et de rattachement à l'auteur
(BNF-14, RG-26), comme les sept entités du patron.

N'hérite PAS du mixin d'archivage : `Session` porte un état métier, pas un
indicateur d'archivage — même raisonnement que D-37 et D-49, à consigner.

INTERDIT, et c'est le point central de cette story : aucun champ, aucune table,
aucune méthode ne recopie le référentiel de la formation dans la session. Pas de
`SessionMatiere`, pas de `volume_horaire_total` dénormalisé, pas de photographie
à l'ouverture. Le critère 2 est satisfait par construction — et seulement par
construction — si la session lit le référentiel de sa formation par la relation.
Une copie invaliderait le critère 6 d'US-REF-02 (« toute modification d'une
matière est répercutée ») trois sprints plus tard, silencieusement. C'est D-29,
transposé.

## 3. Contraintes : ce qui descend en base, ce qui reste en services

En base, migration `0001_initial`, noms conformes à la note d'implémentation § 2.1 :

- `ck_session_dates` — `date_fin > date_debut`. E1, volet base.
- `ck_session_effectif` — `effectif_attendu > 0`. E3, volet base.
- `ck_session_etat` — restriction aux valeurs de l'énumération (note
  d'implémentation § 2.3 : varchar + contrainte de vérification).
- `uq_session_formation_intitule` — unicité composite sur
  `(formation_id, UPPER(intitule))`, insensible à la casse.

  Cette dernière est une PROPOSITION, pas un acquis. Elle n'est portée par aucun
  livrable ; je la propose par analogie avec `uq_formation_type_intitule`
  (D-26) : elle interdit la double saisie exacte sans interdire le chevauchement
  d'A1, deux sessions distinctes de la même formation portant nécessairement des
  intitulés distincts. Consigne-la comme décision explicite avec cette
  justification, et signale-la comme arbitrable par le chef de projet.

AUCUNE contrainte de non-chevauchement de périodes. Ni en base, ni en services.
C'est A1, et un test doit le prouver (§ 11).

En couche services, parce que SQL ne sait pas les dire :

- Critère 4 — formation archivée : conditionnel à l'état d'une ligne liée.
- E4 — référentiel vide : porte sur un agrégat de lignes filles.
- E2 — avertissement de volume : porte sur un agrégat et un paramètre.

## 4. Le service

`app/organisation/services/session.py`, `ServiceSession(ServiceGestion)`.

Attributs de classe : `MODELE`, `DOMAINE` (§ 0.1), `CHAMP_UNICITE = "intitule"`,
`CHAMPS_FILTRABLES = ("formation", "etat")`. Les dépendances vers
`administration` s'injectent par attributs de classe et ne s'importent jamais
dans `noyau` — D-19.

`_queryset()` surchargée : `select_related("formation", "formation__type_formation")`.
La liste affiche le type de formation ; sans cela, une requête par ligne.

Surcharges propres :

- Validation à la création : formation archivée → refus, message désignant
  l'action corrective (BNF-10 : « La formation X est archivée ; désarchivez-la
  ou choisissez une autre formation » — pas « formation invalide »).
- Validation à la création : référentiel vide → refus, message renvoyant vers la
  composition du référentiel de cette formation.
- `referentiel_resume(agissant, session)` — renvoie le nombre de matières et le
  volume horaire total prescrit du référentiel de `session.formation`, pour
  l'étape 2 du scénario nominal et pour la fiche. Délègue à
  `ServiceReferentiel` ; n'interroge pas les modèles de `referentiel` en direct
  et ne recopie rien.
- `_erreur_unicite` surchargée si l'unicité composite du § 3 est retenue, pour
  désigner le doublon dans la bonne formation — le patron ne connaît qu'une
  unicité à un seul champ.

`etat` et `date_cloture` ne sont modifiables par aucune méthode de ce service.

## 5. L'avertissement E2 — mécanisme générique, pas un cas particulier

RG-65 est transverse : « écart entre attribut déclaratif et valeur calculée :
avertissement, jamais refus ». Elle sert ici (E2), au critère 4 d'US-SES-02
(écart d'effectif, RG-15), puis à US-SES-06 et US-PLAN-07.

Si le patron n'a pas de mécanisme d'avertissement (§ 0.5), ajoute-le dans
`noyau/services/gestion.py`, pas dans `organisation` : une structure
d'avertissement (code, message) que `creer` et `modifier` retournent à côté de
l'objet, sans jamais empêcher l'enregistrement. Teste-le sur
`essai_patron_gestion`, pas seulement à travers `Session` — un patron testé à
travers un seul usage n'est pas un patron. Consigne l'extension comme D-27 et
D-32.

Le calcul de E2 réemploie l'existant, il n'invente pas de paramètre :
`VOLUME_HORAIRE_HEBDOMADAIRE_REFERENCE` et
`SEUIL_ECART_VOLUME_REFERENTIEL_POURCENT` (D-33, `config/settings/base.py`), et
`ServiceReferentiel.ecart()` si sa signature s'y prête. Volume attendu = nombre
de semaines de la période × volume hebdomadaire de référence ; avertissement si
la somme des volumes prescrits le dépasse au-delà du seuil.

Consigne dans `DECISIONS.md` que ce calcul est provisoire par construction : la
vraie réponse est la grille horaire active (US-PLAN-12, ce sprint) et le
calendrier (US-PLAN-01, ce sprint). Note que le remplacement est à faire dès que
ces deux stories sont livrées, et que la valeur de 30 h/semaine reste une
question de terrain ouverte.

## 6. Vues, adresses, navigation

Structure de `ressources` reproduite : `views/session.py`, `urls.py`, aucune vue
n'importe un modèle (`test_aucune_vue_n_importe_un_modele`).

Cinq adresses : liste, fiche, création, modification, suppression.

Rubrique de navigation « Sessions », visible si l'utilisateur détient la
permission de lecture du domaine, conformément à la barre de la maquette de
référence MAQ-01 (Référentiel | Sessions | Ressources | Planification |
Évaluations | Suivi). Un seul écran de premier niveau : pas d'onglets, le
mécanisme de D-57/D-58 ne s'applique qu'à partir de deux.

La leçon de P-26 s'applique : un écran neuf doit être ATTEIGNABLE depuis la
navigation, et cela se teste — des permissions exactes sur un écran que rien ne
mène nulle part restent invisibles.

## 7. Écrans

Liste : intitulé, formation, type de formation, période, effectif attendu, état.
Filtre par formation et par état (`CHAMPS_FILTRABLES`), recherche sur l'intitulé,
pagination dès vingt éléments (BNF-15), fenêtre de pagination partagée (P-32).
La colonne Actions porte `data-impression="masquer"` par le gabarit générique
(D-63) ; aucune colonne de donnée n'est masquée à l'impression.

Formulaire : gabarit générique du patron avec le contexte `groupes` (D-46), deux
colonnes — « Rattachement » (formation) et « Période et effectif » (dates,
effectif attendu, intitulé). `etat` et `date_cloture` absents du formulaire.

Le sélecteur de formation exclut les formations archivées et celles au
référentiel vide. C'est un confort d'interface, PAS le contrôle : le service
refuse indépendamment, et les tests le vérifient en court-circuitant le
formulaire. Une règle qui ne vit que dans un formulaire est contournée dès qu'une
donnée entre par un autre chemin.

Fiche session : identité, formation et son type, période, effectif attendu,
état. Un bloc « Référentiel appliqué » affichant le nombre de matières et le
volume horaire total prescrit, avec un lien vers le référentiel de la formation
— c'est l'étape 2 du scénario nominal, et la matérialisation visible du critère 2.
Un emplacement « Brigades » vide et commenté, réservé à US-SES-02 : son
remplissage doit être un ajout de contenu, pas une refonte d'écran (même méthode
que D-30 — mais souviens-toi de P-25 : un emplacement réservé qu'on oublie de
remplir reste ouvert quatre jours sans que personne le voie).

L'avertissement E2 s'affiche à l'écran après l'enregistrement, avec les deux
volumes en regard (prescrit, attendu sur la période). Charte § 3.30.

## 8. Habilitations

Matrice § 11.2, ligne « P3 — Organisation » : pédagogique en écriture ;
planification, examens et Direction de Formation en lecture ; administrateur
AUCUN accès, ni lecture ni écriture.

La matrice fait foi et ne s'anticipe pas. Si elle te paraît discutable — un
administrateur privé de toute lecture sur l'organisation, par exemple —
consigne la remontée dans `DECISIONS.md` sans la corriger, et écris le test qui
constate l'état actuel avec un commentaire disant qu'il doit tomber si
l'arbitrage change. C'est exactement le traitement de D-45.

## 9. Journalisation

Création, modification et suppression journalisées par le patron
(`ServiceJournal`, natures génériques D-18, suppression D-38). Rien de
spécifique à écrire si le patron est correctement câblé — vérifie-le plutôt que
de le supposer.

## 10. Ce que cette story referme, ce qu'elle reporte

REFERME — D-23, critère 4 d'US-REF-01 : « une formation disposant de sessions
ouvertes ne peut être supprimée ». Le `PROTECT` du § 2 y suffit, sans une ligne
de code dans `referentiel`. La preuve est un test, pas une déclaration : voir
§ 11, groupe D. Souviens-toi que D-50 a déclaré un report refermé sans qu'il le
soit, et qu'il a fallu quatre jours et un lot de clôture pour s'en apercevoir.

À SIGNALER en refermant D-23 : `PROTECT` bloque la suppression d'une formation
portant N'IMPORTE QUELLE session, y compris clôturée, alors que le critère ne
parle que des sessions ouvertes. Je considère que c'est le bon comportement — la
session close porte l'historique de la formation — mais c'est un écart entre le
libellé du critère et le mécanisme réel : consigne-le, ne le passe pas sous
silence.

REPORTE — enchaînement A2 de CU-P3-01 : à la modification des dates, le système
doit signaler les séances déjà programmées hors de la nouvelle période et exiger
un arbitrage. `Seance` appartient à US-PLAN-03, même sprint, plus tard. Aucun
code spécifique ici. Consigne le report dans `DECISIONS.md` en le rattachant
nommément à US-PLAN-03, sur le modèle de D-23/D-30/D-45. C'est un report
nouveau : il porte le compte à dix, à annoncer à la revue du 26 septembre.

## 11. Tests attendus

Groupe A — couche services (`app/organisation/tests/test_session.py`)

A1. Création nominale : session à l'état OUVERTE, rattachée à la formation,
    journalisée avec son auteur.
A2. E1, deux cas : date de fin antérieure, puis ÉGALE à la date de début — refus.
A3. E3, deux cas : effectif nul, puis négatif — refus.
A4. Critère 4 : formation archivée — refus, message désignant l'action corrective.
A5. E4 : formation au référentiel vide — refus.
A6. Critère 3 : deux sessions de la même formation sur des périodes disjointes —
    les deux acceptées.
A7. A1 de la fiche : deux sessions de la même formation dont les périodes SE
    CHEVAUCHENT — les deux acceptées. Ce test prouve l'absence de contrainte ;
    nomme-le pour que son intention survive à sa lecture dans six mois.
A8. Critère 5 : deux sessions ouvertes à des dates arbitraires, sans rythme
    régulier — acceptées. Prouve qu'aucune périodicité n'est imposée.
A9. Critère 2, le test qui compte : créer une session, modifier le volume
    prescrit d'un élément du référentiel de sa formation, vérifier que le
    résumé du référentiel DE LA SESSION reflète la nouvelle valeur. Si ce test
    passe, aucune copie n'a été faite.
A10. E2 : session dont le volume prescrit excède largement les heures ouvrables
    estimées — la session EST créée, ET un avertissement est retourné. Les deux
    assertions dans le même test.
A11. Unicité composite, si retenue : doublon d'intitulé dans la même formation
    refusé, casse indifférente ; même intitulé dans une autre formation accepté.

Groupe B — contraintes réellement en base

Chaque contrainte du § 3 est vérifiée par une insertion qui court-circuite le
service et attend une `IntegrityError`. Une contrainte déclarée dans un
`Meta.constraints` mais absente de la migration passerait tous les tests du
groupe A sans exister en base.

Groupe C — cycle HTTP réel (`reverse()` + `client`), règle inscrite en
définition de fini au sprint 1

C1. Chemin nominal, profil pédagogique : GET liste, GET fiche, GET formulaire de
    création, POST création (302 + objet réellement créé en base), POST
    modification, POST suppression.
C2. Refus d'habilitation, par le cycle HTTP, pour CHACUNE des trois adresses
    d'écriture : planification, examens, Direction de Formation, administrateur.
C3. Lecture accordée : pédagogique, planification, examens, Direction de
    Formation. Refusée : administrateur.
C4. Le test de garde mécanique du sprint 1 (toute adresse d'écriture figure à la
    table des refus) doit passer sans modification. S'il échoue, c'est une
    adresse oubliée à la table, pas le test qu'il faut ajuster.
C5. Navigation : la rubrique Sessions est présente dans le menu pour un profil
    habilité, absente sinon.
C6. L'avertissement E2 est VISIBLE dans la réponse HTTP, pas seulement retourné
    par le service. Leçon de P-25 : un service testé ne prouve jamais que
    l'écran affiche ce qu'il produit.
C7. Le bloc « Référentiel appliqué » de la fiche affiche le nombre de matières
    et le volume réels de la formation, vérifiés sur des données de test non
    triviales.

Groupe D — fermeture de D-23

D1. Une formation portant une session ouverte ne peut être supprimée : la
    suppression est refusée ET les sessions opposantes sont énumérées dans le
    message.
D2. Le même refus par le VRAI CYCLE HTTP, depuis l'écran de suppression d'une
    formation (`referentiel/tests/test_formation.py`). C'est la leçon de P-30 :
    un service générique bien testé ne garantit pas que l'écran y mène.
D3. Une formation portant une session CLÔTURÉE est également protégée —
    documente l'écart du § 10 par un test qui le rend visible.

Groupe E — architecture

La suite `tests/architecture` passe en entier : dépendances entre applications,
domaine déclaré par toute classe de service, aucune vue n'important un modèle,
aucune classe de plus de 200 lignes.

## 12. Définition de fini

Implanté, testé, relu par le sous-agent, commité. Suite `pytest` complète verte
— pas seulement les tests de cette story. Écran vérifié réellement dans un
navigateur, pas seulement par `assertContains`. `docs/suivi/DECISIONS.md` à jour
le jour même (R19). Case d'US-SES-01 cochée dans `docs/suivi/sprint-2.md`.

## 13. Ce que tu ne touches pas

Le backlog produit, le cahier des charges, le registre des risques et le
diagramme de classes de référence : `.claude/rules` les réserve au chef de
projet. Si tu constates qu'un livrable doit changer, écris-le dans
`DECISIONS.md`, ligne « Impact sur les livrables », et n'y touche pas.

Les stories US-SES-02 et suivantes. Un emplacement réservé sur la fiche, oui ;
du code par anticipation d'un modèle non conçu, non — c'est le raisonnement
constant de D-23, D-30, D-35 et D-45.

## 14. Ce que tu me rends

- La liste des écarts trouvés à l'étape 0, avant tout code.
- Les entrées `DECISIONS.md` rédigées : arbitrage critère 3 / A1, unicité
  composite proposée, non-héritage du mixin d'archivage, écart PROTECT / « sessions
  ouvertes », report d'A2, extension du patron pour les avertissements, caractère
  provisoire du calcul E2.
- Le compte des tests ajoutés, ventilé par groupe, et le total de la suite.
- Le temps que la story t'a réellement pris, à la demi-heure près : le jalon C2
  exige le relevé des heures réelles, absent du sprint 1, et la clé de 1,3 heure
  par point reste invérifiée pour les 169 points restants.