"""Chargement du référentiel de démonstration — Prompt 15, § 3.2 à § 3.7.

Les volumes horaires ne sont jamais écrits en dur : ils se calculent depuis
`VOLUME_HORAIRE_HEBDOMADAIRE_REFERENCE` (§ 4 du prompt), avec un facteur
délibérément excédentaire pour *Spécialisation chiffre* (`facteur_volume`
dans `donnees.py`) — c'est ce facteur, pas un nombre d'heures, qui porte
l'intention du jeu d'essai.
"""

from django.conf import settings

from referentiel.services.formation import ServiceFormation
from referentiel.services.matiere import ServiceMatiere
from referentiel.services.objectif_pedagogique import ServiceObjectifPedagogique
from referentiel.services.prerequis import ServicePrerequis
from referentiel.services.referentiel import ServiceReferentiel
from referentiel.services.type_formation import ServiceTypeFormation
from ressources.jeu_demonstration.donnees import (
    FORMATIONS,
    MATIERE_ARCHIVEE,
    MATIERES,
    OBJECTIFS,
    PREREQUIS_OFFICIERS,
    TYPE_FORMATION_ARCHIVE,
    TYPES_FORMATION,
)

CLE_OFFICIERS = ("Formation initiale", "Officiers")


def charger_types_formation(agissant, stdout):
    types = {
        intitule: ServiceTypeFormation.creer(agissant, {"intitule": intitule})
        for intitule in TYPES_FORMATION
    }
    archive = ServiceTypeFormation.creer(agissant, {"intitule": TYPE_FORMATION_ARCHIVE})
    ServiceTypeFormation.archiver(agissant, archive.pk)
    types[TYPE_FORMATION_ARCHIVE] = archive
    stdout.write(f"  {len(types)} types de formation créés (1 archivé).")
    return types


def charger_matieres(agissant, stdout):
    matieres = {
        intitule: ServiceMatiere.creer(agissant, {"intitule": intitule, "code": ""})
        for intitule in MATIERES
    }
    ServiceMatiere.archiver(agissant, matieres[MATIERE_ARCHIVEE].pk)
    stdout.write(f"  {len(matieres)} matières créées (1 archivée).")
    return matieres


def charger_formations(agissant, types, stdout):
    formations = {}
    for donnees in FORMATIONS:
        formation = ServiceFormation.creer(
            agissant,
            {
                "intitule": donnees.intitule,
                "specialite": donnees.specialite,
                "duree_semaines": donnees.duree_semaines,
                "type_formation": types[donnees.type_formation],
            },
        )
        if donnees.archive:
            formation = ServiceFormation.archiver(agissant, formation.pk)
        formations[_cle_formation(donnees)] = formation
    stdout.write(f"  {len(formations)} formations créées (1 archivée).")
    return formations


def charger_composition(agissant, formations, matieres, stdout):
    """Rattache chaque matière de `donnees.FORMATIONS` à sa formation.
    Retourne les éléments créés, indexés par (formation, matière) : § 3.7 en
    a besoin pour poser les prérequis sur les bons éléments.
    """
    elements = {}
    total = 0
    for donnees in FORMATIONS:
        if donnees.archive or not donnees.composition:
            continue
        formation = formations[_cle_formation(donnees)]
        cle = _cle_formation(donnees)
        for element, volume in _volumes(donnees):
            objet = ServiceReferentiel.rattacher(
                agissant,
                formation,
                matieres[element.matiere],
                {
                    "volume_horaire_prescrit": volume,
                    "categorie_lieu": element.categorie_lieu,
                    "type_lieu_partage": element.type_lieu_partage,
                },
            )
            elements[(cle, element.matiere)] = objet
            total += 1
    stdout.write(f"  {total} éléments de référentiel rattachés.")
    return elements


def charger_objectifs(agissant, matieres, stdout):
    total = 0
    for intitule, libelles in OBJECTIFS.items():
        for libelle in libelles:
            ServiceObjectifPedagogique.ajouter(agissant, matieres[intitule], libelle)
            total += 1
    stdout.write(f"  {total} objectifs pédagogiques ajoutés.")


def charger_prerequis(agissant, formations, elements, stdout):
    formation_officiers = formations[CLE_OFFICIERS]
    total = 0
    for element_intitule, prerequis_intitule in PREREQUIS_OFFICIERS:
        ServicePrerequis.ajouter(
            agissant,
            formation_officiers,
            elements[(CLE_OFFICIERS, element_intitule)],
            elements[(CLE_OFFICIERS, prerequis_intitule)],
        )
        total += 1
    stdout.write(f"  {total} prérequis déclarés (référentiel Officiers).")


def _cle_formation(donnees):
    return (donnees.intitule, donnees.type_formation)


def _volumes(donnees):
    attendu = donnees.duree_semaines * settings.VOLUME_HORAIRE_HEBDOMADAIRE_REFERENCE
    cible = round(attendu * donnees.facteur_volume)
    return zip(donnees.composition, _repartir(cible, len(donnees.composition)), strict=True)


def _repartir(total, nombre):
    """`nombre` parts entières positives dont la somme vaut exactement
    `total` : les premières absorbent le reste de la division euclidienne,
    plutôt qu'un arrondi par part qui dériverait de la cible."""
    base, reste = divmod(total, nombre)
    return [base + 1 if position < reste else base for position in range(nombre)]
