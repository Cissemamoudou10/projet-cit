# Prompt 38 — Sprint 3, US-EVAL-04 : Organiser une épreuve

Phase 5, sprint 3. Story **US-EVAL-04** · 5 points · Must · BF-EVAL-04 ·
CU-P6-04 · RG-53, RG-53 bis, RG-37 · CLS-05.
Quatrième et dernière story du paquetage Évaluations au sprint 3, avant le
circuit de validation. Elle concentre trois reports : D-193 (revérifier
l'organisation quand la date change), D-202 (pas d'organisation sans sujet
retenu — **réinterprété ici, voir A1**), et le prédicat `sujet_retenu`
(D-205), à n'utiliser que comme garde.

C'est la story la plus lourde du paquetage : RG-53 lie dans les DEUX sens les
épreuves (P6) et les séances (P5). Les arbitrages sont RENDUS ; si le code
réel en rend un inexprimable, ARRÊTE-TOI et signale-le.

---

## 0. Vérifications préalables — lecture seule

Arrêt sur condition d'arrêt seulement ; sinon enchaîne.

1. `DEPENDANCES_AUTORISEES["evaluations"]` : `ressources` y figure-t-il, ou
   seulement `planification` ?
2. Les primitives de disponibilité existantes, que tu réutiliseras sans les
   réécrire : le test d'indisponibilité d'un lieu et d'un instructeur
   (`ressources`), l'occupation d'un lieu et d'un instructeur par des séances
   (`planification`), les fonctions de recouvrement d'intervalles
   (`_se_recouvrent`, `_portee_couvre`). Pour chacune : module, signature,
   nombre de requêtes.
3. Dans `ServiceContraintes`, les codes exacts des contraintes d'occupation
   d'un instructeur et d'un lieu par une autre séance, et l'endroit où leurs
   sources sont lues.
4. Le calcul de l'effectif réel d'une brigade (stagiaires non radiés) :
   fonction existante, jamais un champ.
5. Le badge « non prête » d'US-EVAL-03 (A11) : où il est calculé.
6. **Condition d'arrêt** : si vérifier la disponibilité d'un lieu ou d'un
   instructeur face aux séances exige de recopier la logique de
   `ServiceContraintes` au-delà d'un appel de sélecteur et d'un test de
   recouvrement, rends-moi le code. Deux implantations de RG-53 seraient la
   duplication interdite.

---

## 1. Le besoin

*En tant que membre de la cellule examens, je veux organiser matériellement
une épreuve, afin qu'elle se déroule dans de bonnes conditions.*

| # | Critère | Source |
|---|---|---|
| C1 | L'organisation porte sur une évaluation **certificative** datée : un créneau horaire dans sa date, puis, par brigade du périmètre, un ou plusieurs lieux avec effectif attendu et surveillants | BF-EVAL-04, RG-53 bis, CU-P6-04 |
| C2 | Un même créneau pour toutes les brigades : l'épreuve est simultanée | RG-53 bis |
| C3 | Un lieu est disponible sur le créneau (ni indisponibilité, ni séance, ni autre épreuve) et de capacité suffisante ; sinon refus désignant l'occupant ou l'écart de capacité | RG-53, RG-37, E1, E3 |
| C4 | Un surveillant est un instructeur référencé, OU une personne extérieure désignée par son seul nom | BF-EVAL-04, CLS-05 |
| C5 | Seul le surveillant référencé est contrôlé : indisponibilité, séance, autre surveillance sur un créneau sécant ; refus sinon | RG-53, E2 |
| C6 | Une épreuve pratique peut se tenir sans lieu ; ses surveillants restent obligatoires | A2 |
| C7 | Modification admise jusqu'au début de l'épreuve, refusée ensuite | A3 |
| C8 | Une séance ne peut plus occuper un lieu ou un instructeur pris par une épreuve | RG-53, sens inverse |
| C9 | Une convocation récapitulative est consultable et imprimable, **sans aucune mention de sujet** | US-EVAL-04 c.5, RG-51 |
| C10 | L'épreuve est « prête » quand son organisation est complète ET son sujet retenu | A1 |
| C11 | Un changement de date d'examen revérifie l'organisation existante et signale ses conflits | D-193 |

