"""US-SES-06 — proposition de répartition, sans écriture (Prompt 25, § 12,
Groupe A). Données entièrement fictives.
"""

import datetime

from organisation.models import AffectationBrigade
from organisation.repartition.proposition import proposer
from organisation.services.brigade import ServiceBrigade
from organisation.services.stagiaire import ServiceStagiaire
from organisation.tests.conftest import donnees_brigade, donnees_stagiaire


def _creer_stagiaires(redacteur, session, nombre):
    return [
        ServiceStagiaire.creer(
            redacteur, session, donnees_stagiaire(matricule=f"M{i:03d}", nom=f"Nom{i:03d}")
        )
        for i in range(nombre)
    ]


def _creer_brigades(redacteur, session, effectifs):
    return [
        ServiceBrigade.creer(
            redacteur,
            session,
            donnees_brigade(designation=f"EXP{i}", effectif_previsionnel=effectif),
        )
        for i, effectif in enumerate(effectifs, start=1)
    ]


def test_a1_proposition_nominale_58_stagiaires_20_20_18_aucune_affectation_en_base(
    redacteur, session
):
    _creer_stagiaires(redacteur, session, 58)
    brigades = _creer_brigades(redacteur, session, [20, 20, 18])

    proposition = proposer(session)

    comptes = {b.pk: 0 for b in brigades}
    for _, brigade_id in proposition.affectations:
        comptes[brigade_id] += 1
    assert sorted(comptes.values()) == [18, 20, 20]
    assert not proposition.non_affectes
    assert AffectationBrigade.objects.count() == 0


def test_a2_surnombre_surplus_non_affecte_aucune_brigade_ne_depasse_aucune_creee(
    redacteur, session
):
    _creer_stagiaires(redacteur, session, 45)
    _creer_brigades(redacteur, session, [20, 20])

    proposition = proposer(session)

    assert len(proposition.affectations) == 40
    assert len(proposition.non_affectes) == 5
    assert ServiceBrigade.lister(redacteur, session).count() == 2


def test_a3_nombre_insuffisant_brigades_non_pleines_aucun_avertissement(redacteur, session):
    _creer_stagiaires(redacteur, session, 10)
    brigades = _creer_brigades(redacteur, session, [20, 20])

    proposition = proposer(session)

    comptes = {b.pk: 0 for b in brigades}
    for _, brigade_id in proposition.affectations:
        comptes[brigade_id] += 1
    assert sum(comptes.values()) == 10
    assert not proposition.non_affectes


def test_a4_determinisme_deux_appels_successifs_meme_proposition(redacteur, session):
    _creer_stagiaires(redacteur, session, 30)
    _creer_brigades(redacteur, session, [20, 20])

    premiere = proposer(session)
    seconde = proposer(session)

    assert premiere == seconde


def test_a5_stagiaires_radies_ne_figurent_pas_dans_la_proposition(redacteur, session):
    stagiaires = _creer_stagiaires(redacteur, session, 3)
    _creer_brigades(redacteur, session, [20])
    ServiceStagiaire.radier(redacteur, stagiaires[0], "Fin anticipée", datetime.date.today())

    proposition = proposer(session)

    ids_proposes = {s for s, _ in proposition.affectations} | set(proposition.non_affectes)
    assert stagiaires[0].pk not in ids_proposes
    assert len(ids_proposes) == 2


def test_a6_stagiaires_deja_affectes_ne_figurent_pas_dans_la_proposition(redacteur, session):
    stagiaires = _creer_stagiaires(redacteur, session, 3)
    brigades = _creer_brigades(redacteur, session, [20])
    AffectationBrigade.objects.create(
        stagiaire=stagiaires[0], brigade=brigades[0], date_effet=datetime.date.today()
    )

    proposition = proposer(session)

    ids_proposes = {s for s, _ in proposition.affectations} | set(proposition.non_affectes)
    assert stagiaires[0].pk not in ids_proposes
    assert len(ids_proposes) == 2
