# Prompt 36 — Sprint 3, US-EVAL-02 : Saisir la date d'un examen final

Phase 5, sprint 3. Story **US-EVAL-02** · 2 points · Must · BF-EVAL-02 ·
CU-P6-02 · RG-49, RG-38 · CLS-05.
Troisième élément de l'ordre retenu, après US-EVAL-01 (`a6df84b`, clôture
`f5ecb2a`). ETA-01 toujours en attente des cellules.

Les arbitrages du § 2 sont RENDUS. Si le code réel en rend un inexprimable,
ARRÊTE-TOI et signale-le avant d'écrire la suite.

---

## 0. Vérifications préalables — lecture seule

Même règle qu'au prompt 35 : n'arrête-toi que sur une condition d'arrêt ;
sinon enchaîne, les résultats ouvriront ton rendu final.

1. Comment `ServiceContraintes` évalue RG-38 aujourd'hui : fonction,
   requête des périodes bloquantes, et comment la portée (sessions, brigades,
   centre entier) est résolue en brigades.
2. Le test H6 (`test_contrat_service.py`) et le test des mesures de référence
   (`test_generation_performance.py`) : affirment-ils un nombre EXACT de
   requêtes, ou une borne ? Cite l'assertion.
3. Les vues annuelle et mensuelle du calendrier : comment elles composent
   aujourd'hui les deux couches (périodes et bandes de session, D-124).
4. Le point de résolution posé par US-EVAL-01 pour les séances de contrôle
   (A9 du prompt 35) : son emplacement dans `noyau` et son patron
   d'installation, que tu réutiliseras.
5. Le mécanisme de journal : comment une modification avec motif est
   consignée ailleurs dans le projet, et si une nature existante convient.
6. **Condition d'arrêt** : si RG-38 est évaluée ailleurs que dans
   `ServiceContraintes` (par exemple recalculée dans la génération), rends-moi
   le code. Une seconde implantation de RG-38 serait la duplication
   qu'interdit la note d'implémentation.

---

## 1. Le besoin

*En tant que membre de la cellule examens, je veux enregistrer la date
d'examen final fixée par le 3ᵉ bureau, afin qu'elle s'impose au calendrier.*

| # | Critère | Source |
|---|---|---|
| C1 | La date d'une évaluation certificative est identifiée comme **imposée par une autorité externe** (3ᵉ bureau) partout où elle s'affiche | US-EVAL-02 c.1, RG-49 |
| C2 | Seule la cellule examens la modifie ; toute modification exige un **motif** mentionnant la notification du 3ᵉ bureau, et est journalisée avec l'ancienne et la nouvelle date | US-EVAL-02 c.2, CU-P6-02, CU-P6-01 A4 |
| C3 | Le système ne propose ni ne conteste l'opportunité de la date : il la subit | RG-49, CU-P6-02 |
| C4 | Le jour de l'examen est **fermé à la programmation** pour les brigades du périmètre : la génération n'y place aucune séance, la saisie manuelle y est refusée | US-EVAL-02 c.3, RG-38, RG-52 bis |
| C5 | Les séances **déjà programmées** sur ce jour pour ces brigades sont **énumérées** à la saisie et à chaque modification de la date — signalées, jamais supprimées | US-EVAL-02 c.4 |
| C6 | La date d'examen apparaît sur les vues annuelle et mensuelle du calendrier | US-EVAL-02 c.3 |

---

## 2. Arbitrages rendus

**A1 — Projection, jamais copie.** « Bloquer le créneau au calendrier » ne
crée AUCUNE `PeriodeCalendrier`. Créer une période à partir de l'évaluation,
c'est enregistrer la même date à deux endroits, qui divergent au premier
report du 3ᵉ bureau — exactement le défaut que RG-30 bis interdit pour les
dates de session, et que D-124 a résolu par projection. Même solution : la
date certificative est **projetée** sur le calendrier et sur RG-38, depuis
`Evaluation`, seule source.

**A2 — Un point de résolution, deux consommateurs.** `planification`
(RG-38) et `ressources` (vues du calendrier) ne peuvent pas importer
`evaluations`. Un point de résolution dans `noyau`, fournisseur installé par
`evaluations` au `ready()`, sur le patron de celui posé à US-EVAL-01 :
`jours_d_examen(debut, fin)` rend, pour un intervalle, les couples (jour,
brigades fermées) avec un libellé. **Une seule requête par appel**, quel que
soit le nombre d'évaluations. Sans fournisseur installé, il rend une liste
vide — `planification` et `ressources` restent testables seules.

