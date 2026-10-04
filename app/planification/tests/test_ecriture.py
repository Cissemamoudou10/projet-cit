"""US-PLAN-04, Groupe I (I2) — `ServiceEcritureSeance`, la porte d'écriture
unique : toute tentative violant une règle est refusée par ce chemin, jamais
seulement par `ServiceContraintes` isolément. Prompt 30, § 5. Données
entièrement fictives.
"""

import datetime

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from noyau.exceptions import ErreurHabilitation, ErreurValidation
from planification.models import LigneProgramme, ProgrammeHebdomadaire, Seance
from planification.services.contraintes import Candidate
from planification.services.ecriture import ServiceEcritureSeance
from planification.tests.conftest import Cours, creer_element, instant, qualifier
from referentiel.models import Matiere
from ressources.models import Instructeur, Statut


def _candidate(brigade, cours, debut, duree_min=105, **kw):
    fin = debut + datetime.timedelta(minutes=duree_min)
    return Candidate(
        brigade=brigade,
        element_referentiel=cours.element,
        instructeur=cours.instructeur,
        debut=debut,
        fin=fin,
        **kw,
    )


def test_creation_nominale_journalisee(planificateur, programme, cours, brigade):
    qualifier(cours.instructeur, cours.element.matiere)
    candidate = _candidate(brigade, cours, instant(programme.lundi_de_semaine, 0, 8))

    seance = ServiceEcritureSeance.creer_seance(planificateur, programme, [candidate])

    assert Seance.objects.filter(pk=seance.pk).exists()
    assert LigneProgramme.objects.filter(seance=seance, brigade=brigade).exists()


def test_creation_regroupee_plusieurs_lignes(
    planificateur, programme, cours, brigade, autre_brigade
):
    qualifier(cours.instructeur, cours.element.matiere)
    debut = instant(programme.lundi_de_semaine, 0, 8)
    candidates = [
        _candidate(b, cours, debut, cle_regroupement="groupe-ecriture")
        for b in (brigade, autre_brigade)
    ]

    seance = ServiceEcritureSeance.creer_seance(planificateur, programme, candidates)

    assert seance.lignes.count() == 2


def test_i2_tentative_violant_une_regle_refusee_par_le_chemin_de_service(
    planificateur, programme, cours, brigade
):
    """Aucune qualification posée : RG-35 refuse — et rien n'est écrit."""
    candidate = _candidate(brigade, cours, instant(programme.lundi_de_semaine, 0, 8))
    avant = Seance.objects.count()

    with pytest.raises(ErreurValidation, match="RG-35"):
        ServiceEcritureSeance.creer_seance(planificateur, programme, [candidate])

    assert Seance.objects.count() == avant


def test_habilitation_programme_ecriture_requise(redacteur, programme, cours, brigade):
    qualifier(cours.instructeur, cours.element.matiere)
    candidate = _candidate(brigade, cours, instant(programme.lundi_de_semaine, 0, 8))

    with pytest.raises(ErreurHabilitation):
        ServiceEcritureSeance.creer_seance(redacteur, programme, [candidate])


# --- creer_seances (lot) — US-PLAN-03, § 0.3/point 4, Prompt 31 -------------


def test_creer_seances_ecrit_plusieurs_seances_en_une_seule_transaction(
    planificateur, programme, cours, brigade, autre_brigade
):
    qualifier(cours.instructeur, cours.element.matiere)
    lundi = programme.lundi_de_semaine
    groupe_un = [_candidate(brigade, cours, instant(lundi, 0, 8))]
    groupe_deux = [_candidate(autre_brigade, cours, instant(lundi, 0, 14))]

    seances = ServiceEcritureSeance.creer_seances(
        planificateur, programme, [groupe_un, groupe_deux]
    )

    assert len(seances) == 2
    assert Seance.objects.filter(programme=programme).count() == 2


def test_creer_seances_tout_ou_rien_si_une_candidate_du_lot_est_refusee(
    planificateur, programme, cours, brigade, autre_brigade
):
    """La seconde candidate n'est pas qualifiée (RG-35) : rien ne s'écrit,
    y compris la première, qui aurait été acceptée seule."""
    qualifier(cours.instructeur, cours.element.matiere)
    instructeur_non_qualifie = Instructeur.objects.create(
        nom="Amrovic",
        prenom="Yarnel",
        matricule="M24680",
        grade="Cne",
        specialite="Transmissions",
        statut=Statut.MILITAIRE_DU_CENTRE,
    )
    lundi = programme.lundi_de_semaine
    debut_refusee = instant(lundi, 0, 14)
    groupe_valide = [_candidate(brigade, cours, instant(lundi, 0, 8))]
    candidate_refusee = Candidate(
        brigade=autre_brigade,
        element_referentiel=cours.element,
        instructeur=instructeur_non_qualifie,
        debut=debut_refusee,
        fin=debut_refusee + datetime.timedelta(minutes=105),
    )

    with pytest.raises(ErreurValidation, match="RG-35"):
        ServiceEcritureSeance.creer_seances(
            planificateur, programme, [groupe_valide, [candidate_refusee]]
        )

    assert Seance.objects.filter(programme=programme).count() == 0


