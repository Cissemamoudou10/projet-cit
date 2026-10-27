"""Chargement des cinq comptes de recette — Prompt 34, § 2. Un profil, une
permission par le mécanisme existant (groupe Django synchronisé au profil,
`administration.services.comptes.ServiceCompte`) — jamais d'attribution
manuelle de permission individuelle.

`--reinitialiser` NE RECRÉE JAMAIS les comptes, même motif que le jeu de
démonstration (`ressources.jeu_demonstration.comptes`, D-59/P-28) : la
migration `0007_revoquer_ecriture_journal` (RG-27) retire au rôle applicatif
tout privilège `UPDATE`/`DELETE` sur `administration_entree_journal`, et
chaque compte devient `auteur` d'au moins une entrée dès sa création — le
supprimer ferait échouer la mise à `NULL` que Django tenterait sur cette
entrée, faute de privilège.
"""

from django.contrib.auth import get_user_model

from administration.models import Profil
from administration.services.comptes import ServiceCompte
from evaluations.jeu_recette.donnees import COMPTES, MOT_DE_PASSE_COMMUN

IDENTIFIANT_BOOTSTRAP = "bootstrap.recette"


def _creer_bootstrap():
    """Disposable, propre à CE jeu — jamais le bootstrap ni un compte du jeu
    de démonstration : aucune dépendance entre les deux jeux (§ 0.2 du
    prompt). Désactivé aussitôt après usage, jamais supprimé (même
    contrainte RG-27 que les cinq comptes eux-mêmes)."""
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
    """Le bootstrap crée `u_adm` en premier (seul profil ADMINISTRATEUR de
    `COMPTES`, quel que soit son rang dans le tuple) : lui seul porte le
    domaine `administration` en écriture (matrice d'habilitations) — les
    quatre autres comptes doivent être créés PAR LUI, jamais par le
    bootstrap ni par un compte non administrateur."""
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
    """`ServiceCompte.creer` lève toujours le drapeau de changement de mot de
    passe exigé : aucun des cinq comptes de recette ne doit le porter, à la
    différence du jeu de démonstration (`ped.nouveau`) qui le démontre
    exprès — ce n'est pas l'objet de ce jeu-ci."""
    for compte in comptes.values():
        ServiceCompte.changer_mot_de_passe(compte, MOT_DE_PASSE_COMMUN, MOT_DE_PASSE_COMMUN)


def recuperer_comptes(stdout):
    """`--reinitialiser` ne recrée jamais les comptes (voir docstring du
    module) : relit ceux déjà chargés, pour servir d'agissants au reste du
    chargement."""
    identifiants = [donnees.identifiant for donnees in COMPTES]
    comptes = {
        compte.username: compte
        for compte in get_user_model().objects.filter(username__in=identifiants)
    }
    stdout.write(f"  {len(comptes)} comptes déjà chargés, conservés tels quels.")
    return comptes
