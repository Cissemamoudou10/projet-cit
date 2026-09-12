"""Vues de gestion des stagiaires d'une session — CU-P3-05. Orchestrent, ne
décident rien : toute la logique métier vit dans
organisation.services.stagiaire.ServiceStagiaire.
"""

import datetime

from django.contrib import messages
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.html import format_html
from django.views.decorators.http import require_POST

from administration.habilitations import exige_habilitation
from noyau.exceptions import ErreurIntrouvable, ErreurValidation
from noyau.habilitations import a_permission
from organisation.forms import FormulaireRadiationStagiaire, FormulaireStagiaire
from organisation.import_stagiaires.ecrivain import ecrire_csv, ecrire_xlsx, nom_fichier_export
from organisation.services.brigade import ServiceBrigade
from organisation.services.session import ServiceSession
from organisation.services.stagiaire import NON_AFFECTES, ServiceStagiaire

GROUPES_FORMULAIRE = [
    {"legende": "Identité", "champs": ["matricule", "nom", "prenom", "grade", "unite"]},
]


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


def _url_sans_parametre(request, nom):
    parametres = request.GET.copy()
    parametres.pop(nom, None)
    chaine = parametres.urlencode()
    return f"{request.path}?{chaine}" if chaine else request.path


def _filtres_champs(brigades, etat, brigade):
    return [
        {
            "nom": "etat",
            "libelle": "État",
            "valeur": etat,
            "choix": [("actifs", "Actifs"), ("radies", "Radiés")],
        },
        {
            "nom": "brigade",
            "libelle": "Brigade",
            "valeur": brigade,
            "choix": [(str(b.pk), b.designation) for b in brigades]
            + [(NON_AFFECTES, "Non affectés")],
        },
    ]


def _libelle_brigade(brigades, brigade):
    if brigade == NON_AFFECTES:
        return "Non affectés"
    if brigade:
        for b in brigades:
            if str(b.pk) == brigade:
                return b.designation
    return ""


def _description_filtre(session, brigade_libelle, etat):
    """Le rappel en toutes lettres exigé au § 5, Prompt 26 — une phrase,
    jamais une icône ni une couleur seule : « Session X — brigade EXP1 —
    stagiaires actifs uniquement »."""
    segments = [f"Session {session.intitule}"]
    if brigade_libelle == "Non affectés":
        segments.append("stagiaires non affectés")
    elif brigade_libelle:
        segments.append(f"brigade {brigade_libelle}")
    if etat == "actifs":
        segments.append("stagiaires actifs uniquement")
    elif etat == "radies":
        segments.append("stagiaires radiés uniquement")
    else:
        segments.append("tous statuts")
    return " — ".join(segments)


def _filtres_actifs(request, etat, brigade_libelle):
    actifs = []
    if etat:
        libelle = "Actifs" if etat == "actifs" else "Radiés"
        actifs.append(
            {"libelle": f"État : {libelle}", "url_retrait": _url_sans_parametre(request, "etat")}
        )
    if brigade_libelle:
        actifs.append(
            {
                "libelle": f"Brigade : {brigade_libelle}",
                "url_retrait": _url_sans_parametre(request, "brigade"),
            }
        )
    return actifs


def _colonnes():
    return [
        {"libelle": "Matricule", "cle_tri": None},
        {"libelle": "Nom", "cle_tri": None},
        {"libelle": "Prénom", "cle_tri": None},
        {"libelle": "Grade", "cle_tri": None},
        {"libelle": "Unité d'origine", "cle_tri": None},
        {"libelle": "Brigade", "cle_tri": None},
        {"libelle": "État", "cle_tri": None},
    ]


def _cellule_brigade(stagiaire):
    if stagiaire.brigade_designation:
        return stagiaire.brigade_designation
    return format_html('<span class="text-gris-lecture">Non affecté</span>')


def _badge_etat(stagiaire):
    if not stagiaire.radie:
        return "Actif"
    titre = f"{stagiaire.motif_radiation} — {stagiaire.date_radiation:%d/%m/%Y}"
    return format_html(
        '<span title="{}" class="border border-etat-ecart px-2 py-px text-2xs '
        'font-semibold tracking-wide text-etat-ecart">RADIÉ</span>',
        titre,
    )


