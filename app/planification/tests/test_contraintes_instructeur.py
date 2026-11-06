"""US-PLAN-04, Groupes B (RG-34), C (RG-35), D (RG-36) — Prompt 30, § 4/§ 8.
Données entièrement fictives.
"""

import datetime

from planification.models import LigneProgramme, Seance
from planification.services.contraintes import Candidate, ServiceContraintes
from planification.tests.conftest import creer_element, instant, qualifier
from ressources.models import IndisponibiliteInstructeur


def _candidate(brigade, element, instructeur, debut, duree_min=105, **kw):
    fin = debut + datetime.timedelta(minutes=duree_min)
    return Candidate(
        brigade=brigade,
        element_referentiel=element,
        instructeur=instructeur,
        debut=debut,
        fin=fin,
        **kw,
    )


def _seance_existante(programme, element, instructeur, brigade, debut):
    fin = debut + datetime.timedelta(minutes=105)
    seance = Seance.objects.create(
        programme=programme,
        element_referentiel=element,
        instructeur=instructeur,
        debut=debut,
        fin=fin,
    )
    LigneProgramme.objects.create(seance=seance, brigade=brigade)
    return seance


# --- B1/B2 — RG-34, refus toutes brigades et sessions confondues -----------


def test_b1_deux_seances_memes_instructeur_creneaux_secants_brigades_differentes_refus(
    programme, element_referentiel, instructeur, brigade, autre_brigade
):
    lundi = programme.lundi_de_semaine
    qualifier(instructeur, element_referentiel.matiere)
    _seance_existante(programme, element_referentiel, instructeur, brigade, instant(lundi, 0, 8))
    candidate = _candidate(
        autre_brigade, element_referentiel, instructeur, instant(lundi, 0, 8, 30)
    )

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert not verdict.accepte
    codes = [v["code"] for v in verdict.violations]
    assert "RG-34" in codes


def test_b2_brigades_de_deux_sessions_differentes_refus(
    programme, element_referentiel, instructeur, brigade, brigade_autre_session
):
    """Test central : la portée « toutes sessions confondues » de RG-34."""
    lundi = programme.lundi_de_semaine
    qualifier(instructeur, element_referentiel.matiere)
    _seance_existante(programme, element_referentiel, instructeur, brigade, instant(lundi, 0, 8))
    candidate = _candidate(
        brigade_autre_session, element_referentiel, instructeur, instant(lundi, 0, 8, 30)
    )

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert not verdict.accepte
    assert any(v["code"] == "RG-34" for v in verdict.violations)


# --- B3 — séance regroupée : exception à RG-34 ------------------------------


def test_b3_seance_regroupee_trois_brigades_meme_instructeur_acceptee(
    programme, element_referentiel, instructeur, brigade, autre_brigade
):
    from organisation.services.brigade import ServiceBrigade

    lundi = programme.lundi_de_semaine
    troisieme_brigade = ServiceBrigade.creer(
        brigade.cree_par, brigade.session, {"designation": "EXP3", "effectif_previsionnel": 15}
    )
    qualifier(instructeur, element_referentiel.matiere)
    candidates = [
        _candidate(
            b, element_referentiel, instructeur, instant(lundi, 0, 8), cle_regroupement="groupe-1"
        )
        for b in (brigade, autre_brigade, troisieme_brigade)
    ]

    verdicts = ServiceContraintes.verifier_lot(candidates, ServiceContraintes.contexte(programme))

    assert all(verdict.accepte for verdict in verdicts)


# --- B4/B5 — contigus et disjoints, acceptés --------------------------------


def test_b4_creneaux_contigus_fin_de_l_un_egale_au_debut_du_suivant_acceptes(
    programme, element_referentiel, instructeur, brigade, autre_brigade
):
    lundi = programme.lundi_de_semaine
    qualifier(instructeur, element_referentiel.matiere)
    _seance_existante(programme, element_referentiel, instructeur, brigade, instant(lundi, 0, 8))
    candidate = _candidate(
        autre_brigade, element_referentiel, instructeur, instant(lundi, 0, 9, 45), duree_min=105
    )

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert verdict.accepte


def test_b5_seances_du_meme_instructeur_sur_des_creneaux_disjoints_acceptees(
    programme, element_referentiel, instructeur, brigade, autre_brigade
):
    lundi = programme.lundi_de_semaine
    qualifier(instructeur, element_referentiel.matiere)
    _seance_existante(programme, element_referentiel, instructeur, brigade, instant(lundi, 0, 8))
    candidate = _candidate(
        autre_brigade, element_referentiel, instructeur, instant(lundi, 0, 13), duree_min=75
    )

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert verdict.accepte


