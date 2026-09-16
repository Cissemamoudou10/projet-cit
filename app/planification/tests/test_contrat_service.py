"""US-PLAN-04, Groupe H — contrat de `ServiceContraintes` : n'écrit rien,
retourne toutes les violations, `verifier_lot` distingue base et lot,
performance bornée. Prompt 30, § 3/§ 8/§ 12. Données entièrement fictives.
"""

import datetime

from django.db import connection
from django.test.utils import CaptureQueriesContext

from organisation.services.brigade import ServiceBrigade
from planification.models import LigneProgramme, ProgrammeHebdomadaire, Seance
from planification.services.contraintes import Candidate, ServiceContraintes
from planification.tests.conftest import Cours, creer_element, instant, qualifier
from ressources.models import IndisponibiliteInstructeur, Instructeur, Statut


def _candidate(brigade, cours, debut, duree_min=105):
    fin = debut + datetime.timedelta(minutes=duree_min)
    return Candidate(
        brigade=brigade,
        element_referentiel=cours.element,
        instructeur=cours.instructeur,
        debut=debut,
        fin=fin,
    )


def _comptes():
    return Seance.objects.count(), LigneProgramme.objects.count()


# --- H1 — verifier n'écrit rien, cas accepté et refusé ----------------------


def test_h1_verifier_n_ecrit_rien_cas_accepte(programme, cours, brigade):
    qualifier(cours.instructeur, cours.element.matiere)
    candidate = _candidate(brigade, cours, instant(programme.lundi_de_semaine, 0, 8))
    avant = _comptes()

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert verdict.accepte
    assert _comptes() == avant


def test_h1_verifier_n_ecrit_rien_cas_refuse(programme, cours, brigade):
    candidate = _candidate(brigade, cours, instant(programme.lundi_de_semaine, 0, 8))
    avant = _comptes()

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert not verdict.accepte
    assert _comptes() == avant


# --- H2 — violations multiples : quatre règles, quatre violations ----------


def test_h2_candidate_violant_quatre_regles_rend_quatre_violations(programme, cours, brigade):
    from ressources.models import NatureEvenement, PeriodeCalendrier

    lundi = programme.lundi_de_semaine
    # RG-34 : instructeur déjà affecté sur un créneau sécant.
    autre_element = creer_element(brigade.session.formation, cours.element.matiere)
    seance = Seance.objects.create(
        programme=programme,
        element_referentiel=autre_element,
        instructeur=cours.instructeur,
        debut=instant(lundi, 0, 8),
        fin=instant(lundi, 0, 9, 45),
    )
    LigneProgramme.objects.create(seance=seance, brigade=brigade)
    # RG-35 : pas de qualification posée — refus par construction.
    # RG-36 : indisponibilité recouvrant le créneau.
    IndisponibiliteInstructeur.objects.create(
        instructeur=cours.instructeur,
        debut=instant(lundi, 0, 7),
        fin=instant(lundi, 0, 10),
        motif="Mission",
    )
    # RG-38 : période bloquante, portée centre entier.
    nature = NatureEvenement.objects.create(libelle="Nature H2", effet_par_defaut="bloquant")
    PeriodeCalendrier.objects.create(
        nature=nature,
        intitule="Période H2",
        debut=instant(lundi, 0, 6),
        fin=instant(lundi, 0, 12),
        effet="bloquant",
    )
    candidate = _candidate(brigade, cours, instant(lundi, 0, 8, 30))

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert not verdict.accepte
    codes = sorted(v["code"] for v in verdict.violations)
    assert codes == ["RG-34", "RG-35", "RG-36", "RG-38"]


# --- H3 — chaque violation porte le code et nomme l'élément ----------------


def test_h3_chaque_violation_porte_le_code_et_nomme_l_element(programme, cours, brigade):
    candidate = _candidate(brigade, cours, instant(programme.lundi_de_semaine, 0, 8))

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    violation = next(v for v in verdict.violations if v["code"] == "RG-35")
    assert violation["code"] == "RG-35"
    assert str(cours.instructeur) in violation["message"]
    assert str(cours.element.matiere) in violation["message"]
    assert "origine" in violation


# --- H4 — verifier_lot : conflit intra-lot, la seconde refusée -------------


def test_h4_verifier_lot_deux_candidates_meme_instructeur_meme_creneau_la_seconde_refusee(
    programme, cours, brigade, autre_brigade
):
    lundi = programme.lundi_de_semaine
    qualifier(cours.instructeur, cours.element.matiere)
    candidates = [
        _candidate(brigade, cours, instant(lundi, 0, 8)),
        _candidate(autre_brigade, cours, instant(lundi, 0, 8, 30)),
    ]

    verdicts = ServiceContraintes.verifier_lot(candidates, ServiceContraintes.contexte(programme))

    assert verdicts[0].accepte
    assert not verdicts[1].accepte
    assert any(v["code"] == "RG-34" for v in verdicts[1].violations)


def test_h4_bis_le_motif_de_refus_par_effet_de_lot_est_distinct_du_motif_existant(
    programme, cours, brigade, autre_brigade
):
    """Directive utilisateur, § 12 : le conflit avec l'EXISTANT et le
    conflit avec une candidate ANTÉRIEURE DU MÊME LOT appellent des actions
    différentes — le motif doit le distinguer, pas seulement le texte."""
    lundi = programme.lundi_de_semaine
    qualifier(cours.instructeur, cours.element.matiere)
    candidates = [
        _candidate(brigade, cours, instant(lundi, 0, 8)),
        _candidate(autre_brigade, cours, instant(lundi, 0, 8, 30)),
    ]

    verdicts = ServiceContraintes.verifier_lot(candidates, ServiceContraintes.contexte(programme))

    violation = next(v for v in verdicts[1].violations if v["code"] == "RG-34")
    assert violation["origine"] == "lot"


