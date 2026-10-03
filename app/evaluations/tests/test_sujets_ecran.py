"""US-EVAL-03 — écran dédié des sujets : confidentialité (bloc C) et cycle
HTTP réel (bloc E). Fixtures partagées avec `test_sujets.py` dans
`evaluations/tests/conftest.py` (`.claude/rules/python.md`, fichier sous
400 lignes). Données entièrement fictives.
"""

import datetime

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from administration.models import EntreeJournal, TypeAction
from evaluations.models import Sujet
from evaluations.selectors import evaluations_non_pretes
from evaluations.services.evaluation import ServiceEvaluation
from evaluations.services.sujet import ServiceSujet
from evaluations.tests.conftest import _enregistrer

# --- C — Confidentialité -----------------------------------------------------


def test_c1_chaque_get_cree_une_entree_de_consultation(client, examens, certificative):
    client.force_login(examens)
    url = reverse("evaluations:sujets", args=[certificative.pk])
    avant = EntreeJournal.objects.filter(type_action=TypeAction.CONSULTATION_SUJETS).count()
    client.get(url)
    client.get(url)
    apres = EntreeJournal.objects.filter(type_action=TypeAction.CONSULTATION_SUJETS).count()
    assert apres - avant == 2


def test_c2_get_refuse_aucune_entree(client, direction_formation, certificative):
    """Un 403 journalise déjà `ACCES_REFUSE` (mécanisme RG-02 existant,
    `administration.habilitations.verifier_habilitation`) — ce que C2
    exige d'absent, c'est une entrée `CONSULTATION_SUJETS`, jamais le
    journal entier."""
    client.force_login(direction_formation)
    avant = EntreeJournal.objects.filter(type_action=TypeAction.CONSULTATION_SUJETS).count()
    reponse = client.get(reverse("evaluations:sujets", args=[certificative.pk]))
    assert reponse.status_code == 403
    assert EntreeJournal.objects.filter(type_action=TypeAction.CONSULTATION_SUJETS).count() == avant


def test_c3_journal_ne_contient_jamais_une_reference(client, examens, certificative):
    reference = "Pli confidentiel 42-Alpha"
    client.force_login(examens)
    url = reverse("evaluations:sujets", args=[certificative.pk])
    client.post(url, {"reference": reference, "date_depot": timezone.localdate().isoformat()})
    sujet = certificative.sujets.get()
    client.post(reverse("evaluations:retenir_sujet", args=[sujet.pk]), {"confirmation": "on"})
    client.get(url)

    for entree in EntreeJournal.objects.all():
        assert reference not in entree.detail
        assert reference not in entree.identifiant_saisi
        assert reference not in entree.cible


def test_c4_sujet_absent_de_l_admin_et_str_sans_reference(certificative):
    from django.contrib import admin

    assert Sujet not in admin.site._registry
    sujet = Sujet(evaluation=certificative, rang=1, reference="Pli secret")
    assert "Pli secret" not in str(sujet)


def test_c5_detail_lu_par_direction_formation_sans_reference_ni_rang(
    client, direction_formation, examens, certificative
):
    sujet = _enregistrer(examens, certificative, "Pli très confidentiel")
    ServiceSujet.retenir(examens, sujet, confirmation=True)

    client.force_login(direction_formation)
    reponse = client.get(reverse("evaluations:detail_evaluation", args=[certificative.pk]))
    contenu = reponse.content.decode()
    assert "Pli très confidentiel" not in contenu
    assert "n° 1" not in contenu
    assert "1 sujet enregistré" in contenu
    assert "<dd>Oui</dd>" in contenu


# --- E — Cycle HTTP réel -----------------------------------------------------


def test_e1_deux_sujets_puis_retenue_par_la_cellule_examens(client, examens, certificative):
    client.force_login(examens)
    url = reverse("evaluations:sujets", args=[certificative.pk])
    reponse = client.post(
        url, {"reference": "Pli 1", "date_depot": timezone.localdate().isoformat()}
    )
    assert reponse.status_code == 302
    reponse = client.post(
        url, {"reference": "Pli 2", "date_depot": timezone.localdate().isoformat()}
    )
    assert reponse.status_code == 302

    sujet_un = certificative.sujets.get(rang=1)
    reponse = client.post(reverse("evaluations:retenir_sujet", args=[sujet_un.pk]), {})
    assert reponse.status_code == 302

    reponse = client.get(url)
    assert "Retenu" in reponse.content.decode()
    assert (
        EntreeJournal.objects.filter(type_action=TypeAction.CREATION_ELEMENT_GESTION).count() >= 2
    )
    assert EntreeJournal.objects.filter(type_action=TypeAction.SELECTION_SUJET).exists()


