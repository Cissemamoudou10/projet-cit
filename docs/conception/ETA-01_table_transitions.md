# ETA-01 — Table des transitions du programme hebdomadaire

Prompt 34, fichier B. L'oracle : onze événements × cinq états, source
`docs/conception/ETA-01_note_cellules.md` et `docs/diagrammes/ETA-01_etats_
programme.puml`. Chaque case admise porte le numéro de transition du
diagramme (T1 à T10) ; chaque case refusée le dit sans numéro. Sous chaque
ligne d'événement, une seconde ligne donne le nom du test qu'US-VAL-03 (ou
la story indiquée en tête de section) écrira pour chacune des cinq cases —
55 noms au total, format `test_<etat>_<evenement>_<admis|refuse>`.

Vérifié par confrontation avec ETA-01_audit_code.md (§4) : aucune de ces
cases n'a de mécanisme aujourd'hui en dehors de `ServiceContraintes.
regles_volume` (RG-39, hors circuit) — toutes restent à écrire par les
stories US-VAL-01 à 04 et US-PLAN-05/06/09.

## 4.1 Table état × événement

| Événement ↓ / État → | BROUILLON | SOUMIS | REJETÉ | VALIDÉ | AFFICHÉ |
|---|---|---|---|---|---|
| **soumettre** | T2 → SOUMIS ; refus si aucune séance (A9) | refus — déjà soumis (US-VAL-01 c.4) | refus — reprendre d'abord (A2) | refus | refus |
| ↳ tests | `test_brouillon_soumission_admis` | `test_soumis_soumission_refuse` | `test_rejete_soumission_refuse` | `test_valide_soumission_refuse` | `test_affiche_soumission_refuse` |
| **retirer la soumission** | refus | T3 → BROUILLON | refus | refus — annuler la validation (T9) | refus |
| ↳ tests | `test_brouillon_retrait_soumission_refuse` | `test_soumis_retrait_soumission_admis` | `test_rejete_retrait_soumission_refuse` | `test_valide_retrait_soumission_refuse` | `test_affiche_retrait_soumission_refuse` |
| **valider** | refus — non soumis (CU-P5-11 E1) | T4 → VALIDÉ | refus | refus — déjà validé | refus |
| ↳ tests | `test_brouillon_validation_refuse` | `test_soumis_validation_admis` | `test_rejete_validation_refuse` | `test_valide_validation_refuse` | `test_affiche_validation_refuse` |
| **rejeter** | refus (E1) | T5 → REJETÉ ; refus si motif vide ou blanc (RG-45) | refus | refus — VALIDÉ → REJETÉ n'existe pas | refus |
| ↳ tests | `test_brouillon_rejet_refuse` | `test_soumis_rejet_admis` | `test_rejete_rejet_refuse` | `test_valide_rejet_refuse` | `test_affiche_rejet_refuse` |
| **reprendre en correction** | refus — sans objet | refus | T6 → BROUILLON | refus | refus |
| ↳ tests | `test_brouillon_reprise_correction_refuse` | `test_soumis_reprise_correction_refuse` | `test_rejete_reprise_correction_admis` | `test_valide_reprise_correction_refuse` | `test_affiche_reprise_correction_refuse` |
| **enregistrer la signature** | refus | refus | refus | T7, reste VALIDÉ ; refus si date < validation ou future | refus — figée |
| ↳ tests | `test_brouillon_signature_refuse` | `test_soumis_signature_refuse` | `test_rejete_signature_refuse` | `test_valide_signature_admis` | `test_affiche_signature_refuse` |
| **afficher** | refus (RG-46) | refus (RG-46) | refus (RG-46) | T8 → AFFICHÉ si signature, sinon refus (RG-46) | refus — déjà affiché |
| ↳ tests | `test_brouillon_affichage_refuse` | `test_soumis_affichage_refuse` | `test_rejete_affichage_refuse` | `test_valide_affichage_admis` | `test_affiche_affichage_refuse` |
| **annuler la validation** | refus | refus | refus | T9 → BROUILLON ; refus sans confirmation ou sans motif | refus — avenant (A1) |
| ↳ tests | `test_brouillon_annulation_validation_refuse` | `test_soumis_annulation_validation_refuse` | `test_rejete_annulation_validation_refuse` | `test_valide_annulation_validation_admis` | `test_affiche_annulation_validation_refuse` |
| **porter un avenant** | refus — modifier directement | refus | refus | refus | T10, reste AFFICHÉ ; refus sans motif ou sans nature |
| ↳ tests | `test_brouillon_avenant_refuse` | `test_soumis_avenant_refuse` | `test_rejete_avenant_refuse` | `test_valide_avenant_refuse` | `test_affiche_avenant_admis` |
| **modifier / ajouter / supprimer une séance** (sans avenant) | admis | refus (RG-41) — indique « retirer la soumission » | admis, précédé de T6 implicite | refus (RG-41) — indique « annuler la validation » | refus — avenant obligatoire |
| ↳ tests | `test_brouillon_ecriture_seance_admis` | `test_soumis_ecriture_seance_refuse` | `test_rejete_ecriture_seance_admis` | `test_valide_ecriture_seance_refuse` | `test_affiche_ecriture_seance_refuse` |
| **générer** (US-PLAN-03, sélection de brigades) | admis, complète (D-146) | refus (RG-41) | admis, précédé de T6 implicite | refus (RG-41) | refus |
| ↳ tests | `test_brouillon_generation_admis` | `test_soumis_generation_refuse` | `test_rejete_generation_admis` | `test_valide_generation_refuse` | `test_affiche_generation_refuse` |

