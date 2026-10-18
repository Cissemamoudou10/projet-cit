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


def historique_du_programme(programme):
    """US-VAL-05, H1 : toutes les transitions du programme (génération,
    soumission, retrait, validation, rejet, reprise, signature, affichage,
    annulation de validation), dans l'ordre CHRONOLOGIQUE — le journal porte
    déjà l'auteur, la date et le motif de chacune (le moteur les y écrit,
    `services/circuit.py::_journaliser`) : aucune table d'historique
    nouvelle. Une seule requête, quel que soit le nombre de transitions.

    N'inclut PAS l'avenant (trouvé en relecture) : `garde_modification`
    (`services/circuit.py`, branche `avenant=True`) valide la transition
    `PORTER_AVENANT` mais n'appelle jamais `_appliquer` — aucune entrée n'est
    donc écrite sous `objet_type="programme"` pour un avenant, qui se
    consulte au niveau de la séance (`Avenant`, section « Circuit du
    programme » de la consultation), pas ici."""
    return _entrees_du_programme(programme).select_related("auteur").order_by("cree_le", "pk")


def programmes_filtres(etat=None, periode_debut=None, periode_fin=None):
    """US-VAL-05, H2 : toutes les semaines (pas seulement celles en attente,
    à la différence de `programmes_en_attente`), filtrables par état et par
    période — une seule requête, paginée côté vue. `select_related
    ("valide_par")` : `liste_programmes.html` l'affiche pour un programme
    validé, sans quoi chaque ligne validée déclencherait sa propre requête
    (trouvé en relecture, vérifié en conditions réelles)."""
    programmes = ProgrammeHebdomadaire.objects.select_related("valide_par").order_by(
        "-lundi_de_semaine"
    )
    if etat:
        programmes = programmes.filter(etat=etat)
    if periode_debut:
        programmes = programmes.filter(lundi_de_semaine__gte=periode_debut)
    if periode_fin:
        programmes = programmes.filter(lundi_de_semaine__lte=periode_fin)
    return programmes


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
