"""Chargement du référentiel de la démonstration J2 — une formation, deux
matières : M1 sans lieu (programme hebdomadaire), M2 en salle attitrée
(contrôle, examen final) — voir `donnees.py` pour pourquoi M2 n'est jamais
AUCUN_LIEU."""

from planification.jeu_demonstration_j2.donnees import (
    DUREE_SEMAINES,
    FORMATION,
    MATIERE_EXAMENS,
    MATIERE_PROGRAMME,
    SPECIALITE,
    TYPE_FORMATION,
)
from referentiel.models import CategorieLieu
from referentiel.services.formation import ServiceFormation
from referentiel.services.matiere import ServiceMatiere
from referentiel.services.referentiel import ServiceReferentiel
from referentiel.services.type_formation import ServiceTypeFormation


def charger_referentiel(agissant, stdout):
    """Rend `(formation, element_programme, element_examens)`."""
    type_formation = ServiceTypeFormation.creer(agissant, {"intitule": TYPE_FORMATION})
    formation = ServiceFormation.creer(
        agissant,
        {
            "intitule": FORMATION,
            "specialite": SPECIALITE,
            "duree_semaines": DUREE_SEMAINES,
            "type_formation": type_formation,
        },
    )
    element_programme = _rattacher(agissant, formation, MATIERE_PROGRAMME, CategorieLieu.AUCUN_LIEU)
    element_examens = _rattacher(agissant, formation, MATIERE_EXAMENS, CategorieLieu.SALLE_ATTITREE)
    stdout.write(f"  Référentiel : « {formation} », deux matières rattachées.")
    return formation, element_programme, element_examens


def _rattacher(agissant, formation, donnees_matiere, categorie_lieu):
    intitule, code, volume = donnees_matiere
    matiere = ServiceMatiere.creer(agissant, {"intitule": intitule, "code": code})
    return ServiceReferentiel.rattacher(
        agissant,
        formation,
        matiere,
        {"volume_horaire_prescrit": volume, "categorie_lieu": categorie_lieu},
    )
