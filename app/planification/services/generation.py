"""`ServiceGeneration` — CU-P5-01, orchestre la génération du programme
hebdomadaire (US-PLAN-03, Prompt 31) : charge le contexte, construit les
candidates, appelle une STRATÉGIE (§ 3, paramètre BNF-13 — jamais une
branche de code), écrit via `ServiceEcritureSeance.creer_seances`, produit
le compte rendu (non persisté, F4).

E1/E6 (§ 6) ÉVALUÉS AVANT TOUTE CRÉATION DE `ProgrammeHebdomadaire` (point 3,
Prompt 31) : un programme vide occuperait l'unicité de la semaine et la
génération suivante croirait devoir le compléter — voir
docs/suivi/DECISIONS.md. Le lundi est validé avant même le `get_or_create`,
sans quoi deux programmes de la même semaine coexisteraient sous deux dates.

RÉGÉNÉRATION CHIRURGICALE (§ 2) dans la MÊME transaction que l'écriture du
nouveau lot (point 5, Prompt 31) : `creer_seances` ouvre la sienne, qui
s'imbrique dans celle-ci (savepoint Django).
"""

from django.conf import settings
from django.db import transaction

from administration.habilitations import verifier_habilitation
from administration.models import TypeAction
from administration.services.journal import DonneesEntreeJournal, ServiceJournal
from noyau.exceptions import ErreurValidation
from planification.exceptions import AucuneGrilleActive, SemaineEntierementBloquee
from planification.generation.candidats import construire_cases, projeter_creneaux
from planification.generation.compte_rendu import Regeneration
from planification.generation.compte_rendu import construire as construire_compte_rendu
from planification.generation.gloutonne import StrategieGloutonne
from planification.generation.preparation import preparer
from planification.models import ProgrammeHebdomadaire, Seance
from planification.services.circuit import (
    DECLENCHEUR_GENERATION,
    GENERER,
    ServiceCircuitProgramme,
    motif_refus_action,
)
from planification.services.contraintes import (
    ServiceContraintes,
    _charger_periodes_bloquantes,
    _semaine,
)
from planification.services.ecriture import ServiceEcritureSeance
from ressources.models import CreneauType, GrilleHoraire

PERMISSION_ECRITURE = ServiceEcritureSeance.PERMISSION_ECRITURE
STRATEGIES = {"gloutonne": StrategieGloutonne}


def _valider_lundi(lundi_de_semaine):
    if lundi_de_semaine.isoweekday() != 1:
        raise ErreurValidation(f"{lundi_de_semaine:%d/%m/%Y} n'est pas un lundi.")


def _grille_active_avec_creneaux():
    grille = GrilleHoraire.objects.filter(active=True).first()
    if grille is None:
        raise AucuneGrilleActive(
            "Aucune grille horaire active — activez-en une avant de générer un programme."
        )
    return list(CreneauType.objects.filter(grille=grille))


def _cases_ou_e1(brigades, creneaux, lundi_de_semaine):
    debut, fin = _semaine(lundi_de_semaine)
    periodes_bloquantes = _charger_periodes_bloquantes(debut, fin)
    creneaux_projetes = projeter_creneaux(creneaux, lundi_de_semaine)
    cases = construire_cases(brigades, creneaux_projetes, periodes_bloquantes)
    if not cases:
        raise SemaineEntierementBloquee(
            f"Aucun créneau ouvert pour la semaine du {lundi_de_semaine:%d/%m/%Y} : toutes les "
            "périodes de calendrier bloquantes couvrent les brigades sélectionnées."
        )
    return cases


def _brigades_ids(brigades):
    return {brigade.pk for brigade in brigades}


def _supprimer_seances_regenerees(programme, brigades):
    """Séances NON VERROUILLÉES des brigades SÉLECTIONNÉES : supprimées. Une
    séance regroupée à cheval sur une brigade sélectionnée et une non
    sélectionnée est PRÉSERVÉE intégralement et signalée (§ 2, arbitrage
    retenu — la détruire partiellement n'a pas de sens, docs/suivi/
    DECISIONS.md). Les brigades non sélectionnées ne sont jamais touchées."""
    selectionnees = _brigades_ids(brigades)
    candidates = Seance.objects.filter(programme=programme, verrouillee=False).prefetch_related(
        "lignes__brigade"
    )
    a_supprimer, a_cheval = [], []
    for seance in candidates:
        brigades_seance = {ligne.brigade_id for ligne in seance.lignes.all()}
        if not brigades_seance & selectionnees:
            continue
        (a_supprimer if brigades_seance <= selectionnees else a_cheval).append(seance)
    Seance.objects.filter(pk__in=[s.pk for s in a_supprimer]).delete()
    return a_supprimer, a_cheval


