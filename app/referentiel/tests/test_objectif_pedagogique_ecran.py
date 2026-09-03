"""US-REF-05 — écrans des objectifs pédagogiques : fiche matière (§ 6.1) et
référentiel d'une formation, en lecture seule (§ 3, § 6.2). Le service est
testé dans test_objectif_pedagogique.py, la contrainte différée dans
test_objectif_pedagogique_ordre.py.
"""

from django.urls import reverse

from referentiel.models import ObjectifPedagogique
from referentiel.services.objectif_pedagogique import ServiceObjectifPedagogique
from referentiel.services.referentiel import ServiceReferentiel
from referentiel.tests.conftest import donnees_element_referentiel as _donnees

# --- Fiche matière : critère 1, ajout, modification, réordonnancement, suppression ---


def test_les_objectifs_de_la_matiere_apparaissent_sur_sa_fiche(client, redacteur, matiere):
    ServiceObjectifPedagogique.ajouter(redacteur, matiere, "Analyser un schéma électronique")
    client.force_login(redacteur)

    reponse = client.get(reverse("referentiel:detail_matiere", args=[matiere.pk]))

    assert reponse.status_code == 200
    assert "Analyser un schéma électronique" in reponse.content.decode()


def test_ajout_d_un_objectif_depuis_la_fiche_matiere(client, redacteur, matiere):
    client.force_login(redacteur)

    reponse = client.post(
        reverse("referentiel:ajouter_objectif_pedagogique", args=[matiere.pk]),
        {"libelle": "Câbler un poste radio"},
    )

    assert reponse.status_code == 302
    assert ObjectifPedagogique.objects.filter(
        matiere=matiere, libelle="Câbler un poste radio"
    ).exists()


def test_modification_du_libelle_depuis_la_fiche_matiere(client, redacteur, matiere):
    objectif = ServiceObjectifPedagogique.ajouter(redacteur, matiere, "Premier")
    client.force_login(redacteur)

    client.post(
        reverse("referentiel:modifier_objectif_pedagogique", args=[matiere.pk, objectif.pk]),
        {"libelle": "Premier objectif révisé"},
    )

    objectif.refresh_from_db()
    assert objectif.libelle == "Premier objectif révisé"


def test_monter_et_descendre_echangent_les_positions(client, redacteur, matiere):
    premier = ServiceObjectifPedagogique.ajouter(redacteur, matiere, "Premier")
    second = ServiceObjectifPedagogique.ajouter(redacteur, matiere, "Second")
    client.force_login(redacteur)

    client.post(
        reverse("referentiel:descendre_objectif_pedagogique", args=[matiere.pk, premier.pk])
    )

    premier.refresh_from_db()
    second.refresh_from_db()
    assert premier.ordre == 2
    assert second.ordre == 1


def test_suppression_demande_confirmation_avant_execution(client, redacteur, matiere):
    objectif = ServiceObjectifPedagogique.ajouter(redacteur, matiere, "Premier")
    client.force_login(redacteur)

    reponse = client.get(
        reverse("referentiel:supprimer_objectif_pedagogique", args=[matiere.pk, objectif.pk])
    )

    assert reponse.status_code == 200
    assert ObjectifPedagogique.objects.filter(pk=objectif.pk).exists()


def test_suppression_confirmee_efface_l_objectif(client, redacteur, matiere):
    objectif = ServiceObjectifPedagogique.ajouter(redacteur, matiere, "Premier")
    client.force_login(redacteur)

    client.post(
        reverse("referentiel:supprimer_objectif_pedagogique", args=[matiere.pk, objectif.pk])
    )

    assert not ObjectifPedagogique.objects.filter(pk=objectif.pk).exists()


def test_lecteur_ne_peut_pas_ecrire_depuis_la_fiche_matiere(client, lecteur, matiere):
    client.force_login(lecteur)

    reponse = client.post(
        reverse("referentiel:ajouter_objectif_pedagogique", args=[matiere.pk]),
        {"libelle": "Tentative refusée"},
    )

    assert reponse.status_code == 403
    assert not ObjectifPedagogique.objects.filter(matiere=matiere).exists()


# --- Référentiel d'une formation : critère 3, lecture seule (§ 6.2) ---


def test_les_objectifs_apparaissent_sur_le_referentiel_de_chaque_formation_utilisatrice(
    client, redacteur, formation, matiere
):
    ServiceObjectifPedagogique.ajouter(redacteur, matiere, "Analyser un schéma électronique")
    ServiceReferentiel.rattacher(redacteur, formation, matiere, _donnees())
    client.force_login(redacteur)

    reponse = client.get(reverse("referentiel:referentiel_formation", args=[formation.pk]))

    assert reponse.status_code == 200
    assert "Analyser un schéma électronique" in reponse.content.decode()


def test_le_referentiel_d_une_formation_n_offre_aucune_action_d_ecriture_sur_les_objectifs(
    client, redacteur, formation, matiere
):
    """§ 6.2 : l'objectif se gère depuis la fiche matière, jamais depuis le
    référentiel d'une formation — une compétence ne change pas selon la
    formation qui la dispense (§ 2.1).
    """
    ServiceObjectifPedagogique.ajouter(redacteur, matiere, "Analyser un schéma électronique")
    ServiceReferentiel.rattacher(redacteur, formation, matiere, _donnees())
    client.force_login(redacteur)

    reponse = client.get(reverse("referentiel:referentiel_formation", args=[formation.pk]))

    contenu = reponse.content.decode()
    assert reverse("referentiel:ajouter_objectif_pedagogique", args=[matiere.pk]) not in contenu
    assert (
        reverse(
            "referentiel:supprimer_objectif_pedagogique",
            args=[matiere.pk, ObjectifPedagogique.objects.get().pk],
        )
        not in contenu
    )
