"""US-SES-03 — cycle HTTP réel (`reverse()` + `client`), Groupe C (Prompt 22,
§ 9). Le refus d'habilitation en écriture (C2, C4) et le test de garde
mécanique (C5) sont couverts une fois pour toutes par
tests/architecture/test_ecrans_ecriture.py.
"""

import pytest
from django.urls import reverse

from ressources.models import CategorieLieu, Lieu, SalleAttitree
from ressources.services.salle_attitree import ServiceSalleAttitree


def _autre_lieu(lieu):
    return Lieu.objects.create(
        intitule="Salle C1 bis", capacite=lieu.capacite, categorie=CategorieLieu.SALLE_ATTITREE
    )


def test_c1_attribuer_par_l_ecran_cree_reellement_la_salle(client, planificateur, brigade, lieu):
    client.force_login(planificateur)

    assert client.get(reverse("ressources:affecter_salle", args=[brigade.pk])).status_code == 200

    reponse = client.post(reverse("ressources:soumettre_salle", args=[brigade.pk]), {"lieu": lieu.pk})

    assert reponse.status_code == 302
    assert SalleAttitree.objects.filter(brigade=brigade, lieu=lieu).exists()


def test_c1_changer_par_l_ecran_modifie_reellement_la_salle(client, planificateur, brigade, lieu):
    autre_lieu_pk = _autre_lieu(lieu).pk
    ServiceSalleAttitree.attribuer(planificateur, brigade, lieu)
    client.force_login(planificateur)

    reponse = client.post(
        reverse("ressources:soumettre_salle", args=[brigade.pk]), {"lieu": autre_lieu_pk}
    )

    assert reponse.status_code == 302
    salle = SalleAttitree.objects.get(brigade=brigade)
    assert salle.lieu_id == autre_lieu_pk


def test_c1_retirer_par_l_ecran_retire_reellement_la_salle(client, planificateur, brigade, lieu):
    ServiceSalleAttitree.attribuer(planificateur, brigade, lieu)
    client.force_login(planificateur)

    reponse = client.post(reverse("ressources:retirer_salle", args=[brigade.pk]))

    assert reponse.status_code == 302
    assert not SalleAttitree.objects.filter(brigade=brigade).exists()


def test_c2_pedagogique_lit_mais_ne_peut_pas_ecrire_sur_les_salles(client, redacteur, brigade, lieu):
    """Matérialise le partage décidé par le terrain (§ 6, Prompt 22) : la
    cellule pédagogique crée les brigades mais ne peut pas leur attribuer de
    salle — refus d'écriture, pas un oubli de permission."""
    client.force_login(redacteur)

    assert client.get(reverse("ressources:affecter_salle", args=[brigade.pk])).status_code == 200
    reponse = client.post(reverse("ressources:soumettre_salle", args=[brigade.pk]), {"lieu": lieu.pk})

    assert reponse.status_code == 403
    assert not SalleAttitree.objects.filter(brigade=brigade).exists()


def test_c3_planification_ne_peut_pas_ecrire_sur_les_brigades(client, planificateur, session):
    """Pendant du test précédent (§ 6, Prompt 22) : la cellule planification
    attribue les salles mais ne peut ni créer, ni modifier, ni supprimer une
    brigade."""
    client.force_login(planificateur)

    reponse = client.post(
        reverse("organisation:creer_brigade", args=[session.pk]),
        {"designation": "EXP-refus", "effectif_previsionnel": 10},
    )

    assert reponse.status_code == 403


@pytest.mark.parametrize("nom_utilisateur", ["redacteur", "direction_formation"])
def test_c4_lecture_accordee_ecriture_refusee_pedagogique_direction(
    client, request, nom_utilisateur, brigade, lieu
):
    client.force_login(request.getfixturevalue(nom_utilisateur))

    assert client.get(reverse("ressources:affecter_salle", args=[brigade.pk])).status_code == 200
    reponse = client.post(reverse("ressources:soumettre_salle", args=[brigade.pk]), {"lieu": lieu.pk})

    assert reponse.status_code == 403


def test_c4_administrateur_aucun_acces(client, administrateur, brigade):
    client.force_login(administrateur)

    reponse = client.get(reverse("ressources:affecter_salle", args=[brigade.pk]))

    assert reponse.status_code == 403


def test_c6_lien_atteignable_pour_planification_absent_sinon(
    client, planificateur, redacteur, session, brigade
):
    client.force_login(planificateur)
    reponse = client.get(reverse("organisation:brigades_session", args=[session.pk]))
    assert reverse("ressources:affecter_salle", args=[brigade.pk]) in reponse.content.decode()

    client.force_login(redacteur)
    reponse = client.get(reverse("organisation:brigades_session", args=[session.pk]))
    assert reverse("ressources:affecter_salle", args=[brigade.pk]) not in reponse.content.decode()


def test_c7_salle_attitree_affichee_sur_l_ecran_des_brigades(
    client, planificateur, redacteur, brigade, lieu
):
    ServiceSalleAttitree.attribuer(planificateur, brigade, lieu)
    client.force_login(redacteur)

    reponse = client.get(reverse("organisation:brigades_session", args=[brigade.session.pk]))

    assert lieu.intitule in reponse.content.decode()


def test_c8_fiche_lieu_affiche_reellement_les_brigades_attitrees(
    client, planificateur, brigade, lieu
):
    ServiceSalleAttitree.attribuer(planificateur, brigade, lieu)
    client.force_login(planificateur)

    reponse = client.get(reverse("ressources:detail_lieu", args=[lieu.pk]))
    contenu = reponse.content.decode()

    assert brigade.designation in contenu
    assert brigade.session.intitule in contenu


def test_c9_refus_de_suppression_d_un_lieu_attitre_par_le_vrai_cycle_http(
    client, planificateur, brigade, lieu
):
    ServiceSalleAttitree.attribuer(planificateur, brigade, lieu)
    client.force_login(planificateur)

    client.post(reverse("ressources:supprimer_lieu", args=[lieu.pk]))

    assert Lieu.objects.filter(pk=lieu.pk).exists()
