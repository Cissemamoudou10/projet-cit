"""Rapprochement prescrit/programmé/réalisé — US-SUI-01 (prompt 44, Temps 3).

R7 : le nombre de requêtes ne dépend ni du nombre de brigades ni du nombre
de matières — cinq requêtes au total (brigades, éléments de référentiel,
programmé, réalisé, brigades avec programme affiché), jamais une par ligne
du tableau produit.
"""

import dataclasses

from django.utils import timezone

from organisation.models import Brigade, Session
from planification.models import EtatProgramme, LigneProgramme
from planification.services.contraintes import (
    volumes_programmes_par_element_brigade,
    volumes_realises_par_element_brigade,
)
from referentiel.models import ElementReferentiel, Formation


@dataclasses.dataclass(frozen=True)
class LigneRapprochement:
    """C1, C3 : trois volumes et l'écart, jamais stockés — recalculés à
    chaque consultation (`.claude/rules/modeles.md`)."""

    element_referentiel: object
    prescrit: float
    programme: float
    realise: float

    @property
    def ecart_heures(self):
        return self.prescrit - self.realise

    @property
    def ecart_pourcent(self):
        if not self.prescrit:
            return 0.0
        return self.ecart_heures / self.prescrit * 100


@dataclasses.dataclass(frozen=True)
class GroupeRapprochement:
    """Une brigade et ses lignes — unité de pagination (§ 20 éléments,
    `.claude/rules/vues.md`) : jamais une ligne isolée d'une brigade sur une
    page, le reste sur la suivante."""

    brigade: object
    lignes: list = dataclasses.field(default_factory=list)
    sans_programme_affiche: bool = False


def formations_pour_filtre():
    return list(Formation.objects.filter(archive=False).order_by("intitule"))


def sessions_pour_filtre():
    return list(Session.objects.select_related("formation").order_by("intitule"))


def _brigades_filtrees(formation_id, session_id, brigade_id):
    brigades = Brigade.objects.select_related("session__formation")
    if brigade_id:
        return brigades.filter(pk=brigade_id)
    if session_id:
        return brigades.filter(session_id=session_id)
    if formation_id:
        return brigades.filter(session__formation_id=formation_id)
    return brigades


def _brigades_avec_programme_affiche(brigade_ids, a_la_date):
    return set(
        LigneProgramme.objects.filter(
            brigade_id__in=brigade_ids,
            seance__programme__etat=EtatProgramme.AFFICHE,
            seance__fin__lte=a_la_date,
        )
        .values_list("brigade_id", flat=True)
        .distinct()
    )


def rapprochement(formation_id=None, session_id=None, brigade_id=None, periode_fin=None):
    """R1 : `periode_fin` donne T pour le réalisé (fin de la période
    filtrée), sinon maintenant. R4 : le programmé n'est pas borné par la
    période (toutes les séances, tous états, voir `.claude/rules/
    services.md`). R5/E1 : une brigade sans aucun programme affiché à T
    porte `sans_programme_affiche=True`, jamais de lignes à réalisé nul.
    Rend une liste de `GroupeRapprochement`, une entrée par brigade — unité
    de pagination côté vue."""
    a_la_date = periode_fin or timezone.now()
    brigades = list(_brigades_filtrees(formation_id, session_id, brigade_id))
    brigade_ids = [brigade.pk for brigade in brigades]
    formation_ids = {brigade.session.formation_id for brigade in brigades}
    elements_par_formation: dict = {}
    for element in ElementReferentiel.objects.filter(formation_id__in=formation_ids).select_related(
        "matiere"
    ):
        elements_par_formation.setdefault(element.formation_id, []).append(element)
    programme_par_cle = volumes_programmes_par_element_brigade(brigade_ids=brigade_ids)
    realise_par_cle = volumes_realises_par_element_brigade(a_la_date, brigade_ids=brigade_ids)
    brigades_affichees = _brigades_avec_programme_affiche(brigade_ids, a_la_date)

    groupes = []
    for brigade in brigades:
        if brigade.pk not in brigades_affichees:
            groupes.append(GroupeRapprochement(brigade=brigade, sans_programme_affiche=True))
            continue
        lignes_brigade = [
            LigneRapprochement(
                element_referentiel=element,
                prescrit=element.volume_horaire_prescrit,
                programme=programme_par_cle.get((element.pk, brigade.pk), 0),
                realise=realise_par_cle.get((element.pk, brigade.pk), 0),
            )
            for element in elements_par_formation.get(brigade.session.formation_id, [])
        ]
        groupes.append(GroupeRapprochement(brigade=brigade, lignes=lignes_brigade))
    return groupes