Chaque transition admise est journalisée (auteur, horodatage, état de
départ, état d'arrivée, motif s'il y en a) ; chaque refus rend un message
qui nomme la règle et, quand elle existe, la marche à suivre. **Écart
constaté par l'audit (`ETA-01_audit_code.md` § « journal ») : `TypeAction`
ne compte aujourd'hui que `VALIDATION_PROGRAMME` et `REJET_PROGRAMME`
(T4, T5) — sept valeurs manquent pour T2, T3, T6, T7, T8, T9, T10.**

## 4.2 Acteur de chaque transition

| Transition | Profil autorisé | Refus attendu pour les autres profils |
|---|---|---|
| T2, T3, T6, T7, T8, T9, T10 | Cellule planification | 403 pour pédagogique, examens, direction, administrateur |
| T4, T5 | Cellule pédagogique | 403 pour planification, examens, direction, administrateur |

Direction de Formation : lecture de tous les programmes, aucune transition.

Vérifié par l'audit : les permissions `programme_ecriture` (planification,
T2/T3/T6/T7/T8/T9/T10) et `programme_validation_ecriture` (pédagogique,
T4/T5) existent déjà dans la matrice (`app/administration/constantes.py`)
et sont déjà mutuellement exclusives — test existant, `test_planification_
ecrit_le_programme_mais_pas_sa_validation` (`app/administration/tests/
test_matrice_habilitations.py:103-108`). Rien à créer pour cette table ;
`ServiceValidation` (à créer, US-VAL-01 à 04) les consomme.

## 4.3 Contraintes à porter en base (US-VAL-03 et US-VAL-04)

Les transitions interdites ne s'expriment pas en CHECK (il faudrait
l'ancien état) ; les ÉTATS incohérents, si. Chacune aura son test qui force
l'écriture directe en base et attend `IntegrityError`.

| Nom | Règle | Contenu | État dans le code aujourd'hui |
|---|---|---|---|
| `ck_programme_etat_connu` | RG-44 | état parmi les cinq valeurs | **Déjà présent**, sous le nom `ck_programme_etat` (`app/planification/models.py:73-75`) |
| `ck_programme_rejet_motive` | RG-45 | état = REJETÉ ⇒ motif non vide après suppression des blancs | Absente |
| `ck_programme_motif_hors_circuit` | A2 | état ∈ {SOUMIS, VALIDÉ, AFFICHÉ} ⇒ motif de rejet vide | Absente |
| `ck_programme_soumission_datee` | US-VAL-01 | état ∈ {SOUMIS, VALIDÉ, REJETÉ, AFFICHÉ} ⇒ date de soumission renseignée | Absente |
| `ck_programme_validation_nominative` | RG-47 | état ∈ {VALIDÉ, AFFICHÉ} ⇒ validateur ET date de validation renseignés | Absente |
| `ck_programme_signature_complete` | RG-47 | date de signature et signataire tous deux renseignés ou tous deux vides | Absente |
| `ck_programme_signature_sur_validation` | A5 | signature renseignée ⇒ date de validation renseignée et date de signature ≥ date de validation | Absente |
| `ck_programme_affichage_signe` | RG-46, US-VAL-04 c.3 | état = AFFICHÉ ⇒ signature complète ET date d'affichage renseignée | Absente |

## 4.4 Cas de test par le vrai cycle HTTP (leçon D-50)

- US-VAL-01 — POST de soumission par la planification : redirection, état SOUMIS, ligne de journal ; même POST une seconde fois : refus, état inchangé.
- US-VAL-01 — le programme soumis apparaît dans la liste « en attente » de la pédagogique (GET réel). *(sélecteur à créer, voir ETA-01_audit_code.md § 2)*
- US-VAL-02 — POST de validation par la planification : 403, état inchangé en base.
- US-VAL-02 — POST de rejet sans motif (vide, puis blancs seuls) : formulaire réaffiché avec l'erreur, état inchangé.
- US-VAL-02 — après rejet, GET du détail par la planification : le motif est lisible.
- US-VAL-02 — GET du détail d'un programme soumis par la pédagogique : 200 (A8, ferme D-154). *(permission à trancher, voir ETA-01_audit_code.md § 5)*
- US-VAL-03 — POST de génération (écran réel de lancement, D-159) sur une semaine SOUMISE : refus, aucune séance créée, compte de séances inchangé.
- US-VAL-03 — POST de génération sur une semaine REJETÉE : état BROUILLON après coup, séances créées, journal portant la reprise PUIS la génération.
- US-VAL-04 — POST d'affichage sur un programme VALIDÉ sans signature : refus, état inchangé ; même tentative par écriture directe en base : `IntegrityError`.
- US-VAL-04 — le bouton « Afficher » est absent du détail tant que la signature n'est pas enregistrée ; le refus serveur tient quand on forge le POST quand même.
- US-PLAN-05 — POST de modification d'une séance d'un programme VALIDÉ : refus nommant « annuler la validation » ; sur AFFICHÉ sans motif d'avenant : refus.

Et deux tests d'architecture, pour US-VAL-03 : aucune affectation de l'état
du programme hors du service du circuit (`ServiceValidation`) ; aucun appel
d'écriture de séance qui contourne la garde d'état de `ServiceEcritureSeance`
(même patron que `test_seule_la_porte_d_ecriture_instancie_seance_ou_ligne_
programme`, `tests/architecture/test_couches.py:287`).
