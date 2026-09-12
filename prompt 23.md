# Prompt 23 — US-SES-04 · Consulter la composition d'une session

Sprint 2, story 4 sur 12. Must, 3 points. Lot WBS 5.2.5.

## 0. Étape 0 — inventaire avant tout code

Cette story est en grande partie DÉJÀ RÉALISÉE par les trois précédentes.
Ne code rien avant d'avoir dressé l'inventaire ci-dessous et de me l'avoir rendu.

Pour chacun des éléments suivants, réponds : déjà présent / partiellement présent
/ absent, en citant le fichier et la ligne.

1. La fiche de session présente-t-elle déjà ses brigades ? (posé par US-SES-02)
2. Présente-t-elle déjà leur effectif prévisionnel ?
3. Présente-t-elle déjà leur salle attitrée, lue par la relation inverse ?
   (posé par US-SES-03)
4. Le bloc « Référentiel appliqué » affiche-t-il le nombre de matières et le
   volume total, ou le référentiel complet ? (posé par US-SES-01)
5. Quels profils accèdent aujourd'hui à la fiche de session, réellement, d'après
   les tests d'habilitation existants ?
6. Un taux d'occupation est-il calculé quelque part ?
7. La propriété d'écart capacité / effectif exposée par `ressources` à US-SES-03
   est-elle lisible depuis `organisation` sans import, et comment s'appelle-t-elle
   exactement ?

Vérifie aussi, comme d'habitude : suite `pytest` verte avant de commencer, et
sens de dépendance `ressources` → `organisation` confirmé après l'arbitrage
d'US-SES-03.

Cet inventaire n'est pas une formalité de début de prompt. Il conditionne la
mesure de vélocité du jalon C2 : voir § 9.

## 1. Ce que porte cette story

Besoin BF-SES-04. Cas d'utilisation CU-P3-04 (fiche générique, écarts au § 6.8
du dossier des cas d'utilisation). Aucune règle métier nouvelle.
CONSULTATION SEULE.

Critères d'acceptation du backlog v8 :

1. La fiche de session présente ses brigades, leurs effectifs et leurs salles
   attitrées.
2. Le référentiel appliqué à la session est consultable depuis cette fiche.
3. La vue est accessible aux trois cellules, en lecture pour la planification et
   les examens.

Plus, au titre du tableau des écarts du dossier des cas d'utilisation, qui
mentionne un élément absent du backlog : le TAUX D'OCCUPATION. Voir § 4.

## 2. Le critère 3 est incomplet — récidive de D-44

« Les trois cellules » omet la Direction de Formation. La matrice § 11.2 donne la
lecture du paquetage P3 aux quatre profils : pédagogique, planification, examens
ET Direction de Formation. Le tableau des écarts de la fiche générique le dit
explicitement pour CU-P3-04 : « Accessible à la Direction de Formation ».

La matrice fait foi. C'est l'arbitrage exact de D-44 pour US-REF-07, où le
critère 1 du backlog ne nommait que deux cellules là où la matrice en habilitait
trois. N'ouvre pas de nouveau débat : applique, et consigne.

Consigne-le cependant comme une RÉCIDIVE, pas comme un cas isolé : deux critères
d'acceptation du même backlog omettent la Direction de Formation sur des vues en
lecture que la matrice lui accorde. Un défaut de rédaction qui se répète appelle
une relecture systématique du backlog sur ce point, pas une seconde rustine.
Note-le comme tel à l'intention du chef de projet, pour arbitrage avant la revue
du 26.

## 3. La frontière consultation / écriture

Trois écrans, trois acteurs, à ne pas confondre :

- LA FICHE DE SESSION — cette story. Consultation, quatre profils en lecture.
  AUCUNE action d'écriture. Des liens vers les deux écrans ci-dessous, affichés
  seulement à qui détient la permission correspondante (masquage par `perms.`
  natif de Django, D-43).
- L'ÉCRAN DES BRIGADES — US-SES-02. Écriture, cellule pédagogique.
- L'ÉCRAN D'AFFECTATION D'UNE SALLE — US-SES-03. Écriture, cellule planification.

Ne déplace rien entre eux. N'ajoute aucun bouton de création, de modification ni
de suppression sur la fiche. Un utilisateur de la Direction de Formation qui
ouvre cette fiche ne doit voir aucune commande — pas même grisée.

## 4. Le taux d'occupation

Absent des critères du backlog, présent au tableau des écarts du dossier des cas
d'utilisation : « Présente les brigades, leur effectif, leur salle attitrée et le
taux d'occupation. » Implante-le, et consigne l'écart entre les deux livrables
sur le modèle de D-44 — le tableau des écarts est plus précis, il l'emporte.

Définition à retenir, et à énoncer dans ta décision : effectif prévisionnel de la
brigade rapporté à la capacité de sa salle attitrée. Exprimé en pourcentage,
arrondi à l'entier.

Trois cas à traiter explicitement à l'écran, aucun ne devant produire une case
vide ni un zéro trompeur :

