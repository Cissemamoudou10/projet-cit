"""US-SES-03 — couche services, CU-P3-03. Groupe A (Prompt 22, § 9)."""

import datetime

import pytest
from django.db import IntegrityError, transaction

from administration.models import EntreeJournal, TypeAction
from noyau.exceptions import ErreurHabilitation, ErreurValidation
from organisation.services.brigade import ServiceBrigade
from organisation.services.session import ServiceSession
from referentiel.models import CategorieLieu as CategorieLieuReferentiel
from referentiel.models import ElementReferentiel, Formation, Matiere, TypeFormation
from ressources.models import CategorieLieu, IndisponibiliteLieu, Lieu, SalleAttitree, TypeLieuPartage
from ressources.services.salle_attitree import ServiceSalleAttitree


def _creer_session_et_brigade(redacteur, *, designation, date_debut, date_fin, effectif=20):
    type_formation = TypeFormation.objects.create(intitule=f"Type {designation}")
    formation = Formation.objects.create(
        intitule=f"Formation {designation}",
        specialite="Transmissions",
        duree_semaines=10,
        type_formation=type_formation,
    )
    ElementReferentiel.objects.create(
        formation=formation,
        matiere=Matiere.objects.create(intitule=f"Matière {designation}", code=designation[:10]),
        volume_horaire_prescrit=40,
        categorie_lieu=CategorieLieuReferentiel.SALLE_ATTITREE,
        type_lieu_partage=None,
    )
    session = ServiceSession.creer(
        redacteur,
        {
            "formation": formation,
            "intitule": f"Session {designation}",
            "date_debut": date_debut,
            "date_fin": date_fin,
            "effectif_attendu": effectif,
        },
    )
    brigade = ServiceBrigade.creer(
        redacteur, session, {"designation": designation, "effectif_previsionnel": effectif}
    )
    return session, brigade


def test_a1_attribution_nominale_enregistree_et_journalisee(planificateur, brigade, lieu):
    salle = ServiceSalleAttitree.attribuer(planificateur, brigade, lieu)

    assert salle.lieu == lieu
    assert salle.brigade == brigade
    assert EntreeJournal.objects.filter(
        type_action=TypeAction.CREATION_ELEMENT_GESTION, auteur=planificateur
    ).exists()


def test_a2_lieu_partage_refuse(planificateur, brigade):
    lieu_partage = Lieu.objects.create(
        intitule="Amphi A",
        capacite=100,
        categorie=CategorieLieu.LIEU_PARTAGE,
        type_partage=TypeLieuPartage.AMPHITHEATRE,
    )

    with pytest.raises(ErreurValidation):
        ServiceSalleAttitree.attribuer(planificateur, brigade, lieu_partage)


def test_a3_lieu_archive_refuse(planificateur, brigade, lieu):
    lieu.archive = True
    lieu.save()

    with pytest.raises(ErreurValidation):
        ServiceSalleAttitree.attribuer(planificateur, brigade, lieu)


def test_a4_lieu_sans_capacite_renseignee_refuse_message_nomme_le_lieu(planificateur, brigade):
    """Défensif : `Lieu.capacite` est NOT NULL en base (§ 0.2), ce cas ne
    peut pas survenir pour un lieu réellement enregistré — objet non
    persisté, pour exercer le contrôle malgré tout (RG-13 est une règle
    dure qu'on ne doit jamais silencieusement sauter)."""
    lieu_sans_capacite = Lieu(intitule="Salle sans capacité", categorie=CategorieLieu.SALLE_ATTITREE)
    lieu_sans_capacite.capacite = None

    with pytest.raises(ErreurValidation) as info:
        ServiceSalleAttitree.attribuer(planificateur, brigade, lieu_sans_capacite)

    assert "Salle sans capacité" in str(info.value)


