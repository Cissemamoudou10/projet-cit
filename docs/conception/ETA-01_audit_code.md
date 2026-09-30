# ETA-01 — Audit du code actuel face au diagramme d'états

Prompt 34, fichier C. **Lecture seule** — aucun fichier sous `app/` n'a été
modifié pour produire cet audit. Méthode : chaque point du § 5 du prompt est
vérifié par lecture directe du code (règle « vérifier une absence »,
`.claude/rules/tests.md`), jamais par une seule recherche par motif.

**Conclusion en tête** : aucun des onze arbitrages (A1 à A11) n'est rendu
inexprimable par le code actuel. `ProgrammeHebdomadaire` porte déjà les huit
champs nécessaires, l'énumération à cinq états est en place, et le domaine
d'habilitation dédié à la validation existe déjà, inutilisé. Ce qui manque est
d'ampleur normale pour une tâche non encore développée (US-VAL-01 à 04) — pas
une contradiction avec ce que le diagramme exige. L'audit continue donc en
entier, sans arrêt.

---

## 1. Modèle — `ProgrammeHebdomadaire`

`app/planification/models.py:22-83`.

Les huit champs attendus par CLS-05/§4.3 sont **tous déjà présents** :
`etat`, `date_soumission`, `valide_par` (FK `PROTECT` vers l'utilisateur,
conforme à l'association « validé par » de CLS-04:57), `date_validation`,
`motif_rejet`, `date_signature`, `signataire`, `date_affichage`. La docstring
(models.py:37-41) l'annonce explicitement : champs posés par avance,
« jamais renseignés par cette story — US-VAL-03, sprint 3, les remplira ».

`EtatProgramme` (models.py:22-34) déclare exactement les cinq valeurs du
diagramme — `brouillon`, `soumis`, `valide`, `rejete`, `affiche` — avec
`default=BROUILLON` (conforme à T1). La docstring (models.py:23-27) confirme
que c'est fait exprès : « SEUL `BROUILLON` est atteignable depuis cette
story : aucune machine à états ». Rien à corriger ici.

**Contraintes en base** (models.py:69-80) : trois seulement existent
aujourd'hui — `uq_programme_hebdomadaire_lundi`, `ck_programme_lundi_est_
un_lundi`, et `ck_programme_etat` (condition `etat__in=EtatProgramme.
values`). Cette dernière réalise déjà, sous un autre nom, ce que le § 4.3
nomme `ck_programme_etat_connu` — à renommer ou laisser tel quel, détail
mineur, à trancher par US-VAL-03.

**Écart 1** — les sept autres contraintes du § 4.3 (`ck_programme_rejet_
motive`, `ck_programme_motif_hors_circuit`, `ck_programme_soumission_datee`,
`ck_programme_validation_nominative`, `ck_programme_signature_complete`,
`ck_programme_signature_sur_validation`, `ck_programme_affichage_signe`)
n'existent pas encore. Normal : rien ne les a encore demandées avant ce
prompt. Nouvelle migration à prévoir.

---

## 2. Lecteurs et écrivains de l'état

Recherche par un second angle (pas seulement `grep EtatProgramme`) : tous les
appelants de `ServiceEcritureSeance` et `ServiceGeneration`, tout import de
`ProgrammeHebdomadaire.etat`.

| Endroit | Lit/écrit l'état ? | Conforme | Story |
|---|---|---|---|
| `contraintes.py:65,151-169` (`ETATS_COMPTABILISES`, `_charger_volumes`) | Lit — filtre le volume programmé par état | Non — exclut REJETÉ (voir § 3) | US-VAL-03 |
| `ecriture.py` (`ServiceEcritureSeance.creer_seance`/`creer_seances`) | **Ni l'un ni l'autre** — aucun import de `EtatProgramme` | Gate RG-41 absente (voir § 4) | US-VAL-03 |
| `generation.py` (`ServiceGeneration`) | **Ni l'un ni l'autre** | Gate RG-41 absente (voir § 4) | US-VAL-03 |
| `selectors.py` | Aucune fonction ne lit `etat` | Aucun sélecteur « programmes en attente de décision » (A11, c.3) | US-VAL-01 |
| `views.py:42-63` (`vue_lancement_generation`/`_afficher_lancement`) | Ne lit pas `etat` du programme de la semaine | N'affiche pas l'état avant lancement (D-159, voir § 6) | US-VAL-03 |
| `views.py:123` (`vue_consultation_programme`) | Charge `programme_de_la_semaine(lundi)`, n'affiche pas `etat` explicitement dans le contexte actuel (à vérifier côté gabarit par la story) | À compléter | US-VAL-03/04 |
| `jeu_recette/verification.py:222` | Compte les programmes, ne lit pas `etat` | Conforme, sans objet | — |
| `tests/conftest.py:285-288` (fixture `programme`) | Crée sans préciser `etat` (donc `BROUILLON` par défaut) | Conforme, sans objet | — |

---

## 3. D-140 — volume programmé et programmes rejetés (A7)

`regles_volume.py:1-27` (docstring) et `contraintes.py:65` :

```python
ETATS_COMPTABILISES = [etat for etat in EtatProgramme.values if etat != EtatProgramme.REJETE]
```

Confirmé : le code **exclut aujourd'hui** les programmes à l'état REJETÉ du
volume programmé — exactement l'ancien D-140 que A7 révise. C'est un
changement de code normal, pas une impossibilité : il suffit de retirer ce
filtre (ou de fixer `ETATS_COMPTABILISES = EtatProgramme.values`).

Test à modifier en conséquence : `app/planification/tests/
test_contraintes_volume.py:130-144`,
`test_g4_une_seance_d_un_programme_rejete_ne_compte_pas_dans_le_volume` —
l'assertion finale (`assert verdict.accepte`) devra s'inverser une fois A7
implanté ; le nom du test devra changer avec elle. → US-VAL-03.

---

## 4. Porte d'écriture — RG-41 (A6)

`ServiceEcritureSeance.creer_seance`/`creer_seances` (`ecriture.py:117-176`)
**ne consulte l'état du programme nulle part** — confirmé par lecture
complète du fichier, aucune référence à `EtatProgramme` ni à `programme.
etat`. Même constat pour `ServiceGeneration.generer`/`_generer_dans_
programme` (`generation.py:128-165`) : la docstring de `generer` dit même
explicitement (generation.py:134) « RG-31 : produit toujours un BROUILLON,
aucun passage d'état » — vrai aujourd'hui parce qu'aucune autre transition
n'existe encore, mais ça ne dit rien d'une garde contre une génération
lancée sur un programme SOUMIS ou VALIDÉ.

Point de vigilance vérifié et rassurant : `_generer_dans_programme` supprime
déjà les séances non verrouillées (`_supprimer_seances_regenerees`,
generation.py:71-88) **avant** d'appeler `creer_seances`. Si la future garde
RG-41 est posée dans `ServiceEcritureSeance` (conformément à A6, porte
unique) plutôt que dupliquée dans `ServiceGeneration`, une génération lancée
sur un programme à l'état interdit lèvera `ErreurValidation` depuis
`creer_seances` — et comme tout l'appel tient dans le `transaction.atomic()`
englobant de `ServiceGeneration.generer` (generation.py:142), la suppression
sera annulée avec le reste. Le mécanisme transactionnel existant suffit ;
seule la garde elle-même manque. → US-VAL-03, une seule implantation dans
`ServiceEcritureSeance`, conforme à A6.

Nom du futur service du circuit (A6 : « nom à fixer par US-VAL-03 ») : il
n'y a en réalité rien à fixer — `.claude/rules/services.md` le nomme déjà
`ServiceValidation` dans le tableau des huit services (« machine à états du
programme, validation et signature »). `grep -r "ServiceValidation" app/`
ne renvoie rien : le service n'existe pas encore, mais son nom est acquis.

---

## 5. Habilitations (§ 4.2, A8)

`app/administration/constantes.py:28-75` — le domaine **`programme_
validation`** (lecture/écriture) existe déjà, complet : déclaré dans
`noyau/models.py:110-111`, documenté dans `docs/suivi/HABILITATIONS.md:21`,
et déjà distribué dans la matrice :

- **Cellule pédagogique** : `programme_validation_lecture` **et**
  `programme_validation_ecriture` — couvre T4/T5 tels quels.
- **Cellule planification** : `programme_ecriture` mais **pas**
  `programme_validation_ecriture` — déjà vérifié par un test existant,
  `test_planification_ecrit_le_programme_mais_pas_sa_validation`
  (`app/administration/tests/test_matrice_habilitations.py:103-108`).

Rien à créer pour T4/T5 : la plomberie est prête, seul `ServiceValidation`
manque pour l'utiliser.

**Ce qui manque, conformément à la consigne « dis ce qui manque »** : pour la
lecture de la pédagogique (A8, ferme D-154), la seule vue de détail du
programme qui existe aujourd'hui — `vue_consultation_programme`
(`views.py:123-124`) — est gardée par `PERMISSION_LECTURE = "noyau.
programme_lecture"` (`views.py:30`), permission que la cellule pédagogique
**ne possède pas** (elle n'a que `programme_validation_lecture`, pas
`programme_lecture` — `constantes.py:33-45`). En l'état, un GET de cet écran
par la pédagogique rendrait 403. `exige_habilitation` (`administration/
habilitations.py:42-56`) ne prend qu'une seule permission, pas un OR.

Deux issues possibles, non tranchées ici (ce n'est pas un arbitrage du
prompt 34, c'est une décision de conception pour la story) :
(a) élargir le contrôle de `vue_consultation_programme` pour accepter
`programme_lecture` OU `programme_validation_lecture` ;
(b) une vue de détail séparée, propre au circuit de validation, gardée par
`programme_validation_lecture`. → à trancher par US-VAL-02.

---

## 6. Écran de lancement (D-159)

`vue_lancement_generation`/`_afficher_lancement` (`views.py:42-63`) et son
gabarit `lancement_generation.html` : le contexte envoyé au gabarit
(`views.py:55-62`) ne contient ni `programme` ni son `etat` — seuls la
grille active, les groupes de brigades et leurs séances verrouillées/non
verrouillées sont affichés. **L'écran n'affiche donc pas aujourd'hui l'état
du programme de la semaine.** Cohérent avec l'audit du § 4 : comme aucune
garde RG-41 n'existe encore côté service, l'écran ne peut pas non plus
refuser le lancement selon l'état — les deux manques vont ensemble.
→ US-VAL-03, en même temps que la garde de service (§ 4).

---

## Point remarqué, sans invalider aucun arbitrage

**`Avenant` (T10) n'a pas de story assignée.** `docs/diagrammes/CLS-04.puml`
(déjà versionné dans le dépôt, lignes 39-43 et 54-57, 85-91) modélise
`Avenant` comme une classe à part entière — `motif`, `dateDeclaration`,
`natureModification`, associée à `Seance` (1 -- 0..*) et à `Utilisateur`
(« déclaré par »). Cette classe n'existe pas dans `app/planification/
models.py`. Recherche dans les périmètres fournis (`docs/suivi/sprint-3.md`,
`docs/suivi/sprint-4.md`, la ligne Réserve d'`AVANCEMENT.md`) : **aucune
story ne porte son implantation.** `NonExecution` (même diagramme, lignes
35-38, 53, 56, 77-83), en revanche, est bien couverte par US-SUI-05 (sprint
4). A1 reste parfaitement exprimable — le diagramme et la table n'exigent
qu'une transition AFFICHÉ→AFFICHÉ sans changement d'état — mais le modèle
`Avenant` qui la motive et la trace n'a, à ce jour, aucun porteur. À signaler
au chef de projet, pas à assigner au hasard (consigne du prompt).

**Emplacement du fichier A.** Le prompt (§ 1) nomme la destination `docs/
conception/ETA-01_etats_programme.puml`. Or les dix-sept diagrammes déjà
versionnés du projet (`CLS-*`, `SEQ-*`, `UC-*`, `MAQ-*`, `ARC-*`) vivent tous
sous `docs/diagrammes/`, avec un script de rendu dédié (`docs/diagrammes/
rendre.bat`/`.sh`, trouvé conformément à la consigne du § 1 — `plantuml.jar`
existe localement à `C:\outils\plantuml\plantuml.jar`) qui rend vers `docs/
diagrammes/rendu/{svg,png}/`, **ignoré par git** (`.gitignore:24-25` : « Les
sources .puml sont versionnées, les rendus se régénèrent »). Une copie du
fichier A, identique au caractère près à la source du § 3, est déjà présente
à `docs/diagrammes/ETA-01_etats_programme.puml` (non suivie par git avant ce
commit). Je place donc la source `.puml` à cet emplacement conventionnel
plutôt qu'à celui, isolé, du § 1 — les rendus SVG/PNG restent produits mais
non commités, comme pour tous les autres diagrammes du dépôt. B, C et D
restent sous `docs/conception/`, comme demandé, puisqu'aucun fichier narratif
de ce type n'y contredit une convention existante.

---

## Ce qui n'a pas pu être vérifié

Le gabarit exact de `vue_consultation_programme` (affichage actuel ou non de
l'état dans l'écran déjà livré) n'a pas été ouvert ligne à ligne : le
contexte de la vue prépare `programme_de_la_semaine(lundi)`
(`views.py:127`), mais confirmer si le gabarit l'exploite déjà dépasse le
périmètre lecture-seule de cet audit et relève de la story elle-même.
