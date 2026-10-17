"""US-EVAL-05 — écran dédié des notes : confidentialité (N5) et cycle HTTP
réel (N3). Fixtures partagées avec `test_notes.py` dans
`evaluations/tests/conftest.py`. Données entièrement fictives.
"""

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from administration.models import EntreeJournal, TypeAction
from evaluations.models import Note
from evaluations.services.note import ServiceNote
from evaluations.tests.conftest import affecter_stagiaires

# --- Confidentialité (N5) -----------------------------------------------


def test_chaque_get_cree_une_entree_de_consultation(client, examens, certificative):
    client.force_login(examens)
    url = reverse("evaluations:notes", args=[certificative.pk])
    avant = EntreeJournal.objects.filter(type_action=TypeAction.CONSULTATION_NOTES).count()
    client.get(url)
    client.get(url)
    apres = EntreeJournal.objects.filter(type_action=TypeAction.CONSULTATION_NOTES).count()
    assert apres - avant == 2


def test_get_refuse_par_la_direction_aucune_entree(client, direction_formation, certificative):
    """Un 403 journalise déjà `ACCES_REFUSE` (mécanisme RG-02 existant) — ce
    que N5 exige d'absent, c'est une entrée `CONSULTATION_NOTES`, jamais le
    journal entier."""
    client.force_login(direction_formation)
    avant = EntreeJournal.objects.filter(type_action=TypeAction.CONSULTATION_NOTES).count()
    reponse = client.get(reverse("evaluations:notes", args=[certificative.pk]))
    assert reponse.status_code == 403
    assert EntreeJournal.objects.filter(type_action=TypeAction.CONSULTATION_NOTES).count() == avant


def test_get_refuse_a_la_pedagogique(client, redacteur, certificative):
    client.force_login(redacteur)
    reponse = client.get(reverse("evaluations:notes", args=[certificative.pk]))
    assert reponse.status_code == 403


def test_journal_ne_contient_jamais_la_valeur_hors_des_champs_dedies(
    client, examens, brigade, redacteur, certificative
):
    stagiaire = affecter_stagiaires(redacteur, brigade, 1, prefixe="JRN1")[0]
    client.force_login(examens)
    url_notes = reverse("evaluations:notes", args=[certificative.pk])
    reponse = client.post(
        url_notes,
        {f"valeur_{stagiaire.pk}": "17", f"absent_{stagiaire.pk}": ""},
    )
    client.post(
        reverse("evaluations:confirmer_notes", args=[certificative.pk]),
        {"lignes_b64": reponse.context["lignes_b64"]},
    )

    for entree in EntreeJournal.objects.all():
        assert "17" not in entree.identifiant_saisi
        assert "17" not in entree.detail
        assert "17" not in entree.cible


# --- Cycle HTTP réel (N3) -------------------------------------------------


def test_etape_de_verification_n_ecrit_rien(client, examens, brigade, redacteur, certificative):
    stagiaire = affecter_stagiaires(redacteur, brigade, 1, prefixe="VER1")[0]
    client.force_login(examens)

    reponse = client.post(
        reverse("evaluations:notes", args=[certificative.pk]),
        {f"valeur_{stagiaire.pk}": "12", f"absent_{stagiaire.pk}": ""},
    )

    assert reponse.status_code == 200
    assert not Note.objects.filter(evaluation=certificative, stagiaire=stagiaire).exists()
    assert "lignes_b64" in reponse.context


def test_confirmation_ecrit_reellement_les_notes(
    client, examens, brigade, redacteur, certificative
):
    stagiaire = affecter_stagiaires(redacteur, brigade, 1, prefixe="CONF1")[0]
    client.force_login(examens)
    rapport = client.post(
        reverse("evaluations:notes", args=[certificative.pk]),
        {f"valeur_{stagiaire.pk}": "13", f"absent_{stagiaire.pk}": ""},
    )

    reponse = client.post(
        reverse("evaluations:confirmer_notes", args=[certificative.pk]),
        {"lignes_b64": rapport.context["lignes_b64"]},
        follow=True,
    )

    assert reponse.status_code == 200
    assert Note.objects.filter(evaluation=certificative, stagiaire=stagiaire, valeur=13).exists()


def test_confirmation_sans_verification_prealable_refuse_proprement(client, examens, certificative):
    """L'état a expiré (ou n'a jamais existé) : message explicite, pas une
    erreur technique."""
    client.force_login(examens)

    reponse = client.post(
        reverse("evaluations:confirmer_notes", args=[certificative.pk]), {}, follow=True
    )

    assert reponse.status_code == 200
    assert "expiré" in reponse.content.decode("utf-8").lower()


def test_requetes_de_la_grille_constantes_avec_dix_et_quarante_stagiaires(
    client, examens, brigade, redacteur, certificative
):
    affecter_stagiaires(redacteur, brigade, 10, prefixe="Q1")
    url = reverse("evaluations:notes", args=[certificative.pk])
    client.force_login(examens)

    client.get(url)  # appel de chauffe (P-39) : cache de permissions
    with CaptureQueriesContext(connection) as dix:
        client.get(url)

    affecter_stagiaires(redacteur, brigade, 30, prefixe="Q2")
    with CaptureQueriesContext(connection) as quarante:
        client.get(url)

    assert len(dix.captured_queries) == len(quarante.captured_queries)


def test_consulter_journalise_une_seule_fois_par_appel(examens, brigade, redacteur, certificative):
    affecter_stagiaires(redacteur, brigade, 1, prefixe="UNQ1")
    avant = EntreeJournal.objects.filter(type_action=TypeAction.CONSULTATION_NOTES).count()

    ServiceNote.consulter(examens, certificative)

    assert (
        EntreeJournal.objects.filter(type_action=TypeAction.CONSULTATION_NOTES).count() - avant == 1
    )
