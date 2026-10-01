# Prompt 35 — Sprint 3, US-EVAL-01 : Créer une évaluation selon son type

Phase 5, sprint 3. Story **US-EVAL-01** · 5 points · Must · BF-EVAL-01 ·
CU-P6-01 · RG-48, RG-52, RG-52 bis, RG-07 · CLS-05.
Deuxième élément de l'ordre retenu, après ETA-01 (commit `bb1e419`), pendant
l'attente de la validation des cellules.

**Ce que cette story n'est PAS : indépendante des séances.** Une évaluation
formative insère une séance verrouillée au programme (RG-52 bis). C'est
acceptable avant US-VAL-03 pour une seule raison : l'insertion passe par
`ServiceEcritureSeance`, la porte unique où US-VAL-03 posera la garde d'état
(D-170). Le jour où cette garde existe, l'insertion d'un contrôle en hérite
sans une ligne de code ici. Tout chemin d'écriture de séance qui contournerait
cette porte ruinerait ce raisonnement — c'est le point à ne pas rater.

Les arbitrages du § 2 sont RENDUS. Porte-les ; si le code réel en rend un
inexprimable, ARRÊTE-TOI et signale-le avant d'écrire la suite.

---

## 0. Vérifications préalables — lecture seule, AVANT toute écriture

Rends-moi le résultat de ces six points avant de coder. Deux d'entre eux sont
des conditions d'arrêt.

1. L'application `evaluations` existe-t-elle (modèles, services, tests,
   entrée dans l'ordre des couches de `tests/architecture/test_couches.py`) ?
   Si non, crée-la selon les conventions des applications existantes et
   inscris-la au-dessus de `planification`.
2. Le domaine d'habilitation des évaluations : nom exact, groupes qui le
   portent. Attendu, matrice § 11.2 : examens en écriture, Direction de
   Formation en lecture, tous les autres refusés. N'invente aucun nom.
3. **`ServiceEcritureSeance` : son contrôle d'habilitation.** S'il exige
   lui-même une permission de la cellule planification, l'appel depuis
   l'application `evaluations` échouera pour la cellule examens. **Condition
   d'arrêt** : ne le contourne pas, ne duplique pas la porte — rends-moi le
   code et j'arbitre.
4. `ServiceEcritureSeance` accepte-t-il de créer une séance verrouillée ?
   Expose-t-il une suppression de séance ?
5. **La régénération (D-147) préserve-t-elle les séances verrouillées ?**
   Attendu : oui (badge « N séance(s) verrouillée(s) », D-159). **Condition
   d'arrêt** si non : un contrôle serait effacé à la génération suivante,
   contre CU-P6-01 A1.
6. Les champs de bornes de `Session` (noms exacts).

---

## 1. Le besoin

*En tant que membre de la cellule examens, je veux créer une évaluation
rattachée à un module du référentiel en précisant son type et son périmètre,
afin que le circuit approprié lui soit appliqué.*

### Critères d'acceptation — version arbitrée

Le backlog v9 porte ici des critères contradictoires entre eux : le critère 1
propose TROIS types (contrôle simple, partiel, final), le critère 2 en pose
DEUX. La correction de terrain du 25 août (partiel = contrôle = formative ;
final = certificative) a été ajoutée en v7 sans que les anciens critères
soient retirés. Tu implantes la liste ci-dessous, qui suit CU-P6-01 et
BF-EVAL-01 (cahier des charges v8) — principe 1, et le critère 2 lui-même.

| # | Critère | Source |
|---|---|---|
| C1 | Deux types : **formative** (contrôle, examen partiel) et **certificative** (examen final). Aucun troisième | BF-EVAL-01, RG-48, US-EVAL-01 c.2 |
| C2 | Une évaluation porte sur **un seul élément du référentiel** (module) de la formation concernée ; un module hors référentiel est refusé | RG-52, CU-P6-01 E1 |
| C3 | Périmètre explicite : **exactement un** rattachement, session ou brigade ; contrainte portée en base | RG-52, US-EVAL-01 c.3 |
| C4 | Périmètre par défaut : brigade pour la formative, session pour la certificative ; modifiable avant enregistrement | US-EVAL-01 c.5 |
| C5 | Formative à date présente ou future : une **séance verrouillée** est insérée au programme de la semaine et rattachée à l'évaluation | RG-52 bis, CU-P6-01 A1 |
| C6 | Formative à date passée : admise **par exception, avec motif obligatoire** ; aucune séance insérée | CU-P6-01 A2, BF-EVAL-01 |
| C7 | Certificative : date obligatoire, ni passée, ni séance | RG-49, RG-52 bis |
| C8 | La date tombe dans les bornes de la session | CU-P6-01 étape 5 |
| C9 | Périmètre session : avertissement non bloquant sur l'écart de progression possible entre brigades | CU-P6-01 E2 (forme simplifiée, A8) |
| C10 | Le détail d'une évaluation présente les actions disponibles selon son type | US-EVAL-01 c.9 |
| C11 | La séance d'un contrôle est signalée comme telle dans le programme | CU-P6-01 A1 (« la pédagogique en est notifiée ») |

