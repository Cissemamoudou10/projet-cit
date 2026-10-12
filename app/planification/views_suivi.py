"""Écran de la non-exécution d'une séance — US-SUI-05 (prompt 44, Temps 2).

Deux actions seulement, posées directement sur la grille de consultation du
programme (`consultation_programme.html`) : aucun écran dédié, le motif
tient dans une zone de texte courte, sur le modèle du rejet et de
l'annulation de validation du circuit (`views_circuit.py`).
"""

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from administration.habilitations import exige_habilitation
from noyau.exceptions import ErreurMetier
from planification.models import LigneProgramme
from planification.services.suivi import ServiceSuivi

PERMISSION_ECRITURE = "noyau.programme_ecriture"


def _ligne(pk):
    return get_object_or_404(
        LigneProgramme.objects.select_related("seance__programme", "brigade"), pk=pk
    )


def _retour_consultation(programme):
    url = reverse("planification:consultation_programme")
    return redirect(f"{url}?semaine={programme.lundi_de_semaine.isoformat()}")


@require_POST
@exige_habilitation(PERMISSION_ECRITURE)
def declarer_non_execution(request, pk):
    ligne = _ligne(pk)
    motif = request.POST.get("motif", "")
    try:
        ServiceSuivi.declarer_non_execution(request.user, ligne, motif)
    except ErreurMetier as erreur:
        messages.error(request, str(erreur))
    else:
        messages.success(request, "Non-exécution déclarée : le volume réalisé est retranché.")
    return _retour_consultation(ligne.seance.programme)


@require_POST
@exige_habilitation(PERMISSION_ECRITURE)
def annuler_non_execution(request, pk):
    ligne = _ligne(pk)
    try:
        ServiceSuivi.annuler_non_execution(request.user, ligne)
    except ErreurMetier as erreur:
        messages.error(request, str(erreur))
    else:
        messages.success(request, "Déclaration de non-exécution annulée.")
    return _retour_consultation(ligne.seance.programme)
