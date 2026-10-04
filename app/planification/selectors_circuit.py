"""Lectures du circuit du programme pour les écrans (US-VAL-01 à US-VAL-04).

Chaque liste se lit en une requête, quel que soit le nombre de programmes :
la page d'attente et son compteur doivent rester bornés (prompt 40, US-VAL-01).
Le motif de rejet et l'auteur d'une soumission ne sont pas stockés sur le
programme : ils se lisent dans le journal, où le moteur les écrit déjà.
"""

from administration.models import EntreeJournal, TypeAction
from planification.models import EtatProgramme, ProgrammeHebdomadaire

OBJET_TYPE = "programme"
DETAIL_SOUMISSION = "T2"
SEPARATEUR_DETAIL = " — "


def programmes_en_attente():
    return ProgrammeHebdomadaire.objects.filter(etat=EtatProgramme.SOUMIS).order_by(
        "lundi_de_semaine"
    )


def compte_en_attente():
    return programmes_en_attente().count()


def auteurs_des_soumissions(programmes):
    """{pk du programme : auteur de sa dernière soumission}. Une seule requête,
    jamais une par programme."""
    identifiants = [str(programme.pk) for programme in programmes]
    if not identifiants:
        return {}
    entrees = (
        EntreeJournal.objects.filter(
            objet_type=OBJET_TYPE,
            objet_identifiant__in=identifiants,
            type_action=TypeAction.TRANSITION_PROGRAMME,
            detail=DETAIL_SOUMISSION,
        )
        .select_related("auteur")
        .order_by("pk")
    )
    return {int(entree.objet_identifiant): entree.auteur for entree in entrees}


def _entrees_du_programme(programme, **filtres):
    return EntreeJournal.objects.filter(
        objet_type=OBJET_TYPE, objet_identifiant=str(programme.pk), **filtres
    )


def motif_rejet_visible(programme):
    """Motif à montrer à la planification (CU-P5-03, US-VAL-02 c.4).

    Rejeté : le motif du programme. Repris en correction (BROUILLON) : le
    motif du dernier rejet, tant qu'aucune nouvelle soumission ne l'a remplacé.
    Le moteur efface le champ au retour à BROUILLON (D-227) ; la trace reste
    dans le journal, lue ici, sans rien changer au moteur.
    """
    if programme.etat == EtatProgramme.REJETE:
        return programme.motif_rejet
    if programme.etat != EtatProgramme.BROUILLON:
        return None
    dernier_rejet = (
        _entrees_du_programme(programme, type_action=TypeAction.REJET_PROGRAMME)
        .order_by("-pk")
        .first()
    )
    if dernier_rejet is None:
        return None
    soumis_depuis = _entrees_du_programme(
        programme,
        type_action=TypeAction.TRANSITION_PROGRAMME,
        detail=DETAIL_SOUMISSION,
        pk__gt=dernier_rejet.pk,
    ).exists()
    if soumis_depuis:
        return None
    return dernier_rejet.detail.partition(SEPARATEUR_DETAIL)[2] or None
