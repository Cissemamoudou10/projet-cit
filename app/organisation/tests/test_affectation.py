"""US-SES-06 — contrôles à l'affectation individuelle, couche services
(Prompt 25, § 12, Groupe B — volet sans salle attitrée réelle). Les tests
exigeant une capacité réelle (RG-19, B4/B5/B6) vivent dans
`app/ressources/tests/test_affectation_capacite.py` — `organisation` ne peut
pas construire de `SalleAttitree` (D-85). Données entièrement fictives.
"""

import datetime

import pytest

from administration.models import EntreeJournal
from noyau.exceptions import ErreurValidation
from organisation.services.affectation import ServiceAffectation
from organisation.services.brigade import ServiceBrigade
from organisation.services.stagiaire import ServiceStagiaire
from organisation.tests.conftest import donnees_brigade, donnees_stagiaire


@pytest.fixture
def brigade_sans_salle(redacteur, session):
    return ServiceBrigade.creer(redacteur, session, donnees_brigade(designation="EXP2"))


def test_b1_affectation_nominale_journalisee(redacteur, session, stagiaire, brigade_sans_salle):
    affectation = ServiceAffectation.affecter(redacteur, stagiaire, brigade_sans_salle)

    assert affectation.date_fin is None
    assert ServiceBrigade.effectif_reel(brigade_sans_salle) == 1
    assert EntreeJournal.objects.filter(objet_type="affectation_brigade").exists()


def test_b2_stagiaire_radie_refuse(redacteur, session, stagiaire, brigade_sans_salle):
    ServiceStagiaire.radier(redacteur, stagiaire, "Fin anticipée", datetime.date.today())

    with pytest.raises(ErreurValidation, match="radié"):
        ServiceAffectation.affecter(redacteur, stagiaire, brigade_sans_salle)


def test_b3_rg20_deja_affecte_refus_brigade_actuelle_nommee_deplacement_propose(
    redacteur, session, stagiaire, brigade_sans_salle
):
    ServiceAffectation.affecter(redacteur, stagiaire, brigade_sans_salle)
    autre_brigade = ServiceBrigade.creer(redacteur, session, donnees_brigade(designation="EXP3"))

    with pytest.raises(ErreurValidation) as info:
        ServiceAffectation.affecter(redacteur, stagiaire, autre_brigade)

    assert "EXP2" in str(info.value)
    assert "déplacez" in str(info.value).lower()


def test_b7_brigade_sans_salle_attitree_acceptee_avec_avertissement(
    redacteur, session, stagiaire, brigade_sans_salle
):
    affectation = ServiceAffectation.affecter(redacteur, stagiaire, brigade_sans_salle)

    codes = [a["code"] for a in affectation.avertissements]
    assert "brigade_sans_salle" in codes


def test_e1_deplacement_ferme_l_ancienne_ouvre_la_nouvelle_jamais_deux_ouvertes(
    redacteur, session, stagiaire, brigade_sans_salle
):
    hier = datetime.date.today() - datetime.timedelta(days=1)
    aujourd_hui = datetime.date.today()
    autre_brigade = ServiceBrigade.creer(redacteur, session, donnees_brigade(designation="EXP3"))
    ancienne = ServiceAffectation.affecter(
        redacteur, stagiaire, brigade_sans_salle, date_effet=hier
    )

    nouvelle = ServiceAffectation.deplacer(redacteur, stagiaire, autre_brigade, aujourd_hui)

    ancienne.refresh_from_db()
    assert ancienne.date_fin == aujourd_hui
    assert nouvelle.date_fin is None
    assert nouvelle.brigade == autre_brigade
    assert stagiaire.affectations.filter(date_fin__isnull=True).count() == 1


def test_e2_avertissement_deplacement_reellement_produit(
    redacteur, session, stagiaire, brigade_sans_salle
):
    hier = datetime.date.today() - datetime.timedelta(days=1)
    aujourd_hui = datetime.date.today()
    autre_brigade = ServiceBrigade.creer(redacteur, session, donnees_brigade(designation="EXP3"))
    ServiceAffectation.affecter(redacteur, stagiaire, brigade_sans_salle, date_effet=hier)

    nouvelle = ServiceAffectation.deplacer(redacteur, stagiaire, autre_brigade, aujourd_hui)

    codes = [a["code"] for a in nouvelle.avertissements]
    assert "deplacement_historique" in codes


