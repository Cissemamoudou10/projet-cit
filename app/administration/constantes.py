"""Valeurs de domaine de l'application `administration`."""

from administration.models import Profil

GROUPES = [
    "Administrateur",
    "Cellule pédagogique",
    "Cellule planification",
    "Cellule examens",
    "Direction de formation",
]

# RG-02 bis : les droits reposent sur les groupes Django, jamais sur `profil`
# directement — mais un compte doit être rattaché au groupe correspondant à
# son profil pour que RG-02 bis soit autre chose qu'un champ d'affichage.
# Voir `administration.services.comptes.ServiceCompte` pour l'usage.
PROFIL_VERS_GROUPE = {
    Profil.ADMINISTRATEUR: "Administrateur",
    Profil.CELLULE_PEDAGOGIQUE: "Cellule pédagogique",
    Profil.CELLULE_PLANIFICATION: "Cellule planification",
    Profil.CELLULE_EXAMENS: "Cellule examens",
    Profil.DIRECTION_FORMATION: "Direction de formation",
}

# § 11.2 du dossier des cas d'utilisation — neuf domaines, deux niveaux
# chacun. « É » donne lecture et écriture ; « L » donne lecture seule. Voir
# docs/suivi/DECISIONS.md pour le détail du calcul, croisement par croisement.
#
# Correction datée (2026-10-13, US-SUI-01, prompt 44, D-264) : le domaine
# « suivi » était croisé « L » pour Cellule planification et Cellule examens
# dans le dossier (§ 11.2), jamais consommé avant cette story. Le backlog
# v10 d'US-SUI-01 (C5) et son prompt ne donnent la lecture du rapprochement
# qu'à la cellule pédagogique et à la Direction de formation — les deux
# lignes concernées sont corrigées ici, pas seulement dans l'écran.
MATRICE = {
    "Administrateur": [
        "administration_lecture",
        "administration_ecriture",
    ],
    "Cellule pédagogique": [
        "referentiel_lecture",
        "referentiel_ecriture",
        "organisation_lecture",
        "organisation_ecriture",
        "instructeurs_qualifications_lecture",
        "instructeurs_qualifications_ecriture",
        "lieux_calendrier_lecture",
        "programme_lecture",
        "programme_validation_lecture",
        "programme_validation_ecriture",
        "suivi_lecture",
        "suivi_ecriture",
    ],
    "Cellule planification": [
        "referentiel_lecture",
        "organisation_lecture",
        "instructeurs_qualifications_lecture",
        "lieux_calendrier_lecture",
        "lieux_calendrier_ecriture",
        "programme_lecture",
        "programme_ecriture",
        "programme_validation_lecture",
    ],
    "Cellule examens": [
        "referentiel_lecture",
        "organisation_lecture",
        "lieux_calendrier_lecture",
        "evaluations_lecture",
        "evaluations_ecriture",
    ],
    "Direction de formation": [
        "referentiel_lecture",
        "organisation_lecture",
        "instructeurs_qualifications_lecture",
        "lieux_calendrier_lecture",
        "programme_lecture",
        "programme_validation_lecture",
        "evaluations_lecture",
        "suivi_lecture",
    ],
}
