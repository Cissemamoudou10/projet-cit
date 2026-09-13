"""Vues de LECTURE du calendrier académique annuel — vue annuelle (repérage,
§ 6, Prompt 28) et vue mensuelle (détail horaire, critère 3). Orchestrent,
ne décident rien : toute la logique vit dans
ressources.services.periode_calendrier.ServicePeriodeCalendrier.
"""

import datetime

from django.conf import settings
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from administration.habilitations import exige_habilitation
from noyau.habilitations import a_permission
from ressources.navigation import onglets_ressources
from ressources.services.nature_evenement import ServiceNatureEvenement
from ressources.services.periode_calendrier import ServicePeriodeCalendrier

NOMS_MOIS = [
    "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
    "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre",
]  # fmt: skip


def _mois_suivant(jour):
    if jour.month == 12:
        return jour.replace(year=jour.year + 1, month=1)
    return jour.replace(month=jour.month + 1)


def _debut_journee(jour):
    return timezone.make_aware(datetime.datetime.combine(jour, datetime.time.min))


def _annee_du_parametre(request):
    valeur = request.GET.get("annee")
    if valeur and valeur.isdigit():
        return int(valeur)
    aujourdhui = timezone.localdate()
    mois_debut = settings.MOIS_DEBUT_ANNEE_FORMATION
    return aujourdhui.year if aujourdhui.month >= mois_debut else aujourdhui.year - 1


def _fenetre_annee(annee):
    mois_debut = settings.MOIS_DEBUT_ANNEE_FORMATION
    return datetime.date(annee, mois_debut, 1), datetime.date(annee + 1, mois_debut, 1)


def _filtres_cible(request):
    return {
        "nature": request.GET.get("nature", ""),
        "effet": request.GET.get("effet", ""),
        "session": request.GET.get("session", ""),
        "brigade": request.GET.get("brigade", ""),
    }


def _pastille_periode(periode):
    est_bloquant = periode.effet == "bloquant"
    classe = (
        "border-etat-ecart text-etat-ecart" if est_bloquant else "border-marine-700 text-marine-700"
    )
    sigle = "BLOQUANT" if est_bloquant else "INFORMATIF"
    return {
        "url": reverse("ressources:detail_periode_calendrier", args=[periode.pk]),
        "texte": format_html(
            '<span class="border {} px-1.5 py-px text-2xs font-semibold">{} — {} — {}</span>',
            classe,
            periode.intitule,
            periode.nature.libelle.upper(),
            sigle,
        ),
    }


def _pastille_session(session):
    return {
        "url": reverse("organisation:detail_session", args=[session.pk]),
        "texte": mark_safe(
            f'<span class="border border-gris-trait text-gris-lecture px-1.5 py-px '
            f'text-2xs font-semibold">{session} — SESSION</span>'
        ),
    }


def _pastilles_du_mois(debut_mois, fin_mois, periodes, bandes):
    debut_dt, fin_dt = _debut_journee(debut_mois), _debut_journee(fin_mois)
    pastilles = [_pastille_periode(p) for p in periodes if p.debut < fin_dt and p.fin > debut_dt]
    pastilles += [
        _pastille_session(s) for s in bandes if s.date_debut < fin_mois and s.date_fin >= debut_mois
    ]
    return pastilles


def _construire_mois(fenetre_debut, fenetre_fin, periodes, bandes):
    mois, curseur = [], fenetre_debut
    while curseur < fenetre_fin:
        curseur_fin = _mois_suivant(curseur)
        mois.append(
            {
                "libelle": f"{NOMS_MOIS[curseur.month - 1]} {curseur.year}",
                "url_mensuel": (
                    f"{reverse('ressources:calendrier_mensuel')}?annee={curseur.year}"
                    f"&mois={curseur.month}"
                ),
                "pastilles": _pastilles_du_mois(curseur, curseur_fin, periodes, bandes),
            }
        )
        curseur = curseur_fin
    return mois


