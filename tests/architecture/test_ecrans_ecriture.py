"""Un seul endroit pour toute adresse d'écriture du système, et le refus
qu'elle doit opposer à qui n'a pas la permission requise — bloc D.2 du
Prompt 19. Même mécanisme que la matrice d'US-ADM-03
(administration/tests/test_matrice_habilitations.py) et le masquage
d'US-REF-07 (referentiel/tests/test_masquage_ecriture.py) : une table
déclarative, un test qui l'itère.

Remplace l'ancienne liste locale de `referentiel/tests/test_refus_ecriture_
direct.py` (23 adresses, US-REF-07 seulement) par une table couvrant les
trois applications — cette table est désormais la source unique, croisée
par `test_toute_vue_ecriture_figure_dans_la_table` avec les vues réellement
décorées par `exige_habilitation` dans tout le projet.
"""

import dataclasses
from collections.abc import Callable

import pytest
from django.urls import URLPattern, URLResolver, get_resolver, reverse

from administration.constantes import GROUPES, MATRICE


@dataclasses.dataclass(frozen=True)
class EcranEcriture:
    nom: str
    permission: str
    args: Callable[[dict], list] = lambda objets: []
    methode: str = "POST"


ECRANS_ECRITURE = [
    # --- administration : comptes et habilitations (US-ADM-02, US-ADM-03) ---
    # liste_comptes est un écran de LECTURE, mais § 11.2 ne donne aucune
    # lecture séparée du domaine administration aux profils non-administrateur
    # (voir HABILITATIONS.md) : la vue est gardée par la même permission
    # d'écriture, la table de garde le détecte donc à raison — déjà couvert
    # par ailleurs (test_vues_authentification.py), entrée redondante mais
    # honnête plutôt qu'une exception silencieuse au mécanisme de garde.
    EcranEcriture("administration:liste_comptes", "noyau.administration_ecriture"),
    EcranEcriture("administration:creer_compte", "noyau.administration_ecriture"),
    EcranEcriture(
        "administration:modifier_compte",
        "noyau.administration_ecriture",
        lambda objets: [objets["compte_cible"].pk],
    ),
    EcranEcriture(
        "administration:desactiver_compte",
        "noyau.administration_ecriture",
        lambda objets: [objets["compte_cible"].pk],
    ),
    EcranEcriture(
        "administration:reactiver_compte",
        "noyau.administration_ecriture",
        lambda objets: [objets["compte_cible"].pk],
    ),
    EcranEcriture("administration:habilitations", "noyau.administration_ecriture"),
    # --- referentiel : types de formation (US-REF-00) ---
    EcranEcriture("referentiel:creer_type_formation", "noyau.referentiel_ecriture"),
    EcranEcriture(
        "referentiel:modifier_type_formation",
        "noyau.referentiel_ecriture",
        lambda objets: [objets["type_formation"].pk],
    ),
    EcranEcriture(
        "referentiel:archiver_type_formation",
        "noyau.referentiel_ecriture",
        lambda objets: [objets["type_formation"].pk],
    ),
    EcranEcriture(
        "referentiel:desarchiver_type_formation",
        "noyau.referentiel_ecriture",
        lambda objets: [objets["type_formation"].pk],
    ),
    EcranEcriture(
        "referentiel:supprimer_type_formation",
        "noyau.referentiel_ecriture",
        lambda objets: [objets["type_formation"].pk],
    ),
    # --- referentiel : formations (US-REF-01) ---
    EcranEcriture("referentiel:creer_formation", "noyau.referentiel_ecriture"),
    EcranEcriture(
        "referentiel:modifier_formation",
        "noyau.referentiel_ecriture",
        lambda objets: [objets["formation"].pk],
    ),
    EcranEcriture(
        "referentiel:archiver_formation",
        "noyau.referentiel_ecriture",
        lambda objets: [objets["formation"].pk],
    ),
    EcranEcriture(
        "referentiel:desarchiver_formation",
        "noyau.referentiel_ecriture",
        lambda objets: [objets["formation"].pk],
    ),
    EcranEcriture(
        "referentiel:supprimer_formation",
        "noyau.referentiel_ecriture",
        lambda objets: [objets["formation"].pk],
    ),
    # --- referentiel : matières (US-REF-02) ---
    EcranEcriture("referentiel:creer_matiere", "noyau.referentiel_ecriture"),
    EcranEcriture(
        "referentiel:modifier_matiere",
        "noyau.referentiel_ecriture",
        lambda objets: [objets["matiere"].pk],
    ),
    EcranEcriture(
        "referentiel:archiver_matiere",
        "noyau.referentiel_ecriture",
        lambda objets: [objets["matiere"].pk],
    ),
    EcranEcriture(
        "referentiel:desarchiver_matiere",
        "noyau.referentiel_ecriture",
        lambda objets: [objets["matiere"].pk],
    ),
    EcranEcriture(
        "referentiel:supprimer_matiere",
        "noyau.referentiel_ecriture",
        lambda objets: [objets["matiere"].pk],
    ),
    # --- referentiel : composition du référentiel (US-REF-03/04) ---
    EcranEcriture(
        "referentiel:rattacher_matiere",
        "noyau.referentiel_ecriture",
        lambda objets: [objets["formation"].pk],
    ),
    EcranEcriture(
        "referentiel:creer_matiere_depuis_referentiel",
        "noyau.referentiel_ecriture",
        lambda objets: [objets["formation"].pk],
    ),
    EcranEcriture(
        "referentiel:modifier_element_referentiel",
        "noyau.referentiel_ecriture",
        lambda objets: [objets["formation"].pk, objets["element"].pk],
    ),
    EcranEcriture(
        "referentiel:retirer_element_referentiel",
        "noyau.referentiel_ecriture",
        lambda objets: [objets["formation"].pk, objets["element"].pk],
    ),
    # --- referentiel : objectifs pédagogiques (US-REF-05) ---
    EcranEcriture(
        "referentiel:ajouter_objectif_pedagogique",
        "noyau.referentiel_ecriture",
        lambda objets: [objets["matiere"].pk],
    ),
    EcranEcriture(
        "referentiel:modifier_objectif_pedagogique",
        "noyau.referentiel_ecriture",
        lambda objets: [objets["matiere"].pk, objets["objectif"].pk],
    ),
    EcranEcriture(
        "referentiel:monter_objectif_pedagogique",
        "noyau.referentiel_ecriture",
        lambda objets: [objets["matiere"].pk, objets["objectif"].pk],
    ),
    EcranEcriture(
        "referentiel:descendre_objectif_pedagogique",
        "noyau.referentiel_ecriture",
        lambda objets: [objets["matiere"].pk, objets["objectif"].pk],
    ),
    EcranEcriture(
        "referentiel:supprimer_objectif_pedagogique",
        "noyau.referentiel_ecriture",
        lambda objets: [objets["matiere"].pk, objets["objectif"].pk],
    ),
    # --- referentiel : prérequis (US-REF-06) ---
    EcranEcriture(
        "referentiel:ajouter_prerequis",
        "noyau.referentiel_ecriture",
        lambda objets: [objets["formation"].pk, objets["element"].pk],
    ),
    EcranEcriture(
        "referentiel:supprimer_prerequis",
        "noyau.referentiel_ecriture",
        lambda objets: [objets["formation"].pk, objets["prerequis"].pk],
    ),
    # --- organisation : sessions (US-SES-01) ---
    EcranEcriture("organisation:creer_session", "noyau.organisation_ecriture"),
    EcranEcriture(
        "organisation:modifier_session",
        "noyau.organisation_ecriture",
        lambda objets: [objets["session"].pk],
    ),
    EcranEcriture(
        "organisation:supprimer_session",
        "noyau.organisation_ecriture",
        lambda objets: [objets["session"].pk],
    ),
    # --- organisation : brigades (US-SES-02) ---
    EcranEcriture(
        "organisation:creer_brigade",
        "noyau.organisation_ecriture",
        lambda objets: [objets["session"].pk],
    ),
    EcranEcriture(
        "organisation:modifier_brigade",
        "noyau.organisation_ecriture",
        lambda objets: [objets["session"].pk, objets["brigade"].pk],
    ),
    EcranEcriture(
        "organisation:supprimer_brigade",
        "noyau.organisation_ecriture",
        lambda objets: [objets["session"].pk, objets["brigade"].pk],
    ),
    # --- organisation : stagiaires (US-SES-05) ---
    EcranEcriture(
        "organisation:creer_stagiaire",
        "noyau.organisation_ecriture",
        lambda objets: [objets["session"].pk],
    ),
    EcranEcriture(
        "organisation:modifier_stagiaire",
        "noyau.organisation_ecriture",
        lambda objets: [objets["session"].pk, objets["stagiaire"].pk],
    ),
    EcranEcriture(
        "organisation:radier_stagiaire",
        "noyau.organisation_ecriture",
        lambda objets: [objets["session"].pk, objets["stagiaire"].pk],
    ),
    EcranEcriture(
        "organisation:deradier_stagiaire",
        "noyau.organisation_ecriture",
        lambda objets: [objets["session"].pk, objets["stagiaire"].pk],
    ),
    EcranEcriture(
        "organisation:supprimer_stagiaire",
        "noyau.organisation_ecriture",
        lambda objets: [objets["session"].pk, objets["stagiaire"].pk],
    ),
    EcranEcriture(
        "organisation:importer_stagiaires",
        "noyau.organisation_ecriture",
        lambda objets: [objets["session"].pk],
    ),
    EcranEcriture(
        "organisation:confirmer_import_stagiaires",
        "noyau.organisation_ecriture",
        lambda objets: [objets["session"].pk],
    ),
    EcranEcriture(
        "organisation:modele_import_stagiaires",
        "noyau.organisation_ecriture",
        lambda objets: [objets["session"].pk],
    ),
    # --- organisation : répartition dans les brigades (US-SES-06) ---
    EcranEcriture(
        "organisation:deplacer_stagiaire",
        "noyau.organisation_ecriture",
        lambda objets: [objets["session"].pk, objets["stagiaire"].pk],
    ),
    EcranEcriture(
        "organisation:retirer_affectation",
        "noyau.organisation_ecriture",
        lambda objets: [objets["session"].pk, objets["stagiaire"].pk],
    ),
    EcranEcriture(
        "organisation:affecter_stagiaire",
        "noyau.organisation_ecriture",
        lambda objets: [objets["session"].pk, objets["stagiaire"].pk],
    ),
    EcranEcriture(
        "organisation:proposer_repartition",
        "noyau.organisation_ecriture",
        lambda objets: [objets["session"].pk],
    ),
    EcranEcriture(
        "organisation:ajuster_repartition",
        "noyau.organisation_ecriture",
        lambda objets: [objets["session"].pk],
    ),
    EcranEcriture(
        "organisation:valider_repartition",
        "noyau.organisation_ecriture",
        lambda objets: [objets["session"].pk],
    ),
    # --- ressources : salle attitrée (US-SES-03) ---
    EcranEcriture(
        "ressources:soumettre_salle",
        "noyau.lieux_calendrier_ecriture",
        lambda objets: [objets["brigade"].pk],
    ),
    EcranEcriture(
        "ressources:retirer_salle",
        "noyau.lieux_calendrier_ecriture",
        lambda objets: [objets["brigade"].pk],
    ),
    # --- ressources : lieux (US-PLAN-02) ---
    EcranEcriture("ressources:creer_lieu", "noyau.lieux_calendrier_ecriture"),
    EcranEcriture(
        "ressources:modifier_lieu",
        "noyau.lieux_calendrier_ecriture",
        lambda objets: [objets["lieu"].pk],
    ),
    EcranEcriture(
        "ressources:archiver_lieu",
        "noyau.lieux_calendrier_ecriture",
        lambda objets: [objets["lieu"].pk],
    ),
    EcranEcriture(
        "ressources:desarchiver_lieu",
        "noyau.lieux_calendrier_ecriture",
        lambda objets: [objets["lieu"].pk],
    ),
    EcranEcriture(
        "ressources:supprimer_lieu",
        "noyau.lieux_calendrier_ecriture",
        lambda objets: [objets["lieu"].pk],
    ),
    EcranEcriture(
        "ressources:declarer_indisponibilite_lieu",
        "noyau.lieux_calendrier_ecriture",
        lambda objets: [objets["lieu"].pk],
    ),
    EcranEcriture(
        "ressources:modifier_indisponibilite_lieu",
        "noyau.lieux_calendrier_ecriture",
        lambda objets: [objets["indisponibilite"].pk],
    ),
    EcranEcriture(
        "ressources:supprimer_indisponibilite_lieu",
        "noyau.lieux_calendrier_ecriture",
        lambda objets: [objets["indisponibilite"].pk],
    ),
    # --- ressources : indisponibilités d'instructeur (US-INS-03) ---
    # Écran autonome depuis DECISIONS.md D-115 : l'instructeur est un champ
    # du formulaire, jamais un segment d'URL — args par défaut ([]).
    EcranEcriture(
        "ressources:declarer_indisponibilite_instructeur", "noyau.lieux_calendrier_ecriture"
    ),
    EcranEcriture("ressources:confirmer_fusion_indisponibilite", "noyau.lieux_calendrier_ecriture"),
    EcranEcriture(
        "ressources:modifier_indisponibilite_instructeur",
        "noyau.lieux_calendrier_ecriture",
        lambda objets: [objets["indisponibilite_instructeur"].pk],
    ),
    EcranEcriture(
        "ressources:supprimer_indisponibilite_instructeur",
        "noyau.lieux_calendrier_ecriture",
        lambda objets: [objets["indisponibilite_instructeur"].pk],
    ),
    # --- ressources : instructeurs (US-INS-01) ---
    EcranEcriture("ressources:creer_instructeur", "noyau.instructeurs_qualifications_ecriture"),
    EcranEcriture(
        "ressources:modifier_instructeur",
        "noyau.instructeurs_qualifications_ecriture",
        lambda objets: [objets["instructeur"].pk],
    ),
    EcranEcriture(
        "ressources:archiver_instructeur",
        "noyau.instructeurs_qualifications_ecriture",
        lambda objets: [objets["instructeur"].pk],
    ),
    EcranEcriture(
        "ressources:desarchiver_instructeur",
        "noyau.instructeurs_qualifications_ecriture",
        lambda objets: [objets["instructeur"].pk],
    ),
    # --- ressources : qualifications (US-INS-02) ---
    EcranEcriture(
        "ressources:ajouter_qualification_instructeur",
        "noyau.instructeurs_qualifications_ecriture",
        lambda objets: [objets["instructeur"].pk, objets["autre_element"].matiere_id],
    ),
    EcranEcriture(
        "ressources:ajouter_qualification_matiere",
        "noyau.instructeurs_qualifications_ecriture",
        lambda objets: [objets["autre_element"].matiere_id, objets["instructeur"].pk],
    ),
    EcranEcriture(
        "ressources:retirer_qualification_instructeur",
        "noyau.instructeurs_qualifications_ecriture",
        lambda objets: [objets["qualification"].pk],
    ),
    EcranEcriture(
        "ressources:retirer_qualification_matiere",
        "noyau.instructeurs_qualifications_ecriture",
        lambda objets: [objets["qualification"].pk],
    ),
    # --- ressources : natures d'événement du calendrier (US-PLAN-01) ---
    EcranEcriture("ressources:creer_nature_evenement", "noyau.lieux_calendrier_ecriture"),
    EcranEcriture(
        "ressources:modifier_nature_evenement",
        "noyau.lieux_calendrier_ecriture",
        lambda objets: [objets["nature_evenement"].pk],
    ),
    EcranEcriture(
        "ressources:supprimer_nature_evenement",
        "noyau.lieux_calendrier_ecriture",
        lambda objets: [objets["nature_evenement"].pk],
    ),
    # --- ressources : périodes de calendrier (US-PLAN-01) ---
    EcranEcriture("ressources:declarer_periode_calendrier", "noyau.lieux_calendrier_ecriture"),
    EcranEcriture(
        "ressources:modifier_periode_calendrier",
        "noyau.lieux_calendrier_ecriture",
        lambda objets: [objets["periode_calendrier"].pk],
    ),
    EcranEcriture(
        "ressources:supprimer_periode_calendrier",
        "noyau.lieux_calendrier_ecriture",
        lambda objets: [objets["periode_calendrier"].pk],
    ),
    # --- ressources : grilles horaires et créneaux types (US-PLAN-12) ---
    EcranEcriture("ressources:creer_grille_horaire", "noyau.lieux_calendrier_ecriture"),
    EcranEcriture(
        "ressources:modifier_grille_horaire",
        "noyau.lieux_calendrier_ecriture",
        lambda objets: [objets["grille_horaire"].pk],
    ),
    EcranEcriture(
        "ressources:dupliquer_grille_horaire",
        "noyau.lieux_calendrier_ecriture",
        lambda objets: [objets["grille_horaire"].pk],
    ),
    EcranEcriture(
        "ressources:archiver_grille_horaire",
        "noyau.lieux_calendrier_ecriture",
        lambda objets: [objets["grille_horaire"].pk],
    ),
    EcranEcriture(
        "ressources:desarchiver_grille_horaire",
        "noyau.lieux_calendrier_ecriture",
        lambda objets: [objets["grille_horaire"].pk],
    ),
    EcranEcriture(
        "ressources:supprimer_grille_horaire",
        "noyau.lieux_calendrier_ecriture",
        lambda objets: [objets["grille_horaire"].pk],
    ),
    EcranEcriture(
        "ressources:confirmer_activation_grille_horaire",
        "noyau.lieux_calendrier_ecriture",
        lambda objets: [objets["grille_horaire"].pk],
    ),
    EcranEcriture(
        "ressources:ajouter_creneau",
        "noyau.lieux_calendrier_ecriture",
        lambda objets: [objets["grille_horaire"].pk],
    ),
    EcranEcriture(
        "ressources:supprimer_creneau",
        "noyau.lieux_calendrier_ecriture",
        lambda objets: [objets["creneau_type"].pk],
    ),
    # --- planification : génération du programme hebdomadaire (US-PLAN-03) ---
    EcranEcriture("planification:lancement_generation", "noyau.programme_ecriture"),
    # --- planification : circuit du programme (prompt 40, US-VAL-01, 02, 04) ---
    EcranEcriture("planification:soumettre", "noyau.programme_ecriture", lambda objets: [objets["programme"].pk]),
    EcranEcriture("planification:retirer_soumission", "noyau.programme_ecriture", lambda objets: [objets["programme"].pk]),
    EcranEcriture("planification:valider", "noyau.programme_validation_ecriture", lambda objets: [objets["programme"].pk]),
    EcranEcriture("planification:rejeter", "noyau.programme_validation_ecriture", lambda objets: [objets["programme"].pk]),
    EcranEcriture("planification:reprendre", "noyau.programme_ecriture", lambda objets: [objets["programme"].pk]),
    EcranEcriture("planification:signer", "noyau.programme_ecriture", lambda objets: [objets["programme"].pk]),
    EcranEcriture("planification:afficher", "noyau.programme_ecriture", lambda objets: [objets["programme"].pk]),
    EcranEcriture("planification:annuler_validation", "noyau.programme_ecriture", lambda objets: [objets["programme"].pk]),
    EcranEcriture("planification:modifier_seance", "noyau.programme_ecriture", lambda objets: [objets["seance"].pk]),
    EcranEcriture("planification:supprimer_seance", "noyau.programme_ecriture", lambda objets: [objets["seance"].pk]),
    EcranEcriture("planification:deverrouiller_seance", "noyau.programme_ecriture", lambda objets: [objets["seance"].pk]),
    # --- evaluations : création d'une évaluation (US-EVAL-01) ---
    EcranEcriture("evaluations:creer_evaluation", "noyau.evaluations_ecriture"),
    # --- evaluations : modification de la date d'un examen final (US-EVAL-02) ---
    EcranEcriture(
        "evaluations:modifier_date_certificative",
        "noyau.evaluations_ecriture",
        lambda objets: [objets["evaluation"].pk],
    ),
    # --- evaluations : sujets d'examen (US-EVAL-03) --- A5 : la visibilité
    # des sujets suit evaluations_ecriture, y compris l'écran de
    # consultation (GET) — `sujets` est donc une adresse d'écriture au sens
    # de ce test bien qu'elle serve aussi la lecture (même figure que
    # liste_comptes ci-dessus).
    EcranEcriture(
        "evaluations:sujets", "noyau.evaluations_ecriture", lambda objets: [objets["evaluation"].pk]
    ),
    EcranEcriture(
        "evaluations:corriger_sujet",
        "noyau.evaluations_ecriture",
        lambda objets: [objets["sujet"].pk],
    ),
    EcranEcriture(
        "evaluations:supprimer_sujet",
        "noyau.evaluations_ecriture",
        lambda objets: [objets["sujet"].pk],
    ),
    EcranEcriture(
        "evaluations:retenir_sujet",
        "noyau.evaluations_ecriture",
        lambda objets: [objets["sujet"].pk],
    ),
    EcranEcriture(
        "evaluations:changer_retenu_sujet",
        "noyau.evaluations_ecriture",
        lambda objets: [objets["sujet"].pk],
    ),
    # --- evaluations : organisation d'épreuve (US-EVAL-04, Prompt 38) ---
    EcranEcriture(
        "evaluations:fixer_creneau",
        "noyau.evaluations_ecriture",
        lambda objets: [objets["evaluation"].pk],
    ),
    EcranEcriture(
        "evaluations:ajouter_organisation",
        "noyau.evaluations_ecriture",
        lambda objets: [objets["evaluation"].pk],
    ),
    EcranEcriture(
        "evaluations:retirer_organisation",
        "noyau.evaluations_ecriture",
        lambda objets: [objets["organisation"].pk],
    ),
    EcranEcriture(
        "evaluations:ajouter_surveillant",
        "noyau.evaluations_ecriture",
        lambda objets: [objets["organisation"].pk],
    ),
    EcranEcriture(
        "evaluations:retirer_surveillant",
        "noyau.evaluations_ecriture",
        lambda objets: [objets["surveillance"].pk],
    ),
]

