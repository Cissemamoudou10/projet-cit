"""Calendrier académique annuel — CU-P4-05, RG-28 à RG-30 bis, Prompt 28.

CHEVAUCHEMENT (RG-29, § 2 du Prompt 28 — arbitrage confirmé) : seul le
DOUBLON EXACT est refusé — mêmes bornes, mêmes cibles, même nature (fiche
CU-P4-05, E1). Toute autre intersection de bornes ET de portées est un
AVERTISSEMENT (E3), jamais un refus : les périodes se cumulent sans se
contredire. Ce contrôle porte sur deux relations multiples qu'aucune
contrainte SQL déclarative ne sait exprimer (`ck_periode_calendrier_bornes`
ne couvre que `fin > debut`) : il vit ici, seul endroit qui connaît encore
les cibles proposées avant l'écriture des tables d'association. Voir
docs/suivi/DECISIONS.md.

RG-30 bis : les sessions sont PROJETÉES depuis `organisation.Session`,
jamais saisies au calendrier — `bandes_sessions` est une lecture pure, sans
`PeriodeCalendrier` correspondante.
"""

import datetime
from dataclasses import dataclass

from django.db import models as django_models
from django.db import transaction
from django.utils import timezone

from administration.habilitations import verifier_habilitation
from administration.models import TypeAction
from administration.services.journal import DonneesEntreeJournal, ServiceJournal
from noyau.exceptions import ErreurIntrouvable, ErreurModificationConcurrente, ErreurValidation
from noyau.services.base import ServiceBase
from noyau.services.gestion import avertissement
from organisation.models import Brigade, Session
from ressources.models import PeriodeCalendrier, decrire_cibles

OBJET_TYPE = "periode_calendrier"
PERMISSION_LECTURE = "noyau.lieux_calendrier_lecture"
PERMISSION_ECRITURE = "noyau.lieux_calendrier_ecriture"


@dataclass(frozen=True)
class DonneesPeriode:
    """Regroupe les champs saisis (.claude/rules/python.md, § 5 paramètres
    max) — `effet` vide reprend `nature.effet_par_defaut` (§ 3, Prompt 28)."""

    nature: object
    intitule: str
    debut: object
    fin: object
    effet: str
    sessions: list
    brigades: list


def _valider_bornes(debut, fin):
    if fin <= debut:
        raise ErreurValidation("La fin de la période doit être postérieure au début.")


def _ids(objets):
    return {objet.pk for objet in objets}


def _periodes_secantes(debut, fin, *, exclut_pk=None):
    conflits = (
        PeriodeCalendrier.objects.filter(debut__lt=fin, fin__gt=debut)
        .select_related("nature")
        .prefetch_related("sessions", "brigades")
    )
    if exclut_pk is not None:
        conflits = conflits.exclude(pk=exclut_pk)
    return conflits


def _analyser_chevauchement(donnees, *, exclut_pk=None):
    """RG-29 : compare la période proposée à toute période existante dont
    les bornes se recoupent, PORTÉE PAR PORTÉE — l'absence de cible vaut
    centre entier, qui concerne par définition toute autre portée."""
    sessions_ids, brigades_ids = _ids(donnees.sessions), _ids(donnees.brigades)
    centre_entier = not sessions_ids and not brigades_ids
    avertissements = []
    for autre in _periodes_secantes(donnees.debut, donnees.fin, exclut_pk=exclut_pk):
        autre_sessions, autre_brigades = list(autre.sessions.all()), list(autre.brigades.all())
        autre_sessions_ids, autre_brigades_ids = _ids(autre_sessions), _ids(autre_brigades)
        autre_centre_entier = not autre_sessions_ids and not autre_brigades_ids
        sessions_communes_ids = sessions_ids & autre_sessions_ids
        brigades_communes_ids = brigades_ids & autre_brigades_ids
        if not (
            centre_entier or autre_centre_entier or sessions_communes_ids or brigades_communes_ids
        ):
            continue
        doublon = (
            autre.debut == donnees.debut
            and autre.fin == donnees.fin
            and autre_sessions_ids == sessions_ids
            and autre_brigades_ids == brigades_ids
            and autre.nature_id == donnees.nature.pk
        )
        if doublon:
            raise ErreurValidation(
                f"« {donnees.intitule} » fait doublon exact avec « {autre.intitule} » du "
                f"{autre.debut:%d/%m/%Y %H:%M} au {autre.fin:%d/%m/%Y %H:%M} : "
                "modifiez les bornes, les cibles ou la nature saisies."
            )
        avertissements.append(
            _avertissement_chevauchement(
                autre,
                centre_entier or autre_centre_entier,
                [s for s in donnees.sessions if s.pk in sessions_communes_ids],
                [b for b in donnees.brigades if b.pk in brigades_communes_ids],
            )
        )
    return avertissements