def test_e3_effectif_reel_exclut_le_stagiaire_radie(redacteur, session, brigade_sans_salle):
    stagiaire_1 = ServiceStagiaire.creer(redacteur, session, donnees_stagiaire(matricule="M001"))
    stagiaire_2 = ServiceStagiaire.creer(redacteur, session, donnees_stagiaire(matricule="M002"))
    stagiaire_3 = ServiceStagiaire.creer(redacteur, session, donnees_stagiaire(matricule="M003"))
    for stagiaire in (stagiaire_1, stagiaire_2, stagiaire_3):
        ServiceAffectation.affecter(redacteur, stagiaire, brigade_sans_salle)
    ServiceStagiaire.radier(redacteur, stagiaire_3, "Fin anticipée", datetime.date.today())

    assert ServiceBrigade.effectif_reel(brigade_sans_salle) == 2


def test_e4_effectif_reel_decroit_a_l_origine_croit_a_la_destination(
    redacteur, session, stagiaire, brigade_sans_salle
):
    hier = datetime.date.today() - datetime.timedelta(days=1)
    aujourd_hui = datetime.date.today()
    destination = ServiceBrigade.creer(redacteur, session, donnees_brigade(designation="EXP3"))
    ServiceAffectation.affecter(redacteur, stagiaire, brigade_sans_salle, date_effet=hier)

    ServiceAffectation.deplacer(redacteur, stagiaire, destination, aujourd_hui)

    assert ServiceBrigade.effectif_reel(brigade_sans_salle) == 0
    assert ServiceBrigade.effectif_reel(destination) == 1


def test_e5_historique_d_un_stagiaire_deplace_deux_fois_trois_lignes_une_seule_ouverte(
    redacteur, session, stagiaire, brigade_sans_salle
):
    brigade_2 = ServiceBrigade.creer(redacteur, session, donnees_brigade(designation="EXP3"))
    brigade_3 = ServiceBrigade.creer(redacteur, session, donnees_brigade(designation="EXP4"))
    avant_hier = datetime.date.today() - datetime.timedelta(days=2)
    hier = datetime.date.today() - datetime.timedelta(days=1)
    aujourd_hui = datetime.date.today()
    ServiceAffectation.affecter(redacteur, stagiaire, brigade_sans_salle, date_effet=avant_hier)
    ServiceAffectation.deplacer(redacteur, stagiaire, brigade_2, hier)
    ServiceAffectation.deplacer(redacteur, stagiaire, brigade_3, aujourd_hui)

    historique = list(ServiceAffectation.historique(redacteur, stagiaire))

    assert len(historique) == 3
    ouvertes = [a for a in historique if a.date_fin is None]
    assert len(ouvertes) == 1
    assert ouvertes[0].brigade == brigade_3


def test_e6_aucun_champ_effectif_reel_stocke_sur_brigade():
    from organisation.models import Brigade

    noms_champs = {champ.name for champ in Brigade._meta.get_fields()}
    assert "effectif_reel" not in noms_champs


def test_retirer_refuse_une_date_de_fin_future(redacteur, session, stagiaire, brigade_sans_salle):
    """Découvert en relecture de conception (§ 13, Prompt 25) : `retirer`
    n'appliquait pas la même règle que `affecter`/`deplacer` (D-106) — une
    date future fausserait l'effectif réel jusqu'à cette date."""
    demain = datetime.date.today() + datetime.timedelta(days=1)
    ServiceAffectation.affecter(
        redacteur,
        stagiaire,
        brigade_sans_salle,
        date_effet=datetime.date.today() - datetime.timedelta(days=5),
    )

    with pytest.raises(ErreurValidation, match="future"):
        ServiceAffectation.retirer(redacteur, stagiaire, demain)


def test_retrait_le_jour_meme_de_l_ouverture_est_desormais_accepte(
    redacteur, session, stagiaire, brigade_sans_salle
):
    """Recette RECETTE-00 (R00-SES-15), NC majeur — symétrique au test de
    déplacement ci-dessous : un retrait le jour même de l'ouverture est
    un intervalle vide (`date_fin == date_effet`), pas une durée négative."""
    ServiceAffectation.affecter(redacteur, stagiaire, brigade_sans_salle)

    actuelle = ServiceAffectation.retirer(redacteur, stagiaire, datetime.date.today())

    assert actuelle.date_fin == datetime.date.today()
    assert ServiceAffectation.affectation_ouverte(stagiaire) is None


