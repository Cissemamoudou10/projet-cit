"""Vues des prérequis d'un référentiel — CU-P2-07. Orchestrent, ne décident
rien : toute la logique métier vit dans referentiel.services.prerequis.
"""

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from administration.habilitations import exige_habilitation
from administration.services.journal import ServiceJournal
from noyau.exceptions import ErreurIntrouvable, ErreurValidation
from referentiel.forms import FormulairePrerequis
from referentiel.services.formation import ServiceFormation
from referentiel.services.prerequis import ServicePrerequis, ordre_topologique
from referentiel.services.referentiel import ServiceReferentiel


def _formation_ou_404(pk):
    try:
        return ServiceFormation.obtenir(pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur


def _element_ou_404(pk):
    try:
        return ServiceReferentiel.obtenir(pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur


def _prerequis_ou_404(pk):
    try:
        return ServicePrerequis.obtenir(pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur


def preparer_donnees_prerequis(request, formation):
    """Reprise par `consultation.vue_consultation_formation` (US-REF-07) :
    même composition elements/ordre, sans réécrire `_annoter` (Prompt 11, § 2.1).
    """
    elements = list(ServiceReferentiel.lister(request.user, formation).select_related("matiere"))
    suffisant = len(elements) >= 2
    liens = list(ServicePrerequis.lister(request.user, formation)) if suffisant else []
    _annoter(elements, liens)
    return {
        "elements": elements,
        "elements_suffisants": suffisant,
        "ordre": ordre_topologique(formation) if suffisant else [],
        "liens": liens,
    }


def _rendre_page(request, formation):
    contexte = preparer_donnees_prerequis(request, formation)
    contexte["formation"] = formation
    contexte["url_composer_referentiel"] = reverse(
        "referentiel:referentiel_formation", args=[formation.pk]
    )
    contexte["historique"] = ServiceJournal.historique_plusieurs("prerequis", contexte["liens"])
    return render(request, "referentiel/prerequis_formation.html", contexte)


def _annoter(elements, liens):
    """Pas de requête par ligne (.claude/rules/python.md) : jetons et options
    du menu déroulant calculés depuis les listes déjà chargées, jamais
    depuis `element.prerequis_directs.all` dans le gabarit.
    """
    par_element = {element.pk: [] for element in elements}
    for lien in liens:
        par_element[lien.element_id].append(lien)
    for element in elements:
        exclus = {lien.element_prerequis_id for lien in par_element[element.pk]} | {element.pk}
        element.prerequis_directs_affiches = par_element[element.pk]
        element.elements_disponibles_affiches = [e for e in elements if e.pk not in exclus]


@exige_habilitation(ServicePrerequis.PERMISSION_LECTURE)
def vue_prerequis_formation(request, formation_pk):
    formation = _formation_ou_404(formation_pk)
    return _rendre_page(request, formation)


@require_POST
@exige_habilitation(ServicePrerequis.PERMISSION_ECRITURE)
def vue_ajouter_prerequis(request, formation_pk, element_pk):
    formation = _formation_ou_404(formation_pk)
    element = _element_ou_404(element_pk)
    formulaire = FormulairePrerequis(
        request.POST, elements_disponibles=ServicePrerequis.elements_disponibles(element)
    )
    if formulaire.is_valid():
        element_prerequis = formulaire.cleaned_data["element_prerequis"]
        try:
            ServicePrerequis.ajouter(request.user, formation, element, element_prerequis)
        except ErreurValidation as erreur:
            messages.error(request, str(erreur))
        else:
            messages.success(
                request,
                f"« {element_prerequis.matiere} » ajoutée aux prérequis de « {element.matiere} ».",
            )
    else:
        messages.error(request, "Prérequis non valide.")
    return redirect("referentiel:prerequis_formation", formation.pk)


@exige_habilitation(ServicePrerequis.PERMISSION_ECRITURE)
def vue_confirmer_suppression_prerequis(request, formation_pk, prerequis_pk):
    formation = _formation_ou_404(formation_pk)
    prerequis = _prerequis_ou_404(prerequis_pk)
    if request.method == "POST":
        ServicePrerequis.retirer(request.user, prerequis)
        messages.success(request, "Prérequis retiré.")
        return redirect("referentiel:prerequis_formation", formation.pk)
    return render(
        request,
        "referentiel/prerequis_confirmer_suppression.html",
        {
            "prerequis": prerequis,
            "url_annuler": reverse("referentiel:prerequis_formation", args=[formation.pk]),
        },
    )
