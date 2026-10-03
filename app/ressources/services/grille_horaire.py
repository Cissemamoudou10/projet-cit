"""Grilles horaires et créneaux types — CU-P4-07, RG-62 à RG-64, Prompt 29.

NON-RECOUVREMENT DES CRÉNEAUX (E1) EN COUCHE SERVICES, jamais en base : les
trois autres modèles de période du projet (indisponibilité de lieu,
affectation de brigade, indisponibilité d'instructeur) portent des
horodatages et se contraignent avec `ExclusionConstraint`/`btree_gist` sur
un intervalle daté. `CreneauType` porte des HEURES SANS DATE — PostgreSQL
n'a pas de type d'intervalle horaire natif, et fabriquer un `int4range` de
minutes depuis minuit pour poser une contrainte d'exclusion coûterait une
colonne dérivée et une conversion à chaque écriture, pour quatre lignes par
jour éditées en bloc. Voir docs/suivi/DECISIONS.md.

ACTIVATION (RG-62/RG-63) EN UNE SEULE TRANSACTION : l'ancienne grille active
est désactivée SANS effacer sa `date_activation` (dernière fois où elle a
servi), la nouvelle est activée, journalisée avec les deux grilles. Aucune
entité d'historique d'activation — le journal, immuable, en tient lieu
(CLS-03 : « deux attributs suffisent, aucune entité n'est créée »).
"""

import datetime

from django.db import IntegrityError, transaction
from django.utils import timezone

from administration.habilitations import verifier_habilitation
from administration.models import TypeAction
from administration.services.journal import DonneesEntreeJournal, ServiceJournal
from noyau.exceptions import ErreurIntrouvable, ErreurModificationConcurrente, ErreurValidation
from noyau.intervalles import filtre_recouvrement
from noyau.pagination import paginer
from noyau.services.base import ServiceBase
from ressources.models import CreneauType, GrilleHoraire, JourSemaine

OBJET_TYPE_GRILLE = "grille_horaire"
OBJET_TYPE_CRENEAU = "creneau_type"
PERMISSION_LECTURE = "noyau.lieux_calendrier_lecture"
PERMISSION_ECRITURE = "noyau.lieux_calendrier_ecriture"


def _valider_intitule(intitule):
    if not intitule.strip():
        raise ErreurValidation("L'intitulé de la grille est obligatoire.")


def _erreur_intitule_duplique(intitule):
    existante = GrilleHoraire.objects.filter(intitule__iexact=intitule).first()
    return ErreurValidation(f"« {intitule} » est déjà attribué à {existante}.")


def _journaliser_grille(agissant, nature, grille, **capture):
    ServiceJournal.enregistrer_detaillee(
        DonneesEntreeJournal(
            type_action=nature,
            identifiant_saisi=grille.intitule,
            auteur=agissant,
            objet_type=OBJET_TYPE_GRILLE,
            objet_identifiant=str(grille.pk),
            **capture,
        )
    )


def _journaliser_creneau(agissant, nature, creneau):
    ServiceJournal.enregistrer_detaillee(
        DonneesEntreeJournal(
            type_action=nature,
            identifiant_saisi=str(creneau),
            auteur=agissant,
            objet_type=OBJET_TYPE_CRENEAU,
            objet_identifiant=str(creneau.pk),
        )
    )


def _duree(creneau):
    debut = datetime.datetime.combine(datetime.date.min, creneau.heure_debut)
    fin = datetime.datetime.combine(datetime.date.min, creneau.heure_fin)
    return fin - debut


def _semaine_type(grille):
    """Regroupe les créneaux de `grille` par jour, dans l'ordre de la
    semaine — la vue de fiche ne doit pas importer `JourSemaine` elle-même,
    voir .claude/rules/vues.md."""
    return [
        {
            "jour": jour,
            "libelle": libelle,
            "creneaux": [c for c in grille.creneaux.all() if c.jour_semaine == jour],
        }
        for jour, libelle in JourSemaine.choices
    ]


