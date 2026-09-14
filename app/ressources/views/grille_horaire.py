"""Vues de gestion des grilles horaires et de leurs créneaux — orchestrent,
ne décident rien. Toute la logique métier vit dans
ressources.services.grille_horaire.
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
from ressources.forms import (
    FormulaireCreneauType,
    FormulaireDuplicationGrilleHoraire,
    FormulaireGrilleHoraire,
)
from ressources.navigation import onglets_ressources
from ressources.services.grille_horaire import ServiceCreneauType, ServiceGrilleHoraire


def _grille_ou_404(pk):
    try:
        return ServiceGrilleHoraire.obtenir(pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur


def _creneau_ou_404(pk):
    try:
        return ServiceCreneauType.obtenir(pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur


def _etat_grille(grille):
    if grille.archive:
        return "Archivée"
    if grille.active:
        return "Active"
    return "Disponible"


def _ligne(grille, peut_ecrire):
    lien_intitule = format_html(
        '<a href="{}" class="text-marine-900 no-underline hover:underline">{}</a>',
        reverse("ressources:detail_grille_horaire", args=[grille.pk]),
        grille.intitule,
    )
    ligne = {
        "cellules": [
            lien_intitule,
            grille.creneaux.count(),
            _etat_grille(grille),
            grille.date_activation.strftime("%d/%m/%Y %H:%M") if grille.date_activation else "—",
            str(grille.activee_par) if grille.activee_par else "—",
        ],
        "libelle": grille.intitule,
        "archive": grille.archive,
    }
    if peut_ecrire:
        ligne["url_modifier"] = reverse("ressources:modifier_grille_horaire", args=[grille.pk])
        if not grille.active:
            ligne["url_archiver"] = reverse("ressources:archiver_grille_horaire", args=[grille.pk])
        if grille.archive:
            ligne["url_desarchiver"] = reverse(
                "ressources:desarchiver_grille_horaire", args=[grille.pk]
            )
    return ligne


def _filtres_champs_etat(etat):
    return [
        {
            "nom": "etat",
            "libelle": "État",
            "valeur": etat,
            "choix": [
                ("active", "Active"),
                ("disponible", "Disponible"),
                ("archivee", "Archivée"),
            ],
        }
    ]


_COLONNES_GRILLES = [
    {"libelle": "Intitulé", "cle_tri": None},
    {"libelle": "Créneaux", "cle_tri": None},
    {"libelle": "État", "cle_tri": None},
    {"libelle": "Dernière activation", "cle_tri": None},
    {"libelle": "Agent", "cle_tri": None},
]


@exige_habilitation(ServiceGrilleHoraire.PERMISSION_LECTURE)
def vue_liste_grilles_horaires(request):
    etat = request.GET.get("etat", "")
    filtres = {"etat": etat}
    page = ServiceGrilleHoraire.lister(request.user, filtres, request.GET.get("page"))
    peut_ecrire = a_permission(request.user, ServiceGrilleHoraire.PERMISSION_ECRITURE)
    onglets, onglet_actif = onglets_ressources(request.user, "grilles-horaires")
    contexte = {
        "titre": "Grilles horaires",
        "sous_titre": "Squelettes de semaine — RG-62 : une seule grille active à la fois.",
        "onglets": onglets,
        "onglet_actif": onglet_actif,
        "url_creer": reverse("ressources:creer_grille_horaire") if peut_ecrire else "",
        "libelle_creer": "Créer une grille",
        "masquer_filtre_archive": True,
        "filtres": filtres,
        "filtres_champs": _filtres_champs_etat(etat),
        "url_liste": reverse("ressources:liste_grilles_horaires"),
        "colonnes": _COLONNES_GRILLES,
        "lignes": [_ligne(grille, peut_ecrire) for grille in page] if page else [],
        "libelle_vide": "Aucune grille ne correspond au filtre",
        "texte_vide": "Ajustez le filtre ou réinitialisez-le.",
        "page": page,
    }
    return render(request, "noyau/gestion/liste.html", contexte)


@exige_habilitation(ServiceGrilleHoraire.PERMISSION_LECTURE)
def vue_detail_grille_horaire(request, pk):
    grille = _grille_ou_404(pk)
    peut_ecrire = a_permission(request.user, ServiceGrilleHoraire.PERMISSION_ECRITURE)
    volume = ServiceGrilleHoraire.volume_hebdomadaire_reference() if grille.active else None
    return render(
        request,
        "ressources/grille_horaire_detail.html",
        {
            "grille": grille,
            "semaine": ServiceGrilleHoraire.semaine_type(grille),
            "peut_ecrire": peut_ecrire,
            "volume_hebdomadaire": volume,
            "url_liste": reverse("ressources:liste_grilles_horaires"),
            "url_modifier": reverse("ressources:modifier_grille_horaire", args=[grille.pk]),
            "url_dupliquer": reverse("ressources:dupliquer_grille_horaire", args=[grille.pk]),
            "url_supprimer": reverse("ressources:supprimer_grille_horaire", args=[grille.pk]),
            "url_archiver": reverse("ressources:archiver_grille_horaire", args=[grille.pk]),
            "url_desarchiver": reverse("ressources:desarchiver_grille_horaire", args=[grille.pk]),
            "url_activer": reverse(
                "ressources:confirmer_activation_grille_horaire", args=[grille.pk]
            ),
            "url_ajouter_creneau": reverse("ressources:ajouter_creneau", args=[grille.pk]),
            "form_creneau": FormulaireCreneauType(),
        },
    )


@exige_habilitation(ServiceGrilleHoraire.PERMISSION_ECRITURE)
def vue_creer_grille_horaire(request):
    if request.method == "POST":
        formulaire = FormulaireGrilleHoraire(request.POST)
        if formulaire.is_valid():
            try:
                grille = ServiceGrilleHoraire.creer(
                    request.user, formulaire.cleaned_data["intitule"]
                )
            except ErreurValidation as erreur:
                messages.error(request, str(erreur))
            else:
                messages.success(request, "Grille créée.")
                return redirect("ressources:detail_grille_horaire", pk=grille.pk)
    else:
        formulaire = FormulaireGrilleHoraire()
    return render(
        request,
        "noyau/gestion/formulaire.html",
        {
            "titre": "Créer une grille horaire",
            "legende": "Grille",
            "form": formulaire,
            "url_annuler": reverse("ressources:liste_grilles_horaires"),
            "libelle_bouton": "Créer la grille",
        },
    )


@exige_habilitation(ServiceGrilleHoraire.PERMISSION_ECRITURE)
def vue_modifier_grille_horaire(request, pk):
    grille = _grille_ou_404(pk)
    if request.method == "POST":
        formulaire = FormulaireGrilleHoraire(request.POST)
        modifie_le_attendu = modifie_le_attendu_depuis_requete(request)
        if formulaire.is_valid():
            try:
                ServiceGrilleHoraire.modifier(
                    request.user, pk, formulaire.cleaned_data["intitule"], modifie_le_attendu
                )
            except (ErreurValidation, ErreurModificationConcurrente) as erreur:
                messages.error(request, str(erreur))
            else:
                messages.success(request, "Grille modifiée.")
                return redirect("ressources:detail_grille_horaire", pk=grille.pk)
    else:
        formulaire = FormulaireGrilleHoraire(initial={"intitule": grille.intitule})
    return render(
        request,
        "noyau/gestion/formulaire.html",
        {
            "titre": f"Modifier « {grille.intitule} »",
            "legende": "Grille",
            "form": formulaire,
            "url_annuler": reverse("ressources:detail_grille_horaire", args=[grille.pk]),
            "libelle_bouton": "Enregistrer",
            "modifie_le_attendu": grille.modifie_le,
        },
    )


@exige_habilitation(ServiceGrilleHoraire.PERMISSION_ECRITURE)
def vue_dupliquer_grille_horaire(request, pk):
    source = _grille_ou_404(pk)
    if request.method == "POST":
        formulaire = FormulaireDuplicationGrilleHoraire(request.POST)
        if formulaire.is_valid():
            try:
                copie = ServiceGrilleHoraire.dupliquer(
                    request.user, pk, formulaire.cleaned_data["intitule"]
                )
            except ErreurValidation as erreur:
                messages.error(request, str(erreur))
            else:
                messages.success(
                    request, f"« {copie.intitule} » créée à partir de « {source.intitule} »."
                )
                return redirect("ressources:detail_grille_horaire", pk=copie.pk)
    else:
        formulaire = FormulaireDuplicationGrilleHoraire()
    return render(
        request,
        "noyau/gestion/formulaire.html",
        {
            "titre": f"Dupliquer « {source.intitule} »",
            "legende": "Nouvelle grille",
            "form": formulaire,
            "url_annuler": reverse("ressources:detail_grille_horaire", args=[source.pk]),
            "libelle_bouton": "Dupliquer",
        },
    )


@exige_habilitation(ServiceGrilleHoraire.PERMISSION_ECRITURE)
def vue_confirmer_archivage_grille_horaire(request, pk):
    grille = _grille_ou_404(pk)
    if request.method == "POST":
        try:
            ServiceGrilleHoraire.archiver(request.user, pk)
        except ErreurValidation as erreur:
            messages.error(request, str(erreur))
        else:
            messages.success(request, "Grille archivée.")
        return redirect("ressources:detail_grille_horaire", pk=grille.pk)
    return render(
        request,
        "noyau/gestion/confirmer_archivage.html",
        {
            "titre_dialogue": f"Archiver « {grille.intitule} »",
            "texte_explication": (
                f"« {grille.intitule} » ne sera plus proposée à l'activation. "
                "Ses créneaux restent consultables."
            ),
            "url_annuler": reverse("ressources:detail_grille_horaire", args=[grille.pk]),
        },
    )


@exige_habilitation(ServiceGrilleHoraire.PERMISSION_ECRITURE)
def vue_desarchiver_grille_horaire(request, pk):
    grille = _grille_ou_404(pk)
    if request.method == "POST":
        ServiceGrilleHoraire.desarchiver(request.user, pk)
        messages.success(request, "Grille désarchivée.")
    return redirect("ressources:detail_grille_horaire", pk=grille.pk)


@exige_habilitation(ServiceGrilleHoraire.PERMISSION_ECRITURE)
def vue_confirmer_suppression_grille_horaire(request, pk):
    grille = _grille_ou_404(pk)
    if request.method == "POST":
        try:
            ServiceGrilleHoraire.supprimer(request.user, pk)
        except ErreurValidation as erreur:
            messages.error(request, str(erreur))
            return redirect("ressources:detail_grille_horaire", pk=grille.pk)
        messages.success(request, "Grille supprimée.")
        return redirect("ressources:liste_grilles_horaires")
    return render(
        request,
        "noyau/gestion/confirmer_suppression.html",
        {
            "titre_dialogue": f"Supprimer « {grille.intitule} »",
            "texte_explication": f"« {grille.intitule} » sera supprimée définitivement, avec "
            "tous ses créneaux.",
            "url_annuler": reverse("ressources:detail_grille_horaire", args=[grille.pk]),
        },
    )


@exige_habilitation(ServiceGrilleHoraire.PERMISSION_ECRITURE)
def vue_confirmer_activation_grille_horaire(request, pk):
    """L'activation NOMME la grille désactivée (§ 9, Prompt 29) : un
    changement de grille active modifie le fonctionnement de tout le
    centre."""
    grille = _grille_ou_404(pk)
    actuelle = ServiceGrilleHoraire.autre_grille_active(pk)
    if request.method == "POST":
        try:
            ServiceGrilleHoraire.activer(request.user, pk)
        except ErreurValidation as erreur:
            messages.error(request, str(erreur))
        else:
            messages.success(request, f"« {grille.intitule} » activée.")
        return redirect("ressources:detail_grille_horaire", pk=grille.pk)
    return render(
        request,
        "ressources/grille_horaire_confirmer_activation.html",
        {
            "grille": grille,
            "grille_desactivee": actuelle,
            "url_annuler": reverse("ressources:detail_grille_horaire", args=[grille.pk]),
        },
    )


@exige_habilitation(ServiceGrilleHoraire.PERMISSION_ECRITURE)
def vue_ajouter_creneau(request, grille_pk):
    grille = _grille_ou_404(grille_pk)
    formulaire = FormulaireCreneauType(request.POST)
    if formulaire.is_valid():
        try:
            ServiceCreneauType.ajouter(request.user, grille, formulaire.cleaned_data)
        except ErreurValidation as erreur:
            messages.error(request, str(erreur))
        else:
            messages.success(request, "Créneau ajouté.")
    else:
        messages.error(request, "Créneau invalide : vérifiez le jour, le rang et les heures.")
    return redirect("ressources:detail_grille_horaire", pk=grille.pk)


@exige_habilitation(ServiceGrilleHoraire.PERMISSION_ECRITURE)
def vue_confirmer_suppression_creneau(request, pk):
    creneau = _creneau_ou_404(pk)
    url_retour = reverse("ressources:detail_grille_horaire", args=[creneau.grille_id])
    if request.method == "POST":
        ServiceCreneauType.supprimer(request.user, creneau)
        messages.success(request, "Créneau supprimé.")
        return redirect(url_retour)
    return render(
        request,
        "noyau/gestion/confirmer_suppression.html",
        {
            "titre_dialogue": f"Supprimer le créneau {creneau.heure_debut:%H:%M}–{creneau.heure_fin:%H:%M}",
            "texte_explication": (
                f"Le créneau du {creneau.get_jour_semaine_display().lower()} sera supprimé "
                f"de la grille « {creneau.grille.intitule} »."
            ),
            "url_annuler": url_retour,
        },
    )
