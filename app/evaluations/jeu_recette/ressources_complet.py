"""Ressources ajoutées par l'état `complet` — Prompt 51, § 2.2.

`agissant` est `u_plan` pour tout ce module (instructeurs/lieux/qualifications
sont pédagogiques dans le socle, mais indisponibilités et calendrier sont du
domaine `lieux_calendrier`, propre à la cellule planification — même
répartition que `jeu_recette.referentiel`/`instructeurs` vs `lieux.py`)."""

import datetime

from django.utils import timezone

from evaluations.jeu_recette.donnees_complet import (
    INSTRUCTEURS_COMPLET,
    LIEUX_COMPLET,
    MOTIF_INDISPONIBILITE_I3,
    PERIODES_COMPLET,
    QUALIFICATION_AJOUTEE_I3,
)
from evaluations.jeu_recette.semaines import jour_de_semaine
from ressources.models import NatureEvenement, Statut
from ressources.services.indisponibilite_instructeur import ServiceIndisponibiliteInstructeur
from ressources.services.instructeur import ServiceInstructeur
from ressources.services.lieu import ServiceLieu
from ressources.services.periode_calendrier import DonneesPeriode, ServicePeriodeCalendrier
from ressources.services.qualification import ServiceQualification

GRADE_PAR_DEFAUT = "Lt"
SPECIALITE_PAR_DEFAUT = "Recette"


def charger_instructeurs_complet(agissant, stdout):
    instructeurs = {}
    for donnees in INSTRUCTEURS_COMPLET:
        instructeurs[donnees.code] = ServiceInstructeur.creer(
            agissant,
            {
                "nom": donnees.code,
                "prenom": "Recette",
                "matricule": donnees.matricule,
                "grade": GRADE_PAR_DEFAUT,
                "specialite": SPECIALITE_PAR_DEFAUT,
                "statut": Statut.MILITAIRE_DU_CENTRE,
            },
        )
    stdout.write(f"  {len(instructeurs)} instructeurs ajoutés (I6-I9).")
    return instructeurs


def charger_qualifications_complet(
    agissant, instructeurs_complet, instructeurs_socle, matieres, stdout
):
    total = 0
    for donnees in INSTRUCTEURS_COMPLET:
        instructeur = instructeurs_complet[donnees.code]
        for code_matiere in donnees.qualifications:
            ServiceQualification.ajouter(agissant, instructeur, matieres[code_matiere])
            total += 1
    code_instructeur, code_matiere = QUALIFICATION_AJOUTEE_I3
    ServiceQualification.ajouter(
        agissant, instructeurs_socle[code_instructeur], matieres[code_matiere]
    )
    total += 1
    stdout.write(f"  {total} qualifications accordées (dont M1 ajoutée à I3).")


def charger_lieux_complet(agissant, stdout):
    lieux = {}
    for donnees in LIEUX_COMPLET:
        lieux[donnees.code] = ServiceLieu.creer(
            agissant,
            {
                "intitule": donnees.libelle,
                "capacite": donnees.capacite,
                "categorie": donnees.categorie,
                "type_partage": donnees.type_partage,
                "mode_partage": donnees.mode_partage,
            },
        )
    stdout.write(f"  {len(lieux)} lieux ajoutés (L7-L9).")
    return lieux


def charger_indisponibilite_i3(agissant, instructeur_i3, date_reference, stdout):
    """§ 2.2 : « tout le mardi de W-1 », motif « stage » — bornes posées sur
    la journée entière (00:00 -> 00:00 le lendemain), RG-23 (saisie
    déléguée : `agissant`, jamais `instructeur_i3`, est l'auteur de
    l'indisponibilité)."""
    mardi = jour_de_semaine(date_reference, -1, 2)
    debut = timezone.make_aware(datetime.datetime.combine(mardi, datetime.time.min))
    fin = timezone.make_aware(
        datetime.datetime.combine(mardi + datetime.timedelta(days=1), datetime.time.min)
    )
    ServiceIndisponibiliteInstructeur.confirmer(
        agissant, instructeur_i3, debut, fin, MOTIF_INDISPONIBILITE_I3
    )
    stdout.write(f"  Indisponibilité de I3 déclarée (mardi {mardi.isoformat()}, motif « stage »).")


def _bornes_periode(donnees, date_reference):
    debut_date = jour_de_semaine(
        date_reference, donnees.decalage_semaine_debut, donnees.jour_iso_debut
    )
    fin_date = jour_de_semaine(date_reference, donnees.decalage_semaine_fin, donnees.jour_iso_fin)
    if donnees.heure_debut is None:
        debut = timezone.make_aware(datetime.datetime.combine(debut_date, datetime.time.min))
    else:
        heure, minute = donnees.heure_debut
        debut = timezone.make_aware(
            datetime.datetime.combine(debut_date, datetime.time(heure, minute))
        )
    if donnees.heure_fin is None:
        fin = timezone.make_aware(
            datetime.datetime.combine(fin_date + datetime.timedelta(days=1), datetime.time.min)
        )
    else:
        heure, minute = donnees.heure_fin
        fin = timezone.make_aware(datetime.datetime.combine(fin_date, datetime.time(heure, minute)))
    return debut, fin


def charger_periodes_complet(agissant, brigades_complet, date_reference, stdout):
    """§ 2.2 : trois périodes, centre entier sauf le bivouac (brigade EXP2)."""
    for donnees in PERIODES_COMPLET:
        nature = NatureEvenement.objects.get(libelle=donnees.nature)
        debut, fin = _bornes_periode(donnees, date_reference)
        brigades = [brigades_complet[donnees.cible_brigade]] if donnees.cible_brigade else []
        ServicePeriodeCalendrier.creer(
            agissant,
            DonneesPeriode(
                nature=nature,
                intitule=donnees.intitule,
                debut=debut,
                fin=fin,
                effet="",
                sessions=[],
                brigades=brigades,
            ),
        )
    stdout.write(f"  {len(PERIODES_COMPLET)} périodes de calendrier ajoutées.")
