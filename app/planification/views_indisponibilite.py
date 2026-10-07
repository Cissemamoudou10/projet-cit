"""Écran de traitement d'une indisponibilité déclarée — US-PLAN-09 (prompt 42,
partie 3). Orchestre des opérations d'US-PLAN-05 (I1) : remplacer, substituer,
déprogrammer n'ouvrent aucune nouvelle voie d'écriture, chacune appelle
`ServiceEcritureSeance`.

`ressources` ne peut pas importer `planification` (DEPENDANCES_AUTORISEES) :
le lien part de son gabarit par `{% url %}`, jamais par un import Python —
même principe que D-121 E2 (`views_periode.py`). La liste des séances
impactées (I2) reste à requêtes constantes : aucun sélecteur de remplaçants
(I4) n'y est appelé — il ne l'est que sur l'écran dédié à UNE séance, ou à
UN lot d'une seule matière.
"""

from django.contrib import messages
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from administration.habilitations import exige_habilitation
from noyau.exceptions import ErreurIntrouvable, ErreurMetier
from planification.circuit_affichage import LIBELLES_ACTIONS
from planification.forms_indisponibilite import (
    FormulaireLotRemplacement,
    FormulaireRemplacementInstructeur,
    FormulaireSubstitutionSeance,
)
from planification.models import EtatProgramme, Seance
from planification.selectors_indisponibilite import (
    instructeurs_remplacants,
    seances_impactees_par_indisponibilite,
)
from planification.services.circuit import (
    ANNULER_VALIDATION,
    ECRIRE_SEANCE,
    RETIRER_SOUMISSION,
    motif_refus_action,
)
from planification.services.ecriture import ServiceEcritureSeance
from planification.services.indisponibilite import traiter_lot_remplacement
from planification.services.modification import Avenantage
from referentiel.models import Matiere
from ressources.models import Instructeur
from ressources.services.indisponibilite_instructeur import ServiceIndisponibiliteInstructeur

PERMISSION_LECTURE = "noyau.programme_lecture"
PERMISSION_ECRITURE = "noyau.programme_ecriture"

# I3 : VALIDÉ et SOUMIS renvoient à l'écran qui débloque l'écriture (T9, T3) —
# AFFICHÉ n'est pas ici, il s'écrit avec un avenant (`garde_modification`,
# branche `avenant=True`, hors de ce qu'`ECRIRE_SEANCE` admet seul).
EVENEMENT_DE_DEBLOCAGE = {
    EtatProgramme.VALIDE: ANNULER_VALIDATION,
    EtatProgramme.SOUMIS: RETIRER_SOUMISSION,
}


