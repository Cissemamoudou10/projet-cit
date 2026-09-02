"""`verifier_habilitation` — RG-02, RG-26 : refuse et journalise.

`a_permission` (silencieuse) se teste ici aussi, pas dans noyau/tests/ :
prouver qu'elle n'écrit rien au journal exige `EntreeJournal`, qu'un test
sous noyau ne peut pas importer (noyau ne dépend d'aucune application).
"""

import pytest

from administration.habilitations import verifier_habilitation
from administration.models import EntreeJournal, TypeAction
from noyau.exceptions import ErreurHabilitation
from noyau.habilitations import a_permission


def test_verifier_habilitation_leve_erreur_habilitation(non_administrateur):
    with pytest.raises(ErreurHabilitation):
        verifier_habilitation(non_administrateur, "noyau.administration_ecriture")


def test_verifier_habilitation_journalise_le_refus(non_administrateur):
    with pytest.raises(ErreurHabilitation):
        verifier_habilitation(non_administrateur, "noyau.administration_ecriture")

    entree = EntreeJournal.objects.get(type_action=TypeAction.ACCES_REFUSE)
    assert entree.auteur == non_administrateur
    assert "noyau.administration_ecriture" in entree.detail


def test_verifier_habilitation_habilite_ne_leve_ni_ne_journalise(administrateur):
    verifier_habilitation(administrateur, "noyau.administration_ecriture")

    assert not EntreeJournal.objects.filter(type_action=TypeAction.ACCES_REFUSE).exists()


def test_a_permission_refusee_n_ecrit_rien_au_journal(non_administrateur):
    """§ 2.2 : un masquage silencieux n'est pas une tentative — sans quoi
    chaque affichage de menu écrirait une entrée, et le journal deviendrait
    illisible en une semaine.
    """
    assert a_permission(non_administrateur, "noyau.administration_ecriture") is False
    assert not EntreeJournal.objects.exists()
