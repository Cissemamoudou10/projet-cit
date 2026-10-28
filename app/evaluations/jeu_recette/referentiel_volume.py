"""Référentiel du jeu volumineux — Prompt 51, Temps 3, § 3.1. Catalogue
d'environ 70 matières, 10 formations (1 archivée), référentiels de 8 à 15
matières (150 à 400 h), prérequis en chaînes de profondeur 2 à 3. Toutes
les données sont fictives, générées à partir du générateur partagé
(`jeu_recette.alea`), jamais une matière ou une formation réelle du CIT.

Comme pour l'état `complet` : tout objet portant une règle (RG-05 à RG-10)
passe par un service, jamais par une création directe."""

from evaluations.jeu_recette.alea import nom_fictif
from evaluations.jeu_recette.donnees_volume import (
    MARGE_VOLUME_REFERENTIEL,
    MATIERES_PAR_REFERENTIEL,
    NOMBRE_FORMATIONS,
    NOMBRE_FORMATIONS_ARCHIVEES,
    NOMBRE_MATIERES_CATALOGUE,
    NOMBRE_TYPES_FORMATION,
    PROFONDEUR_PREREQUIS,
    VOLUME_HORAIRE_REFERENTIEL,
)
from referentiel.models import CategorieLieu, TypeLieuPartage
from referentiel.services.formation import ServiceFormation
from referentiel.services.matiere import ServiceMatiere
from referentiel.services.prerequis import ServicePrerequis
from referentiel.services.referentiel import ServiceReferentiel
from referentiel.services.type_formation import ServiceTypeFormation

SPECIALITE_VOLUME = "Volume"


def charger_types_formation_volume(agissant, stdout):
    types = {}
    for indice in range(1, NOMBRE_TYPES_FORMATION + 1):
        code = f"TFV{indice}"
        types[code] = ServiceTypeFormation.creer(
            agissant, {"intitule": f"{code} — Type de formation volumineux {indice}"}
        )
    stdout.write(f"  {len(types)} types de formation ajoutés.")
    return types


def charger_matieres_volume(agissant, generateur, stdout):
    matieres = {}
    for indice in range(1, NOMBRE_MATIERES_CATALOGUE + 1):
        code = f"MV{indice:03d}"
        matieres[code] = ServiceMatiere.creer(
            agissant, {"intitule": f"{code} — {nom_fictif(generateur, 3)}", "code": code}
        )
    stdout.write(f"  {len(matieres)} matières ajoutées au catalogue.")
    return matieres


def charger_formations_volume(agissant, generateur, types, stdout):
    codes_types = list(types.keys())
    formations = {}
    for indice in range(1, NOMBRE_FORMATIONS + 1):
        code = f"FV{indice:02d}"
        formations[code] = ServiceFormation.creer(
            agissant,
            {
                "intitule": f"{code} — {nom_fictif(generateur, 2)}",
                "specialite": SPECIALITE_VOLUME,
                "duree_semaines": generateur.randint(8, 20),
                "type_formation": types[codes_types[(indice - 1) % len(codes_types)]],
            },
        )
    for code in list(formations)[-NOMBRE_FORMATIONS_ARCHIVEES:]:
        formations[code] = ServiceFormation.archiver(agissant, formations[code].pk)
    stdout.write(f"  {len(formations)} formations ajoutées ({NOMBRE_FORMATIONS_ARCHIVEES} archivée).")
    return formations


def _categorie_et_type_lieu(generateur):
    tirage = generateur.random()
    if tirage < 0.6:
        return CategorieLieu.SALLE_ATTITREE, None
    if tirage < 0.85:
        type_partage = generateur.choice(
            (TypeLieuPartage.AMPHITHEATRE, TypeLieuPartage.LABORATOIRE, TypeLieuPartage.SALLE_SPECIALISEE)
        )
        return CategorieLieu.LIEU_PARTAGE, type_partage
    return CategorieLieu.AUCUN_LIEU, None


