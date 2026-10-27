"""Programmes ajoutés par l'état `complet` — Prompt 51, § 2.4 (quatre
semaines W-2 à W+1) et point d'entrée des réservations d'évaluations
(§ 2.5, voir `reservations_complet.py`) et des avenants de W0 (voir
`avenants_complet.py`).

Horloge simulée : `freezegun.freeze_time`, importé ICI, à l'intérieur des
fonctions qui le consomment, jamais en tête de module (même précaution que
pypdf/WeasyPrint, P-44, docs/suivi/PROBLEMES.md ; décision D-296) — une
installation sans `freezegun` démarre normalement.

Aucune garde explicite n'empêche `ServiceGeneration.generer` d'agir sur une
semaine passée ou future (vérifié dans le code, pas supposé) : l'horloge
n'est donc pas nécessaire pour que les appels de génération PASSENT, mais
pour que les champs horodatés (`date_soumission`, `date_validation`,
`date_signature`, `date_affichage`) restent cohérents ENTRE EUX —
`enregistrer_signature` compare `date_signature` à la fois à « aujourd'hui »
et à `programme.date_validation` réellement stocké (`circuit.py::
_verifier_signature`) : sans geler l'horloge à CHAQUE étape, une validation
posée à la date réelle du chargement rendrait toute signature antérieure
simulée irrecevable.

E1/E2/E5 sont réservées AVANT toute génération (même avant W-2) : le budget
d'heures de M1 (40 h, large), M2 (30 h) et surtout M4 (F2 socle, 10 h au
total — serré) doit être amputé de la durée de chaque contrôle avant que la
génération des semaines suivantes ne consomme tout le volume restant et ne
laisse plus de marge (RG-39) — l'ordre inverse (réserver après coup) échoue
dès que les semaines déjà générées ont épuisé le prescrit. La génération
préserve explicitement les séances verrouillées
(`_seances_verrouillees_preservees`, `planification.services.generation`)
et comble le reste de chaque semaine autour d'elles.
"""

import datetime

from django.core.management.base import CommandError
from django.utils import timezone

from evaluations.jeu_recette.avenants_complet import poser_avenants_w0
from evaluations.jeu_recette.creneaux import creneau_libre
from evaluations.jeu_recette.reservations_complet import (
    SpecificationControle,
    inserer_controle,
    reserver_m2_regroupe,
)
from evaluations.jeu_recette.semaines import jour_de_semaine, semaine
from planification.models import ProgrammeHebdomadaire
from planification.selectors import JOUR_SEMAINE_PAR_ISO, grille_active_avec_creneaux
from planification.services.circuit import ServiceCircuitProgramme
from planification.services.generation import ServiceGeneration

LUNDI_ISO, MARDI_ISO, MERCREDI_ISO, JEUDI_ISO, VENDREDI_ISO, SAMEDI_ISO = 1, 2, 3, 4, 5, 6
SIGNATAIRE = "Directeur de la formation (fictif)"


def _instant(jour, heure=9, minute=0):
    return timezone.make_aware(datetime.datetime.combine(jour, datetime.time(heure, minute)))


def _filtrer_jour(creneaux, jour_iso):
    return [c for c in creneaux if JOUR_SEMAINE_PAR_ISO[c.jour_semaine] == jour_iso]


def obtenir_programme_vide(contexte, decalage_semaine):
    """Crée (ou retrouve) le programme BROUILLON d'une semaine, sans le
    générer — pour qu'un appelant puisse y insérer une séance verrouillée
    avant que la génération ne remplisse le reste autour d'elle."""
    lundi = semaine(contexte.date_reference, decalage_semaine)
    programme, _ = ProgrammeHebdomadaire.objects.get_or_create(lundi_de_semaine=lundi)
    return programme


