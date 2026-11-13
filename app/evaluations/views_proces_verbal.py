"""Écran dédié des procès-verbaux — US-EVAL-07, V9/V10. Orchestre, ne
décide rien : toute la logique vit dans
`evaluations.services.proces_verbal.ServiceProcesVerbal`.
"""

from django.contrib import messages
from django.http import Http404, HttpResponse, QueryDict
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.html import format_html

from administration.habilitations import exige_habilitation
from evaluations.models import TypeProcesVerbal
from evaluations.services.evaluation import ServiceEvaluation
from evaluations.services.proces_verbal import (
    PERMISSION_ECRITURE,
    PERMISSION_LECTURE,
    ServiceProcesVerbal,
)
from noyau.exceptions import ErreurIntrouvable, ErreurMetier
from noyau.habilitations import a_permission
from noyau.listes import colonne_triee, correspond_filtre, correspond_recherche
from noyau.pagination import paginer
from organisation.services.session import ServiceSession


def _session_ou_404(pk):
    try:
        return ServiceSession.obtenir(pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur


def _evaluation_depuis_post(request):
    evaluation_pk = request.POST.get("evaluation_pk")
    return ServiceEvaluation.obtenir(evaluation_pk) if evaluation_pk else None


def _evaluation_depuis_requete(request):
    """L'aperçu est désormais une consultation GET (US-IHM-03, prompt 64) —
    lecture seule, idempotente, jamais une écriture : la sélection de
    l'évaluation voyage donc en querystring, pas en POST, pour que la
    recherche/le filtre/le tri de `proces_verbal_apercu.html` puissent s'y
    ajouter comme sur toute autre liste. `générer`, lui, écrit : il reste
    en POST, inchangé."""
    evaluation_pk = request.GET.get("evaluation_pk")
    return ServiceEvaluation.obtenir(evaluation_pk) if evaluation_pk else None


def _url_proces_verbaux(pk):
    return reverse("evaluations:proces_verbaux", args=[pk])


def _url_apercu_sans_filtres(session_pk, type_pv, evaluation, numero):
    """URL de « Réinitialiser » : conserve la sélection (type/évaluation/
    numéro), efface seulement recherche/filtre/tri — contrairement à
    « Annuler », qui quitte l'aperçu."""
    base = reverse("evaluations:apercu_proces_verbal", args=[session_pk])
    requete = QueryDict(mutable=True)
    requete["type_pv"] = type_pv
    requete["evaluation_pk"] = evaluation.pk if evaluation else ""
    requete["numero"] = numero
    return f"{base}?{requete.urlencode()}"


CLES_TRI_APERCU = {
    "stagiaire": lambda ligne: str(ligne.stagiaire).lower(),
    "brigade": lambda ligne: str(ligne.brigade).lower(),
    "rang_session": lambda ligne: (ligne.rang_session is None, ligne.rang_session),
}
TRI_APERCU_PAR_DEFAUT = "rang_session"


def _filtrer_et_trier_apercu(lignes, filtres):
    """Même principe que `views_moyennes._filtrer_et_trier` : tri/filtre
    sur un résultat déjà calculé par le service, jamais un second calcul."""
    filtrees = [
        ligne
        for ligne in lignes
        if correspond_recherche(ligne.stagiaire, filtres["recherche"])
        and correspond_filtre(ligne.brigade, filtres["brigade"])
    ]
    tri = filtres["tri"] or TRI_APERCU_PAR_DEFAUT
    colonne = tri.lstrip("-")
    cle = CLES_TRI_APERCU.get(colonne, CLES_TRI_APERCU[TRI_APERCU_PAR_DEFAUT])
    filtrees.sort(key=cle, reverse=tri.startswith("-"))
    return filtrees


@exige_habilitation(PERMISSION_LECTURE)
def vue_proces_verbaux(request, session_pk):
    session = _session_ou_404(session_pk)
    proces_verbaux = ServiceProcesVerbal.lister(request.user, session)
    peut_generer = a_permission(request.user, PERMISSION_ECRITURE)
    evaluations = (
        ServiceProcesVerbal.evaluations_disponibles(request.user, session) if peut_generer else []
    )
    return render(
        request,
        "evaluations/proces_verbaux.html",
        {
            "session": session,
            "proces_verbaux": proces_verbaux,
            "evaluations": evaluations,
            "peut_generer": peut_generer,
            "url_apercu": reverse("evaluations:apercu_proces_verbal", args=[session.pk]),
        },
    )


def _contexte_filtrage_apercu(request, apercu):
    """Filtres/tri/pagination de l'aperçu — extrait de la vue pour rester
    sous la limite de 40 lignes (`.claude/rules/python.md`)."""
    tri_actuel = request.GET.get("tri", "")
    filtres = {
        "recherche": request.GET.get("recherche", ""),
        "brigade": request.GET.get("brigade", ""),
        "tri": tri_actuel,
    }
    lignes_filtrees = _filtrer_et_trier_apercu(apercu.lignes, filtres) if not apercu.manquants else []
    page = paginer(lignes_filtrees, request.GET.get("page")) if lignes_filtrees else None
    brigades = sorted({str(ligne.brigade) for ligne in apercu.lignes})
    return {
        "filtres": filtres,
        "filtres_champs": [
            {
                "nom": "brigade", "libelle": "Brigade", "type": "choix",
                "valeur": filtres["brigade"], "choix": [(b, b) for b in brigades],
            }
        ],
        "colonnes_apercu": [
            colonne_triee(tri_actuel, "stagiaire", "Stagiaire"),
            colonne_triee(tri_actuel, "brigade", "Brigade"),
            {"libelle": "Valeur", "cle_tri": None},
            colonne_triee(tri_actuel, "rang_session", "Rang"),
            {"libelle": "Décision" if apercu.seuil else "Absence", "cle_tri": None},
        ],
        "page": page,
    }


@exige_habilitation(PERMISSION_ECRITURE)
def vue_apercu_proces_verbal(request, session_pk):
    session = _session_ou_404(session_pk)
    type_pv = request.GET.get("type_pv", TypeProcesVerbal.FIN_DE_FORMATION)
    try:
        evaluation = _evaluation_depuis_requete(request)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur
    numero = request.GET.get("numero", "")
    apercu = ServiceProcesVerbal.apercu(request.user, session, evaluation)

    return render(
        request,
        "evaluations/proces_verbal_apercu.html",
        {
            "session": session,
            "evaluation": evaluation,
            "type_pv": type_pv,
            "numero": numero,
            "apercu": apercu,
            "champ_recherche_libelle": "Stagiaire",
            **_contexte_filtrage_apercu(request, apercu),
            "url_generer": reverse("evaluations:generer_proces_verbal", args=[session.pk]),
            "url_annuler": _url_proces_verbaux(session.pk),
            "url_reinitialiser": _url_apercu_sans_filtres(session.pk, type_pv, evaluation, numero),
        },
    )


@exige_habilitation(PERMISSION_ECRITURE)
def vue_generer_proces_verbal(request, session_pk):
    session = _session_ou_404(session_pk)
    type_pv = request.POST.get("type_pv", TypeProcesVerbal.FIN_DE_FORMATION)
    try:
        evaluation = _evaluation_depuis_post(request)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur
    numero = request.POST.get("numero", "")
    try:
        ServiceProcesVerbal.generer(request.user, session, type_pv, evaluation, numero)
    except ErreurMetier as erreur:
        messages.error(request, str(erreur))
    else:
        messages.success(request, "Procès-verbal généré.")
    return redirect(_url_proces_verbaux(session.pk))


@exige_habilitation(PERMISSION_LECTURE)
def vue_telecharger_proces_verbal(request, pk):
    try:
        proces_verbal = ServiceProcesVerbal.obtenir(pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur
    pdf = ServiceProcesVerbal.telecharger(request.user, proces_verbal)
    reponse = HttpResponse(pdf, content_type="application/pdf")
    nom = f"proces_verbal_{proces_verbal.pk}_v{proces_verbal.version}.pdf"
    reponse["Content-Disposition"] = f'attachment; filename="{nom}"'
    return reponse
