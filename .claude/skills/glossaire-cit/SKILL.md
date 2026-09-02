---
name: glossaire-cit
description: Vocabulaire métier du Centre d'Instruction des Transmissions. À consulter dès qu'un terme du domaine apparaît — brigade, séance, référentiel, progression, créneau, avenant, évaluation — ou pour nommer une classe, un champ, un libellé d'écran ou un message d'erreur.
---

# Glossaire du CIT

Ces définitions viennent de neuf itérations d'entretiens de terrain. **Plusieurs
sont contre-intuitives et ne doivent pas être réinterprétées.** Une erreur sur
l'une d'elles invalide le modèle.

## Chaîne du domaine

`Type de formation → Formation → Session → Brigade → Stagiaire`

**Type de formation** — catégorie de classement : OFF, ODR, CAT-1.

**Formation** — cursus identifié par son intitulé, sa spécialité, sa durée.
**Sans dates** : seules ses sessions en ont.

**Session** — instance datée d'une formation. Deux sessions d'une même formation
peuvent se chevaucher.

**Brigade** — **outil de séparation d'effectifs, non spécialité pédagogique.**
Toutes les brigades d'une session suivent le même référentiel ; seul l'ordre de
déroulement diffère. Constitution manuelle : le système enregistre un découpage
décidé par le terrain, il ne le calcule pas. Sa désignation n'est unique qu'au
sein du type de formation — `EXP1` peut exister dans deux blocs différents.

**Progression décalée** — le décalage volontaire entre brigades d'une même session
est une **contrainte à préserver**, jamais une anomalie à corriger. Il sert
l'optimisation de l'emploi des instructeurs.

## Référentiel

**Matière** — élément d'un **catalogue indépendant des formations**, réutilisable
par plusieurs d'entre elles.

**Référentiel** — ensemble des matières rattachées à une formation, chacune avec
un volume horaire prescrit propre à cette formation. **Le référentiel appartient
à la formation, jamais à la brigade.**

**Chef de module** — instructeur désigné pour une matière **du catalogue**,
indépendamment de la formation et de la session. Il doit être qualifié pour elle.

## Lieux et temps

**Salle attitrée** — salle fixe d'une brigade pour toute la session. Affectée par
la cellule planification, détentrice du catalogue des lieux.

**Lieu partagé** — amphithéâtre, laboratoire, salle spécialisée. Arbitré séance
par séance. Son *mode de partage* dit s'il accueille plusieurs brigades ensemble
ou seulement l'une après l'autre.

**Sans lieu** — place d'armes, terrain de sport, extérieur. Peut accueillir
plusieurs brigades ; porte une capacité si le centre la connaît.

**Grille horaire** — squelette de la semaine. Plusieurs coexistent — horaire
ordinaire, horaire de Ramadan — **une seule est active**, désignée par décision
de la cellule planification et non déduite du calendrier.

**Créneau type** — case du squelette : jour de semaine, rang, heure de début et
de fin. **Aucune date** : c'est un patron répété chaque semaine.

**Séance** — événement d'enseignement un jour donné, portant ses **heures
réelles**. Elle peut couvrir plusieurs créneaux consécutifs, ou sortir de la
grille. Distincte de la **ligne de programme**, qui la rattache à une brigade.

**Séance regroupée** — plusieurs brigades sur la même séance. La charge de
l'instructeur n'est comptée **qu'une fois** ; le volume horaire est décompté
**pour chaque brigade**.

**AD/GROUPEMENT** — libellé d'un créneau non pourvu. Ce n'est pas un vide : le
groupe est à disposition du groupement.

## Programme

**Programme hebdomadaire** — couvre **le centre entier** pour une semaine, non une
brigade. L'impression par journée est un format de sortie.

**Validation croisée** — la cellule planification élabore, la cellule pédagogique
valide, le directeur de la formation signe. **Aucun affichage sans validation et
signature.** La signature est manuscrite : le système en enregistre la date et le
nom du signataire.

**Avenant** — trace datée et motivée portée par une séance modifiée après
affichage. Le programme reste affiché ; la validation et la signature demeurent
acquises.

**Déclaration par exception** — une séance d'un programme affiché est **réputée
exécutée** ; seule la non-exécution se déclare, avec motif. Le silence vaut
exécution. Consolidée en fin de semaine par la cellule planification.

**Report** — une séance reportée puis tenue n'entame **pas** le volume réalisé :
le cours a eu lieu, plus tard. À ne pas confondre avec la non-exécution, qui le
retranche.

**Progression réalisée** — document hebdomadaire de ce qui a effectivement été
dispensé. Pratique existante au CIT, que le système automatise.

## Évaluations

**Deux types seulement.**

**Évaluation formative** — le contrôle. Date décidée par l'instructeur, qui
informe les cellules ; **un seul sujet** ; périmètre brigade ; une séance
verrouillée est insérée au programme.

**Évaluation certificative** — l'examen final. Date fixée par le **3ᵉ bureau** ;
**deux sujets dont un retenu par la commission d'examen** ; périmètre session ;
une salle et des surveillants par brigade, même sujet, même date.

L'« examen partiel » est le contrôle sous un autre nom. Ne pas le traiter comme
un troisième type.

**Périmètre d'une évaluation** — une brigade ou la session entière. Détermine
conjointement la date, le sujet et l'organisation. La raison profonde est le
sujet : deux brigades composant à des dates différentes ne peuvent le partager.

Le **type d'un même module peut varier selon la formation** : le projet de fin
d'études est formatif dans la plupart des formations, certificatif pour le stage
Analyste en informatique.

**Surveillant** — soit un instructeur référencé, dont la disponibilité est
contrôlée, soit une **personne extérieure au système**, enregistrée par son seul
nom et non soumise à ce contrôle.

**Classement** — au niveau de la **session**, tous stagiaires confondus.

**Procès-verbal de fin de formation** — document unique pour la session, portant
toutes les notes de tous les modules.

## Acteurs hors système

Ils n'ont pas de compte et n'accèdent à rien. Une cellule enregistre à leur place,
et la saisie est rattachée à l'agent qui la porte, jamais à eux.

| Acteur | Donnée transmise | Cellule qui saisit |
|---|---|---|
| Instructeur | indisponibilités, sujets, décision de contrôle | planification, examens |
| Commission d'examen | choix du sujet retenu | examens |
| 3ᵉ bureau | date d'examen certificatif | examens |
| Directeur de la formation | signature du programme | planification |

## Les cinq profils

Cellule pédagogique · cellule planification · cellule examens · Direction de
Formation (lecture seule) · administrateur.
