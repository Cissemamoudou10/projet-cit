"""US-EVAL-04, bloc D — sens P5 → P6 (A6) : une organisation d'épreuve occupe son
lieu et ses surveillants pour `ServiceContraintes`, comme une séance. Les
contraintes restent six. Prompt 38. Données entièrement fictives.
"""

import datetime

from django.utils import timezone

from evaluations.services.organisation import ServiceOrganisationEpreuve as Service
from evaluations.tests.conftest import creer_brigade
from noyau.intervalles import instant_de
from noyau.services.parametres import ResolveurOccupationsEpreuves
from planification.models import ProgrammeHebdomadaire
from planification.services.contraintes import Candidate, ServiceContraintes
from ressources.models import Lieu

H8, H10 = datetime.time(8, 0), datetime.time(10, 0)


def _candidate(brigade, element, instructeur, lieu, creneau):
    """`creneau` : (date, heure de début, heure de fin)."""
    date, heure_debut, heure_fin = creneau
    return Candidate(
        brigade=brigade,
        element_referentiel=element,
        instructeur=instructeur,
        debut=instant_de(date, heure_debut),
        fin=instant_de(date, heure_fin),
        lieu=lieu,
    )


def _brigade_autre_session(redacteur, formation):
    """Brigade hors session de l'épreuve : RG-38 (jour d'examen) ne la concerne pas."""
    from organisation.services.session import ServiceSession

    session = ServiceSession.creer(
        redacteur,
        {
            "formation": formation,
            "intitule": "Session D1 hors épreuve",
            "date_debut": timezone.localdate(),
            "date_fin": timezone.localdate() + datetime.timedelta(days=90),
            "effectif_attendu": 10,
        },
    )
    return creer_brigade(redacteur, session, "D-HORS")


def _verdict(candidate, date):
    programme = ProgrammeHebdomadaire.objects.create(
        lundi_de_semaine=date - datetime.timedelta(days=date.weekday())
    )
    contexte = ServiceContraintes.contexte(programme)
    return ServiceContraintes.verifier(candidate, contexte)


def _epreuve_avec_salle(certificative, examens, brigade, salle):
    Service.fixer_creneau(examens, certificative, H8, H10)
    organisation = Service.ajouter_organisation(examens, certificative, brigade, salle, 1)
    Service.ajouter_surveillant(examens, organisation, nom_libre="Surveillant externe")
    return organisation


def test_d1_seance_dans_la_salle_d_examen_sur_un_creneau_secant_refusee(
    certificative, examens, instructeur, redacteur, formation
):
    salle = Lieu.objects.create(intitule="Salle D1", capacite=30, categorie="salle_attitree")
    brigade = creer_brigade(redacteur, certificative.session, "D1-EPREUVE")
    _epreuve_avec_salle(certificative, examens, brigade, salle)
    autre = _brigade_autre_session(redacteur, formation)

    candidate = _candidate(
        autre,
        certificative.element_referentiel,
        instructeur,
        salle,
        (certificative.date, datetime.time(9, 0), datetime.time(10, 30)),
    )
    codes = {v["code"] for v in _verdict(candidate, certificative.date).violations}

    assert "RG-37" in codes


def test_d2_instructeur_surveillant_une_epreuve_refuse_une_seance_secante(
    certificative, examens, instructeur, redacteur, formation
):
    brigade = creer_brigade(redacteur, certificative.session, "D2-EPREUVE")
    Service.fixer_creneau(examens, certificative, H8, H10)
    organisation = Service.ajouter_organisation(examens, certificative, brigade, None, 1)
    Service.ajouter_surveillant(examens, organisation, instructeur=instructeur)
    autre = _brigade_autre_session(redacteur, formation)

    candidate = _candidate(
        autre,
        certificative.element_referentiel,
        instructeur,
        None,
        (certificative.date, datetime.time(9, 0), datetime.time(10, 30)),
    )
    codes = {v["code"] for v in _verdict(candidate, certificative.date).violations}

    assert "RG-34" in codes


def test_d4_sans_fournisseur_aucune_occupation_et_contraintes_fonctionnelles(
    monkeypatch, certificative
):
    monkeypatch.setattr(ResolveurOccupationsEpreuves, "_fournisseur", None)
    debut = timezone.make_aware(datetime.datetime.combine(certificative.date, datetime.time.min))
    assert ResolveurOccupationsEpreuves.resoudre(debut, debut + datetime.timedelta(days=7)) == []