def _repartir_volume(generateur, volume_total, nombre):
    """`nombre` parts entières positives, dont la somme vaut `volume_total` —
    poids aléatoires normalisés, le dernier élément absorbe l'arrondi.

    Correctif du 27/10/2026 : poids resserrés (0,9 à 1,1, contre 0,2 à 1,2
    avant) — un écart de ×6 entre la plus grande et la plus petite part
    pouvait réduire une matière à ≈20 h quand le total visait 900-1000 h
    (cible dimensionnée sur la durée de la session, voir
    `organisation_volume.volumes_cibles_par_formation`), l'épuisant en
    quelques semaines de génération alors que le référentiel ENTIER restait
    loin d'être consommé — observé réellement sur un chargement pleine
    échelle (RG-39 dominant les cases non pourvues de W+1)."""
    poids = [generateur.random() * 0.2 + 0.9 for _ in range(nombre)]
    somme_poids = sum(poids)
    volumes = [max(1, round(volume_total * p / somme_poids)) for p in poids[:-1]]
    volumes.append(max(1, volume_total - sum(volumes)))
    return volumes


def _poids_formatif_et_certificatif(generateur):
    """RG-08 bis (contrainte de base) : jamais les deux à zéro."""
    poids_formatif = generateur.randint(0, 2)
    poids_certificatif = generateur.randint(0, 2)
    if poids_formatif == 0 and poids_certificatif == 0:
        poids_certificatif = 1
    return poids_formatif, poids_certificatif


def _rattacher_un_element(agissant, generateur, formation, matiere, volume):
    categorie, type_partage = _categorie_et_type_lieu(generateur)
    poids_formatif, poids_certificatif = _poids_formatif_et_certificatif(generateur)
    return ServiceReferentiel.rattacher(
        agissant,
        formation,
        matiere,
        {
            "volume_horaire_prescrit": volume,
            "categorie_lieu": categorie,
            "type_lieu_partage": type_partage,
            "coefficient": generateur.randint(1, 3),
            "poids_formatif": poids_formatif,
            "poids_certificatif": poids_certificatif,
        },
    )


def _poser_prerequis_chaine(agissant, formation, elements_formation, generateur):
    """Chaînes de profondeur 2 à 3 (§ 3.1) : chaque élément ne pointe que
    vers un élément plus ancien dans l'ordre de composition — acyclique par
    construction, jamais besoin de le vérifier après coup."""
    profondeur_max = generateur.randint(*PROFONDEUR_PREREQUIS)
    total = 0
    for indice, element in enumerate(elements_formation):
        if indice == 0 or generateur.random() >= 0.35:
            continue
        borne_basse = max(0, indice - profondeur_max)
        element_prerequis = elements_formation[generateur.randint(borne_basse, indice - 1)]
        ServicePrerequis.ajouter(agissant, formation, element, element_prerequis)
        total += 1
    return total


def combiner_formations_et_cibles(formations, volumes_cibles):
    """Fusionne les deux dicts en un seul — `.claude/rules/python.md`, § 5
    paramètres max : `charger_composition_volume` resterait à 6 sinon."""
    return {code: (formation, volumes_cibles.get(code)) for code, formation in formations.items()}


def _volume_total_referentiel(generateur, cible):
    """Plancher par semaine de session active (`cible`, posé par
    `organisation_volume.volumes_cibles_par_formation`, correctif du
    27/10/2026) si une session active porte cette formation — sinon
    l'ancien tirage fixe, pour les formations sans session active
    (terminées seulement, ou archivée)."""
    if cible is None:
        return generateur.randint(*VOLUME_HORAIRE_REFERENTIEL)
    return round(cible * generateur.uniform(*MARGE_VOLUME_REFERENTIEL))


def charger_composition_volume(agissant, generateur, formations_avec_cible, matieres, stdout):
    codes_matieres = list(matieres.keys())
    elements = {}
    total_prerequis = 0
    for code_formation, (formation, cible) in formations_avec_cible.items():
        nombre = generateur.randint(*MATIERES_PAR_REFERENTIEL)
        codes_choisis = generateur.sample(codes_matieres, nombre)
        volume_total = _volume_total_referentiel(generateur, cible)
        volumes = _repartir_volume(generateur, volume_total, nombre)
        elements_formation = [
            _rattacher_un_element(agissant, generateur, formation, matieres[code], volume)
            for code, volume in zip(codes_choisis, volumes)
        ]
        for code, element in zip(codes_choisis, elements_formation):
            elements[(code_formation, code)] = element
        total_prerequis += _poser_prerequis_chaine(agissant, formation, elements_formation, generateur)
    stdout.write(
        f"  {len(elements)} éléments de référentiel rattachés, {total_prerequis} prérequis déclarés."
    )
    return elements
