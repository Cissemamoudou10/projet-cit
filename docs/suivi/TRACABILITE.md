# Traçabilité critères d'acceptation → tests

Prompt 49, Temps 7. Pur inventaire — **aucun test nouveau écrit à ce
stade**. Pour chacune des 52 stories livrées (sprints 1 à 4), ses critères
d'acceptation identifiables et le ou les tests qui les couvrent.

## Méthode et limites

Le backlog v10 (texte intégral des critères) **n'est pas dans ce dépôt**
(document externe, tenu par le chef de projet). Les critères sont
reconstitués à partir de ce qui est réellement tracé dans le code : les
codes courts (A1, B2, C5, E1, N7, V3, M5, R6…) cités dans les noms de
fonctions de test, leurs docstrings, et `docs/suivi/DECISIONS.md`/
`heures-sprint-N.md`. C'est un survol par fichiers/noms de tests et
recherche ciblée, **pas une relecture intégrale du corps de chaque test** —
suffisant pour un inventaire de traçabilité, pas une preuve formelle.

Trois statuts possibles pour un critère :
- **Couvert** — un ou plusieurs tests nommés le couvrent, cités ci-dessous.
- **Reporté** — le critère appartient à cette story mais n'est exercé que
  par les tests d'une story ultérieure (cité, avec sa destination).
