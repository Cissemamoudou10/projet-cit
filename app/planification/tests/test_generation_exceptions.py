"""US-PLAN-03 — Groupe E : les exceptions. Prompt 31, § 6/§ 12. Données
entièrement fictives.
"""

import datetime

import pytest

from noyau.exceptions import ErreurValidation
from planification.exceptions import AucuneGrilleActive, SemaineEntierementBloquee
from planification.models import LigneProgramme, ProgrammeHebdomadaire, Seance
from planification.services.generation import ServiceGeneration
from planification.tests.conftest import activer_grille, creer_element, instant, qualifier
from ressources.models import EffetPeriode, IndisponibiliteInstructeur, NatureEvenement, PeriodeCalendrier


def test_e1_semaine_entierement_bloquee_aucun_programme_cree(scenario, cours, brigade_formation):
    qualifier(cours.instructeur, cours.element.matiere)
    nature = NatureEvenement.objects.create(libelle="Fermeture E1", effet_par_defaut="bloquant")
    PeriodeCalendrier.objects.create(
        nature=nature,
        intitule="Fermeture totale E1",
        debut=instant(scenario.lundi, 0, 0),
        fin=instant(scenario.lundi, 6, 23, 59),
        effet=EffetPeriode.BLOQUANT,
    )

    with pytest.raises(SemaineEntierementBloquee):
        ServiceGeneration.generer(scenario.planificateur, scenario.lundi, [brigade_formation])

    assert not ProgrammeHebdomadaire.objects.filter(lundi_de_semaine=scenario.lundi).exists()


def test_e2_aucune_matiere_programmable_enumeree_avec_motif(
    scenario, cours, brigade_formation
):
    """Volume déjà épuisé pour l'unique matière de la brigade — écartée
    d'emblée, motif chiffré au compte rendu (critère 3)."""
    qualifier(cours.instructeur, cours.element.matiere)
    cours.element.volume_horaire_prescrit = 5
    cours.element.save()
    programme_passe = ProgrammeHebdomadaire.objects.create(
        lundi_de_semaine=scenario.lundi - datetime.timedelta(weeks=52)
    )
    seance = Seance.objects.create(
        programme=programme_passe,
        element_referentiel=cours.element,
        instructeur=cours.instructeur,
        debut=instant(programme_passe.lundi_de_semaine, 0, 8),
        fin=instant(programme_passe.lundi_de_semaine, 0, 8).replace(hour=22),
    )
    LigneProgramme.objects.create(seance=seance, brigade=brigade_formation)

    compte_rendu = ServiceGeneration.generer(scenario.planificateur, scenario.lundi, [brigade_formation])

    assert compte_rendu.seances_par_brigade.get(brigade_formation, 0) == 0
    motifs = {e.element.pk: e.motif for e in compte_rendu.matieres_ecartees}
    assert cours.element.pk in motifs
    assert str(cours.element.volume_horaire_prescrit) in motifs[cours.element.pk]


def test_e3_aucun_instructeur_disponible_motif_nominatif_par_cause(
    scenario, cours, autre_instructeur, brigade_formation
):
    """Deux instructeurs qualifiés, tous deux indisponibles pour des
    raisons DIFFÉRENTES — les deux causes doivent apparaître, nommément."""
    qualifier(cours.instructeur, cours.element.matiere)
    qualifier(autre_instructeur, cours.element.matiere)
    for jour in range(5):
        IndisponibiliteInstructeur.objects.create(
            instructeur=cours.instructeur,
            debut=instant(scenario.lundi, jour, 0),
            fin=instant(scenario.lundi, jour, 23, 59),
            motif="Stage E3",
        )
        IndisponibiliteInstructeur.objects.create(
            instructeur=autre_instructeur,
            debut=instant(scenario.lundi, jour, 0),
            fin=instant(scenario.lundi, jour, 23, 59),
            motif="Mission E3",
        )

    compte_rendu = ServiceGeneration.generer(scenario.planificateur, scenario.lundi, [brigade_formation])

    motifs = " ".join(m for case in compte_rendu.cases_non_pourvues for m in case.motifs)
    assert str(cours.instructeur) in motifs
    assert str(autre_instructeur) in motifs
    assert "RG-36" in motifs