@exige_habilitation(ServicePeriodeCalendrier.PERMISSION_LECTURE)
def vue_calendrier_annuel(request):
    annee = _annee_du_parametre(request)
    fenetre_debut, fenetre_fin = _fenetre_annee(annee)
    filtres = {
        **_filtres_cible(request),
        "fenetre_debut": _debut_journee(fenetre_debut),
        "fenetre_fin": _debut_journee(fenetre_fin),
    }
    periodes = list(ServicePeriodeCalendrier.lister(request.user, filtres))
    bandes = list(
        ServicePeriodeCalendrier.bandes_sessions(
            request.user, fenetre_debut, fenetre_fin - datetime.timedelta(days=1)
        )
    )
    mois = _construire_mois(fenetre_debut, fenetre_fin, periodes, bandes)
    onglets, onglet_actif = onglets_ressources(request.user, "calendrier")
    return render(
        request,
        "ressources/calendrier_annuel.html",
        {
            "titre": f"Calendrier {annee}-{annee + 1}",
            "sous_titre": "Vue de repérage — quand une période a lieu, pas combien d'heures.",
            "onglets": onglets,
            "onglet_actif": onglet_actif,
            "annee": annee,
            "annee_precedente": annee - 1,
            "annee_suivante": annee + 1,
            "mois": mois,
            "filtres": filtres,
            "filtres_champs": _filtres_champs(filtres),
            "peut_ecrire": a_permission(request.user, ServicePeriodeCalendrier.PERMISSION_ECRITURE),
            "url_declarer": reverse("ressources:declarer_periode_calendrier"),
            "url_natures": reverse("ressources:liste_natures_evenement"),
        },
    )


def _filtres_champs(filtres):
    return [
        {
            "nom": "nature",
            "libelle": "Nature",
            "valeur": filtres["nature"],
            "choix": ServiceNatureEvenement.choix_natures(),
        },
        {
            "nom": "effet",
            "libelle": "Effet",
            "valeur": filtres["effet"],
            "choix": ServiceNatureEvenement.choix_effet(),
        },
        {
            "nom": "session",
            "libelle": "Session",
            "valeur": filtres["session"],
            "choix": ServicePeriodeCalendrier.choix_sessions(),
        },
        {
            "nom": "brigade",
            "libelle": "Brigade",
            "valeur": filtres["brigade"],
            "choix": ServicePeriodeCalendrier.choix_brigades(),
        },
    ]


@exige_habilitation(ServicePeriodeCalendrier.PERMISSION_LECTURE)
def vue_calendrier_mensuel(request):
    annee = _annee_du_parametre(request)
    mois_numero = request.GET.get("mois")
    mois_numero = (
        int(mois_numero) if mois_numero and mois_numero.isdigit() else timezone.localdate().month
    )
    debut_mois = datetime.date(annee, mois_numero, 1)
    fin_mois = _mois_suivant(debut_mois)
    filtres = {
        **_filtres_cible(request),
        "fenetre_debut": _debut_journee(debut_mois),
        "fenetre_fin": _debut_journee(fin_mois),
    }
    periodes = list(ServicePeriodeCalendrier.lister(request.user, filtres))
    bandes = list(
        ServicePeriodeCalendrier.bandes_sessions(
            request.user, debut_mois, fin_mois - datetime.timedelta(days=1)
        )
    )
    jours, curseur = [], debut_mois
    while curseur < fin_mois:
        jours.append(_ligne_jour(curseur, periodes, bandes))
        curseur += datetime.timedelta(days=1)
    onglets, onglet_actif = onglets_ressources(request.user, "calendrier")
    return render(
        request,
        "ressources/calendrier_mensuel.html",
        {
            "titre": f"{NOMS_MOIS[mois_numero - 1]} {annee}",
            "sous_titre": "Détail horaire du mois — RG-28 : la journée n'est pas l'unité du calendrier.",
            "onglets": onglets,
            "onglet_actif": onglet_actif,
            "annee": annee,
            "mois_numero": mois_numero,
            "url_annuel": f"{reverse('ressources:calendrier_annuel')}?annee={annee}",
            "jours": jours,
        },
    )


def _plage_du_jour(periode, debut_jour, fin_jour):
    """Une période à cheval sur plusieurs jours (bivouac, congé) n'a pas
    d'heures propres à CE jour-là : « 00:00–00:00 » serait lisible comme un
    événement de durée nulle. Affiche « Toute la journée » quand la période
    couvre le jour entier, sinon la plage réellement bornée par ce jour
    (RG-28 : la journée reste l'angle d'affichage, jamais l'unité de saisie)."""
    debut_effectif = max(periode.debut, debut_jour)
    fin_effective = min(periode.fin, fin_jour)
    if debut_effectif <= debut_jour and fin_effective >= fin_jour:
        return "Toute la journée"
    return f"{debut_effectif:%H:%M}–{fin_effective:%H:%M}"


def _ligne_jour(jour, periodes, bandes):
    debut_dt, fin_dt = _debut_journee(jour), _debut_journee(jour + datetime.timedelta(days=1))
    entrees = [
        f"{_plage_du_jour(p, debut_dt, fin_dt)} {p.intitule} ({p.nature.libelle}, {p.get_effet_display()})"
        for p in periodes
        if p.debut < fin_dt and p.fin > debut_dt
    ]
    entrees += [f"Session : {s}" for s in bandes if s.date_debut <= jour <= s.date_fin]
    return {"date": jour, "entrees": entrees}
