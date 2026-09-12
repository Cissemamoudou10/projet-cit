"""US-INS-03 — enregistrement et fusion des indisponibilités d'instructeur,
couche services (Prompt 27, § 9, Groupes A et C). Données entièrement
fictives.
"""

import datetime
from unittest.mock import patch

import pytest

from administration.models import EntreeJournal
from noyau.exceptions import ErreurValidation
from ressources.models import IndisponibiliteInstructeur, Instructeur, Statut
from ressources.services.indisponibilite_instructeur import ServiceIndisponibiliteInstructeur
from ressources.services.instructeur import ServiceInstructeur


def _instant(jour, heure, minute=0):
    return datetime.datetime(2026, 10, jour, heure, minute, tzinfo=datetime.UTC)


@pytest.fixture
def autre_instructeur(db):
    return Instructeur.objects.create(
        nom="Bennani",
        prenom="Yasmine",
        grade="Cne",
        specialite="Transmissions",
        statut=Statut.VACATAIRE,
    )


# --- Groupe A — modèle et enregistrement -----------------------------------


def test_a1_enregistrement_nominal_journalise_auteur_agent_connecte(planificateur, instructeur):
    resultat = ServiceIndisponibiliteInstructeur.confirmer(
        planificateur, instructeur, _instant(5, 8), _instant(5, 12), "Mission"
    )

    assert resultat.pk is not None
    assert resultat.cree_par == planificateur
    entree = EntreeJournal.objects.get(objet_type="indisponibilite_instructeur")
    assert entree.auteur == planificateur


def test_a2_rg23_auteur_est_l_agent_aucun_champ_ne_relie_l_instructeur_a_un_compte(
    planificateur, instructeur
):
    """Nommé explicitement pour que RG-23 soit lisible sans aller la
    chercher (§ 4, Prompt 27)."""
    resultat = ServiceIndisponibiliteInstructeur.confirmer(
        planificateur, instructeur, _instant(5, 8), _instant(5, 12), "Mission"
    )

    assert resultat.cree_par == planificateur
    noms_champs = {champ.name for champ in IndisponibiliteInstructeur._meta.get_fields()}
    assert noms_champs == {
        "id",
        "cree_le",
        "modifie_le",
        "cree_par",
        "modifie_par",
        "instructeur",
        "debut",
        "fin",
        "motif",
    }


def test_a3_fin_anterieure_au_debut_refusee_par_le_service(planificateur, instructeur):
    with pytest.raises(ErreurValidation, match="postérieure"):
        ServiceIndisponibiliteInstructeur.proposer(
            planificateur, instructeur, _instant(5, 12), _instant(5, 8), "Mission"
        )


def test_a3_fin_egale_au_debut_refusee_par_le_service(planificateur, instructeur):
    with pytest.raises(ErreurValidation, match="postérieure"):
        ServiceIndisponibiliteInstructeur.proposer(
            planificateur, instructeur, _instant(5, 8), _instant(5, 8), "Mission"
        )


def test_a4_instructeur_archive_refuse_avec_message_correctif(
    planificateur, redacteur, instructeur
):
    ServiceInstructeur.archiver(redacteur, instructeur.pk)
    instructeur.refresh_from_db()

    with pytest.raises(ErreurValidation, match="archivé"):
        ServiceIndisponibiliteInstructeur.proposer(
            planificateur, instructeur, _instant(5, 8), _instant(5, 12), "Mission"
        )


def test_a5_periode_entierement_dans_le_passe_acceptee_sans_avertissement(
    planificateur, instructeur
):
    hier = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=1)
    avant_hier = hier - datetime.timedelta(hours=4)

    proposition = ServiceIndisponibiliteInstructeur.proposer(
        planificateur, instructeur, avant_hier, hier, "Mission passée"
    )

    assert not proposition.absorbees
    assert not proposition.sans_effet


def test_a6_periode_a_cheval_sur_aujourd_hui_acceptee(planificateur, instructeur):
    hier = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=1)
    demain = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=1)

    resultat = ServiceIndisponibiliteInstructeur.confirmer(
        planificateur, instructeur, hier, demain, "Mission en cours"
    )

    assert resultat.pk is not None


def test_a7_granularite_horaire_matin_et_apres_midi_disjoints_acceptees(planificateur, instructeur):
    ServiceIndisponibiliteInstructeur.confirmer(
        planificateur, instructeur, _instant(5, 8), _instant(5, 12), "Matin"
    )

    apres_midi = ServiceIndisponibiliteInstructeur.confirmer(
        planificateur, instructeur, _instant(5, 14), _instant(5, 18), "Après-midi"
    )

    assert apres_midi.pk is not None
    assert instructeur.indisponibilites.count() == 2


# --- Groupe C — fusion -------------------------------------------------


def test_c1_chevauchement_partiel_bornes_attendues_rien_ecrit_avant_confirmation(
    planificateur, instructeur
):
    ServiceIndisponibiliteInstructeur.confirmer(
        planificateur, instructeur, _instant(3, 8), _instant(10, 8), "Mission"
    )

    proposition = ServiceIndisponibiliteInstructeur.proposer(
        planificateur, instructeur, _instant(8, 8), _instant(15, 8), "Permission"
    )

    assert proposition.debut == _instant(3, 8)
    assert proposition.fin == _instant(15, 8)
    assert instructeur.indisponibilites.count() == 1