def test_a5_capacite_inferieure_refusee_avec_ecart_chiffre(planificateur, brigade):
    petite_salle = Lieu.objects.create(
        intitule="Petite salle", capacite=15, categorie=CategorieLieu.SALLE_ATTITREE
    )

    with pytest.raises(ErreurValidation) as info:
        ServiceSalleAttitree.attribuer(planificateur, brigade, petite_salle)

    assert "5" in str(info.value)


def test_a5_capacite_egale_a_l_effectif_acceptee(planificateur, brigade):
    salle_juste = Lieu.objects.create(
        intitule="Salle juste", capacite=brigade.effectif_previsionnel, categorie=CategorieLieu.SALLE_ATTITREE
    )

    salle = ServiceSalleAttitree.attribuer(planificateur, brigade, salle_juste)

    assert salle.pk is not None


def test_a6_rg14_deux_brigades_sessions_chevauchantes_second_refus_nomme(planificateur, redacteur, lieu):
    aujourd_hui = datetime.date.today()
    _, brigade_a = _creer_session_et_brigade(
        redacteur,
        designation="A6-A",
        date_debut=aujourd_hui + datetime.timedelta(days=10),
        date_fin=aujourd_hui + datetime.timedelta(days=40),
    )
    _, brigade_b = _creer_session_et_brigade(
        redacteur,
        designation="A6-B",
        date_debut=aujourd_hui + datetime.timedelta(days=30),
        date_fin=aujourd_hui + datetime.timedelta(days=60),
    )
    ServiceSalleAttitree.attribuer(planificateur, brigade_a, lieu)

    with pytest.raises(ErreurValidation) as info:
        ServiceSalleAttitree.attribuer(planificateur, brigade_b, lieu)

    assert "A6-A" in str(info.value)


def test_a7_rg14_periodes_strictement_contigues_acceptee(planificateur, redacteur, lieu):
    """Comportement des bornes (§ 9, A7) : deux périodes strictement
    contiguës ne se chevauchent pas — voir `_periodes_secantes`."""
    aujourd_hui = datetime.date.today()
    fin_a = aujourd_hui + datetime.timedelta(days=40)
    _, brigade_a = _creer_session_et_brigade(
        redacteur, designation="A7-A", date_debut=aujourd_hui + datetime.timedelta(days=10), date_fin=fin_a
    )
    _, brigade_b = _creer_session_et_brigade(
        redacteur,
        designation="A7-B",
        date_debut=fin_a + datetime.timedelta(days=1),
        date_fin=fin_a + datetime.timedelta(days=30),
    )
    ServiceSalleAttitree.attribuer(planificateur, brigade_a, lieu)

    salle_b = ServiceSalleAttitree.attribuer(planificateur, brigade_b, lieu)

    assert salle_b.pk is not None


def test_a8_rg14_deux_brigades_de_la_meme_session_refuse(planificateur, redacteur, session, lieu):
    brigade_1 = ServiceBrigade.creer(redacteur, session, {"designation": "B1", "effectif_previsionnel": 15})
    brigade_2 = ServiceBrigade.creer(redacteur, session, {"designation": "B2", "effectif_previsionnel": 15})
    ServiceSalleAttitree.attribuer(planificateur, brigade_1, lieu)

    with pytest.raises(ErreurValidation):
        ServiceSalleAttitree.attribuer(planificateur, brigade_2, lieu)


def test_a9_changement_de_salle_periode_ecoulee_libre_acceptee(planificateur, redacteur, lieu):
    """Test central de la story : la nouvelle salle est occupée sur une
    période déjà écoulée — seule la période RESTANTE compte (A2, § 4)."""
    aujourd_hui = datetime.date.today()
    _, brigade_ecoulee = _creer_session_et_brigade(
        redacteur,
        designation="A9-passee",
        date_debut=aujourd_hui - datetime.timedelta(days=60),
        date_fin=aujourd_hui - datetime.timedelta(days=5),
    )
    autre_lieu = Lieu.objects.create(
        intitule="Salle A9 historique", capacite=30, categorie=CategorieLieu.SALLE_ATTITREE
    )
    ServiceSalleAttitree.attribuer(planificateur, brigade_ecoulee, autre_lieu)

    _, brigade_en_cours = _creer_session_et_brigade(
        redacteur,
        designation="A9-cours",
        date_debut=aujourd_hui - datetime.timedelta(days=10),
        date_fin=aujourd_hui + datetime.timedelta(days=30),
    )
    salle_en_cours = ServiceSalleAttitree.attribuer(planificateur, brigade_en_cours, lieu)

    salle_modifiee = ServiceSalleAttitree.modifier(planificateur, salle_en_cours, autre_lieu)

    assert salle_modifiee.lieu == autre_lieu


