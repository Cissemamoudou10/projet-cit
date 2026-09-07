"""US-INS-02 — Établir la matrice de qualification, CU-P4-02. Le modèle, la
symétrie des deux entrées et le service — les écrans sont dans
test_qualification_ecran.py.
"""

import pytest
from django.db import IntegrityError, transaction
from django.db.models import ForeignKey
from django.test import Client
from django.urls import reverse

from administration.models import EntreeJournal, TypeAction
from noyau.exceptions import ErreurHabilitation, ErreurValidation
from referentiel.models import ElementReferentiel, Matiere
from referentiel.services.matiere import ServiceMatiere
from referentiel.services.referentiel import ServiceReferentiel
from referentiel.tests.conftest import donnees_element_referentiel
from ressources.models import Instructeur, Qualification
from ressources.services.qualification import ServiceQualification


def test_une_qualification_lie_un_instructeur_a_une_matiere_du_catalogue(
    redacteur, instructeur, matiere
):
    qualification = ServiceQualification.ajouter(redacteur, instructeur, matiere)

    assert qualification.instructeur_id == instructeur.pk
    assert qualification.matiere_id == matiere.pk


def test_qualification_ne_porte_aucune_cle_etrangere_vers_element_referentiel():
    """Test de non-présence, § 2 : la qualification cible le catalogue,
    jamais un élément du référentiel d'une formation précise."""
    cibles = {
        champ.related_model
        for champ in Qualification._meta.get_fields()
        if isinstance(champ, ForeignKey) and champ.name not in ("cree_par", "modifie_par")
    }
    assert ElementReferentiel not in cibles
    assert Matiere in cibles
    assert Instructeur in cibles


def test_qualification_ne_porte_ni_niveau_ni_date_ni_commentaire():
    """Test de non-présence, § 2 : deux colonnes, rien de plus — le point de
    conception écarte explicitement toute anticipation."""
    noms_champs = {champ.name for champ in Qualification._meta.fields}
    interdits = {"niveau", "date_validite", "commentaire"}
    assert not (noms_champs & interdits)


def test_un_instructeur_qualifie_pour_plusieurs_matieres(redacteur, instructeur, matiere):
    autre_matiere = Matiere.objects.create(intitule="Radiocommunications", code="RAD01")

    ServiceQualification.ajouter(redacteur, instructeur, matiere)
    ServiceQualification.ajouter(redacteur, instructeur, autre_matiere)

    assert instructeur.qualifications.count() == 2


def test_une_matiere_comptant_plusieurs_instructeurs(redacteur, instructeur, matiere):
    autre_instructeur = Instructeur.objects.create(
        nom="Alaoui",
        prenom="Yassine",
        matricule=None,
        grade="Lt",
        specialite="Transmissions",
        statut="vacataire",
    )

    ServiceQualification.ajouter(redacteur, instructeur, matiere)
    ServiceQualification.ajouter(redacteur, autre_instructeur, matiere)

    assert matiere.qualifications.count() == 2


def test_doublon_refuse_en_base(db, instructeur, matiere):
    Qualification.objects.create(instructeur=instructeur, matiere=matiere)

    with pytest.raises(IntegrityError), transaction.atomic():
        Qualification.objects.create(instructeur=instructeur, matiere=matiere)


def test_suppression_d_une_matiere_qualifiee_est_refusee_par_le_service(
    redacteur, instructeur, matiere
):
    """Prompt 16, cause racine n° 3, critère 5 : une matière qualifiée ne
    peut plus être supprimée du catalogue (RG-22, `ressources/models.py`).
    Vit ici, pas dans `referentiel/tests/` : `referentiel` ne peut pas
    importer `ressources` (ordre des dépendances, test d'architecture)."""
    ServiceQualification.ajouter(redacteur, instructeur, matiere)

    with pytest.raises(ErreurValidation) as info:
        ServiceMatiere.supprimer(redacteur, matiere.pk)
    assert str(instructeur) in str(info.value)
    assert Matiere.objects.filter(pk=matiere.pk).exists()


def test_colonne_instructeurs_qualifies_du_catalogue_exclut_les_archives(
    redacteur, instructeur, matiere
):
    """Prompt 17, § 2.1 : le compteur de la liste des matières ne compte
    que les instructeurs non archivés — un instructeur archivé ne peut plus
    être affecté, le compter laisserait croire une matière couverte."""
    archive = Instructeur.objects.create(
        nom="Retraité",
        prenom="Ancien",
        matricule="M99999",
        grade="Cne",
        specialite="Transmissions",
        statut="militaire_du_centre",
        archive=True,
    )
    ServiceQualification.ajouter(redacteur, instructeur, matiere)
    ServiceQualification.ajouter(redacteur, archive, matiere)

    page = ServiceMatiere.lister(redacteur, {}, None)
    ligne = next(m for m in page if m.pk == matiere.pk)

    assert ligne.nombre_instructeurs_qualifies == 1


def test_la_vue_consolidee_du_referentiel_affiche_le_nombre_d_instructeurs_qualifies(
    redacteur, direction_formation, instructeur, matiere, formation
):
    """Prompt 17, § 2.2 — voir referentiel/tests/test_couverture_consultation.py
    pour le cas « aucun ». `client` n'est pas un paramètre : au-delà de cinq,
    le patron de test l'instancie lui-même (.claude/rules/python.md)."""
    client = Client()
    ServiceReferentiel.rattacher(redacteur, formation, matiere, donnees_element_referentiel())
    ServiceQualification.ajouter(redacteur, instructeur, matiere)
    client.force_login(direction_formation)

    reponse = client.get(reverse("referentiel:consultation_formation", args=[formation.pk]))

    assert "AUCUN" not in reponse.content.decode()
    assert ">1<" in reponse.content.decode()


