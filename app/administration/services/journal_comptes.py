"""Journalisation des actions de compte — extrait de `ServiceCompte` pour
rester sous 200 lignes (.claude/rules/python.md), même patron que
`garde_fous.py` : fonctions de module, pas des méthodes.
"""

from administration.models import TypeAction
from administration.services.journal import DonneesEntreeJournal, ServiceJournal


def journaliser_creation(agissant, compte):
    ServiceJournal.enregistrer_detaillee(
        DonneesEntreeJournal(
            type_action=TypeAction.CREATION_COMPTE,
            identifiant_saisi=compte.username,
            detail=f"Profil : {compte.get_profil_display()}.",
            auteur=agissant,
            cible=compte.username,
            objet_type="utilisateur",
            objet_identifiant=compte.username,
        )
    )


def journaliser_modification(agissant, compte, ancien_profil):
    ServiceJournal.enregistrer_detaillee(
        DonneesEntreeJournal(
            type_action=TypeAction.MODIFICATION_COMPTE,
            identifiant_saisi=compte.username,
            detail="Compte modifié.",
            auteur=agissant,
            cible=compte.username,
            objet_type="utilisateur",
            objet_identifiant=compte.username,
        )
    )
    if compte.profil != ancien_profil:
        ServiceJournal.enregistrer_detaillee(
            DonneesEntreeJournal(
                type_action=TypeAction.CHANGEMENT_PROFIL,
                identifiant_saisi=compte.username,
                detail=f"Profil : {ancien_profil} → {compte.profil}.",
                auteur=agissant,
                cible=compte.username,
                objet_type="utilisateur",
                objet_identifiant=compte.username,
                valeur_avant={"profil": ancien_profil},
                valeur_apres={"profil": compte.profil},
            )
        )


def journaliser_desactivation(agissant, compte):
    ServiceJournal.enregistrer_detaillee(
        DonneesEntreeJournal(
            type_action=TypeAction.DESACTIVATION_COMPTE,
            identifiant_saisi=compte.username,
            detail="Compte désactivé.",
            auteur=agissant,
            cible=compte.username,
            objet_type="utilisateur",
            objet_identifiant=compte.username,
        )
    )


def journaliser_reactivation(agissant, compte):
    ServiceJournal.enregistrer_detaillee(
        DonneesEntreeJournal(
            type_action=TypeAction.REACTIVATION_COMPTE,
            identifiant_saisi=compte.username,
            detail="Compte réactivé.",
            auteur=agissant,
            cible=compte.username,
            objet_type="utilisateur",
            objet_identifiant=compte.username,
        )
    )
