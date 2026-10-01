"""US-EVAL-01, bloc C — insertion de la séance d'un contrôle à venir, par la
porte unique `ServiceEcritureSeance.inserer_seance_de_controle` (A3/D-177).
"""

import datetime

import pytest
from django.utils import timezone

from evaluations.models import Evaluation, TypeEvaluation
from evaluations.services.evaluation import ServiceEvaluation
from evaluations.tests.conftest import affecter_stagiaires, creer_brigade
from noyau.exceptions import ErreurValidation
from planification.models import EtatProgramme, ProgrammeHebdomadaire, Seance
from referentiel.models import CategorieLieu, ElementReferentiel


def _donnees(**kwargs):
    base = {
        "element_referentiel": None,
        "type": TypeEvaluation.FORMATIVE,
        "session": None,
        "brigade": None,
        "date": None,
        "creneau_type": None,
        "instructeur": None,
        "lieu": None,
        "motif_date_passee": "",
    }
    base.update(kwargs)
    return base


def test_c1_formative_future_brigade_seance_creee_verrouillee_une_ligne(controle):
    evaluation = ServiceEvaluation.creer(
        controle.examens,
        _donnees(
            element_referentiel=controle.element_referentiel,
            brigade=controle.brigade,
            date=controle.jour_creneau.jour,
            creneau_type=controle.jour_creneau.creneau,
            instructeur=controle.instructeur,
        ),
    )
    assert evaluation.seance_id is not None
    assert evaluation.seance.verrouillee is True
    assert evaluation.seance.lignes.count() == 1
    assert evaluation.seance.lignes.first().brigade_id == controle.brigade.pk
    assert evaluation.seance.programme.etat == EtatProgramme.BROUILLON


def test_c2_formative_future_session_trois_brigades_une_seance_trois_lignes(
    controle, redacteur, session
):
    creer_brigade(redacteur, session, "EXP2")
    creer_brigade(redacteur, session, "EXP3")
    evaluation = ServiceEvaluation.creer(
        controle.examens,
        _donnees(
            element_referentiel=controle.element_referentiel,
            session=session,
            date=controle.jour_creneau.jour,
            creneau_type=controle.jour_creneau.creneau,
            instructeur=controle.instructeur,
        ),
    )
    assert Seance.objects.filter(pk=evaluation.seance_id).count() == 1
    assert evaluation.seance.lignes.count() == 3


def test_c3_instructeur_deja_en_seance_refuse_aucune_evaluation_ni_seance(
    controle, redacteur, session
):
    brigade2 = creer_brigade(redacteur, session, "EXP2")
    ServiceEvaluation.creer(
        controle.examens,
        _donnees(
            element_referentiel=controle.element_referentiel,
            brigade=controle.brigade,
            date=controle.jour_creneau.jour,
            creneau_type=controle.jour_creneau.creneau,
            instructeur=controle.instructeur,
        ),
    )
    with pytest.raises(ErreurValidation, match="RG-34"):
        ServiceEvaluation.creer(
            controle.examens,
            _donnees(
                element_referentiel=controle.element_referentiel,
                brigade=brigade2,
                date=controle.jour_creneau.jour,
                creneau_type=controle.jour_creneau.creneau,
                instructeur=controle.instructeur,
            ),
        )
    assert Evaluation.objects.count() == 1
    assert Seance.objects.count() == 1


def test_c4_creneau_sur_periode_bloquante_refuse(controle):
    from ressources.models import (
        EffetPeriode,
        NatureEvenement,
        PeriodeCalendrier,
        PeriodeCalendrierBrigade,
    )

    jour = controle.jour_creneau.jour
    nature = NatureEvenement.objects.create(
        libelle="Indisponibilité EVAL", effet_par_defaut=EffetPeriode.BLOQUANT
    )
    debut = timezone.make_aware(datetime.datetime.combine(jour, datetime.time(0, 0)))
    fin = debut + datetime.timedelta(days=1)
    periode = PeriodeCalendrier.objects.create(
        nature=nature,
        intitule="Journée bloquée EVAL",
        debut=debut,
        fin=fin,
        effet=EffetPeriode.BLOQUANT,
    )
    PeriodeCalendrierBrigade.objects.create(periode=periode, brigade=controle.brigade)

    with pytest.raises(ErreurValidation, match="RG-38"):
        ServiceEvaluation.creer(
            controle.examens,
            _donnees(
                element_referentiel=controle.element_referentiel,
                brigade=controle.brigade,
                date=jour,
                creneau_type=controle.jour_creneau.creneau,
                instructeur=controle.instructeur,
            ),
        )
    assert Evaluation.objects.count() == 0
    assert Seance.objects.count() == 0


