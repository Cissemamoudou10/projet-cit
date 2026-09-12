# Prompt 24 — US-SES-05 · Enregistrer les stagiaires d'une session

Sprint 2, story 5 sur 12. Must, 5 points. Lot WBS 5.2.6.

## 0. Étape 0 — vérifications avant toute ligne de code

1. DÉPENDANCES. `openpyxl` est-il présent dans les dépendances du projet ? Dans
   le paquet hors ligne constitué par `scripts/constituer-paquet.sh` ? Lis
   `docs/suivi/INSTALLATION-HORS-LIGNE.md` et
   `tests/architecture/test_dependances.py`, qui liste les dépendances
   autorisées. Réponds avant de coder : ajouter une dépendance touche le
   protocole d'installation hors ligne, et R9 vient d'être éteint (test réussi
   le 7 septembre sur VM Debian 12 isolée). Voir § 3.
2. Le mécanisme d'avertissement du patron, quatrième utilisation.
3. Comment `ServiceGestion` et les fonctions libres de `noyau/services/gestion.py`
   se comportent sur une opération de MASSE : le patron est écrit pour une
   instance à la fois. Dis-moi ce qui manque avant de l'étendre.
4. Existe-t-il déjà, quelque part dans le projet, une lecture de fichier déposé
   par l'utilisateur ? Si oui, suis ce précédent. Sinon, c'est la première, et
   les choix faits ici serviront de référence.
5. `Brigade` et `Session` tels que livrés : noms exacts, services, adresses.
6. Suite `pytest` verte avant de commencer.

## 1. Ce que porte cette story

Besoin BF-SES-05. Cas d'utilisation CU-P3-05, fiche détaillée. Règles RG-17 et
RG-18. Classe `Stagiaire` (CLS-00, paquetage P3). Acteur en écriture : cellule
pédagogique.

Critères d'acceptation du backlog v8 :

1. Un stagiaire comporte une identité, un matricule et une unité d'origine, et
   est rattaché à une session.
2. L'enregistrement peut se faire manuellement, stagiaire par stagiaire.
3. Un fichier tabulaire au format CSV ou Excel peut être importé pour créer
   l'ensemble des stagiaires d'une session.
4. Le format attendu des colonnes est documenté et un modèle de fichier est
   téléchargeable.
5. Les lignes comportant une erreur sont signalées avec leur numéro et le motif ;
   aucun import partiel n'est effectué tant que les erreurs subsistent.
6. Le matricule est unique au sein d'une session ; les doublons sont détectés à
   l'import.

Plus l'enchaînement A4 de la fiche — la RADIATION d'un stagiaire — absent des
critères du backlog. Voir § 7.

HORS PÉRIMÈTRE : l'affectation aux brigades (US-SES-06), la liste consultable et
son export (US-SES-07). Un stagiaire enregistré ici est en attente d'affectation,
c'est la postcondition de la fiche.

## 2. Le modèle

`app/organisation/models.py`, `Meta.db_table = "organisation_stagiaire"`.

`Stagiaire`, d'après CLS-00 :

- `session` — clé étrangère vers `Session`, `on_delete=PROTECT`,
  `related_name="stagiaires"`.
- `matricule` — texte court, obligatoire.
- `nom`, `prenom`, `grade` — texte court, obligatoires (CLS-00 ne les marque pas
  facultatifs).
- `unite` — texte court, obligatoire. C'est l'unité d'origine du critère 1.
- `radie` — booléen, faux par défaut.
- `motif_radiation` — texte, facultatif.
- `date_radiation` — date, facultative.

Hérite de la classe de base d'horodatage et de rattachement à l'auteur.

En base :

- `uq_stagiaire_session_matricule` — unicité composite sur
  `(session_id, UPPER(matricule))`. C'est RG-17, et la note d'implémentation
  § 5.5 la prescrit explicitement en base. Insensible à la casse, cohérent avec
  D-21, D-26 et l'unicité de désignation de brigade posée à US-SES-02.
- `ck_stagiaire_radiation` — cohérence du triplet de radiation : si `radie` est
  vrai, `motif_radiation` et `date_radiation` sont renseignés ; s'il est faux,
  les deux sont vides. Un stagiaire radié sans motif ni date rend la radiation
  inexploitable, et un motif sans radiation est un état qui ne veut rien dire.
  Même figure que `ck_evaluation_perimetre` de la note d'implémentation.

