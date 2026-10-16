"""Écran de la progression réalisée hebdomadaire — US-SUI-06 (prompt 45,
Temps 2). Orchestre, ne décide rien (`.claude/rules/vues.md`) : tout le
calcul et la production du PDF vivent dans `ServiceSuivi`.
"""

import datetime

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from administration.habilitations import exige_habilitation
from noyau.exceptions import ErreurMetier
from planification.models import EditionProgression, ProgrammeHebdomadaire
from planification.services.suivi import PERMISSION_LECTURE, ServiceSuivi

PERMISSION_ECRITURE = "noyau.programme_ecriture"


def _retour_progression(programme):
    return redirect(reverse("planification:progression_realisee", args=[programme.pk]))


@exige_habilitation(PERMISSION_LECTURE)
def vue_progression(request, pk):
    programme = get_object_or_404(ProgrammeHebdomadaire, pk=pk)
    editions = programme.editions_progression.order_by("-cree_le")
    return render(
        request,
        "planification/progression_realisee.html",
        {"programme": programme, "editions": editions},
    )


@require_POST
@exige_habilitation(PERMISSION_ECRITURE)
def editer_progression(request, pk):
    programme = get_object_or_404(ProgrammeHebdomadaire, pk=pk)
    try:
        ServiceSuivi.editer_progression(request.user, programme)
    except ErreurMetier as erreur:
        messages.error(request, str(erreur))
    else:
        messages.success(request, "Progression réalisée éditée.")
    return _retour_progression(programme)


@require_POST
@exige_habilitation(PERMISSION_ECRITURE)
def signer_progression(request, edition_pk):
    edition = get_object_or_404(
        EditionProgression.objects.select_related("programme"), pk=edition_pk
    )
    date_signature_brute = request.POST.get("date_signature", "")
    try:
        date_signature = datetime.date.fromisoformat(date_signature_brute)
    except ValueError:
        date_signature = None
    try:
        ServiceSuivi.enregistrer_signature_progression(
            request.user, edition, date_signature, request.POST.get("signataire", "")
        )
    except ErreurMetier as erreur:
        messages.error(request, str(erreur))
    else:
        messages.success(request, "Signature enregistrée.")
    return _retour_progression(edition.programme)


@exige_habilitation(PERMISSION_LECTURE)
def telecharger_progression(request, edition_pk):
    edition = get_object_or_404(
        EditionProgression.objects.select_related("programme"), pk=edition_pk
    )
    pdf = ServiceSuivi.produire_pdf_progression(request.user, edition)
    reponse = HttpResponse(pdf, content_type="application/pdf")
    nom_fichier = f"progression-{edition.programme.lundi_de_semaine.isoformat()}-{edition.pk}.pdf"
    reponse["Content-Disposition"] = f'attachment; filename="{nom_fichier}"'
    return reponse
