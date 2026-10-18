"""US-EVAL-06 — Calculer moyennes et classement, RG-56, RG-57. Jeu calculé
à la main, jamais par le code testé (`.claude/rules/tests.md`) : les
valeurs attendues sont écrites en dur ci-dessous, pas dérivées de
`ServiceMoyenne`.

Scénario (une session, deux brigades, un module à deux types d'évaluation,
coefficients et poids distincts) :

- Module M — coefficient 2, poids formatif 3, poids certificatif 1.
- Module « Jamais évalué » — aucune évaluation, ignoré de la moyenne
  générale (M4).
- E1 : FORMATIVE, module M, brigade B1 seulement, note maximale 20.
- E2 : CERTIFICATIVE, module M, session entière, note maximale 10 — ramenée
  sur 20 (M2).

Brigade B1 (X1, X2, X3) :
- X1 — E1=16, E2=7 → formatif 16, certificatif 7/10*20=14 →
  (3*16 + 1*14) / 4 = 15.50
- X2 — E1=10, E2 absent (N6 défaut : compte zéro) → certificatif 0 →
  (3*10 + 1*0) / 4 = 7.50
- X3 — E2=7, E1 JAMAIS SAISI (ni valeur ni absence) → manquant, bloque le
  calcul entier de X3 (M5)

Brigade B2 (Y1, Y2) — E1 ne les concerne pas (brigade B1 seulement) : le
type formatif est retiré du calcul, son poids avec lui (M3) — seul E2 compte :
- Y1 — E2=10 → 10/10*20 = 20.00
- Y2 — E2=10 → 20.00 — même moyenne que Y1, deux ex aequo (M6)

Classement attendu :
- Session : Y1 et Y2 à égalité rang 1, X1 rang 3 (le rang suivant deux ex
  aequo reprend augmenté de leur nombre), X2 rang 4, X3 absent du classement.
- Brigade B1 : X1 rang 1, X2 rang 2. Brigade B2 : Y1 et Y2 à égalité rang 1.
"""

import dataclasses
import datetime
import decimal

import pytest
from django.test import override_settings

from evaluations.models import Evaluation, Note, TypeEvaluation
from evaluations.services.moyenne import ServiceMoyenne
from evaluations.tests.conftest import creer_brigade
from organisation.models import Stagiaire
from organisation.services.affectation import ServiceAffectation
from referentiel.models import CategorieLieu, ElementReferentiel, Matiere


@pytest.fixture
def module_m(formation):
    """Coefficient et poids distincts (US-REF-03, P-45) — le jeu calculé à
    la main ci-dessous en a besoin pour exercer M3."""
    matiere = Matiere.objects.create(intitule="Transmissions tactiques EVAL", code="TRANSTAC")
    return ElementReferentiel.objects.create(
        formation=formation,
        matiere=matiere,
        volume_horaire_prescrit=20,
        categorie_lieu=CategorieLieu.AUCUN_LIEU,
        coefficient=decimal.Decimal(2),
        poids_formatif=decimal.Decimal(3),
        poids_certificatif=decimal.Decimal(1),
    )


@pytest.fixture
def module_jamais_evalue(formation):
    matiere = Matiere.objects.create(intitule="Jamais évaluée EVAL", code="JAMEV1")
    return ElementReferentiel.objects.create(
        formation=formation,
        matiere=matiere,
        volume_horaire_prescrit=10,
        categorie_lieu=CategorieLieu.AUCUN_LIEU,
    )


def _stagiaire_moyenne(session_obj, matricule):
    return Stagiaire.objects.create(
        session=session_obj,
        matricule=matricule,
        nom="Stagiaire",
        prenom=matricule,
        grade="Sgt",
        unite="1er RTR EVAL",
    )


@dataclasses.dataclass(frozen=True)
class _Stagiaires:
    """Regroupe les cinq stagiaires du scénario — `.claude/rules/python.md`,
    § 5 paramètres max : ils voyagent ensemble entre les deux étapes de
    construction du jeu d'essai."""

    x1: object
    x2: object
    x3: object
    y1: object
    y2: object


def _creer_brigades_et_stagiaires(redacteur, session):
    brigade_1 = creer_brigade(redacteur, session, "MOYB1")
    brigade_2 = creer_brigade(redacteur, session, "MOYB2")
    x1, x2, x3 = (_stagiaire_moyenne(session, f"MOYX{i}") for i in (1, 2, 3))
    y1, y2 = (_stagiaire_moyenne(session, f"MOYY{i}") for i in (1, 2))
    for stagiaire in (x1, x2, x3):
        ServiceAffectation.affecter(redacteur, stagiaire, brigade_1)
    for stagiaire in (y1, y2):
        ServiceAffectation.affecter(redacteur, stagiaire, brigade_2)
    return brigade_1, brigade_2, _Stagiaires(x1=x1, x2=x2, x3=x3, y1=y1, y2=y2)