def _indisponibilite_ou_404(pk):
    try:
        return ServiceIndisponibiliteInstructeur.obtenir(pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur


def _ligne(seance):
    """I3 : ce que l'écran montre pour une séance selon l'état de son
    programme — le message et la route de déblocage viennent du moteur
    (`motif_refus_action`, `circuit_affichage.LIBELLES_ACTIONS`), jamais
    recodés ici (D-256 corrigée après relecture)."""
    programme = seance.programme
    brigades = ", ".join(str(ligne.brigade) for ligne in seance.lignes.all())
    evenement_deblocage = EVENEMENT_DE_DEBLOCAGE.get(programme.etat)
    if evenement_deblocage is not None:
        _, url_nom = LIBELLES_ACTIONS[evenement_deblocage]
        return {
            "seance": seance,
            "brigades": brigades,
            "bloquee": True,
            "message_blocage": motif_refus_action(ECRIRE_SEANCE, programme.etat),
            "url_blocage": reverse(url_nom, args=[programme.pk]),
        }
    return {
        "seance": seance,
        "brigades": brigades,
        "bloquee": False,
        "deprogrammer_possible": programme.etat != EtatProgramme.AFFICHE,
    }


def _groupes_lot(lignes):
    """C5 : un lien « traiter en lot » par matière qui compte plus d'une
    séance traitable — uniquement de l'EXISTANT déjà chargé (`seances`),
    aucune requête supplémentaire sur l'écran de liste (I2)."""
    comptes = {}
    for ligne in lignes:
        if ligne["bloquee"]:
            continue
        matiere = ligne["seance"].element_referentiel.matiere
        comptes[matiere] = comptes.get(matiere, 0) + 1
    return [
        {"matiere": matiere, "nombre": nombre} for matiere, nombre in comptes.items() if nombre > 1
    ]


@exige_habilitation(PERMISSION_LECTURE)
def traiter_indisponibilite(request, pk):
    indisponibilite = _indisponibilite_ou_404(pk)
    seances = seances_impactees_par_indisponibilite(indisponibilite)
    lignes = [_ligne(seance) for seance in seances]
    return render(
        request,
        "planification/traiter_indisponibilite.html",
        {
            "indisponibilite": indisponibilite,
            "lignes": lignes,
            "groupes_lot": _groupes_lot(lignes),
        },
    )


def _retour(indisponibilite):
    return redirect(reverse("planification:traiter_indisponibilite", args=[indisponibilite.pk]))


def _avenant_de(formulaire):
    demande = formulaire.motif_et_nature_avenant()
    return Avenantage(*demande) if demande else None


@exige_habilitation(PERMISSION_ECRITURE)
def remplacer_seance(request, indispo_pk, seance_pk):
    indisponibilite = _indisponibilite_ou_404(indispo_pk)
    seance = get_object_or_404(Seance.objects.select_related("programme"), pk=seance_pk)
    remplacants = instructeurs_remplacants(
        seance.element_referentiel.matiere, seance.debut, seance.fin
    )
    if request.method == "POST":
        formulaire = FormulaireRemplacementInstructeur(request.POST, remplacants=remplacants)
        if formulaire.is_valid():
            try:
                ServiceEcritureSeance.modifier_seance(
                    request.user,
                    seance,
                    {"instructeur": formulaire.cleaned_data["instructeur"]},
                    avenant=_avenant_de(formulaire),
                    confirmee=formulaire.cleaned_data["confirmee"],
                )
            except ErreurMetier as erreur:
                messages.error(request, str(erreur))
            else:
                messages.success(request, "Instructeur remplacé.")
                return _retour(indisponibilite)
    else:
        formulaire = FormulaireRemplacementInstructeur(remplacants=remplacants)
    return render(
        request,
        "planification/remplacer_seance.html",
        {"indisponibilite": indisponibilite, "seance": seance, "formulaire": formulaire},
    )


@exige_habilitation(PERMISSION_ECRITURE)
def substituer_seance(request, indispo_pk, seance_pk):
    indisponibilite = _indisponibilite_ou_404(indispo_pk)
    seance = get_object_or_404(Seance.objects.select_related("programme"), pk=seance_pk)
    if request.method == "POST":
        formulaire = FormulaireSubstitutionSeance(request.POST)
        if formulaire.is_valid():
            try:
                ServiceEcritureSeance.modifier_seance(
                    request.user,
                    seance,
                    formulaire.changements(),
                    avenant=_avenant_de(formulaire),
                    confirmee=formulaire.cleaned_data["confirmee"],
                )
            except ErreurMetier as erreur:
                messages.error(request, str(erreur))
            else:
                messages.success(request, "Matière substituée.")
                return _retour(indisponibilite)
    else:
        formulaire = FormulaireSubstitutionSeance()
    return render(
        request,
        "planification/substituer_seance.html",
        {"indisponibilite": indisponibilite, "seance": seance, "formulaire": formulaire},
    )


@exige_habilitation(PERMISSION_ECRITURE)
def deprogrammer_seance(request, indispo_pk, seance_pk):
    indisponibilite = _indisponibilite_ou_404(indispo_pk)
    seance = get_object_or_404(Seance, pk=seance_pk)
    if request.method == "POST":
        try:
            ServiceEcritureSeance.supprimer_seance(request.user, seance)
        except ErreurMetier as erreur:
            messages.error(request, str(erreur))
        else:
            messages.success(request, "Séance déprogrammée.")
    return _retour(indisponibilite)


def _candidats_lot(indisponibilite, matiere, matiere_pk):
    """Séances traitables de `matiere` (ni bloquées, I3), remplaçants libres
    sur l'étendue du lot (I4, bornes les plus larges du groupe) et le
    queryset qui borne le champ `seances` du formulaire."""
    seances = [
        seance
        for seance in seances_impactees_par_indisponibilite(indisponibilite)
        if seance.element_referentiel.matiere_id == matiere_pk
        and seance.programme.etat not in EVENEMENT_DE_DEBLOCAGE
    ]
    remplacants = (
        instructeurs_remplacants(
            matiere, min(s.debut for s in seances), max(s.fin for s in seances)
        )
        if seances
        else Instructeur.objects.none()
    )
    pks = [seance.pk for seance in seances]
    return seances, remplacants, Seance.objects.filter(pk__in=pks)


@exige_habilitation(PERMISSION_ECRITURE)
def lot_remplacement(request, indispo_pk, matiere_pk):
    indisponibilite = _indisponibilite_ou_404(indispo_pk)
    matiere = get_object_or_404(Matiere, pk=matiere_pk)
    seances, remplacants, seances_candidates = _candidats_lot(indisponibilite, matiere, matiere_pk)
    pks = [seance.pk for seance in seances]
    if request.method == "POST":
        formulaire = FormulaireLotRemplacement(
            request.POST, seances_candidates=seances_candidates, remplacants=remplacants
        )
        if formulaire.is_valid():
            try:
                traiter_lot_remplacement(
                    request.user,
                    list(formulaire.cleaned_data["seances"]),
                    formulaire.cleaned_data["instructeur"],
                    avenant=_avenant_de(formulaire),
                    confirmee=formulaire.cleaned_data["confirmee"],
                )
            except ErreurMetier as erreur:
                messages.error(request, str(erreur))
            else:
                messages.success(request, "Séances du lot remplacées.")
                return _retour(indisponibilite)
    else:
        formulaire = FormulaireLotRemplacement(
            seances_candidates=seances_candidates, remplacants=remplacants, initial={"seances": pks}
        )
    return render(
        request,
        "planification/lot_remplacement.html",
        {
            "indisponibilite": indisponibilite,
            "matiere": matiere,
            "seances": seances,
            "formulaire": formulaire,
        },
    )
