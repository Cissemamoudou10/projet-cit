"""Vues de l'affectation individuelle des stagiaires — déplacement, retrait,
historique (CU-P3-06). Orchestrent, ne décident rien : toute la logique
métier vit dans organisation.services.affectation.ServiceAffectation.
"""

import datetime

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse

from administration.habilitations import exige_habilitation
from noyau.exceptions import ErreurIntrouvable, ErreurValidation
from organisation.forms import FormulaireDeplacementStagiaire, FormulaireRetraitAffectation
from organisation.services.affectation import ServiceAffectation
from organisation.services.brigade import ServiceBrigade
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


def _premiere_date_valide(actuelle):
    """Plus petite date acceptable pour fermer `actuelle` (déplacement ou
    retrait) : le lendemain de sa date d'effet — `ck_affectation_dates`
    exige une durée strictement positive (§ 3, Prompt 25), donc jamais le
    jour même, y compris si `actuelle` a été ouverte aujourd'hui. Peut
    tomber dans le futur : dans ce cas, l'appelant refuse l'action plutôt
    que de présenter un formulaire voué à l'échec."""
    return actuelle.date_effet + datetime.timedelta(days=1)


def _refuser_si_trop_tot(request, session, stagiaire, actuelle, verbe):
    date_minimale = _premiere_date_valide(actuelle)
    if date_minimale <= datetime.date.today():
        return None
    messages.error(
        request,
        f"« {stagiaire} » a été affecté à « {actuelle.brigade} » le "
        f"{actuelle.date_effet:%d/%m/%Y} : un {verbe} ne peut prendre effet avant le "
        f"{date_minimale:%d/%m/%Y} (une affectation dure au moins un jour).",
    )
    return redirect("organisation:repartition_session", session.pk)


@exige_habilitation(ServiceStagiaire.PERMISSION_LECTURE)
def vue_historique_affectations(request, session_pk, pk):
    session = _session_ou_404(session_pk)
    stagiaire = _stagiaire_ou_404(pk)
    historique = ServiceAffectation.historique(request.user, stagiaire)
    return render(
        request,
        "organisation/stagiaire_historique.html",
        {
            "session": session,
            "stagiaire": stagiaire,
            "historique": historique,
            "url_retour": reverse("organisation:liste_stagiaires", args=[session.pk]),
        },
    )


def _traiter_deplacement(request, session, stagiaire, brigades):
    """Retourne une redirection si le déplacement a réussi, sinon `None` —
    le formulaire invalide ou l'erreur métier restent à afficher par
    l'appelant."""
    formulaire = FormulaireDeplacementStagiaire(request.POST, brigades=brigades)
    if not formulaire.is_valid():
        return formulaire, None
    try:
        nouvelle_brigade = ServiceBrigade.obtenir(formulaire.cleaned_data["brigade"])
        ServiceAffectation.deplacer(
            request.user, stagiaire, nouvelle_brigade, formulaire.cleaned_data["date_effet"]
        )
    except ErreurValidation as erreur:
        messages.error(request, str(erreur))
        return formulaire, None
    messages.success(request, f"« {stagiaire} » déplacé vers « {nouvelle_brigade} ».")
    return formulaire, redirect("organisation:repartition_session", session.pk)


@exige_habilitation(ServiceStagiaire.PERMISSION_ECRITURE)
def vue_deplacer_stagiaire(request, session_pk, pk):
    session = _session_ou_404(session_pk)
    stagiaire = _stagiaire_ou_404(pk)
    actuelle = ServiceAffectation.affectation_ouverte(stagiaire)
    if actuelle is None:
        messages.error(request, f"« {stagiaire} » n'a aucune affectation ouverte à déplacer.")
        return redirect("organisation:liste_stagiaires", session.pk)
    refus = _refuser_si_trop_tot(request, session, stagiaire, actuelle, "déplacement")
    if refus is not None:
        return refus
    brigades = [
        b for b in ServiceBrigade.lister(request.user, session) if b.pk != actuelle.brigade_id
    ]
    if request.method == "POST":
        formulaire, reponse = _traiter_deplacement(request, session, stagiaire, brigades)
        if reponse is not None:
            return reponse
    else:
        formulaire = FormulaireDeplacementStagiaire(
            brigades=brigades, initial={"date_effet": _premiere_date_valide(actuelle)}
        )
    return render(
        request,
        "organisation/stagiaire_deplacer.html",
        {
            "session": session,
            "stagiaire": stagiaire,
            "brigade_actuelle": actuelle.brigade,
            "form": formulaire,
            "url_annuler": reverse("organisation:repartition_session", args=[session.pk]),
        },
    )


@exige_habilitation(ServiceStagiaire.PERMISSION_ECRITURE)
def vue_retirer_affectation(request, session_pk, pk):
    session = _session_ou_404(session_pk)
    stagiaire = _stagiaire_ou_404(pk)
    actuelle = ServiceAffectation.affectation_ouverte(stagiaire)
    if actuelle is None:
        messages.error(request, f"« {stagiaire} » n'a aucune affectation ouverte à retirer.")
        return redirect("organisation:liste_stagiaires", session.pk)
    refus = _refuser_si_trop_tot(request, session, stagiaire, actuelle, "retrait")
    if refus is not None:
        return refus
    if request.method == "POST":
        formulaire = FormulaireRetraitAffectation(request.POST)
        if formulaire.is_valid():
            try:
                ServiceAffectation.retirer(
                    request.user, stagiaire, formulaire.cleaned_data["date_fin"]
                )
            except ErreurValidation as erreur:
                messages.error(request, str(erreur))
            else:
                messages.success(request, f"« {stagiaire} » retiré de « {actuelle.brigade} ».")
                return redirect("organisation:repartition_session", session.pk)
    else:
        formulaire = FormulaireRetraitAffectation(
            initial={"date_fin": _premiere_date_valide(actuelle)}
        )
    return render(
        request,
        "organisation/stagiaire_retirer.html",
        {
            "session": session,
            "stagiaire": stagiaire,
            "brigade_actuelle": actuelle.brigade,
            "form": formulaire,
            "url_annuler": reverse("organisation:repartition_session", args=[session.pk]),
        },
    )