def test_a10_retrait_accepte_et_journalise(planificateur, brigade, lieu):
    salle = ServiceSalleAttitree.attribuer(planificateur, brigade, lieu)

    ServiceSalleAttitree.retirer(planificateur, salle)

    assert not SalleAttitree.objects.filter(pk=salle.pk).exists()
    assert EntreeJournal.objects.filter(type_action=TypeAction.SUPPRESSION_ELEMENT_GESTION).exists()


def test_a11_avertissement_indisponibilite_recouvrant_attribution_enregistree(
    planificateur, brigade, lieu, session
):
    debut_indispo = datetime.datetime.combine(session.date_debut, datetime.time(8, 0)).replace(
        tzinfo=datetime.timezone.utc
    )
    IndisponibiliteLieu.objects.create(
        lieu=lieu, debut=debut_indispo, fin=debut_indispo + datetime.timedelta(hours=2), motif="Travaux"
    )

    salle = ServiceSalleAttitree.attribuer(planificateur, brigade, lieu)

    assert salle.pk is not None
    assert len(salle.avertissements) == 1
    assert salle.avertissements[0]["code"] == "salle_partiellement_indisponible"


def test_a12_suppression_d_un_lieu_attitre_refusee_avec_enumeration(planificateur, brigade, lieu):
    from ressources.services.lieu import ServiceLieu

    ServiceSalleAttitree.attribuer(planificateur, brigade, lieu)

    with pytest.raises(ErreurValidation) as info:
        ServiceLieu.supprimer(planificateur, lieu.pk)

    assert brigade.designation in str(info.value)
    assert Lieu.objects.filter(pk=lieu.pk).exists()


def test_a13_suppression_d_une_brigade_dotee_d_une_salle_refusee_avec_enumeration(
    planificateur, redacteur, brigade, lieu
):
    ServiceSalleAttitree.attribuer(planificateur, brigade, lieu)

    with pytest.raises(ErreurValidation):
        ServiceBrigade.supprimer(redacteur, brigade)


def test_lister_pour_lieu_retourne_les_brigades_attitrees(planificateur, brigade, lieu):
    """Relecture US-SES-03 : la fiche d'un lieu appelle un service, jamais
    un gestionnaire de relation à même le modèle (.claude/rules/vues.md)."""
    ServiceSalleAttitree.attribuer(planificateur, brigade, lieu)

    resultat = list(ServiceSalleAttitree.lister_pour_lieu(planificateur, lieu))

    assert [salle.brigade for salle in resultat] == [brigade]


def test_habilitation_insuffisante_refuse(redacteur, brigade, lieu):
    with pytest.raises(ErreurHabilitation):
        ServiceSalleAttitree.attribuer(redacteur, brigade, lieu)


# --- Groupe B — contraintes réellement en base --------------------------


def test_uq_salle_attitree_brigade_en_base(brigade, lieu):
    autre_lieu = Lieu.objects.create(
        intitule="Autre salle base", capacite=30, categorie=CategorieLieu.SALLE_ATTITREE
    )
    SalleAttitree.objects.create(brigade=brigade, lieu=lieu)
    with pytest.raises(IntegrityError), transaction.atomic():
        SalleAttitree.objects.create(brigade=brigade, lieu=autre_lieu)
