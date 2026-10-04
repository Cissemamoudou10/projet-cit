"""Convention « gardée par la vue » (D-219) rendue mécanique : chaque vue nommée de
l'application porte sa garde (`exige_habilitation` ou `HabilitationMixin`), sauf les
adresses publiques listées ci-dessous, avec leur raison. Une vue ajoutée sans garde
fait échouer la suite.
"""

from django.urls import URLPattern, URLResolver, get_resolver

ADRESSES_PUBLIQUES = {
    # Authentification : écrans qui ouvrent la session, par construction.
    "administration:connexion": "écran de connexion, avant toute session",
    "administration:deconnexion": "fermeture de session",
    "administration:changer_mot_de_passe": "compte authentifié, changement obligatoire ou volontaire",
    # Accueil : page d'entrée, sans donnée.
    "noyau:accueil": "page d'entrée sans donnée",
}
PREFIXES_PUBLICS = {
    # Interface d'administration de Django : garde propre à Django (is_staff, superutilisateur),
    # hors de la convention de l'application.
    "admin:": "administration Django, garde propre à Django",
}


def _toutes_les_vues_nommees():
    resultat = []

    def parcourir(motifs, prefixe=""):
        for motif in motifs:
            if isinstance(motif, URLResolver):
                espace = f"{motif.namespace}:" if motif.namespace else ""
                parcourir(motif.url_patterns, f"{prefixe}{espace}")
            elif isinstance(motif, URLPattern) and motif.name:
                resultat.append((f"{prefixe}{motif.name}", motif.callback))

    parcourir(get_resolver().url_patterns)
    return resultat


def _garde(vue):
    garde = getattr(vue, "permission_requise", None)
    if garde is None:
        garde = getattr(getattr(vue, "view_class", None), "permission_requise", None)
    return garde


def _publique(nom):
    return nom in ADRESSES_PUBLIQUES or any(nom.startswith(p) for p in PREFIXES_PUBLICS)


def test_chaque_vue_nommee_est_gardee_ou_declaree_publique():
    sans_garde = [
        nom for nom, vue in _toutes_les_vues_nommees() if not _garde(vue) and not _publique(nom)
    ]
    assert not sans_garde, (
        "Vue(s) sans garde ni déclaration publique : " + ", ".join(sorted(sans_garde))
        + " — ajoutez exige_habilitation, ou déclarez l'adresse publique avec sa raison."
    )


def test_les_adresses_publiques_declarees_existent_encore():
    noms = {nom for nom, _ in _toutes_les_vues_nommees()}
    perimees = [nom for nom in ADRESSES_PUBLIQUES if nom not in noms]
    assert not perimees, f"Adresses publiques périmées : {perimees}"
