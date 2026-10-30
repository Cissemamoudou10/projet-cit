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
from planification.circuit_affichage import contexte_circuit
from planification.exceptions import (
    AucuneGrilleActive,
    SemaineEntierementBloquee,
    TransitionProgrammeRefusee,
)
from planification.forms import FormulaireLancementGeneration, FormulaireSemaine
from planification.selectors import (
    apercu_regeneration,
    brigades_groupees_par_session,
    brigades_pour_filtre,
    grille_active_avec_creneaux,
    grille_consultation,
    jours_disponibles,
    programme_de_la_semaine,
)
from planification.selectors_circuit import (
    brigades_et_nombre_seances,
    historique_du_programme,
    peut_supprimer_brouillon,
)
from planification.selectors_ecart_volume import ecarts_volume_horaire
from planification.services.generation import PERMISSION_ECRITURE, ServiceGeneration

PERMISSION_LECTURE = "noyau.programme_lecture"


def _lundi_depuis_parametre(valeur):
    try:
        date = datetime.date.fromisoformat(valeur) if valeur else timezone.localdate()
    except ValueError:
        date = timezone.localdate()
    return date - datetime.timedelta(days=date.weekday())


@exige_habilitation(PERMISSION_ECRITURE)
def vue_lancement_generation(request):
    grille, _creneaux = grille_active_avec_creneaux()
    if request.method == "POST":
        return _traiter_lancement(request, grille)
    lundi = _lundi_depuis_parametre(request.GET.get("semaine"))
    formulaire = FormulaireLancementGeneration(initial={"semaine": lundi})
    return _afficher_lancement(request, grille, lundi, formulaire, set())


def _afficher_lancement(request, grille, lundi, formulaire, brigades_selectionnees):
    return render(
        request,
        "planification/lancement_generation.html",
        {
            "formulaire_semaine": FormulaireSemaine(initial={"semaine": lundi}),
            "formulaire": formulaire,
            "lundi": lundi,
            "grille_active": grille,
            "groupes_brigades": brigades_groupees_par_session(lundi),
            "brigades_selectionnees": brigades_selectionnees,
            "programme": programme_de_la_semaine(lundi),
            "motif_indisponible": ServiceGeneration.motif_indisponible(lundi),
        },
    )


def _redirection_lancement(lundi):
    url = reverse("planification:lancement_generation")
    return redirect(f"{url}?semaine={lundi.isoformat()}")


def _traiter_lancement(request, grille):
    formulaire = FormulaireLancementGeneration(request.POST)
    lundi = _lundi_depuis_parametre(request.POST.get("semaine"))
    if not formulaire.is_valid():
        selection = set(request.POST.getlist("brigades"))
        return _afficher_lancement(request, grille, lundi, formulaire, selection)
    motif = ServiceGeneration.motif_indisponible(lundi)
    if motif:
        messages.error(request, motif)
        return _redirection_lancement(lundi)
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
    except (
        AucuneGrilleActive,
        SemaineEntierementBloquee,
        ErreurValidation,
        ErreurHabilitation,
        TransitionProgrammeRefusee,
    ) as erreur:
        messages.error(request, str(erreur))
        return _redirection_lancement(lundi)
    return render(
        request, "planification/compte_rendu_generation.html", {"compte_rendu": compte_rendu}
    )


JOURS_OFFSET = {
    "lundi": 0,
    "mardi": 1,
    "mercredi": 2,
    "jeudi": 3,
    "vendredi": 4,
    "samedi": 5,
    "dimanche": 6,
}


def _onglets_jours(jours, jour_actif, lundi):
    """Un onglet par jour de la grille active (§ 9 : la semaine tient en
    largeur un jour à la fois, retour utilisateur du 17/09) — jamais les
    sept jours dans une seule table."""
    onglets = []
    for jour in jours:
        date_jour = lundi + datetime.timedelta(days=JOURS_OFFSET[jour])
        onglets.append({"jour": jour, "date": date_jour, "actif": jour == jour_actif})
    return onglets


def _contexte_suppression(programme):
    """Évolution du prompt 53, Temps 2 (S4) : bouton absent si non
    supprimable (jamais grisé sans explication) ; sinon, les éléments à
    nommer dans la confirmation (semaine déjà dans le contexte)."""
    if not programme or not peut_supprimer_brouillon(programme):
        return {"supprimable": False}
    brigades, nombre_seances = brigades_et_nombre_seances(programme)
    return {
        "supprimable": True,
        "brigades_suppression": brigades,
        "nombre_seances_suppression": nombre_seances,
    }


@exige_habilitation(PERMISSION_LECTURE)
def vue_consultation_programme(request):
    grille, creneaux_semaine = grille_active_avec_creneaux()
    lundi = _lundi_depuis_parametre(request.GET.get("semaine"))
    programme = programme_de_la_semaine(lundi)

    jours = jours_disponibles()
    jour_actif = request.GET.get("jour") if request.GET.get("jour") in jours else jours[0]
    creneaux_du_jour = [c for c in creneaux_semaine if c.jour_semaine == jour_actif]

    brigades = list(
        brigades_pour_filtre(
            brigade_pk=request.GET.get("brigade"), session_pk=request.GET.get("session")
        )
    )
    groupes = grille_consultation(programme, creneaux_du_jour, brigades) if programme else []
    contexte_du_circuit = contexte_circuit(programme, request.user) if programme else {}
    return render(
        request,
        "planification/consultation_programme.html",
        {
            **contexte_du_circuit,
            "programme": programme,
            "lundi": lundi,
            "date_du_jour": lundi + datetime.timedelta(days=JOURS_OFFSET[jour_actif]),
            "creneaux": creneaux_du_jour,
            "jour_actif": jour_actif,
            "onglets_jours": _onglets_jours(jours, jour_actif, lundi),
            "grille_active": grille,
            "groupes": groupes,
            "nombre_brigades": len(brigades),
            "toutes_brigades": brigades_pour_filtre(),
            # US-PLAN-07, E2 : visible avant soumission, mêmes brigades que
            # la grille consultée — aucun calcul nouveau (E1).
            "ecarts_volume_horaire": ecarts_volume_horaire(brigades),
            # US-VAL-05, H1 : lu dans le journal, aucune table nouvelle.
            "historique": historique_du_programme(programme) if programme else [],
            **_contexte_suppression(programme),
        },
    )
