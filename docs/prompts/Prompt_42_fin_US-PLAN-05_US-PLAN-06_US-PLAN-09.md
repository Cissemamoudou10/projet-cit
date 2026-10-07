# Prompt 42 — Sprint 3 : fin d'US-PLAN-05, puis US-PLAN-06 et US-PLAN-09

Phase 5, sprint 3. Trois parties, trois commits, **un seul rendu à la fin**.
Ce sont les dernières stories du sprint ; la clôture et la préparation de J2
feront l'objet du prompt suivant.

| Partie | Objet | Points |
|---|---|---|
| 1 | Fin d'US-PLAN-05 : écran d'ajout, deux reports, relecture complète | (8, déjà comptés) |
| 2 | US-PLAN-06 — Regrouper plusieurs brigades sur une même séance | 5 |
| 3 | US-PLAN-09 — Traiter une indisponibilité déclarée | 5 |

Règles inchangées : arrêt sur les seules conditions écrites ici ; pour le
reste, tu tranches selon les trois principes du sprint 2, tu consignes, tu
continues ; aucun numéro de décision cité de mémoire ; **heure de début
écrite dans `heures-sprint-3.md` avant toute autre action, pour chaque
partie**.

**Condition d'arrêt commune** : une opération qui exigerait d'écrire ou de
supprimer une séance ou une ligne hors de la porte unique.

