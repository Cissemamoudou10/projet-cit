"""ServiceJournal — écriture isolée, indépendante du flux d'authentification."""

from administration.models import EntreeJournal, TypeAction
from administration.services.journal import ServiceJournal


def test_enregistrer_cree_une_entree_sans_auteur_par_defaut(db):
    entree = ServiceJournal.enregistrer(
        type_action=TypeAction.ECHEC_AUTHENTIFICATION,
        identifiant_saisi="essai",
        detail="essai",
        cible="authentification",
    )

    assert EntreeJournal.objects.filter(pk=entree.pk).exists()
    assert entree.auteur is None
    assert entree.cree_par is None  # voir D-03, docs/suivi/DECISIONS.md


def test_enregistrer_avec_auteur(utilisateur):
    entree = ServiceJournal.enregistrer(
        type_action=TypeAction.ECHEC_AUTHENTIFICATION,
        identifiant_saisi=utilisateur.username,
        auteur=utilisateur,
    )

    assert entree.auteur == utilisateur
