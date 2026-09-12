"""Confirmation de l'import de stagiaires — temps 2 du scénario nominal
(RG-18, § 4, Prompt 24). Revalide INTÉGRALEMENT à partir du même contenu de
fichier, jamais du compte rendu du temps 1 : c'est la contrainte
`uq_stagiaire_session_matricule`, doublée de cette revalidation immédiate,
qui empêche deux imports concurrents de produire un doublon (C3).

Écrit en une seule transaction (RG-18) : chaque ligne valide est enregistrée
par `instance.save()`, jamais `bulk_create`, pour qu'un échec survenant après
N lignes déjà écrites soit intégralement défait par `transaction.atomic` —
la preuve attendue par C2, pas une hypothèse sur le comportement d'un INSERT
multi-lignes.
"""

from django.db import IntegrityError, transaction

from administration.habilitations import verifier_habilitation
from administration.models import TypeAction
from administration.services.journal import DonneesEntreeJournal, ServiceJournal
from noyau.exceptions import ErreurValidation
from noyau.services.base import ServiceBase
from organisation.import_stagiaires.analyse import analyser
from organisation.models import Stagiaire
from organisation.services.session import PERMISSION_ECRITURE

OBJET_TYPE = "import_stagiaires"


def confirmer(agissant, session, contenu, nom_fichier):
    verifier_habilitation(agissant, PERMISSION_ECRITURE)
    rapport = analyser(session, contenu, nom_fichier)
    if not rapport.peut_confirmer:
        raise ErreurValidation(
            "Aucune ligne valide à enregistrer : reprenez l'import depuis l'analyse."
        )
    try:
        with transaction.atomic():
            for ligne in rapport.lignes_valides:
                instance = Stagiaire(session=session, **ligne.donnees)
                ServiceBase.creer(instance, agissant)
            _journaliser(agissant, session, rapport)
    except IntegrityError as erreur:
        raise ErreurValidation(
            "L'enregistrement a été interrompu par un conflit de données : aucune ligne "
            "n'a été enregistrée. Reprenez l'import depuis l'analyse."
        ) from erreur
    return rapport


def _journaliser(agissant, session, rapport):
    """LE JOURNAL PORTE LE COMPTE, JAMAIS LA LISTE DES IDENTITÉS (§ 8,
    Prompt 24) : soixante identités complètes déversées ici créeraient un
    fichier nominatif parallèle, non prévu et non effaçable (RG-27)."""
    ServiceJournal.enregistrer_detaillee(
        DonneesEntreeJournal(
            type_action=TypeAction.CREATION_ELEMENT_GESTION,
            identifiant_saisi=f"Import de stagiaires — {session}",
            auteur=agissant,
            objet_type=OBJET_TYPE,
            objet_identifiant=str(session.pk),
            valeur_apres={
                "session": str(session),
                "nombre_enregistres": len(rapport.lignes_valides),
                "nombre_ignores": len(rapport.anomalies) + len(rapport.doublons_en_base),
            },
        )
    )
