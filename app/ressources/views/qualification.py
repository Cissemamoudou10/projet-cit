"""Vues de la matrice de qualification — orchestrent, ne décident rien.
Toute la logique métier vit dans ressources.services.qualification.
ServiceQualification.
"""

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse

from administration.habilitations import exige_habilitation
from noyau.exceptions import ErreurIntrouvable, ErreurValidation
from referentiel.services.formation import ServiceFormation
from referentiel.services.matiere import ServiceMatiere
from referentiel.services.referentiel import ServiceReferentiel
from ressources.services.instructeur import ServiceInstructeur
from ressources.services.qualification import ServiceQualification


def _instructeur_ou_404(pk):
    try:
        return ServiceInstructeur.obtenir(pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur


def _matiere_ou_404(pk):
    try:
        return ServiceMatiere.obtenir(pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur


def _formation_ou_404(pk):
    try:
        return ServiceFormation.obtenir(pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur


def _qualification_ou_404(pk):
    try:
        return ServiceQualification.obtenir(pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur


def _url_retour(origine, instructeur, matiere):
    if origine == "matiere":
        return reverse("ressources:qualifications_matiere", args=[matiere.pk])
    return reverse("ressources:qualifications_instructeur", args=[instructeur.pk])


@exige_habilitation(ServiceQualification.PERMISSION_LECTURE)
def vue_qualifications_instructeur(request, pk):
    instructeur = _instructeur_ou_404(pk)
    filtres = {
        "recherche": request.GET.get("recherche", ""),
        "etat": request.GET.get("etat", ""),
        "tri": request.GET.get("tri", ""),
    }
    page = ServiceQualification.matieres_avec_etat(
        request.user, instructeur, filtres, request.GET.get("page")
    )
    return render(
        request,
        "ressources/qualifications_instructeur.html",
        {
            "instructeur": instructeur,
            "page": page,
            "filtres": filtres,
            "url_liste": reverse("ressources:qualifications_instructeur", args=[instructeur.pk]),
        },
    )


@exige_habilitation(ServiceQualification.PERMISSION_LECTURE)
def vue_qualifications_matiere(request, pk):
    matiere = _matiere_ou_404(pk)
    instructeurs = ServiceQualification.instructeurs_avec_etat(request.user, matiere)
    return render(
        request,
        "ressources/qualifications_matiere.html",
        {"matiere": matiere, "instructeurs": instructeurs},
    )


@exige_habilitation(ServiceQualification.PERMISSION_ECRITURE)
def vue_ajouter_qualification(request, instructeur_pk, matiere_pk, origine):
    instructeur = _instructeur_ou_404(instructeur_pk)
    matiere = _matiere_ou_404(matiere_pk)
    if request.method == "POST":
        try:
            ServiceQualification.ajouter(request.user, instructeur, matiere)
        except ErreurValidation as erreur:
            messages.error(request, str(erreur))
        else:
            messages.success(request, f"« {matiere} » qualifiée pour {instructeur}.")
    return redirect(_url_retour(origine, instructeur, matiere))


@exige_habilitation(ServiceQualification.PERMISSION_ECRITURE)
def vue_confirmer_retrait_qualification(request, pk, origine):
    qualification = _qualification_ou_404(pk)
    url_retour = _url_retour(origine, qualification.instructeur, qualification.matiere)
    if request.method == "POST":
        try:
            ServiceQualification.retirer(request.user, qualification)
        except ErreurValidation as erreur:
            messages.error(request, str(erreur))
        else:
            messages.success(
                request,
                f"Qualification retirée : {qualification.instructeur} — {qualification.matiere}.",
            )
        return redirect(url_retour)
    return render(
        request,
        "ressources/qualification_confirmer_retrait.html",
        {
            "qualification": qualification,
            "seances_futures": ServiceQualification.seances_futures(qualification),
            "laisserait_non_couverte": ServiceQualification.laisserait_la_matiere_non_couverte(
                qualification
            ),
            "url_annuler": url_retour,
        },
    )


@exige_habilitation(ServiceQualification.PERMISSION_LECTURE)
def vue_couverture_qualifications(request, formation_pk):
    """A2 — § 7.4 : matières du référentiel de la formation et nombre
    d'instructeurs qualifiés pour chacune, en une seule requête annotée
    (`ServiceReferentiel.lister`)."""
    formation = _formation_ou_404(formation_pk)
    elements = ServiceReferentiel.lister(request.user, formation)
    non_couvertes = sum(1 for element in elements if element.nombre_instructeurs_qualifies == 0)
    return render(
        request,
        "ressources/couverture_qualifications.html",
        {"formation": formation, "elements": elements, "non_couvertes": non_couvertes},
    )
