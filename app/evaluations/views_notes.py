"""Écran dédié des notes — US-EVAL-05, N5 : visibilité réservée à
`evaluations_ecriture`, jamais la lecture séparée des évaluations.
Orchestrent, ne décident rien : toute la logique vit dans
`evaluations.services.note.ServiceNote`.

État entre les deux requêtes de la double vérification (N3) : les valeurs
brutes soumises à l'étape 1 sont encodées en JSON puis base64 dans un champ
caché du récapitulatif, jamais stockées côté serveur — même mécanisme que
l'import de stagiaires (`noyau.services.etat_transitoire`).
"""

import json

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from administration.habilitations import exige_habilitation
from evaluations.services.evaluation import ServiceEvaluation
from evaluations.services.note import PERMISSION_ECRITURE, ServiceNote
from noyau.exceptions import ErreurIntrouvable, ErreurValidation
from noyau.services import etat_transitoire


def _evaluation_ou_404(pk):
    try:
        return ServiceEvaluation.obtenir(pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur


def _url_notes(pk):
    return reverse("evaluations:notes", args=[pk])


def _lignes_depuis_post(request):
    """Un préfixe par stagiaire (`valeur_<pk>`, `absent_<pk>`) : chaque
    valeur reste associée à l'identifiant réel du stagiaire, jamais à sa
    position dans le tableau."""
    lignes = {}
    for cle in request.POST:
        if not cle.startswith("valeur_"):
            continue
        stagiaire_pk = cle.removeprefix("valeur_")
        lignes[stagiaire_pk] = {
            "valeur": request.POST.get(cle, ""),
            "absent": request.POST.get(f"absent_{stagiaire_pk}") == "on",
        }
    return lignes


def _rendre_grille(request, evaluation, *, brutes=None):
    stagiaires, notes = ServiceNote.consulter(request.user, evaluation)
    lignes = []
    for stagiaire in stagiaires:
        brute = (brutes or {}).get(str(stagiaire.pk))
        note = notes.get(stagiaire.pk)
        if brute is not None:
            valeur, absent = brute.get("valeur", ""), brute.get("absent", False)
        elif note is not None:
            valeur, absent = ("" if note.absent else note.valeur), note.absent
        else:
            valeur, absent = "", False
        lignes.append({"stagiaire": stagiaire, "valeur": valeur, "absent": absent})
    return render(
        request,
        "evaluations/notes_saisie.html",
        {
            "evaluation": evaluation,
            "lignes": lignes,
            "url_verifier": _url_notes(evaluation.pk),
            "url_liste": reverse("evaluations:detail_evaluation", args=[evaluation.pk]),
        },
    )


@exige_habilitation(PERMISSION_ECRITURE)
def vue_notes(request, pk):
    evaluation = _evaluation_ou_404(pk)
    if request.method != "POST":
        return _rendre_grille(request, evaluation)
    lignes_brutes = _lignes_depuis_post(request)
    try:
        rapport = ServiceNote.verifier(request.user, evaluation, lignes_brutes)
    except ErreurValidation as erreur:
        messages.error(request, str(erreur))
        return _rendre_grille(request, evaluation, brutes=lignes_brutes)
    return render(
        request,
        "evaluations/notes_recapitulatif.html",
        {
            "evaluation": evaluation,
            "rapport": rapport,
            "lignes_b64": etat_transitoire.encoder(json.dumps(lignes_brutes).encode("utf-8")),
            "url_confirmer": reverse("evaluations:confirmer_notes", args=[evaluation.pk]),
            "url_annuler": _url_notes(evaluation.pk),
        },
    )


@require_POST
@exige_habilitation(PERMISSION_ECRITURE)
def vue_confirmer_notes(request, pk):
    evaluation = _evaluation_ou_404(pk)
    contenu = etat_transitoire.decoder(request.POST.get("lignes_b64", ""))
    if not contenu:
        # `decoder("")` rend des octets vides, pas None (base64 décode
        # valablement la chaîne vide) : un champ cru absent doit refuser
        # tout comme un champ corrompu, jamais planter sur `json.loads(b"")`.
        messages.error(request, "La vérification a expiré : reprenez la saisie depuis le début.")
        return redirect(_url_notes(pk))
    lignes_brutes = json.loads(contenu)
    try:
        rapport = ServiceNote.confirmer(request.user, evaluation, lignes_brutes)
    except ErreurValidation as erreur:
        messages.error(request, str(erreur))
    else:
        total = len(rapport.saisies) + len(rapport.absences)
        messages.success(request, f"{total} note(s) enregistrée(s).")
    return redirect(_url_notes(pk))
