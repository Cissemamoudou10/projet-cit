"""US-VAL-03, groupe B — contraintes en base (ETA-01 § 4.3).

Un test par contrainte, chacun par écriture directe (`update`) qui attend
`IntegrityError`. Chaque cas ne viole QUE la contrainte nommée : les autres
faits sont cohérents, sans quoi le test ne prouverait rien. Le nom est vérifié
dans le message d'erreur PostgreSQL.
"""

import datetime

import pytest
from django.db import IntegrityError
from django.utils import timezone

from planification.models import EtatProgramme, ProgrammeHebdomadaire

MAINTENANT = timezone.now()


def _ecrire_directement(programme, nom_contrainte, **champs):
    with pytest.raises(IntegrityError, match=nom_contrainte):
        ProgrammeHebdomadaire.objects.filter(pk=programme.pk).update(**champs)


def _faits_valides(pedagogique):
    """Faits d'un programme validé et cohérent : ce que le circuit écrirait."""
    return {
        "date_soumission": MAINTENANT - datetime.timedelta(days=4),
        "date_validation": MAINTENANT - datetime.timedelta(days=3),
        "valide_par": pedagogique,
    }


def test_ck_programme_etat_refuse_un_etat_inconnu(programme):
    _ecrire_directement(programme, "ck_programme_etat", etat="inconnu")


def test_ck_programme_rejet_motive_refuse_un_rejet_sans_motif(programme):
    _ecrire_directement(
        programme,
        "ck_programme_rejet_motive",
        etat=EtatProgramme.REJETE,
        date_soumission=MAINTENANT,
        motif_rejet="   ",
    )


def test_ck_programme_rejet_motive_refuse_un_rejet_sans_motif_nul(programme):
    """Un motif NULL donne NULL à la condition, que le CHECK accepterait :
    la contrainte doit aussi nommer le cas NULL."""
    _ecrire_directement(
        programme,
        "ck_programme_rejet_motive",
        etat=EtatProgramme.REJETE,
        date_soumission=MAINTENANT,
        motif_rejet=None,
    )


def test_ck_programme_motif_hors_circuit_refuse_un_motif_sur_un_soumis(programme):
    _ecrire_directement(
        programme,
        "ck_programme_motif_hors_circuit",
        etat=EtatProgramme.SOUMIS,
        date_soumission=MAINTENANT,
        motif_rejet="Motif resté d'un rejet antérieur.",
    )


def test_ck_programme_soumission_datee_refuse_un_soumis_sans_date(programme):
    _ecrire_directement(programme, "ck_programme_soumission_datee", etat=EtatProgramme.SOUMIS)


def test_ck_programme_validation_nominative_refuse_un_valide_sans_validateur(programme, redacteur):
    faits = _faits_valides(redacteur)
    faits["valide_par"] = None
    _ecrire_directement(
        programme,
        "ck_programme_validation_nominative",
        etat=EtatProgramme.VALIDE,
        **faits,
    )


def test_ck_programme_signature_complete_refuse_une_date_sans_signataire(programme, redacteur):
    _ecrire_directement(
        programme,
        "ck_programme_signature_complete",
        etat=EtatProgramme.VALIDE,
        date_signature=timezone.localdate(),
        signataire=None,
        **_faits_valides(redacteur),
    )


def test_ck_programme_signature_sur_validation_refuse_une_signature_anterieure(
    programme, redacteur
):
    faits = _faits_valides(redacteur)
    date_signature = faits["date_validation"].date() - datetime.timedelta(days=1)
    _ecrire_directement(
        programme,
        "ck_programme_signature_sur_validation",
        etat=EtatProgramme.VALIDE,
        date_signature=date_signature,
        signataire="Signataire fictif",
        **faits,
    )


def test_ck_programme_affichage_signe_refuse_un_affiche_sans_date_d_affichage(programme, redacteur):
    _ecrire_directement(
        programme,
        "ck_programme_affichage_signe",
        etat=EtatProgramme.AFFICHE,
        date_signature=timezone.localdate(),
        signataire="Signataire fictif",
        date_affichage=None,
        **_faits_valides(redacteur),
    )
