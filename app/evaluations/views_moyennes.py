"""Écran dédié des moyennes et du classement — US-EVAL-06, M8 : visibilité
réservée à `evaluations_ecriture`, même confidentialité que les notes.
Orchestre, ne décide rien : toute la logique vit dans
`evaluations.services.moyenne.ServiceMoyenne`.

US-IHM-03 (prompt 64) : la liste des stagiaires passe par le même
composant que les autres listes de l'application (`noyau/gestion/
liste.html` — recherche, filtre, tri, pagination). `ServiceMoyenne.
calculer` rend déjà une liste PLATE de résultats (un par stagiaire) :
filtrer/trier/paginer cette liste pour l'affichage n'est pas un second
calcul de moyenne — aucune valeur numérique n'est retouchée, seul l'ORDRE
et le SOUS-ENSEMBLE affichés changent (`.claude/rules/services.md`, « un
service ne connaît pas la requête HTTP »)."""

from django.http import Http404
from django.shortcuts import render
from django.urls import reverse
from django.utils.html import format_html

from administration.habilitations import exige_habilitation
from evaluations.services.moyenne import PERMISSION_ECRITURE, ServiceMoyenne
from noyau.exceptions import ErreurIntrouvable
from noyau.listes import colonne_triee, correspond_filtre, correspond_recherche
from noyau.pagination import paginer
from organisation.services.session import ServiceSession
from organisation.services.stagiaire import ServiceStagiaire


def _session_ou_404(pk):
    try:
        return ServiceSession.obtenir(pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur


def _stagiaire_ou_404(pk):
    try:
        return ServiceStagiaire.obtenir(pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur


def _regrouper_manquants(manquants):
    """M5, RG-59 bis : par module, puis par brigade — à l'affichage seulement,
    aucune règle métier dans cette vue."""
    par_module: dict = {}
    for manquant in manquants:
        par_brigade = par_module.setdefault(manquant.module, {})
        par_brigade.setdefault(manquant.brigade, []).append(manquant.stagiaire)
    return par_module


CLES_TRI = {
    "stagiaire": lambda resultat: str(resultat.stagiaire).lower(),
    "brigade": lambda resultat: str(resultat.brigade).lower(),
    "moyenne": lambda resultat: resultat.moyenne,
    "rang_session": lambda resultat: resultat.rang_session,
}
TRI_PAR_DEFAUT = "rang_session"


def _filtrer_et_trier(resultats, filtres):
    """Tri/filtre/recherche sur la liste déjà calculée — jamais une requête
    SQL (il n'y en a pas : `ServiceMoyenne.calculer` lit les notes et
    calcule en Python), jamais une nouvelle moyenne."""
    filtres_resultats = [
        resultat
        for resultat in resultats
        if correspond_recherche(resultat.stagiaire, filtres["recherche"])
        and correspond_filtre(resultat.brigade.pk, filtres["brigade"])
    ]
    tri = filtres["tri"] or TRI_PAR_DEFAUT
    colonne = tri.lstrip("-")
    cle = CLES_TRI.get(colonne, CLES_TRI[TRI_PAR_DEFAUT])
    filtres_resultats.sort(key=cle, reverse=tri.startswith("-"))
    return filtres_resultats


def _colonnes(tri_actuel):
    return [
        colonne_triee(tri_actuel, "stagiaire", "Stagiaire"),
        colonne_triee(tri_actuel, "brigade", "Brigade"),
        colonne_triee(tri_actuel, "moyenne", "Moyenne"),
        colonne_triee(tri_actuel, "rang_session", "Rang (session)"),
        {"libelle": "Rang (brigade)", "cle_tri": None},
    ]


def _ligne(resultat, session_pk):
    url_detail = reverse("evaluations:detail_moyenne", args=[session_pk, resultat.stagiaire.pk])
    return {
        "cellules": [
            format_html(
                '<a href="{}" class="text-marine-700 no-underline hover:underline">{}</a>',
                url_detail,
                resultat.stagiaire,
            ),
            str(resultat.brigade),
            format_html('<span class="tabular-nums">{}</span>', resultat.moyenne),
            format_html('<span class="tabular-nums">{}</span>', resultat.rang_session),
            format_html('<span class="tabular-nums">{}</span>', resultat.rang_brigade),
        ],
        "libelle": str(resultat.stagiaire),
    }


def _brigades_filtrables(resultats):
    brigades = {resultat.brigade for resultat in resultats}
    return sorted(brigades, key=str)


@exige_habilitation(PERMISSION_ECRITURE)
def vue_moyennes(request, session_pk):
    session = _session_ou_404(session_pk)
    rapport = ServiceMoyenne.calculer(request.user, session)
    tri_actuel = request.GET.get("tri", "")
    filtres = {
        "recherche": request.GET.get("recherche", ""),
        "brigade": request.GET.get("brigade", ""),
        "tri": tri_actuel,
    }
    resultats_filtres = _filtrer_et_trier(rapport.resultats, filtres)
    page = paginer(resultats_filtres, request.GET.get("page"))
    brigades = _brigades_filtrables(rapport.resultats)
    return render(
        request,
        "evaluations/moyennes.html",
        {
            "session": session,
            "manquants_par_module": _regrouper_manquants(rapport.manquants),
            "modules_ignores": rapport.modules_ignores,
            "titre": f"Moyennes — {session}",
            "champ_recherche_libelle": "Stagiaire",
            "filtres": filtres,
            "filtres_champs": [
                {
                    "nom": "brigade",
                    "libelle": "Brigade",
                    "type": "choix",
                    "valeur": filtres["brigade"],
                    "choix": [(str(brigade.pk), str(brigade)) for brigade in brigades],
                }
            ],
            "masquer_filtre_archive": True,
            "url_liste": reverse("evaluations:moyennes_session", args=[session.pk]),
            "colonnes": _colonnes(tri_actuel),
            "lignes": [_ligne(resultat, session.pk) for resultat in page] if page else [],
            "libelle_vide": "Aucun stagiaire ne correspond aux filtres",
            "texte_vide": "Ajustez la recherche ou réinitialisez les filtres.",
            "page": page,
        },
    )


@exige_habilitation(PERMISSION_ECRITURE)
def vue_detail_moyenne(request, session_pk, stagiaire_pk):
    """US-EVAL-12 : détail par module — `ServiceMoyenne.detailler` fait
    toute la décision (calcul, journalisation), cette vue ne fait
    qu'afficher."""
    session = _session_ou_404(session_pk)
    stagiaire = _stagiaire_ou_404(stagiaire_pk)
    try:
        detail = ServiceMoyenne.detailler(request.user, session, stagiaire)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur
    return render(
        request,
        "evaluations/detail_moyenne.html",
        {
            "session": session,
            "detail": detail,
            "url_liste": reverse("evaluations:moyennes_session", args=[session.pk]),
        },
    )
