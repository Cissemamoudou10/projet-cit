"""Lecture de la grille de consultation du programme — US-PLAN-03 (Prompt 31,
§ 9), scindé de `selectors.py` qui dépassait 400 lignes
(.claude/rules/python.md) après R00B-GEN-06 (prompt 54).
"""

import dataclasses
import datetime

from django.db.models import Q
from django.utils import timezone

from noyau.services.parametres import ResolveurSeancesDeControle
from planification.generation.candidats import periode_bloquante
from planification.models import LigneProgramme
from planification.selectors import JOUR_SEMAINE_PAR_ISO
from planification.selectors_suivi import non_executions_des_lignes
from planification.services.contraintes import charger_periodes_bloquantes
from planification.services.temps import duree_heures


@dataclasses.dataclass(frozen=True)
class CelluleProgramme:
    ligne: object = None
    volume_cumule: float = 0.0
    autres_brigades: str = ""
    est_controle: bool = False
    creneau: object = None
    non_execution: object = None
    evenement_bloquant: object = None

    @property
    def seance(self):
        return self.ligne.seance if self.ligne else None

    @property
    def libelle_vide(self):
        return "AD/GROUPEMENT"

    @property
    def est_passee(self):
        """US-SUI-05, S2 : séance passée = fin antérieure à maintenant."""
        return self.seance is not None and self.seance.fin <= timezone.now()


def _lignes_du_programme(programme, brigades):
    return (
        LigneProgramme.objects.filter(seance__programme=programme, brigade__in=brigades)
        .select_related(
            "brigade", "seance__element_referentiel__matiere", "seance__instructeur", "seance__lieu"
        )
        .prefetch_related("seance__lignes__brigade")
    )


def _volumes_cumules(lignes_cibles):
    """Volume cumulé (`.claude/rules/modeles.md`, LigneProgramme) de chaque
    ligne affichée, calculé EN BLOC — `LigneProgramme.volume_cumule`
    interroge la base à chaque accès, une requête par cellule affichée
    violerait « aucune requête dans une boucle » (.claude/rules/python.md)
    sur une grille qui en compte plusieurs dizaines."""
    cibles_pk = {ligne.pk for ligne in lignes_cibles}
    paires = {(ligne.brigade_id, ligne.seance.element_referentiel_id) for ligne in lignes_cibles}
    if not paires:
        return {}
    filtre = Q()
    for brigade_id, element_id in paires:
        filtre |= Q(brigade_id=brigade_id, seance__element_referentiel_id=element_id)
    historique = (
        LigneProgramme.objects.filter(filtre).select_related("seance").order_by("seance__debut")
    )
    cumul, resultat = {}, {}
    for ligne in historique:
        cle = (ligne.brigade_id, ligne.seance.element_referentiel_id)
        cumul[cle] = cumul.get(cle, 0) + duree_heures(ligne.seance.debut, ligne.seance.fin)
        if ligne.pk in cibles_pk:
            resultat[ligne.pk] = cumul[cle]
    return resultat


def _autres_brigades(ligne):
    autres = [
        str(autre.brigade)
        for autre in ligne.seance.lignes.all()
        if autre.brigade_id != ligne.brigade_id
    ]
    if not autres:
        return ""
    return "regroupée — " + " + ".join([str(ligne.brigade)] + autres)


def _bornes_creneaux(programme, creneaux):
    """Datetimes réels (début du premier créneau, fin du dernier) du jour
    représenté par `creneaux` dans la semaine de `programme` — un seul jour,
    comme `grille_consultation` (§ 9). `None` si `creneaux` est vide."""
    if not creneaux:
        return None, None
    jour = programme.lundi_de_semaine + datetime.timedelta(
        days=JOUR_SEMAINE_PAR_ISO[creneaux[0].jour_semaine] - 1
    )
    debuts = [timezone.make_aware(datetime.datetime.combine(jour, c.heure_debut)) for c in creneaux]
    fins = [timezone.make_aware(datetime.datetime.combine(jour, c.heure_fin)) for c in creneaux]
    return jour, (min(debuts), max(fins))


