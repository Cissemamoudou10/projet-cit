"""Vues de gestion des sessions de formation — orchestrent, ne décident rien.
Toute la logique métier vit dans organisation.services.session.ServiceSession.
"""

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.html import format_html

from administration.habilitations import exige_habilitation
from noyau.exceptions import ErreurIntrouvable, ErreurModificationConcurrente, ErreurValidation
from noyau.forms import modifie_le_attendu_depuis_requete
from noyau.habilitations import a_permission
from organisation.forms import FormulaireSession
from organisation.services.brigade import ServiceBrigade
from organisation.services.session import ServiceSession
from referentiel.services.formation import ServiceFormation

GROUPES_FORMULAIRE = [
    {"legende": "Rattachement", "champs": ["formation"]},
    {
        "legende": "Période et effectif",
        "champs": ["intitule", "date_debut", "date_fin", "effectif_attendu"],
    },
]


def _session_ou_404(pk):
    try:
        return ServiceSession.obtenir(pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur


def _etat_tri(tri_actuel, colonne):
    """§ 3.09 : même patron que views/comptes.py::_etat_tri."""
    if tri_actuel == colonne:
        return {"aria": "ascending", "suivant": f"-{colonne}", "sens": "asc"}
    if tri_actuel == f"-{colonne}":
        return {"aria": "descending", "suivant": colonne, "sens": "desc"}
    return {"aria": "none", "suivant": colonne, "sens": None}


def _url_sans_parametre(request, nom):
    parametres = request.GET.copy()
    parametres.pop(nom, None)
    chaine = parametres.urlencode()
    return f"{request.path}?{chaine}" if chaine else request.path


def _filtres_champs(formation_id, etat):
    return [
        {
            "nom": "formation",
            "libelle": "Formation",
            "valeur": formation_id,
            "choix": [
                (formation.pk, formation.intitule)
                for formation in ServiceFormation.disponibles_pour_selection().order_by("intitule")
            ],
        },
        {
            "nom": "etat",
            "libelle": "État",
            "valeur": etat,
            "choix": ServiceSession.choix_etat(),
        },
    ]


def _filtres_actifs(request, formation_id, etat):
    actifs = []
    if formation_id:
        try:
            formation = ServiceFormation.obtenir(formation_id)
        except ErreurIntrouvable:
            formation = None
        if formation:
            actifs.append(
                {
                    "libelle": f"Formation : {formation}",
                    "url_retrait": _url_sans_parametre(request, "formation"),
                }
            )
    if etat:
        actifs.append(
            {
                "libelle": f"État : {ServiceSession.libelle_etat(etat)}",
                "url_retrait": _url_sans_parametre(request, "etat"),
            }
        )
    return actifs


def _colonnes(tri_actuel):
    return [
        _colonne_tri(tri_actuel, "intitule", "Intitulé"),
        {"libelle": "Formation", "cle_tri": None},
        {"libelle": "Type de formation", "cle_tri": None},
        {"libelle": "Période", "cle_tri": None},
        {"libelle": "Effectif attendu", "cle_tri": None},
        {"libelle": "État", "cle_tri": None},
        {"libelle": "Brigades", "cle_tri": None},
    ]


def _colonne_tri(tri_actuel, champ, libelle):
    etat = _etat_tri(tri_actuel, champ)
    return {
        "libelle": libelle,
        "cle_tri": champ,
        "tri_suivant": etat["suivant"],
        "sens": etat["sens"],
        "aria": etat["aria"],
    }


def _cellule_brigades(session):
    """Signale, sans bloquer, une session qui n'a encore aucune brigade —
    critère 2 (§ 4, Prompt 21) : une postcondition de CU-P3-02, pas un
    invariant — une session ouverte ce matin n'est pas en faute."""
    if session.nombre_brigades:
        return format_html('<span class="tabular-nums">{}</span>', session.nombre_brigades)
    return format_html(
        '<span class="bg-etat-attention px-2 py-px text-2xs font-semibold '
        'tracking-wide text-blanc">{}</span>',
        "AUCUNE BRIGADE",
    )


def _ligne(session, peut_ecrire):
    lien_intitule = format_html(
        '<a href="{}" class="text-marine-900 no-underline hover:underline">{}</a>',
        reverse("organisation:detail_session", args=[session.pk]),
        session.intitule,
    )
    ligne = {
        "cellules": [
            lien_intitule,
            session.formation.intitule,
            session.formation.type_formation.intitule,
            f"{session.date_debut:%d/%m/%Y} — {session.date_fin:%d/%m/%Y}",
            format_html('<span class="tabular-nums">{}</span>', session.effectif_attendu),
            session.get_etat_display(),
            _cellule_brigades(session),
        ],
        "libelle": session.intitule,
    }
    if peut_ecrire:
        ligne["url_modifier"] = reverse("organisation:modifier_session", args=[session.pk])
        ligne["url_supprimer"] = reverse("organisation:supprimer_session", args=[session.pk])
    return ligne


@exige_habilitation(ServiceSession.PERMISSION_LECTURE)
def vue_liste_sessions(request):
    tri_actuel = request.GET.get("tri", "")
    formation_id = request.GET.get("formation", "")
    etat = request.GET.get("etat", "")
    filtres = {
        "recherche": request.GET.get("recherche", ""),
        "formation": formation_id,
        "etat": etat,
        "tri": tri_actuel,
    }
    page = ServiceSession.lister(request.user, filtres, request.GET.get("page"))
    peut_ecrire = a_permission(request.user, ServiceSession.PERMISSION_ECRITURE)
    contexte = {
        "titre": "Sessions",
        "sous_titre": "Sessions de formation ouvertes par le centre.",
        "url_creer": reverse("organisation:creer_session") if peut_ecrire else "",
        "libelle_creer": "Ouvrir une session",
        "champ_recherche_libelle": "Intitulé",
        "filtres": filtres,
        "filtres_champs": _filtres_champs(formation_id, etat),
        "filtres_actifs": _filtres_actifs(request, formation_id, etat),
        "url_liste": reverse("organisation:liste_sessions"),
        "colonnes": _colonnes(tri_actuel),
        "lignes": [_ligne(session, peut_ecrire) for session in page] if page else [],
        "libelle_vide": "Aucune session ne correspond aux filtres",
        "texte_vide": "Ajustez la recherche ou réinitialisez les filtres.",
        "page": page,
        "masquer_filtre_archive": True,
    }
    return render(request, "noyau/gestion/liste.html", contexte)


@exige_habilitation(ServiceSession.PERMISSION_LECTURE)
def vue_detail_session(request, pk):
    session = _session_ou_404(pk)
    resume = ServiceSession.referentiel_resume(request.user, session)
    brigades = ServiceBrigade.lister(request.user, session)
    return render(
        request,
        "organisation/session_detail.html",
        {
            "session": session,
            "url_modifier": reverse("organisation:modifier_session", args=[session.pk]),
            "url_referentiel": reverse(
                "referentiel:referentiel_formation", args=[session.formation.pk]
            ),
            "url_brigades": reverse("organisation:brigades_session", args=[session.pk]),
            "nombre_matieres": resume["nombre_matieres"],
            "volume_total_referentiel": resume["volume_total"],
            "nombre_brigades": len(brigades),
        },
    )


@exige_habilitation(ServiceSession.PERMISSION_ECRITURE)
def vue_creer_session(request):
    if request.method == "POST":
        formulaire = FormulaireSession(request.POST)
        if formulaire.is_valid():
            try:
                session = ServiceSession.creer(request.user, formulaire.cleaned_data)
            except ErreurValidation as erreur:
                messages.error(request, str(erreur))
            else:
                messages.success(request, "Session ouverte.")
                for avertissement in session.avertissements:
                    messages.warning(request, avertissement["message"])
                return redirect("organisation:detail_session", session.pk)
    else:
        formulaire = FormulaireSession()
    return render(
        request,
        "noyau/gestion/formulaire.html",
        {
            "titre": "Ouvrir une session",
            "groupes": GROUPES_FORMULAIRE,
            "form": formulaire,
            "url_annuler": reverse("organisation:liste_sessions"),
            "libelle_bouton": "Ouvrir la session",
        },
    )


@exige_habilitation(ServiceSession.PERMISSION_ECRITURE)
def vue_modifier_session(request, pk):
    session = _session_ou_404(pk)
    if request.method == "POST":
        return _traiter_modification(request, session)
    formulaire = FormulaireSession(instance=session)
    return render(
        request, "noyau/gestion/formulaire.html", _contexte_modification(session, formulaire)
    )


def _traiter_modification(request, session):
    formulaire = FormulaireSession(request.POST, instance=session)
    modifie_le_attendu = modifie_le_attendu_depuis_requete(request)
    if formulaire.is_valid():
        try:
            session_modifiee = ServiceSession.modifier(
                request.user, session.pk, formulaire.cleaned_data, modifie_le_attendu
            )
        except (ErreurValidation, ErreurModificationConcurrente) as erreur:
            messages.error(request, str(erreur))
        else:
            messages.success(request, "Session modifiée.")
            for avertissement in session_modifiee.avertissements:
                messages.warning(request, avertissement["message"])
            return redirect("organisation:detail_session", session_modifiee.pk)
    return render(
        request, "noyau/gestion/formulaire.html", _contexte_modification(session, formulaire)
    )


def _contexte_modification(session, formulaire):
    return {
        "titre": f"Modifier « {session.intitule} »",
        "groupes": GROUPES_FORMULAIRE,
        "form": formulaire,
        "url_annuler": reverse("organisation:liste_sessions"),
        "libelle_bouton": "Enregistrer",
        "modifie_le_attendu": session.modifie_le,
    }


@exige_habilitation(ServiceSession.PERMISSION_ECRITURE)
def vue_confirmer_suppression_session(request, pk):
    session = _session_ou_404(pk)
    if request.method == "POST":
        try:
            ServiceSession.supprimer(request.user, pk)
        except ErreurValidation as erreur:
            messages.error(request, str(erreur))
        else:
            messages.success(request, "Session supprimée.")
        return redirect("organisation:liste_sessions")
    return render(
        request,
        "noyau/gestion/confirmer_suppression.html",
        {
            "titre_dialogue": f"Supprimer « {session.intitule} »",
            "texte_explication": f"« {session.intitule} » sera supprimée définitivement.",
            "url_annuler": reverse("organisation:liste_sessions"),
        },
    )
