"""Écran autonome « Indisponibilités des instructeurs » — § 7, Prompt 27,
corrigé par DECISIONS.md D-115 : la donnée relève du domaine
`lieux_calendrier`, cet écran en est l'unique lecture et l'unique saisie —
jamais une seconde sur la fiche instructeur. Toute la logique métier vit
dans ressources.services.indisponibilite_instructeur.
ServiceIndisponibiliteInstructeur.
"""

import datetime

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_POST

from administration.habilitations import exige_habilitation
from noyau.exceptions import ErreurIntrouvable, ErreurValidation
from noyau.habilitations import a_permission
from ressources.forms import (
    FormulaireDeclarationIndisponibiliteInstructeur,
    FormulaireIndisponibiliteInstructeur,
)
from ressources.navigation import onglets_ressources
from ressources.services.indisponibilite_instructeur import ServiceIndisponibiliteInstructeur
from ressources.services.instructeur import ServiceInstructeur


def _indisponibilite_ou_404(pk):
    try:
        return ServiceIndisponibiliteInstructeur.obtenir(pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur


def _url_sans_parametre(request, nom):
    parametres = request.GET.copy()
    parametres.pop(nom, None)
    chaine = parametres.urlencode()
    return f"{request.path}?{chaine}" if chaine else request.path


def _date_du_parametre(request, nom):
    valeur = request.GET.get(nom)
    if not valeur:
        return None
    return datetime.date.fromisoformat(valeur) if _est_date_iso(valeur) else None


def _est_date_iso(valeur):
    try:
        datetime.date.fromisoformat(valeur)
    except ValueError:
        return False
    return True


def _url_liste_filtree(instructeur_pk):
    url = reverse("ressources:liste_indisponibilites_instructeurs")
    return f"{url}?instructeur={instructeur_pk}" if instructeur_pk else url


def _url_declarer_filtree(instructeur_pk):
    url = reverse("ressources:declarer_indisponibilite_instructeur")
    return f"{url}?instructeur={instructeur_pk}" if instructeur_pk else url


def _filtres_champs(instructeur_pk, periode_du, periode_au):
    return [
        {
            "nom": "instructeur",
            "libelle": "Instructeur",
            "valeur": instructeur_pk,
            "choix": ServiceIndisponibiliteInstructeur.choix_instructeurs(),
        },
        {
            "nom": "periode_du",
            "libelle": "Période du",
            "valeur": periode_du,
            "type": "date",
        },
        {
            "nom": "periode_au",
            "libelle": "au",
            "valeur": periode_au,
            "type": "date",
        },
    ]


def _filtres_actifs(request, instructeur_pk):
    if not instructeur_pk:
        return []
    libelles = dict(ServiceIndisponibiliteInstructeur.choix_instructeurs())
    libelle = libelles.get(int(instructeur_pk), instructeur_pk)
    return [
        {
            "libelle": f"Instructeur : {libelle}",
            "url_retrait": _url_sans_parametre(request, "instructeur"),
        }
    ]


def _colonnes():
    return [
        {"libelle": "Instructeur", "cle_tri": None},
        {"libelle": "Début", "cle_tri": None},
        {"libelle": "Fin", "cle_tri": None},
        {"libelle": "Motif", "cle_tri": None},
        {"libelle": "État", "cle_tri": None},
        {"libelle": "Séances impactées", "cle_tri": None},
    ]


def _traitement_affiche(indisponibilite):
    """I2 (US-PLAN-09, prompt 42, partie 3) : consultable depuis la liste,
    pas seulement à l'enregistrement (C1). Aucune condition d'habilitation
    ici : c'est l'écran de `planification` qui la vérifie pour son propre
    domaine (même principe que le lien D-121 E2 vers `seances_de_la_periode`,
    jamais gardé par `ressources`)."""
    return format_html(
        '<a href="{}" class="text-marine-900 no-underline hover:underline">Traiter</a>',
        _url_traitement(indisponibilite.pk),
    )


def _ligne(indisponibilite, peut_ecrire, peut_lire_instructeur):
    """Le nom de l'instructeur n'est un lien vers sa fiche que si le profil
    peut réellement l'atteindre (`instructeurs_qualifications_lecture`) —
    sinon un lien mort reproduirait, en miniature, l'adresse inatteignable
    que D-115 corrige."""
    if peut_lire_instructeur:
        instructeur_affiche = format_html(
            '<a href="{}" class="text-marine-900 no-underline hover:underline">{}</a>',
            reverse("ressources:detail_instructeur", args=[indisponibilite.instructeur_id]),
            indisponibilite.instructeur,
        )
    else:
        instructeur_affiche = str(indisponibilite.instructeur)
    ligne = {
        "cellules": [
            instructeur_affiche,
            indisponibilite.debut.strftime("%d/%m/%Y %H:%M"),
            indisponibilite.fin.strftime("%d/%m/%Y %H:%M"),
            indisponibilite.motif,
            _badge_etat(indisponibilite),
            _traitement_affiche(indisponibilite),
        ],
        "libelle": str(indisponibilite),
    }
    if peut_ecrire:
        ligne["url_modifier"] = reverse(
            "ressources:modifier_indisponibilite_instructeur", args=[indisponibilite.pk]
        )
        ligne["url_supprimer"] = reverse(
            "ressources:supprimer_indisponibilite_instructeur", args=[indisponibilite.pk]
        )
    return ligne


def _badge_etat(indisponibilite):
    if indisponibilite.est_passee:
        return mark_safe(
            '<span class="border border-gris-trait px-2 py-px text-2xs font-semibold '
            'tracking-wide text-gris-lecture">PASSÉE</span>'
        )
    if indisponibilite.est_en_cours:
        return mark_safe(
            '<span class="border border-etat-attention px-2 py-px text-2xs font-semibold '
            'tracking-wide text-etat-attention">EN COURS</span>'
        )
    return mark_safe(
        '<span class="border border-marine-700 px-2 py-px text-2xs font-semibold '
        'tracking-wide text-marine-700">À VENIR</span>'
    )


@exige_habilitation(ServiceIndisponibiliteInstructeur.PERMISSION_LECTURE)
def vue_liste_indisponibilites_instructeurs(request):
    instructeur_pk = request.GET.get("instructeur", "")
    periode_du = _date_du_parametre(request, "periode_du")
    periode_au = _date_du_parametre(request, "periode_au")
    motif = request.GET.get("recherche", "")
    filtres_service = {
        "instructeur": instructeur_pk,
        "motif": motif,
        "periode_du": periode_du,
        "periode_au": periode_au,
    }
    filtres = {**filtres_service, "recherche": motif}
    page = ServiceIndisponibiliteInstructeur.lister(
        request.user, filtres_service, request.GET.get("page")
    )
    peut_ecrire = a_permission(request.user, ServiceIndisponibiliteInstructeur.PERMISSION_ECRITURE)
    peut_lire_instructeur = a_permission(request.user, ServiceInstructeur.PERMISSION_LECTURE)
    onglets, onglet_actif = onglets_ressources(request.user, "indisponibilites-instructeurs")
    contexte = {
        "titre": "Indisponibilités des instructeurs",
        "sous_titre": "Périodes où un instructeur ne peut pas être affecté.",
        "onglets": onglets,
        "onglet_actif": onglet_actif,
        "url_creer": _url_declarer_filtree(instructeur_pk) if peut_ecrire else "",
        "libelle_creer": "Déclarer une indisponibilité",
        "champ_recherche_libelle": "Motif",
        "masquer_filtre_archive": True,
        "filtres": filtres,
        "filtres_champs": _filtres_champs(instructeur_pk, periode_du, periode_au),
        "filtres_actifs": _filtres_actifs(request, instructeur_pk),
        "url_liste": reverse("ressources:liste_indisponibilites_instructeurs"),
        "colonnes": _colonnes(),
        "lignes": [_ligne(i, peut_ecrire, peut_lire_instructeur) for i in page] if page else [],
        "libelle_vide": "Aucune indisponibilité ne correspond aux filtres",
        "texte_vide": "Ajustez la recherche ou réinitialisez les filtres.",
        "page": page,
    }
    return render(request, "noyau/gestion/liste.html", contexte)


def _rendre_saisie(request, formulaire, instructeur_pk):
    return render(
        request,
        "noyau/gestion/formulaire.html",
        {
            "titre": "Déclarer une indisponibilité d'instructeur",
            "legende": "Instructeur, période et motif",
            "form": formulaire,
            "url_annuler": _url_liste_filtree(instructeur_pk),
            "libelle_bouton": "Déclarer l'indisponibilité",
        },
    )


def _rendre_fusion(request, instructeur, formulaire, proposition):
    return render(
        request,
        "ressources/indisponibilite_instructeur_fusion.html",
        {
            "instructeur": instructeur,
            "proposition": proposition,
            "form": formulaire,
            "url_confirmer": reverse("ressources:confirmer_fusion_indisponibilite"),
            "url_annuler": _url_liste_filtree(instructeur.pk),
        },
    )


def _url_traitement(indisponibilite_pk):
    """US-PLAN-09 (prompt 42, partie 3, C1) : la liste des séances
    impactées appartient à `planification`, qui peut dépendre de
    `ressources` — pas l'inverse. Lien par nom de route, aucun import
    Python (même principe que D-121 E2)."""
    return reverse("planification:traiter_indisponibilite", args=[indisponibilite_pk])


def _traiter_saisie(request, formulaire):
    """Retourne une redirection/un rendu à renvoyer immédiatement, ou `None`
    pour laisser l'appelant réafficher le formulaire de saisie (motif
    invalide notamment)."""
    instructeur = formulaire.cleaned_data["instructeur"]
    debut, fin, motif = (
        formulaire.cleaned_data["debut"],
        formulaire.cleaned_data["fin"],
        formulaire.cleaned_data["motif"],
    )
    try:
        proposition = ServiceIndisponibiliteInstructeur.proposer(
            request.user, instructeur, debut, fin, motif
        )
    except ErreurValidation as erreur:
        messages.error(request, str(erreur))
        return None
    if proposition.absorbees:
        return _rendre_fusion(request, instructeur, formulaire, proposition)
    indisponibilite = ServiceIndisponibiliteInstructeur.confirmer(
        request.user, instructeur, debut, fin, motif
    )
    messages.success(request, "Indisponibilité déclarée.")
    return redirect(_url_traitement(indisponibilite.pk))


@exige_habilitation(ServiceIndisponibiliteInstructeur.PERMISSION_ECRITURE)
def vue_declarer_indisponibilite_instructeur(request):
    if request.method == "POST":
        formulaire = FormulaireDeclarationIndisponibiliteInstructeur(request.POST)
        instructeur_pk = request.POST.get("instructeur")
        if formulaire.is_valid():
            reponse = _traiter_saisie(request, formulaire)
            if reponse is not None:
                return reponse
    else:
        instructeur_pk = request.GET.get("instructeur")
        formulaire = FormulaireDeclarationIndisponibiliteInstructeur(
            initial={"instructeur": instructeur_pk} if instructeur_pk else None
        )
    return _rendre_saisie(request, formulaire, instructeur_pk)


@require_POST
@exige_habilitation(ServiceIndisponibiliteInstructeur.PERMISSION_ECRITURE)
def vue_confirmer_fusion_indisponibilite(request):
    formulaire = FormulaireDeclarationIndisponibiliteInstructeur(request.POST)
    if formulaire.is_valid():
        instructeur = formulaire.cleaned_data["instructeur"]
        try:
            indisponibilite = ServiceIndisponibiliteInstructeur.confirmer(
                request.user,
                instructeur,
                formulaire.cleaned_data["debut"],
                formulaire.cleaned_data["fin"],
                formulaire.cleaned_data["motif"],
            )
        except ErreurValidation as erreur:
            messages.error(request, str(erreur))
            return redirect(_url_declarer_filtree(instructeur.pk))
        messages.success(request, "Indisponibilité enregistrée.")
        return redirect(_url_traitement(indisponibilite.pk))
    messages.error(request, "La proposition a expiré : reprenez la saisie depuis le début.")
    return redirect("ressources:declarer_indisponibilite_instructeur")


@exige_habilitation(ServiceIndisponibiliteInstructeur.PERMISSION_ECRITURE)
def vue_modifier_indisponibilite_instructeur(request, pk):
    indisponibilite = _indisponibilite_ou_404(pk)
    url_retour = _url_liste_filtree(indisponibilite.instructeur_id)
    if request.method == "POST":
        formulaire = FormulaireIndisponibiliteInstructeur(request.POST)
        if formulaire.is_valid():
            try:
                ServiceIndisponibiliteInstructeur.modifier(
                    request.user,
                    indisponibilite,
                    formulaire.cleaned_data["debut"],
                    formulaire.cleaned_data["fin"],
                    formulaire.cleaned_data["motif"],
                )
            except ErreurValidation as erreur:
                messages.error(request, str(erreur))
            else:
                messages.success(request, "Indisponibilité modifiée.")
                return redirect(url_retour)
    else:
        formulaire = FormulaireIndisponibiliteInstructeur(
            initial={
                "debut": indisponibilite.debut,
                "fin": indisponibilite.fin,
                "motif": indisponibilite.motif,
            }
        )
    return render(
        request,
        "noyau/gestion/formulaire.html",
        {
            "titre": f"Modifier l'indisponibilité — {indisponibilite.instructeur}",
            "legende": "Période et motif",
            "form": formulaire,
            "url_annuler": url_retour,
            "libelle_bouton": "Enregistrer",
        },
    )


@exige_habilitation(ServiceIndisponibiliteInstructeur.PERMISSION_ECRITURE)
def vue_confirmer_suppression_indisponibilite_instructeur(request, pk):
    indisponibilite = _indisponibilite_ou_404(pk)
    url_retour = _url_liste_filtree(indisponibilite.instructeur_id)
    if request.method == "POST":
        try:
            ServiceIndisponibiliteInstructeur.supprimer(request.user, indisponibilite)
        except ErreurValidation as erreur:
            messages.error(request, str(erreur))
        else:
            messages.success(request, "Indisponibilité supprimée.")
        return redirect(url_retour)
    return render(
        request,
        "noyau/gestion/confirmer_suppression.html",
        {
            "titre_dialogue": f"Supprimer l'indisponibilité de « {indisponibilite.instructeur} »",
            "texte_explication": (
                f"La période du {indisponibilite.debut:%d/%m/%Y %H:%M} au "
                f"{indisponibilite.fin:%d/%m/%Y %H:%M} sera supprimée définitivement."
            ),
            "url_annuler": url_retour,
        },
    )
