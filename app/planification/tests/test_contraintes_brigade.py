"""RG-67 — une brigade ne peut pas avoir deux séances qui se chevauchent.

Découverte en recette (RECETTE-01, A10/A1/A6 b, prompt 58) : la génération
posait une candidate sur le créneau d'une séance verrouillée de la même
brigade (contrôle ou saisie manuelle), et l'affichage écrasait l'une des
deux en silence. Données entièrement fictives.
"""

import dataclasses
import datetime

import pytest

from noyau.exceptions import ErreurValidation
from planification.generation.candidats import brigade_deja_occupee, construire_cases
from planification.models import LigneProgramme, ProgrammeHebdomadaire, Seance
from planification.selectors_consultation import grille_consultation
from planification.services.contraintes import Candidate, ServiceContraintes
from planification.services.ecriture import ServiceEcritureSeance
from planification.services.generation import ServiceGeneration
from planification.services.modification import _contexte_sans_la_seance
from planification.services.regroupement import associer_brigades
from planification.tests.conftest import Cours, creer_element, instant, qualifier
from referentiel.models import CategorieLieu, Matiere, TypeLieuPartage
from ressources.models import CreneauType, GrilleHoraire


@dataclasses.dataclass(frozen=True)
class Base:
    """`.claude/rules/python.md`, § 5 paramètres max : ce module teste
    surtout des combinaisons de brigades/séances, regroupées ici plutôt que
    listées une à une dans chaque test."""

    programme: object
    formation: object
    matiere: object
    instructeur: object
    brigade: object


@pytest.fixture
def base(programme, formation, matiere, instructeur, brigade_formation):
    """`brigade_formation` (session ouverte sur `formation`), jamais la
    `brigade` générique (session avec sa PROPRE formation, sans rapport) :
    `test_refuse_en_modification_manuelle` change l'élément d'une séance de
    cette brigade, que RG-05 (K3, prompt 58) refuserait sinon pour une
    raison étrangère à RG-67, ce que ce module ne teste pas."""
    return Base(programme, formation, matiere, instructeur, brigade_formation)


@dataclasses.dataclass(frozen=True)
class BasePartage(Base):
    autre_brigade: object = None
    lieu_partage: object = None


@pytest.fixture
def base_partage(base, autre_brigade, lieu_partage):
    return BasePartage(**dataclasses.asdict(base), autre_brigade=autre_brigade, lieu_partage=lieu_partage)


def _candidate(brigade, cours, debut, duree_min=120, **kw):
    fin = debut + datetime.timedelta(minutes=duree_min)
    return Candidate(
        brigade=brigade,
        element_referentiel=cours.element,
        instructeur=cours.instructeur,
        debut=debut,
        fin=fin,
        **kw,
    )


def _seance_verrouillee(programme, cours, brigade, debut, duree_min=105):
    fin = debut + datetime.timedelta(minutes=duree_min)
    seance = Seance.objects.create(
        programme=programme,
        element_referentiel=cours.element,
        instructeur=cours.instructeur,
        debut=debut,
        fin=fin,
        verrouillee=True,
    )
    LigneProgramme.objects.create(seance=seance, brigade=brigade)
    return seance


def _seance_partagee(base_p, cours, debut, brigades):
    seance = Seance.objects.create(
        programme=base_p.programme,
        element_referentiel=cours.element,
        instructeur=cours.instructeur,
        lieu=base_p.lieu_partage,
        debut=debut,
        fin=debut + datetime.timedelta(hours=2),
    )
    for brigade in brigades:
        LigneProgramme.objects.create(seance=seance, brigade=brigade)
    return seance


def _cours_partage(base_p):
    element = creer_element(
        base_p.formation,
        base_p.matiere,
        categorie=CategorieLieu.LIEU_PARTAGE,
        type_lieu_partage=TypeLieuPartage.AMPHITHEATRE,
    )
    qualifier(base_p.instructeur, base_p.matiere)
    return Cours(element, base_p.instructeur)


# --- Service de contraintes, directement ------------------------------------


def test_refuse_en_modification_manuelle(base, planificateur):
    """K1, point (1) : RG-67 passe par `ServiceEcritureSeance.modifier_seance`
    (modification manuelle), même porte que toutes les autres."""
    cours = Cours(creer_element(base.formation, base.matiere), base.instructeur)
    qualifier(base.instructeur, base.matiere)
    lundi = base.programme.lundi_de_semaine
    _seance_verrouillee(base.programme, cours, base.brigade, instant(lundi, 0, 8))
    element_2 = creer_element(base.formation, Matiere.objects.create(intitule="Matière à déplacer", code="DEP01"))
    qualifier(base.instructeur, element_2.matiere)
    seance_a_deplacer = Seance.objects.create(
        programme=base.programme,
        element_referentiel=element_2,
        instructeur=base.instructeur,
        debut=instant(lundi, 1, 8),
        fin=instant(lundi, 1, 10),
    )
    LigneProgramme.objects.create(seance=seance_a_deplacer, brigade=base.brigade)

    with pytest.raises(ErreurValidation, match="RG-67"):
        ServiceEcritureSeance.modifier_seance(
            planificateur,
            seance_a_deplacer,
            {"debut": instant(lundi, 0, 8), "fin": instant(lundi, 0, 9, 45)},
        )


# --- Génération : scénario exact du recetteur -------------------------------


