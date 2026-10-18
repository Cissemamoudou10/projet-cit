"""Écrans du circuit du programme (prompt 40, US-VAL-01, 02 et 04 ; prompt 47,
US-VAL-05).

Chaque écran d'écriture est une action POST : elle appelle le moteur
`ServiceCircuitProgramme` et n'en reprend aucune règle. Un refus du moteur
s'affiche par message, l'état reste celui du moteur.
"""

import datetime

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from administration.habilitations import exige_habilitation
from noyau.pagination import paginer
from planification.exceptions import TransitionProgrammeRefusee
from planification.forms_circuit import FormulaireSignature
from planification.models import EtatProgramme, ProgrammeHebdomadaire
from planification.selectors_circuit import (
    auteurs_des_soumissions,
    programmes_en_attente,
    programmes_filtres,
)
from planification.services.circuit import ServiceCircuitProgramme

PERMISSION_PLANIFICATION = "noyau.programme_ecriture"
PERMISSION_PEDAGOGIQUE = "noyau.programme_validation_ecriture"
PERMISSION_PEDAGOGIQUE_LECTURE = "noyau.programme_validation_lecture"
PERMISSION_LECTURE = "noyau.programme_lecture"


def _retour_consultation(programme):
    url = reverse("planification:consultation_programme")
    return redirect(f"{url}?semaine={programme.lundi_de_semaine.isoformat()}")


def _executer(request, programme, action, message_succes):
    """Applique `action(agissant, programme)` ; le refus du moteur devient un message."""
    try:
        action(request.user, programme)
    except TransitionProgrammeRefusee as erreur:
        messages.error(request, str(erreur))
    else:
        messages.success(request, message_succes)
    return _retour_consultation(programme)


def _programme(pk):
    return get_object_or_404(ProgrammeHebdomadaire, pk=pk)


@require_POST
@exige_habilitation(PERMISSION_PLANIFICATION)
def soumettre(request, pk):
    programme = _programme(pk)
    return _executer(
        request, programme, ServiceCircuitProgramme.soumettre, "Programme soumis à validation."
    )


@require_POST
@exige_habilitation(PERMISSION_PLANIFICATION)
def retirer_soumission(request, pk):
    programme = _programme(pk)
    return _executer(
        request,
        programme,
        ServiceCircuitProgramme.retirer_soumission,
        "Soumission retirée : le programme est de nouveau modifiable.",
    )


@require_POST
@exige_habilitation(PERMISSION_PEDAGOGIQUE)
def valider(request, pk):
    programme = _programme(pk)
    return _executer(request, programme, ServiceCircuitProgramme.valider, "Programme validé.")


@require_POST
@exige_habilitation(PERMISSION_PEDAGOGIQUE)
def rejeter(request, pk):
    programme = _programme(pk)
    motif = request.POST.get("motif", "")
    return _executer(
        request,
        programme,
        lambda agissant, cible: ServiceCircuitProgramme.rejeter(agissant, cible, motif),
        "Programme rejeté.",
    )


@require_POST
@exige_habilitation(PERMISSION_PLANIFICATION)
def reprendre(request, pk):
    programme = _programme(pk)
    return _executer(
        request,
        programme,
        ServiceCircuitProgramme.reprendre,
        "Programme repris en correction.",
    )


@require_POST
@exige_habilitation(PERMISSION_PLANIFICATION)
def signer(request, pk):
    programme = _programme(pk)
    formulaire = FormulaireSignature(request.POST)
    if not formulaire.is_valid():
        messages.error(request, "La signature exige une date et le nom du signataire.")
        return _retour_consultation(programme)
    donnees = formulaire.cleaned_data
    return _executer(
        request,
        programme,
        lambda agissant, cible: ServiceCircuitProgramme.enregistrer_signature(
            agissant, cible, donnees["date_signature"], donnees["signataire"]
        ),
        "Signature enregistrée.",
    )


@require_POST
@exige_habilitation(PERMISSION_PLANIFICATION)
def afficher(request, pk):
    programme = _programme(pk)
    return _executer(request, programme, ServiceCircuitProgramme.afficher, "Programme affiché.")


@exige_habilitation(PERMISSION_PEDAGOGIQUE_LECTURE)
def attente_validation(request):
    """CU-P5-03, US-VAL-01 c.3 : les programmes soumis, en une seule requête pour
    les auteurs quel que soit leur nombre."""
    programmes = list(programmes_en_attente())
    auteurs = auteurs_des_soumissions(programmes)
    lignes = [
        {"programme": programme, "auteur": auteurs.get(programme.pk)} for programme in programmes
    ]
    return render(
        request,
        "planification/attente_validation.html",
        {"lignes": lignes},
    )


def _date_filtre(request, nom):
    valeur = request.GET.get(nom)
    if not valeur:
        return None
    try:
        return datetime.date.fromisoformat(valeur)
    except ValueError:
        return None


@exige_habilitation(PERMISSION_LECTURE)
def vue_liste_programmes(request):
    """US-VAL-05, H2 : toutes les semaines, filtrables par état et par
    période — chaque ligne mène à la consultation de la semaine, qui porte
    son historique (H1). `programme_lecture`, pas `programme_validation_
    lecture` (celle d'`attente_validation`, ci-dessus) : cet écran liste des
    PROGRAMMES, le circuit de validation n'en est qu'une colonne parmi
    d'autres — choix distinct signalé en relecture, les deux permissions se
    recoupent aujourd'hui exactement dans `MATRICE` (D-280)."""
    etat = request.GET.get("etat") or None
    periode_debut = _date_filtre(request, "debut")
    periode_fin = _date_filtre(request, "fin")
    programmes = programmes_filtres(etat=etat, periode_debut=periode_debut, periode_fin=periode_fin)
    page = paginer(programmes, request.GET.get("page"))
    return render(
        request,
        "planification/liste_programmes.html",
        {"page": page, "etats": EtatProgramme.choices},
    )