- brigade sans salle attitrée : mention explicite, pas de taux ;
- salle sans capacité renseignée : mention explicite (le cas est censé être
  impossible depuis US-SES-03, où l'attribution le refuse — mais des données
  antérieures peuvent exister) ;
- taux supérieur à 100 % : signalé. Ce n'est pas censé arriver, RG-13 l'ayant
  refusé à l'attribution ; cela arrive pourtant si l'effectif prévisionnel d'une
  brigade est relevé APRÈS l'attribution de sa salle. C'est la limite consignée à
  US-SES-03, née du sens de dépendance entre applications : `organisation` ne
  peut pas rappeler le service de `ressources` quand l'effectif change. Cette
  fiche est donc l'endroit où ce dépassement se constate. Signale-le avec les
  deux nombres, couleur toujours doublée d'un mot.

À RESERVER, non à implanter : le taux d'occupation sur l'effectif RÉEL, qui
suppose `Stagiaire` et les affectations (US-SES-06). Emplacement prévu et
commenté, comme US-SES-01 l'avait fait pour les brigades — et vérifie à l'écran
que le commentaire est bien un emplacement, pas un oubli (P-25).

## 5. Le référentiel appliqué

Le critère 2 demande que le référentiel soit CONSULTABLE depuis la fiche. Selon
l'inventaire du § 0.4, deux situations :

- si US-SES-01 n'a posé qu'un résumé (nombre de matières, volume total) et un
  lien, cette story ajoute la consultation du référentiel complet depuis la
  session : matières, volume horaire prescrit de chacune, catégorie de lieu
  requise, en lecture seule ;
- s'il présente déjà le référentiel complet, dis-le et ne réécris rien.

Dans les deux cas, la consultation lit le référentiel de la formation par la
relation. RAPPEL, c'est l'interdit central du paquetage : rien n'est recopié dans
la session, jamais, ni à l'ouverture ni ici. Un test doit le prouver — voir A5.

Réutilise `ServiceReferentiel` plutôt que d'écrire une seconde lecture du
référentiel dans `organisation`. Deux lectures du même objet divergeraient, et
c'est précisément le motif qui a fait remonter deux extensions au patron en D-32.

## 6. Écran

Pas de nouvelle adresse si la fiche de session existe déjà : cette story enrichit
la fiche livrée à US-SES-01. Pas de nouvelle rubrique de navigation.

Structure attendue, de haut en bas :

- identité de la session : intitulé, formation, type de formation, période, état,
  effectif attendu ;
- l'indicateur d'écart d'effectif de RG-15 posé à US-SES-02, conservé tel quel ;
- le tableau des brigades : désignation, effectif prévisionnel, salle attitrée et
  sa capacité, taux d'occupation, emplacement réservé pour l'effectif réel ;
- le référentiel appliqué (§ 5) ;
- les liens vers les écrans d'écriture, conditionnés aux permissions (§ 3).

Une session sans aucune brigade affiche le signalement posé à US-SES-02, pas un
tableau vide sans explication.

Pagination : inutile ici, une session portant deux à six brigades. Ne l'ajoute
pas « au cas où » — BNF-15 ne l'exige qu'au-delà de vingt éléments. Le référentiel
complet, lui, peut dépasser vingt matières : applique la règle à ce tableau-là si
c'est le cas, et à lui seul.

## 7. Impression — traiter le contrôle K3 ici plutôt qu'au sprint 4

Cette fiche est un document destiné à circuler sur papier : c'est la composition
d'une session, elle sera imprimée et transmise. Le point ouvert du sprint 1
(Prompt 19, bloc B) constate que les écrans Instructeurs et Lieux débordent
encore de la largeur imprimable en portrait, de 33 et 74 px, et renvoie leur
traitement aux gabarits imprimables du sprint 4.

Mesure la largeur imprimable de cette fiche MAINTENANT, selon le protocole de
`docs/suivi/IMPRESSION-ANALYSE.md`, et reporte le résultat dans ce même fichier.
Si elle tient, c'est acquis pour dix minutes de travail. Si elle déborde, n'y
touche pas au-delà de ce que D-63 autorise — aucune colonne de donnée n'est
masquée — et ajoute la ligne au point ouvert du sprint 4 plutôt que d'improviser
une correction ici.

## 8. Habilitations

Lecture : pédagogique, planification, examens, Direction de Formation.
Écriture : aucune sur cet écran.
Administrateur : aucun accès, comme sur tout le paquetage P3.

Le test qui compte vraiment ici n'est pas le refus, c'est l'ACCÈS : un profil
Direction de Formation, qui n'écrit nulle part dans le système, doit atteindre
cette fiche depuis la navigation et la lire entièrement. Leçon de P-26 : des
permissions exactes sur un écran que rien ne mène nulle part restent invisibles.
Vérifie donc aussi que la rubrique Sessions apparaît bien dans son menu.

## 9. Vélocité — ce que cette story doit produire comme mesure

La revue du 26 septembre doit établir la clé de conversion réelle, absente du
sprint 1, sur laquelle reposent les 169 points restants. Une story cotée 3 points
et livrée en une heure parce que trois stories précédentes l'avaient déjà faite
fausse cette mesure dans le sens optimiste.

