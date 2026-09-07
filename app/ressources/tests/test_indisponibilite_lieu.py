"""US-PLAN-02 — Indisponibilités de lieu, § 3.1 du Prompt 14. Contrainte
d'exclusion `ex_indispo_lieu_chevauchement`, premier usage réel de
`btree_gist` au socle.
"""

import datetime

import pytest
from django.db import IntegrityError, transaction
from django.urls import reverse
from django.utils import timezone

from administration.models import EntreeJournal, TypeAction
from noyau.exceptions import ErreurHabilitation, ErreurValidation
from ressources.models import CategorieLieu, IndisponibiliteLieu, Lieu
from ressources.services.indisponibilite_lieu import ServiceIndisponibiliteLieu


def _instant(jour, heure, minute=0):
    return timezone.make_aware(datetime.datetime(2027, 1, jour, heure, minute))


def test_declaration_d_une_periode_sur_un_lieu(planificateur, lieu):
    """Critère 3."""
    indisponibilite = ServiceIndisponibiliteLieu.declarer(
        planificateur, lieu, _instant(4, 8), _instant(4, 12), "Réfection du sol"
    )

    assert indisponibilite.pk is not None
    assert indisponibilite.lieu_id == lieu.pk


def test_ecriture_refusee_a_la_cellule_pedagogique(redacteur, lieu):
    with pytest.raises(ErreurHabilitation):
        ServiceIndisponibiliteLieu.declarer(
            redacteur, lieu, _instant(4, 8), _instant(4, 12), "Réfection du sol"
        )


def test_fin_anterieure_au_debut_est_refusee_en_base(lieu):
    with pytest.raises(IntegrityError), transaction.atomic():
        IndisponibiliteLieu.objects.create(
            lieu=lieu, debut=_instant(4, 12), fin=_instant(4, 8), motif="Incohérent"
        )


def test_motif_vide_est_refuse_en_base(lieu):
    with pytest.raises(IntegrityError), transaction.atomic():
        IndisponibiliteLieu.objects.create(
            lieu=lieu, debut=_instant(4, 8), fin=_instant(4, 12), motif=""
        )


def test_motif_vide_est_refuse_par_le_service(planificateur, lieu):
    with pytest.raises(ErreurValidation):
        ServiceIndisponibiliteLieu.declarer(
            planificateur, lieu, _instant(4, 8), _instant(4, 12), "   "
        )


def test_fin_anterieure_au_debut_est_refusee_par_le_service(planificateur, lieu):
    with pytest.raises(ErreurValidation):
        ServiceIndisponibiliteLieu.declarer(
            planificateur, lieu, _instant(4, 12), _instant(4, 8), "Incohérent"
        )


def test_deux_periodes_qui_se_recouvrent_sur_le_meme_lieu_sont_refusees_en_base(lieu):
    """§ 3.1 : la contrainte d'exclusion `ex_indispo_lieu_chevauchement`."""
    IndisponibiliteLieu.objects.create(
        lieu=lieu, debut=_instant(4, 8), fin=_instant(4, 12), motif="Réfection du sol"
    )

    with pytest.raises(IntegrityError), transaction.atomic():
        IndisponibiliteLieu.objects.create(
            lieu=lieu, debut=_instant(4, 10), fin=_instant(4, 14), motif="Recouvrement"
        )


def test_deux_periodes_contigues_sans_recouvrement_sont_acceptees(lieu):
    """Le test qu'on oublie (§ 9) : une contrainte mal écrite refuserait
    aussi deux périodes qui se touchent sans se recouvrir."""
    IndisponibiliteLieu.objects.create(
        lieu=lieu, debut=_instant(4, 8), fin=_instant(4, 12), motif="Matinée"
    )

    IndisponibiliteLieu.objects.create(  # ne lève pas
        lieu=lieu, debut=_instant(4, 12), fin=_instant(4, 16), motif="Après-midi"
    )


def test_deux_periodes_qui_se_recouvrent_sur_deux_lieux_differents_sont_acceptees(lieu):
    autre_lieu = Lieu.objects.create(
        intitule="Salle 102", capacite=25, categorie=CategorieLieu.SALLE_ATTITREE
    )
    IndisponibiliteLieu.objects.create(
        lieu=lieu, debut=_instant(4, 8), fin=_instant(4, 12), motif="Réfection du sol"
    )

    IndisponibiliteLieu.objects.create(  # ne lève pas
        lieu=autre_lieu, debut=_instant(4, 8), fin=_instant(4, 12), motif="Désinfection"
    )


