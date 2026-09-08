"""Chemin nominal en écriture de l'écran de configuration des habilitations
— bloc D.2 du Prompt 19, priorité 1. Preuve d'un effet réel en base, pas
seulement d'un code de retour : l'audit `docs/suivi/COUVERTURE-HTTP.md` a
trouvé que le seul test HTTP existant sur cet écran écrit
(`test_appliquer_changements_habilitations.py`) dit lui-même, dans sa
docstring, appeler le service directement plutôt que de passer par HTTP —
le point le plus exposé de l'audit, cet écran gardant tous les autres.
"""

from django.contrib.auth.models import Group
from django.urls import reverse

from administration.services.matrice_habilitations import ServiceMatriceHabilitations


def _charge_utile(agissant):
    """Reproduit exactement ce que le gabarit soumet : une case cochée par
    croisement actuellement vrai — une case absente du POST équivaut à
    décochée, comportement natif d'un `<input type="checkbox">`.
    """
    charge = {}
    for ligne in ServiceMatriceHabilitations.matrice(agissant):
        code = ligne["code"]
        for colonne in ligne["colonnes"]:
            slug = colonne["slug"]
            if colonne["lecture"]:
                charge[f"{slug}-{code}-lecture"] = "on"
            if colonne["ecriture"]:
                charge[f"{slug}-{code}-ecriture"] = "on"
    return charge


def test_cocher_une_lecture_l_accorde_reellement_au_groupe(client, administrateur):
    """Cellule examens n'a, par construction (§ 11.2), aucun accès au
    domaine programme — cocher sa case lecture depuis l'écran doit
    réellement le lui accorder en base, pas seulement rediriger sans erreur.
    """
    client.force_login(administrateur)
    groupe = Group.objects.get(name="Cellule examens")
    assert not groupe.permissions.filter(codename="programme_lecture").exists()

    charge = _charge_utile(administrateur)
    charge["examens-programme-lecture"] = "on"
    reponse = client.post(reverse("administration:habilitations"), charge)

    assert reponse.status_code == 302
    assert groupe.permissions.filter(codename="programme_lecture").exists()


def test_decocher_ne_perd_aucun_autre_croisement_du_meme_groupe(client, administrateur):
    """Preuve inverse, sur le même appel : les croisements non touchés du
    formulaire complet restent inchangés — sans quoi un POST complet
    effacerait silencieusement le reste de la matrice d'un groupe.
    """
    client.force_login(administrateur)
    groupe = Group.objects.get(name="Cellule pédagogique")
    assert groupe.permissions.filter(codename="referentiel_ecriture").exists()
    assert groupe.permissions.filter(codename="suivi_ecriture").exists()

    charge = _charge_utile(administrateur)
    del charge["pedagogique-suivi-ecriture"]
    del charge["pedagogique-suivi-lecture"]
    client.post(reverse("administration:habilitations"), charge)

    assert groupe.permissions.filter(codename="referentiel_ecriture").exists()
    assert not groupe.permissions.filter(codename="suivi_ecriture").exists()
