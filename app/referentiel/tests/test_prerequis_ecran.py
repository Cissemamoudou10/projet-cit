"""US-REF-06 — écrans des prérequis et fermeture de RG-07. Le graphe et le
service sont testés dans test_prerequis.py.
"""

import pytest
from django.urls import reverse

from administration.models import EntreeJournal, TypeAction
from noyau.exceptions import ErreurValidation
from referentiel.models import ElementReferentiel, Formation, Prerequis
from referentiel.services.prerequis import ServicePrerequis
from referentiel.services.referentiel import ServiceReferentiel
from referentiel.tests.conftest import creer_element

# --- RG-07 : retrait bloqué par un prérequis ---


def test_retrait_d_une_matiere_liee_par_un_prerequis_est_refuse(redacteur, formation):
    a = creer_element(formation, "Analyse de signal")
    b = creer_element(formation, "Bases électroniques")
    ServicePrerequis.ajouter(redacteur, formation, a, b)

    with pytest.raises(ErreurValidation) as info:
        ServiceReferentiel.retirer(redacteur, b)

    assert "Analyse de signal" in str(info.value)
    assert ElementReferentiel.objects.filter(pk=b.pk).exists()


def test_retrait_refuse_meme_cote_prerequis(redacteur, formation):
    """RG-07 bloque dans les deux sens : que l'élément exige ou soit exigé."""
    a = creer_element(formation, "Analyse de signal")
    b = creer_element(formation, "Bases électroniques")
    ServicePrerequis.ajouter(redacteur, formation, a, b)

    with pytest.raises(ErreurValidation) as info:
        ServiceReferentiel.retirer(redacteur, a)

    assert "Bases électroniques" in str(info.value)


def test_retrait_par_la_vue_est_refuse_et_affiche_les_liens(client, redacteur, formation):
    a = creer_element(formation, "Analyse de signal")
    b = creer_element(formation, "Bases électroniques")
    ServicePrerequis.ajouter(redacteur, formation, a, b)
    client.force_login(redacteur)

    reponse = client.post(
        reverse("referentiel:retirer_element_referentiel", args=[formation.pk, b.pk]), follow=True
    )

    assert ElementReferentiel.objects.filter(pk=b.pk).exists()
    assert "Analyse de signal" in reponse.content.decode()


def test_suppression_d_un_element_sans_prerequis_reste_possible(redacteur, formation):
    a = creer_element(formation, "Analyse de signal")

    ServiceReferentiel.retirer(redacteur, a)  # ne lève pas

    assert not ElementReferentiel.objects.filter(pk=a.pk).exists()


def test_suppression_directe_d_un_element_efface_ses_liens_par_cascade(formation):
    """La cascade posée en base (§ 6) n'est qu'un filet — ce test la
    contourne le service pour la prouver directement, en ORM.
    """
    a = creer_element(formation, "Analyse de signal")
    b = creer_element(formation, "Bases électroniques")
    Prerequis.objects.create(element=a, element_prerequis=b)

    b.delete()

    assert not Prerequis.objects.filter(element=a, element_prerequis=b.pk).exists()


# --- Écran ---


def test_moins_de_deux_matieres_affiche_l_ecran_d_orientation(
    client, redacteur, formation, matiere
):
    client.force_login(redacteur)

    reponse = client.get(reverse("referentiel:prerequis_formation", args=[formation.pk]))

    assert reponse.status_code == 200
    assert "au moins deux" in reponse.content.decode().lower()


def test_la_liste_deroulante_n_offre_ni_la_matiere_elle_meme_ni_un_autre_referentiel(
    client, redacteur, formation, type_officiers
):
    autre_formation = Formation.objects.create(
        intitule="Formation continue",
        specialite="Transmissions",
        duree_semaines=4,
        type_formation=type_officiers,
    )
    a = creer_element(formation, "Analyse de signal")
    b = creer_element(formation, "Bases électroniques")
    creer_element(autre_formation, "Hors référentiel")
    client.force_login(redacteur)

    reponse = client.get(reverse("referentiel:prerequis_formation", args=[formation.pk]))

    disponibles_pour_a = reponse.context["elements"][0].elements_disponibles_affiches
    assert a not in disponibles_pour_a
    assert all(element.formation_id == formation.pk for element in disponibles_pour_a)
    assert b in disponibles_pour_a


def test_ajout_et_suppression_sont_journalises(client, redacteur, formation):
    a = creer_element(formation, "Analyse de signal")
    b = creer_element(formation, "Bases électroniques")
    client.force_login(redacteur)

    client.post(
        reverse("referentiel:ajouter_prerequis", args=[formation.pk, a.pk]),
        {"element_prerequis": b.pk},
    )
    lien = Prerequis.objects.get(element=a, element_prerequis=b)
    client.post(reverse("referentiel:supprimer_prerequis", args=[formation.pk, lien.pk]))

    natures = list(
        EntreeJournal.objects.filter(objet_type="prerequis").values_list("type_action", flat=True)
    )
    assert TypeAction.CREATION_ELEMENT_GESTION in natures
    assert TypeAction.SUPPRESSION_ELEMENT_GESTION in natures


def test_ajout_par_la_vue_signale_un_cycle(client, redacteur, formation):
    a = creer_element(formation, "Analyse de signal")
    b = creer_element(formation, "Bases électroniques")
    ServicePrerequis.ajouter(redacteur, formation, a, b)
    client.force_login(redacteur)

    reponse = client.post(
        reverse("referentiel:ajouter_prerequis", args=[formation.pk, b.pk]),
        {"element_prerequis": a.pk},
        follow=True,
    )

    assert not Prerequis.objects.filter(element=b, element_prerequis=a).exists()
    assert "cycle" in reponse.content.decode().lower()


def test_suppression_demande_confirmation_avant_execution(client, redacteur, formation):
    a = creer_element(formation, "Analyse de signal")
    b = creer_element(formation, "Bases électroniques")
    lien = ServicePrerequis.ajouter(redacteur, formation, a, b)
    client.force_login(redacteur)

    reponse = client.get(reverse("referentiel:supprimer_prerequis", args=[formation.pk, lien.pk]))

    assert reponse.status_code == 200
    assert Prerequis.objects.filter(pk=lien.pk).exists()


def test_lecteur_ne_peut_pas_ecrire_depuis_l_ecran_des_prerequis(client, lecteur, formation):
    a = creer_element(formation, "Analyse de signal")
    b = creer_element(formation, "Bases électroniques")
    client.force_login(lecteur)

    reponse = client.post(
        reverse("referentiel:ajouter_prerequis", args=[formation.pk, a.pk]),
        {"element_prerequis": b.pk},
    )

    assert reponse.status_code == 403
    assert not Prerequis.objects.filter(element=a, element_prerequis=b).exists()
