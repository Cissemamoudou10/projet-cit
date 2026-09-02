"""ServiceCompte — RG-01, RG-04, RG-26, CU-P1-02."""

import pytest
from django.contrib.auth import get_user_model

from administration.exceptions import ErreurIdentifiantExistant
from administration.models import EntreeJournal, Profil, TypeAction
from administration.services.authentification import ServiceAuthentification
from administration.services.comptes import ServiceCompte
from noyau.exceptions import ErreurCompteDesactive, ErreurHabilitation, ErreurValidation

DONNEES_MINIMALES = {
    "grade": "Sgt",
    "prenom": "",
    "nom": "Test",
    "profil": Profil.CELLULE_PEDAGOGIQUE,
}


def _creer_cible(**champs):
    modele = get_user_model()
    valeurs = {
        "username": "cible",
        "password": "x",
        "grade": "Sgt",
        "profil": modele.Profil.CELLULE_PEDAGOGIQUE,
    }
    valeurs.update(champs)
    return modele.objects.create_user(**valeurs)


def test_creation_cree_un_compte_actif_avec_drapeau_et_journal(administrateur):
    compte = ServiceCompte.creer(
        administrateur,
        {**DONNEES_MINIMALES, "identifiant": "nouveau", "mot_de_passe": "un-mot-de-passe-correct"},
    )

    assert compte.is_active is True
    assert compte.doit_changer_mot_de_passe is True
    entree = EntreeJournal.objects.get(type_action=TypeAction.CREATION_COMPTE, cible="nouveau")
    assert entree.auteur == administrateur


def test_creation_avec_identifiant_existant_est_refusee(administrateur, utilisateur):
    with pytest.raises(ErreurIdentifiantExistant):
        ServiceCompte.creer(
            administrateur,
            {
                **DONNEES_MINIMALES,
                "identifiant": utilisateur.username,
                "mot_de_passe": "un-mot-de-passe-correct",
            },
        )


def test_mot_de_passe_initial_stocke_en_condensat(administrateur):
    compte = ServiceCompte.creer(
        administrateur,
        {**DONNEES_MINIMALES, "identifiant": "nouveau2", "mot_de_passe": "un-mot-de-passe-correct"},
    )

    assert compte.password != "un-mot-de-passe-correct"
    assert compte.check_password("un-mot-de-passe-correct")


def test_mot_de_passe_initial_absent_de_toute_entree_de_journal(administrateur):
    secret = "un-mot-de-passe-tres-particulier-a-chercher"
    ServiceCompte.creer(
        administrateur, {**DONNEES_MINIMALES, "identifiant": "nouveau3", "mot_de_passe": secret}
    )

    for entree in EntreeJournal.objects.all():
        assert secret not in entree.detail
        assert secret not in entree.identifiant_saisi
        assert secret not in entree.cible


def test_desactivation_rend_le_compte_inactif_sans_le_supprimer(administrateur):
    cible = _creer_cible(username="cible-desactivation")

    ServiceCompte.desactiver(administrateur, cible)

    cible.refresh_from_db()
    assert cible.is_active is False
    assert get_user_model().objects.filter(pk=cible.pk).exists()
    assert EntreeJournal.objects.filter(
        type_action=TypeAction.DESACTIVATION_COMPTE, cible="cible-desactivation"
    ).exists()


def test_compte_desactive_ne_peut_plus_s_authentifier(administrateur, mot_de_passe):
    cible = _creer_cible(username="cible-auth", password=mot_de_passe)

    ServiceCompte.desactiver(administrateur, cible)

    with pytest.raises(ErreurCompteDesactive):
        ServiceAuthentification.authentifier(cible.username, mot_de_passe)


def test_changement_de_profil_journalise_ancienne_et_nouvelle_valeur(administrateur):
    cible = _creer_cible(username="cible-profil", profil=Profil.CELLULE_PEDAGOGIQUE)

    ServiceCompte.modifier(administrateur, cible, {"profil": Profil.CELLULE_EXAMENS})

    entree = EntreeJournal.objects.get(
        type_action=TypeAction.CHANGEMENT_PROFIL, cible="cible-profil"
    )
    assert Profil.CELLULE_PEDAGOGIQUE in entree.detail
    assert Profil.CELLULE_EXAMENS in entree.detail


def test_administrateur_ne_peut_pas_se_desactiver_lui_meme(administrateur):
    with pytest.raises(ErreurValidation):
        ServiceCompte.desactiver(administrateur, administrateur)


def test_dernier_administrateur_actif_ne_peut_changer_de_profil(administrateur):
    """`administrateur` est ici le seul administrateur actif de la base — la
    désactivation de ce même cas est déjà couverte par l'autodésactivation
    ci-dessus : les deux garde-fous se recouvrent sur `desactiver`, mais pas
    sur `modifier`, qu'aucune autre règle ne bloque.
    """
    with pytest.raises(ErreurValidation):
        ServiceCompte.modifier(
            administrateur, administrateur, {"profil": Profil.CELLULE_PEDAGOGIQUE}
        )


def test_non_administrateur_appelant_le_service_leve_erreur_habilitation(non_administrateur):
    with pytest.raises(ErreurHabilitation):
        ServiceCompte.lister(non_administrateur, {}, None)


def test_changement_de_mot_de_passe_reussi_abaisse_le_drapeau(db, mot_de_passe):
    cible = _creer_cible(username="premiere-connexion", password=mot_de_passe)
    assert cible.doit_changer_mot_de_passe is True

    ServiceCompte.changer_mot_de_passe(cible, mot_de_passe, "un-nouveau-mot-de-passe-correct")

    cible.refresh_from_db()
    assert cible.doit_changer_mot_de_passe is False


def test_aucune_methode_de_suppression_n_existe_sur_le_service():
    assert not any("suppr" in nom.lower() for nom in dir(ServiceCompte) if not nom.startswith("_"))