def _ligne(stagiaire, peut_ecrire):
    ligne = {
        "cellules": [
            stagiaire.matricule,
            stagiaire.nom,
            stagiaire.prenom,
            stagiaire.grade,
            stagiaire.unite,
            _cellule_brigade(stagiaire),
            _badge_etat(stagiaire),
        ],
        "libelle": f"{stagiaire.nom} {stagiaire.prenom}",
        "url_historique": reverse(
            "organisation:historique_affectations", args=[stagiaire.session_id, stagiaire.pk]
        ),
    }
    if peut_ecrire:
        ligne["url_modifier"] = reverse(
            "organisation:modifier_stagiaire", args=[stagiaire.session_id, stagiaire.pk]
        )
        if stagiaire.radie:
            ligne["url_deradier"] = reverse(
                "organisation:deradier_stagiaire", args=[stagiaire.session_id, stagiaire.pk]
            )
        else:
            ligne["url_radier"] = reverse(
                "organisation:radier_stagiaire", args=[stagiaire.session_id, stagiaire.pk]
            )
        ligne["url_supprimer"] = reverse(
            "organisation:supprimer_stagiaire", args=[stagiaire.session_id, stagiaire.pk]
        )
    return ligne


def _urls_export(session, request):
    parametres = request.GET.urlencode()
    base_csv = reverse("organisation:exporter_stagiaires", args=[session.pk, "csv"])
    base_xlsx = reverse("organisation:exporter_stagiaires", args=[session.pk, "xlsx"])
    return (
        f"{base_csv}?{parametres}" if parametres else base_csv,
        f"{base_xlsx}?{parametres}" if parametres else base_xlsx,
    )


@exige_habilitation(ServiceStagiaire.PERMISSION_LECTURE)
def vue_liste_stagiaires(request, session_pk):
    session = _session_ou_404(session_pk)
    etat = request.GET.get("etat", "")
    brigade = request.GET.get("brigade", "")
    filtres = {"recherche": request.GET.get("recherche", ""), "etat": etat, "brigade": brigade}
    page = ServiceStagiaire.lister(request.user, session, filtres, request.GET.get("page"))
    peut_ecrire = a_permission(request.user, ServiceStagiaire.PERMISSION_ECRITURE)
    brigades = list(ServiceBrigade.lister(request.user, session))
    brigade_libelle = _libelle_brigade(brigades, brigade)
    url_export_csv, url_export_xlsx = _urls_export(session, request)
    contexte = {
        "session": session,
        "titre": f"Stagiaires — {session.intitule}",
        "sous_titre": f"{session.formation} · du {session.date_debut:%d/%m/%Y} au "
        f"{session.date_fin:%d/%m/%Y}",
        "url_creer": reverse("organisation:creer_stagiaire", args=[session.pk])
        if peut_ecrire
        else "",
        "libelle_creer": "Enregistrer un stagiaire",
        "url_importer": reverse("organisation:importer_stagiaires", args=[session.pk])
        if peut_ecrire
        else "",
        "url_export_csv": url_export_csv,
        "url_export_xlsx": url_export_xlsx,
        "description_filtre": _description_filtre(session, brigade_libelle, etat),
        "champ_recherche_libelle": "Matricule, nom ou prénom",
        "filtres": filtres,
        "filtres_champs": _filtres_champs(brigades, etat, brigade),
        "filtres_actifs": _filtres_actifs(request, etat, brigade_libelle),
        "url_liste": reverse("organisation:liste_stagiaires", args=[session.pk]),
        "colonnes": _colonnes(),
        "lignes": [_ligne(stagiaire, peut_ecrire) for stagiaire in page] if page else [],
        "libelle_vide": "Aucun stagiaire ne correspond aux filtres",
        "texte_vide": "Ajustez la recherche ou réinitialisez les filtres.",
        "page": page,
        "masquer_filtre_archive": True,
    }
    return render(request, "organisation/stagiaire_liste.html", contexte)


