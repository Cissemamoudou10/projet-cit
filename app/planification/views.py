"""Vues de génération et de consultation du programme hebdomadaire —
CU-P5-01, Prompt 31, § 9. Orchestrent, ne décident rien : toute la logique
vit dans `planification.services.generation.ServiceGeneration`, toute
lecture complexe dans `planification.selectors` (une vue n'importe jamais
un modèle directement, .claude/rules/vues.md).
"""

import datetime

from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from administration.habilitations import exige_habilitation
from noyau.exceptions import ErreurHabilitation, ErreurValidation
from planification.exceptions import AucuneGrilleActive, SemaineEntierementBloquee
from planification.forms import FormulaireLancementGeneration
from planification.selectors import (
    apercu_regeneration,
    brigades_pour_filtre,
    grille_active_avec_creneaux,
    grille_consultation,
    programme_de_la_semaine,
)
from planification.services.generation import PERMISSION_ECRITURE, ServiceGeneration

PERMISSION_LECTURE = "noyau.programme_lecture"


@exige_habilitation(PERMISSION_ECRITURE)
def vue_lancement_generation(request):
    grille, _creneaux = grille_active_avec_creneaux()
    if request.method == "POST":
        return _traiter_lancement(request, grille)
    formulaire = FormulaireLancementGeneration()
    return render(
        request,
        "planification/lancement_generation.html",
        {"formulaire": formulaire, "grille_active": grille},
    )


def _traiter_lancement(request, grille):
    formulaire = FormulaireLancementGeneration(request.POST)
    if not formulaire.is_valid():
        return render(
            request,
            "planification/lancement_generation.html",
            {"formulaire": formulaire, "grille_active": grille},
        )
    lundi = formulaire.lundi_de_semaine()
    brigades = list(formulaire.cleaned_data["brigades"])
    if not formulaire.cleaned_data["confirme"]:
        impact = apercu_regeneration(lundi, brigades)
        if impact:
            return render(
                request,
                "planification/confirmer_regeneration.html",
                {"formulaire": formulaire, "lundi": lundi, "impact": impact},
            )
    return _generer_et_afficher(request, lundi, brigades)


def _generer_et_afficher(request, lundi, brigades):
    try:
        compte_rendu = ServiceGeneration.generer(request.user, lundi, brigades)
    except (AucuneGrilleActive, SemaineEntierementBloquee, ErreurValidation, ErreurHabilitation) as erreur:
        messages.error(request, str(erreur))
        return redirect(reverse("planification:lancement_generation"))
    return render(
        request, "planification/compte_rendu_generation.html", {"compte_rendu": compte_rendu}
    )


@exige_habilitation(PERMISSION_LECTURE)
def vue_consultation_programme(request):
    grille, creneaux = grille_active_avec_creneaux()
    semaine_texte = request.GET.get("semaine")
    semaine = datetime.date.fromisoformat(semaine_texte) if semaine_texte else timezone.localdate()
    lundi = semaine - datetime.timedelta(days=semaine.weekday())
    programme = programme_de_la_semaine(lundi)

    brigades = brigades_pour_filtre(
        brigade_pk=request.GET.get("brigade"), session_pk=request.GET.get("session")
    )
    lignes = grille_consultation(programme, creneaux, brigades) if programme else []
    return render(
        request,
        "planification/consultation_programme.html",
        {
            "programme": programme,
            "lundi": lundi,
            "creneaux": creneaux,
            "grille_active": grille,
            "lignes": lignes,
            "toutes_brigades": brigades_pour_filtre(),
        },
    )