---

## 2. Arbitrages rendus

**A1 — Le périmètre n'est pas stocké.** CLS-05 porte un attribut
`perimetre : PerimetreEvaluation` EN PLUS des deux rattachements. Il se déduit
de celui des deux qui est renseigné : le stocker, c'est un attribut dérivé,
contraire à la règle tenue depuis le sprint 1. Propriété calculée ; un test
constate l'absence de la colonne. Écart au diagramme de classes.

**A2 — La date OU la séance, jamais les deux.** Pour une formative avec
séance, la date EST celle de la séance ; la recopier dans l'évaluation, c'est
deux vérités qui divergeront au premier déplacement de séance. `date` n'est
renseignée que sans séance (certificative, formative déclarée après coup) ;
avec séance, elle se lit sur la séance. Contrainte en base : exactement un des
deux.

**A3 — Formative future : séance insérée par la porte unique.** Le service
d'évaluation vérifie l'habilitation de la cellule examens, puis demande à
`ServiceEcritureSeance` une séance **verrouillée** : élément du référentiel de
l'évaluation, instructeur, créneau de la grille active à la date choisie,
lieu, une ligne de programme par brigade du périmètre. Programme de la semaine
créé à l'état brouillon s'il n'existe pas (T1 d'ETA-01, même `get_or_create`
que D-146). Les six contraintes dures s'appliquent sans exception : un
créneau occupé est **refusé** avec le motif de `ServiceContraintes` (E3 de la
fiche). Périmètre session : une séance regroupée, une ligne par brigade, lieu
de capacité suffisante — ce que `ServiceContraintes` sait déjà vérifier
(D-135, D-139). Séance et évaluation dans une même transaction : l'échec de
l'une annule l'autre.

**A4 — Le contrôle compte au volume programmé du module.** C'est une séance du
module : RG-39 a) la compte comme les autres. Conforme au terrain (« pendant
ses créneaux ») et au précédent du projet de fin d'études, compté à chaque
apparition. Question ajoutée au terrain, sans blocage.

**A5 — Formative à date passée : aucune séance.** La semaine passée est, en
régime normal, affichée : ETA-01 y refuse tout ajout hors avenant. Insérer une
séance dans le passé serait donc inexprimable sur le modèle (principe 3). Le
contrôle déclaré après coup s'est tenu dans un créneau existant de
l'instructeur ; l'évaluation porte sa date et son motif, sans séance.

**A6 — L'instructeur et le lieu se choisissent sans ouvrir le domaine des
instructeurs.** La cellule examens n'a aucun accès au domaine
`instructeurs_qualifications` (D-38, test
`test_cellule_examens_n_a_aucun_acces_ni_lecture_ni_ecriture`, qui DOIT
rester vert). Choisir un instructeur dans une liste d'instructeurs qualifiés
pour le module n'est pas consulter ce domaine : la liste est exposée par un
sélecteur de `planification` (P6 dépend de P5), réduite au nom et au grade.
Même chose pour les lieux. Pas de fiche, pas de qualification affichée.

**A7 — Type et périmètre immuables après création.** Changer le type change
le circuit (sujets, organisation, séance) ; changer le périmètre change le
sujet (RG-52). Une erreur se corrige par suppression et recréation.
**Suppression** : implantée ICI seulement si `ServiceEcritureSeance` expose
déjà une suppression de séance (vérification 0.4) ; sinon reportée à
US-PLAN-05, qui apporte la suppression manuelle — et tu le signales. Jamais de
`.delete()` direct sur une séance hors de la porte.

**A8 — E2 sous forme simplifiée.** La fiche avertit quand « les progressions
des brigades sont trop décalées », sans définir la mesure ni le seuil.
Avertissement systématique, non bloquant, sur tout périmètre session,
rappelant que le sujet sera commun. La mesure précise est un report sans
story, à arbitrer au backlog v10.