**Préalable** : remplace par des noms manifestement inventés les noms de
personnes de `docs/conception/16-maquettes.md` et de tout autre document du
dépôt (même règle qu'aux fixtures : le doute suffit). Commit `docs: noms
inventés dans les maquettes`.

---

## Partie 1 — Fin d'US-PLAN-05

1. **Écran d'ajout manuel (C4)** : depuis la consultation de la semaine, un
   lien « Ajouter une séance » sur un créneau libre d'une brigade ; formulaire
   (matière, instructeur, lieu) appelant `creer_seance`, qui verrouille.
   Tests HTTP : ajout admis et verrouillé ; ajout violant une contrainte,
   message nommant la contrainte, rien en base ; ajout sur un programme
   affiché sans avenant refusé, avec avenant admis (nature « ajout »).
2. **D-121 E2** : la création d'une période bloquante qui recouvre des
   séances programmées énumère ces séances (sélecteur existant), avec pour
   chacune un lien vers sa modification. Elle ne les supprime ni ne les
   déplace : l'arbitrage est humain. Test service et test HTTP.
3. **D-121 A3** : la suppression d'une période bloquante ne restaure aucune
   séance. Décision consignée, test qui le constate.
4. **Relecture complète** de la story par `relecteur-conception`, corrections
   comprises — la précédente n'avait pas relu après les corrections.
5. Case cochée, ligne au tableau des sprints, ligne d'heures.

Commit : `feat(planification): US-PLAN-05 ajout manuel et périodes bloquantes`.

---

## Partie 2 — US-PLAN-06 : regrouper plusieurs brigades sur une même séance

| # | Critère | Source |
|---|---|---|
| C1 | Plusieurs brigades peuvent être associées à une même séance en lieu partagé | backlog c.1 |
| C2 | Chaque brigade conserve une ligne distincte sur le programme | backlog c.2 |
| C3 | Les lignes d'un regroupement partagent une séance commune | backlog c.3 |
| C4 | La charge de l'instructeur n'est comptée qu'une fois | backlog c.4 |
| C5 | Capacité du lieu < somme des effectifs : refus avec l'écart | CU-P5-04 E1 |

C2, C3 et C4 sont **déjà vrais par construction** (une `Seance`, N
`LigneProgramme`, D-139) : la story les prouve par des tests, elle ne les
recode pas.

**Arbitrages.**

**R1 — Deux opérations dans la porte unique.** `associer_brigades(seance,
brigades, confirmation)` et `retirer_brigade(seance, brigade)`. Chacune
passe la garde, puis `ServiceContraintes` sur la séance résultante (capacité
cumulée, mode de partage du lieu, volume et prérequis pour chaque brigade
ajoutée, brigades libres sur le créneau), puis journalise. La séance reste
verrouillée.

**R2 — Le retrait et la dissolution ne créent pas de séance autonome.**
CU-P5-04 A2 et A3 disent que la ligne retirée « redevient une séance
autonome ». C'est inexprimable : cette séance aurait le même instructeur au
même créneau que la séance d'origine, ce que RG-34 interdit. Principe 3 :
le retrait **supprime la ligne de la brigade** ; son créneau redevient libre,
à replanifier par ajout manuel ou régénération. La dissolution est le retrait
de toutes les brigades sauf une, choisie. Écart à consigner contre CU-P5-04.

**R3 — Le partage séquentiel (A1) n'est pas un regroupement** : plusieurs
séances distinctes dans le même lieu, déjà possibles par l'ajout manuel.
Rien à implanter ; un test le constate (charge comptée par séance).

**R4 — Sur un programme affiché.** Associer une brigade est un ajout pour
elle : avenant obligatoire (nature « ajout »). Retirer une brigade efface sa
ligne : refusé, comme la suppression (renvoi à la non-exécution, qui se
rattache justement à la ligne).

**R5 — L'écran.** Sur une séance de la consultation, « Associer des
brigades » présente les brigades pour lesquelles la matière est programmable
au créneau (CU-P5-04, étape 2) — calculées en un nombre constant de
requêtes, pas une par brigade. Avertissement et confirmation dès que la
séance réunit déjà plusieurs brigades (E3 de CU-P5-03).

**Tests attendus**
- service : association admise (lignes ajoutées, une seule séance, charge
  comptée une fois dans le calcul existant de la charge) ; capacité
  dépassée avec l'écart ; lieu non partageable ; brigade déjà occupée sur le
  créneau ; prérequis non atteint pour une brigade ajoutée ; retrait (ligne
  supprimée, créneau libre) ; dissolution ; retrait sur un affiché refusé ;
  association sur un affiché sans puis avec avenant ; sur un soumis, refus
- HTTP : association par la planification ; liste des brigades proposées et
  nombre de requêtes identique avec 2 et 10 brigades candidates ; POST par la
  pédagogique : 403
- architecture : aucune ligne écrite ou supprimée hors de la porte

Commit : `feat(planification): US-PLAN-06 regroupement de brigades`.

---

## Partie 3 — US-PLAN-09 : traiter une indisponibilité déclarée

| # | Critère | Source |
|---|---|---|
| C1 | La déclaration d'une indisponibilité liste immédiatement les séances affectées, toutes brigades confondues | backlog c.1 |
| C2 | Pour chaque séance : remplacer l'instructeur, substituer une autre matière, ou déprogrammer | backlog c.2, CU-P5-07 |
| C3 | Le remplacement ne propose que des instructeurs qualifiés et disponibles sur le créneau | backlog c.3, RG-35, RG-36 |
| C4 | La substitution place une autre matière du référentiel, dans le respect des prérequis et du volume | backlog c.4, A1 |
| C5 | Traitement en lot : même remplaçant pour toutes les séances de la même matière, confirmation globale | A3 |

**Arbitrages.**

**I1 — Aucune nouvelle voie d'écriture.** Les trois traitements sont des
opérations d'US-PLAN-05 : remplacer = `modifier_seance` (instructeur) ;
substituer = `modifier_seance` (matière, et instructeur si besoin) ;
déprogrammer = `supprimer_seance`. US-PLAN-09 est un **écran de traitement**
qui les orchestre, comme US-VAL-01 à 04 sur le circuit.

**I2 — Séances impactées.** Sélecteur : séances non commencées dont
l'instructeur est concerné et dont le créneau recoupe l'indisponibilité
(définition unique du recouvrement, `noyau/intervalles.py`), toutes
brigades, avec l'état de leur programme. Une requête. Affiché à
l'enregistrement de l'indisponibilité (C1) et consultable ensuite. Une
séance commencée n'y figure pas : elle relève de la non-exécution.

**I3 — CU-P5-07 A4 est obsolète, ETA-01 s'applique.** Séance d'un programme
**validé** : le traitement annonce qu'il faut d'abord annuler la validation
(T9, action d'US-PLAN-05) et y renvoie. Séance d'un programme **affiché** :
remplacement et substitution portent un **avenant** (natures
« remplacement d'instructeur », « changement de matière ») ; le programme
reste affiché ; la déprogrammation est refusée et renvoie à la
non-exécution. Soumis : renvoi au retrait de la soumission.

**I4 — Liste des remplaçants.** Instructeurs qualifiés pour la matière et
libres sur le créneau, ni indisponibles, ni en séance, ni surveillants d'une
épreuve sécante — sélecteurs existants, une requête par source pour toute la
liste. Ordre alphabétique : le classement de RG-43 dépend d'US-PLAN-08,
déclassée.

**I5 — Lot (A3).** Le lot ne contourne rien : chaque séance du lot passe
individuellement la garde et les contraintes, dans une seule transaction.
Si une seule échoue, rien n'est écrit, et le refus nomme la séance et la
contrainte.

**I6 — Reports refermés.** D-119 pts 4-5 (séances impactées) par C1 et
I2 ; D-119 A3/A4 (extension d'une indisponibilité, séances passées) :
l'extension relance la liste des séances impactées ; les séances passées
sont exclues (I2). Un test par volet.

**Tests attendus**
- service : liste des impactées sur deux brigades et trois états de
  programme ; séance commencée exclue ; remplacement admis ; remplaçant non
  qualifié ou occupé refusé par les contraintes ; substitution admise ;
  substitution violant un prérequis ou le volume refusée ; déprogrammation
  sur un brouillon ; lot admis ; lot avec une séance en conflit, rien
  d'écrit ; séance d'un validé, renvoi à T9 ; d'un affiché, avenant, programme
  toujours affiché ; déprogrammation sur un affiché refusée
- HTTP : enregistrement d'une indisponibilité, liste affichée dans la
  réponse ; POST de remplacement ; POST de lot ; liste des remplaçants sans
  instructeur non qualifié ; nombre de requêtes de la liste identique avec 1
  et 10 séances impactées ; POST par la pédagogique : 403

Commit : `feat(planification): US-PLAN-09 traitement d'une indisponibilité`.

---

## Suivi et rendu

Pour chaque partie : `DECISIONS.md`, reports refermés et recompte, écarts
(CU-P5-04 A2/A3 ; CU-P5-07 A4), définition de fini complète, relecture avant
chaque commit. Mesure des requêtes de génération après la partie 3, et
constante mise à jour avec note datée si elle bouge.

Rendu final, en français, en une fois : totaux de tests ; requêtes ;
décisions ; reports ouverts et fermés ; ce que tu as tranché seul ; ce que
tu n'as pas pu vérifier.