def test_doublon_refuse_avec_message_exploitable(redacteur, instructeur, matiere):
    ServiceQualification.ajouter(redacteur, instructeur, matiere)

    with pytest.raises(ErreurValidation) as info:
        ServiceQualification.ajouter(redacteur, instructeur, matiere)

    assert "Ziani" in str(info.value)
    assert "Électronique numérique" in str(info.value)


def test_creee_par_l_entree_instructeur_visible_par_l_entree_matiere(
    redacteur, instructeur, matiere
):
    ServiceQualification.ajouter(redacteur, instructeur, matiere)

    instructeurs = ServiceQualification.instructeurs_avec_etat(redacteur, matiere)

    assert next(i for i in instructeurs if i.pk == instructeur.pk).est_qualifie


def test_creee_par_l_entree_matiere_visible_par_l_entree_instructeur(
    redacteur, instructeur, matiere
):
    ServiceQualification.ajouter(redacteur, instructeur, matiere)

    page = ServiceQualification.matieres_avec_etat(redacteur, instructeur, {}, None)

    assert next(m for m in page if m.pk == matiere.pk).est_qualifiee


def test_suppression_d_une_matiere_qualifiee_est_refusee(redacteur, instructeur, matiere):
    """Referme le second volet du report D-30 (US-REF-02, écart 2) — la
    première source (référentiel) était déjà fermée depuis US-REF-03, sans
    l'avoir consigné (voir docs/suivi/DECISIONS.md)."""
    ServiceQualification.ajouter(redacteur, instructeur, matiere)

    with pytest.raises(IntegrityError), transaction.atomic():
        matiere.delete()

    ServiceMatiere.obtenir(matiere.pk)  # toujours là


def test_suppression_d_un_instructeur_efface_ses_qualifications_par_cascade(instructeur, matiere):
    Qualification.objects.create(instructeur=instructeur, matiere=matiere)

    instructeur.delete()

    assert not Qualification.objects.filter(matiere=matiere).exists()


def test_ajout_et_retrait_sont_journalises(redacteur, instructeur, matiere):
    qualification = ServiceQualification.ajouter(redacteur, instructeur, matiere)
    ServiceQualification.retirer(redacteur, qualification)

    natures = list(
        EntreeJournal.objects.filter(objet_type="qualification")
        .order_by("cree_le")
        .values_list("type_action", flat=True)
    )
    assert TypeAction.CREATION_ELEMENT_GESTION in natures
    assert TypeAction.SUPPRESSION_ELEMENT_GESTION in natures


def test_retrait_laissant_une_matiere_non_couverte_aboutit_avec_avertissement(
    redacteur, instructeur, matiere
):
    qualification = ServiceQualification.ajouter(redacteur, instructeur, matiere)

    assert ServiceQualification.laisserait_la_matiere_non_couverte(qualification)

    ServiceQualification.retirer(redacteur, qualification)  # ne lève pas, § 3.4

    assert not Qualification.objects.filter(pk=qualification.pk).exists()


def test_retrait_ne_laissant_pas_la_matiere_decouverte_n_avertit_pas(
    redacteur, instructeur, matiere
):
    autre_instructeur = Instructeur.objects.create(
        nom="Alaoui",
        prenom="Yassine",
        matricule=None,
        grade="Lt",
        specialite="Transmissions",
        statut="vacataire",
    )
    qualification = ServiceQualification.ajouter(redacteur, instructeur, matiere)
    ServiceQualification.ajouter(redacteur, autre_instructeur, matiere)

    assert not ServiceQualification.laisserait_la_matiere_non_couverte(qualification)


def test_la_methode_de_verification_d_e1_existe_et_rend_une_liste_vide(
    redacteur, instructeur, matiere
):
    """§ 3.2 : les séances arrivent au sprint 3 — US-PLAN-03 remplira cette
    méthode."""
    qualification = ServiceQualification.ajouter(redacteur, instructeur, matiere)

    assert ServiceQualification.seances_futures(qualification) == []


def test_cellule_pedagogique_ecrit(redacteur, instructeur, matiere):
    ServiceQualification.ajouter(redacteur, instructeur, matiere)  # ne lève pas


def test_planification_et_direction_formation_lisent_seulement(
    planificateur, direction_formation, instructeur, matiere
):
    ServiceQualification.instructeurs_avec_etat(planificateur, matiere)  # ne lève pas
    ServiceQualification.instructeurs_avec_etat(direction_formation, matiere)  # ne lève pas

    with pytest.raises(ErreurHabilitation):
        ServiceQualification.ajouter(planificateur, instructeur, matiere)
    with pytest.raises(ErreurHabilitation):
        ServiceQualification.ajouter(direction_formation, instructeur, matiere)


def test_cellule_examens_n_a_aucun_acces(cellule_examens, instructeur, matiere):
    with pytest.raises(ErreurHabilitation):
        ServiceQualification.instructeurs_avec_etat(cellule_examens, matiere)
    with pytest.raises(ErreurHabilitation):
        ServiceQualification.ajouter(cellule_examens, instructeur, matiere)
