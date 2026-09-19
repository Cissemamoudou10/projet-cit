"""US-PLAN-04, Groupe I (I2) — `ServiceEcritureSeance`, la porte d'écriture
unique : toute tentative violant une règle est refusée par ce chemin, jamais
seulement par `ServiceContraintes` isolément. Prompt 30, § 5. Données
entièrement fictives.
"""

import datetime

import pytest

from noyau.exceptions import ErreurHabilitation, ErreurValidation
from planification.models import LigneProgramme, Seance
from planification.services.contraintes import Candidate
from planification.services.ecriture import ServiceEcritureSeance
from planification.tests.conftest import instant, qualifier
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
        nom="Amrani",
        prenom="Yassir",
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
