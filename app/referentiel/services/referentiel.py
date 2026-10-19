"""Composition du référentiel d'une formation — CU-P2-04, CU-P2-05.

Pas `ServiceGestion` : `ElementReferentiel` n'est pas une entité de gestion
autonome (liste/créer/modifier/archiver) mais une sous-ressource composée
depuis l'écran d'une formation — c'est `ServiceReferentiel`, nommé dans
`.claude/rules/services.md`, table des huit services. Réutilise deux points
d'extension posés dans le patron pour ce cas précis : `noyau.services.
gestion.decrire_opposants` (RG-07, E3) et `valider_instance` (E2).

Un service ne connaît pas la requête HTTP — voir .claude/rules/services.md.
"""

from django.conf import settings
from django.db import IntegrityError, transaction
from django.db.models import Count, Sum
from django.db.models.deletion import ProtectedError

from administration.habilitations import verifier_habilitation
from administration.models import TypeAction
from administration.services.journal import DonneesEntreeJournal, ServiceJournal
from noyau.exceptions import ErreurIntrouvable, ErreurValidation
from noyau.services.base import ServiceBase
from noyau.services.gestion import decrire_opposants, valider_instance
from noyau.services.parametres import ResolveurVolumeHoraireReference
from referentiel.models import CategorieLieu, ElementReferentiel, TypeLieuPartage
from referentiel.services.matiere import ServiceMatiere
from referentiel.services.prerequis import ServicePrerequis

PERMISSION_LECTURE = "noyau.referentiel_lecture"
PERMISSION_ECRITURE = "noyau.referentiel_ecriture"


class ServiceReferentiel:
    DOMAINE = "referentiel"
    PERMISSION_LECTURE = PERMISSION_LECTURE
    PERMISSION_ECRITURE = PERMISSION_ECRITURE

    @staticmethod
    def categories_lieu():
        """Choix pour la liste déroulante — la vue ne doit jamais importer
        `referentiel.models` directement, voir .claude/rules/vues.md.
        """
        return CategorieLieu.choices

    @staticmethod
    def types_lieu_partage():
        return TypeLieuPartage.choices

    @staticmethod
    def lister(agissant, formation):
        """`nombre_instructeurs_qualifies` — US-INS-02, § 7.4 : compté par la
        relation inverse `matiere.qualifications` (posée dans `ressources`,
        `Qualification.matiere.related_name`), jamais par un import de
        `ressources` — `referentiel` ne peut pas en dépendre (voir
        `tests/architecture/test_couches.py::DEPENDANCES_AUTORISEES`).
        """
        verifier_habilitation(agissant, PERMISSION_LECTURE)
        return (
            ElementReferentiel.objects.filter(formation=formation)
            .select_related("matiere")
            .prefetch_related("matiere__objectifs_pedagogiques")
            .annotate(nombre_instructeurs_qualifies=Count("matiere__qualifications", distinct=True))
            .order_by("matiere__intitule")
        )

    @staticmethod
    def total_volume(formation):
        total = ElementReferentiel.objects.filter(formation=formation).aggregate(
            total=Sum("volume_horaire_prescrit")
        )["total"]
        return total or 0

    @staticmethod
    def ecart(formation):
        """Critère 5 — compare le total prescrit à la durée de la formation
        convertie en heures via le volume hebdomadaire de référence, résolu
        depuis la grille horaire active (US-PLAN-12, § 7, remboursement de
        D-33) — `referentiel` n'importe rien de `ressources` : voir
        `noyau.services.parametres.ResolveurVolumeHoraireReference` et
        docs/suivi/DECISIONS.md.
        """
        attendu = formation.duree_semaines * ResolveurVolumeHoraireReference.resoudre()
        total = ServiceReferentiel.total_volume(formation)
        depasse_seuil = False
        if attendu:
            ecart_pourcent = abs(total - attendu) / attendu * 100
            depasse_seuil = ecart_pourcent > settings.SEUIL_ECART_VOLUME_REFERENTIEL_POURCENT
        return {"total": total, "attendu": attendu, "depasse_seuil": depasse_seuil}

    @staticmethod
    def matieres_disponibles(formation):
        """Catalogue non archivé, pas encore rattaché à cette formation —
        évite E1 par construction sur la voie normale (§ 6.1), même si E1
        doit exister par ailleurs pour la voie directe.
        """
        deja_rattachees = ElementReferentiel.objects.filter(formation=formation).values_list(
            "matiere_id", flat=True
        )
        return ServiceMatiere.disponibles_pour_selection().exclude(pk__in=deja_rattachees)

    @staticmethod
    def rattacher(agissant, formation, matiere, donnees):
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        element = ElementReferentiel(
            formation=formation, matiere=matiere, **_donnees_coherentes(donnees)
        )
        valider_instance(element)
        try:
            with transaction.atomic():
                ServiceBase.creer(element, agissant)
                _journaliser(
                    agissant, TypeAction.CREATION_ELEMENT_GESTION, element,
                    valeur_apres=_capturer(element),
                )
        except IntegrityError as erreur:
            raise _erreur_doublon(formation, matiere) from erreur
        return element

    @staticmethod
    def modifier_volume(agissant, element, donnees):
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        avant = _capturer(element)
        for champ, valeur in _donnees_coherentes(donnees).items():
            setattr(element, champ, valeur)
        valider_instance(element)
        with transaction.atomic():
            ServiceBase.modifier(element, agissant)
            _journaliser(
                agissant, TypeAction.MODIFICATION_ELEMENT_GESTION, element,
                valeur_avant=avant, valeur_apres=_capturer(element),
            )
        return element

    @staticmethod
    def obtenir(pk):
        try:
            return ElementReferentiel.objects.select_related("formation", "matiere").get(pk=pk)
        except ElementReferentiel.DoesNotExist as erreur:
            raise ErreurIntrouvable(
                f"Élément de référentiel introuvable (identifiant {pk})."
            ) from erreur

    @staticmethod
    def retirer(agissant, element):
        """RG-07 : un prérequis bloque le retrait — contrôle explicite, pas
        `ProtectedError` : `Prerequis.element`/`element_prerequis` sont en
        `CASCADE`, pas en `PROTECT` (Prompt 10, § 6). La cascade reste un
        filet pour un retrait qui contournerait ce contrôle ; ce n'est
        jamais elle qui doit refuser.
        """
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        liens = ServicePrerequis.elements_lies(element)
        if liens:
            raise ErreurValidation(decrire_opposants(element, liens))
        try:
            with transaction.atomic():
                element.delete()
        except ProtectedError as erreur:
            raise ErreurValidation(decrire_opposants(element, erreur.protected_objects)) from erreur


