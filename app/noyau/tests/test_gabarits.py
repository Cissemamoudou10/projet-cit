"""L'ossature doit rendre sans erreur avant que la navigation, le fil
d'Ariane et la grille active n'aient de source réelle — voir docs/charte,
§ 2.2, 2.3 et 3.04. `rubriques`, `fil_ariane` restent des listes vides tant
qu'aucune vue métier ne les alimente (noyau/context_processors.py).

L'utilisateur de la requête est enregistré en base, pas seulement construit
en mémoire : depuis US-ADM-02, le processeur de contexte appelle
`user.has_perm(...)`, qui exige un compte doté d'une clé primaire.
"""

from django.contrib.auth import get_user_model
from django.template.loader import render_to_string


def _requete(rf):
    modele_utilisateur = get_user_model()
    utilisateur = modele_utilisateur(
        username="essai",
        grade="Lt",
        profil=modele_utilisateur.Profil.ADMINISTRATEUR,
        last_name="Cissé",
    )
    utilisateur.set_unusable_password()
    utilisateur.save()

    requete = rf.get("/")
    requete.user = utilisateur
    return requete


def test_base_rend_avec_listes_vides(rf, db):
    contenu = render_to_string("noyau/base.html", request=_requete(rf))
    assert "GESTION DES ACTIVITÉS" in contenu
    assert "CISSÉ" in contenu


def test_base_masque_le_cartouche_sans_grille_active(rf, db):
    contenu = render_to_string("noyau/base.html", request=_requete(rf))
    assert "Grille active" not in contenu
