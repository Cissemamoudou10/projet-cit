"""US-SES-07 — export des stagiaires, couche services (Prompt 26, § 10,
Groupes B et C). Données entièrement fictives.
"""

import csv
import datetime
import io

import openpyxl

from administration.models import EntreeJournal
from organisation.import_stagiaires.confirmation import confirmer
from organisation.import_stagiaires.ecrivain import ecrire_csv, ecrire_xlsx, nom_fichier_export
from organisation.services.affectation import ServiceAffectation
from organisation.services.brigade import ServiceBrigade
from organisation.services.session import ServiceSession
from organisation.services.stagiaire import ServiceStagiaire
from organisation.tests.conftest import donnees_brigade, donnees_session, donnees_stagiaire


def _creer_stagiaires(redacteur, session, noms):
    return [
        ServiceStagiaire.creer(
            redacteur, session, donnees_stagiaire(matricule=f"M{i:03d}", nom=nom)
        )
        for i, nom in enumerate(noms)
    ]


def test_b1_export_csv_colonnes_entetes_nombre_de_lignes(redacteur, session):
    _creer_stagiaires(redacteur, session, ["Aaa", "Bbb"])

    stagiaires = ServiceStagiaire.exporter(redacteur, session, {}, "toutes")
    lignes = list(
        csv.reader(io.StringIO(ecrire_csv(stagiaires).decode("utf-8-sig")), delimiter=";")
    )

    assert lignes[0] == ["Matricule", "Nom", "Prénom", "Grade", "Unité", "Brigade", "Statut"]
    assert len(lignes) == 3


def test_b2_export_xlsx_colonnes_entetes_nombre_de_lignes(redacteur, session):
    _creer_stagiaires(redacteur, session, ["Aaa", "Bbb"])

    stagiaires = ServiceStagiaire.exporter(redacteur, session, {}, "toutes")
    classeur = openpyxl.load_workbook(io.BytesIO(ecrire_xlsx(stagiaires)))
    lignes = list(classeur.active.iter_rows(values_only=True))

    assert list(lignes[0]) == ["Matricule", "Nom", "Prénom", "Grade", "Unité", "Brigade", "Statut"]
    assert len(lignes) == 3


def test_b3_export_respecte_le_filtre_de_brigade(redacteur, session):
    brigade = ServiceBrigade.creer(redacteur, session, donnees_brigade())
    stagiaires = _creer_stagiaires(redacteur, session, ["Aaa", "Bbb"])
    ServiceAffectation.affecter(redacteur, stagiaires[0], brigade)

    exportes = ServiceStagiaire.exporter(redacteur, session, {"brigade": str(brigade.pk)}, "EXP1")

    assert [s.pk for s in exportes] == [stagiaires[0].pk]


def test_b4_export_respecte_le_filtre_de_statut_deux_comptes_differents(
    redacteur, session, stagiaire
):
    ServiceStagiaire.radier(redacteur, stagiaire, "Fin anticipée", datetime.date.today())
    ServiceStagiaire.creer(redacteur, session, donnees_stagiaire(matricule="M999"))

    actifs = ServiceStagiaire.exporter(redacteur, session, {"etat": "actifs"}, "actifs")
    tous = ServiceStagiaire.exporter(redacteur, session, {}, "tous")

    assert len(actifs) == 1
    assert len(tous) == 2


def test_b5_export_respecte_la_recherche_en_cours(redacteur, session):
    _creer_stagiaires(redacteur, session, ["Zalbrok", "Bramvel"])

    exportes = ServiceStagiaire.exporter(redacteur, session, {"recherche": "zalbrok"}, "recherche")

    assert len(exportes) == 1
    assert exportes[0].nom == "Zalbrok"