def _creer_evaluations_et_notes(session, module_m, brigade_1, stagiaires):
    e1 = Evaluation.objects.create(
        element_referentiel=module_m,
        brigade=brigade_1,
        type=TypeEvaluation.FORMATIVE,
        date=datetime.date(2026, 1, 12),
        note_maximale=20,
    )
    e2 = Evaluation.objects.create(
        element_referentiel=module_m,
        session=session,
        type=TypeEvaluation.CERTIFICATIVE,
        date=datetime.date(2026, 1, 19),
        note_maximale=10,
    )
    Note.objects.create(evaluation=e1, stagiaire=stagiaires.x1, valeur=16)
    Note.objects.create(evaluation=e2, stagiaire=stagiaires.x1, valeur=7)
    Note.objects.create(evaluation=e1, stagiaire=stagiaires.x2, valeur=10)
    Note.objects.create(evaluation=e2, stagiaire=stagiaires.x2, valeur=None, absent=True)
    Note.objects.create(evaluation=e2, stagiaire=stagiaires.x3, valeur=7)
    # x3 n'a jamais de note sur e1 : manquant, volontairement omis.
    Note.objects.create(evaluation=e2, stagiaire=stagiaires.y1, valeur=10)
    Note.objects.create(evaluation=e2, stagiaire=stagiaires.y2, valeur=10)
    return e1, e2


@pytest.fixture
def scenario(redacteur, session, module_m, module_jamais_evalue):
    """Jeu calculé à la main (docstring du module) : deux brigades, un
    module à deux types pondérés différemment, une évaluation sur 10
    ramenée sur 20, une absence, une note jamais saisie, deux ex aequo."""
    brigade_1, brigade_2, stagiaires = _creer_brigades_et_stagiaires(redacteur, session)
    e1, e2 = _creer_evaluations_et_notes(session, module_m, brigade_1, stagiaires)
    return {
        "brigade_1": brigade_1,
        "brigade_2": brigade_2,
        "x1": stagiaires.x1,
        "x2": stagiaires.x2,
        "x3": stagiaires.x3,
        "y1": stagiaires.y1,
        "y2": stagiaires.y2,
        "module_m": module_m,
        "module_jamais_evalue": module_jamais_evalue,
        "e1_formative_brigade1": e1,
        "e2_certificative_session": e2,
    }


def _moyenne_de(rapport, stagiaire):
    return next(r for r in rapport.resultats if r.stagiaire.pk == stagiaire.pk)


def test_moyennes_calculees_a_la_main(examens, session, scenario):
    rapport = ServiceMoyenne.calculer(examens, session)

    moyennes = {r.stagiaire.pk: r.moyenne for r in rapport.resultats}
    assert moyennes[scenario["x1"].pk] == decimal.Decimal("15.50")
    assert moyennes[scenario["x2"].pk] == decimal.Decimal("7.50")
    assert moyennes[scenario["y1"].pk] == decimal.Decimal("20.00")
    assert moyennes[scenario["y2"].pk] == decimal.Decimal("20.00")
    assert scenario["x3"].pk not in moyennes


def test_module_sans_evaluation_est_ignore_et_signale(examens, session, scenario):
    rapport = ServiceMoyenne.calculer(examens, session)

    assert scenario["module_jamais_evalue"] in rapport.modules_ignores
    assert scenario["module_m"] not in rapport.modules_ignores


def test_note_manquante_bloque_le_calcul_et_est_signalee_par_module_et_brigade(
    examens, session, scenario
):
    rapport = ServiceMoyenne.calculer(examens, session)

    manquant = next(m for m in rapport.manquants if m.stagiaire.pk == scenario["x3"].pk)
    assert manquant.module.pk == scenario["module_m"].pk
    assert manquant.brigade.pk == scenario["brigade_1"].pk


def test_deux_ex_aequo_partagent_le_meme_rang_et_le_suivant_est_decale(examens, session, scenario):
    rapport = ServiceMoyenne.calculer(examens, session)

    rang_y1 = _moyenne_de(rapport, scenario["y1"]).rang_session
    rang_y2 = _moyenne_de(rapport, scenario["y2"]).rang_session
    rang_x1 = _moyenne_de(rapport, scenario["x1"]).rang_session
    rang_x2 = _moyenne_de(rapport, scenario["x2"]).rang_session

    assert rang_y1 == rang_y2 == 1
    assert rang_x1 == 3
    assert rang_x2 == 4


