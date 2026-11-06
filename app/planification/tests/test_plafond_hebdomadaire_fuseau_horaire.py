"""K7, prompt 58 (RECETTE-01) : trois sources du même `RuntimeWarning`
« DateTimeField ... received a naive datetime », pervasif dans toute la
suite, invisible fonctionnellement tant qu'`Africa/Casablanca` (fuseau du
projet) reste à UTC+0, comme sur toute la période couverte par le jeu de
recette (mi-octobre à mi-novembre 2026) — et jamais vérifié après son
retour à UTC+1 (~11 novembre 2026, selon la base tzdata installée) :
`_charger_donnees_calcul` (RG-66, `generation.plafond_hebdomadaire`),
`decorer_rapprochement` (US-SUI-02, `selectors_alerte_ecart`, D-308) et
`tableau_de_bord` (US-SUI-03, `selectors_tableau_bord`, trouvée après coup
par la même suite). Ces tests portent sur une semaine POSTÉRIEURE à ce
changement, pour que l'absence d'avertissement et la détection de la
période bloquante soient vérifiées dans le fuseau qui aurait exposé le
défaut. Données entièrement fictives.
"""

import datetime
import warnings

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command

from organisation.services.brigade import ServiceBrigade
from organisation.services.session import ServiceSession
from planification.generation.plafond_hebdomadaire import _charger_donnees_calcul
from referentiel.models import CategorieLieu, ElementReferentiel, Formation, Matiere, TypeFormation
from ressources.models import NatureEvenement
from ressources.services.periode_calendrier import DonneesPeriode, ServicePeriodeCalendrier

LUNDI_APRES_RETOUR_UTC1 = datetime.date(2026, 11, 16)  # postérieur au ~11/11/2026


def _utilisateur(username, profil, groupe):
    modele = get_user_model()
    utilisateur = modele.objects.create_user(username=username, password="x", profil=profil)
    utilisateur.groups.add(Group.objects.get(name=groupe))
    utilisateur.doit_changer_mot_de_passe = False
    utilisateur.save()
    return utilisateur


@pytest.fixture
def _brigade_apres_retour_utc1(db):
    call_command("initialiser_habilitations")
    planificateur = _utilisateur("plan-fh", "cellule_planification", "Cellule planification")
    redacteur = _utilisateur("ped-fh", "cellule_pedagogique", "Cellule pédagogique")
    formation = Formation.objects.create(
        intitule="Formation fuseau horaire",
        specialite="Transmissions",
        duree_semaines=20,
        type_formation=TypeFormation.objects.create(intitule="Type fuseau horaire"),
    )
    ElementReferentiel.objects.create(
        formation=formation,
        matiere=Matiere.objects.create(intitule="Matière fuseau horaire", code="FH1"),
        volume_horaire_prescrit=10,
        categorie_lieu=CategorieLieu.AUCUN_LIEU,
    )
    session = ServiceSession.creer(
        redacteur,
        {
            "formation": formation,
            "intitule": "Session fuseau horaire",
            "date_debut": datetime.date(2026, 9, 1),
            "date_fin": datetime.date(2027, 3, 1),
            "effectif_attendu": 20,
        },
    )
    brigade = ServiceBrigade.creer(
        redacteur, session, {"designation": "EXP-FH", "effectif_previsionnel": 20}
    )
    return planificateur, brigade


def test_sans_avertissement_de_datetime_naif_apres_le_retour_a_utc_plus_1(
    _brigade_apres_retour_utc1,
):
    _, brigade = _brigade_apres_retour_utc1
    with warnings.catch_warnings(record=True) as capturees:
        warnings.simplefilter("always")
        _charger_donnees_calcul({}, [brigade], [], LUNDI_APRES_RETOUR_UTC1)
    avertissements_naifs = [
        w for w in capturees if "naive datetime" in str(w.message)
    ]
    assert not avertissements_naifs, avertissements_naifs


def test_periode_bloquante_detectee_apres_le_retour_a_utc_plus_1(_brigade_apres_retour_utc1):
    planificateur, brigade = _brigade_apres_retour_utc1
    nature = NatureEvenement.objects.create(libelle="Bivouac fuseau horaire", effet_par_defaut="bloquant")
    jeudi = LUNDI_APRES_RETOUR_UTC1 + datetime.timedelta(days=3)
    ServicePeriodeCalendrier.creer(
        planificateur,
        DonneesPeriode(
            nature=nature,
            intitule="Bivouac EXP-FH (fuseau horaire)",
            debut=datetime.datetime.combine(jeudi, datetime.time(8, 0), tzinfo=datetime.UTC),
            fin=datetime.datetime.combine(jeudi, datetime.time(16, 0), tzinfo=datetime.UTC),
            effet="",
            sessions=[],
            brigades=[brigade],
        ),
    )

    donnees = _charger_donnees_calcul({}, [brigade], [], LUNDI_APRES_RETOUR_UTC1)

    assert any(brigade.pk in p["brigades"] for p in donnees.periodes_bloquantes)


def test_tableau_de_bord_sans_avertissement_de_datetime_naif_apres_le_retour_a_utc_plus_1(
    _brigade_apres_retour_utc1,
):
    from freezegun import freeze_time

    from planification.selectors_tableau_bord import tableau_de_bord

    instant = datetime.datetime.combine(
        LUNDI_APRES_RETOUR_UTC1, datetime.time(9, 0), tzinfo=datetime.UTC
    )
    with freeze_time(instant), warnings.catch_warnings(record=True) as capturees:
        warnings.simplefilter("always")
        tableau_de_bord()
    avertissements_naifs = [w for w in capturees if "naive datetime" in str(w.message)]
    assert not avertissements_naifs, avertissements_naifs
