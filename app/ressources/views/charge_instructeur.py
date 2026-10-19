"""Écran de la charge d'enseignement des instructeurs — US-INS-04 (prompt
48). Lecture seule : orchestre, ne décide rien (`.claude/rules/vues.md`) —
tout le calcul vit dans `ressources.selectors_charge`.
"""

import datetime

from django.http import Http404
from django.shortcuts import render
from django.utils import timezone

from administration.habilitations import exige_habilitation
from noyau.exceptions import ErreurIntrouvable
from ressources.navigation import onglets_ressources
from ressources.selectors_charge import charge_d_un_instructeur, charge_instructeurs
from ressources.services.instructeur import ServiceInstructeur

PERMISSION_LECTURE = ServiceInstructeur.PERMISSION_LECTURE


def _date_filtre(request, nom):
    valeur = request.GET.get(nom)
    if not valeur:
        return None
    try:
        return datetime.date.fromisoformat(valeur)
    except ValueError:
        return None


def _periode(request):
    """Par défaut, les sept derniers jours jusqu'à aujourd'hui — l'écran
    affiche quelque chose dès l'ouverture, sans attendre un filtre."""
    aujourd_hui = timezone.localdate()
    debut = _date_filtre(request, "debut") or (aujourd_hui - datetime.timedelta(days=7))
    fin = _date_filtre(request, "fin") or aujourd_hui
    debut_instant = timezone.make_aware(datetime.datetime.combine(debut, datetime.time.min))
    fin_instant = timezone.make_aware(datetime.datetime.combine(fin, datetime.time.max))
    return debut, fin, debut_instant, fin_instant


@exige_habilitation(PERMISSION_LECTURE)
def vue_charge_instructeurs(request):
    debut, fin, debut_instant, fin_instant = _periode(request)
    lignes = charge_instructeurs(debut_instant, fin_instant)
    if request.GET.get("tri") == "charge":
        lignes = sorted(lignes, key=lambda ligne: ligne.heures_enseignement, reverse=True)
    onglets, onglet_actif = onglets_ressources(request.user, "charge-instructeurs")
    return render(
        request,
        "ressources/charge_instructeurs.html",
        {
            "lignes": lignes,
            "periode_debut": debut,
            "periode_fin": fin,
            "onglets": onglets,
            "onglet_actif": onglet_actif,
        },
    )


def _instructeur_ou_404(pk):
    try:
        return ServiceInstructeur.obtenir(pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur


@exige_habilitation(PERMISSION_LECTURE)
def vue_detail_charge_instructeur(request, pk):
    instructeur = _instructeur_ou_404(pk)
    debut, fin, debut_instant, fin_instant = _periode(request)
    ligne = charge_d_un_instructeur(instructeur, debut_instant, fin_instant)
    return render(
        request,
        "ressources/charge_instructeur_detail.html",
        {"ligne": ligne, "periode_debut": debut, "periode_fin": fin},
    )
