"""Vues de l'affectation individuelle des stagiaires — déplacement, retrait,
historique (CU-P3-06). Orchestrent, ne décident rien : toute la logique
métier vit dans organisation.services.affectation.ServiceAffectation.
"""

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

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
    brigades = [
        b for b in ServiceBrigade.lister(request.user, session) if b.pk != actuelle.brigade_id
    ]
    if request.method == "POST":
        formulaire, reponse = _traiter_deplacement(request, session, stagiaire, brigades)
        if reponse is not None:
            return reponse
    else:
        formulaire = FormulaireDeplacementStagiaire(
            brigades=brigades, initial={"date_effet": timezone.localdate()}
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
        formulaire = FormulaireRetraitAffectation(initial={"date_fin": timezone.localdate()})
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
