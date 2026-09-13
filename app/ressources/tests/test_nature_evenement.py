"""US-PLAN-01, Groupe A — `NatureEvenement`, patron de gestion (CLS-03,
Prompt 28, § 3). Données entièrement fictives.
"""

import pytest
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.urls import reverse

from administration.models import EntreeJournal, TypeAction
from noyau.exceptions import ErreurValidation
from ressources.models import NatureEvenement, PeriodeCalendrier
from ressources.services.nature_evenement import ServiceNatureEvenement

# --- A1 — CRUD nominal, journalisé -------------------------------------------


def test_a1_creation_modification_suppression_sont_journalisees(planificateur):
    nature = ServiceNatureEvenement.creer(
        planificateur, {"libelle": "Stage", "effet_par_defaut": "bloquant"}
    )
    ServiceNatureEvenement.modifier(
        planificateur,
        nature.pk,
        {"libelle": "Stage interarmes", "effet_par_defaut": "bloquant"},
        nature.modifie_le,
    )
    ServiceNatureEvenement.supprimer(planificateur, nature.pk)

    natures = list(
        EntreeJournal.objects.filter(objet_type="nature_evenement")
        .order_by("cree_le")
        .values_list("type_action", flat=True)
    )
    assert TypeAction.CREATION_ELEMENT_GESTION in natures
    assert TypeAction.MODIFICATION_ELEMENT_GESTION in natures
    assert TypeAction.SUPPRESSION_ELEMENT_GESTION in natures


# --- A2 — unicité du libellé, casse indifférente -----------------------------


def test_a2_unicite_du_libelle_insensible_a_la_casse_en_base(db):
    NatureEvenement.objects.create(libelle="Manoeuvre", effet_par_defaut="bloquant")

    with pytest.raises(IntegrityError), transaction.atomic():
        NatureEvenement.objects.create(libelle="manoeuvre", effet_par_defaut="informatif")


def test_a2_service_refuse_le_doublon_de_libelle(planificateur):
    ServiceNatureEvenement.creer(
        planificateur, {"libelle": "Sortie", "effet_par_defaut": "bloquant"}
    )

    with pytest.raises(ErreurValidation):
        ServiceNatureEvenement.creer(
            planificateur, {"libelle": "SORTIE", "effet_par_defaut": "informatif"}
        )


def test_effet_par_defaut_hors_domaine_refuse_par_insertion_directe(db):
    """`ck_nature_evenement_effet` — relecture de conception : une énumération
    (`EffetPeriode`) doit porter une contrainte de vérification en base
    (.claude/rules/modeles.md), pas seulement une validation Python
    contournable par un import ou une requête directe."""
    with pytest.raises(IntegrityError), transaction.atomic():
        NatureEvenement.objects.create(libelle="Hors domaine", effet_par_defaut="autre")


# --- A3 — suppression bloquée par PROTECT, énumération, cycle HTTP réel -----


def test_a3_suppression_refusee_par_service_quand_une_periode_l_utilise(
    planificateur, nature_evenement
):
    PeriodeCalendrier.objects.create(
        nature=nature_evenement,
        intitule="Période essai",
        debut="2026-09-08T08:00:00Z",
        fin="2026-09-08T09:45:00Z",
        effet="bloquant",
    )

    with pytest.raises(ErreurValidation, match="Période essai"):
        ServiceNatureEvenement.supprimer(planificateur, nature_evenement.pk)


def test_a3_suppression_refusee_depuis_l_ecran_reel(client, planificateur, nature_evenement):
    PeriodeCalendrier.objects.create(
        nature=nature_evenement,
        intitule="Période essai HTTP",
        debut="2026-09-08T08:00:00Z",
        fin="2026-09-08T09:45:00Z",
        effet="bloquant",
    )
    client.force_login(planificateur)

    reponse = client.post(
        reverse("ressources:supprimer_nature_evenement", args=[nature_evenement.pk]), follow=True
    )

    assert reponse.status_code == 200
    assert b"P\xc3\xa9riode essai HTTP" in reponse.content
    assert NatureEvenement.objects.filter(pk=nature_evenement.pk).exists()


# --- A4 — les sept natures initiales, chargées par commande ----------------


def test_a4_les_sept_natures_initiales_sont_presentes_avec_leur_effet(db):
    """`initialiser_natures_evenement`, pas une migration de données : voir
    la docstring de la commande — une migration ne survit pas à
    `transactional_db` (`test_objectif_pedagogique_ordre.py`), qui vide la
    base sans `serialized_rollback`. La commande est donc rejouée ici même,
    comme `initialiser_habilitations` l'est par `groupes_habilitation`."""
    call_command("initialiser_natures_evenement")
    attendues = {
        "Cours": "informatif",
        "Conférence": "bloquant",
        "Visite": "bloquant",
        "Congé": "bloquant",
        "Examen": "bloquant",
        "Bivouac": "bloquant",
        "Formation technique": "bloquant",
    }

    for libelle, effet in attendues.items():
        assert NatureEvenement.objects.get(libelle=libelle).effet_par_defaut == effet


def test_a4_commande_idempotente_ne_reecrase_pas_un_effet_deja_modifie(db):
    call_command("initialiser_natures_evenement")
    examen = NatureEvenement.objects.get(libelle="Examen")
    examen.effet_par_defaut = "informatif"
    examen.save()

    call_command("initialiser_natures_evenement")

    examen.refresh_from_db()
    assert examen.effet_par_defaut == "informatif"
