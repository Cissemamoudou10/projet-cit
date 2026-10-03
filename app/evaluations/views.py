"""Vues de gestion des évaluations — CU-P6-01. Orchestrent, ne décident
rien : toute la logique vit dans
evaluations.services.evaluation.ServiceEvaluation.
"""

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.html import format_html

from administration.habilitations import exige_habilitation
from evaluations.forms import FormulaireEvaluation, FormulaireModificationDateCertificative
from evaluations.selectors import evaluations_non_pretes, resume_sujets
from evaluations.services.evaluation import (
    PERMISSION_ECRITURE,
    PERMISSION_LECTURE,
    ServiceEvaluation,
)
from noyau.exceptions import ErreurIntrouvable, ErreurValidation
from noyau.habilitations import a_permission
from noyau.pagination import paginer

GROUPES_FORMULAIRE = [
    {"legende": "Module et type", "champs": ["element_referentiel", "type"]},
    {"legende": "Périmètre", "champs": ["session", "brigade"]},
    {
        "legende": "Date et contrôle à venir",
        "champs": ["date", "creneau_type", "instructeur", "lieu", "motif_date_passee"],
    },
]


def _evaluation_ou_404(pk):
    try:
        return ServiceEvaluation.obtenir(pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur


def _perimetre(evaluation):
    return str(evaluation.session) if evaluation.session_id else str(evaluation.brigade)


def _date_affichee(evaluation):
    """C1 : la date imposée se signale partout où elle s'affiche."""
    if evaluation.seance_id:
        return evaluation.seance.debut.strftime("%d/%m/%Y %H:%M")
    if not evaluation.date:
        return "—"
    date_formatee = evaluation.date.strftime("%d/%m/%Y")
    if evaluation.est_certificative:
        return f"{date_formatee} — imposée (3ᵉ bureau)"
    return date_formatee


def _badge_non_prete():
    return format_html(
        '<span class="ml-2 border border-etat-ecart px-1.5 py-px text-2xs font-semibold '
        'uppercase tracking-wide text-etat-ecart">Non prête</span>'
    )


def _ligne(evaluation, non_pretes):
    lien_module = format_html(
        '<a href="{}" class="text-marine-900 no-underline hover:underline">{}</a>',
        reverse("evaluations:detail_evaluation", args=[evaluation.pk]),
        evaluation.element_referentiel,
    )
    if evaluation.pk in non_pretes:
        lien_module = format_html("{}{}", lien_module, _badge_non_prete())
    return {
        "cellules": [
            lien_module,
            evaluation.get_type_display(),
            _perimetre(evaluation),
            _date_affichee(evaluation),
        ],
        "libelle": str(evaluation),
    }


@exige_habilitation(PERMISSION_LECTURE)
def vue_liste_evaluations(request):
    page = paginer(ServiceEvaluation.lister(), request.GET.get("page"))
    non_pretes = evaluations_non_pretes([evaluation.pk for evaluation in page]) if page else ()
    contexte = {
        "titre": "Évaluations",
        "sous_titre": "Contrôles (formative) et examens finaux (certificative) du centre.",
        "url_creer": reverse("evaluations:creer_evaluation"),
        "libelle_creer": "Créer une évaluation",
        "url_liste": reverse("evaluations:liste_evaluations"),
        "colonnes": [
            {"libelle": "Module", "cle_tri": None},
            {"libelle": "Type", "cle_tri": None},
            {"libelle": "Périmètre", "cle_tri": None},
            {"libelle": "Date / séance", "cle_tri": None},
        ],
        "lignes": [_ligne(evaluation, non_pretes) for evaluation in page] if page else [],
        "libelle_vide": "Aucune évaluation créée",
        "texte_vide": "Créez la première évaluation depuis le bouton ci-dessus.",
        "page": page,
        "masquer_filtre_archive": True,
    }
    return render(request, "noyau/gestion/liste.html", contexte)


@exige_habilitation(PERMISSION_ECRITURE)
def vue_creer_evaluation(request):
    if request.method == "POST":
        formulaire = FormulaireEvaluation(request.POST)
        if formulaire.is_valid():
            try:
                evaluation = ServiceEvaluation.creer(request.user, formulaire.cleaned_data)
            except ErreurValidation as erreur:
                messages.error(request, str(erreur))
            else:
                messages.success(request, "Évaluation créée.")
                for item in evaluation.avertissements:
                    messages.warning(request, item["message"])
                return redirect("evaluations:detail_evaluation", evaluation.pk)
    else:
        formulaire = FormulaireEvaluation()
    return render(
        request,
        "noyau/gestion/formulaire.html",
        {
            "titre": "Créer une évaluation",
            "groupes": GROUPES_FORMULAIRE,
            "form": formulaire,
            "url_annuler": reverse("evaluations:liste_evaluations"),
            "libelle_bouton": "Créer l'évaluation",
        },
    )


@exige_habilitation(PERMISSION_LECTURE)
def vue_detail_evaluation(request, pk):
    evaluation = _evaluation_ou_404(pk)
    return render(
        request,
        "evaluations/evaluation_detail.html",
        {
            "evaluation": evaluation,
            "actions": ServiceEvaluation.actions_disponibles(evaluation),
            "url_liste": reverse("evaluations:liste_evaluations"),
            "resume_sujets": resume_sujets(evaluation),
            "peut_gerer_sujets": a_permission(request.user, PERMISSION_ECRITURE),
            "peut_modifier_date": a_permission(request.user, PERMISSION_ECRITURE),
        },
    )


@exige_habilitation(PERMISSION_ECRITURE)
def vue_modifier_date_certificative(request, pk):
    evaluation = _evaluation_ou_404(pk)
    if request.method == "POST":
        formulaire = FormulaireModificationDateCertificative(request.POST)
        if formulaire.is_valid():
            try:
                evaluation = ServiceEvaluation.modifier_date_certificative(
                    request.user,
                    evaluation,
                    formulaire.cleaned_data["nouvelle_date"],
                    formulaire.cleaned_data["motif"],
                )
            except ErreurValidation as erreur:
                messages.error(request, str(erreur))
            else:
                messages.success(request, "Date de l'examen final modifiée.")
                for item in evaluation.avertissements:
                    messages.warning(request, item["message"])
                return redirect("evaluations:detail_evaluation", evaluation.pk)
    else:
        formulaire = FormulaireModificationDateCertificative(
            initial={"nouvelle_date": evaluation.date}
        )
    return render(
        request,
        "noyau/gestion/formulaire.html",
        {
            "titre": f"Modifier la date — {evaluation.element_referentiel}",
            "form": formulaire,
            "url_annuler": reverse("evaluations:detail_evaluation", args=[evaluation.pk]),
            "libelle_bouton": "Enregistrer la nouvelle date",
        },
    )
