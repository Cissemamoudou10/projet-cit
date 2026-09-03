"""Prérequis d'un référentiel — CU-P2-07, RG-09, RG-10.

Pas `ServiceGestion` : ni liste paginée, ni archivage, ni formulaire de
saisie classique (Prompt 10, préambule). Deux fonctions de graphe pures,
`trouver_chemin` et `ordre_topologique`, vivent au niveau du module plutôt
que comme méthodes de `ServicePrerequis` : § 3.2 bis exige qu'elles restent
appelables telles quelles depuis `planification` au sprint 3, sans aucun
contexte d'écran.

Un service ne connaît pas la requête HTTP — voir .claude/rules/services.md.
"""

from django.db import IntegrityError, models, transaction

from administration.habilitations import verifier_habilitation
from administration.models import TypeAction
from administration.services.journal import DonneesEntreeJournal, ServiceJournal
from noyau.exceptions import ErreurIntrouvable, ErreurValidation
from noyau.services.base import ServiceBase
from referentiel.models import ElementReferentiel, Prerequis

OBJET_TYPE = "prerequis"


def trouver_chemin(depart, arrivee, formation):
    """Parcours en profondeur depuis `depart`, cherchant `arrivee`, en
    suivant les liens « exige » déjà enregistrés dans le référentiel de
    `formation`. Retourne la chaîne complète (depart, ..., arrivee) si
    trouvée, sinon `None`. Pure : ne lève rien, n'écrit rien — condition de
    cycle, § 3.1 du Prompt 10 : ajouter *A exige B* crée un cycle si et
    seulement si A est déjà atteignable depuis B, donc l'appel se fait avec
    `depart=B, arrivee=A`.
    """
    return _parcourir(depart, arrivee, _exigences(formation), set())


def _exigences(formation):
    liens = Prerequis.objects.filter(element__formation=formation).select_related(
        "element_prerequis"
    )
    graphe = {}
    for lien in liens:
        graphe.setdefault(lien.element_id, []).append(lien.element_prerequis)
    return graphe


def _parcourir(sommet, cible, graphe, visites):
    if sommet.pk == cible.pk:
        return [sommet]
    if sommet.pk in visites:
        return None
    visites.add(sommet.pk)
    for voisin in graphe.get(sommet.pk, []):
        chemin = _parcourir(voisin, cible, graphe, visites)
        if chemin is not None:
            return [sommet, *chemin]
    return None


def ordre_topologique(formation):
    """Algorithme de Kahn sur le référentiel de `formation`. Départage
    déterministe par `matiere.intitule` (§ 3.2) : deux exécutions sur les
    mêmes données rendent le même ordre — l'unicité du catalogue
    (`uq_matiere_intitule`) garantit qu'aucune égalité ne peut se produire.
    """
    elements = list(
        ElementReferentiel.objects.filter(formation=formation).select_related("matiere")
    )
    par_id = {element.pk: element for element in elements}
    degre, dependants = _graphe_kahn(formation, par_id)
    disponibles = sorted(
        (element for element in elements if degre[element.pk] == 0),
        key=lambda element: element.matiere.intitule,
    )
    ordre = []
    while disponibles:
        courant = disponibles.pop(0)
        ordre.append(courant)
        for suivant_id in dependants.get(courant.pk, ()):
            degre[suivant_id] -= 1
            if degre[suivant_id] == 0:
                _inserer_trie(disponibles, par_id[suivant_id])
    return ordre


def _graphe_kahn(formation, par_id):
    degre = dict.fromkeys(par_id, 0)
    dependants = {}
    liens = Prerequis.objects.filter(element__formation=formation).values_list(
        "element_id", "element_prerequis_id"
    )
    for element_id, prerequis_id in liens:
        degre[element_id] += 1
        dependants.setdefault(prerequis_id, []).append(element_id)
    return degre, dependants


def _inserer_trie(disponibles, element):
    """Insertion triée — évite un tri complet à chaque itération, sans
    conséquence sur un graphe de quelques dizaines de sommets (point de
    conception de la fiche CU-P2-07)."""
    for index, autre in enumerate(disponibles):
        if element.matiere.intitule < autre.matiere.intitule:
            disponibles.insert(index, element)
            return
    disponibles.append(element)