# --- H5 — verifier_lot : deux candidates compatibles, toutes acceptées -----


def test_h5_verifier_lot_deux_candidates_compatibles_toutes_acceptees(
    programme, cours, autre_instructeur, brigade, autre_brigade
):
    lundi = programme.lundi_de_semaine
    qualifier(cours.instructeur, cours.element.matiere)
    qualifier(autre_instructeur, cours.element.matiere)
    autre_cours = Cours(cours.element, autre_instructeur)
    candidates = [
        _candidate(brigade, cours, instant(lundi, 0, 8)),
        _candidate(autre_brigade, autre_cours, instant(lundi, 0, 8)),
    ]

    verdicts = ServiceContraintes.verifier_lot(candidates, ServiceContraintes.contexte(programme))

    assert all(verdict.accepte for verdict in verdicts)


# --- H6 — performance : nombre de requêtes borné, indépendant du lot -------


def _former_session(redacteur, indice, matiere, type_formation):
    from organisation.services.session import ServiceSession
    from referentiel.models import CategorieLieu, ElementReferentiel, Formation

    aujourd_hui = datetime.date.today()
    formation = Formation.objects.create(
        intitule=f"Formation H6-{indice}",
        specialite="Transmissions",
        duree_semaines=10,
        type_formation=type_formation,
    )
    element = ElementReferentiel.objects.create(
        formation=formation,
        matiere=matiere,
        volume_horaire_prescrit=200,
        categorie_lieu=CategorieLieu.AUCUN_LIEU,
    )
    session = ServiceSession.creer(
        redacteur,
        {
            "formation": formation,
            "intitule": f"Session H6-{indice}",
            "date_debut": aujourd_hui + datetime.timedelta(days=30),
            "date_fin": aujourd_hui + datetime.timedelta(days=200),
            "effectif_attendu": 24,
        },
    )
    return session, element


def _former_brigade_et_instructeur(redacteur, indice, matiere, type_formation):
    session, element = _former_session(redacteur, indice, matiere, type_formation)
    brigades = [
        (
            ServiceBrigade.creer(
                redacteur, session, {"designation": f"B{indice}{j}", "effectif_previsionnel": 15}
            ),
            element,
        )
        for j in range(4)
    ]
    instructeur = Instructeur.objects.create(
        nom=f"Instructeur H6-{indice}",
        prenom="Essai",
        matricule=f"H6{indice:04d}",
        grade="Lt",
        specialite="Transmissions",
        statut=Statut.MILITAIRE_DU_CENTRE,
    )
    qualifier(instructeur, matiere)
    return brigades, instructeur


def _jeu_representatif(redacteur):
    """Plusieurs sessions, une dizaine de brigades — jeu représentatif du
    § 12, Prompt 30."""
    from referentiel.models import Matiere, TypeFormation

    type_formation = TypeFormation.objects.create(intitule="Officiers H6")
    matiere = Matiere.objects.create(intitule="Matière H6", code="H6M01")
    brigades, instructeurs = [], []
    for i in range(3):
        brigades_i, instructeur = _former_brigade_et_instructeur(
            redacteur, i, matiere, type_formation
        )
        brigades += brigades_i
        instructeurs.append(instructeur)
    return brigades, instructeurs


def _seances_initiales(programme, brigades, instructeurs, lundi):
    for jour in range(3):
        seance = Seance.objects.create(
            programme=programme,
            element_referentiel=brigades[jour][1],
            instructeur=instructeurs[jour % len(instructeurs)],
            debut=instant(lundi, jour, 8),
            fin=instant(lundi, jour, 9, 45),
        )
        LigneProgramme.objects.create(seance=seance, brigade=brigades[jour][0])


def _lot(nombre, brigades, instructeurs, lundi):
    return [
        _candidate(
            brigades[i % len(brigades)][0],
            Cours(brigades[i % len(brigades)][1], instructeurs[i % len(instructeurs)]),
            instant(lundi, 0, 10, i),
        )
        for i in range(nombre)
    ]


def test_h6_nombre_de_requetes_sql_borne_et_independant_du_nombre_de_candidates(
    redacteur, lundi_semaine
):
    """Jeu représentatif : plusieurs sessions, une dizaine de brigades, une
    semaine complète — mesure reportée au compte rendu (§ 12)."""
    brigades, instructeurs = _jeu_representatif(redacteur)
    programme = ProgrammeHebdomadaire.objects.create(lundi_de_semaine=lundi_semaine)
    _seances_initiales(programme, brigades, instructeurs, lundi_semaine)

    with CaptureQueriesContext(connection) as petit_lot:
        contexte = ServiceContraintes.contexte(programme)
        ServiceContraintes.verifier_lot(_lot(3, brigades, instructeurs, lundi_semaine), contexte)
    with CaptureQueriesContext(connection) as grand_lot:
        contexte = ServiceContraintes.contexte(programme)
        ServiceContraintes.verifier_lot(_lot(15, brigades, instructeurs, lundi_semaine), contexte)

    assert len(petit_lot) == len(grand_lot)
    assert len(grand_lot) < 15
