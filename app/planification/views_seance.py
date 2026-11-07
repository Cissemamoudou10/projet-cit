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
from organisation.models import Brigade
from planification.forms_seance import (
    FormulaireAjoutSeance,
    FormulaireAssociationBrigades,
    FormulaireSeance,
)
from planification.models import ProgrammeHebdomadaire, Seance
from planification.selectors import (
    JOUR_SEMAINE_PAR_ISO,
    brigades_candidates_au_regroupement,
    filtres_seance_par_element,
    formation_de_la_seance,
    grille_active_avec_creneaux,
)
from planification.services.circuit import ServiceCircuitProgramme
from planification.services.contraintes import Candidate
from planification.services.ecriture import ServiceEcritureSeance
from planification.services.modification import Avenantage

PERMISSION_ECRITURE = "noyau.programme_ecriture"


def _retour_consultation(programme):
    url = reverse("planification:consultation_programme")
    return redirect(f"{url}?semaine={programme.lundi_de_semaine.isoformat()}")


def _filtres_seance(formulaire):
    """L10, prompt 61 : les éléments déjà bornés par le formulaire
    (`formation`, prompt 58) — jamais une seconde requête non filtrée."""
    return filtres_seance_par_element(formulaire.fields["element_referentiel"].queryset)


def _url_modification(seance):
    return reverse("planification:modifier_seance", args=[seance.pk])


def _creneau_actuel(seance):
    """K8, prompt 59 : le créneau de la grille active dont le jour et les
    heures correspondent à ceux, RÉELS, de `seance` — `None` si elle est
    HORS GRILLE (aucune correspondance, données anciennes ou grille
    changée) : le formulaire de modification force alors un choix neuf,
    plutôt que de présélectionner un créneau qui ne serait pas le sien."""
    debut = timezone.localtime(seance.debut)
    fin = timezone.localtime(seance.fin)
    _, creneaux = grille_active_avec_creneaux()
    for creneau in creneaux:
        meme_jour = JOUR_SEMAINE_PAR_ISO[creneau.jour_semaine] == debut.isoweekday()
        if meme_jour and creneau.heure_debut == debut.time() and creneau.heure_fin == fin.time():
            return creneau
    return None


def _valeurs_initiales(seance):
    creneau = _creneau_actuel(seance)
    return {
        "element_referentiel": seance.element_referentiel_id,
        "instructeur": seance.instructeur_id,
        "lieu": seance.lieu_id,
        "creneau": creneau.pk if creneau else None,
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
    formation = formation_de_la_seance(seance)
    programme = seance.programme
    if request.method == "POST":
        formulaire = FormulaireSeance(request.POST, formation=formation, programme=programme)
        if formulaire.is_valid():
            return _appliquer(request, seance, formulaire)
    else:
        formulaire = FormulaireSeance(
            initial=_valeurs_initiales(seance), formation=formation, programme=programme
        )
    return render(
        request,
        "planification/modifier_seance.html",
        {
            "seance": seance,
            "programme": seance.programme,
            "formulaire": formulaire,
            "avenants": seance.avenants.select_related("cree_par").order_by("cree_le"),
            "filtres_seance": _filtres_seance(formulaire),
        },
    )


def _valeurs_initiales_ajout(request):
    valeurs = {}
    if request.GET.get("brigade"):
        valeurs["brigade"] = request.GET["brigade"]
    if request.GET.get("creneau"):
        valeurs["creneau"] = request.GET["creneau"]
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
        formulaire = FormulaireAjoutSeance(request.POST, programme=programme)
        if formulaire.is_valid():
            return _appliquer_ajout(request, programme, formulaire)
    else:
        formulaire = FormulaireAjoutSeance(
            initial=_valeurs_initiales_ajout(request), programme=programme
        )
    return render(
        request,
        "planification/ajouter_seance.html",
        {
            "programme": programme,
            "formulaire": formulaire,
            "filtres_seance": _filtres_seance(formulaire),
        },
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


def _appliquer_association(request, seance, formulaire):
    demande = formulaire.motif_et_nature_avenant()
    avenant = Avenantage(*demande) if demande else None
    try:
        ServiceEcritureSeance.associer_brigades(
            request.user,
            seance,
            list(formulaire.cleaned_data["brigades"]),
            confirmee=formulaire.cleaned_data["confirmee"],
            avenant=avenant,
        )
    except ErreurMetier as erreur:
        messages.error(request, str(erreur))
        return redirect(reverse("planification:gerer_brigades", args=[seance.pk]))
    messages.success(request, "Brigades associées à la séance.")
    return _retour_consultation(seance.programme)


@exige_habilitation(PERMISSION_ECRITURE)
def gerer_brigades(request, pk):
    """US-PLAN-06 (R1, R5) : associe des brigades à une séance en lieu
    partagé, ou en retire une (bouton par ligne). Brigades candidates en
    nombre de requêtes constant (`brigades_candidates_au_regroupement`)."""
    seance = get_object_or_404(Seance.objects.select_related("programme"), pk=pk)
    candidates = brigades_candidates_au_regroupement(seance)
    if request.method == "POST":
        formulaire = FormulaireAssociationBrigades(request.POST, brigades_candidates=candidates)
        if formulaire.is_valid():
            return _appliquer_association(request, seance, formulaire)
    else:
        formulaire = FormulaireAssociationBrigades(brigades_candidates=candidates)
    return render(
        request,
        "planification/gerer_brigades.html",
        {
            "seance": seance,
            "programme": seance.programme,
            "formulaire": formulaire,
            "lignes": list(seance.lignes.select_related("brigade")),
        },
    )


@require_POST
@exige_habilitation(PERMISSION_ECRITURE)
def retirer_brigade(request, pk):
    seance = get_object_or_404(Seance.objects.select_related("programme"), pk=pk)
    programme = seance.programme
    brigade = get_object_or_404(Brigade, pk=request.POST.get("brigade"))
    try:
        ServiceEcritureSeance.retirer_brigade(request.user, seance, brigade)
    except ErreurMetier as erreur:
        messages.error(request, str(erreur))
    else:
        messages.success(request, "Brigade retirée de la séance.")
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
