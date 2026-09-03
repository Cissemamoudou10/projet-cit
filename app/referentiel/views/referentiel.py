"""Vues de composition du référentiel d'une formation — CU-P2-04, CU-P2-05.
Orchestrent, ne décident rien : toute la logique métier vit dans
referentiel.services.referentiel.ServiceReferentiel.
"""

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from administration.habilitations import exige_habilitation
from noyau.exceptions import ErreurIntrouvable, ErreurValidation
from referentiel.forms import (
    FormulaireElementReferentiel,
    FormulaireMatiere,
    FormulaireRattachementMatiere,
)
from referentiel.services.formation import ServiceFormation
from referentiel.services.matiere import ServiceMatiere
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


def _rendre_page(request, formation, *, formulaire_rattachement=None):
    disponibles = ServiceReferentiel.matieres_disponibles(formation)
    if formulaire_rattachement is None:
        formulaire_rattachement = FormulaireRattachementMatiere(
            matieres_disponibles=disponibles,
            initial={"matiere": request.GET.get("matiere")},
        )
    contexte = {
        "formation": formation,
        "elements": ServiceReferentiel.lister(request.user, formation),
        "ecart": ServiceReferentiel.ecart(formation),
        "formulaire_rattachement": formulaire_rattachement,
        "categories_lieu": ServiceReferentiel.categories_lieu(),
        "types_lieu_partage": ServiceReferentiel.types_lieu_partage(),
        "url_rattacher": reverse("referentiel:rattacher_matiere", args=[formation.pk]),
        "url_creer_matiere": reverse(
            "referentiel:creer_matiere_depuis_referentiel", args=[formation.pk]
        ),
    }
    return render(request, "referentiel/formation_referentiel.html", contexte)


@exige_habilitation(ServiceReferentiel.PERMISSION_LECTURE)
def vue_referentiel_formation(request, formation_pk):
    formation = _formation_ou_404(formation_pk)
    return _rendre_page(request, formation)


@require_POST
@exige_habilitation(ServiceReferentiel.PERMISSION_ECRITURE)
def vue_rattacher_matiere(request, formation_pk):
    formation = _formation_ou_404(formation_pk)
    disponibles = ServiceReferentiel.matieres_disponibles(formation)
    formulaire = FormulaireRattachementMatiere(request.POST, matieres_disponibles=disponibles)
    if formulaire.is_valid():
        donnees = formulaire.cleaned_data
        matiere = donnees.pop("matiere")
        try:
            ServiceReferentiel.rattacher(request.user, formation, matiere, donnees)
        except ErreurValidation as erreur:
            messages.error(request, str(erreur))
        else:
            messages.success(request, f"« {matiere} » rattachée au référentiel.")
            return redirect("referentiel:referentiel_formation", formation.pk)
    return _rendre_page(request, formation, formulaire_rattachement=formulaire)


@exige_habilitation(ServiceReferentiel.PERMISSION_ECRITURE)
def vue_creer_matiere_depuis_referentiel(request, formation_pk):
    """A1 : la matière est créée sans quitter l'écran de composition — un
    aller-retour par un écran de dialogue dédié (§ 3.32 : un `<dialog>` ne
    se centre en superposition, sans script, que sur un écran qui ne
    contient rien d'autre que lui), en réutilisant le service de création
    de matière d'US-REF-02, jamais réécrit (Prompt 08, § 3.4).
    """
    formation = _formation_ou_404(formation_pk)
    if request.method == "POST":
        formulaire = FormulaireMatiere(request.POST)
        if formulaire.is_valid():
            try:
                matiere = ServiceMatiere.creer(request.user, formulaire.cleaned_data)
            except ErreurValidation as erreur:
                messages.error(request, str(erreur))
            else:
                messages.success(request, f"« {matiere} » créée. Renseignez son rattachement.")
                url = reverse("referentiel:referentiel_formation", args=[formation.pk])
                return redirect(f"{url}?matiere={matiere.pk}")
    else:
        formulaire = FormulaireMatiere()
    return render(
        request,
        "referentiel/matiere_creer_depuis_referentiel.html",
        {
            "formation": formation,
            "form": formulaire,
            "url_annuler": reverse("referentiel:referentiel_formation", args=[formation.pk]),
        },
    )


@require_POST
@exige_habilitation(ServiceReferentiel.PERMISSION_ECRITURE)
def vue_modifier_element_referentiel(request, formation_pk, element_pk):
    formation = _formation_ou_404(formation_pk)
    element = _element_ou_404(element_pk)
    formulaire = FormulaireElementReferentiel(request.POST)
    if formulaire.is_valid():
        try:
            ServiceReferentiel.modifier_volume(request.user, element, formulaire.cleaned_data)
        except ErreurValidation as erreur:
            messages.error(request, str(erreur))
        else:
            messages.success(request, f"« {element.matiere} » modifiée.")
    else:
        messages.error(request, "Volume ou catégorie de lieu non valide.")
    return redirect("referentiel:referentiel_formation", formation.pk)


@exige_habilitation(ServiceReferentiel.PERMISSION_ECRITURE)
def vue_confirmer_retrait_element_referentiel(request, formation_pk, element_pk):
    formation = _formation_ou_404(formation_pk)
    element = _element_ou_404(element_pk)
    if request.method == "POST":
        try:
            ServiceReferentiel.retirer(request.user, element)
        except ErreurValidation as erreur:
            messages.error(request, str(erreur))
        else:
            messages.success(request, f"« {element.matiere} » retirée du référentiel.")
        return redirect("referentiel:referentiel_formation", formation.pk)
    return render(
        request,
        "referentiel/element_referentiel_confirmer_retrait.html",
        {
            "element": element,
            "url_annuler": reverse("referentiel:referentiel_formation", args=[formation.pk]),
        },
    )