def _avertissement_chevauchement(autre, zone_centre_entier, sessions_communes, brigades_communes):
    if zone_centre_entier:
        zone = "le centre entier"
    else:
        description = decrire_cibles(sessions_communes, brigades_communes)
        zone = description[0].lower() + description[1:]
    return avertissement(
        "periode_chevauchement",
        f"Recouvre « {autre.intitule} » ({autre.nature.libelle}, du {autre.debut:%d/%m/%Y %H:%M} "
        f"au {autre.fin:%d/%m/%Y %H:%M}) sur {zone} : les deux périodes se cumulent, aucune "
        "n'est modifiée automatiquement.",
    )


def _avertissements_hors_dates_session(sessions, debut, fin):
    """E3/F1/F2 : une période ciblant une session dont les bornes débordent
    les dates de cette session est ACCEPTÉE, avec avertissement nommant la
    session concernée — jamais un refus (§ 7, Prompt 28)."""
    avertissements = []
    for session in sessions:
        debut_session = timezone.make_aware(
            datetime.datetime.combine(session.date_debut, datetime.time.min)
        )
        fin_session = timezone.make_aware(
            datetime.datetime.combine(
                session.date_fin + datetime.timedelta(days=1), datetime.time.min
            )
        )
        if debut < debut_session or fin > fin_session:
            avertissements.append(
                avertissement(
                    "periode_hors_dates_session",
                    f"La période déborde les dates de « {session} » (du "
                    f"{session.date_debut:%d/%m/%Y} au {session.date_fin:%d/%m/%Y}) : "
                    "vérifiez les bornes saisies.",
                )
            )
    return avertissements


def _capturer(periode):
    return {
        "nature": periode.nature.libelle,
        "intitule": periode.intitule,
        "debut": periode.debut.isoformat(),
        "fin": periode.fin.isoformat(),
        "effet": periode.effet,
    }


def _journaliser(agissant, nature_action, periode, *, valeur_avant=None, valeur_apres=None):
    ServiceJournal.enregistrer_detaillee(
        DonneesEntreeJournal(
            type_action=nature_action,
            identifiant_saisi=periode.intitule,
            auteur=agissant,
            objet_type=OBJET_TYPE,
            objet_identifiant=str(periode.pk),
            valeur_avant=valeur_avant,
            valeur_apres=valeur_apres,
        )
    )