class ServiceGrilleHoraire:
    DOMAINE = "lieux_calendrier"
    PERMISSION_LECTURE = PERMISSION_LECTURE
    PERMISSION_ECRITURE = PERMISSION_ECRITURE

    @staticmethod
    def obtenir(pk):
        try:
            return (
                GrilleHoraire.objects.select_related("activee_par")
                .prefetch_related("creneaux")
                .get(pk=pk)
            )
        except GrilleHoraire.DoesNotExist as erreur:
            raise ErreurIntrouvable(f"Grille introuvable (identifiant {pk}).") from erreur

    @staticmethod
    def autre_grille_active(pk):
        """Pour l'écran de confirmation d'activation (§ 9, Prompt 29) : la
        vue ne doit jamais importer `ressources.models` directement, voir
        .claude/rules/vues.md."""
        return GrilleHoraire.objects.filter(active=True).exclude(pk=pk).first()

    @staticmethod
    def lister(agissant, filtres, page):
        verifier_habilitation(agissant, PERMISSION_LECTURE)
        queryset = GrilleHoraire.objects.select_related("activee_par").order_by("intitule")
        etat = filtres.get("etat")
        if etat == "active":
            queryset = queryset.filter(active=True)
        elif etat == "disponible":
            queryset = queryset.filter(active=False, archive=False)
        elif etat == "archivee":
            queryset = queryset.filter(archive=True)
        return paginer(queryset, page)

    @staticmethod
    def creer(agissant, intitule):
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        _valider_intitule(intitule)
        grille = GrilleHoraire(intitule=intitule)
        try:
            with transaction.atomic():
                ServiceBase.creer(grille, agissant)
                _journaliser_grille(
                    agissant,
                    TypeAction.CREATION_ELEMENT_GESTION,
                    grille,
                    valeur_apres={"intitule": intitule},
                )
        except IntegrityError as erreur:
            raise _erreur_intitule_duplique(intitule) from erreur
        return grille

    @staticmethod
    def modifier(agissant, pk, intitule, modifie_le_attendu):
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        grille = ServiceGrilleHoraire.obtenir(pk)
        if grille.modifie_le != modifie_le_attendu:
            raise ErreurModificationConcurrente(
                f"Cette grille a été modifiée par {grille.modifie_par} entre-temps : "
                "reprenez votre saisie."
            )
        _valider_intitule(intitule)
        avant = grille.intitule
        grille.intitule = intitule
        try:
            with transaction.atomic():
                ServiceBase.modifier(grille, agissant)
                _journaliser_grille(
                    agissant,
                    TypeAction.MODIFICATION_ELEMENT_GESTION,
                    grille,
                    valeur_avant={"intitule": avant},
                    valeur_apres={"intitule": intitule},
                )
        except IntegrityError as erreur:
            raise _erreur_intitule_duplique(intitule) from erreur
        return grille

    @staticmethod
    def dupliquer(agissant, pk, nouvel_intitule):
        """A3 : la grille de Ramadan se construit en partant de l'ordinaire
        — copie inactive, non archivée, tous les créneaux dupliqués."""
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        source = ServiceGrilleHoraire.obtenir(pk)
        _valider_intitule(nouvel_intitule)
        copie = GrilleHoraire(intitule=nouvel_intitule)
        try:
            with transaction.atomic():
                ServiceBase.creer(copie, agissant)
                for creneau in source.creneaux.all():
                    CreneauType.objects.create(
                        grille=copie,
                        jour_semaine=creneau.jour_semaine,
                        ordre=creneau.ordre,
                        heure_debut=creneau.heure_debut,
                        heure_fin=creneau.heure_fin,
                        cree_par=agissant,
                        modifie_par=agissant,
                    )
                _journaliser_grille(
                    agissant,
                    TypeAction.CREATION_ELEMENT_GESTION,
                    copie,
                    valeur_apres={"intitule": nouvel_intitule, "dupliquee_depuis": source.intitule},
                )
        except IntegrityError as erreur:
            raise _erreur_intitule_duplique(nouvel_intitule) from erreur
        return copie

    @staticmethod
    def archiver(agissant, pk):
        """§ 3, Prompt 29 : la grille active ne peut pas être archivée —
        il faut d'abord en activer une autre (E2, transposé)."""
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        grille = ServiceGrilleHoraire.obtenir(pk)
        if grille.active:
            raise ErreurValidation(
                f"« {grille.intitule} » est la grille active : activez-en une autre "
                "avant de l'archiver."
            )
        with transaction.atomic():
            grille.archive = True
            grille.archive_le = timezone.now()
            ServiceBase.modifier(grille, agissant)
            _journaliser_grille(agissant, TypeAction.ARCHIVAGE_ELEMENT_GESTION, grille)
        return grille

    @staticmethod
    def desarchiver(agissant, pk):
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        grille = ServiceGrilleHoraire.obtenir(pk)
        with transaction.atomic():
            grille.archive = False
            grille.archive_le = None
            ServiceBase.modifier(grille, agissant)
        return grille

    @staticmethod
    def supprimer(agissant, pk):
        """§ 3 : une grille jamais activée (brouillon) se supprime ; une
        grille qui a déjà servi ne se supprime plus, seulement s'archive —
        des séances en découlent, leur origine doit rester lisible."""
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        grille = ServiceGrilleHoraire.obtenir(pk)
        if grille.date_activation is not None:
            raise ErreurValidation(
                f"« {grille.intitule} » a déjà été activée : elle ne peut plus être "
                "supprimée, seulement archivée."
            )
        with transaction.atomic():
            _journaliser_grille(agissant, TypeAction.SUPPRESSION_ELEMENT_GESTION, grille)
            grille.delete()

    @staticmethod
    def activer(agissant, pk):
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        nouvelle = ServiceGrilleHoraire.obtenir(pk)
        if nouvelle.archive:
            raise ErreurValidation(
                f"« {nouvelle.intitule} » est archivée : désarchivez-la avant de l'activer."
            )
        if not nouvelle.creneaux.exists():
            raise ErreurValidation(
                f"« {nouvelle.intitule} » ne porte aucun créneau : aucune génération ne "
                "serait possible (E3)."
            )
        with transaction.atomic():
            ancienne = GrilleHoraire.objects.filter(active=True).exclude(pk=nouvelle.pk).first()
            if ancienne is not None:
                ancienne.active = False
                ServiceBase.modifier(ancienne, agissant)
            nouvelle.active = True
            nouvelle.date_activation = timezone.now()
            nouvelle.activee_par = agissant
            ServiceBase.modifier(nouvelle, agissant)
            _journaliser_grille(
                agissant,
                TypeAction.MODIFICATION_ELEMENT_GESTION,
                nouvelle,
                valeur_avant={"grille_desactivee": ancienne.intitule if ancienne else None},
                valeur_apres={"grille_activee": nouvelle.intitule},
            )
        return nouvelle

    @staticmethod
    def volume_hebdomadaire_reference():
        """§ 7, Prompt 29 : installé comme fournisseur au démarrage de
        l'application (`ressources.apps.RessourcesConfig.ready`) dans
        `noyau.services.parametres.ResolveurVolumeHoraireReference` — ne
        vérifie aucune habilitation, ce n'est pas un écran mais une lecture
        interne consommée par d'autres domaines."""
        grille = GrilleHoraire.objects.filter(active=True).first()
        if grille is None:
            return None
        total = sum((_duree(creneau) for creneau in grille.creneaux.all()), datetime.timedelta())
        return total.total_seconds() / 3600

    semaine_type = staticmethod(_semaine_type)


