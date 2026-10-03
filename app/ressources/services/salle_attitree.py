"""Affectation d'une salle attitrée à une brigade — CU-P3-03, RG-13, RG-14.

Domaine `lieux_calendrier` (D-11), pas `organisation` : l'affectation est un
acte de la cellule planification sur une ressource qu'elle détient,
appliqué à une brigade qu'elle ne peut pas modifier (arbitrage § 0.1,
Prompt 22, D-85, D-78).

Un service ne connaît pas la requête HTTP — voir .claude/rules/services.md.
"""

import datetime

from django.db import IntegrityError, transaction
from django.utils import timezone

from administration.habilitations import verifier_habilitation
from administration.models import TypeAction
from administration.services.journal import DonneesEntreeJournal, ServiceJournal
from noyau.exceptions import ErreurIntrouvable, ErreurValidation
from noyau.intervalles import filtre_recouvrement
from noyau.services.base import ServiceBase
from noyau.services.gestion import avertissement
from ressources.models import CategorieLieu, Lieu, SalleAttitree

OBJET_TYPE = "salle_attitree"
PERMISSION_LECTURE = "noyau.lieux_calendrier_lecture"
PERMISSION_ECRITURE = "noyau.lieux_calendrier_ecriture"


class ServiceSalleAttitree:
    DOMAINE = "lieux_calendrier"
    PERMISSION_LECTURE = PERMISSION_LECTURE
    PERMISSION_ECRITURE = PERMISSION_ECRITURE

    @staticmethod
    def obtenir(pk):
        try:
            return SalleAttitree.objects.select_related("lieu", "brigade__session").get(pk=pk)
        except SalleAttitree.DoesNotExist as erreur:
            raise ErreurIntrouvable(f"Salle attitrée introuvable (identifiant {pk}).") from erreur

    @staticmethod
    def obtenir_pour_brigade(brigade):
        """`None` si la brigade n'a pas encore de salle — état transitoire
        légitime entre sa création et son attribution (§ 4, Prompt 22)."""
        try:
            return brigade.salle_attitree
        except SalleAttitree.DoesNotExist:
            return None

    @staticmethod
    def lister_pour_lieu(agissant, lieu):
        """Fiche d'un lieu (§ 5, Prompt 22) — même patron que
        `ServiceIndisponibiliteLieu.lister_pour_lieu` : une vue appelle un
        service, jamais un gestionnaire de relation à même le modèle."""
        verifier_habilitation(agissant, PERMISSION_LECTURE)
        return lieu.brigades_attitrees.select_related("brigade", "brigade__session").order_by(
            "brigade__session__date_debut"
        )

    @staticmethod
    def salles_candidates(agissant, brigade):
        """Salles « attribuables » (§ 5, Prompt 22) : catégorie salle
        attitrée, non archivées, capacité renseignée, libres sur la période
        de la session. Les salles de capacité insuffisante restent dans la
        liste, signalées — retirer silencieusement une information qu'un
        lecteur ne peut pas deviner est le défaut que D-63 a refusé.
        Confort d'écran, PAS le contrôle : `attribuer` refuse indépendamment.
        """
        verifier_habilitation(agissant, PERMISSION_LECTURE)
        session = brigade.session
        candidats = Lieu.objects.filter(
            categorie=CategorieLieu.SALLE_ATTITREE, archive=False, capacite__isnull=False
        )
        occupes = {
            candidat.lieu_id
            for candidat in SalleAttitree.objects.filter(lieu__in=candidats)
            .exclude(brigade=brigade)
            .select_related("brigade__session")
            if _periodes_secantes(
                candidat.brigade.session.date_debut,
                candidat.brigade.session.date_fin,
                session.date_debut,
                session.date_fin,
            )
        }
        return [
            {"lieu": lieu, "capacite_suffisante": lieu.capacite >= brigade.effectif_previsionnel}
            for lieu in candidats.exclude(pk__in=occupes).order_by("intitule")
        ]

    @classmethod
    def attribuer(cls, agissant, brigade, lieu):
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        cls._verifier_lieu(lieu, brigade, brigade.session.date_debut, brigade.session.date_fin)
        salle = SalleAttitree(brigade=brigade, lieu=lieu)
        try:
            with transaction.atomic():
                ServiceBase.creer(salle, agissant)
                _journaliser(
                    agissant,
                    TypeAction.CREATION_ELEMENT_GESTION,
                    salle,
                    valeur_apres={"lieu": lieu.intitule},
                )
        except IntegrityError as erreur:
            raise ErreurValidation(
                f"« {brigade} » porte déjà une salle attitrée."
            ) from erreur
        salle.avertissements = _avertissement_indisponibilites(lieu, brigade.session)
        return salle

    @classmethod
    def modifier(cls, agissant, salle, nouveau_lieu):
        """A2 — la nouvelle salle est vérifiée disponible sur la PÉRIODE
        RESTANTE, pas sur toute la période de la session : une salle occupée
        par une autre brigade jusqu'à la semaine dernière n'empêche pas de
        la reprendre aujourd'hui (§ 4, Prompt 22)."""
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        session = salle.brigade.session
        debut_restant, fin_restant = _periode_restante(session)
        cls._verifier_lieu(
            nouveau_lieu, salle.brigade, debut_restant, fin_restant, exclure_pk=salle.pk
        )
        ancien_lieu = salle.lieu
        salle.lieu = nouveau_lieu
        with transaction.atomic():
            ServiceBase.modifier(salle, agissant)
            _journaliser(
                agissant,
                TypeAction.MODIFICATION_ELEMENT_GESTION,
                salle,
                valeur_avant={"lieu": ancien_lieu.intitule},
                valeur_apres={"lieu": nouveau_lieu.intitule},
            )
        salle.avertissements = _avertissement_indisponibilites(nouveau_lieu, session)
        return salle

    @staticmethod
    def retirer(agissant, salle):
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        with transaction.atomic():
            _journaliser(
                agissant,
                TypeAction.SUPPRESSION_ELEMENT_GESTION,
                salle,
                valeur_avant={"lieu": salle.lieu.intitule},
            )
            salle.delete()

    @staticmethod
    def _verifier_lieu(lieu, brigade, debut, fin, *, exclure_pk=None):
        """Contrôles dans l'ordre du § 4 (Prompt 22), tous testés."""
        if lieu.categorie != CategorieLieu.SALLE_ATTITREE:
            raise ErreurValidation(
                f"« {lieu} » est un lieu partagé, non attribuable à demeure : "
                "choisissez un lieu de catégorie « salle attitrée »."
            )
        if lieu.archive:
            raise ErreurValidation(f"« {lieu} » est archivé ; désarchivez-le ou choisissez un autre lieu.")
        if lieu.capacite is None:
            raise ErreurValidation(
                f"La capacité de « {lieu} » n'est pas renseignée ; renseignez-la avant de l'attribuer."
            )
        if lieu.capacite < brigade.effectif_previsionnel:
            ecart = brigade.effectif_previsionnel - lieu.capacite
            raise ErreurValidation(
                f"La capacité de « {lieu} » ({lieu.capacite}) est insuffisante pour "
                f"« {brigade.designation} » (effectif prévisionnel {brigade.effectif_previsionnel}) : "
                f"il manque {ecart} place{'s' if ecart > 1 else ''}."
            )
        conflit = _conflit_occupation(lieu, debut, fin, exclure_pk=exclure_pk)
        if conflit:
            session_conflit = conflit.brigade.session
            raise ErreurValidation(
                f"« {lieu} » est déjà attitrée à « {conflit.brigade.designation} » de la session "
                f"« {session_conflit.intitule} », du {session_conflit.date_debut:%d/%m/%Y} au "
                f"{session_conflit.date_fin:%d/%m/%Y}."
            )