CONSÉQUENCE DE MODÈLE À CONSIGNER EXPLICITEMENT. RG-17 n'impose l'unicité qu'au
sein d'une session : un même militaire suivant deux formations existe deux fois
dans la base, sans lien entre ses deux enregistrements. C'est cohérent avec
CLS-00, où `Stagiaire` est rattaché à une session et non un annuaire du centre.
Écris-le dans `DECISIONS.md` avec ses deux conséquences : aucun historique de
formation par personne n'est constituable en l'état, et une correction d'identité
ne se propage pas d'une session à l'autre. Question de terrain à poser : le CIT
a-t-il besoin de suivre le parcours d'un stagiaire à travers plusieurs
formations ? Si oui, c'est une entité « personne » et une story qui n'existent
pas au backlog. Ne tranche pas, signale.

## 3. La dépendance Excel et le paquet hors ligne

Le critère 3 nomme CSV ET Excel. Implante les deux — le terrain transmettra des
`.xlsx`, c'est certain, et ne supporter que CSV laisserait un critère à moitié
tenu, donc un report de plus.

`openpyxl` est une roue pure Python, sans dépendance native : le risque pour
l'installation hors ligne est faible, contrairement à ce qu'avait fait craindre
WeasyPrint jusqu'à D-60. Faible n'est pas nul, et surtout, R9 n'est éteint que
parce qu'un protocole a été rejoué réellement.

Dans CETTE story, pas plus tard :

- ajoute `openpyxl` aux dépendances et à `tests/architecture/test_dependances.py` ;
- reconstitue le paquet hors ligne avec `scripts/constituer-paquet.sh` et vérifie
  que la roue y figure réellement ;
- mets à jour `docs/suivi/INSTALLATION-HORS-LIGNE.md` : nouvelle dépendance,
  date, motif ;
- dis-moi si le rejeu complet du protocole sur VM te paraît nécessaire ou si le
  raisonnement de D-62 s'applique — aucune logique native touchée, à confirmer à
  la prochaine installation réelle. Argumente, ne tranche pas seul.

N'utilise PAS pandas. La bibliothèque est lourde, tire numpy, et lire soixante
lignes tabulaires ne la justifie pas. Le module `csv` de la bibliothèque standard
et `openpyxl` suffisent.

## 4. L'import en deux temps — le cœur de la story

Le scénario nominal impose une analyse SANS AUCUN ENREGISTREMENT, suivie d'une
confirmation. La fiche explique pourquoi : un import direct de soixante
stagiaires échouant à la quarantième ligne laisserait une session à moitié
pourvue, sans moyen simple de revenir en arrière.

TEMPS 1 — analyse. Le fichier est lu, chaque ligne validée, et un compte rendu
présenté : lignes valides comptées, lignes en anomalie avec leur NUMÉRO DE LIGNE
DANS LE FICHIER et la nature de l'anomalie, doublons détectés. Rien n'est écrit
en base, pas même un brouillon.

TEMPS 2 — confirmation. Les lignes valides sont enregistrées, en une seule
transaction (RG-18 : tout ou rien), et l'opération est journalisée.

RÈGLE ABSOLUE, à ne contourner sous aucun prétexte : LE COMPTE RENDU EST UN
APERÇU, JAMAIS UNE SOURCE DE VÉRITÉ. La confirmation revalide intégralement,
dans la transaction. Sans cela, deux agents important deux fichiers en parallèle
sur la même session créent des doublons que l'analyse de chacun avait déclarés
valides — variante exacte de la modification concurrente examinée en P-31, et la
contrainte d'unicité en base est la seule garantie qui tienne.

Décide où vit l'état entre les deux requêtes et JUSTIFIE-LE dans `DECISIONS.md`.
Trois voies possibles, toutes défendables : session Django côté serveur, fichier
temporaire avec jeton, ou nouveau dépôt du fichier à la confirmation. Contraintes
à respecter quelle que soit la voie retenue : aucune entité nouvelle en base pour
un état transitoire, aucune donnée nominative écrite sur disque sans nettoyage,
et un comportement défini si la confirmation n'arrive jamais. Écris ce que tu
retiens et pourquoi les deux autres ont été écartées.

Borne le volume : refuse un fichier au-delà d'un seuil raisonnable en taille et
en nombre de lignes, paramétrable au titre de BNF-13 comme les paramètres de
D-33, jamais codé en dur. Une session du CIT compte quelques dizaines de
stagiaires ; un fichier de cent mille lignes est une erreur ou une attaque, pas
un cas d'usage.

## 5. Le format du fichier

Le critère 4 demande que le format soit documenté ET qu'un modèle soit
téléchargeable. Le modèle est produit par le système, pas rédigé à la main dans
un coin du dépôt : un modèle qui diverge du format réellement attendu est pire
que pas de modèle.