**A9 — La signalisation du contrôle passe par `noyau`.** `planification` ne
peut pas importer `evaluations`. Le programme sait qu'une séance est un
contrôle par un point de résolution dans `noyau`, dont `evaluations` installe
le fournisseur au `ready()` — le patron de D-128 et D-143. Une seule requête
pour toutes les séances affichées, pas une par séance. C'est la
« notification » de la cellule pédagogique : elle voit le contrôle dans le
programme, qu'elle lira grâce à D-172. Aucun autre mécanisme.

**A10 — US-EVAL-02 garde la date certificative.** Ici, la certificative reçoit
sa date à la création. Son marquage « imposée par une autorité externe », le
blocage du calendrier, la détection des conflits et le report de date (A4 de
la fiche) sont US-EVAL-02, story suivante — pas un report.

---

## 3. Modèle et contraintes en base

`Evaluation` (application `evaluations`), sur la classe de base horodatée :

| Champ | Type | Suppression de la cible |
|---|---|---|
| `element_referentiel` | FK `ElementReferentiel` | `PROTECT` — referme D-35 volet évaluation |
| `session` | FK `Session`, nulle | `PROTECT` |
| `brigade` | FK `Brigade`, nulle | `PROTECT` |
| `type` | choix FORMATIVE / CERTIFICATIVE | — |
| `date` | date, nulle | — |
| `seance` | OneToOne `planification.Seance`, nulle | `PROTECT` |
| `motif_date_passee` | texte, vide par défaut | — |

Aucun champ `perimetre`, aucune copie de la date de séance, aucune copie de
la formation (elle se lit par l'élément du référentiel).

| Contrainte | Règle | Contenu |
|---|---|---|
| `ck_evaluation_type_connu` | RG-48 | type parmi les deux valeurs |
| `ck_evaluation_perimetre_exclusif` | RG-52, C3 | exactement un de `session`, `brigade` non nul |
| `ck_evaluation_date_ou_seance` | A2 | exactement un de `date`, `seance` non nul |
| `ck_evaluation_certificative_sans_seance` | RG-52 bis | type CERTIFICATIVE ⇒ `seance` nulle |
| `ck_evaluation_motif_formative` | C6 | `motif_date_passee` non vide ⇒ type FORMATIVE et `seance` nulle |

Hors base, faute d'expression immuable : « date passée ⇒ motif » (dépend du
jour courant), « élément du référentiel de la formation de la session ou de la
brigade » (inter-tables). Couche services, testés.

---

## 4. Fichiers

- `app/evaluations/models.py`, migration
- `app/evaluations/services/evaluation.py` — `ServiceEvaluation.creer`, `actions_disponibles`
- `app/evaluations/forms.py`, `views.py`, `urls.py`, gabarits liste / création / détail, sur le patron de gestion existant
- `app/planification/selectors.py` — instructeurs qualifiés et lieux pour un créneau (A6)
- `app/noyau/…` — point de résolution « séances de contrôle » (A9) ; fournisseur installé dans `evaluations.apps`
- gabarit de consultation du programme — marque « Contrôle » sur la séance
- `app/evaluations/tests/…`

---

## 5. Cas de test attendus

**A — Base** (écriture directe, `IntegrityError` attendue)
- A1 les deux rattachements renseignés ; A2 aucun des deux
- A3 date ET séance ; A4 ni date ni séance
- A5 certificative portant une séance
- A6 motif renseigné sur une certificative ; A7 motif renseigné sur une formative avec séance
- A8 absence de colonne `perimetre` et de toute colonne de date sur la séance recopiée (constat du schéma)

**B — Règles du service**
- B1 module hors du référentiel de la formation → refus (E1)
- B2 date hors des bornes de la session → refus
- B3 certificative à date passée → refus
- B4 formative à date passée sans motif, puis avec motif blanc → refus ; avec motif → créée, sans séance
- B5 périmètre par défaut selon le type (C4) ; périmètre session → avertissement retourné (C9)
- B6 `actions_disponibles` diffère selon le type (C10)
- B7 type et périmètre non modifiables (A7)

**C — Insertion de la séance**
- C1 formative future, brigade : séance créée, verrouillée, une ligne, rattachée ; programme créé en brouillon s'il n'existait pas
- C2 formative future, session à trois brigades : une séance, trois lignes
- C3 instructeur déjà en séance sur le créneau → refus avec le motif RG-34, **aucune évaluation créée**, aucune séance
- C4 créneau sur période bloquante → refus (RG-38)
- C5 lieu de capacité insuffisante pour la session → refus (RG-37)
- C6 volume du module déjà atteint → refus (RG-39 a, A4)
- C7 **régénération** de la brigade après création du contrôle : la séance du contrôle est intacte
- C8 échec forcé de la création de l'évaluation après écriture de la séance : aucune séance orpheline

