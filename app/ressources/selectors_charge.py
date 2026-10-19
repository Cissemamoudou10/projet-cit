"""Charge d'enseignement d'un instructeur — US-INS-04, BF-INS-04 (prompt 48).

C1 : l'enseignement (`ResolveurHeuresEnseignementParInstructeur`, fourni par
`planification`) et la surveillance d'épreuve (`ResolveurOccupationsEpreuves`,
fourni par `evaluations`) sont deux colonnes distinctes — la surveillance ne
s'additionne jamais à la charge d'enseignement, qui seule compare au seuil.
`ressources` ne peut importer ni `planification` ni `evaluations` (sens de
dépendance interdit) : les deux passent par un résolveur.
"""

import dataclasses
import datetime

from django.conf import settings

from noyau.services.parametres import (
    ResolveurHeuresEnseignementParInstructeur,
    ResolveurOccupationsEpreuves,
)
from ressources.models import Instructeur


@dataclasses.dataclass(frozen=True)
class LigneChargeInstructeur:
    """Jamais stockée (`.claude/rules/modeles.md`) : recalculée à chaque
    consultation, pour la période choisie."""

    instructeur: object
    heures_enseignement: float
    heures_surveillance: float
    par_matiere: list
    moyenne_hebdomadaire: float
    seuil_franchi: bool


def seuil_charge_hebdomadaire() -> float:
    return float(settings.SEUIL_CHARGE_HEBDOMADAIRE_INSTRUCTEUR)


def _heures_surveillance_par_instructeur(debut, fin):
    """Surveillance d'épreuve, hors charge d'enseignement (C1) — une seule
    requête (`ResolveurOccupationsEpreuves`, « trois requêtes au plus, quel
    que soit le nombre d'épreuves »), jamais une par instructeur."""
    totaux: dict = {}
    for occupation in ResolveurOccupationsEpreuves.resoudre(debut, fin):
        duree = (occupation["fin"] - occupation["debut"]) / datetime.timedelta(hours=1)
        for instructeur_id in occupation["instructeurs"]:
            totaux[instructeur_id] = totaux.get(instructeur_id, 0.0) + duree
    return totaux


def _ligne_de_instructeur(instructeur, detail, heures_surveillance, nb_semaines, seuil):
    total_enseignement = sum(ligne["heures"] for ligne in detail)
    moyenne = total_enseignement / nb_semaines
    return LigneChargeInstructeur(
        instructeur=instructeur,
        heures_enseignement=total_enseignement,
        heures_surveillance=heures_surveillance,
        par_matiere=detail,
        moyenne_hebdomadaire=moyenne,
        seuil_franchi=moyenne > seuil,
    )


def charge_instructeurs(debut, fin) -> list:
    """C3 : tous les instructeurs NON ARCHIVÉS, triables par charge sur la
    période `[debut, fin)` (instants) — même ordre que par moyenne
    hebdomadaire, `nb_semaines` étant constant pour tous sur une même
    période. Trois requêtes au plus (enseignement, surveillance,
    instructeurs), jamais une par instructeur."""
    seuil = seuil_charge_hebdomadaire()
    nb_semaines = max((fin - debut) / datetime.timedelta(weeks=1), 1e-9)
    heures_par_instructeur = ResolveurHeuresEnseignementParInstructeur.resoudre(debut, fin)
    heures_surveillance = _heures_surveillance_par_instructeur(debut, fin)
    instructeurs = Instructeur.objects.filter(archive=False).order_by("nom", "prenom")
    return [
        _ligne_de_instructeur(
            instructeur,
            heures_par_instructeur.get(instructeur.pk, []),
            heures_surveillance.get(instructeur.pk, 0.0),
            nb_semaines,
            seuil,
        )
        for instructeur in instructeurs
    ]


def charge_d_un_instructeur(instructeur, debut, fin) -> LigneChargeInstructeur:
    """C3, détail par matière : même calcul que `charge_instructeurs`, pour
    un seul instructeur — réutilise les mêmes résolveurs, jamais un second
    calcul."""
    seuil = seuil_charge_hebdomadaire()
    nb_semaines = max((fin - debut) / datetime.timedelta(weeks=1), 1e-9)
    detail = ResolveurHeuresEnseignementParInstructeur.resoudre(debut, fin).get(instructeur.pk, [])
    heures_surveillance = _heures_surveillance_par_instructeur(debut, fin).get(instructeur.pk, 0.0)
    return _ligne_de_instructeur(instructeur, detail, heures_surveillance, nb_semaines, seuil)