def _periodes_secantes(debut_a, fin_a, debut_b, fin_b):
    """Bornes inclusives : deux périodes strictement contiguës (l'une
    commence le lendemain de la fin de l'autre) ne se chevauchent PAS —
    comportement retenu pour A7, énoncé une fois ici plutôt que recopié."""
    return debut_a <= fin_b and debut_b <= fin_a


def _periode_restante(session):
    """§ 4, Prompt 22 : de la date du jour si la session a commencé, de sa
    date de début sinon — `max()` couvre les deux cas d'un coup."""
    return max(session.date_debut, timezone.localdate()), session.date_fin


def _conflit_occupation(lieu, debut, fin, *, exclure_pk=None):
    candidats = SalleAttitree.objects.filter(lieu=lieu).select_related("brigade__session")
    if exclure_pk is not None:
        candidats = candidats.exclude(pk=exclure_pk)
    for candidat in candidats:
        session = candidat.brigade.session
        if _periodes_secantes(session.date_debut, session.date_fin, debut, fin):
            return candidat
    return None


def _avertissement_indisponibilites(lieu, session):
    """Troisième usage du mécanisme d'avertissement (D-71/D-79) : la salle
    est attribuée MALGRÉ TOUT si elle porte des indisponibilités recouvrant
    la période — ce sont les séances de ces périodes qui devront être
    replacées, pas l'attribution qui doit être refusée (§ 4, Prompt 22)."""
    debut_dt = timezone.make_aware(datetime.datetime.combine(session.date_debut, datetime.time.min))
    fin_dt = timezone.make_aware(
        datetime.datetime.combine(session.date_fin + datetime.timedelta(days=1), datetime.time.min)
    )
    indisponibilites = lieu.indisponibilites.filter(
        filtre_recouvrement("debut", "fin", debut_dt, fin_dt)
    ).order_by("debut")
    if not indisponibilites:
        return []
    periodes = ", ".join(
        f"du {i.debut:%d/%m/%Y %H:%M} au {i.fin:%d/%m/%Y %H:%M}" for i in indisponibilites
    )
    return [
        avertissement(
            "salle_partiellement_indisponible",
            f"« {lieu} » porte une ou plusieurs indisponibilités recouvrant la période de la "
            f"session : {periodes}. Les séances concernées devront être placées ailleurs.",
        )
    ]


def _journaliser(agissant, nature, salle, *, valeur_avant=None, valeur_apres=None):
    identifiant = str(salle.brigade)
    ServiceJournal.enregistrer_detaillee(
        DonneesEntreeJournal(
            type_action=nature,
            identifiant_saisi=identifiant,
            auteur=agissant,
            objet_type=OBJET_TYPE,
            objet_identifiant=identifiant,
            valeur_avant=valeur_avant,
            valeur_apres=valeur_apres,
        )
    )