def test_historique_departage_deux_deplacements_du_meme_jour_dans_l_ordre_reel(
    redacteur, session, stagiaire, brigade_sans_salle
):
    """`date_effet` seule ne départage pas deux lignes ouvertes/fermées le
    même jour (trois déplacements le même jour) : `historique()` doit lire
    dans l'ordre réel des déplacements, du plus récent au plus ancien —
    recette RECETTE-00 (R00-SES-15)."""
    brigade_2 = ServiceBrigade.creer(redacteur, session, donnees_brigade(designation="EXP3"))
    brigade_3 = ServiceBrigade.creer(redacteur, session, donnees_brigade(designation="EXP4"))
    aujourd_hui = datetime.date.today()
    ServiceAffectation.affecter(redacteur, stagiaire, brigade_sans_salle, date_effet=aujourd_hui)
    ServiceAffectation.deplacer(redacteur, stagiaire, brigade_2, aujourd_hui)
    ServiceAffectation.deplacer(redacteur, stagiaire, brigade_3, aujourd_hui)

    historique = list(ServiceAffectation.historique(redacteur, stagiaire))

    assert [a.brigade for a in historique] == [brigade_3, brigade_2, brigade_sans_salle]
    assert historique[0].date_fin is None


def test_historique_dit_la_bonne_brigade_a_la_date_du_deplacement_le_jour_meme(
    redacteur, session, stagiaire, brigade_sans_salle
):
    """RG-20 : « dire à quelle brigade appartenait le stagiaire à toute
    date passée » doit rester vrai le jour même d'un déplacement — demi-
    ouvert comme les autres plages du projet (`[date_effet, date_fin)`) :
    à la date de bascule, c'est la NOUVELLE brigade qui s'applique, jamais
    les deux à la fois."""
    autre_brigade = ServiceBrigade.creer(redacteur, session, donnees_brigade(designation="EXP3"))
    jour_bascule = datetime.date.today()
    ServiceAffectation.affecter(
        redacteur,
        stagiaire,
        brigade_sans_salle,
        date_effet=jour_bascule - datetime.timedelta(days=5),
    )
    ServiceAffectation.deplacer(redacteur, stagiaire, autre_brigade, jour_bascule)

    historique = list(ServiceAffectation.historique(redacteur, stagiaire))
    for affectation in historique:
        appartient = affectation.date_effet <= jour_bascule and (
            affectation.date_fin is None or jour_bascule < affectation.date_fin
        )
        if appartient:
            assert affectation.brigade == autre_brigade
            break
    else:
        pytest.fail("Aucune affectation de l'historique ne couvre le jour de bascule.")


def test_deplacement_le_jour_meme_de_l_ouverture_est_desormais_accepte(
    redacteur, session, stagiaire, brigade_sans_salle
):
    """Recette RECETTE-00 (R00-SES-15), NC majeur : le jour même reste
    refusé seulement pour une date ANTÉRIEURE à l'ouverture, plus pour une
    date égale — `ck_affectation_dates` accepte maintenant `date_fin ==
    date_effet` (voir DECISIONS.md, supersède D-110). Remplace l'ancien
    `test_deplacement_le_jour_meme_de_l_ouverture_est_impossible`, qui
    affirmait le refus."""
    autre_brigade = ServiceBrigade.creer(redacteur, session, donnees_brigade(designation="EXP3"))
    ServiceAffectation.affecter(redacteur, stagiaire, brigade_sans_salle)

    with pytest.raises(ErreurValidation, match="future"):
        ServiceAffectation.deplacer(
            redacteur, stagiaire, autre_brigade, datetime.date.today() + datetime.timedelta(days=1)
        )

    nouvelle = ServiceAffectation.deplacer(
        redacteur, stagiaire, autre_brigade, datetime.date.today()
    )

    assert nouvelle.brigade == autre_brigade
    assert nouvelle.date_effet == datetime.date.today()
    assert stagiaire.affectations.filter(date_fin__isnull=True).count() == 1