def test_c5_lieu_de_capacite_insuffisante_pour_la_session_refuse(controle, redacteur, session):
    from referentiel.models import Matiere
    from ressources.models import Lieu, Qualification

    brigade2 = creer_brigade(redacteur, session, "EXP2")
    matiere_lieu = Matiere.objects.create(intitule="Matière lieu EVAL", code=f"LIEUEV{session.pk}")
    element_lieu = ElementReferentiel.objects.create(
        formation=session.formation,
        matiere=matiere_lieu,
        volume_horaire_prescrit=20,
        categorie_lieu=CategorieLieu.LIEU_PARTAGE,
        type_lieu_partage="amphitheatre",
    )
    Qualification.objects.create(instructeur=controle.instructeur, matiere=matiere_lieu)
    petit_lieu = Lieu.objects.create(
        intitule="Petite salle EVAL",
        capacite=1,
        categorie="lieu_partage",
        type_partage="amphitheatre",
    )
    affecter_stagiaires(redacteur, controle.brigade, 3, prefixe="C5A")
    affecter_stagiaires(redacteur, brigade2, 3, prefixe="C5B")

    with pytest.raises(ErreurValidation, match="RG-37"):
        ServiceEvaluation.creer(
            controle.examens,
            _donnees(
                element_referentiel=element_lieu,
                session=session,
                date=controle.jour_creneau.jour,
                creneau_type=controle.jour_creneau.creneau,
                instructeur=controle.instructeur,
                lieu=petit_lieu,
            ),
        )


def _element_plein_et_seance_existante(controle, formation):
    """Module au volume déjà épuisé par une séance d'une AUTRE semaine —
    préparation extraite pour rester sous 40 lignes (`.claude/rules/
    python.md`). `element_plein` doit appartenir à la formation de
    `controle.brigade` (celle de `formation`, § 3, Prompt 35) — sinon
    `_verifier_module` (C2/E1) refuserait avant même d'atteindre RG-39 a)."""
    from referentiel.models import Matiere
    from ressources.models import Qualification

    matiere_pleine = Matiere.objects.create(intitule="Matière pleine EVAL", code="PLEINEV")
    element_plein = ElementReferentiel.objects.create(
        formation=formation,
        matiere=matiere_pleine,
        volume_horaire_prescrit=1,
        categorie_lieu=CategorieLieu.AUCUN_LIEU,
    )
    Qualification.objects.get_or_create(instructeur=controle.instructeur, matiere=matiere_pleine)

    jour = controle.jour_creneau.jour
    creneau = controle.jour_creneau.creneau
    programme = ProgrammeHebdomadaire.objects.create(
        lundi_de_semaine=jour - datetime.timedelta(days=jour.weekday())
    )
    debut = timezone.make_aware(datetime.datetime.combine(jour, creneau.heure_debut))
    fin = timezone.make_aware(datetime.datetime.combine(jour, creneau.heure_fin))
    Seance.objects.create(
        programme=programme,
        element_referentiel=element_plein,
        instructeur=controle.instructeur,
        debut=debut - datetime.timedelta(days=1),
        fin=fin - datetime.timedelta(days=1),
        verrouillee=False,
    )
    return element_plein


def test_c6_volume_du_module_deja_atteint_refuse(controle, formation):
    element_plein = _element_plein_et_seance_existante(controle, formation)
    with pytest.raises(ErreurValidation, match="RG-39"):
        ServiceEvaluation.creer(
            controle.examens,
            _donnees(
                element_referentiel=element_plein,
                brigade=controle.brigade,
                date=controle.jour_creneau.jour,
                creneau_type=controle.jour_creneau.creneau,
                instructeur=controle.instructeur,
            ),
        )


def test_c7_regeneration_de_la_brigade_preserve_la_seance_du_controle(controle, planificateur):
    from planification.services.generation import ServiceGeneration

    evaluation = ServiceEvaluation.creer(
        controle.examens,
        _donnees(
            element_referentiel=controle.element_referentiel,
            brigade=controle.brigade,
            date=controle.jour_creneau.jour,
            creneau_type=controle.jour_creneau.creneau,
            instructeur=controle.instructeur,
        ),
    )
    lundi = controle.jour_creneau.jour - datetime.timedelta(
        days=controle.jour_creneau.jour.weekday()
    )
    ServiceGeneration.generer(planificateur, lundi, [controle.brigade])
    assert Seance.objects.filter(pk=evaluation.seance_id).exists()


def test_c8_echec_de_creation_de_l_evaluation_apres_ecriture_de_la_seance_aucune_orpheline(
    monkeypatch, controle
):
    from noyau.services import base as base_module

    original = base_module.ServiceBase.creer

    def _creer_qui_echoue_pour_l_evaluation(instance, utilisateur):
        if isinstance(instance, Evaluation):
            raise RuntimeError("échec simulé après écriture de la séance")
        return original(instance, utilisateur)

    monkeypatch.setattr(base_module.ServiceBase, "creer", _creer_qui_echoue_pour_l_evaluation)

    with pytest.raises(RuntimeError):
        ServiceEvaluation.creer(
            controle.examens,
            _donnees(
                element_referentiel=controle.element_referentiel,
                brigade=controle.brigade,
                date=controle.jour_creneau.jour,
                creneau_type=controle.jour_creneau.creneau,
                instructeur=controle.instructeur,
            ),
        )
    assert Seance.objects.count() == 0
    assert Evaluation.objects.count() == 0