def _seances_verrouillees_preservees(programme, brigades):
    selectionnees = _brigades_ids(brigades)
    return list(
        Seance.objects.filter(
            programme=programme, verrouillee=True, lignes__brigade_id__in=selectionnees
        )
        .distinct()
        .prefetch_related("lignes__brigade")
    )


def _construire_strategie(preparation):
    classe = STRATEGIES[settings.GENERATION_STRATEGIE]
    return classe(preparation)


def _journaliser_acte(agissant, programme, brigades, nb_creees, nb_supprimees):
    """L'ACTE, jamais le détail (§ 7, point 4, Prompt 31) — voir
    `planification.services.ecriture` pour la distinction avec
    `creer_seance` (saisie manuelle, journal détaillé par séance)."""
    noms_brigades = ", ".join(str(brigade) for brigade in brigades)
    detail = (
        f"Semaine du {programme.lundi_de_semaine:%d/%m/%Y} — brigades : {noms_brigades} — "
        f"{nb_creees} séance(s) créée(s), {nb_supprimees} supprimée(s)."
    )
    ServiceJournal.enregistrer_detaillee(
        DonneesEntreeJournal(
            type_action=TypeAction.GENERATION_PROGRAMME,
            identifiant_saisi=str(programme),
            auteur=agissant,
            objet_type="programme",
            objet_identifiant=str(programme.pk),
            detail=detail,
        )
    )


class ServiceGeneration:
    DOMAINE = "programme"
    PERMISSION_ECRITURE = PERMISSION_ECRITURE

    @staticmethod
    def motif_indisponible(lundi_de_semaine):
        """V8 — motif pour lequel la génération ne peut pas être lancée sur
        cette semaine, ou `None`. Lecture seule : l'écran de lancement s'en
        sert pour dire pourquoi son bouton est indisponible."""
        programme = ProgrammeHebdomadaire.objects.filter(lundi_de_semaine=lundi_de_semaine).first()
        if programme is None:
            return None
        return motif_refus_action(GENERER, programme.etat)

    @staticmethod
    def generer(agissant, lundi_de_semaine, brigades):
        """RG-31 : produit toujours un BROUILLON, aucun passage d'état.
        Complète le programme de la semaine s'il existe déjà (§ 2, RG-33
        bis — un seul programme par semaine, centre entier), le crée sinon.
        """
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        _valider_lundi(lundi_de_semaine)
        creneaux = _grille_active_avec_creneaux()
        cases = _cases_ou_e1(brigades, creneaux, lundi_de_semaine)
        with transaction.atomic():
            programme, _ = ProgrammeHebdomadaire.objects.get_or_create(
                lundi_de_semaine=lundi_de_semaine
            )
            return ServiceGeneration._generer_dans_programme(agissant, programme, brigades, cases)

    @staticmethod
    def _generer_dans_programme(agissant, programme, brigades, cases):
        # V3 : la garde précède la SUPPRESSION des séances régénérées — un
        # programme soumis, validé ou affiché n'en perd aucune (C2, C5).
        programme = ServiceCircuitProgramme.garde_modification(
            programme, agissant, evenement=GENERER, declencheur=DECLENCHEUR_GENERATION
        )
        supprimees, a_cheval = _supprimer_seances_regenerees(programme, brigades)
        verrouillees = _seances_verrouillees_preservees(programme, brigades)
        contexte = ServiceContraintes.contexte(programme)
        preparation = preparer(brigades, contexte)
        strategie = _construire_strategie(preparation)
        resultat = strategie.generer(contexte, cases, settings.GENERATION_BORNE_TEMPS_SECONDES)
        groupes = [placement.candidates for placement in resultat.placements]
        ServiceEcritureSeance.creer_seances(agissant, programme, groupes)
        _journaliser_acte(agissant, programme, brigades, len(groupes), len(supprimees))
        regeneration = Regeneration(
            verrouillees_preservees=verrouillees,
            a_cheval_preservees=a_cheval,
            nombre_supprimees=len(supprimees),
        )
        return construire_compte_rendu(programme, resultat, contexte, brigades, regeneration)