# --- C1/C2 — RG-35, qualification -------------------------------------------


def test_c1_instructeur_non_qualifie_refus_matiere_et_instructeur_nommes(
    programme, element_referentiel, instructeur, brigade
):
    candidate = _candidate(
        brigade, element_referentiel, instructeur, instant(programme.lundi_de_semaine, 0, 8)
    )

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert not verdict.accepte
    violation = next(v for v in verdict.violations if v["code"] == "RG-35")
    assert str(instructeur) in violation["message"]
    assert str(element_referentiel.matiere) in violation["message"]


def _element_et_brigade_sur_une_nouvelle_formation(redacteur, type_formation, intitule, matiere):
    from organisation.services.brigade import ServiceBrigade
    from organisation.services.session import ServiceSession
    from referentiel.models import Formation

    formation = Formation.objects.create(
        intitule=intitule, specialite="Transmissions", duree_semaines=8, type_formation=type_formation
    )
    element = creer_element(formation, matiere)
    aujourd_hui = datetime.date.today()
    session = ServiceSession.creer(
        redacteur,
        {
            "formation": formation,
            "intitule": f"Session {intitule}",
            "date_debut": aujourd_hui + datetime.timedelta(days=30),
            "date_fin": aujourd_hui + datetime.timedelta(days=111),
            "effectif_attendu": 24,
        },
    )
    brigade = ServiceBrigade.creer(
        redacteur, session, {"designation": "C2B1", "effectif_previsionnel": 20}
    )
    return element, brigade


def test_c2_instructeur_qualifie_via_une_autre_formation_accepte(
    programme, instructeur, brigade, matiere, redacteur
):
    """La qualification est indépendante de la formation (CLS-03) : un
    instructeur qualifié pour une matière peut l'enseigner dans N'IMPORTE
    QUELLE formation qui la porte. La brigade candidate doit néanmoins
    suivre CETTE formation (RG-05, D-309, prompt 58) — construite ici sur
    `autre_formation` elle-même, jamais sur `brigade` (formation partagée),
    pour isoler RG-35 sans jamais exercer RG-05."""
    element_autre_formation, brigade_autre_formation = _element_et_brigade_sur_une_nouvelle_formation(
        redacteur, brigade.session.formation.type_formation, "Formation C2", matiere
    )
    qualifier(instructeur, matiere)
    candidate = _candidate(
        brigade_autre_formation,
        element_autre_formation,
        instructeur,
        instant(programme.lundi_de_semaine, 0, 8),
    )

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert verdict.accepte


# --- D1/D2/D3 — RG-36, disponibilité ----------------------------------------


def test_d1_seance_recouvrant_une_indisponibilite_refus_periode_nommee(
    programme, element_referentiel, instructeur, brigade
):
    lundi = programme.lundi_de_semaine
    qualifier(instructeur, element_referentiel.matiere)
    IndisponibiliteInstructeur.objects.create(
        instructeur=instructeur,
        debut=instant(lundi, 0, 7),
        fin=instant(lundi, 0, 10),
        motif="Mission extérieure",
    )
    candidate = _candidate(brigade, element_referentiel, instructeur, instant(lundi, 0, 8))

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert not verdict.accepte
    violation = next(v for v in verdict.violations if v["code"] == "RG-36")
    assert str(instructeur) in violation["message"]


def test_d2_bornes_semi_ouvertes_seance_finissant_quand_l_indisponibilite_commence_acceptee(
    programme, element_referentiel, instructeur, brigade
):
    lundi = programme.lundi_de_semaine
    qualifier(instructeur, element_referentiel.matiere)
    IndisponibiliteInstructeur.objects.create(
        instructeur=instructeur,
        debut=instant(lundi, 0, 9, 45),
        fin=instant(lundi, 0, 12),
        motif="Mission extérieure",
    )
    candidate = _candidate(
        brigade, element_referentiel, instructeur, instant(lundi, 0, 8), duree_min=105
    )

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert verdict.accepte


def test_d3_indisponibilite_d_un_autre_instructeur_sans_effet(
    programme, element_referentiel, instructeur, autre_instructeur, brigade
):
    lundi = programme.lundi_de_semaine
    qualifier(instructeur, element_referentiel.matiere)
    IndisponibiliteInstructeur.objects.create(
        instructeur=autre_instructeur,
        debut=instant(lundi, 0, 7),
        fin=instant(lundi, 0, 10),
        motif="Mission extérieure",
    )
    candidate = _candidate(brigade, element_referentiel, instructeur, instant(lundi, 0, 8))

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert verdict.accepte