def test_generation_ne_pose_rien_sur_le_creneau_d_une_seance_verrouillee(
    scenario, brigade_formation, formation, matiere, instructeur
):
    """Le scénario exact du recetteur (A1/A10) : un contrôle verrouillé
    (type E2) existe déjà sur le premier créneau de la semaine ; la
    génération ne doit RIEN y poser, et le contrôle reste visible, intact,
    après génération."""
    qualifier(instructeur, matiere)
    element = creer_element(formation, matiere, volume=40)
    cours = Cours(element, instructeur)
    programme = ProgrammeHebdomadaire.objects.create(lundi_de_semaine=scenario.lundi)
    controle = _seance_verrouillee(
        programme, cours, brigade_formation, instant(scenario.lundi, 0, 8), duree_min=105
    )

    compte_rendu = ServiceGeneration.generer(
        scenario.planificateur, scenario.lundi, [brigade_formation]
    )

    controle.refresh_from_db()
    assert controle.verrouillee
    assert LigneProgramme.objects.filter(seance=controle, brigade=brigade_formation).exists()
    conflits = Seance.objects.filter(
        programme=compte_rendu.programme,
        debut__lt=controle.fin,
        fin__gt=controle.debut,
        lignes__brigade=brigade_formation,
    ).exclude(pk=controle.pk)
    assert not conflits.exists()


def test_construire_cases_exclut_le_creneau_deja_occupe(base):
    """K1, point (2) : `construire_cases` n'engendre aucune case pour une
    brigade déjà occupée par une séance verrouillée sur ce créneau."""
    qualifier(base.instructeur, base.matiere)
    cours = Cours(creer_element(base.formation, base.matiere), base.instructeur)
    debut = instant(base.programme.lundi_de_semaine, 0, 8)
    fin = debut + datetime.timedelta(minutes=105)
    seance = _seance_verrouillee(base.programme, cours, base.brigade, debut, duree_min=105)

    assert brigade_deja_occupee(base.brigade, debut, fin, [seance])
    cases = construire_cases(
        [base.brigade], [(debut, fin)], periodes_bloquantes=[], seances_verrouillees=[seance]
    )
    assert cases == []


# --- Regroupement ------------------------------------------------------------


def test_refuse_en_regroupement(base_partage, planificateur):
    """K1, point (1) : la brigade déjà occupée ailleurs ne peut pas être
    associée à une séance en lieu partagé sur ce créneau."""
    cours = _cours_partage(base_partage)
    debut = instant(base_partage.programme.lundi_de_semaine, 0, 8)
    seance = _seance_partagee(base_partage, cours, debut, [base_partage.brigade])
    _seance_verrouillee(base_partage.programme, cours, base_partage.autre_brigade, debut, duree_min=105)

    with pytest.raises(ErreurValidation, match="RG-67"):
        associer_brigades(planificateur, seance, [base_partage.autre_brigade])


def test_seance_regroupee_occupe_le_creneau_pour_chaque_brigade(base_partage):
    """K1 : une séance regroupée occupe le créneau pour CHACUNE de ses
    brigades — deux candidates du même regroupement (même `cle_regroupement`)
    ne se bloquent jamais mutuellement via RG-67. Même chemin que le vrai
    regroupement (`regroupement.py::_verifier_contraintes_association`) :
    contexte SANS la séance, candidates vérifiées ENSEMBLE par
    `verifier_lot` — la seconde voit la première dans `lot_acceptees`,
    c'est là que l'exemption par `cle_regroupement` de RG-67 s'exerce."""
    cours = _cours_partage(base_partage)
    debut = instant(base_partage.programme.lundi_de_semaine, 0, 8)
    brigades = [base_partage.brigade, base_partage.autre_brigade]
    seance = _seance_partagee(base_partage, cours, debut, brigades)
    candidates = [
        _candidate(b, cours, debut, lieu=base_partage.lieu_partage, cle_regroupement=seance.pk)
        for b in brigades
    ]
    contexte = _contexte_sans_la_seance(base_partage.programme, seance)

    verdicts = ServiceContraintes.verifier_lot(candidates, contexte)

    assert not any(v["code"] == "RG-67" for verdict in verdicts for v in verdict.violations)


# --- Affichage de données anciennes (chevauchement déjà en base) -----------


def test_affichage_de_deux_lignes_qui_se_chevauchent(base):
    """K1, point (3) : deux séances anciennes qui se chevauchent pour la
    même brigade s'affichent TOUTES LES DEUX, jamais l'une masquant
    l'autre."""
    matiere_2 = Matiere.objects.create(intitule="Seconde matière du chevauchement", code="CHEV2")
    qualifier(base.instructeur, base.matiere)
    qualifier(base.instructeur, matiere_2)
    debut = instant(base.programme.lundi_de_semaine, 0, 8)
    seance_1 = _seance_sans_lieu(base, base.matiere, debut)
    seance_2 = _seance_sans_lieu(base, matiere_2, debut)
    creneau = CreneauType.objects.create(
        grille=GrilleHoraire.objects.create(intitule="Grille chevauchement"),
        jour_semaine="lundi",
        ordre=1,
        heure_debut=datetime.time(8, 0),
        heure_fin=datetime.time(9, 45),
    )

    groupes = grille_consultation(base.programme, [creneau], [base.brigade])
    cellules = [c for g in groupes for ligne in g["lignes"] for c in ligne["cellules"]]
    cellule = next(c for c in cellules if c.ligne is not None)

    assert len(cellule.chevauchements) == 1
    pks = {cellule.seance.pk, cellule.chevauchements[0].seance.pk}
    assert pks == {seance_1.pk, seance_2.pk}


def _seance_sans_lieu(base, matiere, debut):
    element = creer_element(base.formation, matiere, categorie=CategorieLieu.AUCUN_LIEU)
    seance = Seance.objects.create(
        programme=base.programme,
        element_referentiel=element,
        instructeur=base.instructeur,
        debut=debut,
        fin=debut + datetime.timedelta(minutes=105),
    )
    LigneProgramme.objects.create(seance=seance, brigade=base.brigade)
    return seance
