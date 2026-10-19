"""US-INS-04 — Consulter la charge d'un instructeur (prompt 48). Les
scénarios impliquant la surveillance d'épreuve (`evaluations.Surveillance`)
vivent ici : ni `planification` ni `ressources` ne peuvent importer
`evaluations` (sens de dépendance interdit — même motif que
`planification/tests/test_resolveur_charge_instructeur.py`, qui porte les
scénarios n'ayant besoin que de `Seance`). Données entièrement fictives.
"""

import datetime

from django.urls import reverse
from django.utils import timezone

from evaluations.models import OrganisationEpreuve, Surveillance
from ressources.selectors_charge import charge_d_un_instructeur

HEURE_8 = datetime.time(8, 0)
HEURE_10 = datetime.time(10, 0)


def _avec_creneau(evaluation, debut, fin):
    evaluation.heure_debut = debut
    evaluation.heure_fin = fin
    evaluation.save()
    return evaluation


def _periode_du_jour(jour):
    debut = timezone.make_aware(datetime.datetime.combine(jour, datetime.time.min))
    fin = timezone.make_aware(datetime.datetime.combine(jour, datetime.time.max))
    return debut, fin


def test_surveillance_hors_charge(certificative, brigade, lieu, instructeur):
    """C1 : la surveillance s'affiche à part et ne s'additionne jamais à la
    charge d'enseignement, seule comparée au seuil (C2)."""
    _avec_creneau(certificative, HEURE_8, HEURE_10)
    organisation = OrganisationEpreuve.objects.create(
        evaluation=certificative, brigade=brigade, lieu=lieu, effectif_attendu=5
    )
    Surveillance.objects.create(organisation=organisation, instructeur=instructeur)
    debut, fin = _periode_du_jour(certificative.date)

    ligne = charge_d_un_instructeur(instructeur, debut, fin)

    assert ligne.heures_surveillance == 2.0
    assert ligne.heures_enseignement == 0.0
    assert ligne.moyenne_hebdomadaire == 0.0
    assert ligne.seuil_franchi is False


def test_http_charge_instructeurs_pour_la_planification(client, planificateur, seance):
    client.force_login(planificateur)
    debut = (seance.debut - datetime.timedelta(days=1)).date()
    fin = (seance.debut + datetime.timedelta(days=1)).date()

    reponse = client.get(
        reverse("ressources:charge_instructeurs"),
        {"debut": debut.isoformat(), "fin": fin.isoformat()},
    )

    assert reponse.status_code == 200
    page = reponse.content.decode("utf-8")
    assert seance.instructeur.nom in page


def test_http_detail_par_matiere(client, planificateur, seance):
    client.force_login(planificateur)
    debut = (seance.debut - datetime.timedelta(days=1)).date()
    fin = (seance.debut + datetime.timedelta(days=1)).date()

    reponse = client.get(
        reverse("ressources:detail_charge_instructeur", args=[seance.instructeur.pk]),
        {"debut": debut.isoformat(), "fin": fin.isoformat()},
    )

    assert reponse.status_code == 200
    page = reponse.content.decode("utf-8")
    assert str(seance.element_referentiel.matiere) in page


def test_http_examens_refusee(client, examens):
    """C4 : la planification et les profils qui lisent les instructeurs —
    la Cellule examens n'en fait pas partie (`instructeurs_qualifications_
    lecture`, `administration/constantes.py::MATRICE`)."""
    client.force_login(examens)

    reponse = client.get(reverse("ressources:charge_instructeurs"))

    assert reponse.status_code == 403
