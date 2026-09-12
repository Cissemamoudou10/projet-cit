"""Vues de la répartition des stagiaires dans les brigades — CU-P3-06,
Prompt 25. Orchestrent, ne décident rien : la proposition, l'ajustement et
la validation vivent dans `organisation.repartition` et
`organisation.services.affectation`.

ÉTAT ENTRE LES REQUÊTES (§ 5) : la proposition ajustée est encodée en base64
(JSON dessous) dans un champ caché du formulaire de répartition, jamais
stockée côté serveur — même mécanisme que l'import de stagiaires
(`noyau.services.etat_transitoire`, généralisé à cette story, D-100/D-101).
"""

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse

from administration.habilitations import exige_habilitation
from noyau.exceptions import ErreurIntrouvable, ErreurValidation
from noyau.services import etat_transitoire
from organisation.repartition import proposition as proposition_module
from organisation.repartition.validation import valider
from organisation.services.affectation import ServiceAffectation
from organisation.services.brigade import ServiceBrigade
from organisation.services.session import ServiceSession
from organisation.services.stagiaire import ServiceStagiaire


def _session_ou_404(pk):
    try:
        return ServiceSession.obtenir(pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur


def _messages_uniques(textes):
    """Un avertissement identique répété pour chaque ligne (ex. une brigade
    sans salle, une par stagiaire proposé) ne s'affiche qu'une fois — un
    message dupliqué N fois n'apprend rien de plus au N-ième affichage."""
    vus = []
    for texte in textes:
        if texte not in vus:
            vus.append(texte)
    return vus


def _decoder_proposition(request):
    contenu = etat_transitoire.decoder(request.POST.get("proposition_b64", ""))
    if contenu is None:
        return None
    return proposition_module.deserialiser(contenu)


def _contexte_reel(request, session):
    brigades = ServiceAffectation.brigades_avec_affectations(request.user, session)
    non_affectes = proposition_module.stagiaires_sans_affectation_ouverte(session).order_by(
        "nom", "prenom"
    )
    return {
        "session": session,
        "brigades": brigades,
        "non_affectes": non_affectes,
        "url_proposer": reverse("organisation:proposer_repartition", args=[session.pk]),
    }


@exige_habilitation(ServiceStagiaire.PERMISSION_LECTURE)
def vue_repartition(request, session_pk):
    session = _session_ou_404(session_pk)
    return render(request, "organisation/repartition.html", _contexte_reel(request, session))


def _contexte_proposition(session, proposition):
    stagiaires = {s.pk: s for s in session.stagiaires.all()}
    brigades = list(session.brigades.order_by("designation"))
    par_brigade = [
        {
            "brigade": brigade,
            "stagiaires": [
                stagiaires[s_id]
                for s_id, b_id in proposition.affectations
                if b_id == brigade.pk and s_id in stagiaires
            ],
        }
        for brigade in brigades
    ]
    return {
        "brigades": brigades,
        "par_brigade": par_brigade,
        "non_affectes": [
            stagiaires[s_id] for s_id in proposition.non_affectes if s_id in stagiaires
        ],
        "proposition_b64": etat_transitoire.encoder(proposition_module.serialiser(proposition)),
    }


@exige_habilitation(ServiceStagiaire.PERMISSION_ECRITURE)
def vue_proposer_repartition(request, session_pk):
    session = _session_ou_404(session_pk)
    proposition = proposition_module.proposer(session)
    contexte = {"session": session, **_contexte_proposition(session, proposition)}
    return render(request, "organisation/repartition_proposition.html", contexte)


@exige_habilitation(ServiceStagiaire.PERMISSION_ECRITURE)
def vue_ajuster_repartition(request, session_pk):
    session = _session_ou_404(session_pk)
    proposition = _decoder_proposition(request)
    if proposition is None:
        messages.error(request, "La proposition a expiré : reprenez depuis le début.")
        return redirect("organisation:repartition_session", session.pk)
    stagiaire_id = int(request.POST.get("stagiaire_id"))
    brigade_id = request.POST.get("brigade_id") or None
    proposition = proposition_module.ajuster(
        proposition, stagiaire_id, int(brigade_id) if brigade_id else None
    )
    contexte = {"session": session, **_contexte_proposition(session, proposition)}
    return render(request, "organisation/repartition_proposition.html", contexte)


@exige_habilitation(ServiceStagiaire.PERMISSION_ECRITURE)
def vue_valider_repartition(request, session_pk):
    session = _session_ou_404(session_pk)
    proposition = _decoder_proposition(request)
    if proposition is None:
        messages.error(request, "La proposition a expiré : reprenez depuis le début.")
        return redirect("organisation:repartition_session", session.pk)
    try:
        rapport = valider(request.user, session, proposition)
    except ErreurValidation as erreur:
        messages.error(request, str(erreur))
        return redirect("organisation:repartition_session", session.pk)
    messages.success(request, f"{len(rapport.enregistrees)} affectation(s) enregistrée(s).")
    for motif in _messages_uniques(ligne.motif for ligne in rapport.refusees):
        messages.warning(request, motif)
    for texte in _messages_uniques(avert["message"] for avert in rapport.avertissements):
        messages.warning(request, texte)
    if rapport.stagiaires_non_affectes:
        messages.warning(
            request,
            f"{len(rapport.stagiaires_non_affectes)} stagiaire(s) restent sans brigade.",
        )
    return redirect("organisation:repartition_session", session.pk)


@exige_habilitation(ServiceStagiaire.PERMISSION_ECRITURE)
def vue_affecter_stagiaire(request, session_pk, pk):
    session = _session_ou_404(session_pk)
    stagiaire = ServiceStagiaire.obtenir(pk)
    brigade_id = request.POST.get("brigade_id")
    if not brigade_id:
        messages.error(request, "Choisissez une brigade avant de valider.")
        return redirect("organisation:repartition_session", session.pk)
    try:
        brigade = ServiceBrigade.obtenir(brigade_id)
        affectation = ServiceAffectation.affecter(request.user, stagiaire, brigade)
    except ErreurValidation as erreur:
        messages.error(request, str(erreur))
    else:
        messages.success(request, f"« {stagiaire} » affecté à « {brigade} ».")
        for avert in affectation.avertissements:
            messages.warning(request, avert["message"])
    return redirect("organisation:repartition_session", session.pk)