Colonnes obligatoires : matricule, nom, prénom, grade, unité. En-têtes en
français, terminologie du CIT (BNF-08).

Robustesse à traiter explicitement, parce que les fichiers viendront d'Excel sous
Windows et porteront des noms accentués :

- encodage : UTF-8 avec ou sans BOM, repli sur CP1252 ; jamais un échec muet ni
  des caractères remplacés silencieusement ;
- séparateur CSV : point-virgule ou virgule, détectés ;
- espaces de début et de fin supprimés sur chaque cellule ;
- lignes entièrement vides ignorées sans être comptées en anomalie ;
- ordre des colonnes indifférent, identification par l'en-tête.

L'installation hors ligne a déjà validé le tri accentué réel en base ; le même
soin vaut ici en lecture.

## 6. Les exceptions

E1 — format de fichier non reconnu : refus, rappel du format attendu, renvoi vers
le modèle téléchargeable. Ni trace ni écriture.

E2 — colonnes obligatoires manquantes : REFUS GLOBAL. Le fichier n'est pas
importé partiellement, et la liste des colonnes manquantes est présentée. Ne
tente pas de deviner une correspondance approximative entre en-têtes.

E3 — fichier entièrement en anomalie : le compte rendu est présenté, aucun
enregistrement n'est proposé. Pas de bouton de confirmation actif sur un compte
rendu sans aucune ligne valide.

E4 — matricule en doublon DANS LE FICHIER : la ligne est signalée en anomalie et
exclue ; les autres restent importables. À distinguer du doublon avec un
stagiaire DÉJÀ EN BASE, qui relève de A2 : celui-ci est identifié et IGNORÉ, non
dupliqué, et il ne rend pas le reste du fichier inimportable. Deux cas, deux
messages distincts dans le compte rendu.

A3 — correction puis réimport : rien à coder, mais vérifie que le parcours est
praticable sans repartir de zéro.

Tous les messages nomment l'action corrective (BNF-10) : « ligne 12 : matricule
absent » et non « ligne 12 invalide ».

## 7. La radiation — enchaînement A4

Absente des critères du backlog, présente à la fiche, portée par trois attributs
de CLS-00, et nécessaire à la définition de l'effectif réel d'US-SES-06
(« affectations ouvertes de stagiaires NON RADIÉS »). Implante-la ici, et
consigne l'écart backlog/fiche sur le modèle de D-44 et du taux d'occupation
d'US-SES-04.

Radier : marquer `radie`, saisir un motif et une date, journaliser. Le stagiaire
n'est PAS supprimé — ses évaluations éventuelles doivent être conservées. Il
disparaît des listes actives et reste consultable.

DISTINCTION À NE PAS LAISSER SE BROUILLER À L'ÉCRAN. Supprimer et radier sont
deux actes différents :

- SUPPRIMER — corriger une erreur de saisie ou d'import. Autorisé tant qu'aucune
  affectation ni note ne référence le stagiaire ; le `PROTECT` que poseront
  US-SES-06 et le paquetage Évaluations le bloquera automatiquement, sans une
  ligne de plus ici (mécanisme de D-23).
- RADIER — constater qu'un stagiaire quitte la formation. Toujours possible,
  jamais destructif.

Libellés explicites, confirmation distincte pour chacun (BNF-09). Si les deux
commandes se ressemblent, quelqu'un radiera pour corriger une faute de frappe, et
le procès-verbal de fin de formation en portera la trace.

Prévois la dé-radiation, ou assume explicitement son absence en le disant : une
radiation saisie par erreur doit pouvoir être défaite, sinon la seule issue est
la suppression, c'est-à-dire la perte de l'historique qu'on voulait préserver.

## 8. Journalisation — données nominatives

La fiche demande de journaliser l'import « avec le nombre de lignes traitées ».
Prends-la au mot : LE JOURNAL PORTE LE COMPTE, JAMAIS LA LISTE DES IDENTITÉS.

Une entrée de journal est immuable (RG-27) : ce qui y entre n'en sort plus, par
aucun profil, administrateur compris. Y déverser soixante identités complètes à
chaque import créerait un fichier nominatif parallèle, non prévu, non maîtrisé et
non effaçable. L'entrée porte la session, le nombre de lignes enregistrées, le
nombre ignorées, l'auteur et l'horodatage.

Les créations individuelles, modifications, radiations et suppressions sont
journalisées par le mécanisme habituel. Vérifie que les valeurs avant/après n'y
recopient pas plus que nécessaire.

## 9. Écrans

