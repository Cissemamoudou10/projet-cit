"""Chargement, UNE FOIS par génération, de ce que la stratégie et la
construction des candidates ont besoin de connaître, au-delà de `Contexte`
(propre à `ServiceContraintes`) — I3, § 10, Prompt 31 : borné, indépendant
du nombre de cases.
"""

import dataclasses

from planification.generation.candidats import matieres_programmables
from referentiel.models import ElementReferentiel
from ressources.models import CategorieLieu as CategorieLieuRessource
from ressources.models import Instructeur, Lieu


@dataclasses.dataclass(frozen=True)
class Preparation:
    matieres_par_brigade: dict
    matieres_ecartees: list
    instructeurs_qualifies: dict
    lieux_partages_par_type: dict


def _elements_par_formation(brigades):
    formation_ids = {brigade.session.formation_id for brigade in brigades}
    elements = ElementReferentiel.objects.filter(formation_id__in=formation_ids).select_related(
        "matiere"
    )
    resultat = {}
    for element in elements:
        resultat.setdefault(element.formation_id, []).append(element)
    return resultat


def _matieres_et_ecartees(brigades, contexte):
    par_formation = _elements_par_formation(brigades)
    matieres_par_brigade, ecartees = {}, []
    for brigade in brigades:
        elements = par_formation.get(brigade.session.formation_id, [])
        programmables, ecartees_brigade = matieres_programmables(brigade, elements, contexte)
        matieres_par_brigade[brigade.pk] = programmables
        ecartees += ecartees_brigade
    return matieres_par_brigade, ecartees


def _instructeurs_qualifies(contexte):
    """`contexte.qualifications` (RG-35) : des identifiants seulement — la
    stratégie a besoin des objets pour construire les `Candidate`, une seule
    requête ici plutôt qu'une par instructeur qualifié."""
    instructeurs = {i.pk: i for i in Instructeur.objects.filter(archive=False)}
    resultat = {}
    for instructeur_id, matiere_id in contexte.qualifications:
        instructeur = instructeurs.get(instructeur_id)
        if instructeur is not None:
            resultat.setdefault(matiere_id, []).append(instructeur)
    return resultat


def _lieux_partages_par_type():
    lieux = Lieu.objects.filter(categorie=CategorieLieuRessource.LIEU_PARTAGE, archive=False)
    resultat = {}
    for lieu in lieux:
        resultat.setdefault(lieu.type_partage, []).append(lieu)
    return resultat


def preparer(brigades, contexte):
    matieres_par_brigade, ecartees = _matieres_et_ecartees(brigades, contexte)
    return Preparation(
        matieres_par_brigade=matieres_par_brigade,
        matieres_ecartees=ecartees,
        instructeurs_qualifies=_instructeurs_qualifies(contexte),
        lieux_partages_par_type=_lieux_partages_par_type(),
    )