def _donnees_coherentes(donnees):
    """§ 3.1 : `type_lieu_partage` doit être renseigné **si et seulement
    si** la catégorie est *lieu partagé* — imposé ici, pas seulement
    attendu du formulaire, sans quoi un appel direct au service (import,
    script) pourrait violer la cohérence.

    Chaîne vide normalisée en `None` **avant** le test de catégorie : sans
    ce premier pas, un `ChoiceField(required=False)` resté sur son option
    vide soumet `''`, qui n'est ni rejeté par `full_clean` (le champ est
    `blank=True`) ni par la contrainte en base (`''` n'est pas `NULL`) —
    un « lieu partagé » sans type réel s'enregistrait alors silencieusement.
    """
    donnees = dict(donnees)
    donnees.setdefault("coefficient", 1)
    donnees.setdefault("poids_formatif", 1)
    donnees.setdefault("poids_certificatif", 1)
    donnees["type_lieu_partage"] = donnees.get("type_lieu_partage") or None
    if donnees["categorie_lieu"] != CategorieLieu.LIEU_PARTAGE:
        donnees["type_lieu_partage"] = None
    elif donnees["type_lieu_partage"] is None:
        raise ErreurValidation(
            "Le type de lieu partagé est obligatoire pour la catégorie « Lieu partagé » : "
            "amphithéâtre, laboratoire ou salle spécialisée."
        )
    if donnees["poids_formatif"] == 0 and donnees["poids_certificatif"] == 0:
        raise ErreurValidation(
            "Le poids formatif et le poids certificatif ne peuvent pas être nuls "
            "tous les deux : indiquez au moins l'un des deux, selon le type "
            "d'évaluation du module pour cette formation."
        )
    return donnees


def _erreur_doublon(formation, matiere):
    """E1 — refuse le doublon et désigne le rattachement existant, avec son
    volume, pour que le message propose explicitement de le modifier plutôt
    que de simplement constater le refus (RG-06).
    """
    existant = ElementReferentiel.objects.filter(formation=formation, matiere=matiere).first()
    return ErreurValidation(
        f"« {matiere} » est déjà rattachée à cette formation, avec un volume de "
        f"{existant.volume_horaire_prescrit} h — modifiez le rattachement existant plutôt "
        "que d'en créer un nouveau."
    )


def _capturer(element):
    """US-REF-09, E1/E2 : liste blanche de champs (BNF-03), les quatre
    attributs cités par le critère — volume, coefficient, poids, catégorie
    de lieu. `coefficient`/`poids_formatif`/`poids_certificatif` sont des
    `Decimal` (`.claude/rules/modeles.md`) : convertis en `float`, le
    `JSONField` du journal ne sait pas sérialiser un `Decimal` nativement."""
    return {
        "volume_horaire_prescrit": element.volume_horaire_prescrit,
        "coefficient": float(element.coefficient),
        "poids_formatif": float(element.poids_formatif),
        "poids_certificatif": float(element.poids_certificatif),
        "categorie_lieu": element.categorie_lieu,
    }


def _journaliser(agissant, nature, element, *, valeur_avant=None, valeur_apres=None):
    identifiant = str(element)
    ServiceJournal.enregistrer_detaillee(
        DonneesEntreeJournal(
            type_action=nature,
            identifiant_saisi=identifiant,
            auteur=agissant,
            objet_type="element_referentiel",
            objet_identifiant=identifiant,
            valeur_avant=valeur_avant,
            valeur_apres=valeur_apres,
        )
    )
