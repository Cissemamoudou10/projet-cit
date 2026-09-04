"""US-INS-01 — Gérer les instructeurs, CU-P4-01. Le modèle, ses contraintes
en base et le service — les écrans sont dans test_instructeur_ecran.py.
"""

import pytest
from django.db import IntegrityError, transaction
from django.db.models import ForeignKey

from administration.models import EntreeJournal, TypeAction, Utilisateur
from noyau.exceptions import ErreurHabilitation, ErreurModificationConcurrente, ErreurValidation
from ressources.models import Instructeur, Statut
from ressources.services.instructeur import ServiceInstructeur


def _donnees(**supplement):
    donnees = {
        "nom": "Ziani",
        "prenom": "Karim",
        "matricule": "M12345",
        "grade": "Lt",
        "specialite": "Transmissions",
        "statut": Statut.MILITAIRE_DU_CENTRE,
    }
    donnees.update(supplement)
    return donnees


def test_creation_avec_les_six_attributs(redacteur):
    instructeur = ServiceInstructeur.creer(redacteur, _donnees())

    assert instructeur.pk is not None
    assert instructeur.nom == "Ziani"
    assert instructeur.prenom == "Karim"
    assert instructeur.matricule == "M12345"
    assert instructeur.grade == "Lt"
    assert instructeur.specialite == "Transmissions"
    assert instructeur.statut == Statut.MILITAIRE_DU_CENTRE


def test_instructeur_ne_porte_aucune_cle_etrangere_vers_utilisateur():
    """Test de non-présence, § 3.1 : un instructeur n'est pas un utilisateur
    du système — voir les critères d'US-INS-03. `cree_par`/`modifie_par`
    (`ModeleHorodate`, sur tout modèle du patron) sont l'auteur d'une
    écriture, pas une relation métier vers l'instructeur lui-même : seuls
    les autres champs comptent ici.
    """
    cibles = {
        champ.related_model
        for champ in Instructeur._meta.get_fields()
        if isinstance(champ, ForeignKey) and champ.name not in ("cree_par", "modifie_par")
    }
    assert Utilisateur not in cibles


def test_statut_hors_des_trois_valeurs_est_refuse_en_base(db):
    with pytest.raises(IntegrityError), transaction.atomic():
        Instructeur.objects.create(**_donnees(statut="stagiaire"))


def test_matricule_obligatoire_pour_un_militaire_du_centre_impose_en_base(db):
    with pytest.raises(IntegrityError), transaction.atomic():
        Instructeur.objects.create(**_donnees(matricule=None, statut=Statut.MILITAIRE_DU_CENTRE))


def test_matricule_facultatif_pour_un_vacataire(db):
    Instructeur.objects.create(  # ne lève pas
        **_donnees(matricule=None, statut=Statut.VACATAIRE, nom="Alaoui")
    )


def test_deux_vacataires_sans_matricule_coexistent(db):
    Instructeur.objects.create(**_donnees(matricule=None, statut=Statut.VACATAIRE, nom="Alaoui"))

    Instructeur.objects.create(  # ne lève pas
        **_donnees(matricule=None, statut=Statut.CIVIL, nom="Bennani")
    )


def test_matricule_duplique_est_refuse_en_base(db):
    Instructeur.objects.create(**_donnees())

    with pytest.raises(IntegrityError), transaction.atomic():
        Instructeur.objects.create(**_donnees(nom="Autre"))


def test_matricule_duplique_est_refuse_avec_l_instructeur_existant(redacteur):
    ServiceInstructeur.creer(redacteur, _donnees())

    with pytest.raises(ErreurValidation) as info:
        ServiceInstructeur.creer(redacteur, _donnees(nom="Autre"))

    assert "M12345" in str(info.value)
    assert "Ziani" in str(info.value)


def test_liste_paginee_au_dela_de_vingt_instructeurs(redacteur):
    for i in range(21):
        ServiceInstructeur.creer(
            redacteur, _donnees(nom=f"Instructeur {i:02d}", matricule=f"M{i:05d}")
        )

    page = ServiceInstructeur.lister(redacteur, {}, None)

    assert page.has_next()


def test_recherche_par_nom_par_prenom_et_par_matricule(redacteur):
    ServiceInstructeur.creer(redacteur, _donnees())
    ServiceInstructeur.creer(
        redacteur, _donnees(nom="Alaoui", prenom="Yassine", matricule="M99999")
    )

    par_nom = ServiceInstructeur.lister(redacteur, {"recherche": "Ziani"}, None)
    par_prenom = ServiceInstructeur.lister(redacteur, {"recherche": "Yassine"}, None)
    par_matricule = ServiceInstructeur.lister(redacteur, {"recherche": "M9999"}, None)

    assert [i.nom for i in par_nom] == ["Ziani"]
    assert [i.nom for i in par_prenom] == ["Alaoui"]
    assert [i.nom for i in par_matricule] == ["Alaoui"]


def test_filtre_par_statut(redacteur):
    ServiceInstructeur.creer(redacteur, _donnees())
    ServiceInstructeur.creer(redacteur, _donnees(nom="Alaoui", matricule=None, statut=Statut.CIVIL))

    page = ServiceInstructeur.lister(redacteur, {"statut": Statut.CIVIL}, None)

    assert [i.nom for i in page] == ["Alaoui"]