class ServicePeriodeCalendrier:
    DOMAINE = "lieux_calendrier"
    PERMISSION_LECTURE = PERMISSION_LECTURE
    PERMISSION_ECRITURE = PERMISSION_ECRITURE

    @staticmethod
    def obtenir(pk):
        try:
            return (
                PeriodeCalendrier.objects.select_related("nature")
                .prefetch_related("sessions", "brigades")
                .get(pk=pk)
            )
        except PeriodeCalendrier.DoesNotExist as erreur:
            raise ErreurIntrouvable(f"Période introuvable (identifiant {pk}).") from erreur

    @staticmethod
    def lister(agissant, filtres):
        """Pas de pagination (D-32 : voir aussi US-SES-07) — une vue
        calendaire consomme une fenêtre entière (année/mois), jamais une
        page à la fois."""
        verifier_habilitation(agissant, PERMISSION_LECTURE)
        queryset = (
            PeriodeCalendrier.objects.select_related("nature")
            .prefetch_related("sessions", "brigades")
            .order_by("debut")
        )
        if filtres.get("fenetre_debut") and filtres.get("fenetre_fin"):
            queryset = queryset.filter(
                debut__lt=filtres["fenetre_fin"], fin__gt=filtres["fenetre_debut"]
            )
        if filtres.get("nature"):
            queryset = queryset.filter(nature_id=filtres["nature"])
        if filtres.get("effet"):
            queryset = queryset.filter(effet=filtres["effet"])
        session_pk, brigade_pk = filtres.get("session"), filtres.get("brigade")
        if session_pk or brigade_pk:
            condition = django_models.Q(sessions__isnull=True, brigades__isnull=True)
            if session_pk:
                condition |= django_models.Q(sessions__id=session_pk)
            if brigade_pk:
                condition |= django_models.Q(brigades__id=brigade_pk)
            queryset = queryset.filter(condition).distinct()
        return queryset

    @staticmethod
    def choix_sessions():
        """Pour le filtre par cible (§ 6, Prompt 28) — la vue ne doit jamais
        importer de modèle directement (.claude/rules/vues.md)."""
        return [(s.pk, s.intitule) for s in Session.objects.order_by("intitule")]

    @staticmethod
    def choix_brigades():
        return [(b.pk, str(b)) for b in Brigade.objects.order_by("designation")]

    @staticmethod
    def bandes_sessions(agissant, fenetre_debut, fenetre_fin):
        """RG-30 bis : lecture pure depuis `Session`, aucune écriture,
        aucune `PeriodeCalendrier` créée en contrepartie."""
        verifier_habilitation(agissant, PERMISSION_LECTURE)
        return Session.objects.filter(
            date_debut__lte=fenetre_fin, date_fin__gte=fenetre_debut
        ).order_by("date_debut")

    @staticmethod
    def creer(agissant, donnees):
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        _valider_bornes(donnees.debut, donnees.fin)
        effet_retenu = donnees.effet or donnees.nature.effet_par_defaut
        avertissements = _analyser_chevauchement(donnees) + _avertissements_hors_dates_session(
            donnees.sessions, donnees.debut, donnees.fin
        )
        with transaction.atomic():
            periode = PeriodeCalendrier(
                nature=donnees.nature,
                intitule=donnees.intitule,
                debut=donnees.debut,
                fin=donnees.fin,
                effet=effet_retenu,
            )
            ServiceBase.creer(periode, agissant)
            periode.sessions.set(donnees.sessions)
            periode.brigades.set(donnees.brigades)
            _journaliser(
                agissant,
                TypeAction.CREATION_ELEMENT_GESTION,
                periode,
                valeur_apres=_capturer(periode),
            )
        periode.avertissements = avertissements
        return periode

    @staticmethod
    def modifier(agissant, pk, donnees, modifie_le_attendu):
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        periode = ServicePeriodeCalendrier.obtenir(pk)
        if periode.modifie_le != modifie_le_attendu:
            raise ErreurModificationConcurrente(
                f"Cette période a été modifiée par {periode.modifie_par} entre-temps : "
                "reprenez votre saisie."
            )
        _valider_bornes(donnees.debut, donnees.fin)
        effet_retenu = donnees.effet or donnees.nature.effet_par_defaut
        avertissements = _analyser_chevauchement(
            donnees, exclut_pk=pk
        ) + _avertissements_hors_dates_session(donnees.sessions, donnees.debut, donnees.fin)
        avant = _capturer(periode)
        with transaction.atomic():
            periode.nature = donnees.nature
            periode.intitule = donnees.intitule
            periode.debut = donnees.debut
            periode.fin = donnees.fin
            periode.effet = effet_retenu
            ServiceBase.modifier(periode, agissant)
            periode.sessions.set(donnees.sessions)
            periode.brigades.set(donnees.brigades)
            _journaliser(
                agissant,
                TypeAction.MODIFICATION_ELEMENT_GESTION,
                periode,
                valeur_avant=avant,
                valeur_apres=_capturer(periode),
            )
        periode.avertissements = avertissements
        return periode

    @staticmethod
    def supprimer(agissant, pk):
        """A4 (report/déprogrammation) : traité comme une suppression puis
        une nouvelle déclaration, rien de spécifique à coder (§ 7, Prompt 28)."""
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        periode = ServicePeriodeCalendrier.obtenir(pk)
        with transaction.atomic():
            _journaliser(
                agissant,
                TypeAction.SUPPRESSION_ELEMENT_GESTION,
                periode,
                valeur_avant=_capturer(periode),
            )
            periode.delete()