**A3 — RG-38 gagne une source ; les six contraintes restent six.** Un
créneau est ouvert s'il n'est couvert ni par une période bloquante dont la
portée couvre la brigade, **ni par un jour d'examen certificatif dont le
périmètre la couvre**. C'est une source de plus pour RG-38, pas une septième
contrainte dure — le même raisonnement que les trois sources de RG-07 (D-35).
Le compte « six contraintes dures » de l'écart 14 du sprint 2 ne bouge pas.
Le jour entier est fermé : l'heure de l'épreuve n'existe qu'avec
l'organisation (US-EVAL-04).

**A4 — Le périmètre se résout au moment de la lecture.** Périmètre brigade :
cette brigade. Périmètre session : les brigades de la session **au moment de
l'appel**, jamais une liste recopiée — une brigade constituée après la saisie
de la date est fermée elle aussi.

**A5 — « Imposée par une autorité externe » n'est pas un champ.** Toute date
certificative l'est, par RG-49 : c'est une propriété du type. Un booléen
stocké serait un attribut dérivé du type. Libellé affiché « Date imposée —
3ᵉ bureau », calculé.

**A6 — Modification : bornes et gel.** La nouvelle date reste dans les bornes
de la session (`date_debut`, `date_fin`), n'est pas passée, et la date
actuelle non plus : un examen déjà tenu ne change plus de date. Seules les
évaluations **certificatives** se modifient ici. La date d'une formative avec
séance se déplace avec sa séance (US-PLAN-05) ; celle d'une formative
déclarée après coup est figée. Refus explicites, testés.

**A7 — Le signalement de C5 est un sélecteur réutilisable.**
`planification.selectors.seances_recouvertes(brigades, debut, fin)` rend les
séances concernées avec leur programme et son état. Il servira à refermer
D-121 E2 (période bloquante recouvrant des séances) à US-PLAN-05 ; D-121 E2
**reste ouvert** ici, faute de l'arbitrage explicite qu'il exige. Le
signalement est rendu à l'agent comme un avertissement : la date est
enregistrée quoi qu'il arrive (C3).

**A8 — Mesures de référence : aucune dérive silencieuse.** Si la nouvelle
source de RG-38 ajoute une requête au contrôle des contraintes et à la
génération, cet ajout doit être **constant**, indépendant du nombre de
séances et du nombre d'examens. Si une assertion fige un nombre exact, mets-la
à jour avec la nouvelle valeur ET une note datée dans
`MESURES-REFERENCE.md` — jamais en relâchant l'assertion en une borne vague.

---

## 3. Modèle et contraintes en base

**Aucun champ ajouté à `Evaluation`, aucune migration attendue.** La date
existe depuis US-EVAL-01 ; le motif de modification va au journal, qui en
tient lieu d'historique (précédent D-132). Si tu juges une migration
nécessaire, c'est un écart au présent prompt : arrête-toi et justifie.

Les contraintes de US-EVAL-01 couvrent déjà l'essentiel : la certificative
porte une date et jamais de séance (`ck_evaluation_date_ou_seance`,
`ck_evaluation_certificative_sans_seance`). Rien à ajouter en base pour cette
story : le gel de la date passée dépend du jour courant, inexprimable en
CHECK — couche services, testé.

---

## 4. Fichiers

- `app/evaluations/services/evaluation.py` — `ServiceEvaluation.modifier_date_certificative(agissant, evaluation, nouvelle_date, motif)` ; signalement à la création d'une certificative
- `app/evaluations/apps.py` — installation du fournisseur `jours_d_examen`
- `app/noyau/…` — point de résolution `jours_d_examen`
- `app/planification/services/contraintes.py` (ou le module où vit RG-38) — nouvelle source
- `app/planification/selectors.py` — `seances_recouvertes`
- vues annuelle et mensuelle du calendrier (`ressources`) — troisième couche affichée
- formulaire, vue, gabarit de modification de la date ; détail de l'évaluation : libellé « imposée », action « Modifier la date » pour une certificative non échue
- tests

---

## 5. Cas de test attendus