- **Recette manuelle** — aucun test automatisé par construction : une
  limite de conception assumée (rien à exécuter), ou un jugement humain
  (lisibilité d'un document imprimé).
- **Non identifié** — le survol n'a pas retrouvé de code de critère
  correspondant avec certitude ; peut exister sans être retrouvé, ou avoir
  été retiré/fusionné entre les versions du backlog.

**Avertissement méthodologique (sprint 1).** Le sprint 1 n'a pas appliqué
la convention « un test nommé par critère », adoptée à partir du sprint 2.
Un critère « non identifié » au sprint 1 ne signifie donc PAS une absence
de couverture — la fonctionnalité est très généralement testée, seulement
sans étiquette de critère explicite dans le nom du test.

---

## Sprint 1 (15 stories)

### US-ADM-01 — S'authentifier
Fichiers : `test_authentification.py`, `test_vues_authentification.py`, `test_gabarit_connexion.py`.
- A9 (verrouillage après 5 échecs) — couvert : `test_cinq_echecs_verrouille_le_compte`
- A10 (compte verrouillé refuse même le bon mot de passe) — couvert : `test_compte_verrouille_avec_bon_mot_de_passe_reste_refuse`
- Critère 1 (gabarit de connexion) — couvert : `test_gabarit_connexion.py` (ensemble)
- Reste (RG-01, RG-03, RG-26, CU-P1-01) — couvert, non identifié par n° de critère (convention absente au sprint 1) : `test_authentification.py`, `test_vues_authentification.py`

### US-ADM-02 — Comptes utilisateurs
Fichiers : `test_comptes.py`, `test_vues_comptes.py`.
- Aucun code de critère retrouvé — couverture fonctionnelle réelle (création/désactivation/profil/mot de passe/pagination/recherche), non identifiée par n°.

### US-ADM-03 — Accès par profil
Fichiers : `test_acces_habilitations.py`, `test_habilitations.py`, `test_matrice_habilitations.py`, `test_vue_habilitations_ecran.py`, `test_appliquer_changements_habilitations.py`, `test_initialiser_habilitations.py`.
- Critère 6 (masquage = conséquence, refus direct journalisé) — couvert : `test_acces_habilitations.py`
- RG-02, RG-26 — couvert : `test_habilitations.py` ; RG-02 bis — `test_initialiser_habilitations.py`
- Reste (matrice §11.2, écran d'édition) — couvert, non identifié par n°.

### US-ADM-04 — Journaliser les actions sensibles
Fichiers : `test_journal.py`, `test_consultation_journal.py`, `test_contenu_journal.py`, `test_immuabilite_journal.py`.
- Critère 1 (contenu : auteur, date, valeur précédente, liste blanche, aucun mot de passe) — couvert : `test_contenu_journal.py`
- RG-27 (immuabilité) — couvert : `test_immuabilite_journal.py`

### US-REF-00 — Types de formation
Fichier : `test_type_formation.py`.
- E3 (refus énumère l'élément opposant) — couvert.
- Reste — non identifié par n°.

### US-REF-01 — Formations
Fichiers : `test_formation.py`, `test_formation_ecran.py`.
- E5 (P-23/P-30, fausse détection de conflit) — couvert.
- E11 (P-31, modification concurrente) — couvert : `test_modification_concurrente_est_detectee`
- Reste — non identifié par n°.

### US-REF-02 — Catalogue des matières
Fichier : `test_matiere.py`.
- E3 (refus énumère l'élément opposant) — couvert.
- Reste — non identifié par n°.

### US-REF-03 — Composer le référentiel
Fichiers : `test_referentiel.py`, `test_referentiel_ecran.py`.
- Aucun code retrouvé — couverture réelle complète, non identifiée par n°.
- Écart 4 (`ECARTS-LIVRABLES-SPRINT-4.md`) : coefficient/poids absents des critères — fermé, voir US-REF-03 au prompt 46.

### US-REF-04 — Catégorie de lieu requise par matière
Fichiers : `test_referentiel.py`, `test_matiere.py`.
- Aucun code retrouvé — couverture réelle complète (contrainte base + service), non identifiée par n°.

### US-REF-05 — Objectifs pédagogiques
Fichiers : `test_objectif_pedagogique.py`, `test_objectif_pedagogique_ecran.py`, `test_objectif_pedagogique_ordre.py`.
- Aucun code retrouvé — couverture réelle complète, non identifiée par n°.

### US-REF-06 — Prérequis d'un référentiel
Fichiers : `test_prerequis.py`, `test_prerequis_ecran.py`.
- E1 (chemin RG-10 satisfait mais échoue) — couvert. E3 (contrainte non différée) — couvert.
- **Critère 4, volet saisie manuelle — reporté** : aucun test dans `referentiel` au sprint 1 ; fermé seulement au sprint 3 par `planification/tests/test_modification.py::test_e_prerequis_non_acheve_refuse_une_modification_manuelle` (US-PLAN-05, D-39). Trou réel au sprint 1, comblé au sprint 3.

### US-REF-07 — Consulter le référentiel depuis les autres cellules
Fichiers : `test_couverture_consultation.py`, `test_fraicheur_consultation.py`, `test_masquage_ecriture.py`, `test_refus_ecriture_direct.py`.
- Critère 2 (masquage écriture) — couvert : `test_masquage_ecriture.py`
- Critère 3 (refus direct journalisé une fois, non-divulgation) — couvert : `test_refus_ecriture_direct.py`
- Critère 4 (fraîcheur immédiate) — couvert : `test_fraicheur_consultation.py`
- Critère 1 — non identifié (probablement couvert implicitement par les tests de lecture dispersés).

### US-INS-01 — Gérer les instructeurs
Fichiers : `test_instructeur.py`, `test_instructeur_ecran.py`.
- Aucun code retrouvé — couverture réelle complète, non identifiée par n°.

### US-INS-02 — Matrice de qualification
Fichiers : `test_qualification.py`, `test_qualification_ecran.py`.
- Critère 5 (matière qualifiée non supprimable) — couvert : `test_suppression_d_une_matiere_qualifiee_est_refusee_par_le_service`. Couverture HTTP réelle du même refus non confirmée par le survol — **à vérifier**.
- Reste — non identifié par n°.

### US-PLAN-02 — Lieux d'enseignement
Fichiers : `test_lieu.py`, `test_lieu_ecran.py`.
- Aucun code retrouvé — couverture réelle complète, non identifiée par n°.

**Recette manuelle sprint 1** : aucune identifiée — tout défaut initialement trouvé en recette manuelle (A9/A10, E11 — P-30/P-31) a reçu un test automatisé depuis.

---

## Sprint 2 (12 stories)

### US-SES-01 — Ouvrir une session
Fichiers : `test_session.py`, `test_session_ecran.py`, `test_protection_formation.py`.
- E1-E4 (dates, volume excessif/avertissement, effectif, référentiel vide) — couverts.
- Critères 2-5 (résumé référentiel, périodes disjointes, formation archivée, sans périodicité) — couverts.
- A1 (chevauchement accepté) — couvert. Protection Formation (D-69/70) — couvert : `test_protection_formation.py`.
- **A2 (modification des dates, signalement des séances) — reporté** à US-PLAN-03 (D-70), aucun test dans `organisation`.

### US-SES-02 — Constituer les brigades
Fichiers : `test_brigade.py`, `test_brigade_ecran.py`.
- A2-A10, C1, C3, C5-C8 — tous couverts (voir rapport détaillé, noms `test_a2_…` à `test_c8_…`).
- **Critère 5 (brigade au programme en cours non supprimable) — reporté** : mécanisme générique sans opposant au sprint 2 (`test_critere_5_suppression_sans_programme_toujours_acceptee` constate l'absence), fermé réellement au sprint 2 par `planification/tests/test_modeles.py::test_d83_suppression_brigade_au_programme_refusee_par_le_vrai_chemin_de_service` (US-PLAN-04, même sprint).
- Unicité de désignation « au sein du type de formation » (D-80) — **recette manuelle / arbitrage non tranché**, testée seulement au niveau session.

### US-SES-03 — Salle attitrée par brigade
Fichiers : `test_salle_attitree.py`, `test_salle_attitree_ecran.py`.
- A1-A13, C1-C9 — tous couverts.
- **Critère 4 (salle par défaut si matière sans lieu requis) — reporté** à US-PLAN-03/04, couvert par `planification/tests/test_generation_lieux.py::test_d1_matiere_salle_attitree_reprend_la_salle_de_la_brigade`.

### US-SES-04 — Consulter la composition d'une session
Fichiers : `test_composition_session_ecran.py` (organisation + ressources), `test_taux_occupation.py`.
- A6, B1-B5, taux d'occupation A1-A4, C7 — tous couverts.
- **Taux d'occupation sur l'effectif réel (D-94) — reporté** à US-SES-06, couvert par `ressources/tests/test_affectation_capacite.py`.

### US-SES-05 — Enregistrer les stagiaires
Fichiers : `test_stagiaire.py`, `test_import_stagiaires.py`, `test_stagiaire_ecran.py`.
- A1-A6, B1-B12, D1-D5, E1-E7 — tous couverts.
- Entité « personne » transverse (D-95) — hors périmètre, question de terrain non tranchée, aucun critère formel.

### US-SES-06 — Affecter les stagiaires aux brigades
Fichiers : `test_affectation.py`, `test_affectation_contraintes.py`, `test_repartition_proposition.py`, `test_repartition_validation.py`, `test_repartition_ecran.py`, `ressources/test_affectation_capacite.py`.
- A1-A6, B1-B7, C1-C4, D1-D4bis, E1-E6, F1-F8 — tous couverts.
- **Volet volume horaire dispensé (D-108) — reporté** à US-SUI-01 (sprint 4), fermé le 2026-10-13 (voir `AVANCEMENT.md`).

### US-SES-07 — Consulter la liste des stagiaires
Fichiers : `test_liste_stagiaires.py`, `test_export_stagiaires.py`, `test_export_stagiaires_ecran.py`.
- A2-A7, B1-B10, C1-C3, D1-D7 — tous couverts. Aucun report identifié.

### US-INS-03 — Enregistrer les indisponibilités transmises
Fichiers : `test_indisponibilite_instructeur.py`, `test_indisponibilite_instructeur_contraintes.py`, `test_indisponibilite_instructeur_ecran.py`.
- A1-A7, B1-B4, C1-C8, D1-D8 — tous couverts.
- **Critère 4/RG-25 (contrainte dure) — reporté** à US-PLAN-04, couvert par `test_contraintes_instructeur.py`.
- **Critère 5, points 4-5 (séances recoupant la période) — reporté** à US-PLAN-09 (sprint 3).

### US-PLAN-01 — Calendrier académique annuel
Fichiers : `test_periode_calendrier.py`, `test_periode_calendrier_chevauchement.py`, `test_periode_calendrier_projection.py`, `test_nature_evenement.py`, `test_calendrier_ecran.py`.
- A1-A4, B1-B6, C1-C5, D1-D5, E1-E3, F1-F2, G1-G8 — tous couverts.
- **Critère 5/RG-38 (exclusion à la génération) — reporté** à US-PLAN-03/04, couvert par `test_contraintes_calendrier.py`.
- **E2 et A3 (période bloquante recouvrant des séances, séances redevenues programmables) — reportés** à US-PLAN-05 (sprint 3, D-121).

### US-PLAN-03 — Générer le programme hebdomadaire
Fichiers : `test_generation.py`, `test_generation_heuristique.py`/`2.py`, `test_generation_lieux.py`, `test_generation_exceptions.py`, `test_generation_compte_rendu.py`, `test_generation_regeneration.py`, `test_generation_ecran.py`, `test_generation_architecture.py`, `test_generation_performance.py`.
- A1-A5, C1-C6, D1-D5, E1-E6, F1-F5, B1-B5, G1-G7, I3, mesures de référence §10 — tous couverts.
- Impression « par journée » (RG-33 bis) — **recette manuelle/différé** : mesurée, non implantée, reportée au lot d'impression du sprint 4 (D-155).
- **Critère 6 d'US-PLAN-12 (changement de grille n'affecte pas les séances passées) — vérifié par lecture de code, pas par test automatisé** (D-156 : constat d'absence de code produisant ce risque, pas un test).

### US-PLAN-04 — Garantir le respect des contraintes dures
Fichiers : `test_contraintes_instructeur.py`, `test_contraintes_lieu.py`, `test_contraintes_calendrier.py`, `test_contraintes_volume.py`, `test_contrat_service.py`, `test_modeles.py`.
- RG-34 (b1-b5, c1-c2, d1-d3), RG-37 (e1-e8), RG-38 (f1-f6), RG-39 (g1-g8), contrat de service (h1-h6), modèles (a1-a9) — tous couverts.
- RG-39 b) « prérequis achevé » — testé pour sa définition PROVISOIRE (volume programmé) ; la définition finale (réalisé) n'existait pas encore — comblé au sprint 4 (US-SUI-01, R2).
- Vérification terrain D-137 (0 lieu sans capacité) — **recette manuelle** (constat, pas un test).

### US-PLAN-12 — Grilles horaires
Fichiers : `test_grille_horaire.py`, `test_creneau_type.py`, `test_grille_horaire_ecran.py`, `test_volume_horaire_reference.py`, `test_initialiser_grilles_horaires.py`.
- A1-A8, B1-B10, C1-C9, D2, F1-F7, G1, E1-E5 — tous couverts.
- **Critère 6 — vérifié par lecture de code**, pas par test (même point que ci-dessus, D-156).
- RG-64 (relation facultative Séance↔CréneauType) — **limite de conception**, tranchée D-288/D-293 (prompt 49), jamais exercée par aucun test ni comportement (consigné, pas un trou de recette).

**Recette manuelle sprint 2** : critère 6 d'US-PLAN-12 (× son double emploi dans US-PLAN-03), vérification terrain D-137, unicité de désignation de brigade (D-80, arbitrage non tranché).

---

## Sprint 3 (11 stories)

### US-PLAN-05 — Modifier manuellement une affectation
Fichiers : `test_modification.py`, `test_modification_ecran.py`, `test_ajout_manuel.py`, `evaluations/test_suppression_evaluation.py`.
- M2-M10, C4 — couverts (voir rapport détaillé pour chaque test nommé).
- M1 (porte unique) — couvert diffusément par l'ensemble du fichier, pas un test isolé.
- E2 (sélecteur période/séances recouvertes, côté `ressources`) — **statut incertain**, non confirmé par le survol (hors `planification`/`evaluations`).

### US-PLAN-06 — Regrouper plusieurs brigades sur une même séance
Fichier : `test_regroupement.py`.
- R1, R2, R4 — couverts par thème (pas de préfixe `r` dans les noms).
- R5 (confirmation si séance déjà regroupée) — **non identifié**, pas de test isolé trouvé.
- R3 — **non identifié**, absent de la séquence des décisions D-247 à D-251 ; à vérifier au backlog lui-même.

### US-PLAN-09 — Traiter une indisponibilité déclarée
Fichiers : `test_indisponibilite.py`, `test_indisponibilite_ecran.py`.
- I1-I6 — tous couverts (I6 fermé par les mêmes tests qu'I2).
- (`test_p42_verrouillage_lot.py` est un correctif de production, P-42 — explicitement hors critère d'acceptation, pas à compter ici.)

### US-VAL-03 — Gérer les états du programme
Fichiers : `test_circuit_table.py`, `test_circuit_base.py`, `test_circuit_garde.py`, `test_circuit_transitions.py`, `test_circuit_volume.py`, `test_circuit_ecran.py`.
- V1-V8, sept contraintes en base — tous couverts.

### US-VAL-01 — Soumettre un programme à validation
Fichier : `test_circuit_ecran_validation.py`.
- C3 — couvert. C1/C2 — **non identifiés** explicitement (probablement couverts implicitement par les mêmes tests de soumission/retrait).

### US-VAL-02 — Valider ou rejeter un programme
Fichier : `test_circuit_ecran_decision.py`.
- C4 — couvert. C5 (décision centre entier, une action par semaine) — **couverture indirecte**, pas de test dédié isolant ce point.

### US-VAL-04 — Empêcher l'affichage d'un programme non validé
Fichier : `test_circuit_ecran_signature.py`.
- C1-C4 — tous couverts (C3/C4 partiellement pré-testés côté moteur par US-VAL-03, D-234, prouvés ici par le cycle HTTP).

### US-EVAL-01 — Créer une évaluation selon son type
Fichiers : `test_modeles.py`, `test_service.py`, `test_insertion_seance.py`, `test_habilitations.py`, `test_ecran.py`, `test_reports.py`.
- A1-A8, B1-B7, C1-C8, D1-D3/D5-D8, E1-E6, G1-G3 — tous couverts.
- **D4 — non identifié** (saut dans la numérotation, possible fusion au backlog v10).
- **Bloc F — non identifié**, aucun fichier retrouvé pour ce bloc.

### US-EVAL-02 — Saisir la date d'un examen final
Fichiers : `test_rg38_examen.py`, `test_modification_date.py`, `test_signalement_seances.py`, `test_ecran_date_examen.py`.
- A1, A3, A5-A8 — couverts avec confiance. **A2, A4 — correspondance par thème, pas par nom** (fiabilité moindre, à confirmer si besoin absolu).

### US-EVAL-03 — Enregistrer les sujets transmis, sélectionner celui retenu
Fichiers : `test_sujets.py`, `test_sujets_ecran.py`.
- A1-A6, B1-B10, D1, C1-C5, E1-E5 — tous couverts (noms de test = codes, forte confiance).
- Critère c.7 (aucune évaluation sans sujet retenu) — **réinterprété** par D-205, le prédicat est testé seul ici (B9), le refus réel est reporté et fermé par US-EVAL-04 — pas un trou, un changement de critère documenté.

### US-EVAL-04 — Organiser une épreuve
Fichiers : `test_organisation_base.py`, `test_organisation_services.py`, `test_organisation_contraintes.py`, `test_organisation_droits.py`, `test_organisation_generation.py`, `test_organisation_ecran.py`.
- A1-A7, B1-B10, C1-C8, D1-D4, E1-E2, F1-F4, G1-G6, H2 — tous couverts.
- Critère c.7 d'US-EVAL-03 — fermé ici par réinterprétation (C10, booléen « prête »), testé (B9).

**Recette manuelle sprint 3** : aucune identifiée explicitement dans `DECISIONS.md` pour ces onze stories — tous les reports retrouvés renvoient à un test nommé, dans cette story ou une suivante.

---

## Sprint 4 (14 stories)

### US-SUI-05 — Déclarer la non-exécution d'une séance
Fichiers : `test_suivi.py`, `test_suivi_ecran.py`.
- C1, C2, C4-C6 — couverts. **C3 (volume retranché du réalisé) — pas de test dans cette story par construction**, vérifié par le calcul du rapprochement lui-même (US-SUI-01/US-SUI-06) : `test_rapprochement.py::test_c2_non_execution_retranchee_du_realise`, `test_progression.py::test_c2_non_execution_listee_avec_motif_et_retranchee`.

### US-SUI-01 — Consulter le rapprochement prescrit/programmé/réalisé
Fichiers : `test_rapprochement.py`, `test_rapprochement_ecran.py`, `test_resolveur_volume_realise_brigade.py`.
- C1/C3, C2, C5, R4, R5/E1, R7, filtres — couverts.
- R6 (avertissement à l'affectation, D-108) — couvert, nom de test porte « c6 » dans le fichier (incohérence de nommage probable, pas un trou).

### US-SUI-06 — Éditer la progression réalisée hebdomadaire
Fichiers : `test_progression.py`, `test_progression_ecran.py`, `test_progression_pdf.py` ; architecture : `test_calcul_unique_progression.py`.
- C1-C3, P1, P4, C5, signature, calcul unique — couverts.
- PDF (6 tests) — couverts, exécutés via `pytest -m pdf` **dans le conteneur Docker, jamais sous Windows** (P-44) : test automatisé à contrainte d'environnement, **pas une recette manuelle**.

### US-EVAL-05 — Saisir et vérifier les notes
Fichiers : `test_notes.py`, `test_notes_ecran.py`.
- A3, N5 — couverts.
- **N7 (verrouillage par procès-verbal) — stub à `False` dans cette story par construction** (D-270) : aucun test de refus réel possible ici, câblage et test réels reportés à US-EVAL-07.

### US-EVAL-06 — Calculer moyennes et classement
Fichiers : `test_moyennes.py`, `test_moyennes_ecran.py`.
- M2-M8, N6, A1 — couverts.
- **M1 (rien n'est stocké) — propriété architecturale, pas de test dédié isolé** (vérifiée indirectement par l'absence de champ stocké).

### US-EVAL-07 — Générer les procès-verbaux de résultats
Fichiers : `test_proces_verbal.py`, `test_proces_verbal_ecran.py`, `test_proces_verbal_pdf.py`.
- V2-V7, V10, A1/§1.2 — couverts. N7 réel câblé et testé ici (referme le stub d'US-EVAL-05).
- PDF (9 tests) — couverts, `pytest -m pdf` en conteneur, pas une recette manuelle.
- **Recette manuelle confirmée** : trois PDF réels (exemplaires liés à la correction §1.2) produits en conteneur et **relus visuellement**, scripts non commités (`heures-sprint-4.md`, prompt 47 §1.3) — jugement humain sur la mise en page, aucun test par construction.

### US-PLAN-07 — Signaler les écarts de volume horaire
Fichier : `test_ecart_volume.py` ; architecture : `test_calcul_unique_ecart_volume.py`, `test_calcul_unique_statut_volume.py`.
- E1, E3, seuil, requêtes constantes, habilitation — couverts.
- **E2, second écran (rapprochement) — déplacé sous US-SUI-02** par D-282 (prompt 48) : couvert là, pas ici (`test_alerte_ecart.py`).

### US-VAL-05 — Consulter les programmes et l'historique des validations
Fichier : `test_programmes_liste_historique.py`.
- H1, H2, H4, requêtes constantes — couverts.
- **H3 — non identifié** (absent des codes cités dans `heures-sprint-4.md`, qui ne mentionne que H1/H2/H4).

### US-SES-09 — Clôturer une session
Fichiers : `organisation/test_cloture_session.py`, `evaluations/test_cloture_session.py`, `planification/test_suivi.py`, `planification/test_cloture_session_selection.py`.
- C1-C5 — couverts (23 tests au total, répartis par couche applicative).
- **C6 (aucune réouverture) — recette manuelle / non applicable** : limite de conception assumée (D-281), aucun mécanisme n'existe à tester.

### US-SUI-02 — Être alerté des écarts significatifs
Fichiers : `test_alerte_ecart.py`, `test_alertes_ecran.py` ; architecture : `test_calcul_unique_statut_volume.py`.
- A2, décoration conforme/retard/dépassement (reprend l'ex-E2 de PLAN-07), seuil, requêtes constantes, écran/navigation — tous couverts.

### US-SUI-03 — Consulter le tableau de bord des formations
Fichier : `test_tableau_bord.py`.
- B2, B3, B4, B6, requêtes constantes, brigade absente si clôturée/future — couverts.
- **B5 (barre de progression CSS pure) — pas de test dédié identifié** : aspect de rendu visuel, autorisé sans test par le prompt lui-même, non signalé comme recette manuelle dans les décisions.

### US-INS-04 — Consulter la charge d'un instructeur
Fichiers : `test_resolveur_charge_instructeur.py`, `evaluations/test_ins04_charge_instructeur.py`.
- C2, fournisseur câblé, regroupement, période à cheval, requêtes constantes, surveillance, HTTP — couverts.
- Seul C2 est explicitement cité par `heures-sprint-4.md` — les autres critères possibles ne sont pas nommément confirmés.

### US-REF-09 — Historiser les modifications du référentiel
Fichier : `test_historique.py`.
- E1, historique sur quatre fiches, filtrage par valeur stable (D-287), porte unique/immuabilité — couverts.
- **E4 (aucune reprise rétroactive) — recette manuelle / non applicable** : limite assumée (D-286), rien à exécuter.

### US-PLAN-11 — Dupliquer un programme hebdomadaire
Fichiers : `test_duplication.py`, `test_duplication_ecran.py`, `evaluations/test_plan11_duplication.py`.
- D1, D4, D7, refus croisés, contrôle non dupliqué, HTTP — couverts.
- **D2 (créneau équivalent) — pas de test au nom explicite**, probablement couvert implicitement par le test nominal.

**Recette manuelle sprint 4** : US-SES-09/C6, US-REF-09/E4 (limites de conception assumées, D-281/D-286), les trois PDF de démonstration d'US-EVAL-07 (jugement visuel, prompt 47 §1.3).

**Hors des 52 stories, pour mémoire** : les deux PDF d'exemplaires
« programme hebdomadaire » et « convocation d'épreuve » produits au Temps
4b du prompt 49 (D-291) sont du travail hors backlog (aucune story) — un
jugement de lisibilité laissé au lecteur, sans test par construction. Ne
pas les compter sous une des 52 stories ci-dessus.

---

## Récapitulatif

- **Critères couverts par un test automatisé** : grande majorité des
  critères identifiables, sur les quatre sprints.
- **Critères recette manuelle** (limite de conception assumée ou jugement
  humain, aucun test possible par construction) : US-PLAN-12/US-PLAN-03
  (critère 6, grille active), US-SES-09 (C6), US-REF-09 (E4), US-EVAL-07
  (trois PDF relus visuellement), D-80/US-SES-02 (arbitrage non tranché),
  D-137/US-PLAN-04 (vérification terrain).
- **Critères reportés à une story ultérieure** : une dizaine, tous
  retrouvés et fermés par leur destination (listés story par story
  ci-dessus) — sauf US-REF-06 critère 4 (reporté du sprint 1 au sprint 3)
  et US-PLAN-07/E2 (déplacé au sprint 4 par un arbitrage de backlog,
  D-282), qui ont traversé une frontière de sprint.
- **Critères non identifiés** (survol insuffisant pour conclure, pas une
  absence confirmée) : une quinzaine au total, listés story par story —
  concentrés sur US-PLAN-05/E2, US-PLAN-06/R3/R5, US-VAL-01/C1-C2,
  US-VAL-02/C5, US-EVAL-01/D4/bloc F, US-EVAL-02/A2/A4, US-VAL-05/H3,
  US-EVAL-06/M1, US-SUI-03/B5, US-PLAN-11/D2, et la quasi-totalité du
  sprint 1 (convention de nommage absente).

Aucun nouveau test n'a été écrit pour produire cet inventaire.
