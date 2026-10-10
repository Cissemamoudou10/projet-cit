"""Chargement des cinq comptes de la démonstration J2 — un par profil.

Jamais recréés par un rechargement (RG-27, même raison que les deux jeux
existants) : chaque compte signe au moins une entrée de journal dès sa
création, que le rôle applicatif ne peut plus modifier ni supprimer
(migration `administration.0007_revoquer_ecriture_journal`).
"""

from django.contrib.auth import get_user_model

from administration.models import Profil
from administration.services.comptes import ServiceCompte
from planification.jeu_demonstration_j2.donnees import COMPTES, MOT_DE_PASSE_COMMUN

IDENTIFIANT_BOOTSTRAP = "bootstrap.demo.j2"


def _creer_bootstrap():
    """Disposable, jamais supprimé — même raison que les deux jeux
    existants (RG-27) : désactivé aussitôt après usage."""
    return get_user_model().objects.create_superuser(
        username=IDENTIFIANT_BOOTSTRAP,
        email="",
        password=MOT_DE_PASSE_COMMUN,
        grade="Système",
        profil=Profil.ADMINISTRATEUR,
    )


def _creer_un_compte(agissant, donnees):
    return ServiceCompte.creer(
        agissant,
        {
            "identifiant": donnees.identifiant,
            "profil": donnees.profil,
            "grade": donnees.grade,
            "nom": donnees.nom,
            "prenom": donnees.prenom,
            "mot_de_passe": MOT_DE_PASSE_COMMUN,
        },
    )


def charger_comptes(stdout):
    """Le bootstrap crée l'administrateur, qui crée seul les quatre autres
    — lui seul porte le domaine `administration` en écriture."""
    bootstrap = _creer_bootstrap()
    donnees_admin = next(d for d in COMPTES if d.profil == Profil.ADMINISTRATEUR)
    administrateur = _creer_un_compte(bootstrap, donnees_admin)
    comptes = {donnees_admin.identifiant: administrateur}
    for donnees in COMPTES:
        if donnees.identifiant == donnees_admin.identifiant:
            continue
        comptes[donnees.identifiant] = _creer_un_compte(administrateur, donnees)
    _neutraliser_changement_mot_de_passe(comptes)
    bootstrap.is_active = False
    bootstrap.save(update_fields=["is_active"])
    stdout.write(f"  {len(comptes)} comptes créés.")
    return comptes


def _neutraliser_changement_mot_de_passe(comptes):
    for compte in comptes.values():
        ServiceCompte.changer_mot_de_passe(compte, MOT_DE_PASSE_COMMUN, MOT_DE_PASSE_COMMUN)


def recuperer_comptes(stdout):
    identifiants = [donnees.identifiant for donnees in COMPTES]
    comptes = {
        compte.username: compte
        for compte in get_user_model().objects.filter(username__in=identifiants)
    }
    stdout.write(f"  {len(comptes)} comptes déjà présents, conservés tels quels.")
    return comptes
