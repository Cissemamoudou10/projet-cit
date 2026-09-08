"""US-REF-01 — chemin nominal en écriture par le vrai cycle HTTP, bloc D.2
du Prompt 19, priorité 3. Extrait de test_formation.py (limite de 400 lignes,
`.claude/rules/python.md`) : preuve d'un effet réel, pas d'un code de
retour (P-21).
"""

from django.urls import reverse

from referentiel.models import Formation
from referentiel.services.formation import ServiceFormation
from referentiel.tests.test_formation import _donnees


def test_creer_par_l_ecran_cree_reellement_la_formation(client, redacteur, type_officiers):
    client.force_login(redacteur)

    client.post(
        reverse("referentiel:creer_formation"),
        {
            "intitule": "Formation initiale",
            "specialite": "Transmissions",
            "duree_semaines": 12,
            "type_formation": type_officiers.pk,
        },
    )

    assert Formation.objects.filter(intitule="Formation initiale").exists()


def test_archiver_par_l_ecran_la_retire_reellement_de_la_selection(
    client, redacteur, type_officiers
):
    formation = ServiceFormation.creer(redacteur, _donnees(type_officiers))
    client.force_login(redacteur)

    client.post(reverse("referentiel:archiver_formation", args=[formation.pk]))

    assert formation.pk not in [f.pk for f in ServiceFormation.disponibles_pour_selection()]


def test_desarchiver_par_l_ecran_la_rend_reellement_a_la_selection(
    client, redacteur, type_officiers
):
    formation = ServiceFormation.creer(redacteur, _donnees(type_officiers))
    ServiceFormation.archiver(redacteur, formation.pk)
    client.force_login(redacteur)

    client.post(reverse("referentiel:desarchiver_formation", args=[formation.pk]))

    assert formation.pk in [f.pk for f in ServiceFormation.disponibles_pour_selection()]
