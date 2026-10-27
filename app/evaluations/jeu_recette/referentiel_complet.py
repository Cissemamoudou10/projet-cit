"""Référentiel ajouté par l'état `complet` — Prompt 51, § 2.1.

Patron identique à `referentiel.py` (jeu `socle`), qui ne change pas : les
fonctions d'ici créent uniquement les objets NOUVEAUX (matières M6-M9,
formation F6, son référentiel, son prérequis, ses objectifs pédagogiques).
"""

from evaluations.jeu_recette.donnees import (
    DUREE_SEMAINES_PAR_DEFAUT,
    SPECIALITE_PAR_DEFAUT,
)
from evaluations.jeu_recette.donnees import (
    MATIERES as MATIERES_SOCLE,
)
from evaluations.jeu_recette.donnees_complet import (
    CODE_FORMATION_F6,
    COMPOSITION_F6,
    LIBELLE_FORMATION_F6,
    MATIERES_COMPLET,
    OBJECTIFS_PEDAGOGIQUES_M6,
    PREREQUIS_COMPLET,
    TYPE_LIEU_PARTAGE_M7,
)
from referentiel.models import CategorieLieu
from referentiel.services.formation import ServiceFormation
from referentiel.services.matiere import ServiceMatiere
from referentiel.services.objectif_pedagogique import ServiceObjectifPedagogique
from referentiel.services.prerequis import ServicePrerequis
from referentiel.services.referentiel import ServiceReferentiel

CATEGORIES_PAR_MATIERE = {
    **{code: categorie for code, (_, categorie) in MATIERES_SOCLE.items()},
    **{code: categorie for code, (_, categorie) in MATIERES_COMPLET.items()},
}


def charger_matieres_complet(agissant, stdout):
    matieres = {
        code: ServiceMatiere.creer(agissant, {"intitule": intitule, "code": code})
        for code, (intitule, _categorie) in MATIERES_COMPLET.items()
    }
    stdout.write(f"  {len(matieres)} matières ajoutées (M6-M9).")
    return matieres


def charger_formation_f6(agissant, types, stdout):
    formation = ServiceFormation.creer(
        agissant,
        {
            "intitule": LIBELLE_FORMATION_F6,
            "specialite": SPECIALITE_PAR_DEFAUT,
            "duree_semaines": DUREE_SEMAINES_PAR_DEFAUT,
            "type_formation": types["TF1"],
        },
    )
    stdout.write(f"  Formation {CODE_FORMATION_F6} créée.")
    return formation


def charger_composition_f6(agissant, formation, matieres_socle, matieres_complet, stdout):
    """`matieres_socle` : M1/M2/M3 (déjà chargées par l'état `socle`) ;
    `matieres_complet` : M6-M9 (ci-dessus). F6 compose les deux catalogues
    (§ 2.1). Retourne les éléments créés, indexés par code de matière."""
    toutes_matieres = {**matieres_socle, **matieres_complet}
    elements = {}
    for donnees in COMPOSITION_F6:
        categorie = CATEGORIES_PAR_MATIERE[donnees.code_matiere]
        type_lieu_partage = (
            TYPE_LIEU_PARTAGE_M7 if categorie == CategorieLieu.LIEU_PARTAGE else None
        )
        elements[donnees.code_matiere] = ServiceReferentiel.rattacher(
            agissant,
            formation,
            toutes_matieres[donnees.code_matiere],
            {
                "volume_horaire_prescrit": donnees.volume_horaire,
                "categorie_lieu": categorie,
                "type_lieu_partage": type_lieu_partage,
                "coefficient": donnees.coefficient,
                "poids_formatif": donnees.poids_formatif,
                "poids_certificatif": donnees.poids_certificatif,
            },
        )
    stdout.write(f"  {len(elements)} éléments de référentiel rattachés à F6 (200 h).")
    return elements


def charger_prerequis_f6(agissant, formation, elements_f6, stdout):
    for _, code_element, code_prerequis in PREREQUIS_COMPLET:
        ServicePrerequis.ajouter(
            agissant, formation, elements_f6[code_element], elements_f6[code_prerequis]
        )
    stdout.write(f"  {len(PREREQUIS_COMPLET)} prérequis déclarés sur F6.")


def charger_objectifs_m6(agissant, matieres_complet, stdout):
    matiere_m6 = matieres_complet["M6"]
    for libelle in OBJECTIFS_PEDAGOGIQUES_M6:
        ServiceObjectifPedagogique.ajouter(agissant, matiere_m6, libelle)
    stdout.write(f"  {len(OBJECTIFS_PEDAGOGIQUES_M6)} objectifs pédagogiques ajoutés sur M6.")
