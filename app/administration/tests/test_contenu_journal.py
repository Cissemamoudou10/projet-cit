"""Contenu des entrées — Prompt 04 § 2.5, § 2.6, critère 1."""

from administration.models import EntreeJournal, Profil, TypeAction
from administration.services.comptes import ServiceCompte

NATURES_RG26_COMPTES = {
    TypeAction.CREATION_COMPTE,
    TypeAction.MODIFICATION_COMPTE,
    TypeAction.CHANGEMENT_PROFIL,
    TypeAction.DESACTIVATION_COMPTE,
    TypeAction.REACTIVATION_COMPTE,
}
NATURES_RG26_PLACEHOLDER = {
    TypeAction.SAISIE_NOTE,
    TypeAction.MODIFICATION_NOTE,
    TypeAction.VALIDATION_PROGRAMME,
    TypeAction.REJET_PROGRAMME,
    TypeAction.SELECTION_SUJET,
}
NATURES_RG26_AUTHENTIFICATION = {TypeAction.ECHEC_AUTHENTIFICATION}
EXTENSIONS_HORS_RG26 = {
    TypeAction.ACCES_REFUSE,
    TypeAction.MODIFICATION_HABILITATIONS,
    TypeAction.CONSULTATION_JOURNAL,
}
# US-REF-00 (D-18) : quatrième extension à RG-26, trois valeurs génériques
# réutilisées par les cinq stories du patron de gestion.
NATURES_PATRON_GESTION = {
    TypeAction.CREATION_ELEMENT_GESTION,
    TypeAction.MODIFICATION_ELEMENT_GESTION,
    TypeAction.ARCHIVAGE_ELEMENT_GESTION,
}


def test_une_modification_enregistre_auteur_date_et_valeur_precedente(administrateur):
    compte = ServiceCompte.creer(
        administrateur,
        {
            "identifiant": "essai-contenu",
            "grade": "Lt",
            "mot_de_passe": "un-mot-de-passe-suffisamment-long",
            "profil": Profil.CELLULE_PEDAGOGIQUE,
        },
    )

    ServiceCompte.modifier(administrateur, compte, {"profil": Profil.CELLULE_EXAMENS})

    entree = EntreeJournal.objects.get(type_action=TypeAction.CHANGEMENT_PROFIL)
    assert entree.auteur == administrateur
    assert entree.cree_le is not None
    assert entree.valeur_avant == {"profil": Profil.CELLULE_PEDAGOGIQUE}


def test_seuls_les_champs_de_la_liste_blanche_sont_enregistres(administrateur):
    compte = ServiceCompte.creer(
        administrateur,
        {
            "identifiant": "essai-liste-blanche",
            "grade": "Lt",
            "mot_de_passe": "un-mot-de-passe-suffisamment-long",
            "profil": Profil.CELLULE_PEDAGOGIQUE,
        },
    )

    ServiceCompte.modifier(administrateur, compte, {"profil": Profil.DIRECTION_FORMATION})

    entree = EntreeJournal.objects.get(type_action=TypeAction.CHANGEMENT_PROFIL)
    assert set(entree.valeur_avant.keys()) == {"profil"}
    assert set(entree.valeur_apres.keys()) == {"profil"}


def test_aucun_condense_de_mot_de_passe_n_entre_au_journal(administrateur):
    mot_de_passe = "un-mot-de-passe-tres-secret-a-ne-jamais-journaliser"
    compte = ServiceCompte.creer(
        administrateur,
        {
            "identifiant": "essai-secret",
            "grade": "Lt",
            "mot_de_passe": mot_de_passe,
            "profil": Profil.CELLULE_PEDAGOGIQUE,
        },
    )
    ServiceCompte.modifier(administrateur, compte, {"profil": Profil.CELLULE_EXAMENS})
    ServiceCompte.desactiver(administrateur, compte)

    condense = compte.password  # le condensat réellement stocké, pas le mot de passe en clair
    for entree in EntreeJournal.objects.all():
        assert mot_de_passe not in entree.detail
        assert mot_de_passe not in entree.cible
        assert condense not in entree.detail
        assert condense not in entree.cible
        assert entree.valeur_avant is None or "password" not in entree.valeur_avant
        assert entree.valeur_apres is None or "password" not in entree.valeur_apres
        if entree.valeur_avant:
            assert condense not in str(entree.valeur_avant)
        if entree.valeur_apres:
            assert condense not in str(entree.valeur_apres)


def test_enumeration_couvre_les_cinq_natures_de_rg_26_plus_les_extensions():
    """§ 2.5 : cinq natures RG-26 (trois sans TypeAction encore atteignable —
    note, programme, sujet — déclarées quand même), plus les natures hors
    RG-26 signalées dans docs/suivi/DECISIONS.md.
    """
    attendu = (
        NATURES_RG26_COMPTES
        | NATURES_RG26_PLACEHOLDER
        | NATURES_RG26_AUTHENTIFICATION
        | EXTENSIONS_HORS_RG26
        | NATURES_PATRON_GESTION
    )
    assert set(TypeAction.values) == {nature.value for nature in attendu}