def test_rang_en_brigade_restreint_au_perimetre_de_la_brigade(examens, session, scenario):
    rapport = ServiceMoyenne.calculer(examens, session)

    assert _moyenne_de(rapport, scenario["x1"]).rang_brigade == 1
    assert _moyenne_de(rapport, scenario["x2"]).rang_brigade == 2
    assert _moyenne_de(rapport, scenario["y1"]).rang_brigade == 1
    assert _moyenne_de(rapport, scenario["y2"]).rang_brigade == 1


def test_formative_sans_evaluation_applicable_est_retiree_avec_son_poids(
    examens, session, scenario
):
    """M3, brigade B2 : E1 ne concerne pas B2, seul le certificatif compte
    — la moyenne du module est donc EXACTEMENT la note certificative
    normalisée, pas une moyenne pondérée tronquée."""
    rapport = ServiceMoyenne.calculer(examens, session)

    assert _moyenne_de(rapport, scenario["y1"]).moyenne == decimal.Decimal("20.00")


@override_settings(TRAITEMENT_ABSENCE_NOTE="exclusion")
def test_n6_absence_en_exclusion_retire_l_evaluation_du_calcul(examens, session, scenario):
    """N6, seconde valeur : l'absence de X2 sur E2 exclut l'évaluation du
    calcul du module au lieu de compter zéro — seul le formatif (10) reste,
    sans pondération à partager (le certificatif est retiré avec son poids,
    comme un type sans évaluation, M3)."""
    rapport = ServiceMoyenne.calculer(examens, session)

    assert _moyenne_de(rapport, scenario["x2"]).moyenne == decimal.Decimal("10.00")


# --- US-EVAL-07, V1 (D-277, prompt 47 § 1.2) : `calculer_evaluation` rapporte
# UNE évaluation, jamais la moyenne de son module — mêmes stagiaires que
# `scenario` ci-dessus, pour comparer directement les deux résultats.


def _resultat_de(rapport, stagiaire):
    return next(r for r in rapport.resultats if r.stagiaire.pk == stagiaire.pk)


def test_note_d_une_evaluation_distincte_de_la_moyenne_du_module(examens, session, scenario):
    """X1 : moyenne du module M (E1=16, E2=7/10*20=14, poids 3/1) = 15.50 ;
    la note de la seule E2 doit être 14.00, jamais 15.50."""
    e2 = scenario["e2_certificative_session"]
    rapport = ServiceMoyenne.calculer_evaluation(examens, session, e2)

    assert _resultat_de(rapport, scenario["x1"]).note == decimal.Decimal("14.00")


def test_absence_sur_l_evaluation_affichee_sans_bloquer_le_rang(examens, session, scenario):
    """X2 est absent sur E2 (N6 défaut : compte zéro) — affiché comme
    absent, avec une note et un rang, pas exclu de la liste."""
    e2 = scenario["e2_certificative_session"]
    rapport = ServiceMoyenne.calculer_evaluation(examens, session, e2)

    resultat = _resultat_de(rapport, scenario["x2"])
    assert resultat.absent is True
    assert resultat.note == decimal.Decimal("0.00")


def test_manquant_sur_le_module_n_est_pas_manquant_sur_une_autre_evaluation(
    examens, session, scenario
):
    """X3 est manquant sur E1 (jamais saisie) donc bloqué pour la moyenne du
    module (M5, RG-59 bis) — mais E2 porte bien sa note : il doit apparaître
    dans le résultat de E2, pas dans ses manquants."""
    e2 = scenario["e2_certificative_session"]
    rapport = ServiceMoyenne.calculer_evaluation(examens, session, e2)

    assert not rapport.manquants
    assert _resultat_de(rapport, scenario["x3"]).note == decimal.Decimal("14.00")


def test_evaluation_de_brigade_restreint_le_perimetre_et_le_classement(examens, session, scenario):
    """E1 (formative, brigade B1 seulement, RG-52) ne doit rapporter que
    X1/X2/X3 — Y1/Y2 (brigade B2) absents du résultat ET du classement.
    X3 n'a jamais saisi E1 : manquant, énuméré par cette seule évaluation."""
    e1 = scenario["e1_formative_brigade1"]
    rapport = ServiceMoyenne.calculer_evaluation(examens, session, e1)

    stagiaires_rapportes = {r.stagiaire.pk for r in rapport.resultats}
    assert stagiaires_rapportes == {scenario["x1"].pk, scenario["x2"].pk}
    assert scenario["x3"].pk in {m.stagiaire.pk for m in rapport.manquants}
    assert _resultat_de(rapport, scenario["x1"]).rang_brigade == 1
    assert _resultat_de(rapport, scenario["x1"]).rang_session == 1
