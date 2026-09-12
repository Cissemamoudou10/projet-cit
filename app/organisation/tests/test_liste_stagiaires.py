"""US-SES-07 — liste et filtres, couche services (Prompt 26, § 10, Groupe A).

PRÉEXISTAIENT (US-SES-05/06, non dupliqués ici) : liste au niveau de la
session (`test_stagiaire.py`), filtre actifs/radiés
(`test_d2_stagiaire_radie_disparait_des_listes_actives_reste_consultable_avec_filtre`),
pagination et fenêtre partagée (`noyau/tests`). Données entièrement fictives.
"""

import datetime

from organisation.services.affectation import ServiceAffectation
from organisation.services.brigade import ServiceBrigade
from organisation.services.stagiaire import NON_AFFECTES, ServiceStagiaire
from organisation.tests.conftest import donnees_brigade, donnees_stagiaire


def _creer_stagiaires(redacteur, session, noms):
    return [
        ServiceStagiaire.creer(redacteur, session, donnees_stagiaire(matricule=f"M{i:03d}", nom=nom))
        for i, nom in enumerate(noms)
    ]


def test_a2_liste_filtree_sur_une_brigade_seulement_ses_stagiaires(redacteur, session):
    brigade_1 = ServiceBrigade.creer(redacteur, session, donnees_brigade(designation="EXP1"))
    brigade_2 = ServiceBrigade.creer(redacteur, session, donnees_brigade(designation="EXP2"))
    stagiaires = _creer_stagiaires(redacteur, session, ["Aaa", "Bbb"])
    ServiceAffectation.affecter(redacteur, stagiaires[0], brigade_1)
    ServiceAffectation.affecter(redacteur, stagiaires[1], brigade_2)

    page = ServiceStagiaire.lister(redacteur, session, {"brigade": str(brigade_1.pk)}, None)

    pks = [s.pk for s in page]
    assert stagiaires[0].pk in pks
    assert stagiaires[1].pk not in pks


def test_a3_filtre_non_affectes_seulement_ceux_sans_affectation_ouverte(redacteur, session):
    brigade = ServiceBrigade.creer(redacteur, session, donnees_brigade())
    stagiaires = _creer_stagiaires(redacteur, session, ["Aaa", "Bbb"])
    ServiceAffectation.affecter(redacteur, stagiaires[0], brigade)

    page = ServiceStagiaire.lister(redacteur, session, {"brigade": NON_AFFECTES}, None)

    pks = [s.pk for s in page]
    assert stagiaires[0].pk not in pks
    assert stagiaires[1].pk in pks


def test_a4_filtre_tous_les_trois_statuts_distincts(redacteur, session, stagiaire):
    ServiceStagiaire.radier(redacteur, stagiaire, "Fin anticipée", datetime.date.today())
    autre = ServiceStagiaire.creer(redacteur, session, donnees_stagiaire(matricule="M999"))

    tous = [s.pk for s in ServiceStagiaire.lister(redacteur, session, {}, None)]
    actifs = [s.pk for s in ServiceStagiaire.lister(redacteur, session, {"etat": "actifs"}, None)]
    radies = [s.pk for s in ServiceStagiaire.lister(redacteur, session, {"etat": "radies"}, None)]

    assert set(tous) == {stagiaire.pk, autre.pk}
    assert actifs == [autre.pk]
    assert radies == [stagiaire.pk]


def test_a5_recherche_insensible_a_la_casse_et_aux_accents(redacteur, session):
    ServiceStagiaire.creer(redacteur, session, donnees_stagiaire(matricule="M001", nom="Éçàôù"))

    par_nom_sans_accent = ServiceStagiaire.lister(redacteur, session, {"recherche": "ecaou"}, None)
    par_nom_majuscules = ServiceStagiaire.lister(redacteur, session, {"recherche": "ECAOU"}, None)

    assert len(list(par_nom_sans_accent)) == 1
    assert len(list(par_nom_majuscules)) == 1


def test_a6_tri_accentue_e_aigu_e_et_a_ranges_avant_z(redacteur, session):
    """Le tri accentué réel a été validé en base au test d'installation hors
    ligne du 7 septembre (collation ICU fr-FR) : É et E doivent se ranger
    près de A, jamais après Z comme le ferait un tri naïf sur les points de
    code Unicode (É = U+00C9, largement après Z = U+005A)."""
    ServiceStagiaire.creer(redacteur, session, donnees_stagiaire(matricule="M001", nom="Zorro"))
    ServiceStagiaire.creer(redacteur, session, donnees_stagiaire(matricule="M002", nom="Émile"))
    ServiceStagiaire.creer(redacteur, session, donnees_stagiaire(matricule="M003", nom="Emile"))
    ServiceStagiaire.creer(redacteur, session, donnees_stagiaire(matricule="M004", nom="Amar"))

    page = ServiceStagiaire.lister(redacteur, session, {}, None)

    noms = [s.nom for s in page]
    assert noms[0] == "Amar"
    assert noms[-1] == "Zorro"
    assert set(noms[1:3]) == {"Émile", "Emile"}


def test_a7_stagiaire_deplace_apparait_sous_sa_brigade_courante(redacteur, session, stagiaire):
    brigade_1 = ServiceBrigade.creer(redacteur, session, donnees_brigade(designation="EXP1"))
    brigade_2 = ServiceBrigade.creer(redacteur, session, donnees_brigade(designation="EXP2"))
    hier = datetime.date.today() - datetime.timedelta(days=1)
    ServiceAffectation.affecter(redacteur, stagiaire, brigade_1, date_effet=hier)
    ServiceAffectation.deplacer(redacteur, stagiaire, brigade_2, datetime.date.today())

    page = ServiceStagiaire.lister(redacteur, session, {}, None)

    trouve = next(s for s in page if s.pk == stagiaire.pk)
    assert trouve.brigade_designation == "EXP2"
