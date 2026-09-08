# Inventaire de couverture par le vrai cycle HTTP — bloc D, Prompt 19

Vérifié le 2026-09-08 sur le code réel (lecture des tests, pas une estimation
d'après leur nom). Un test compte seulement s'il appelle `reverse()` **et**
le client de test Django sur l'écran, et vérifie réellement l'effet (chemin
nominal) ou le refus HTTP (403/`PermissionDenied`) — un test qui appelle le
service directement, ou qui vérifie seulement qu'un lien est masqué dans le
HTML, ne compte pas.

`×` = test réel trouvé (fichier::fonction cité). Case vide = aucun test réel
trouvé. `N/A` = écran en lecture seule, la colonne écriture ne s'applique
pas.

| Écran (nom d'URL) | Story | Chemin nominal en écriture (HTTP réel) | Refus d'habilitation (HTTP réel) |
|---|---|---|---|
| connexion | US-ADM-01 | × (`test_vues_authentification.py::test_connexion_valide_redirige_vers_l_accueil`) | |
| deconnexion | US-ADM-01 | × (`test_vues_authentification.py::test_deconnexion_en_post_invalide_la_session`) | |
| changer_mot_de_passe | US-ADM-02 | × (`test_vues_comptes.py::test_apres_changement_reussi_acces_normal`) | |
| liste_comptes | US-ADM-02 | N/A | × (`test_vues_authentification.py::test_utilisateur_connecte_sans_le_droit_recoit_toujours_un_403`) |
| creer_compte | US-ADM-02 | | |
| modifier_compte | US-ADM-02 | | |
| desactiver_compte | US-ADM-02 | | |
| reactiver_compte | US-ADM-02 | | |
| habilitations | US-ADM-03 | | × (`test_acces_habilitations.py::test_acces_direct_a_l_url_sans_permission_est_refuse`) |
| journal | US-ADM-04 | N/A | × (`test_consultation_journal.py::test_un_non_administrateur_est_refuse`) |
| liste_types_formation | US-REF-00 | N/A | |
| creer_type_formation | US-REF-00 | | × (`test_refus_ecriture_direct.py`) |
| modifier_type_formation | US-REF-00 | × (`test_type_formation.py::test_modifier_par_le_vrai_formulaire_html_ne_declenche_pas_a_tort_e5`) | × (idem) |
| archiver_type_formation | US-REF-00 | | × (idem) |
| desarchiver_type_formation | US-REF-00 | | × (idem) |
| supprimer_type_formation | US-REF-00 | × (`test_type_formation.py::test_suppression_d_un_type_jamais_utilise_reussit_depuis_l_ecran`) | |
| liste_formations | US-REF-01 | N/A | |
| creer_formation | US-REF-01 | | × (`test_refus_ecriture_direct.py`) |
| detail_formation | US-REF-01 | N/A | |
| modifier_formation | US-REF-01 | × (`test_formation.py::test_modifier_par_le_vrai_formulaire_html_ne_declenche_pas_a_tort_e5`) | × (idem) |
| archiver_formation | US-REF-01 | | × (idem + `test_le_refus_est_journalise_une_fois_par_tentative`) |
| desarchiver_formation | US-REF-01 | | × (idem) |
| supprimer_formation | US-REF-01 | × (`test_formation.py::test_suppression_d_une_formation_jamais_utilisee_reussit_depuis_l_ecran`) | |
| liste_matieres | US-REF-02 | N/A | |
| creer_matiere | US-REF-02 | | × (idem `test_refus_ecriture_direct.py`) |
| detail_matiere | US-REF-02 | N/A | |
| modifier_matiere | US-REF-02 | × (`test_matiere.py::test_modifier_par_le_vrai_formulaire_html_ne_declenche_pas_a_tort_e5`) | × (idem) |
| archiver_matiere | US-REF-02 | | × (idem) |
| desarchiver_matiere | US-REF-02 | | × (idem) |
| supprimer_matiere | US-REF-02 | × (`test_matiere.py::test_suppression_d_une_matiere_jamais_utilisee_reussit_depuis_l_ecran`) | |
| referentiel_formation | US-REF-03/04 | N/A | |
| rattacher_matiere | US-REF-03/04 | | × (idem `test_refus_ecriture_direct.py`) |
| creer_matiere_depuis_referentiel | US-REF-03/04 | × (`test_referentiel_ecran.py::test_creation_d_une_matiere_depuis_le_dialogue_puis_reprise_au_rattachement`) | × (idem) |
| modifier_element_referentiel | US-REF-03/04 | | × (idem) |
| retirer_element_referentiel | US-REF-03/04 | × (`test_referentiel_ecran.py::test_retrait_confirme_supprime_l_element`) | × (idem) |
| ajouter_objectif_pedagogique | US-REF-05 | × (`test_objectif_pedagogique_ecran.py::test_ajout_d_un_objectif_depuis_la_fiche_matiere`) | × (idem + `test_lecteur_ne_peut_pas_ecrire_depuis_la_fiche_matiere`) |
| modifier_objectif_pedagogique | US-REF-05 | × (`test_objectif_pedagogique_ecran.py::test_modification_du_libelle_depuis_la_fiche_matiere`) | × (idem) |
| monter_objectif_pedagogique | US-REF-05 | | × (idem) |
| descendre_objectif_pedagogique | US-REF-05 | × (`test_objectif_pedagogique_ecran.py::test_monter_et_descendre_echangent_les_positions`) | × (idem) |
| supprimer_objectif_pedagogique | US-REF-05 | × (`test_objectif_pedagogique_ecran.py::test_suppression_confirmee_efface_l_objectif`) | × (idem) |
| prerequis_formation | US-REF-06 | N/A | |
| ajouter_prerequis | US-REF-06 | × (`test_prerequis_ecran.py::test_ajout_et_suppression_sont_journalises`) | × (idem + `test_lecteur_ne_peut_pas_ecrire_depuis_l_ecran_des_prerequis`) |
| supprimer_prerequis | US-REF-06 | × (`test_prerequis_ecran.py::test_ajout_et_suppression_sont_journalises`) | × (idem) |
| consultation_formation | US-REF-07 | N/A | |
| liste_lieux | US-PLAN-02 | N/A | |
| creer_lieu | US-PLAN-02 | | × (`test_lieu_ecran.py::test_pedagogie_ne_peut_pas_creer_par_appel_direct`, `test_examens_et_direction_lisent_seulement`) |
| detail_lieu | US-PLAN-02 | N/A | |
| modifier_lieu | US-PLAN-02 | × (`test_lieu_ecran.py::test_modifier_par_le_vrai_formulaire_html_ne_declenche_pas_a_tort_e5`) | |
| archiver_lieu | US-PLAN-02 | | |
| desarchiver_lieu | US-PLAN-02 | | |
| supprimer_lieu | US-PLAN-02 | × (`test_lieu_ecran.py::test_suppression_d_un_lieu_jamais_utilise_reussit_depuis_l_ecran`) | |
| declarer_indisponibilite_lieu | US-PLAN-02 | × (`test_lieu_ecran.py::test_declarer_une_indisponibilite_par_le_formulaire`) | × (`test_declarer_une_indisponibilite_refusee_a_la_cellule_pedagogique`) |
| modifier_indisponibilite_lieu | US-PLAN-02 | × (`test_indisponibilite_lieu.py::test_modification_d_une_indisponibilite_reussit_depuis_l_ecran`) | |
| supprimer_indisponibilite_lieu | US-PLAN-02 | × (`test_indisponibilite_lieu.py::test_suppression_d_une_indisponibilite_reussit_depuis_l_ecran`) | |
| liste_instructeurs | US-INS-01 | N/A | × (`test_instructeur_ecran.py::test_acces_direct_a_la_liste_refuse_a_la_cellule_examens`) |
| creer_instructeur | US-INS-01 | | × (`test_instructeur_ecran.py::test_planification_ne_peut_pas_creer_par_appel_direct`) |
| detail_instructeur | US-INS-01 | N/A | |
| modifier_instructeur | US-INS-01 | × (`test_instructeur_ecran.py::test_modifier_par_le_vrai_formulaire_html_ne_declenche_pas_a_tort_e5`) | |
| archiver_instructeur | US-INS-01 | | |
| desarchiver_instructeur | US-INS-01 | | |
| qualifications_instructeur | US-INS-02 | N/A | × (`test_qualification_ecran.py::test_cellule_examens_n_a_aucun_acces_a_l_ecran`) |
| ajouter_qualification_instructeur | US-INS-02 | × (`test_qualification_ecran.py::test_qualifier_depuis_l_entree_instructeur`) | × (`test_planification_ne_peut_pas_qualifier_par_appel_direct`) |
| qualifications_matiere | US-INS-02 | N/A | |
| ajouter_qualification_matiere | US-INS-02 | × (`test_qualification_ecran.py::test_qualifier_depuis_l_entree_matiere`) | |
| retirer_qualification_instructeur | US-INS-02 | × (`test_qualification_ecran.py::test_retrait_affiche_la_confirmation_puis_aboutit`) | |
| retirer_qualification_matiere | US-INS-02 | | |
| couverture_qualifications | US-INS-02 | N/A | |
| accueil | (squelette) | N/A | |

## Décompte

- **37 écrans** au total.
- **Chemin nominal en écriture** : 27 écrans concernés (10 en lecture seule,
  N/A) — **17 couverts par un test HTTP réel, 10 non couverts.**
- **Refus d'habilitation par un test HTTP réel** : **16 écrans sur 37**
  couverts, **21 non couverts** — dont plusieurs écrans en lecture qui
  n'ont, eux non plus, aucun test de refus HTTP (`detail_formation`,
  `detail_matiere`, `referentiel_formation`, `prerequis_formation`,
  `consultation_formation`, `detail_lieu`, `detail_instructeur`,
  `couverture_qualifications`).

## Angles morts les plus nets, relevés par l'audit

- **`administration:modifier_compte`, `desactiver_compte`, `reactiver_compte`**
  — aucun test HTTP réel du tout, ni écriture ni refus : uniquement des
  tests de service direct (`test_comptes.py`).
- **`administration:creer_compte`** — le seul test HTTP existant
  (`test_vues_comptes.py::test_mot_de_passe_initial_absent_de_toute_reponse_apres_creation`)
  vérifie l'absence du mot de passe dans la réponse, jamais que le compte a
  réellement été créé — ne compte donc pas comme preuve du chemin nominal.
- **`administration:habilitations`** — le seul test d'application de
  changements dit explicitement, dans sa propre docstring, qu'il ne passe
  pas par HTTP.
- **`referentiel:test_refus_ecriture_direct.py`** couvre le refus HTTP réel
  pour 23 adresses d'écriture en une seule fois — exemplaire — mais exclut
  délibérément les trois suppressions (`supprimer_type_formation`,
  `supprimer_formation`, `supprimer_matiere`), qui n'ont donc aucun test de
  refus HTTP.
- **`ressources:archiver_lieu`, `desarchiver_lieu`, `archiver_instructeur`,
  `desarchiver_instructeur`** — aucun test HTTP, ni écriture ni refus.
- **`ressources:creer_lieu`, `creer_instructeur`** — le refus est testé,
  mais aucun test de succès HTTP (seule la création directe via le service
  existe).
- **`ressources:retirer_qualification_matiere`** — aucune preuve HTTP,
  contrairement à son symétrique `retirer_qualification_instructeur`, bien
  testé.

## Ce que ce document ne fait pas

Ne comble aucun manque — c'est l'objet du bloc D.2, après validation. Point
d'arrêt : voir `docs/suivi/AVANCEMENT.md` pour la suite.