def test_c2_confirmation_une_seule_periode_subsiste_bornes_fusionnees(planificateur, instructeur):
    ServiceIndisponibiliteInstructeur.confirmer(
        planificateur, instructeur, _instant(3, 8), _instant(10, 8), "Mission"
    )

    ServiceIndisponibiliteInstructeur.confirmer(
        planificateur, instructeur, _instant(8, 8), _instant(15, 8), "Permission"
    )

    restantes = list(instructeur.indisponibilites.all())
    assert len(restantes) == 1
    assert restantes[0].debut == _instant(3, 8)
    assert restantes[0].fin == _instant(15, 8)


def test_c3_echec_au_milieu_de_la_fusion_aucune_periode_supprimee_ni_creee(
    planificateur, instructeur
):
    ServiceIndisponibiliteInstructeur.confirmer(
        planificateur, instructeur, _instant(3, 8), _instant(10, 8), "Mission"
    )

    with (
        patch(
            "ressources.services.indisponibilite_instructeur.ServiceBase.creer",
            side_effect=Exception("échec simulé"),
        ),
        pytest.raises(Exception, match="échec simulé"),
    ):
        ServiceIndisponibiliteInstructeur.confirmer(
            planificateur, instructeur, _instant(8, 8), _instant(15, 8), "Permission"
        )

    restantes = list(instructeur.indisponibilites.all())
    assert len(restantes) == 1
    assert restantes[0].debut == _instant(3, 8)
    assert restantes[0].fin == _instant(10, 8)


def test_c4_fusion_absorbant_deux_periodes_d_un_coup(planificateur, instructeur):
    ServiceIndisponibiliteInstructeur.confirmer(
        planificateur, instructeur, _instant(1, 8), _instant(3, 8), "Mission 1"
    )
    ServiceIndisponibiliteInstructeur.confirmer(
        planificateur, instructeur, _instant(10, 8), _instant(12, 8), "Mission 2"
    )

    resultat = ServiceIndisponibiliteInstructeur.confirmer(
        planificateur, instructeur, _instant(2, 8), _instant(11, 8), "Permission longue"
    )

    assert resultat.debut == _instant(1, 8)
    assert resultat.fin == _instant(12, 8)
    assert instructeur.indisponibilites.count() == 1


def test_c5_periode_contenue_dans_une_existante_signalee_sans_effet_pas_de_doublon(
    planificateur, instructeur
):
    ServiceIndisponibiliteInstructeur.confirmer(
        planificateur, instructeur, _instant(1, 8), _instant(15, 8), "Mission longue"
    )

    proposition = ServiceIndisponibiliteInstructeur.proposer(
        planificateur, instructeur, _instant(5, 8), _instant(8, 8), "Permission"
    )

    assert proposition.sans_effet is True
    with pytest.raises(ErreurValidation, match="déjà entièrement couverte"):
        ServiceIndisponibiliteInstructeur.confirmer(
            planificateur, instructeur, _instant(5, 8), _instant(8, 8), "Permission"
        )
    assert instructeur.indisponibilites.count() == 1


def test_c6_le_journal_conserve_bornes_et_motif_des_periodes_absorbees(planificateur, instructeur):
    ServiceIndisponibiliteInstructeur.confirmer(
        planificateur, instructeur, _instant(3, 8), _instant(10, 8), "Mission initiale"
    )

    ServiceIndisponibiliteInstructeur.confirmer(
        planificateur, instructeur, _instant(8, 8), _instant(15, 8), "Permission"
    )

    entree_absorption = EntreeJournal.objects.filter(
        objet_type="indisponibilite_instructeur", identifiant_saisi__startswith="Absorbée"
    ).get()
    assert entree_absorption.valeur_avant["motif"] == "Mission initiale"


def test_c7_motif_de_la_periode_fusionnee_est_celui_saisi_a_la_confirmation(
    planificateur, instructeur
):
    """Choix retenu au § 3 (DECISIONS.md) : le motif est celui saisi par
    l'agent à la confirmation, jamais une concaténation ni un refus sur
    motifs différents."""
    ServiceIndisponibiliteInstructeur.confirmer(
        planificateur, instructeur, _instant(3, 8), _instant(10, 8), "Mission"
    )

    resultat = ServiceIndisponibiliteInstructeur.confirmer(
        planificateur,
        instructeur,
        _instant(8, 8),
        _instant(15, 8),
        "Permission — remplace la mission",
    )

    assert resultat.motif == "Permission — remplace la mission"


def test_c8_le_message_de_proposition_nomme_les_periodes_concernees_avec_leurs_bornes(
    planificateur, instructeur
):
    ServiceIndisponibiliteInstructeur.confirmer(
        planificateur, instructeur, _instant(3, 8), _instant(10, 8), "Mission"
    )

    proposition = ServiceIndisponibiliteInstructeur.proposer(
        planificateur, instructeur, _instant(8, 8), _instant(15, 8), "Permission"
    )

    assert len(proposition.absorbees) == 1
    absorbee = proposition.absorbees[0]
    assert absorbee.debut == _instant(3, 8)
    assert absorbee.fin == _instant(10, 8)
    assert absorbee.motif == "Mission"
