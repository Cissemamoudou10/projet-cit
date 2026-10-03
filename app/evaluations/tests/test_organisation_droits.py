"""US-EVAL-04, F4 — habilitations de lecture et d'écriture de l'organisation d'épreuve :
planification, pédagogique et administrateur sont refusés, en HTTP et en appel direct
au service. Données entièrement fictives.
"""

import pytest
from django.urls import reverse

from evaluations.services.organisation import ServiceOrganisationEpreuve as Service
from noyau.exceptions import ErreurHabilitation
from noyau.habilitations import a_permission

PROFILS_SANS_EVALUATIONS = ["planificateur", "redacteur", "administrateur"]


@pytest.mark.parametrize("profil", PROFILS_SANS_EVALUATIONS)
def test_f4_lecture_refusee_en_http(client, request, profil, epreuve_creneau):
    utilisateur = request.getfixturevalue(profil)
    client.force_login(utilisateur)
    assert (
        client.get(reverse("evaluations:organisation", args=[epreuve_creneau.pk])).status_code
        == 403
    )
    assert (
        client.get(reverse("evaluations:convocation", args=[epreuve_creneau.pk])).status_code == 403
    )


@pytest.mark.parametrize("profil", PROFILS_SANS_EVALUATIONS)
def test_f4_ecriture_refusee_en_appel_direct_au_service(
    request, profil, epreuve_creneau, brigade, salle_f4
):
    utilisateur = request.getfixturevalue(profil)
    assert not a_permission(utilisateur, "noyau.evaluations_lecture")
    with pytest.raises(ErreurHabilitation):
        Service.ajouter_organisation(utilisateur, epreuve_creneau, brigade, salle_f4, 1)
    with pytest.raises(ErreurHabilitation):
        Service.fixer_creneau(
            utilisateur, epreuve_creneau, epreuve_creneau.heure_debut, epreuve_creneau.heure_fin
        )


@pytest.fixture
def salle_f4(db):
    from ressources.models import Lieu

    return Lieu.objects.create(intitule="Salle F4", capacite=30, categorie="salle_attitree")


@pytest.fixture
def epreuve_creneau(certificative, examens):
    import datetime

    return Service.fixer_creneau(examens, certificative, datetime.time(8, 0), datetime.time(10, 0))