**A — Projection et RG-38**
- A1 certificative, périmètre brigade, à J : `ServiceContraintes` refuse une candidate de cette brigade à J, motif RG-38 nommant l'examen
- A2 même jour, autre brigade de la même session : acceptée
- A3 périmètre session : toutes les brigades de la session fermées à J, aucune autre
- A4 brigade constituée dans la session APRÈS la saisie de la date : fermée elle aussi (A4)
- A5 génération sur la semaine de J : aucune séance des brigades du périmètre à J ; les autres jours remplis normalement
- A6 modification de la date de J à J' : J rouvert, J' fermé, sans autre écriture qu'en `Evaluation` et au journal
- A7 aucune `PeriodeCalendrier` créée par la saisie ni par la modification (A1)
- A8 point de résolution sans fournisseur : liste vide, `ServiceContraintes` fonctionne

**B — Modification de la date**
- B1 examens modifie avec motif : date changée, entrée de journal portant ancienne date, nouvelle date, motif, auteur
- B2 motif vide puis blanc → refus, date inchangée
- B3 nouvelle date hors des bornes de la session → refus
- B4 nouvelle date passée → refus ; date actuelle passée (examen échu) → refus
- B5 formative avec séance → refus nommant US-PLAN-05 ; formative déclarée après coup → refus
- B6 le libellé « Date imposée — 3ᵉ bureau » est calculé sans champ stocké (constat du schéma)

**C — Signalement des séances recouvertes**
- C1 création d'une certificative à J alors que deux séances de la brigade existent à J : enregistrée, les deux séances énumérées avec l'état de leur programme
- C2 aucune séance supprimée ni modifiée (compte avant/après)
- C3 modification de la date vers un jour occupé : même signalement
- C4 séance d'une brigade hors périmètre à J : non énumérée

**D — Habilitations**
- D1 Direction de Formation, planification, pédagogique : modification refusée
- D2 la nouvelle vue entre dans `ECRANS_ECRITURE` ; les refus paramétrés passent

**E — Cycle HTTP réel**
- E1 POST de modification par la cellule examens : redirection vers le détail, nouvelle date affichée avec le libellé « imposée »
- E2 POST sans motif : formulaire réaffiché avec l'erreur, date inchangée en base
- E3 POST de création d'une certificative sur un jour occupé : redirection, avertissement affiché énumérant les séances
- E4 GET de la vue annuelle et de la vue mensuelle : le jour d'examen apparaît ; nombre de requêtes identique avec 1 et 10 examens
- E5 POST de modification par la cellule planification : 403, date inchangée

**F — Mesures et architecture**
- F1 H6 toujours vert ; nombre de requêtes de `verifier_lot` identique avec 0 et 10 examens dans la semaine
- F2 test des mesures de référence d'US-PLAN-03 vert, nombre de requêtes constant (A8)
- F3 ni `planification` ni `ressources` n'importent `evaluations`

---

## 6. Suivi

**`DECISIONS.md`** — une entrée par arbitrage A1 à A8, « imposée par le
prompt 36 », à partir de D-185. Pour A3, dire explicitement que le compte des
contraintes dures reste six.

**Reports** — aucun fermé. D-121 E2 reste ouvert, avec la mention « sélecteur
`seances_recouvertes` posé à US-EVAL-02, l'arbitrage reste à US-PLAN-05 ».
Nouveau, si la vérification 0 le confirme : une organisation d'épreuve
(US-EVAL-04) devra être revérifiée quand la date de l'évaluation change →
US-EVAL-04.

**`ECARTS-LIVRABLES-SPRINT-3.md`** — à la suite :
- RG-38 (fiche CU-P5-02 et récapitulatif) ne cite que les périodes du calendrier ; le jour d'examen certificatif en est une seconde source (A3)
- tableau des contraintes de la phase 4 : même ajout de source, compte inchangé

**Définition de fini (R23)** — case cochée dans `sprint-3.md` ; ligne au
tableau des sprints d'`AVANCEMENT.md` ; ligne dans `heures-sprint-3.md`,
**datée d'un seul jour** (celui de la session), début noté avant le § 0, fin
à l'heure du commit de clôture.

---

## 7. Avant de conclure

1. `pytest` complet et `pytest tests/architecture -q` : totaux et écart avec 1 482.
2. Relecture par `relecteur-conception` : A1 tenu (aucune période créée),
   A3 tenu (six contraintes dures), chaque décision citée existe.
3. Un commit : `feat(evaluations): US-EVAL-02 date d'examen final imposée et projetée`.
4. Rends-moi : résultats du § 0, totaux, mesures de requêtes avant et après,
   reports, et ce que tu n'as pas pu vérifier — sans attendre que je le
   redemande.