# 102 adresses : les 97 précédentes (Prompt 37) plus les cinq adresses
# d'écriture de l'organisation d'épreuve (US-EVAL-04, Prompt 38) ; 109 après le
# circuit du programme (prompt 40, sept routes POST) ; 113 après la modification
# manuelle et l'avenant (prompt 41, US-PLAN-05 : quatre routes POST).
assert len(ECRANS_ECRITURE) == 113


def _groupes_sans(permission):
    codename = permission.removeprefix("noyau.")
    return [groupe for groupe in GROUPES if codename not in MATRICE.get(groupe, [])]


CAS_REFUS = [
    pytest.param(ecran, groupe, id=f"{ecran.nom}-{groupe}")
    for ecran in ECRANS_ECRITURE
    for groupe in _groupes_sans(ecran.permission)
]


@pytest.mark.parametrize("ecran, groupe", CAS_REFUS)
def test_refus_habilitation_pour_chaque_ecran_ecriture(client, utilisateurs, objets, ecran, groupe):
    """Un utilisateur du groupe `groupe`, qui ne détient pas `ecran.permission`,
    reçoit 403 en appel direct — pas un simple masquage de lien."""
    client.force_login(utilisateurs[groupe])
    reponse = client.post(reverse(ecran.nom, args=ecran.args(objets)))
    assert (
        reponse.status_code == 403
    ), f"{ecran.nom} aurait dû refuser {groupe} (permission {ecran.permission})"