def test_le_message_d_erreur_nomme_la_periode_existante(planificateur, lieu):
    ServiceIndisponibiliteLieu.declarer(
        planificateur, lieu, _instant(4, 8), _instant(4, 12), "Réfection du sol"
    )

    with pytest.raises(ErreurValidation) as info:
        ServiceIndisponibiliteLieu.declarer(
            planificateur, lieu, _instant(4, 10), _instant(4, 14), "Recouvrement"
        )

    assert "08:00" in str(info.value)
    assert "12:00" in str(info.value)
    assert "Réfection du sol" in str(info.value)


def test_modifier_le_motif_seul_reussit(planificateur, lieu):
    indisponibilite = ServiceIndisponibiliteLieu.declarer(
        planificateur, lieu, _instant(4, 8), _instant(4, 12), "Réfection du sol"
    )

    ServiceIndisponibiliteLieu.modifier(
        planificateur,
        indisponibilite,
        _instant(4, 8),
        _instant(4, 12),
        "Réfection du sol et peinture",
    )

    indisponibilite.refresh_from_db()
    assert indisponibilite.motif == "Réfection du sol et peinture"


def test_decaler_les_bornes_sans_conflit_reussit(planificateur, lieu):
    indisponibilite = ServiceIndisponibiliteLieu.declarer(
        planificateur, lieu, _instant(4, 8), _instant(4, 12), "Réfection du sol"
    )

    ServiceIndisponibiliteLieu.modifier(
        planificateur, indisponibilite, _instant(4, 9), _instant(4, 13), "Réfection du sol"
    )

    indisponibilite.refresh_from_db()
    assert indisponibilite.debut == _instant(4, 9)
    assert indisponibilite.fin == _instant(4, 13)


def test_modifier_sans_deplacer_les_bornes_reussit(planificateur, lieu):
    """Le piège : la contrainte ne doit pas détecter la période comme son
    propre conflit."""
    indisponibilite = ServiceIndisponibiliteLieu.declarer(
        planificateur, lieu, _instant(4, 8), _instant(4, 12), "Réfection du sol"
    )

    ServiceIndisponibiliteLieu.modifier(
        planificateur, indisponibilite, _instant(4, 8), _instant(4, 12), "Réfection du sol"
    )  # ne lève pas


def test_deplacer_sur_une_periode_existante_est_refuse_en_nommant_la_periode(planificateur, lieu):
    ServiceIndisponibiliteLieu.declarer(
        planificateur, lieu, _instant(4, 8), _instant(4, 12), "Réfection du sol"
    )
    indisponibilite = ServiceIndisponibiliteLieu.declarer(
        planificateur, lieu, _instant(5, 8), _instant(5, 12), "Désinfection"
    )

    with pytest.raises(ErreurValidation) as info:
        ServiceIndisponibiliteLieu.modifier(
            planificateur, indisponibilite, _instant(4, 10), _instant(4, 14), "Désinfection"
        )

    assert "Réfection du sol" in str(info.value)
    indisponibilite.refresh_from_db()
    assert indisponibilite.debut == _instant(5, 8)


def test_deplacer_jusqu_a_etre_contigue_reussit(planificateur, lieu):
    """Cas limite d'US-PLAN-02 : se toucher sans se recouvrir est permis."""
    ServiceIndisponibiliteLieu.declarer(
        planificateur, lieu, _instant(4, 8), _instant(4, 12), "Matinée"
    )
    indisponibilite = ServiceIndisponibiliteLieu.declarer(
        planificateur, lieu, _instant(5, 8), _instant(5, 12), "Après-midi"
    )

    ServiceIndisponibiliteLieu.modifier(
        planificateur, indisponibilite, _instant(4, 12), _instant(4, 16), "Après-midi"
    )  # ne lève pas


def test_modifier_avec_fin_avant_debut_est_refuse(planificateur, lieu):
    indisponibilite = ServiceIndisponibiliteLieu.declarer(
        planificateur, lieu, _instant(4, 8), _instant(4, 12), "Réfection du sol"
    )

    with pytest.raises(ErreurValidation):
        ServiceIndisponibiliteLieu.modifier(
            planificateur, indisponibilite, _instant(4, 12), _instant(4, 8), "Incohérent"
        )