Tu me rends donc, en fin de story :

- le temps réellement passé, à la demi-heure près ;
- l'estimation, d'après l'inventaire du § 0, de la part des 3 points qui avait
  déjà été produite par US-SES-01, US-SES-02 et US-SES-03 ;
- ton avis sur ce qu'aurait dû être le découpage : les emplacements réservés
  posés par les stories précédentes ont-ils facilité le travail, ou US-SES-04
  aurait-elle dû être fondue dans US-SES-01 dès la planification du sprint ?

Ces trois éléments vont en rétrospective. Ne les lisse pas.

## 10. Ce que cette story referme, ce qu'elle reporte

REFERME — aucun report de critère.

Elle remplit en revanche des emplacements réservés : celui du taux d'occupation
si les stories précédentes l'avaient prévu, et le cas échéant celui du
référentiel complet. Vérifie-les À L'ÉCRAN, pas seulement par un test : P-25
reste la leçon la plus coûteuse du sprint 1, quatre jours d'ouverture pour un
emplacement qu'on croyait rempli.

REPORTE — le taux d'occupation sur l'effectif réel, vers US-SES-06. Consigne-le
sur le modèle de D-23. Ce n'est pas un report de critère d'acceptation : ne le
compte pas dans le décompte des reports que la revue du 26 vérifie nommément,
et dis-le explicitement dans ta décision pour qu'il ne s'y glisse pas.

## 11. Tests attendus

Les tests déjà écrits par US-SES-01 à US-SES-03 couvrent une partie de cette
story. N'en réécris aucun. Ajoute seulement ce qui manque, et dis-moi lesquels
existaient déjà.

Groupe A — lecture et calcul

A1. Taux d'occupation nominal : effectif 18, capacité 24 — 75 %.
A2. Brigade sans salle attitrée : mention explicite, aucun taux, aucune erreur.
A3. Salle sans capacité renseignée : mention explicite.
A4. Taux supérieur à 100 % : effectif relevé après attribution — signalé, avec
    les deux nombres. Test central du § 4 ; nomme-le pour que la limite qu'il
    documente soit lisible sans lire la décision d'US-SES-03.
A5. Le référentiel présenté est celui de la formation, lu par la relation :
    modifie le volume prescrit d'un élément, vérifie que la fiche de la session
    montre la nouvelle valeur. Si ce test existe déjà depuis US-SES-01, ne le
    duplique pas — cite-le.
A6. Session sans aucune brigade : signalement affiché, pas de tableau vide.

Groupe B — cycle HTTP réel

B1. GET de la fiche par chacun des quatre profils habilités : 200, et le contenu
    attendu réellement présent — brigades, effectifs, salles, taux, référentiel.
    Quatre tests ou un test paramétré, à ta main.
B2. Direction de Formation : accès accordé ET aucune commande d'écriture dans la
    réponse. Les deux assertions.
B3. Cellule pédagogique : le lien vers l'écran des brigades est présent.
    Cellule planification : le lien vers l'écran d'affectation d'une salle est
    présent, celui vers l'écran des brigades est absent.
B4. Administrateur : refus.
B5. Navigation : la rubrique Sessions figure au menu d'un profil Direction de
    Formation, qui n'écrit nulle part.
B6. Test de garde du sprint 1 : passe sans modification. Cette story n'ajoute
    aucune adresse d'écriture ; s'il réclame quelque chose, c'est que tu en as
    ajouté une sans le vouloir.

Groupe C — architecture

`tests/architecture` passe en entier, aucun import de `ressources` dans
`organisation`. La salle attitrée et sa capacité se lisent par la relation
inverse, méthode D-52.

## 12. Définition de fini

Implanté, testé, relu par le sous-agent, commité. Suite `pytest` complète verte.
Fiche vérifiée dans un navigateur avec les quatre profils, pas seulement par
`assertContains`. Mesure d'impression reportée dans `IMPRESSION-ANALYSE.md`.
`DECISIONS.md` à jour le jour même. Case d'US-SES-04 cochée dans
`docs/suivi/sprint-2.md`.

## 13. Ce que tu ne touches pas

Le backlog, le cahier des charges, le registre des risques, le diagramme de
classes : réservés au chef de projet. L'omission de la Direction de Formation au
critère 3 s'écrit dans `DECISIONS.md`, ligne « Impact sur les livrables ».

Les écrans d'écriture d'US-SES-02 et US-SES-03 : aucun déplacement de
fonctionnalité vers la fiche.

US-SES-05 et US-SES-06. Un emplacement réservé pour l'effectif réel, oui ; une
lecture anticipée d'un modèle `Stagiaire` qui n'existe pas, non.

## 14. Ce que tu me rends

- L'inventaire du § 0, point par point, avec fichiers et lignes.
- Les trois éléments de vélocité du § 9.
- Les entrées `DECISIONS.md` : omission de la Direction de Formation et son
  caractère de récidive, taux d'occupation absent du backlog, définition retenue
  du taux, report de sa version sur effectif réel.
- Le résultat de la mesure d'impression.
- Le compte des tests ajoutés, en distinguant ceux qui existaient déjà.