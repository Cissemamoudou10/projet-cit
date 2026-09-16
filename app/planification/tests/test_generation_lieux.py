"""US-PLAN-03 — Groupe D : les lieux. Prompt 31, § 12 (référme D-34, § 5).
Données entièrement fictives.
"""

from planification.services.generation import ServiceGeneration
from planification.tests.conftest import creer_element, instant, qualifier
from referentiel.models import CategorieLieu as CategorieLieuReferentiel
from referentiel.models import TypeLieuPartage as TypeLieuPartageReferentiel
from ressources.models import CategorieLieu as CategorieLieuRessource
from ressources.models import IndisponibiliteInstructeur, Instructeur, Lieu, Statut
from ressources.models import TypeLieuPartage as TypeLieuPartageRessource
from ressources.services.salle_attitree import ServiceSalleAttitree


def _instructeur_disponible_un_jour(nom, jour_libre):
    return Instructeur.objects.create(
        nom=nom,
        prenom=f"J{jour_libre}",
        matricule=f"{nom}{jour_libre}",
        grade="Lt",
        specialite="Transmissions",
        statut=Statut.MILITAIRE_DU_CENTRE,
    )


def _reserver_a_un_seul_jour(instructeur, lundi, jour_libre):
    for autre_jour in range(5):
        if autre_jour == jour_libre:
            continue
        IndisponibiliteInstructeur.objects.create(
            instructeur=instructeur,
            debut=instant(lundi, autre_jour, 0),
            fin=instant(lundi, autre_jour, 23, 59),
            motif="Réservé D5",
        )


def test_d1_matiere_salle_attitree_reprend_la_salle_de_la_brigade(
    scenario, formation, matiere, instructeur, brigade_formation
):
    salle = Lieu.objects.create(
        intitule="Salle D1", capacite=30, categorie=CategorieLieuRessource.SALLE_ATTITREE
    )
    ServiceSalleAttitree.attribuer(scenario.planificateur, brigade_formation, salle)
    element = creer_element(formation, matiere, categorie=CategorieLieuReferentiel.SALLE_ATTITREE)
    qualifier(instructeur, matiere)

    ServiceGeneration.generer(scenario.planificateur, scenario.lundi, [brigade_formation])

    from planification.models import Seance

    seances = Seance.objects.filter(element_referentiel=element)
    assert seances.exists()
    assert all(s.lieu_id == salle.pk for s in seances)


def test_d2_brigade_sans_salle_attitree_case_non_pourvue_motif_explicite(
    scenario, formation, matiere, instructeur, brigade_formation
):
    creer_element(formation, matiere, categorie=CategorieLieuReferentiel.SALLE_ATTITREE)
    qualifier(instructeur, matiere)

    compte_rendu = ServiceGeneration.generer(scenario.planificateur, scenario.lundi, [brigade_formation])

    assert compte_rendu.seances_par_brigade.get(brigade_formation, 0) == 0
    assert any(
        "salle attitrée" in e.motif for e in compte_rendu.matieres_ecartees
    )


def test_d3_matiere_lieu_partage_retient_un_lieu_libre_de_capacite_suffisante(
    scenario, formation, matiere, instructeur, brigade_formation
):
    Lieu.objects.create(
        intitule="Amphi D3",
        capacite=30,
        categorie=CategorieLieuRessource.LIEU_PARTAGE,
        type_partage=TypeLieuPartageRessource.AMPHITHEATRE,
    )
    element = creer_element(
        formation,
        matiere,
        categorie=CategorieLieuReferentiel.LIEU_PARTAGE,
        type_lieu_partage=TypeLieuPartageReferentiel.AMPHITHEATRE,
    )
    qualifier(instructeur, matiere)

    ServiceGeneration.generer(scenario.planificateur, scenario.lundi, [brigade_formation])

    from planification.models import Seance

    seances = Seance.objects.filter(element_referentiel=element)
    assert seances.exists()
    assert all(s.lieu is not None for s in seances)


def test_d4_matiere_sans_lieu_placee_lieu_nul(scenario, cours, brigade_formation):
    qualifier(cours.instructeur, cours.element.matiere)

    ServiceGeneration.generer(scenario.planificateur, scenario.lundi, [brigade_formation])

    from planification.models import Seance

    seances = Seance.objects.filter(element_referentiel=cours.element)
    assert seances.exists()
    assert all(s.lieu is None for s in seances)


def _elements_d5(formation):
    from referentiel.models import Matiere

    salle = Lieu.objects.create(
        intitule="Salle D5", capacite=30, categorie=CategorieLieuRessource.SALLE_ATTITREE
    )
    Lieu.objects.create(
        intitule="Amphi D5",
        capacite=30,
        categorie=CategorieLieuRessource.LIEU_PARTAGE,
        type_partage=TypeLieuPartageRessource.AMPHITHEATRE,
    )
    element_salle = creer_element(
        formation,
        Matiere.objects.create(intitule="Matière salle D5", code="SAL5"),
        categorie=CategorieLieuReferentiel.SALLE_ATTITREE,
    )
    element_partage = creer_element(
        formation,
        Matiere.objects.create(intitule="Matière partagée D5", code="PAR5"),
        categorie=CategorieLieuReferentiel.LIEU_PARTAGE,
        type_lieu_partage=TypeLieuPartageReferentiel.AMPHITHEATRE,
    )
    element_libre = creer_element(
        formation, Matiere.objects.create(intitule="Matière libre D5", code="LIB5")
    )
    return salle, element_salle, element_partage, element_libre


def test_d5_les_trois_cas_dans_une_meme_generation(scenario, formation, brigade_formation):
    """Chaque instructeur n'est disponible qu'UN jour distinct de la
    semaine (indisponibilité déclarée les quatre autres) : les trois
    matières ne se disputent alors jamais les mêmes cases — sans quoi elles
    sont « également rares » (un seul lieu compatible chacune) et l'ordre
    de priorité, purement déterministe, ferait gagner la même à chaque
    case, masquant les deux autres plutôt que de prouver qu'elles
    cohabitent."""
    salle, element_salle, element_partage, element_libre = _elements_d5(formation)
    ServiceSalleAttitree.attribuer(scenario.planificateur, brigade_formation, salle)

    jours_reserves = [1, 2, 3]  # mardi, mercredi, jeudi (0 = lundi)
    matieres = [element_salle.matiere, element_partage.matiere, element_libre.matiere]
    for jour_libre, matiere in zip(jours_reserves, matieres):
        instructeur = _instructeur_disponible_un_jour("D5", jour_libre)
        qualifier(instructeur, matiere)
        _reserver_a_un_seul_jour(instructeur, scenario.lundi, jour_libre)

    ServiceGeneration.generer(scenario.planificateur, scenario.lundi, [brigade_formation])

    from planification.models import Seance

    assert Seance.objects.filter(element_referentiel=element_salle, lieu=salle).exists()
    assert Seance.objects.filter(element_referentiel=element_partage).exclude(lieu=None).exists()
    assert Seance.objects.filter(element_referentiel=element_libre, lieu=None).exists()
