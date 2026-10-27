"""Chargement du référentiel de recette — Prompt 34, § 2. Volumes horaires
EXPLICITES (20 h, 10 h…) : contrairement au jeu de démonstration, le § 2 du
cahier les fixe lui-même, ils ne se calculent pas depuis un réglage.
"""

from evaluations.jeu_recette.donnees import (
    DUREE_SEMAINES_PAR_DEFAUT,
    FORMATIONS,
    MATIERES,
    PREREQUIS,
    SPECIALITE_PAR_DEFAUT,
    TYPE_LIEU_PARTAGE_M2,
    TYPES_FORMATION,
)
from referentiel.models import CategorieLieu
from referentiel.services.formation import ServiceFormation
from referentiel.services.matiere import ServiceMatiere
from referentiel.services.prerequis import ServicePrerequis
from referentiel.services.referentiel import ServiceReferentiel
from referentiel.services.type_formation import ServiceTypeFormation


def charger_types_formation(agissant, stdout):
    types = {
        code: ServiceTypeFormation.creer(agissant, {"intitule": intitule})
        for code, intitule in TYPES_FORMATION.items()
    }
    stdout.write(f"  {len(types)} types de formation créés.")
    return types


def charger_matieres(agissant, stdout):
    matieres = {
        code: ServiceMatiere.creer(agissant, {"intitule": intitule, "code": code})
        for code, (intitule, _categorie) in MATIERES.items()
    }
    stdout.write(f"  {len(matieres)} matières créées.")
    return matieres


def charger_formations(agissant, types, stdout):
    formations = {}
    for donnees in FORMATIONS:
        formation = ServiceFormation.creer(
            agissant,
            {
                "intitule": donnees.libelle,
                "specialite": SPECIALITE_PAR_DEFAUT,
                "duree_semaines": DUREE_SEMAINES_PAR_DEFAUT,
                "type_formation": types[donnees.type_formation],
            },
        )
        if donnees.archive:
            formation = ServiceFormation.archiver(agissant, formation.pk)
        formations[donnees.code] = formation
    nb_archivees = sum(1 for donnees in FORMATIONS if donnees.archive)
    stdout.write(f"  {len(formations)} formations créées ({nb_archivees} archivée).")
    return formations


def charger_composition(agissant, formations, matieres, stdout):
    """Retourne les éléments créés, indexés par (code_formation,
    code_matiere) — § 2 en a besoin pour poser le prérequis M4→M5 sur les
    bons éléments de F2."""
    elements = {}
    for donnees in FORMATIONS:
        formation = formations[donnees.code]
        for code_matiere, volume in donnees.composition:
            _, categorie = MATIERES[code_matiere]
            type_lieu_partage = (
                TYPE_LIEU_PARTAGE_M2 if categorie == CategorieLieu.LIEU_PARTAGE else None
            )
            objet = ServiceReferentiel.rattacher(
                agissant,
                formation,
                matieres[code_matiere],
                {
                    "volume_horaire_prescrit": volume,
                    "categorie_lieu": categorie,
                    "type_lieu_partage": type_lieu_partage,
                },
            )
            elements[(donnees.code, code_matiere)] = objet
    stdout.write(f"  {len(elements)} éléments de référentiel rattachés.")
    return elements


def charger_prerequis(agissant, formations, elements, stdout):
    for code_formation, code_element, code_prerequis in PREREQUIS:
        ServicePrerequis.ajouter(
            agissant,
            formations[code_formation],
            elements[(code_formation, code_element)],
            elements[(code_formation, code_prerequis)],
        )
    stdout.write(f"  {len(PREREQUIS)} prérequis déclarés.")
