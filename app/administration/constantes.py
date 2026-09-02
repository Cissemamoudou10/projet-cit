"""Valeurs de domaine de l'application `administration`."""

GROUPES = [
    "Administrateur",
    "Cellule pédagogique",
    "Cellule planification",
    "Cellule examens",
    "Direction de formation",
]

# § 11.2 du dossier des cas d'utilisation — neuf domaines, deux niveaux
# chacun. « É » donne lecture et écriture ; « L » donne lecture seule. Voir
# docs/suivi/DECISIONS.md pour le détail du calcul, croisement par croisement.
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
        "suivi_lecture",
    ],
    "Cellule examens": [
        "referentiel_lecture",
        "organisation_lecture",
        "lieux_calendrier_lecture",
        "evaluations_lecture",
        "evaluations_ecriture",
        "suivi_lecture",
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
