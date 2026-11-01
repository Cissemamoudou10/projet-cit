"""US-REF-02 — cycle HTTP réel du catalogue des matières, scindé de
test_matiere.py qui dépassait 400 lignes (.claude/rules/python.md) après
les corrections du prompt 54.
"""

import pytest
from django.urls import reverse

from noyau.exceptions import ErreurModificationConcurrente
from referentiel.services.matiere import ServiceMatiere


def _donnees(**supplement):
    donnees = {"intitule": "Électronique numérique", "code": "ELN01"}
    donnees.update(supplement)
    return donnees


def test_les_trois_ecrans_du_referentiel_sont_croises(client, redacteur):
    client.force_login(redacteur)

    reponse_matieres = client.get(reverse("referentiel:liste_matieres"))
    reponse_types = client.get(reverse("referentiel:liste_types_formation"))
    reponse_formations = client.get(reverse("referentiel:liste_formations"))

    assert reverse("referentiel:liste_types_formation").encode() in reponse_matieres.content
    assert reverse("referentiel:liste_formations").encode() in reponse_matieres.content
    assert reverse("referentiel:liste_matieres").encode() in reponse_types.content
    assert reverse("referentiel:liste_matieres").encode() in reponse_formations.content


def test_le_bouton_modifier_de_la_liste_n_est_pas_casse_par_le_lien_de_l_intitule(
    client, redacteur
):
    """Voir referentiel/tests/test_formation.py — même correctif, même
    gabarit générique, exercé ici pour le catalogue des matières.
    """
    ServiceMatiere.creer(redacteur, _donnees())
    client.force_login(redacteur)

    reponse = client.get(reverse("referentiel:liste_matieres"))
    contenu = reponse.content.decode()

    assert 'aria-label="Modifier Électronique numérique"' in contenu
    assert "<a" not in contenu.split('aria-label="Modifier')[1].split('"')[0]


def test_modifier_par_le_vrai_formulaire_html_ne_declenche_pas_a_tort_e5(client, redacteur):
    """Voir referentiel/tests/test_type_formation.py et test_formation.py —
    même bug, même correctif, exercé ici pour le catalogue des matières.
    """
    matiere = ServiceMatiere.creer(redacteur, _donnees())
    client.force_login(redacteur)

    reponse_get = client.get(reverse("referentiel:modifier_matiere", args=[matiere.pk]))
    modifie_le_attendu = reponse_get.context["modifie_le_attendu"]

    reponse_post = client.post(
        reverse("referentiel:modifier_matiere", args=[matiere.pk]),
        {
            "intitule": matiere.intitule,
            "code": "ELN02",
            "modifie_le_attendu": modifie_le_attendu.isoformat(),
        },
    )

    assert reponse_post.status_code == 302
    matiere.refresh_from_db()
    assert matiere.code == "ELN02"


def test_modification_concurrente_est_detectee(redacteur):
    matiere = ServiceMatiere.creer(redacteur, _donnees())
    modifie_le_initial = matiere.modifie_le

    ServiceMatiere.modifier(redacteur, matiere.pk, _donnees(code="ELN02"), modifie_le_initial)

    with pytest.raises(ErreurModificationConcurrente) as info:
        ServiceMatiere.modifier(redacteur, matiere.pk, _donnees(code="ELN03"), modifie_le_initial)
    assert redacteur.username in str(info.value)