def _toutes_les_vues():
    """(nom d'URL complet, fonction vue) pour toute route du projet, en
    reconstruisant le préfixe de namespace comme reverse() l'attend."""
    resultat = []

    def _parcourir(motifs, prefixe):
        for motif in motifs:
            if isinstance(motif, URLResolver):
                espace = f"{motif.namespace}:" if motif.namespace else ""
                _parcourir(motif.url_patterns, f"{prefixe}{espace}")
            elif isinstance(motif, URLPattern) and motif.name:
                resultat.append((f"{prefixe}{motif.name}", motif.callback))

    _parcourir(get_resolver().url_patterns, "")
    return resultat


def _permission_requise(vue):
    """`permission_requise` se trouve directement sur une vue fonction
    décorée par `exige_habilitation`. Sur une vue basée sur une classe,
    `View.as_view()` ne copie que `dispatch`, jamais les attributs de
    classe : `HabilitationMixin.permission_requise` (posé sur la classe,
    pas la fonction retournée) n'est visible qu'en passant par l'attribut
    `view_class` que Django pose lui-même sur la fonction — sans ce détour,
    une future vue à base de `HabilitationMixin` échapperait silencieusement
    à ce test de garde, alors même que ce mixin existe pour ce cas.
    """
    permission = getattr(vue, "permission_requise", None)
    if permission is not None:
        return permission
    return getattr(getattr(vue, "view_class", None), "permission_requise", "") or ""


