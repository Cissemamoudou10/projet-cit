# Prompt 26 — US-SES-07 · Consulter la liste des stagiaires

Sprint 2, story 7 sur 12. Must, 3 points. Lot WBS 5.2.8.

## 0. Étape 0 — inventaire avant tout code

Comme à US-SES-04, cette story est en partie DÉJÀ RÉALISÉE. Dresse l'inventaire
et rends-le-moi avant de coder. Pour chaque point : déjà présent / partiel /
absent, fichier et ligne.

1. La liste des stagiaires au niveau de la SESSION existe-t-elle ? (US-SES-05)
2. La recherche par nom, prénom, matricule y est-elle déjà offerte, et sur quels
   champs exactement ?
3. La pagination et la fenêtre partagée (P-32) y sont-elles ?
4. La brigade d'affectation de chaque stagiaire y figure-t-elle ? (US-SES-06)
5. Le filtre actifs / radiés / tous existe-t-il ?
6. Une lecture au niveau d'une BRIGADE existe-t-elle quelque part ?
7. Un export tabulaire existe-t-il, sous quelque forme que ce soit, dans tout le
   projet ? Si oui, c'est le précédent à suivre ; sinon, celui-ci fera référence.
8. Le lecteur de fichier d'US-SES-05 : où vit-il, quelles colonnes attend-il
   exactement, dans quel ordre, avec quels en-têtes ? Cette story doit écrire ce
   que celui-là sait lire (§ 4).

Suite `pytest` verte avant de commencer.

## 1. Ce que porte cette story

Besoin BF-SES-07. Cas d'utilisation CU-P3-07, fiche générique, écarts au § 6.8 du
dossier des cas d'utilisation : « Consultation seule, filtrable par session et par
brigade. Accessible à la cellule examens, qui en a besoin pour la saisie des
notes. » Aucune règle métier nouvelle. CONSULTATION SEULE.

Critères d'acceptation du backlog v8 :

1. La liste est consultable au niveau de la session et au niveau de chaque
   brigade.
2. Une recherche par nom, prénom ou matricule est disponible.
3. La liste est exportable au format tabulaire.
4. La cellule examens y accède en lecture pour la saisie des notes.