@dataclasses.dataclass(frozen=True)
class _ContexteGrille:
    """Regroupe les lectures faites UNE FOIS pour toute la grille — § 5
    paramètres max, `.claude/rules/python.md` — avant la boucle par brigade
    de `grille_consultation`."""

    jour: object
    par_brigade_horaire: dict
    volumes: dict
    controles: set
    non_executions: dict
    periodes_bloquantes: list


def _cellules_de_la_brigade(brigade, creneaux, contexte):
    """Une `CelluleProgramme` par créneau du jour pour `brigade` —
    `evenement_bloquant` (R00B-GEN-06) seulement si la cellule est vide,
    par `periode_bloquante`, jamais une seconde implantation du blocage
    déjà écrit pour la génération (`planification.generation.candidats`)."""
    cellules = []
    for creneau in creneaux:
        cle = (brigade.pk, JOUR_SEMAINE_PAR_ISO[creneau.jour_semaine], creneau.heure_debut)
        ligne = contexte.par_brigade_horaire.get(cle)
        evenement = None
        if not ligne:
            debut = timezone.make_aware(
                datetime.datetime.combine(contexte.jour, creneau.heure_debut)
            )
            fin = timezone.make_aware(datetime.datetime.combine(contexte.jour, creneau.heure_fin))
            evenement = periode_bloquante(brigade, debut, fin, contexte.periodes_bloquantes)
        cellules.append(
            CelluleProgramme(
                ligne=ligne,
                volume_cumule=contexte.volumes.get(ligne.pk, 0) if ligne else 0,
                autres_brigades=_autres_brigades(ligne) if ligne else "",
                est_controle=ligne.seance_id in contexte.controles if ligne else False,
                creneau=creneau,
                non_execution=contexte.non_executions.get(ligne.pk) if ligne else None,
                evenement_bloquant=evenement,
            )
        )
    return cellules


def _par_brigade_horaire(lignes_qs):
    par_brigade_horaire = {}
    for ligne in lignes_qs:
        debut_local = timezone.localtime(ligne.seance.debut)
        cle = (ligne.brigade_id, debut_local.isoweekday(), debut_local.time())
        par_brigade_horaire[cle] = ligne
    return par_brigade_horaire


def _contexte_grille(programme, creneaux, lignes_qs):
    jour, bornes_jour = _bornes_creneaux(programme, creneaux)
    return _ContexteGrille(
        jour=jour,
        par_brigade_horaire=_par_brigade_horaire(lignes_qs),
        volumes=_volumes_cumules(lignes_qs),
        controles=ResolveurSeancesDeControle.resoudre({ligne.seance_id for ligne in lignes_qs}),
        non_executions=non_executions_des_lignes([ligne.pk for ligne in lignes_qs]),
        periodes_bloquantes=charger_periodes_bloquantes(*bornes_jour) if jour else [],
    )


def grille_consultation(programme, creneaux, brigades):
    """Groupée par type de formation, une ligne par brigade, une colonne
    par créneau (§ 9) — `creneaux` porte déjà UN SEUL JOUR, sélectionné par
    la vue (onglets), pour tenir en largeur (jamais les sept jours à la
    fois). R00B-GEN-06 : un créneau bloqué par une période du calendrier
    (US-PLAN-04) porte désormais l'événement — voir `_cellules_de_la_brigade`."""
    lignes_qs = list(_lignes_du_programme(programme, brigades))
    contexte = _contexte_grille(programme, creneaux, lignes_qs)

    groupes, brigades_par_type = [], {}
    for brigade in brigades:
        type_formation = brigade.session.formation.type_formation
        brigades_par_type.setdefault(type_formation, []).append(brigade)

    for type_formation, brigades_du_type in brigades_par_type.items():
        lignes_affichees = [
            {"brigade": brigade, "cellules": _cellules_de_la_brigade(brigade, creneaux, contexte)}
            for brigade in brigades_du_type
        ]
        groupes.append({"type_formation": type_formation, "lignes": lignes_affichees})
    return groupes