def _approuver(contexte, programme, jour_soumission, jour_signature):
    from freezegun import freeze_time

    with freeze_time(_instant(jour_soumission)):
        ServiceCircuitProgramme.soumettre(contexte.agissant_plan, programme)
        programme.refresh_from_db()
        ServiceCircuitProgramme.valider(contexte.agissant_ped, programme)
        programme.refresh_from_db()
    with freeze_time(_instant(jour_signature)):
        ServiceCircuitProgramme.enregistrer_signature(
            contexte.agissant_plan, programme, jour_signature, SIGNATAIRE
        )
        programme.refresh_from_db()
        ServiceCircuitProgramme.afficher(contexte.agissant_plan, programme)
        programme.refresh_from_db()
    return programme


def _generer_et_approuver(contexte, lundi, jours):
    """`jours` : (jour_generation, jour_soumission, jour_signature) —
    chronologie simulée complète d'une semaine, du BROUILLON à l'AFFICHÉ
    (§ 2.4)."""
    from freezegun import freeze_time

    jour_generation, jour_soumission, jour_signature = jours
    with freeze_time(_instant(jour_generation)):
        programme = ServiceGeneration.generer(
            contexte.agissant_plan, lundi, contexte.toutes_brigades
        ).programme
    _approuver(contexte, programme, jour_soumission, jour_signature)
    contexte.stdout.write(f"  Programme {lundi.isoformat()} généré, approuvé et affiché.")
    return programme


def _reserver_e1_e5(contexte, programme_w1, jeudi_w1, creneaux_jeudi):
    evaluation_e1 = inserer_controle(
        contexte,
        SpecificationControle(
            programme=programme_w1,
            element_referentiel=contexte.elements_f6["M1"],
            brigade=contexte.exp1,
            jour=jeudi_w1,
            instructeur=contexte.instructeurs["I2"],
            lieu=contexte.exp1.salle_attitree.lieu,
            creneaux=creneaux_jeudi,
            libelle="E1",
        ),
    )
    evaluation_e5 = inserer_controle(
        contexte,
        SpecificationControle(
            programme=programme_w1,
            element_referentiel=contexte.element_m4_socle,
            brigade=contexte.cdp1,
            jour=jeudi_w1,
            instructeur=contexte.instructeurs["I5"],
            lieu=contexte.cdp1.salle_attitree.lieu,
            creneaux=creneaux_jeudi,
            libelle="E5",
        ),
    )
    return evaluation_e1, evaluation_e5


def _reserver_m2(contexte, programme_w1, mardi_w1, creneaux_mardi):
    creneau_m2 = creneau_libre(programme_w1, contexte.exp1, MARDI_ISO, creneaux_mardi)
    if creneau_m2 is None:
        raise CommandError(
            "Aucun créneau libre le mardi de W-1 pour EXP1 — regroupement M2 impossible."
        )
    reserver_m2_regroupe(contexte, programme_w1, mardi_w1, creneau_m2)


def _reserver_e2(contexte, mercredi_w_plus_1, creneaux_mercredi):
    programme_w_plus_1 = obtenir_programme_vide(contexte, 1)
    return inserer_controle(
        contexte,
        SpecificationControle(
            programme=programme_w_plus_1,
            element_referentiel=contexte.elements_f6["M2"],
            brigade=contexte.exp2,
            jour=mercredi_w_plus_1,
            instructeur=contexte.instructeurs["I1"],
            lieu=contexte.lieux["L9"],
            creneaux=creneaux_mercredi,
            libelle="E2",
        ),
    )


