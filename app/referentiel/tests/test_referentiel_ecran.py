"""US-REF-03 + US-REF-04 — le déroulement (rattachement, retrait, dialogue
de création) et les écrans. Le modèle et ses contraintes sont dans
test_referentiel.py.
"""

import pytest
from django.test import override_settings
from django.urls import reverse

from administration.models import EntreeJournal, TypeAction
from noyau.exceptions import ErreurHabilitation, ErreurValidation
from referentiel.models import CategorieLieu, ElementReferentiel, Matiere, TypeLieuPartage
from referentiel.services.referentiel import ServiceReferentiel
from referentiel.tests.conftest import donnees_element_referentiel as _donnees

# --- Le déroulement ---


def test_rattachement_volume_categorie_enregistres_et_total_recalcule(
    redacteur, formation, matiere
):
    ServiceReferentiel.rattacher(redacteur, formation, matiere, _donnees())

    assert ServiceReferentiel.total_volume(formation) == 40


def test_chaque_rattachement_est_journalise(redacteur, formation, matiere):
    ServiceReferentiel.rattacher(redacteur, formation, matiere, _donnees())

    assert EntreeJournal.objects.filter(
        objet_type="element_referentiel",
        type_action=TypeAction.CREATION_ELEMENT_GESTION,
        objet_identifiant__icontains="électronique numérique",
    ).exists()


def test_doublon_est_refuse_en_proposant_la_modification_du_volume_existant(
    redacteur, formation, matiere
):
    ServiceReferentiel.rattacher(
        redacteur, formation, matiere, _donnees(volume_horaire_prescrit=40)
    )

    with pytest.raises(ErreurValidation) as info:
        ServiceReferentiel.rattacher(
            redacteur, formation, matiere, _donnees(volume_horaire_prescrit=20)
        )

    assert "40" in str(info.value)
    assert "modifiez" in str(info.value).lower()


def test_volume_non_conforme_est_refuse_avec_l_intervalle_attendu(redacteur, formation, matiere):
    with pytest.raises(ErreurValidation) as info:
        ServiceReferentiel.rattacher(
            redacteur, formation, matiere, _donnees(volume_horaire_prescrit=0)
        )

    assert "1" in str(info.value)


def test_retrait_par_la_vue_demande_confirmation_avant_execution(
    client, redacteur, formation, matiere
):
    element = ServiceReferentiel.rattacher(redacteur, formation, matiere, _donnees())
    client.force_login(redacteur)

    reponse = client.get(
        reverse("referentiel:retirer_element_referentiel", args=[formation.pk, element.pk])
    )

    assert reponse.status_code == 200
    assert ElementReferentiel.objects.filter(pk=element.pk).exists()


def test_retrait_confirme_supprime_l_element(client, redacteur, formation, matiere):
    element = ServiceReferentiel.rattacher(redacteur, formation, matiere, _donnees())
    client.force_login(redacteur)

    client.post(reverse("referentiel:retirer_element_referentiel", args=[formation.pk, element.pk]))

    assert not ElementReferentiel.objects.filter(pk=element.pk).exists()


def test_methode_d_enumeration_des_bloquants_existe_et_ne_trouve_rien(
    redacteur, formation, matiere
):
    """§ 3.3 : deux des trois sources de RG-07 (prérequis, évaluation)
    n'existent pas encore, et la troisième (séance programmée) est reportée
    à US-PLAN — l'énumération ne trouve donc rien aujourd'hui, ce qui est
    le comportement attendu, pas un défaut.
    """
    element = ServiceReferentiel.rattacher(redacteur, formation, matiere, _donnees())

    ServiceReferentiel.retirer(redacteur, element)  # ne lève pas

    assert not ElementReferentiel.objects.filter(pk=element.pk).exists()


def test_le_dialogue_de_creation_est_un_ecran_dedie(client, redacteur, formation):
    """§ 3.32 : un `<dialog>` sans script ne se centre en superposition que
    sur un écran qui ne contient rien d'autre que lui — voir le gabarit de
    confirmation d'archivage, déjà bâti sur ce principe.
    """
    client.force_login(redacteur)

    reponse = client.get(
        reverse("referentiel:creer_matiere_depuis_referentiel", args=[formation.pk])
    )

    assert reponse.status_code == 200
    assert "dialog" in reponse.content.decode().lower()


