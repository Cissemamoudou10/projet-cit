"""Comptes du jeu volumineux — Prompt 51, Temps 3, § 3.1 : sept comptes,
préfixés `v_` (jamais `u_`, réservé à l'état `socle`/`complet` — bases
distinctes, § garde-fou n° 6 : aucune coexistence entre jeux). Un par
profil (`v_ped`, `v_plan`, `v_exa`, `v_df`, `v_adm`), plus un second
compte pédagogique et planification (`v_ped2`, `v_plan2`) — recette à
plusieurs agents simultanés sur une même cellule, pas exercé plus avant
par ce chargeur.

Même mécanisme que `comptes.py` (bootstrap disposable, § garde `RG-27`) —
non réutilisé tel quel : les identifiants et le nombre de comptes
diffèrent."""

from dataclasses import dataclass

from django.contrib.auth import get_user_model

from administration.models import Profil
from administration.services.comptes import ServiceCompte
from evaluations.jeu_recette.donnees import MOT_DE_PASSE_COMMUN

IDENTIFIANT_BOOTSTRAP_VOLUME = "bootstrap.volume"


@dataclass(frozen=True)
class _DonneesCompteVolume:
    identifiant: str
    profil: str
    grade: str
    nom: str
    prenom: str


COMPTES_VOLUME = (
    _DonneesCompteVolume("v_ped", Profil.CELLULE_PEDAGOGIQUE, "Lt", "FICT Volume", "Pédagogique"),
    _DonneesCompteVolume("v_plan", Profil.CELLULE_PLANIFICATION, "Lt", "FICT Volume", "Planification"),
    _DonneesCompteVolume("v_exa", Profil.CELLULE_EXAMENS, "Lt", "FICT Volume", "Examens"),
    _DonneesCompteVolume("v_df", Profil.DIRECTION_FORMATION, "Col", "FICT Volume", "Direction"),
    _DonneesCompteVolume("v_adm", Profil.ADMINISTRATEUR, "Cne", "FICT Volume", "Administrateur"),
    _DonneesCompteVolume("v_ped2", Profil.CELLULE_PEDAGOGIQUE, "Lt", "FICT Volume", "Pédagogique 2"),
    _DonneesCompteVolume("v_plan2", Profil.CELLULE_PLANIFICATION, "Lt", "FICT Volume", "Planification 2"),
)


def _creer_bootstrap_volume():
    return get_user_model().objects.create_superuser(
        username=IDENTIFIANT_BOOTSTRAP_VOLUME,
        email="",
        password=MOT_DE_PASSE_COMMUN,
        grade="Système",
        profil=Profil.ADMINISTRATEUR,
    )


def _creer_un_compte_volume(agissant, donnees):
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


def charger_comptes_volume(stdout):
    bootstrap = _creer_bootstrap_volume()
    donnees_admin = next(d for d in COMPTES_VOLUME if d.profil == Profil.ADMINISTRATEUR)
    administrateur = _creer_un_compte_volume(bootstrap, donnees_admin)
    comptes = {donnees_admin.identifiant: administrateur}
    for donnees in COMPTES_VOLUME:
        if donnees.identifiant == donnees_admin.identifiant:
            continue
        comptes[donnees.identifiant] = _creer_un_compte_volume(administrateur, donnees)
    for compte in comptes.values():
        ServiceCompte.changer_mot_de_passe(compte, MOT_DE_PASSE_COMMUN, MOT_DE_PASSE_COMMUN)
    bootstrap.is_active = False
    bootstrap.save(update_fields=["is_active"])
    stdout.write(f"  {len(comptes)} comptes créés.")
    return comptes


def recuperer_comptes_volume(stdout):
    identifiants = [donnees.identifiant for donnees in COMPTES_VOLUME]
    comptes = {
        compte.username: compte
        for compte in get_user_model().objects.filter(username__in=identifiants)
    }
    stdout.write(f"  {len(comptes)} comptes déjà chargés, conservés tels quels.")
    return comptes
