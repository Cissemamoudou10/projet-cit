"""Écran de duplication d'un programme hebdomadaire — US-PLAN-11 (prompt
48). Orchestre, ne décide rien (`.claude/rules/vues.md`) : tout le calcul
vit dans `ServiceDuplication`.
"""

import datetime

from django.contrib import messages
from django.shortcuts import render

from administration.habilitations import exige_habilitation
from noyau.exceptions import ErreurHabilitation, ErreurValidation
from planification.exceptions import TransitionProgrammeRefusee
from planification.forms_duplication import FormulaireDuplication
from planification.models import ProgrammeHebdomadaire
from planification.services.duplication import PERMISSION_ECRITURE, ServiceDuplication

GABARIT_LANCEMENT = "planification/lancement_duplication.html"


def _lundi(date_quelconque):
    return date_quelconque - datetime.timedelta(days=date_quelconque.weekday())


@exige_habilitation(PERMISSION_ECRITURE)
def vue_lancement_duplication(request):
    if request.method == "POST":
        return _traiter_duplication(request)
    return render(request, GABARIT_LANCEMENT, {"formulaire": FormulaireDuplication()})


def _programme_source_ou_erreur(request, lundi_source, formulaire):
    programme = ProgrammeHebdomadaire.objects.filter(lundi_de_semaine=lundi_source).first()
    if programme is None:
        messages.error(request, f"Aucun programme pour la semaine du {lundi_source:%d/%m/%Y}.")
        return None, render(request, GABARIT_LANCEMENT, {"formulaire": formulaire})
    return programme, None


def _traiter_duplication(request):
    formulaire = FormulaireDuplication(request.POST)
    if not formulaire.is_valid():
        return render(request, GABARIT_LANCEMENT, {"formulaire": formulaire})
    lundi_source = _lundi(formulaire.cleaned_data["semaine_source"])
    lundi_cible = _lundi(formulaire.cleaned_data["semaine_cible"])
    programme_source, reponse_erreur = _programme_source_ou_erreur(request, lundi_source, formulaire)
    if programme_source is None:
        return reponse_erreur
    brigades = list(formulaire.cleaned_data["brigades"])
    try:
        compte_rendu = ServiceDuplication.dupliquer(
            request.user, programme_source, lundi_cible, brigades
        )
    except (ErreurValidation, ErreurHabilitation, TransitionProgrammeRefusee) as erreur:
        messages.error(request, str(erreur))
        return render(request, GABARIT_LANCEMENT, {"formulaire": formulaire})
    return render(
        request, "planification/compte_rendu_duplication.html", {"compte_rendu": compte_rendu}
    )