def test_permission_requise_detecte_aussi_une_vue_a_base_de_classe():
    """Preuve directe du détour par `view_class` ci-dessus — relevé en
    relecture (Prompt 19) : sans lui, une vue à base de `HabilitationMixin`
    échapperait silencieusement au test de garde qui suit.
    """
    from django.views import View

    from administration.habilitations import HabilitationMixin

    class VueEssai(HabilitationMixin, View):
        permission_requise = "noyau.exemple_ecriture"

    assert _permission_requise(VueEssai.as_view()) == "noyau.exemple_ecriture"


def test_toute_vue_ecriture_figure_dans_la_table():
    """Test de garde : sans lui, la règle du bloc C (Prompt 19) reste
    volontaire — une story du sprint 2 qui ajoute un écran sans l'inscrire
    ici rouvrirait l'angle mort mécaniquement, pas seulement par oubli de
    revue. Compare aux vues réellement gardées par une permission
    d'écriture — décorateur `exige_habilitation` ou mixin
    `HabilitationMixin`, les deux mécanismes du projet — jamais à une
    convention de nommage d'URL.
    """
    noms_en_table = {ecran.nom for ecran in ECRANS_ECRITURE}
    vues_ecriture_reelles = {
        nom for nom, vue in _toutes_les_vues() if _permission_requise(vue).endswith("_ecriture")
    }

    manquantes = vues_ecriture_reelles - noms_en_table
    assert not manquantes, (
        "Adresse(s) d'écriture absente(s) de ECRANS_ECRITURE : "
        + ", ".join(sorted(manquantes))
        + " — ajoute une entrée dans tests/architecture/test_ecrans_ecriture.py."
    )

    perimees = noms_en_table - vues_ecriture_reelles
    assert not perimees, (
        "Entrée(s) de ECRANS_ECRITURE qui ne correspond(ent) plus à une vue "
        "d'écriture réelle : " + ", ".join(sorted(perimees))
    )