ECRIVAINS_EXPORT = {
    "csv": (ecrire_csv, "text/csv"),
    "xlsx": (ecrire_xlsx, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
}


@exige_habilitation(ServiceStagiaire.PERMISSION_LECTURE)
def vue_exporter_stagiaires(request, session_pk, format_fichier):
    session = _session_ou_404(session_pk)
    if format_fichier not in ECRIVAINS_EXPORT:
        raise Http404
    etat = request.GET.get("etat", "")
    brigade = request.GET.get("brigade", "")
    filtres = {"recherche": request.GET.get("recherche", ""), "etat": etat, "brigade": brigade}
    brigades = list(ServiceBrigade.lister(request.user, session))
    brigade_libelle = _libelle_brigade(brigades, brigade)
    description = _description_filtre(session, brigade_libelle, etat)
    stagiaires = ServiceStagiaire.exporter(request.user, session, filtres, description)
    ecrivain, type_contenu = ECRIVAINS_EXPORT[format_fichier]
    nom_fichier = nom_fichier_export(
        session, {"brigade_libelle": brigade_libelle, "etat": etat}, format_fichier
    )
    reponse = HttpResponse(ecrivain(stagiaires), content_type=type_contenu)
    reponse["Content-Disposition"] = f'attachment; filename="{nom_fichier}"'
    return reponse


@exige_habilitation(ServiceStagiaire.PERMISSION_ECRITURE)
def vue_creer_stagiaire(request, session_pk):
    session = _session_ou_404(session_pk)
    if request.method == "POST":
        formulaire = FormulaireStagiaire(request.POST)
        if formulaire.is_valid():
            try:
                stagiaire = ServiceStagiaire.creer(request.user, session, formulaire.cleaned_data)
            except ErreurValidation as erreur:
                messages.error(request, str(erreur))
            else:
                messages.success(request, f"« {stagiaire} » enregistré.")
                return redirect("organisation:liste_stagiaires", session.pk)
    else:
        formulaire = FormulaireStagiaire()
    return render(
        request,
        "noyau/gestion/formulaire.html",
        {
            "titre": "Enregistrer un stagiaire",
            "groupes": GROUPES_FORMULAIRE,
            "form": formulaire,
            "url_annuler": reverse("organisation:liste_stagiaires", args=[session.pk]),
            "libelle_bouton": "Enregistrer le stagiaire",
        },
    )


@exige_habilitation(ServiceStagiaire.PERMISSION_ECRITURE)
def vue_modifier_stagiaire(request, session_pk, pk):
    session = _session_ou_404(session_pk)
    stagiaire = _stagiaire_ou_404(pk)
    if request.method == "POST":
        formulaire = FormulaireStagiaire(request.POST)
        if formulaire.is_valid():
            try:
                ServiceStagiaire.modifier(request.user, stagiaire, formulaire.cleaned_data)
            except ErreurValidation as erreur:
                messages.error(request, str(erreur))
            else:
                messages.success(request, f"« {stagiaire} » modifié.")
                return redirect("organisation:liste_stagiaires", session.pk)
    else:
        formulaire = FormulaireStagiaire(
            initial={
                "matricule": stagiaire.matricule,
                "nom": stagiaire.nom,
                "prenom": stagiaire.prenom,
                "grade": stagiaire.grade,
                "unite": stagiaire.unite,
            }
        )
    return render(
        request,
        "noyau/gestion/formulaire.html",
        {
            "titre": f"Modifier « {stagiaire} »",
            "groupes": GROUPES_FORMULAIRE,
            "form": formulaire,
            "url_annuler": reverse("organisation:liste_stagiaires", args=[session.pk]),
            "libelle_bouton": "Enregistrer",
        },
    )


@exige_habilitation(ServiceStagiaire.PERMISSION_ECRITURE)
def vue_confirmer_radiation_stagiaire(request, session_pk, pk):
    session = _session_ou_404(session_pk)
    stagiaire = _stagiaire_ou_404(pk)
    if request.method == "POST":
        formulaire = FormulaireRadiationStagiaire(request.POST)
        if formulaire.is_valid():
            try:
                ServiceStagiaire.radier(
                    request.user,
                    stagiaire,
                    formulaire.cleaned_data["motif"],
                    formulaire.cleaned_data["date_radiation"],
                )
            except ErreurValidation as erreur:
                messages.error(request, str(erreur))
            else:
                messages.success(request, f"« {stagiaire} » radié.")
                return redirect("organisation:liste_stagiaires", session.pk)
    else:
        formulaire = FormulaireRadiationStagiaire(initial={"date_radiation": datetime.date.today()})
    return render(
        request,
        "organisation/stagiaire_radier.html",
        {
            "session": session,
            "stagiaire": stagiaire,
            "form": formulaire,
            "url_annuler": reverse("organisation:liste_stagiaires", args=[session.pk]),
        },
    )


@require_POST
@exige_habilitation(ServiceStagiaire.PERMISSION_ECRITURE)
def vue_deradier_stagiaire(request, session_pk, pk):
    session = _session_ou_404(session_pk)
    stagiaire = _stagiaire_ou_404(pk)
    ServiceStagiaire.deradier(request.user, stagiaire)
    messages.success(request, f"« {stagiaire} » n'est plus radié.")
    return redirect("organisation:liste_stagiaires", session.pk)


@exige_habilitation(ServiceStagiaire.PERMISSION_ECRITURE)
def vue_confirmer_suppression_stagiaire(request, session_pk, pk):
    session = _session_ou_404(session_pk)
    stagiaire = _stagiaire_ou_404(pk)
    if request.method == "POST":
        try:
            ServiceStagiaire.supprimer(request.user, stagiaire)
        except ErreurValidation as erreur:
            messages.error(request, str(erreur))
        else:
            messages.success(request, f"« {stagiaire} » supprimé.")
        return redirect("organisation:liste_stagiaires", session.pk)
    return render(
        request,
        "noyau/gestion/confirmer_suppression.html",
        {
            "titre_dialogue": f"Supprimer « {stagiaire} »",
            "texte_explication": (
                f"« {stagiaire} » sera supprimé définitivement — à distinguer de la "
                "radiation, qui conserve l'historique."
            ),
            "url_annuler": reverse("organisation:liste_stagiaires", args=[session.pk]),
        },
    )
