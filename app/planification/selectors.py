"""Lectures complexes séparées des services — .claude/rules/python.md.

`seances_futures_qualification` est installée comme fournisseur de
`noyau.services.parametres.ResolveurSeancesFuturesQualification` au
démarrage de l'application (`planification.apps.PlanificationConfig.ready`)
— c'est ce câblage qui referme réellement D-51 (RG-22), voir
docs/suivi/DECISIONS.md.

`apercu_regeneration`/`grille_consultation` servent les écrans de l'US-PLAN-03
(Prompt 31, § 9) — lecture seule, aucune règle métier : la vue les appelle
pour construire un contexte déjà prêt à afficher.
"""

import dataclasses

from django.utils import timezone

from organisation.models import Brigade
from planification.models import ProgrammeHebdomadaire, Seance
from ressources.models import CreneauType, GrilleHoraire

JOUR_SEMAINE_PAR_ISO = {
    "lundi": 1,
    "mardi": 2,
    "mercredi": 3,
    "jeudi": 4,
    "vendredi": 5,
    "samedi": 6,
    "dimanche": 7,
}


def grille_active_avec_creneaux():
    """Lecture seule utilisée par les vues (`.claude/rules/vues.md` — une
    vue n'importe jamais un modèle, elle appelle un sélecteur)."""
    grille = GrilleHoraire.objects.filter(active=True).first()
    creneaux = list(CreneauType.objects.filter(grille=grille)) if grille else []
    return grille, creneaux


def programme_de_la_semaine(lundi_de_semaine):
    return ProgrammeHebdomadaire.objects.filter(lundi_de_semaine=lundi_de_semaine).first()


def brigades_pour_filtre(brigade_pk=None, session_pk=None):
    brigades = Brigade.objects.select_related("session").order_by("session__intitule", "designation")
    if brigade_pk:
        return brigades.filter(pk=brigade_pk)
    if session_pk:
        return brigades.filter(session_id=session_pk)
    return brigades


def apercu_regeneration(lundi_de_semaine, brigades) -> dict:
    """BNF-09 : nombre de séances NON VERROUILLÉES qu'une régénération
    supprimerait pour chaque brigade sélectionnée — vide si aucun programme
    n'existe encore pour cette semaine (première génération, rien à
    régénérer)."""
    programme = ProgrammeHebdomadaire.objects.filter(lundi_de_semaine=lundi_de_semaine).first()
    if programme is None:
        return {}
    brigades_par_pk = {brigade.pk: brigade for brigade in brigades}
    lignes = Seance.objects.filter(
        programme=programme, verrouillee=False, lignes__brigade_id__in=brigades_par_pk
    ).values_list("lignes__brigade_id", flat=True)
    comptes = {}
    for brigade_id in lignes:
        brigade = brigades_par_pk[brigade_id]
        comptes[brigade] = comptes.get(brigade, 0) + 1
    return comptes


@dataclasses.dataclass(frozen=True)
class CelluleProgramme:
    seance: object = None

    @property
    def libelle_vide(self):
        return "AD/GROUPEMENT"


def grille_consultation(programme, creneaux, brigades):
    """Une ligne par brigade (§ 9), une colonne par créneau de la grille
    fournie par l'appelant. `creneaux` : `CreneauType` ordonnés jour/rang."""
    brigades_ids = {brigade.pk for brigade in brigades}
    seances = (
        Seance.objects.filter(programme=programme, lignes__brigade__in=brigades)
        .distinct()
        .select_related("element_referentiel__matiere", "instructeur", "lieu")
        .prefetch_related("lignes__brigade")
    )
    par_brigade_horaire = {}
    for seance in seances:
        debut_local = timezone.localtime(seance.debut)
        cle_horaire = (debut_local.isoweekday(), debut_local.time())
        for ligne in seance.lignes.all():
            if ligne.brigade_id in brigades_ids:
                par_brigade_horaire[(ligne.brigade_id, cle_horaire)] = seance
    lignes = []
    for brigade in brigades:
        cellules = []
        for creneau in creneaux:
            cle = (JOUR_SEMAINE_PAR_ISO[creneau.jour_semaine], creneau.heure_debut)
            cellules.append(CelluleProgramme(seance=par_brigade_horaire.get((brigade.pk, cle))))
        lignes.append({"brigade": brigade, "cellules": cellules})
    return lignes


def seances_futures_qualification(instructeur, matiere) -> list[str]:
    """Séances NON ENCORE TERMINÉES (`fin > maintenant`) de cet instructeur
    sur cette matière du catalogue — RG-22. Rendu en chaînes déjà formées :
    `ressources` n'a besoin de rien connaître de `Seance` au-delà de ce
    texte, le résolveur de `noyau` ne transporte que la donnée, jamais
    l'objet."""
    seances = (
        Seance.objects.filter(
            instructeur=instructeur,
            element_referentiel__matiere=matiere,
            fin__gt=timezone.now(),
        )
        .select_related("element_referentiel__matiere")
        .order_by("debut")
    )
    return [str(seance) for seance in seances]