def test_creer_seances_pose_les_horodatages_et_l_auteur_malgre_bulk_create(
    planificateur, programme, cours, brigade, autre_brigade
):
    """P-38 (revue du Prompt 32) : `creer_seances` écrit par lot
    (`bulk_create`), qui n'appelle jamais `save()` — `cree_le`/`modifie_le`
    (`auto_now_add`/`auto_now`) et `cree_par`/`modifie_par` (posés par
    `ServiceBase.creer` d'ordinaire) ne se posent alors JAMAIS tout seuls.
    Si `_horodater` disparaissait de `creer_seances`, ces quatre champs
    resteraient `None` en base — ce test l'aurait attrapé."""
    qualifier(cours.instructeur, cours.element.matiere)
    lundi = programme.lundi_de_semaine
    groupe_un = [_candidate(brigade, cours, instant(lundi, 0, 8))]
    groupe_deux = [_candidate(autre_brigade, cours, instant(lundi, 0, 14))]

    seances = ServiceEcritureSeance.creer_seances(
        planificateur, programme, [groupe_un, groupe_deux]
    )

    for seance in Seance.objects.filter(pk__in=[s.pk for s in seances]):
        assert seance.cree_le is not None
        assert seance.modifie_le is not None
        assert seance.cree_par_id == planificateur.pk
        assert seance.modifie_par_id == planificateur.pk
    for ligne in LigneProgramme.objects.filter(seance__in=seances):
        assert ligne.cree_le is not None
        assert ligne.modifie_le is not None
        assert ligne.cree_par_id == planificateur.pk
        assert ligne.modifie_par_id == planificateur.pk


def test_creer_seances_ne_journalise_pas_le_detail_par_seance(
    planificateur, programme, cours, brigade, autre_brigade
):
    """§ 7, Prompt 31 : l'acte de génération est journalisé par
    `ServiceGeneration`, jamais le détail des séances par cette porte."""
    from administration.models import EntreeJournal

    qualifier(cours.instructeur, cours.element.matiere)
    lundi = programme.lundi_de_semaine
    avant = EntreeJournal.objects.count()
    groupe_un = [_candidate(brigade, cours, instant(lundi, 0, 8))]
    groupe_deux = [_candidate(autre_brigade, cours, instant(lundi, 0, 14))]

    ServiceEcritureSeance.creer_seances(planificateur, programme, [groupe_un, groupe_deux])

    assert EntreeJournal.objects.count() == avant


# --- P-38 — garde réelle de la pente nulle (Prompt 37, Temps 1) ------------


def _candidates_independantes(brigade, cours, lundi, nombre, decalage_jours):
    """`nombre` groupes d'une candidate chacun, un jour distinct par
    candidate (aucun recouvrement RG-34 entre elles, ni entre les deux
    volumes comparés par le test de pente — `decalage_jours` les sépare)."""
    return [
        [_candidate(brigade, cours, instant(lundi, decalage_jours + i, 8), duree_min=60)]
        for i in range(nombre)
    ]


def _programmes_de_mesure(lundi):
    """Trois programmes DISTINCTS et VIERGES — chauffe, 40, 200 — jamais
    deux mesures sur le même programme : `_charger_seances_existantes`
    (`contraintes.py`) filtre par `programme`, un programme déjà écrit par
    la mesure précédente fausserait la comparaison (prefetch non vide),
    voir `docs/suivi/PROBLEMES.md`, P-39."""
    return (
        ProgrammeHebdomadaire.objects.create(lundi_de_semaine=lundi - datetime.timedelta(weeks=3)),
        ProgrammeHebdomadaire.objects.create(lundi_de_semaine=lundi - datetime.timedelta(weeks=2)),
        ProgrammeHebdomadaire.objects.create(lundi_de_semaine=lundi - datetime.timedelta(weeks=1)),
    )


def test_p38_nombre_de_requetes_independant_du_nombre_de_seances_ecrites(
    planificateur, programme, formation, brigade, instructeur
):
    """P-38 (revue du Prompt 32) a remplacé une boucle coûtant 6 requêtes par
    séance par un `bulk_create` en deux requêtes pour tout le lot — mais
    aucun test existant ne le prouvait : `test_i3_...`
    (`test_generation_architecture.py`) compare un nombre de CASES ÉVALUÉES,
    pas de séances ÉCRITES ; `test_h6_...` (`test_contrat_service.py`)
    compare `verifier_lot` seul, jamais l'écriture. Volume prescrit à 300 h :
    les deux lots comparés (40 + 200 séances d'1 h) s'écrivent sans heurter
    RG-39. Chauffe préalable (même motif que `test_i3_...`) : absorbe le
    cache de permission de `planificateur` avant toute capture, pour que
    les deux mesures restent symétriques — détail et historique en P-39."""
    matiere = Matiere.objects.create(intitule="Matière P-38", code="P38M01")
    element = creer_element(formation, matiere, volume=300)
    qualifier(instructeur, matiere)
    cours = Cours(element, instructeur)
    lundi = programme.lundi_de_semaine
    programme_chauffe, programme_40, programme_200 = _programmes_de_mesure(lundi)

    groupe_chauffe = _candidates_independantes(brigade, cours, lundi, 1, decalage_jours=-70)
    ServiceEcritureSeance.creer_seances(planificateur, programme_chauffe, groupe_chauffe)

    groupes_40 = _candidates_independantes(brigade, cours, lundi, 40, decalage_jours=0)
    groupes_200 = _candidates_independantes(brigade, cours, lundi, 200, decalage_jours=1000)

    with CaptureQueriesContext(connection) as requetes_40:
        ServiceEcritureSeance.creer_seances(planificateur, programme_40, groupes_40)
    with CaptureQueriesContext(connection) as requetes_200:
        ServiceEcritureSeance.creer_seances(planificateur, programme_200, groupes_200)

    assert len(requetes_40) == len(requetes_200)