def test_b6_csv_bom_separateur_point_virgule_accents_intacts_apres_relecture(redacteur, session):
    ServiceStagiaire.creer(redacteur, session, donnees_stagiaire(matricule="M001", nom="Éçàôù"))

    contenu = ecrire_csv(ServiceStagiaire.exporter(redacteur, session, {}, "toutes"))

    assert contenu.startswith(b"\xef\xbb\xbf")
    texte = contenu.decode("utf-8-sig")
    assert ";" in texte.splitlines()[0]
    assert "Éçàôù" in texte


def test_b7_nom_de_fichier_deterministe_sans_espace_accent_ni_caractere_interdit(session):
    nom = nom_fichier_export(session, {"brigade_libelle": "École EXP1", "etat": "actifs"}, "csv")

    assert " " not in nom
    assert all(ord(c) < 128 for c in nom)
    for caractere in '<>:"/\\|?*':
        assert caractere not in nom
    assert nom.endswith(".csv")


def test_b8_aller_retour_export_puis_reimport_sur_une_autre_session_csv_et_xlsx(
    redacteur, session, formation
):
    _creer_stagiaires(redacteur, session, ["Éçàôù", "Bramvel"])
    autre_session = ServiceSession.creer(
        redacteur, donnees_session(formation, intitule="Session 2")
    )

    stagiaires = ServiceStagiaire.exporter(redacteur, session, {}, "toutes")
    rapport_csv = confirmer(redacteur, autre_session, ecrire_csv(stagiaires), "export.csv")
    assert len(rapport_csv.lignes_valides) == 2

    troisieme_session = ServiceSession.creer(
        redacteur, donnees_session(formation, intitule="Session 3")
    )
    rapport_xlsx = confirmer(redacteur, troisieme_session, ecrire_xlsx(stagiaires), "export.xlsx")
    assert len(rapport_xlsx.lignes_valides) == 2

    reimporte = autre_session.stagiaires.get(matricule="M000")
    assert reimporte.nom == "Éçàôù"


def test_b9_export_d_une_liste_vide_fichier_valide_avec_le_seul_entete(redacteur, session):
    exportes = ServiceStagiaire.exporter(redacteur, session, {}, "vide")

    lignes = list(csv.reader(io.StringIO(ecrire_csv(exportes).decode("utf-8-sig")), delimiter=";"))

    assert len(lignes) == 1
    assert lignes[0] == ["Matricule", "Nom", "Prénom", "Grade", "Unité", "Brigade", "Statut"]


def test_b10_export_d_un_radie_filtre_tous_statut_exporte_et_lisible(redacteur, session, stagiaire):
    ServiceStagiaire.radier(redacteur, stagiaire, "Fin anticipée", datetime.date.today())

    exportes = ServiceStagiaire.exporter(redacteur, session, {}, "tous")
    lignes = list(csv.reader(io.StringIO(ecrire_csv(exportes).decode("utf-8-sig")), delimiter=";"))

    assert lignes[1][-1] == "Radié"


def test_c1_export_produit_une_entree_de_journal(redacteur, session):
    _creer_stagiaires(redacteur, session, ["Aaa"])

    ServiceStagiaire.exporter(redacteur, session, {"etat": "actifs"}, "Session X — actifs")

    entree = EntreeJournal.objects.get(objet_type="export_stagiaires")
    assert entree.valeur_apres["nombre_lignes"] == 1
    assert entree.valeur_apres["filtre"] == "Session X — actifs"
    assert entree.auteur == redacteur


def test_c2_l_entree_ne_contient_aucune_identite(redacteur, session):
    _creer_stagiaires(redacteur, session, ["Zalbrok"])

    ServiceStagiaire.exporter(redacteur, session, {}, "toutes")

    entree = EntreeJournal.objects.get(objet_type="export_stagiaires")
    assert "Zalbrok" not in str(entree.valeur_apres)
    assert "M000" not in str(entree.valeur_apres)


def test_c3_simple_consultation_sans_export_ne_journalise_rien(redacteur, session, stagiaire):
    ServiceStagiaire.lister(redacteur, session, {}, None)

    assert not EntreeJournal.objects.filter(objet_type="export_stagiaires").exists()