def _reserver_controles_et_m2(contexte):
    """E1 (M1, EXP1), E5 (M4 socle, CDP1) et la séance M2 regroupée
    (EXP1+EXP2) réservées au même instant, le plus tôt possible (jeudi
    W-3) ; E2 (M2, EXP2, mercredi W+1) réservée dans la foulée — voir le
    docstring du module."""
    from freezegun import freeze_time

    date_reference = contexte.date_reference
    jeudi_reservation = jour_de_semaine(date_reference, -3, JEUDI_ISO)
    _, creneaux = grille_active_avec_creneaux()

    with freeze_time(_instant(jeudi_reservation)):
        programme_w1 = obtenir_programme_vide(contexte, -1)
        evaluation_e1, evaluation_e5 = _reserver_e1_e5(
            contexte,
            programme_w1,
            jour_de_semaine(date_reference, -1, JEUDI_ISO),
            _filtrer_jour(creneaux, JEUDI_ISO),
        )
        _reserver_m2(
            contexte,
            programme_w1,
            jour_de_semaine(date_reference, -1, MARDI_ISO),
            _filtrer_jour(creneaux, MARDI_ISO),
        )
        evaluation_e2 = _reserver_e2(
            contexte,
            jour_de_semaine(date_reference, 1, MERCREDI_ISO),
            _filtrer_jour(creneaux, MERCREDI_ISO),
        )
    return evaluation_e1, evaluation_e2, evaluation_e5


def _generer_semaine_moins_2(contexte):
    date_reference = contexte.date_reference
    jours = (
        jour_de_semaine(date_reference, -3, JEUDI_ISO),
        jour_de_semaine(date_reference, -3, VENDREDI_ISO),
        jour_de_semaine(date_reference, -3, SAMEDI_ISO),
    )
    return _generer_et_approuver(contexte, semaine(date_reference, -2), jours)


def _generer_semaine_moins_1(contexte):
    """E1/E5/M2 regroupée déjà réservées (`_reserver_controles_et_m2`) :
    cette génération les préserve et comble le reste de la semaine
    autour d'elles."""
    from freezegun import freeze_time

    date_reference = contexte.date_reference
    lundi_w1 = semaine(date_reference, -1)
    with freeze_time(_instant(jour_de_semaine(date_reference, -2, JEUDI_ISO))):
        programme = ServiceGeneration.generer(
            contexte.agissant_plan, lundi_w1, contexte.toutes_brigades
        ).programme
    _approuver(
        contexte,
        programme,
        jour_de_semaine(date_reference, -2, VENDREDI_ISO),
        jour_de_semaine(date_reference, -2, SAMEDI_ISO),
    )
    contexte.stdout.write(
        "  Programme W-1 généré, contrôles E1/E5 insérés, M2 regroupée, approuvé et affiché."
    )
    return programme


def _generer_semaine_zero(contexte):
    date_reference = contexte.date_reference
    jours = (
        jour_de_semaine(date_reference, -1, JEUDI_ISO),
        jour_de_semaine(date_reference, -1, VENDREDI_ISO),
        jour_de_semaine(date_reference, -1, SAMEDI_ISO),
    )
    programme = _generer_et_approuver(contexte, semaine(date_reference, 0), jours)
    poser_avenants_w0(contexte, programme)
    return programme


def _generer_semaine_plus_1(contexte):
    """E2 déjà réservée (`_reserver_controles_et_m2`) : générée le jour D
    (horloge réelle), reste BROUILLON."""
    programme = ServiceGeneration.generer(
        contexte.agissant_plan, semaine(contexte.date_reference, 1), contexte.toutes_brigades
    ).programme
    contexte.stdout.write("  Programme W+1 généré (brouillon, horloge réelle, E2 déjà insérée).")
    return programme


def charger_programmes_complet(contexte):
    """§ 2.4 (quatre semaines) + réservation de E1/E2/E5 (§ 2.5). Rend
    `(programmes, evaluation_e1, evaluation_e2, evaluation_e5)`."""
    programmes = {}
    evaluation_e1, evaluation_e2, evaluation_e5 = _reserver_controles_et_m2(contexte)
    programmes["W-2"] = _generer_semaine_moins_2(contexte)
    programmes["W-1"] = _generer_semaine_moins_1(contexte)
    programmes["W0"] = _generer_semaine_zero(contexte)
    programmes["W+1"] = _generer_semaine_plus_1(contexte)
    return programmes, evaluation_e1, evaluation_e2, evaluation_e5
