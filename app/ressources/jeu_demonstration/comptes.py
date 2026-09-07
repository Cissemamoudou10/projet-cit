"""Chargement des comptes de démonstration — Prompt 15, § 3.1.

Peuple aussi le journal au passage (§ 5 du plan validé) : une modification,
un cycle désactivation/réactivation, un refus d'habilitation et le
verrouillage du huitième compte, tous par appel de service — jamais une
écriture directe sur `echecs_consecutifs` ou `verrouille_jusqu_a`.

Les comptes ne sont jamais rechargés par `--reinitialiser` : la migration
`0007_revoquer_ecriture_journal` (RG-27) retire au rôle applicatif tout
privilège `UPDATE`/`DELETE` sur `administration_entree_journal`, et chaque
compte a déjà signé au moins une entrée de journal (`auteur`, `SET_NULL`) —
le supprimer ferait échouer la suppression elle-même sur cette contrainte de
privilège. `recuperer_comptes` relit les comptes existants plutôt que d'en
recréer.
"""

from contextlib import suppress

from django.conf import settings
from django.contrib.auth import get_user_model

from administration.models import Profil
from administration.services.authentification import ServiceAuthentification
from administration.services.comptes import ServiceCompte
from noyau.exceptions import ErreurAuthentification, ErreurHabilitation
from ressources.jeu_demonstration.donnees import (
    COMPTES,
    IDENTIFIANT_INACTIF,
    IDENTIFIANT_NOUVEAU,
    IDENTIFIANT_VERROUILLE,
    MOT_DE_PASSE_COMMUN,
)
from ressources.services.instructeur import ServiceInstructeur

IDENTIFIANT_BOOTSTRAP = "bootstrap.technique"


def charger_comptes(stdout):
    comptes = _creer_comptes(stdout)
    _neutraliser_changement_mot_de_passe(comptes)
    _demontrer_modification(comptes)
    _demontrer_desactivation_reactivation(comptes)
    _demontrer_refus_habilitation(comptes)
    _demontrer_verrouillage(comptes, stdout)
    _demontrer_echecs_puis_succes()
    return comptes


def _creer_bootstrap():
    """Acteur technique, seul moyen de créer `adm.demo` (§ 3.1, exception
    admise) : aucun compte n'existe encore pour agir. Désactivé — jamais
    supprimé — aussitôt après usage : sa création a déjà signé une entrée de
    journal comme `auteur`, que le rôle applicatif n'a plus le droit de
    modifier (RG-27) ; une suppression échouerait sur la mise à `NULL` que
    Django tenterait d'appliquer à cette entrée.
    """
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


def _creer_comptes(stdout):
    # COMPTES[0] est « adm.demo » (donnees.py) : une fois créé, il agit pour
    # les sept autres — le bootstrap ne sert qu'à lui seul.
    bootstrap = _creer_bootstrap()
    premiere, *reste = COMPTES
    comptes = {premiere.identifiant: _creer_un_compte(bootstrap, premiere)}
    administrateur = comptes[premiere.identifiant]
    for donnees in reste:
        comptes[donnees.identifiant] = _creer_un_compte(administrateur, donnees)
    bootstrap.is_active = False
    bootstrap.save(update_fields=["is_active"])
    stdout.write(f"  {len(comptes)} comptes créés.")
    return comptes


def recuperer_comptes(stdout):
    """`--reinitialiser` ne recrée jamais les comptes (voir docstring du
    module) : relit ceux déjà chargés, pour servir d'agissants au reste du
    chargement.
    """
    identifiants = [donnees.identifiant for donnees in COMPTES]
    comptes = {
        compte.username: compte
        for compte in get_user_model().objects.filter(username__in=identifiants)
    }
    stdout.write(f"  {len(comptes)} comptes déjà chargés, conservés tels quels.")
    return comptes


def _neutraliser_changement_mot_de_passe(comptes):
    """`ServiceCompte.creer` lève toujours le drapeau (§ 1.2 du service) —
    `ped.nouveau` est seul à devoir le garder, unique démonstration de
    l'intergiciel d'US-ADM-02 (§ 3.1 du prompt).
    """
    for identifiant, compte in comptes.items():
        if identifiant == IDENTIFIANT_NOUVEAU:
            continue
        ServiceCompte.changer_mot_de_passe(compte, MOT_DE_PASSE_COMMUN, MOT_DE_PASSE_COMMUN)


def _demontrer_modification(comptes):
    ServiceCompte.modifier(comptes["adm.demo"], comptes["pla.demo"], {"grade": "Cdt"})


def _demontrer_desactivation_reactivation(comptes):
    agissant, compte = comptes["adm.demo"], comptes[IDENTIFIANT_INACTIF]
    ServiceCompte.desactiver(agissant, compte)
    ServiceCompte.reactiver(agissant, compte)
    ServiceCompte.desactiver(agissant, compte)


def _demontrer_refus_habilitation(comptes):
    """`exa.demo` n'a aucun accès au domaine instructeurs (§ 3.1) — le refus
    est journalisé par `verifier_habilitation` lui-même, rien à faire ici."""
    with suppress(ErreurHabilitation):
        ServiceInstructeur.lister(comptes["exa.demo"], {}, 1)


def _demontrer_verrouillage(comptes, stdout):
    for _ in range(settings.AUTH_SEUIL_ECHECS):
        ServiceAuthentification.enregistrer_echec(IDENTIFIANT_VERROUILLE)
    comptes[IDENTIFIANT_VERROUILLE].refresh_from_db()
    stdout.write(f"  Compte « {IDENTIFIANT_VERROUILLE} » verrouillé (§ 3.1).")


def _demontrer_echecs_puis_succes():
    """Deux échecs sous le seuil sur `ped.demo`, puis un succès qui
    réinitialise le compteur — exerce `authentifier` de bout en bout, pas
    seulement `enregistrer_echec`."""
    for _ in range(2):
        with suppress(ErreurAuthentification):
            ServiceAuthentification.authentifier("ped.demo", "mot-de-passe-errone")
    ServiceAuthentification.authentifier("ped.demo", MOT_DE_PASSE_COMMUN)