def _amphi_element_e4(formation):
    from referentiel.models import CategorieLieu as CategorieLieuReferentiel
    from referentiel.models import Matiere
    from referentiel.models import TypeLieuPartage as TypeLieuPartageReferentiel
    from ressources.models import CategorieLieu as CategorieLieuRessource
    from ressources.models import Lieu, ModePartage
    from ressources.models import TypeLieuPartage as TypeLieuPartageRessource

    lieu = Lieu.objects.create(
        intitule="Amphi E4",
        capacite=10,
        categorie=CategorieLieuRessource.LIEU_PARTAGE,
        type_partage=TypeLieuPartageRessource.AMPHITHEATRE,
        mode_partage=ModePartage.SEQUENTIEL,
    )
    element = creer_element(
        formation,
        Matiere.objects.create(intitule="Matière E4", code="AMP4"),
        categorie=CategorieLieuReferentiel.LIEU_PARTAGE,
        type_lieu_partage=TypeLieuPartageReferentiel.AMPHITHEATRE,
    )
    return lieu, element


def _occuper_creneau_e4(programme, element, lieu, brigade, lundi):
    """Aligné sur `projeter_creneaux` (heure LOCALE, Africa/Casablanca) et
    non sur `instant()` (UTC fixe) : un décalage d'une heure entre les deux
    ferait manquer le recouvrement visé par le test E4."""
    from django.utils import timezone as _tz

    instructeur = _instructeur_e4()
    qualifier(instructeur, element.matiere)
    debut = _tz.make_aware(datetime.datetime.combine(lundi, datetime.time(8, 0)))
    fin = _tz.make_aware(datetime.datetime.combine(lundi, datetime.time(9, 45)))
    seance = Seance.objects.create(
        programme=programme, element_referentiel=element, instructeur=instructeur,
        lieu=lieu, debut=debut, fin=fin,
    )
    LigneProgramme.objects.create(seance=seance, brigade=brigade)


def test_e4_aucun_lieu_partage_disponible_propose_un_autre_creneau_ou_le_report(
    scenario, formation, brigade_formation, autre_brigade_formation
):
    """L'amphi est déjà occupé le lundi matin par une AUTRE brigade
    (`autre_brigade_formation`, non sélectionnée cette fois — une séance
    d'une brigade sélectionnée serait supprimée par la régénération
    chirurgicale avant même d'être vue comme un conflit). E4 doit proposer
    un autre créneau de la semaine où l'amphi est libre."""
    lieu, element = _amphi_element_e4(formation)
    programme = ProgrammeHebdomadaire.objects.create(lundi_de_semaine=scenario.lundi)
    _occuper_creneau_e4(programme, element, lieu, autre_brigade_formation, scenario.lundi)

    compte_rendu = ServiceGeneration.generer(scenario.planificateur, scenario.lundi, [brigade_formation])

    propositions = [c.proposition for c in compte_rendu.cases_non_pourvues if c.proposition]
    assert propositions
    assert "Amphi E4" in propositions[0]


def _instructeur_e4():
    from ressources.models import Instructeur, Statut

    return Instructeur.objects.create(
        nom="E4", prenom="Test", matricule="E4TST", grade="Lt",
        specialite="Transmissions", statut=Statut.MILITAIRE_DU_CENTRE,
    )


def test_e5_borne_de_temps_interrompt_et_retourne_les_placements_deja_obtenus(
    scenario, cours, brigade_formation, settings
):
    qualifier(cours.instructeur, cours.element.matiere)
    settings.GENERATION_BORNE_TEMPS_SECONDES = 0

    compte_rendu = ServiceGeneration.generer(scenario.planificateur, scenario.lundi, [brigade_formation])

    assert compte_rendu.interrompu_par_la_borne
    assert compte_rendu.programme is not None


def test_e6_aucune_grille_active_generation_refusee(planificateur, lundi_semaine, cours, brigade_formation):
    qualifier(cours.instructeur, cours.element.matiere)

    with pytest.raises(AucuneGrilleActive):
        ServiceGeneration.generer(planificateur, lundi_semaine, [brigade_formation])

    assert not ProgrammeHebdomadaire.objects.filter(lundi_de_semaine=lundi_semaine).exists()


