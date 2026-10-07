"""Écrans de modification d'une séance, de suppression, de déverrouillage et
d'annulation de validation (US-PLAN-05, prompt 41 § 1 et F).

Chaque écriture appelle la porte unique (`ServiceEcritureSeance`) ou le moteur
(`ServiceCircuitProgramme`) ; un refus s'affiche par message, rien n'est écrit.
"""

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from administration.habilitations import exige_habilitation
from noyau.exceptions import ErreurMetier
from planification.forms_seance import FormulaireAjoutSeance, FormulaireSeance
from planification.models import ProgrammeHebdomadaire, Seance
from planification.services.circuit import ServiceCircuitProgramme
from planification.services.contraintes import Candidate
from planification.services.ecriture import ServiceEcritureSeance
from planification.services.modification import Avenantage

PERMISSION_ECRITURE = "noyau.programme_ecriture"


def _retour_consultation(programme):
    url = reverse("planification:consultation_programme")
    return redirect(f"{url}?semaine={programme.lundi_de_semaine.isoformat()}")


def _url_modification(seance):
    return reverse("planification:modifier_seance", args=[seance.pk])


def _valeurs_initiales(seance):
    debut = timezone.localtime(seance.debut)
    fin = timezone.localtime(seance.fin)
    return {
        "element_referentiel": seance.element_referentiel_id,
        "instructeur": seance.instructeur_id,
        "lieu": seance.lieu_id,
        "date_seance": debut.date(),
        "heure_debut": debut.time(),
        "heure_fin": fin.time(),
    }


def _appliquer(request, seance, formulaire):
    demande = formulaire.motif_et_nature_avenant()
    avenant = Avenantage(*demande) if demande else None
    try:
        ServiceEcritureSeance.modifier_seance(
            request.user,
            seance,
            formulaire.changements(),
            avenant=avenant,
            confirmee=formulaire.cleaned_data["confirmee"],
        )
    except ErreurMetier as erreur:
        messages.error(request, str(erreur))
        return redirect(_url_modification(seance))
    messages.success(request, "Séance modifiée et verrouillée.")
    return _retour_consultation(seance.programme)


@exige_habilitation(PERMISSION_ECRITURE)
def modifier_seance(request, pk):
    seance = get_object_or_404(Seance.objects.select_related("programme"), pk=pk)
    if request.method == "POST":
        formulaire = FormulaireSeance(request.POST)
        if formulaire.is_valid():
            return _appliquer(request, seance, formulaire)
    else:
        formulaire = FormulaireSeance(initial=_valeurs_initiales(seance))
    return render(
        request,
        "planification/modifier_seance.html",
        {"seance": seance, "programme": seance.programme, "formulaire": formulaire},
    )


def _valeurs_initiales_ajout(request):
    valeurs = {}
    if request.GET.get("brigade"):
        valeurs["brigade"] = request.GET["brigade"]
    if request.GET.get("date"):
        valeurs["date_seance"] = request.GET["date"]
    if request.GET.get("heure_debut"):
        valeurs["heure_debut"] = request.GET["heure_debut"]
    if request.GET.get("heure_fin"):
        valeurs["heure_fin"] = request.GET["heure_fin"]
    return valeurs


def _appliquer_ajout(request, programme, formulaire):
    donnees = formulaire.cleaned_data
    candidate = Candidate(
        brigade=donnees["brigade"],
        element_referentiel=donnees["element_referentiel"],
        instructeur=donnees["instructeur"],
        lieu=donnees.get("lieu"),
        debut=donnees["debut_instant"],
        fin=donnees["fin_instant"],
    )
    demande = formulaire.motif_et_nature_avenant()
    avenant = Avenantage(*demande) if demande else None
    try:
        ServiceEcritureSeance.creer_seance(request.user, programme, [candidate], avenant=avenant)
    except ErreurMetier as erreur:
        messages.error(request, str(erreur))
        url = reverse("planification:ajouter_seance", args=[programme.pk])
        return redirect(url)
    messages.success(request, "Séance ajoutée et verrouillée.")
    return _retour_consultation(programme)


@exige_habilitation(PERMISSION_ECRITURE)
def ajouter_seance(request, pk):
    programme = get_object_or_404(ProgrammeHebdomadaire, pk=pk)
    if request.method == "POST":
        formulaire = FormulaireAjoutSeance(request.POST)
        if formulaire.is_valid():
            return _appliquer_ajout(request, programme, formulaire)
    else:
        formulaire = FormulaireAjoutSeance(initial=_valeurs_initiales_ajout(request))
    return render(
        request,
        "planification/ajouter_seance.html",
        {"programme": programme, "formulaire": formulaire},
    )


@require_POST
@exige_habilitation(PERMISSION_ECRITURE)
def supprimer_seance(request, pk):
    seance = get_object_or_404(Seance.objects.select_related("programme"), pk=pk)
    programme = seance.programme
    try:
        ServiceEcritureSeance.supprimer_seance(request.user, seance)
    except ErreurMetier as erreur:
        messages.error(request, str(erreur))
    else:
        messages.success(request, "Séance supprimée.")
    return _retour_consultation(programme)


@require_POST
@exige_habilitation(PERMISSION_ECRITURE)
def deverrouiller_seance(request, pk):
    seance = get_object_or_404(Seance.objects.select_related("programme"), pk=pk)
    programme = seance.programme
    try:
        ServiceEcritureSeance.deverrouiller_seance(request.user, seance)
    except ErreurMetier as erreur:
        messages.error(request, str(erreur))
    else:
        messages.success(request, "Séance déverrouillée : la régénération pourra la remplacer.")
    return _retour_consultation(programme)


@require_POST
@exige_habilitation(PERMISSION_ECRITURE)
def annuler_validation(request, pk):
    programme = get_object_or_404(ProgrammeHebdomadaire, pk=pk)
    motif = request.POST.get("motif", "")
    confirmee = request.POST.get("confirmee") == "on"
    try:
        ServiceCircuitProgramme.annuler_validation(request.user, programme, motif, confirmee)
    except ErreurMetier as erreur:
        messages.error(request, str(erreur))
    else:
        messages.success(request, "Validation annulée : le programme est de nouveau en brouillon.")
    return _retour_consultation(programme)
