"""US-PLAN-04/US-PLAN-11, Groupes G9, G11, G12 — correction du prompt 55
(R01-VAL03-03, `docs/suivi/DECISIONS.md`, `docs/suivi/PROBLEMES.md`) :
RG-39 a) plafonne le volume programmé par (ÉLÉMENT, BRIGADE), jamais par
élément seul. Scindé de `test_contraintes_volume.py` (G1 à G8, inchangés)
qui dépassait 400 lignes (`.claude/rules/python.md`). Données entièrement
fictives.
"""

import datetime

from planification.models import LigneProgramme, ProgrammeHebdomadaire, Seance
from planification.services.contraintes import Candidate, ServiceContraintes
from planification.tests.conftest import Cours, creer_element, instant, qualifier


def _candidate(brigade, cours, debut, duree_min=120):
    fin = debut + datetime.timedelta(minutes=duree_min)
    return Candidate(
        brigade=brigade,
        element_referentiel=cours.element,
        instructeur=cours.instructeur,
        debut=debut,
        fin=fin,
    )


def _autre_programme(lundi, decalage_semaines=1):
    lundi_autre = lundi + datetime.timedelta(weeks=decalage_semaines)
    return ProgrammeHebdomadaire.objects.create(lundi_de_semaine=lundi_autre)


def _seance_dans(prog, cours, brigade, debut, duree_min=120):
    fin = debut + datetime.timedelta(minutes=duree_min)
    seance = Seance.objects.create(
        programme=prog,
        element_referentiel=cours.element,
        instructeur=cours.instructeur,
        debut=debut,
        fin=fin,
    )
    LigneProgramme.objects.create(seance=seance, brigade=brigade)
    return seance


# --- G9 — le plafond doit s'isoler par brigade ------------------------------


def test_g9_volume_programme_isole_par_brigade_meme_session(
    programme, matiere, instructeur, brigade_formation, autre_brigade_formation
):
    """RG-39 a), conception de référence (`docs/conception/11-cas-
    utilisation.md`, § RG-39) : « le volume programmé D'UNE MATIÈRE POUR
    UNE BRIGADE ne peut excéder le volume prescrit ». `brigade_formation`
    et `autre_brigade_formation` partagent la même session/formation, donc
    le même `ElementReferentiel` — la première a déjà consommé tout le
    prescrit (2 h), la seconde est vierge. Une candidate de 30 min pour la
    seconde doit être acceptée : elle n'a RIEN programmé elle-même."""
    formation = brigade_formation.session.formation
    lundi = programme.lundi_de_semaine
    cours = Cours(creer_element(formation, matiere, volume=2), instructeur)
    qualifier(instructeur, matiere)
    autre_programme = _autre_programme(lundi)
    _seance_dans(
        autre_programme, cours, brigade_formation, instant(autre_programme.lundi_de_semaine, 0, 8)
    )
    candidate = _candidate(autre_brigade_formation, cours, instant(lundi, 0, 8), duree_min=30)

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert verdict.accepte, (
        "la brigade vierge ne devrait jamais être bloquée par le volume déjà "
        "consommé d'une AUTRE brigade de la même session"
    )


# --- G11 — une séance regroupée compte UNE FOIS par brigade ----------------


def test_g11_seance_regroupee_compte_une_fois_pour_chacune_de_ses_brigades(
    programme, matiere, instructeur, brigade, autre_brigade
):
    """RG-32/D-139 : une séance regroupée porte UNE LIGNE PAR BRIGADE, même
    séance (comme la séance pk=3 du jeu `complet`, M2 EXP1+EXP2, prompt
    51). Chaque brigade doit la voir intégralement dans son propre volume
    programmé — ni zéro (elle y participe bien), ni deux fois la durée
    totale (ce n'est pas deux séances distinctes)."""
    formation = brigade.session.formation
    lundi = programme.lundi_de_semaine
    cours = Cours(creer_element(formation, matiere, volume=4), instructeur)
    qualifier(instructeur, matiere)
    autre_programme = _autre_programme(lundi)
    debut = instant(autre_programme.lundi_de_semaine, 0, 8)
    seance = Seance.objects.create(
        programme=autre_programme,
        element_referentiel=cours.element,
        instructeur=cours.instructeur,
        debut=debut,
        fin=debut + datetime.timedelta(minutes=90),
    )
    LigneProgramme.objects.create(seance=seance, brigade=brigade)
    LigneProgramme.objects.create(seance=seance, brigade=autre_brigade)

    contexte = ServiceContraintes.contexte(programme)

    cle_brigade = (cours.element.pk, brigade.pk)
    cle_autre = (cours.element.pk, autre_brigade.pk)
    assert contexte.volume_programme_par_element_brigade.get(cle_brigade, 0) == 1.5
    assert contexte.volume_programme_par_element_brigade.get(cle_autre, 0) == 1.5


# --- G12 — le cumul DU LOT s'isole aussi par brigade ------------------------


def test_g12_lot_de_generation_isole_le_cumul_par_brigade(
    programme, matiere, instructeur, brigade_formation, autre_brigade_formation
):
    """Même risque que G9, mais DANS LE MÊME LOT de génération (`verifier_
    lot`/`_volume_lot`), pas seulement contre la base déjà en db : une
    génération place plusieurs candidates dans UN SEUL appel, pour
    plusieurs brigades. Trois candidates dans le même lot : la première
    brigade consomme 1,5 h (acceptée), la seconde brigade — de la même
    session, sur la même matière — ne doit PAS être bloquée par le lot de
    la première (acceptée elle aussi) ; mais la première brigade reste
    plafonnée par SON PROPRE cumul de lot quand elle revient (1,5 + 1 =
    2,5 > 2, refusée)."""
    formation = brigade_formation.session.formation
    lundi = programme.lundi_de_semaine
    cours = Cours(creer_element(formation, matiere, volume=2), instructeur)
    qualifier(instructeur, matiere)
    candidate_b1_1 = _candidate(brigade_formation, cours, instant(lundi, 0, 8), duree_min=90)
    candidate_b2_1 = _candidate(autre_brigade_formation, cours, instant(lundi, 0, 10), duree_min=90)
    candidate_b1_2 = _candidate(brigade_formation, cours, instant(lundi, 0, 13), duree_min=60)

    verdicts = ServiceContraintes.verifier_lot(
        [candidate_b1_1, candidate_b2_1, candidate_b1_2], ServiceContraintes.contexte(programme)
    )

    assert verdicts[0].accepte
    assert verdicts[
        1
    ].accepte, "la seconde brigade ne doit pas être bloquée par le lot de la première"
    assert not verdicts[2].accepte, "la première brigade reste plafonnée par SON PROPRE lot"