def _decrire_cycle(chaine):
    parcours = " → ".join(str(element.matiere) for element in chaine)
    dernier_lien = f"« {chaine[-2].matiere} » exige « {chaine[-1].matiere} »"
    return (
        f"Impossible : ce prérequis fermerait un cycle ({parcours}). Retirez par exemple "
        f"le lien {dernier_lien} pour rompre la chaîne."
    )


def _verifier_couple(formation, element, element_prerequis):
    if element.pk == element_prerequis.pk:
        raise ErreurValidation(
            "Une matière ne peut pas être son propre prérequis : choisissez une autre matière."
        )
    if element.formation_id != formation.pk or element_prerequis.formation_id != formation.pk:
        raise ErreurValidation(
            "Le prérequis doit appartenir au même référentiel que la matière concernée "
            "(RG-09) : choisissez une matière déjà rattachée à cette formation."
        )


def _journaliser(agissant, nature, prerequis):
    identifiant = str(prerequis)
    ServiceJournal.enregistrer_detaillee(
        DonneesEntreeJournal(
            type_action=nature,
            identifiant_saisi=identifiant,
            auteur=agissant,
            objet_type=OBJET_TYPE,
            objet_identifiant=identifiant,
        )
    )


class ServicePrerequis:
    DOMAINE = "referentiel"
    PERMISSION_LECTURE = "noyau.referentiel_lecture"
    PERMISSION_ECRITURE = "noyau.referentiel_ecriture"

    @staticmethod
    def obtenir(pk):
        try:
            return Prerequis.objects.select_related(
                "element__matiere", "element_prerequis__matiere"
            ).get(pk=pk)
        except Prerequis.DoesNotExist as erreur:
            raise ErreurIntrouvable(f"Prérequis introuvable (identifiant {pk}).") from erreur

    @staticmethod
    def lister(agissant, formation):
        verifier_habilitation(agissant, ServicePrerequis.PERMISSION_LECTURE)
        return Prerequis.objects.filter(element__formation=formation).select_related(
            "element__matiere", "element_prerequis__matiere"
        )

    @staticmethod
    def elements_disponibles(element):
        """Dropdown d'ajout, § 7 : même référentiel, hors la matière
        elle-même, hors celles déjà déclarées comme prérequis direct."""
        deja = element.prerequis_directs.values_list("element_prerequis_id", flat=True)
        return (
            ElementReferentiel.objects.filter(formation=element.formation)
            .exclude(pk=element.pk)
            .exclude(pk__in=deja)
            .select_related("matiere")
        )

    @staticmethod
    def elements_lies(element):
        """RG-07 : éléments impliqués dans un prérequis touchant `element`,
        dans un sens ou l'autre. Appelé par `ServiceReferentiel.retirer`
        avant toute suppression — la cascade posée en base n'est qu'un
        filet, ce contrôle est la règle (Prompt 10, § 6).
        """
        liens = Prerequis.objects.filter(
            models.Q(element=element) | models.Q(element_prerequis=element)
        ).select_related("element__matiere", "element_prerequis__matiere")
        return [
            lien.element_prerequis if lien.element_id == element.pk else lien.element
            for lien in liens
        ]

    @staticmethod
    def ajouter(agissant, formation, element, element_prerequis):
        verifier_habilitation(agissant, ServicePrerequis.PERMISSION_ECRITURE)
        _verifier_couple(formation, element, element_prerequis)
        chemin = trouver_chemin(element_prerequis, element, formation)
        if chemin is not None:
            raise ErreurValidation(_decrire_cycle([element, *chemin]))
        prerequis = Prerequis(element=element, element_prerequis=element_prerequis)
        try:
            with transaction.atomic():
                ServiceBase.creer(prerequis, agissant)
                _journaliser(agissant, TypeAction.CREATION_ELEMENT_GESTION, prerequis)
        except IntegrityError as erreur:
            raise ErreurValidation(
                f"« {element_prerequis.matiere} » est déjà déclarée prérequis de "
                f"« {element.matiere} »."
            ) from erreur
        return prerequis

    @staticmethod
    def retirer(agissant, prerequis):
        """A1 : aucune vérification supplémentaire — une suppression ne
        peut pas créer de cycle."""
        verifier_habilitation(agissant, ServicePrerequis.PERMISSION_ECRITURE)
        with transaction.atomic():
            _journaliser(agissant, TypeAction.SUPPRESSION_ELEMENT_GESTION, prerequis)
            prerequis.delete()