HORS PÉRIMÈTRE : toute écriture. Aucune création, modification, radiation,
affectation ni suppression sur ces écrans — seulement des liens vers les écrans
qui les portent (US-SES-05 pour la saisie, US-SES-06 pour l'affectation),
conditionnés aux permissions.

## 2. Une seule liste, filtrée — pas deux écrans

Le critère 1 nomme deux niveaux de lecture. Sers-les avec UN SEUL écran de liste
et un filtre par brigade, pas avec deux écrans distincts.

Motif à consigner : deux lectures du même objet divergent à la première
évolution — colonne ajoutée d'un côté, format d'export corrigé de l'autre. C'est
le raisonnement qui a fait remonter deux extensions au patron en D-32, et celui
qui a fait réutiliser `ServiceReferentiel` à US-SES-04 plutôt qu'écrire une
seconde lecture du référentiel.

Points d'entrée, tous vers le même écran avec un filtre préréglé :

- depuis la fiche de session — liste de tous les stagiaires de la session ;
- depuis chaque ligne de brigade, sur l'écran des brigades et sur la fiche de
  composition — liste filtrée sur cette brigade ;
- la liste déjà livrée par US-SES-05 EST cet écran. Ne la double pas : enrichis-la.

Filtres offerts : brigade (dont « non affectés » et « toutes »), statut (actifs /
radiés / tous). Le filtre actif est TOUJOURS visible et énoncé en toutes lettres
au-dessus du tableau — voir § 5, c'est le point qui engage.

Colonnes : matricule, nom, prénom, grade, unité, brigade d'affectation, statut.
Tri par nom par défaut, accentué correctement — le tri accentué réel a été validé
en base au test d'installation hors ligne du 7 septembre, sers-t'en.

Recherche sur nom, prénom et matricule, insensible à la casse et aux accents.
Pagination et fenêtre partagée (P-32) dès vingt éléments : une session en compte
couramment plus, la règle s'applique réellement ici.

## 3. L'export — le vrai contenu de la story

Le critère 3 demande un export « au format tabulaire ».

Formats : CSV et XLSX. Pas de dépendance nouvelle — `openpyxl` a été ajouté au
paquet hors ligne à US-SES-05, et sert ici en écriture. Ne réintroduis rien
d'autre, surtout pas pandas.

CE QUI EST EXPORTÉ : exactement ce que l'écran montre, filtre et recherche
compris. Un export qui ignore le filtre affiché est un piège à procès-verbal.

ENCODAGE CSV : UTF-8 AVEC BOM. Sans le BOM, Excel sous Windows ouvre les noms
accentués en charabia, et l'agent conclura que le système est cassé. Le parseur
d'US-SES-05 sait déjà lire le BOM — c'est un test qu'il a passé.

Séparateur CSV : point-virgule, cohérent avec les Excel configurés en français,
et lu par le parseur d'US-SES-05.

## 4. L'export doit être réimportable — exigence, pas bonus

Les colonnes exportées sont EXACTEMENT celles que le parseur d'US-SES-05 attend :
mêmes en-têtes, même orthographe, même casse. Un fichier exporté puis redéposé à
l'import doit être accepté sans une retouche.

Trois raisons, à écrire dans ta décision :

- l'enchaînement A3 de CU-P3-05 prévoit qu'on corrige un fichier hors système
  puis qu'on recommence l'import ; exporter, corriger, réimporter est le parcours
  naturel, et il n'existe que si les formats coïncident ;
- transporter une liste nominative d'une session vers une autre est un besoin
  réel du centre ;
- cela donne un test d'intégration qui vérifie d'un coup le lecteur et
  l'écrivain, et qui tombera le jour où l'un des deux dérivera sans l'autre.

CONSÉQUENCE À RESPECTER : le fichier exporté ne porte AUCUNE ligne de titre,
aucune ligne de total, aucune cellule fusionnée, aucun commentaire. Rien qu'un
en-tête de colonnes et des lignes. Une jolie mise en page casserait la
réimportabilité, et ce serait un mauvais échange.

Les colonnes supplémentaires que l'import ne connaît pas — brigade, statut —
peuvent figurer APRÈS les colonnes du modèle, à condition que le parseur les
ignore sans broncher. Vérifie-le : US-SES-05 identifie les colonnes par leur
en-tête et tolère l'ordre, il doit tolérer aussi le surplus. Si ce n'est pas le
cas, c'est un défaut d'US-SES-05 à corriger ici, à consigner dans `PROBLEMES.md`.

## 5. Le contexte va dans le NOM DU FICHIER, pas dans le contenu

Puisque le fichier reste strictement tabulaire (§ 4), le contexte se porte
ailleurs, et il doit se porter quelque part : un fichier de soixante noms, ouvert
trois semaines plus tard, doit dire de quelle session il vient et quel filtre lui
était appliqué. Sans cela, quelqu'un fondera un procès-verbal sur une liste dont
il ignore qu'elle excluait les radiés.

Nom de fichier déterministe et documenté, portant : la session, la brigade si un
filtre de brigade est actif, le statut filtré, la date d'export. Sans espaces ni
accents ni caractères interdits sous Windows.

À l'écran et à l'impression, le filtre actif est rappelé en toutes lettres
au-dessus du tableau : « Session X — brigade EXP1 — stagiaires actifs
uniquement ». Pas une icône, pas une couleur seule : une phrase.

## 6. Journalisation de l'export — données nominatives qui sortent

Un export fait sortir des données nominatives du périmètre du système. Journalise
l'opération, avec la même règle qu'à US-SES-05 : LE JOURNAL PORTE LE COMPTE ET LE
CONTEXTE, JAMAIS LES IDENTITÉS. Session, filtre appliqué, nombre de lignes,
format, auteur, horodatage.

Motif à consigner : une entrée de journal est immuable (RG-27) ; y déverser les
identités créerait un second fichier nominatif, non prévu et non effaçable. Et
sans journal du tout, personne ne pourra jamais dire qui a sorti la liste
nominative d'une session — ce qui est exactement la question qu'on pose après
coup, jamais avant.

C'est une opération de LECTURE qui se journalise, ce qui est inhabituel dans ce
système : le journal ne traçait jusqu'ici que les écritures. Dis-le explicitement
dans ta décision, et vérifie que le mécanisme s'y prête sans être tordu. Si la
nature d'action à employer n'existe pas, ajoute-la proprement au catalogue plutôt
que d'en détourner une (précédent D-18 et D-38).

## 7. Impression

Cette liste sera imprimée : c'est la liste nominative d'une session ou d'une
brigade, elle circule sur papier et sert d'appel.

Colonne Actions — s'il y en a une — masquée à l'impression par le gabarit
générique (D-63), aucune colonne de donnée masquée. Le rappel du filtre (§ 5)
figure sur le papier.

Mesure la largeur imprimable en portrait selon le protocole de
`docs/suivi/IMPRESSION-ANALYSE.md` et reporte le résultat. Sept colonnes, dont
plusieurs textuelles : c'est un candidat sérieux au débordement, comme l'ont été
Instructeurs et Lieux au sprint 1. Si elle déborde, n'improvise pas de correction
— ajoute la ligne au point ouvert du sprint 4, avec la mesure chiffrée.

## 8. Habilitations

Domaine de l'organisation. Lecture : pédagogique, planification, examens,
Direction de Formation. Écriture : aucune sur ces écrans. Administrateur : aucun
accès.

Le critère 4 nomme la cellule EXAMENS, qui détient déjà la lecture sur ce domaine.
Rien de neuf à déclarer, mais le test compte : un profil examens doit atteindre
cette liste depuis la navigation, la filtrer par brigade et l'exporter. C'est la
lecture dont il aura besoin au sprint 4 pour la saisie des notes ; s'il ne peut
pas l'atteindre, on le découvrira dans six semaines. Leçon de P-26.

L'export suit la lecture : qui peut lire peut exporter. Ne crée pas une
permission d'export distincte — elle n'existe ni dans la matrice ni dans le
catalogue des domaines, et l'inventer serait ajouter une règle que personne n'a
arbitrée.

## 9. Ce que cette story referme, ce qu'elle reporte

REFERME — aucun report de critère. REPORTE — aucun. Dis-le explicitement dans ton
compte rendu : le tableau des reports suivi en revue ne bouge pas de cette story,
et il vaut mieux que ce soit écrit que déduit d'un silence.

## 10. Tests attendus

N'écris aucun test qui existe déjà depuis US-SES-05 ou US-SES-06. Cite-les, et
ajoute seulement ce qui manque. Dis-moi lesquels préexistaient.

Groupe A — lecture et filtres

A1. Liste au niveau de la session : tous les stagiaires, affectés ou non.
A2. Liste filtrée sur une brigade : seulement ses stagiaires.
A3. Filtre « non affectés » : seulement ceux sans affectation ouverte.
A4. Filtre de statut : actifs, radiés, tous — trois résultats distincts.
A5. Recherche sur nom, prénom et matricule, insensible à la casse ET aux accents.
A6. Tri accentué : des noms commençant par É, E et A se rangent correctement.
A7. Un stagiaire déplacé d'une brigade à l'autre (US-SES-06) apparaît sous sa
    brigade COURANTE, pas sous l'ancienne. Test de la lecture par affectation
    ouverte ; il tomberait si quelqu'un lisait l'historique au lieu du présent.

Groupe B — export

B1. Export CSV : colonnes, en-têtes, nombre de lignes conformes.
B2. Export XLSX : idem.
B3. L'export respecte le filtre de brigade actif.
B4. L'export respecte le filtre de statut actif. Deux exports d'une même session,
    l'un actifs seuls, l'autre tous, produisent des comptes différents.
B5. L'export respecte la recherche en cours.
B6. CSV : BOM présent, séparateur point-virgule, noms accentués intacts après
    relecture.
B7. Nom de fichier : déterministe, portant session, filtre et date, sans espace
    ni accent ni caractère interdit.
B8. LE TEST QUI COMPTE — aller-retour : exporte une session, redépose le fichier
    exporté à l'import d'US-SES-05 sur une AUTRE session, vérifie que toutes les
    lignes sont acceptées et que les stagiaires créés portent les mêmes valeurs.
    En CSV et en XLSX. Ce test tombe le jour où le lecteur et l'écrivain
    divergent, et c'est exactement ce qu'on veut qu'il fasse.
B9. Export d'une liste vide : fichier valide avec le seul en-tête, pas une erreur.
B10. Export d'une liste comportant un stagiaire radié, filtre « tous » : le
    statut est exporté et lisible.

Groupe C — journalisation

C1. Un export produit une entrée de journal portant session, filtre, nombre de
    lignes, format et auteur.
C2. Cette entrée ne contient AUCUNE identité de stagiaire. Vérifie-le
    explicitement sur le contenu de l'entrée, pas en supposant.
C3. Une simple consultation sans export ne produit PAS d'entrée : on journalise
    la sortie de données, pas la lecture d'un écran.

Groupe D — cycle HTTP réel

D1. GET de la liste par chacun des quatre profils habilités : 200 et contenu
    réellement présent.
D2. GET de l'export CSV puis XLSX par un profil habilité : en-tête de réponse
    correct, nom de fichier correct, contenu correct.
D3. Profil EXAMENS : atteint la liste depuis la navigation, la filtre par brigade
    et l'exporte. Les trois assertions — c'est le critère 4, et il ne se prouve
    pas autrement.
D4. Aucune commande d'écriture n'est présente dans la réponse pour un profil
    Direction de Formation.
D5. Les liens vers les écrans d'écriture apparaissent pour la cellule pédagogique
    et sont absents pour les autres.
D6. Administrateur : refus sur la liste ET sur l'export.
D7. Le rappel du filtre en toutes lettres (§ 5) est RÉELLEMENT présent dans la
    réponse HTTP. Leçon de P-25.
D8. Test de garde du sprint 1 : cette story n'ajoute aucune adresse d'écriture.
    S'il réclame quelque chose, c'est que l'export a été déclaré en écriture —
    vérifie alors que c'est bien ce que tu voulais et tranche explicitement.

Groupe E — architecture

`tests/architecture` en entier. Aucun import de `ressources` dans `organisation`.
Aucune classe au-delà de 200 lignes : l'écrivain de fichier va de pair avec le
lecteur d'US-SES-05, garde-les de taille comparable et au même endroit s'il y a
un module dédié.

## 11. Définition de fini

Implanté, testé, relu par le sous-agent, commité. Suite `pytest` complète verte.
Export essayé RÉELLEMENT : fichier CSV ouvert dans un tableur avec des noms
accentués, fichier XLSX de même, et l'un des deux redéposé à l'import pour
vérifier l'aller-retour à la main. Mesure d'impression reportée dans
`IMPRESSION-ANALYSE.md`. `DECISIONS.md` à jour le jour même. Case cochée dans
`docs/suivi/sprint-2.md`.

## 12. Ce que tu ne touches pas

Le backlog, le cahier des charges, le registre des risques, le diagramme de
classes.

Les écrans d'écriture d'US-SES-05 et US-SES-06 : aucune fonctionnalité déplacée
vers la consultation. Si le parseur d'US-SES-05 doit être corrigé pour tolérer
les colonnes supplémentaires (§ 4), c'est une correction ciblée, consignée dans
`PROBLEMES.md`, pas une refonte.

Le paquetage Évaluations, même si la cellule examens lira cette liste au sprint 4.

## 13. Ce que tu me rends

- L'inventaire du § 0, point par point.
- Ce qui restait réellement à faire une fois l'inventaire dressé, et ton
  estimation de la part des 3 points déjà produite par US-SES-05 et US-SES-06 —
  même exercice qu'à US-SES-04, et pour la même raison : la clé de conversion du
  jalon C2 ne vaut que si les mesures sont honnêtes.
- Les entrées `DECISIONS.md` : écran unique filtré plutôt que deux écrans,
  réimportabilité de l'export et ce qu'elle interdit, contexte porté par le nom
  de fichier, journalisation d'une opération de lecture et nature d'action
  employée.
- Le résultat de la mesure d'impression.
- Le compte des tests ajoutés, en distinguant ceux qui préexistaient.
- Le temps réellement passé, à la demi-heure près.