**D — Habilitations**
- D1 examens crée ; D2 Direction de Formation lit, ne crée pas ; D3 planification, pédagogique, administrateur : refusés en lecture et en écriture
- D4 `test_cellule_examens_n_a_aucun_acces_ni_lecture_ni_ecriture` (D-38) toujours vert, relancé nommément

**E — Cycle HTTP réel**
- E1 POST de création d'une formative future par la cellule examens : redirection vers le détail, séance présente au programme de la semaine
- E2 GET de la consultation du programme : la séance porte la marque « Contrôle » ; nombre de requêtes identique avec 1 et 10 contrôles (A9)
- E3 POST d'une formative à date passée sans motif : formulaire réaffiché avec l'erreur, rien en base
- E4 POST d'un contrôle sur un créneau occupé : formulaire réaffiché avec le motif de la contrainte, rien en base
- E5 POST de création par la cellule planification : 403, rien en base
- E6 formulaire : aucun troisième type proposé

**F — Architecture**
- F1 `evaluations` n'écrit aucune `Seance`/`LigneProgramme` hors de `ServiceEcritureSeance` (le test de D-142 le couvre déjà : vérifie qu'il scanne bien `evaluations`)
- F2 `planification` n'importe pas `evaluations`

**G — Reports refermés** (par le vrai chemin de service, leçon D-83)
- G1 D-35 volet évaluation : `ServiceReferentiel.retirer` d'un élément porteur d'une évaluation → refusé, évaluation énumérée parmi les opposants
- G2 `ServiceBrigade.supprimer` d'une brigade porteuse d'une évaluation → refusé
- G3 suppression d'une session porteuse d'une évaluation → refusée par son service

---

## 6. Suivi

**`DECISIONS.md`** — une entrée par arbitrage A1 à A9 (A10 est une frontière
de story, une ligne dans l'entrée d'A3 suffit), « imposée par le prompt 35 »,
à partir de D-174.

**Reports** (tableau d'`AVANCEMENT.md`, recompte à la fin) :
- D-35 volet évaluation → **Fermé**, test G1
- NOUVEAU — mesure de l'écart de progression (A8, E2) → **Ouvert, orphelin**, à arbitrer au backlog v10
- NOUVEAU — une séance portant une évaluation ne doit pas pouvoir être déverrouillée ni supprimée hors du service d'évaluation → US-PLAN-05
- NOUVEAU — l'insertion d'un contrôle dans un programme SOUMIS, VALIDÉ ou AFFICHÉ est refusée → cas à ajouter à l'oracle d'US-VAL-03 (`ETA-01_table_transitions.md`)
- NOUVEAU, seulement si la vérification 0.4 est négative — suppression d'une évaluation → US-PLAN-05

**`ECARTS-LIVRABLES-SPRINT-3.md`** — à la suite :
- backlog v9, US-EVAL-01 c.1, 6, 7, 8 : trois types, alors que c.2 en pose deux — correction v7 ajoutée sans retrait des anciens critères
- CLS-05 : attribut `perimetre` stocké (A1) ; attribut `date` sans exclusivité avec la séance (A2)
- Objectifs SMART, OS3 : « trois circuits » d'évaluation

**Questions de terrain** (section d'`AVANCEMENT.md`) — deux ajouts :
- un contrôle se tient-il sur un créneau libre, ou à la place d'une séance déjà programmée du module ? *Retenu : créneau libre (fiche CU-P6-01)*
- la séance d'un contrôle compte-t-elle au volume horaire du module ? *Retenu : oui (A4)*

**Définition de fini (mesure de R23)** — à la clôture : case cochée dans
`sprint-3.md`, ligne au tableau des sprints d'`AVANCEMENT.md`, ligne datée
dans `heures-sprint-3.md` (début et fin de ta session ; heures humaines à
saisir par l'étudiant le jour même).

---

## 7. Avant de conclure

1. `pytest` complet et `pytest tests/architecture -q` ; donne les deux totaux
   et l'écart avec 1 432.
2. Relecture par `relecteur-conception` : conformité à CU-P6-01 et à CLS-05
   compte tenu des écarts A1 et A2, et cohérence des reports.
3. Un commit : `feat(evaluations): US-EVAL-01 créer une évaluation selon son type`.
4. Rends-moi : les résultats du § 0, les totaux de tests, les reports
   ouverts et fermés avec le nouveau compte, et ce que tu n'as pas pu
   vérifier.