def _verifier_non_recouvrement(grille, jour_semaine, heure_debut, heure_fin, *, exclut_pk=None):
    """E1, § 5, Prompt 29 : par grille et par jour, jamais global (B5) —
    bornes semi-ouvertes, deux créneaux contigus ne se chevauchent pas
    (même convention qu'US-INS-03/US-PLAN-01, § 0.4)."""
    if heure_fin <= heure_debut:
        raise ErreurValidation("L'heure de fin doit être postérieure à l'heure de début.")
    conflits = grille.creneaux.filter(
        filtre_recouvrement("heure_debut", "heure_fin", heure_debut, heure_fin),
        jour_semaine=jour_semaine,
    )
    if exclut_pk is not None:
        conflits = conflits.exclude(pk=exclut_pk)
    conflit = conflits.first()
    if conflit is not None:
        raise ErreurValidation(
            f"Chevauche le créneau {conflit.heure_debut:%H:%M}–{conflit.heure_fin:%H:%M} "
            f"déjà présent le {conflit.get_jour_semaine_display().lower()} de cette grille."
        )


class ServiceCreneauType:
    """Sous-ressource composée depuis l'écran de sa grille — même figure
    que `ElementReferentiel` depuis une formation, `Brigade` depuis une
    session (§ 0.3, Prompt 29) : pas d'écran de premier niveau, pas de
    pagination."""

    DOMAINE = "lieux_calendrier"
    PERMISSION_LECTURE = PERMISSION_LECTURE
    PERMISSION_ECRITURE = PERMISSION_ECRITURE

    @staticmethod
    def obtenir(pk):
        try:
            return CreneauType.objects.select_related("grille").get(pk=pk)
        except CreneauType.DoesNotExist as erreur:
            raise ErreurIntrouvable(f"Créneau introuvable (identifiant {pk}).") from erreur

    @staticmethod
    def ajouter(agissant, grille, donnees):
        """`donnees` : `jour_semaine`, `ordre`, `heure_debut`, `heure_fin`
        (.claude/rules/python.md, § 5 paramètres max)."""
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        _verifier_non_recouvrement(
            grille, donnees["jour_semaine"], donnees["heure_debut"], donnees["heure_fin"]
        )
        creneau = CreneauType(grille=grille, **donnees)
        try:
            with transaction.atomic():
                ServiceBase.creer(creneau, agissant)
                _journaliser_creneau(agissant, TypeAction.CREATION_ELEMENT_GESTION, creneau)
        except IntegrityError as erreur:
            raise ErreurValidation(
                f"Le rang {donnees['ordre']} est déjà utilisé ce jour-là dans cette grille."
            ) from erreur
        return creneau

    @staticmethod
    def supprimer(agissant, creneau):
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        with transaction.atomic():
            _journaliser_creneau(agissant, TypeAction.SUPPRESSION_ELEMENT_GESTION, creneau)
            creneau.delete()