def test_creation_d_une_matiere_depuis_le_dialogue_puis_reprise_au_rattachement(
    client, redacteur, formation
):
    client.force_login(redacteur)

    reponse = client.post(
        reverse("referentiel:creer_matiere_depuis_referentiel", args=[formation.pk]),
        {"intitule": "Cryptographie", "code": ""},
    )

    matiere_creee = Matiere.objects.get(intitule="Cryptographie")
    assert reponse.status_code == 302
    assert str(matiere_creee.pk) in reponse.url

    reponse_page = client.get(reponse.url)
    assert reponse_page.context["formulaire_rattachement"].initial["matiere"] == str(
        matiere_creee.pk
    )


def test_le_dialogue_appelle_le_service_de_matiere_sans_le_reecrire(client, redacteur, formation):
    """§ 3.4 : la matière créée depuis le dialogue est journalisée comme
    n'importe quelle matière d'US-REF-02 — preuve que c'est bien
    ServiceMatiere.creer qui est appelé, pas une création parallèle.
    """
    client.force_login(redacteur)

    client.post(
        reverse("referentiel:creer_matiere_depuis_referentiel", args=[formation.pk]),
        {"intitule": "Cryptographie", "code": ""},
    )

    assert EntreeJournal.objects.filter(
        objet_type="matiere",
        type_action=TypeAction.CREATION_ELEMENT_GESTION,
        objet_identifiant__icontains="cryptographie",
    ).exists()


# --- Le total et l'écart ---


def test_le_total_est_la_somme_des_volumes(redacteur, formation, matiere, type_officiers):
    autre_matiere = Matiere.objects.create(intitule="Réseaux", code="")
    ServiceReferentiel.rattacher(
        redacteur, formation, matiere, _donnees(volume_horaire_prescrit=40)
    )
    ServiceReferentiel.rattacher(
        redacteur, formation, autre_matiere, _donnees(volume_horaire_prescrit=15)
    )

    assert ServiceReferentiel.total_volume(formation) == 55


@override_settings(
    VOLUME_HORAIRE_HEBDOMADAIRE_REFERENCE=30, SEUIL_ECART_VOLUME_REFERENTIEL_POURCENT=10
)
def test_ecart_au_dela_du_seuil_declenche_l_avertissement(redacteur, formation, matiere):
    # formation.duree_semaines = 10 → attendu 300 h ; total très inférieur.
    ServiceReferentiel.rattacher(
        redacteur, formation, matiere, _donnees(volume_horaire_prescrit=40)
    )

    ecart = ServiceReferentiel.ecart(formation)

    assert ecart["depasse_seuil"] is True


def test_avertissement_n_empeche_pas_l_enregistrement(redacteur, formation, matiere):
    element = ServiceReferentiel.rattacher(
        redacteur, formation, matiere, _donnees(volume_horaire_prescrit=1)
    )  # ne lève pas, malgré un écart énorme

    assert ElementReferentiel.objects.filter(pk=element.pk).exists()


@override_settings(VOLUME_HORAIRE_HEBDOMADAIRE_REFERENCE=99)
def test_le_parametre_de_conversion_est_lu_non_code_en_dur(formation):
    ecart = ServiceReferentiel.ecart(formation)

    assert ecart["attendu"] == formation.duree_semaines * 99


# --- Habilitation ---


def test_cellule_pedagogique_ecrit(redacteur, formation, matiere):
    ServiceReferentiel.rattacher(redacteur, formation, matiere, _donnees())  # ne lève pas


def test_planification_examens_direction_lisent_seulement(lecteur, formation, matiere):
    ServiceReferentiel.lister(lecteur, formation)  # ne lève pas

    with pytest.raises(ErreurHabilitation):
        ServiceReferentiel.rattacher(lecteur, formation, matiere, _donnees())


# --- Rendu de l'écran, avec au moins une ligne (tableau + formulaires) ---


def test_la_page_du_referentiel_rend_avec_une_ligne_rattachee(
    client, redacteur, formation, matiere
):
    ServiceReferentiel.rattacher(
        redacteur,
        formation,
        matiere,
        _donnees(
            categorie_lieu=CategorieLieu.LIEU_PARTAGE, type_lieu_partage=TypeLieuPartage.LABORATOIRE
        ),
    )
    client.force_login(redacteur)

    reponse = client.get(reverse("referentiel:referentiel_formation", args=[formation.pk]))

    assert reponse.status_code == 200
    assert "Électronique numérique" in reponse.content.decode()
