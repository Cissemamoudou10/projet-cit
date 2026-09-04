"""US-PLAN-02 — Indisponibilités de lieu, § 3.1 du Prompt 14. Contrainte
d'exclusion `ex_indispo_lieu_chevauchement`, premier usage réel de
`btree_gist` au socle.
"""

import datetime

import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone

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


def test_suppression_d_un_lieu_supprime_ses_indisponibilites(planificateur, lieu):
    ServiceIndisponibiliteLieu.declarer(
        planificateur, lieu, _instant(4, 8), _instant(4, 12), "Réfection du sol"
    )

    lieu.delete()

    assert not IndisponibiliteLieu.objects.exists()