---

## 2. Arbitrages rendus

**A1 — D-202 réinterprété : on organise sans sujet, on n'est « prêt »
qu'avec.** Le backlog (US-EVAL-03 c.7) interdit d'organiser une évaluation
sans sujet retenu. Appliqué à la lettre, il force la commission à choisir le
sujet dès que les salles sont réservées, c'est-à-dire des jours ou des
semaines plus tôt : la fenêtre de divulgation s'élargit, contre l'objet même
de RG-50 et RG-51. La fiche CU-P6-04, plus précise, ne pose en précondition
qu'une évaluation datée. Principe 2 (la règle structurante l'emporte) et
principe 1 (la fiche précise l'emporte). Retenu : l'organisation se prépare
sans sujet ; l'épreuve n'est **prête** (C10) qu'avec un sujet retenu.
`sujet_retenu` sert de garde booléenne au calcul de « prête », jamais
d'affichage. D-202 se referme ainsi ; écart au backlog à corriger en v10.

**A2 — Le créneau vit sur l'évaluation.** `heure_debut`, `heure_fin` sur
`Evaluation`, comme dans CLS-05 : un seul créneau pour toutes les
organisations, ce qui rend C2 vrai par construction et non par vérification.
Heures libres, non tirées de la grille horaire : un examen ne suit pas les
créneaux de cours. Réservé aux certificatives (la formative a sa séance).

**A3 — L'organisation est un triplet brigade — lieu — surveillants
(RG-53 bis), et une brigade peut en avoir plusieurs (A1 de la fiche).**
`effectif_attendu` est stocké, et ce n'est pas un dérivé : c'est la PART de
la brigade affectée à ce lieu, une décision de répartition. Ce qui est
dérivé, et donc jamais stocké : l'effectif réel de la brigade, et la
complétude.

**A4 — Complète, et prête, sont calculées.** Complète : chaque brigade du
périmètre (résolu au moment de la lecture, comme à US-EVAL-02) a au moins
une organisation ; la somme de ses effectifs attendus égale son effectif
réel ; chaque organisation a au moins un surveillant ; le créneau existe.
Prête : complète et sujet retenu. Une radiation de stagiaire rend une
organisation incomplète sans qu'aucun champ ne bouge — c'est le but.
L'organisation se saisit par étapes, brigade par brigade : un état
incomplet est un état légitime, pas une erreur. Le badge d'US-EVAL-03
devient ce calcul, toujours en une requête bornée pour toute la liste.

**A5 — RG-53 dans le sens P6 → P5 : `evaluations` interroge, ne
recalcule pas.** Pour un lieu ou un surveillant référencé sur le créneau :
indisponibilité (primitive de `ressources`), séances (sélecteur de
`planification`), autres épreuves (`evaluations` même). Les trois sources
sont lues en un nombre constant de requêtes pour toute l'organisation, pas
par lieu ni par surveillant.

**A6 — RG-53 dans le sens P5 → P6 : deux sources de plus, pas de nouvelle
contrainte.** Sans cela, une génération lancée après l'organisation place une
séance dans la salle d'examen. Point de résolution `occupations_epreuves(
debut, fin)` dans `noyau`, fournisseur installé par `evaluations` — le patron
de `jours_d_examen` (US-EVAL-02). Il nourrit les deux contraintes
d'occupation identifiées au § 0.3 : un lieu ou un instructeur pris par une
épreuve est occupé, comme s'il l'était par une séance. **Les contraintes
dures restent six.** Coût constant (A8 du prompt 36) : si le nombre de
requêtes de référence passe de 43 à 44 ou 45, mets à jour
`REQUETES_REFERENCE_US_PLAN_03` avec une note datée — ne consomme pas la
marge en silence.

**A7 — Surveillant : exactement une des deux natures, garanti en base.**
`Surveillance.instructeur` ou `Surveillance.nom_libre`, jamais les deux,
jamais aucun. Un nom libre n'est soumis à aucun contrôle de disponibilité
(C5) : le système ne vérifie pas ce qu'il ne connaît pas (CLS-05 § 7.5). Un
même instructeur ne surveille pas deux salles de la même épreuve : refus en
service, le créneau étant commun.

**A8 — Le choix des surveillants n'ouvre pas le domaine des instructeurs.**
Même solution qu'à US-EVAL-01 (A6) : un sélecteur réduit au nom et au grade,
ici de TOUS les instructeurs (un surveillant n'a pas à être qualifié), avec
leur disponibilité sur le créneau. Le test de D-38 reste vert.

**A9 — Le changement de date ne se refuse pas, il se signale (D-193).** La
date est subie (RG-49) : `modifier_date_certificative` ne peut pas la
refuser parce que l'organisation gêne. Elle garde les heures et les
organisations, revérifie chaque lieu et chaque surveillant sur la nouvelle
date (A5), et rend les conflits à l'agent comme un avertissement. L'épreuve
n'est plus « prête » tant qu'un conflit subsiste : la complétude (A4)
intègre l'absence de conflit, calculée au détail de l'évaluation. Dans la
liste, le badge reste à une requête : il ne recalcule pas les conflits, il
porte la mention « à vérifier » pour toute épreuve dont la date a changé
après sa dernière organisation (lisible dans le journal, sans champ ajouté —
si ce n'est pas faisable en une requête, dis-le et propose).

**A10 — Le gel au début de l'épreuve.** Maintenant que l'heure existe, la
borne de C7 est `date + heure_debut` : toute modification de l'organisation
est refusée à partir de cet instant. La borne d'US-EVAL-03 pour le sujet
(le jour de l'épreuve, A9 du prompt 37) ne change pas : elle reste plus
stricte, à dessein.

**A11 — La convocation ne connaît pas le sujet.** Une page imprimable, sur
la charte d'impression : évaluation (module, type), date, créneau, et par
brigade, lieu, effectif attendu, surveillants. Aucun appel aux sujets, pas
même `sujet_retenu` : la convocation peut circuler. Lisible par la Direction
de Formation (`evaluations_lecture`). Mesure de hauteur comme pour les autres
écrans, ajoutée à `IMPRESSION-ANALYSE.md`.

---

## 3. Modèle et contraintes en base

`Evaluation` — deux champs ajoutés :

| Champ | Type |
|---|---|
| `heure_debut` | heure, nulle |
| `heure_fin` | heure, nulle |

`OrganisationEpreuve` (horodatée) : `evaluation` (FK, `CASCADE`), `brigade`
(FK, `PROTECT`), `lieu` (FK nulle, `PROTECT`), `effectif_attendu` (entier).

`Surveillance` (horodatée) : `organisation` (FK, `CASCADE`), `instructeur`
(FK nulle, `PROTECT`), `nom_libre` (texte, vide par défaut).

| Contrainte | Règle | Contenu |
|---|---|---|
| `ck_evaluation_creneau_complet` | A2 | `heure_debut` et `heure_fin` toutes deux renseignées ou toutes deux nulles |
| `ck_evaluation_creneau_ordonne` | A2 | `heure_fin` > `heure_debut` |
| `ck_evaluation_creneau_certificative` | A2 | heures renseignées ⇒ type CERTIFICATIVE |
| `ck_organisation_effectif_positif` | A3 | `effectif_attendu` > 0 |
| `uq_organisation_lieu_par_epreuve` | RG-53 bis | (évaluation, lieu) unique, lieu non nul : une salle par brigade, jamais partagée dans la même épreuve |
| `ck_surveillance_une_nature` | A7, C4 | exactement un de `instructeur` non nul, `nom_libre` non vide après suppression des blancs |
| `uq_surveillance_instructeur` | A7 | (organisation, instructeur) unique, instructeur non nul |
| `uq_surveillance_nom_libre` | A7 | (organisation, nom libre) unique, insensible à la casse, nom non vide |

Hors base, inter-tables ou dépendant du temps : brigade du périmètre,
capacité, disponibilités (A5), instructeur dans deux salles de la même
épreuve, au moins un surveillant par organisation, gel (A10). Services,
testés.

---

## 4. Fichiers

- `app/evaluations/models.py`, migration
- `app/evaluations/services/organisation.py` — `ServiceOrganisationEpreuve` : `fixer_creneau`, `ajouter_organisation`, `modifier_organisation`, `retirer_organisation`, `ajouter_surveillant`, `retirer_surveillant`, `verifier` (conflits), `est_complete`, `est_prete`
- `app/evaluations/services/evaluation.py` — `modifier_date_certificative` étendu (A9)
- `app/evaluations/apps.py` — fournisseur `occupations_epreuves`
- `app/noyau/…` — point de résolution `occupations_epreuves`
- `app/planification/services/contraintes.py` (ou le module des sources) — deux sources ajoutées (A6)
- `app/planification/selectors.py` et/ou `ressources` — sélecteur des instructeurs disponibles (A8)
- vues, formulaires, gabarits : organisation par brigade, convocation imprimable
- tests

---

## 5. Cas de test attendus

**A — Base**
- A1 une heure sans l'autre ; A2 fin ≤ début ; A3 heures sur une formative → `IntegrityError`
- A4 effectif nul ou négatif → `IntegrityError`
- A5 même lieu pour deux brigades de la même épreuve → `IntegrityError`
- A6 surveillance sans instructeur ni nom ; avec les deux ; nom fait de blancs → `IntegrityError`
- A7 même instructeur deux fois dans une organisation ; même nom libre à la casse près → `IntegrityError`

**B — Règles et complétude**
- B1 organisation d'une formative → refus
- B2 créneau fixé sur une épreuve dont la date est passée → refus
- B3 brigade hors du périmètre → refus
- B4 capacité du lieu < effectif attendu → refus énonçant l'écart (E3)
- B5 épreuve pratique sans lieu, un surveillant → admise (C6)
- B6 complétude : périmètre session à trois brigades ; deux organisées → incomplète ; la troisième → complète ; une radiation dans une brigade → incomplète sans aucune écriture (A4)
- B7 brigade répartie sur deux salles dont la somme égale l'effectif réel → complète ; somme différente → incomplète
- B8 organisation sans surveillant → incomplète
- B9 complète sans sujet retenu → non prête ; avec sujet retenu → prête (A1)
- B10 modification à `date + heure_debut` et après → refus ; une minute avant → admise (A10)

**C — Disponibilité, sens P6 → P5 (A5)**
- C1 lieu en indisponibilité sur le créneau → refus nommant l'indisponibilité
- C2 lieu occupé par une séance sécante → refus nommant la séance (E1)
- C3 lieu occupé par une autre épreuve sécante → refus nommant l'épreuve
- C4 surveillant référencé en indisponibilité ; en séance ; surveillant d'une autre épreuve sécante → trois refus (E2)
- C5 surveillant extérieur au même créneau qu'une séance quelconque → admis, aucun contrôle (C5)
- C6 même instructeur sur deux salles de la même épreuve → refus (A7)
- C7 créneaux contigus, non sécants (bornes semi-ouvertes, D-116) → admis
- C8 nombre de requêtes de `verifier` identique pour 1 et 10 organisations

**D — Sens P5 → P6 (A6)**
- D1 après organisation, `ServiceContraintes` refuse une séance dans la salle d'examen sur un créneau sécant
- D2 même chose pour un instructeur surveillant
- D3 génération sur la semaine : aucune séance placée dans le lieu ni avec le surveillant pendant l'épreuve ; le reste rempli
- D4 point de résolution sans fournisseur : liste vide, contraintes fonctionnelles
- D5 H6 vert ; requêtes de `verifier_lot` identiques avec 0 et 10 épreuves ; mesure de référence et test P-38 verts, constante mise à jour si elle bouge

**E — Changement de date (A9, ferme D-193)**
- E1 date changée vers un jour où un lieu affecté est occupé : date enregistrée, conflit retourné, épreuve non prête
- E2 date changée vers un jour libre : aucun conflit, organisation intacte
- E3 la liste porte « à vérifier » après un changement de date postérieur à l'organisation

**F — Confidentialité et habilitations**
- F1 le HTML de la convocation ne contient ni référence ni rang de sujet ; aucun appel aux sujets dans le code de la vue (constat)
- F2 aucune entrée `CONSULTATION_SUJETS` créée par l'affichage de l'organisation ni de la convocation
- F3 Direction de Formation : convocation et organisation lisibles, toute action refusée en service ET en HTTP
- F4 planification, pédagogique, administrateur : refusés ; nouvelles vues dans `ECRANS_ECRITURE`
- F5 `test_cellule_examens_n_a_aucun_acces_ni_lecture_ni_ecriture` (D-38) vert, relancé nommément

**G — Cycle HTTP réel**
- G1 POST du créneau, puis d'une organisation par brigade, puis des surveillants par la cellule examens : détail affichant « complète », puis « prête » après la sélection du sujet
- G2 POST d'un lieu occupé : redirection avec message nommant l'occupant, rien en base
- G3 POST d'un surveillant indisponible : même chose
- G4 GET de la convocation par la Direction de Formation : 200, sans sujet
- G5 POST de modification après le début de l'épreuve : refus, rien en base
- G6 liste des épreuves à venir : nombre de requêtes identique avec 1 et 10 évaluations

---

## 6. Suivi

**`DECISIONS.md`** — une entrée par arbitrage A1 à A11, « imposée par le
prompt 38 », numérotée au moment de l'écrire.

**Reports** —
- D-202 → **Fermé** par A1 (réinterprété), tests B9 et G1
- D-193 → **Fermé**, tests E1 à E3
- nouveaux éventuels : à dire, avec leur story

**`ECARTS-LIVRABLES-SPRINT-3.md`** —
- backlog v9, US-EVAL-03 c.7 : « aucune évaluation ne peut être organisée sans sujet sélectionné » → l'épreuve n'est PRÊTE qu'avec un sujet retenu (A1)
- CLS-05 : `OrganisationEpreuve.effectifAttendu` lu comme une part de répartition, non comme l'effectif de la brigade (A3)
- dossier d'architecture : `ServiceRessources` (P4) devait porter la disponibilité commune ; elle est répartie entre primitives de `ressources`, sélecteurs de `planification` et deux points de résolution de `noyau` — à décrire tel qu'implanté
- RG-53 dans le tableau des contraintes de la phase 4 : sources « épreuve » ajoutées aux deux contraintes d'occupation, compte inchangé

**Définition de fini (R23)** — case cochée, ligne au tableau des sprints,
ligne d'heures (une date par jour réellement traversé ; si une pause de
limite d'usage survient, note son heure de début et de fin).

---

## 7. Avant de conclure

1. `pytest` complet et `pytest tests/architecture -q` : totaux et écart avec 1 571.
2. Relecture par `relecteur-conception` : A1 (aucun affichage de sujet hors
   de son écran), A5 et A6 (aucune seconde implantation de RG-53, six
   contraintes dures), puis chaque numéro de décision cité.
3. Commit : `feat(evaluations): US-EVAL-04 organiser une épreuve`.
4. Rendu en français, sans que je le redemande : § 0, totaux, mesures de
   requêtes avant et après, reports, ce que tu n'as pas pu vérifier.
