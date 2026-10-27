"""Ressources du jeu volumineux — Prompt 51, Temps 3, § 3.1. ≈80
instructeurs (militaires, vacataires, civils ; 2 à 5 qualifications
chacun ; quelques archivés), 36 salles attitrées, 8 lieux partagés,
≈40 indisponibilités passées et à venir."""

import datetime

from django.utils import timezone

from evaluations.jeu_recette.alea import nom_fictif
from evaluations.jeu_recette.donnees_volume import (
    CAPACITE_LIEU_PARTAGE,
    CAPACITE_SALLE_ATTITREE,
    NOMBRE_INDISPONIBILITES,
    NOMBRE_INSTRUCTEURS,
    NOMBRE_LIEUX_PARTAGES_AMPHI_SIMULTANE,
    NOMBRE_LIEUX_PARTAGES_LABO_SEQUENTIEL,
    NOMBRE_LIEUX_PARTAGES_SALLE_SPECIALISEE,
    NOMBRE_SALLES_ATTITREES,
    PROPORTION_INSTRUCTEURS_ARCHIVES,
    QUALIFICATIONS_PAR_INSTRUCTEUR,
)
from ressources.models import CategorieLieu, ModePartage, Statut, TypeLieuPartage
from ressources.services.indisponibilite_instructeur import ServiceIndisponibiliteInstructeur
from ressources.services.instructeur import ServiceInstructeur
from ressources.services.lieu import ServiceLieu
from ressources.services.qualification import ServiceQualification

STATUTS = (Statut.MILITAIRE_DU_CENTRE, Statut.VACATAIRE, Statut.CIVIL)
MOTIF_INDISPONIBILITE = "Mission (jeu volumineux)."


def charger_instructeurs_volume(agissant, generateur, stdout):
    instructeurs = {}
    nombre_archives = round(NOMBRE_INSTRUCTEURS * PROPORTION_INSTRUCTEURS_ARCHIVES)
    for indice in range(1, NOMBRE_INSTRUCTEURS + 1):
        code = f"IV{indice:03d}"
        instructeur = ServiceInstructeur.creer(
            agissant,
            {
                "nom": code,
                "prenom": nom_fictif(generateur, 2),
                "matricule": f"REC-VOL-{indice:04d}",
                "grade": generateur.choice(("Lt", "Cne", "Cdt", "2cl", "Sgt")),
                "specialite": "Volume",
                "statut": generateur.choice(STATUTS),
            },
        )
        if indice > NOMBRE_INSTRUCTEURS - nombre_archives:
            instructeur = ServiceInstructeur.archiver(agissant, instructeur.pk)
        instructeurs[code] = instructeur
    stdout.write(f"  {len(instructeurs)} instructeurs ajoutés ({nombre_archives} archivés).")
    return instructeurs


def charger_qualifications_volume(agissant, generateur, instructeurs, matieres, stdout):
    codes_matieres = list(matieres.keys())
    total = 0
    for instructeur in instructeurs.values():
        nombre = generateur.randint(*QUALIFICATIONS_PAR_INSTRUCTEUR)
        for code_matiere in generateur.sample(codes_matieres, nombre):
            ServiceQualification.ajouter(agissant, instructeur, matieres[code_matiere])
            total += 1
    stdout.write(f"  {total} qualifications accordées.")


def _charger_salles_attitrees(agissant, generateur, stdout):
    salles = {}
    for indice in range(1, NOMBRE_SALLES_ATTITREES + 1):
        code = f"LV-A{indice:02d}"
        salles[code] = ServiceLieu.creer(
            agissant,
            {
                "intitule": f"{code} — Salle de recette volumineuse {indice}",
                "capacite": generateur.randint(*CAPACITE_SALLE_ATTITREE),
                "categorie": CategorieLieu.SALLE_ATTITREE,
                "type_partage": None,
                "mode_partage": None,
            },
        )
    stdout.write(f"  {len(salles)} salles attitrées ajoutées.")
    return salles


def _charger_lieux_partages(agissant, generateur, stdout):
    lieux = {}
    specification = (
        ("AM", NOMBRE_LIEUX_PARTAGES_AMPHI_SIMULTANE, TypeLieuPartage.AMPHITHEATRE, ModePartage.SIMULTANE),
        ("LB", NOMBRE_LIEUX_PARTAGES_LABO_SEQUENTIEL, TypeLieuPartage.LABORATOIRE, ModePartage.SEQUENTIEL),
        ("SP", NOMBRE_LIEUX_PARTAGES_SALLE_SPECIALISEE, TypeLieuPartage.SALLE_SPECIALISEE, ModePartage.SEQUENTIEL),
    )
    for prefixe, nombre, type_partage, mode_partage in specification:
        for indice in range(1, nombre + 1):
            code = f"LV-{prefixe}{indice}"
            lieux[code] = ServiceLieu.creer(
                agissant,
                {
                    "intitule": f"{code} — Lieu partagé volumineux {indice}",
                    "capacite": generateur.randint(*CAPACITE_LIEU_PARTAGE),
                    "categorie": CategorieLieu.LIEU_PARTAGE,
                    "type_partage": type_partage,
                    "mode_partage": mode_partage,
                },
            )
    stdout.write(f"  {len(lieux)} lieux partagés ajoutés.")
    return lieux


def charger_lieux_volume(agissant, generateur, stdout):
    lieux = _charger_salles_attitrees(agissant, generateur, stdout)
    lieux.update(_charger_lieux_partages(agissant, generateur, stdout))
    return lieux


def charger_indisponibilites_volume(agissant, generateur, instructeurs, date_reference, stdout):
    """≈40, passées et à venir (§ 3.1) — bornées à ± 6 mois autour de `D`
    pour rester dans l'horizon d'une année de calendrier (§ 3.1, une
    année). RG-24 ne refuse jamais un chevauchement (fusion automatique) :
    seul un doublon EXACT lèverait — impossible en pratique avec un tirage
    aléatoire sur ±180 jours, aucune garde nécessaire ici. Un instructeur
    archivé refuse toute indisponibilité nouvelle (service) : exclus du
    tirage, pas une exception à rattraper."""
    codes_instructeurs = [code for code, i in instructeurs.items() if not i.archive]
    for _ in range(NOMBRE_INDISPONIBILITES):
        instructeur = instructeurs[generateur.choice(codes_instructeurs)]
        decalage_jours = generateur.randint(-180, 180)
        jour = date_reference + datetime.timedelta(days=decalage_jours)
        debut = timezone.make_aware(datetime.datetime.combine(jour, datetime.time(8, 0)))
        fin = debut + datetime.timedelta(hours=generateur.randint(2, 48))
        ServiceIndisponibiliteInstructeur.confirmer(agissant, instructeur, debut, fin, MOTIF_INDISPONIBILITE)
    stdout.write(f"  {NOMBRE_INDISPONIBILITES} indisponibilités ajoutées.")