Accrochés à la session, dans la rubrique Sessions. Pas de nouvelle rubrique.

- Liste des stagiaires d'une session : matricule, nom, prénom, grade, unité,
  état (actif ou radié, avec motif et date au survol ou en colonne). Paginée et
  dotée d'une recherche dès vingt éléments (BNF-15) — une session en compte
  couramment davantage, donc la règle s'applique ici réellement. Filtre actifs /
  radiés / tous. Fenêtre de pagination partagée (P-32).
  N'anticipe pas US-SES-07 : cette liste sert la saisie et vit au niveau de la
  session. La consultation par brigade et l'export tabulaire sont l'autre story.
- Saisie individuelle (A1) : mêmes contrôles que l'import.
- Écran d'import : format attendu, lien vers le modèle téléchargeable, dépôt du
  fichier, puis compte rendu et confirmation.
- Compte rendu : nombre de lignes valides, tableau des anomalies avec numéro de
  ligne et motif, doublons déjà en base listés séparément. Confirmation explicite
  (BNF-09), inactive s'il n'y a aucune ligne valide.
- Sur la fiche de session : le nombre de stagiaires enregistrés, et le lien vers
  cette liste. L'emplacement « effectif réel » réservé par US-SES-04 reste réservé
  — il dépend des affectations, pas des enregistrements.

Colonne Actions masquée à l'impression (D-63), aucune colonne de donnée masquée.
Mesure la largeur imprimable de la liste et reporte-la dans
`docs/suivi/IMPRESSION-ANALYSE.md`, comme à US-SES-04.

## 10. Habilitations

Domaine de l'organisation. Pédagogique en écriture ; planification, examens et
Direction de Formation en lecture ; administrateur aucun accès.

La cellule EXAMENS lit cette liste — elle en a besoin pour la saisie des notes,
le tableau des écarts de la fiche générique le dit pour CU-P3-07. Elle ne l'écrit
pas. Teste les deux.

## 11. Ce que cette story referme, ce qu'elle reporte

REFERME — aucun report de critère.

REPORTE — la suppression bloquée par une affectation ou une note : mécanisme
générique déjà en place, `PROTECT` posé par les stories à venir, rien à écrire.
Consigne sur le modèle de D-23, avec le test qui constate qu'aucun opposant
n'existe aujourd'hui.

## 12. Tests attendus

Groupe A — modèle et saisie individuelle

A1. Création nominale, journalisée.
A2. RG-17 : même matricule dans la même session, casse indifférente — refus.
A3. Même matricule dans une AUTRE session — ACCEPTÉ. Porte la conséquence de
    modèle du § 2 ; nomme-le pour qu'elle soit lisible sans lire la décision.
A4. Champ obligatoire manquant — refus, message nommant le champ.
A5. `ck_stagiaire_radiation` : radié sans motif, radié sans date, motif sans
    radiation — trois refus, vérifiés PAR INSERTION DIRECTE en base, contrainte
    réellement portée.
A6. Unicité vérifiée aussi par insertion directe court-circuitant le service.

Groupe B — analyse du fichier, sans enregistrement

B1. Fichier CSV valide : compte rendu exact, ET ZÉRO STAGIAIRE EN BASE après
    l'analyse. La seconde assertion est celle qui compte.
B2. Fichier XLSX valide : même résultat. Prouve que la dépendance du § 3 sert.
B3. E1, format non reconnu (un PDF renommé, par exemple) — refus propre, pas une
    trace d'erreur technique.
B4. E2, colonne obligatoire absente — refus global, colonnes manquantes nommées.
B5. E3, toutes les lignes en anomalie — compte rendu, aucune confirmation
    possible.
B6. E4, matricule en doublon dans le fichier — ligne signalée et exclue, les
    autres restent importables.
B7. A2, matricule déjà présent en base — signalé comme déjà présent, IGNORÉ, et
    surtout distinct du cas B6 dans le compte rendu.
B8. Numéros de ligne exacts : une anomalie en ligne 12 du fichier est annoncée en
    ligne 12, en-tête compris dans le décompte de façon cohérente et documentée.
B9. Encodage : fichier UTF-8 avec BOM, fichier CP1252, noms accentués — lus
    correctement dans les trois cas, sans substitution silencieuse.
B10. Séparateur point-virgule et séparateur virgule, tous deux acceptés.
B11. Ordre des colonnes permuté — accepté, identification par l'en-tête.
B12. Fichier au-delà du seuil du § 4 — refusé avec message explicite.

Groupe C — confirmation et transaction

C1. Confirmation nominale : toutes les lignes valides enregistrées, une entrée de
    journal portant le COMPTE et non les identités.