def test_e2_retenue_sujet_unique_sans_confirmation_reaffiche_avertissement(
    client, examens, certificative
):
    """`retenir_sujet` est un bouton d'action en ligne sur l'écran des
    sujets, jamais une page de formulaire autonome (contrairement à
    `modifier_date_certificative`) : le refus se traduit par une
    redirection avec avertissement, pas un réaffichage du même template —
    même observable pour l'utilisateur (rien de retenu, avertissement
    visible), mécanique différente."""
    client.force_login(examens)
    sujet = _enregistrer(examens, certificative, "Pli unique")
    reponse = client.post(reverse("evaluations:retenir_sujet", args=[sujet.pk]), {}, follow=True)
    assert "RG-50" in reponse.content.decode()
    assert not Sujet.objects.get(pk=sujet.pk).retenu


def test_e3_troisieme_sujet_en_post_refuse_formulaire_reaffiche(client, examens, certificative):
    """Un POST refusé redirige vers l'écran (jamais un rendu direct après
    POST, A6 : seul le GET qui suit journalise une consultation — vérifié
    ci-dessous, une seule entrée pour ce GET, pas deux)."""
    client.force_login(examens)
    url = reverse("evaluations:sujets", args=[certificative.pk])
    client.post(url, {"reference": "Pli 1", "date_depot": timezone.localdate().isoformat()})
    client.post(url, {"reference": "Pli 2", "date_depot": timezone.localdate().isoformat()})
    avant = EntreeJournal.objects.filter(type_action=TypeAction.CONSULTATION_SUJETS).count()
    reponse = client.post(
        url, {"reference": "Pli 3", "date_depot": timezone.localdate().isoformat()}, follow=True
    )
    assert "RG-50" in reponse.content.decode()
    assert certificative.sujets.count() == 2
    assert (
        EntreeJournal.objects.filter(type_action=TypeAction.CONSULTATION_SUJETS).count()
        == avant + 1
    )


def _certificative_a_venir(examens, session, element_referentiel, decalage_jours):
    return ServiceEvaluation.creer(
        examens,
        {
            "element_referentiel": element_referentiel,
            "type": "certificative",
            "session": session,
            "brigade": None,
            "date": timezone.localdate() + datetime.timedelta(days=decalage_jours),
            "creneau_type": None,
            "instructeur": None,
            "lieu": None,
            "motif_date_passee": "",
        },
    )


def test_e4_badge_non_prete_nombre_de_requetes_stable(
    client, examens, session, element_referentiel
):
    autres = [
        _certificative_a_venir(examens, session, element_referentiel, 30 + indice).pk
        for indice in range(10)
    ]

    with CaptureQueriesContext(connection) as une:
        non_pretes_une = evaluations_non_pretes(autres[:1])
    with CaptureQueriesContext(connection) as dix:
        non_pretes_dix = evaluations_non_pretes(autres)

    assert len(une) == len(dix)
    assert autres[0] in non_pretes_une
    assert set(autres).issubset(non_pretes_dix)


def test_e5_get_ecran_sujets_par_direction_formation_403_sans_journal(
    client, direction_formation, certificative
):
    """Aucune entrée `CONSULTATION_SUJETS` — le 403 journalise par ailleurs
    `ACCES_REFUSE` (RG-02, mécanisme existant, hors périmètre de C2/E5)."""
    client.force_login(direction_formation)
    avant = EntreeJournal.objects.filter(type_action=TypeAction.CONSULTATION_SUJETS).count()
    reponse = client.get(reverse("evaluations:sujets", args=[certificative.pk]))
    assert reponse.status_code == 403
    assert EntreeJournal.objects.filter(type_action=TypeAction.CONSULTATION_SUJETS).count() == avant