def test_filtre_par_specialite(redacteur):
    ServiceInstructeur.creer(redacteur, _donnees())
    ServiceInstructeur.creer(
        redacteur, _donnees(nom="Alaoui", matricule="M99999", specialite="Informatique")
    )

    page = ServiceInstructeur.lister(redacteur, {"specialite": "Informatique"}, None)

    assert [i.nom for i in page] == ["Alaoui"]


def test_le_filtre_de_specialite_n_offre_que_les_valeurs_enregistrees(redacteur):
    ServiceInstructeur.creer(redacteur, _donnees(specialite="Transmissions"))
    ServiceInstructeur.creer(
        redacteur, _donnees(nom="Alaoui", matricule="M99999", specialite="Informatique")
    )

    valeurs = list(ServiceInstructeur.valeurs_specialite_distinctes())

    assert valeurs == ["Informatique", "Transmissions"]


def test_methode_d_enumeration_des_bloquants_existe_et_ne_trouve_rien(redacteur):
    """Critère 4, § 3.3 du Prompt 12 : le blocage par une affectation à un
    programme en cours n'est pas testable aujourd'hui — le programme
    appartient à US-PLAN-03, sprint 3. La suppression ne doit rien trouver
    qui s'y oppose, en attendant.
    """
    instructeur = ServiceInstructeur.creer(redacteur, _donnees())

    ServiceInstructeur.supprimer(redacteur, instructeur.pk)  # ne lève pas

    assert not Instructeur.objects.filter(pk=instructeur.pk).exists()


def test_instructeur_archive_absent_de_la_selection_present_en_consultation(redacteur):
    instructeur = ServiceInstructeur.creer(redacteur, _donnees())
    ServiceInstructeur.archiver(redacteur, instructeur.pk)

    disponibles = ServiceInstructeur.disponibles_pour_selection()
    page_consultation = ServiceInstructeur.lister(redacteur, {}, None)

    assert instructeur.pk not in disponibles.values_list("pk", flat=True)
    assert instructeur.pk in [ligne.pk for ligne in page_consultation]


def test_l_archivage_ne_supprime_rien(redacteur):
    instructeur = ServiceInstructeur.creer(redacteur, _donnees())

    ServiceInstructeur.archiver(redacteur, instructeur.pk)

    assert Instructeur.objects.filter(pk=instructeur.pk).exists()


def test_cellule_pedagogique_ecrit(redacteur):
    ServiceInstructeur.creer(redacteur, _donnees())  # ne lève pas


def test_planification_et_direction_formation_lisent_seulement(planificateur, direction_formation):
    ServiceInstructeur.lister(planificateur, {}, None)  # ne lève pas
    ServiceInstructeur.lister(direction_formation, {}, None)  # ne lève pas

    with pytest.raises(ErreurHabilitation):
        ServiceInstructeur.creer(planificateur, _donnees())
    with pytest.raises(ErreurHabilitation):
        ServiceInstructeur.creer(direction_formation, _donnees())


def test_cellule_examens_n_a_aucun_acces_ni_lecture_ni_ecriture(cellule_examens):
    """§ 4.1 du Prompt 12 : vrai aujourd'hui parce que la matrice § 11.2 ne
    donne rien à la cellule examens sur `instructeurs_qualifications` — ce
    test **doit tomber** le jour où CU-P6-04 (désignation des surveillants,
    sprint 4) obtient l'arbitrage inverse. Ne le supprime pas alors,
    change-le : il documente pourquoi le refus existait.
    """
    with pytest.raises(ErreurHabilitation):
        ServiceInstructeur.lister(cellule_examens, {}, None)
    with pytest.raises(ErreurHabilitation):
        ServiceInstructeur.creer(cellule_examens, _donnees())


def test_creation_modification_archivage_sont_journalises(redacteur):
    instructeur = ServiceInstructeur.creer(redacteur, _donnees())
    ServiceInstructeur.modifier(
        redacteur, instructeur.pk, _donnees(grade="Cne"), instructeur.modifie_le
    )
    ServiceInstructeur.archiver(redacteur, instructeur.pk)

    natures = list(
        EntreeJournal.objects.filter(objet_type="instructeur", objet_identifiant="Ziani")
        .order_by("cree_le")
        .values_list("type_action", flat=True)
    )
    assert TypeAction.CREATION_ELEMENT_GESTION in natures
    assert TypeAction.MODIFICATION_ELEMENT_GESTION in natures
    assert TypeAction.ARCHIVAGE_ELEMENT_GESTION in natures


def test_modification_concurrente_est_detectee(redacteur):
    instructeur = ServiceInstructeur.creer(redacteur, _donnees())
    modifie_le_initial = instructeur.modifie_le

    ServiceInstructeur.modifier(
        redacteur, instructeur.pk, _donnees(grade="Cne"), modifie_le_initial
    )

    with pytest.raises(ErreurModificationConcurrente) as info:
        ServiceInstructeur.modifier(
            redacteur, instructeur.pk, _donnees(grade="Cdt"), modifie_le_initial
        )
    assert redacteur.username in str(info.value)