C2. RG-18, le test central : provoque un échec au milieu de l'enregistrement et
    vérifie qu'AUCUNE ligne n'a été écrite. Tout ou rien, prouvé, pas supposé.
C3. Revalidation à la confirmation : après une analyse déclarant une ligne
    valide, insère le même matricule par un autre chemin, puis confirme —
    l'enregistrement doit refuser ou ignorer cette ligne, jamais produire un
    doublon ni une erreur technique brute. C'est la règle absolue du § 4, et sa
    seule preuve.
C4. Confirmation jamais envoyée : vérifie que l'état transitoire retenu au § 4 ne
    laisse rien derrière lui.

Groupe D — radiation

D1. Radiation nominale : `radie` vrai, motif et date enregistrés, journalisée,
    stagiaire toujours présent en base.
D2. Le stagiaire radié disparaît des listes actives et reste consultable avec le
    filtre adéquat.
D3. Dé-radiation, ou test constatant explicitement qu'elle n'est pas offerte,
    selon ce que tu as retenu au § 7.
D4. Suppression d'un stagiaire sans affectation ni note — acceptée, journalisée.
D5. Suppression et radiation sont deux adresses distinctes, avec deux
    confirmations distinctes.

Groupe E — cycle HTTP réel

E1. Chemin nominal, profil pédagogique, sur CHAQUE adresse d'écriture : saisie
    individuelle, import (analyse), import (confirmation), modification,
    radiation, suppression, téléchargement du modèle.
E2. L'import complet par le vrai cycle HTTP, dépôt de fichier compris : POST du
    fichier, compte rendu rendu à l'écran, POST de confirmation, stagiaires en
    base. Pas seulement un appel de service. Leçon de P-30 et de P-23.
E3. Le compte rendu affiche RÉELLEMENT les numéros de ligne et les motifs dans la
    réponse HTTP. Leçon de P-25.
E4. Refus d'habilitation sur chacune des adresses d'écriture : planification,
    examens, Direction de Formation, administrateur.
E5. Lecture accordée aux quatre profils habilités, refusée à l'administrateur.
    La cellule examens lit et n'écrit pas : les deux assertions.
E6. Test de garde du sprint 1 — toute adresse d'écriture figure à la table des
    refus. Cette story en ajoute plusieurs, dont deux inhabituelles (analyse et
    confirmation d'import) : c'est précisément le cas que ce test existe pour
    attraper.
E7. Le modèle téléchargeable est réellement servi, et son en-tête correspond au
    format que l'analyse attend. Un modèle qui diverge du parseur est un défaut,
    pas une broutille : importe le modèle vide lui-même et vérifie qu'il est
    accepté comme fichier valide à zéro ligne.

Groupe F — architecture et dépendances

`tests/architecture` passe en entier, `test_dependances.py` compris avec la
nouvelle dépendance déclarée. Aucune classe au-delà de 200 lignes : l'analyseur
de fichier est le candidat évident au dépassement, découpe-le avant d'y arriver.

## 13. Définition de fini

Implanté, testé, relu par le sous-agent, commité. Suite `pytest` complète verte.
Import essayé RÉELLEMENT dans un navigateur avec un fichier CSV et un fichier
XLSX contenant des noms accentués. Paquet hors ligne reconstitué et
`INSTALLATION-HORS-LIGNE.md` à jour. Mesure d'impression reportée.
`DECISIONS.md` à jour le jour même. Case cochée dans `docs/suivi/sprint-2.md`.

## 14. Ce que tu ne touches pas

Le backlog, le cahier des charges, le registre des risques, le diagramme de
classes.

US-SES-06 : aucune affectation, aucun calcul d'effectif réel, aucune proposition
de répartition. US-SES-07 : aucun export tabulaire, aucune vue par brigade.

## 15. Ce que tu me rends

- La réponse au § 0.1 et ton avis argumenté sur le rejeu du protocole hors ligne.
- Le choix retenu au § 4 pour l'état entre analyse et confirmation, avec les deux
  voies écartées et pourquoi.
- Les entrées `DECISIONS.md` : conséquence de RG-17 sur le modèle et sa question
  de terrain, radiation absente des critères, dé-radiation offerte ou non,
  périmètre de ce qui entre au journal, dépendance ajoutée et effet sur R9.
- Le compte des tests par groupe et le total de la suite.
- Le temps réellement passé, à la demi-heure près. Cinquième mesure, et la
  première sur une story à 5 points dont la fiche annonce elle-même le point
  coûteux : c'est celle qui dira si l'estimation du sprint tient.