def test_modification_est_journalisee(planificateur, lieu):
    indisponibilite = ServiceIndisponibiliteLieu.declarer(
        planificateur, lieu, _instant(4, 8), _instant(4, 12), "Réfection du sol"
    )

    ServiceIndisponibiliteLieu.modifier(
        planificateur, indisponibilite, _instant(4, 8), _instant(4, 12), "Motif corrigé"
    )

    assert EntreeJournal.objects.filter(
        objet_type="indisponibilite_lieu",
        objet_identifiant=str(indisponibilite.pk),
        type_action=TypeAction.MODIFICATION_ELEMENT_GESTION,
    ).exists()


def test_suppression_d_un_lieu_supprime_ses_indisponibilites(planificateur, lieu):
    ServiceIndisponibiliteLieu.declarer(
        planificateur, lieu, _instant(4, 8), _instant(4, 12), "Réfection du sol"
    )

    lieu.delete()

    assert not IndisponibiliteLieu.objects.exists()


def test_suppression_d_une_indisponibilite_par_le_service(planificateur, lieu):
    """Prompt 16, cause racine n° 3 : `ServiceIndisponibiliteLieu` n'avait
    aucun moyen de supprimer une déclaration erronée — signalé en recette."""
    indisponibilite = ServiceIndisponibiliteLieu.declarer(
        planificateur, lieu, _instant(4, 8), _instant(4, 12), "Réfection du sol"
    )

    ServiceIndisponibiliteLieu.supprimer(planificateur, indisponibilite)

    assert not IndisponibiliteLieu.objects.filter(pk=indisponibilite.pk).exists()


def test_modification_d_une_indisponibilite_reussit_depuis_l_ecran(client, planificateur, lieu):
    indisponibilite = ServiceIndisponibiliteLieu.declarer(
        planificateur, lieu, _instant(4, 8), _instant(4, 12), "Réfection du sol"
    )
    client.force_login(planificateur)

    reponse_get = client.get(
        reverse("ressources:modifier_indisponibilite_lieu", args=[indisponibilite.pk])
    )
    assert reponse_get.status_code == 200

    reponse_post = client.post(
        reverse("ressources:modifier_indisponibilite_lieu", args=[indisponibilite.pk]),
        {"debut": "2027-01-04T08:00", "fin": "2027-01-04T12:00", "motif": "Motif corrigé"},
    )

    assert reponse_post.status_code == 302
    indisponibilite.refresh_from_db()
    assert indisponibilite.motif == "Motif corrigé"


def test_modification_vers_un_chevauchement_est_refusee_depuis_l_ecran(client, planificateur, lieu):
    ServiceIndisponibiliteLieu.declarer(
        planificateur, lieu, _instant(4, 8), _instant(4, 12), "Réfection du sol"
    )
    indisponibilite = ServiceIndisponibiliteLieu.declarer(
        planificateur, lieu, _instant(5, 8), _instant(5, 12), "Désinfection"
    )
    client.force_login(planificateur)

    reponse = client.post(
        reverse("ressources:modifier_indisponibilite_lieu", args=[indisponibilite.pk]),
        {"debut": "2027-01-04T10:00", "fin": "2027-01-04T14:00", "motif": "Désinfection"},
    )

    assert reponse.status_code == 200
    assert "Réfection du sol" in reponse.content.decode()
    indisponibilite.refresh_from_db()
    assert indisponibilite.debut == _instant(5, 8)


def test_suppression_d_une_indisponibilite_reussit_depuis_l_ecran(client, planificateur, lieu):
    indisponibilite = ServiceIndisponibiliteLieu.declarer(
        planificateur, lieu, _instant(4, 8), _instant(4, 12), "Réfection du sol"
    )
    client.force_login(planificateur)

    reponse_get = client.get(
        reverse("ressources:supprimer_indisponibilite_lieu", args=[indisponibilite.pk])
    )
    assert reponse_get.status_code == 200

    reponse_post = client.post(
        reverse("ressources:supprimer_indisponibilite_lieu", args=[indisponibilite.pk])
    )

    assert reponse_post.status_code == 302
    assert not IndisponibiliteLieu.objects.filter(pk=indisponibilite.pk).exists()
