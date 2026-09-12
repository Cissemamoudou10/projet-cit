"""Vues de l'import de stagiaires, en deux temps — CU-P3-05, § 4, Prompt 24.
Orchestrent, ne décident rien : la lecture, l'analyse et l'écriture vivent
dans `organisation.import_stagiaires`.

ÉTAT ENTRE LES DEUX REQUÊTES (§ 4) : le contenu du fichier déposé au temps 1
est encodé en base64 dans un champ caché du compte rendu, jamais stocké côté
serveur. Voir docs/suivi/DECISIONS.md pour les deux voies écartées
(session Django, fichier temporaire) et pourquoi.
"""

import base64
import binascii

from django.contrib import messages
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from administration.habilitations import exige_habilitation
from noyau.exceptions import ErreurIntrouvable, ErreurValidation
from organisation.forms import FormulaireImportStagiaires
from organisation.import_stagiaires.analyse import analyser
from organisation.import_stagiaires.confirmation import confirmer
from organisation.import_stagiaires.modele import NOM_FICHIER_MODELE, generer_modele_xlsx
from organisation.services.session import ServiceSession
from organisation.services.stagiaire import ServiceStagiaire


def _session_ou_404(pk):
    try:
        return ServiceSession.obtenir(pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur


def _rendre_depot(request, session, *, formulaire=None):
    return render(
        request,
        "organisation/stagiaire_importer.html",
        {
            "session": session,
            "form": formulaire or FormulaireImportStagiaires(),
            "url_modele": reverse("organisation:modele_import_stagiaires", args=[session.pk]),
            "url_annuler": reverse("organisation:liste_stagiaires", args=[session.pk]),
        },
    )


@exige_habilitation(ServiceStagiaire.PERMISSION_ECRITURE)
def vue_importer_stagiaires(request, session_pk):
    session = _session_ou_404(session_pk)
    if request.method != "POST":
        return _rendre_depot(request, session)

    formulaire = FormulaireImportStagiaires(request.POST, request.FILES)
    if not formulaire.is_valid():
        return _rendre_depot(request, session, formulaire=formulaire)

    fichier = formulaire.cleaned_data["fichier"]
    contenu = fichier.read()
    try:
        rapport = analyser(session, contenu, fichier.name)
    except ErreurValidation as erreur:
        messages.error(request, str(erreur))
        return _rendre_depot(request, session)

    return render(
        request,
        "organisation/stagiaire_import_rapport.html",
        {
            "session": session,
            "rapport": rapport,
            "fichier_b64": base64.b64encode(contenu).decode("ascii"),
            "nom_fichier": fichier.name,
            "url_confirmer": reverse("organisation:confirmer_import_stagiaires", args=[session.pk]),
            "url_annuler": reverse("organisation:liste_stagiaires", args=[session.pk]),
        },
    )


@require_POST
@exige_habilitation(ServiceStagiaire.PERMISSION_ECRITURE)
def vue_confirmer_import_stagiaires(request, session_pk):
    session = _session_ou_404(session_pk)
    contenu = _decoder_fichier_depose(request)
    if contenu is None:
        messages.error(request, "Le dépôt a expiré : reprenez l'import depuis le début.")
        return redirect("organisation:importer_stagiaires", session.pk)

    nom_fichier = request.POST.get("nom_fichier", "")
    try:
        rapport = confirmer(request.user, session, contenu, nom_fichier)
    except ErreurValidation as erreur:
        messages.error(request, str(erreur))
        return redirect("organisation:importer_stagiaires", session.pk)

    messages.success(
        request, f"{len(rapport.lignes_valides)} stagiaire(s) enregistré(s)."
    )
    return redirect("organisation:liste_stagiaires", session.pk)


def _decoder_fichier_depose(request):
    fichier_b64 = request.POST.get("fichier_b64", "")
    try:
        return base64.b64decode(fichier_b64, validate=True)
    except (binascii.Error, ValueError):
        return None


@exige_habilitation(ServiceStagiaire.PERMISSION_ECRITURE)
def vue_telecharger_modele(request, session_pk):
    _session_ou_404(session_pk)
    contenu = generer_modele_xlsx()
    reponse = HttpResponse(
        contenu,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    reponse["Content-Disposition"] = f'attachment; filename="{NOM_FICHIER_MODELE}"'
    return reponse
