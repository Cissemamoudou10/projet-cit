"""Jeu de données de recette du sprint 2 — Prompt 34, § 7. Données entièrement
fictives.
"""

import io

import openpyxl
import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError

from noyau.exceptions import ErreurValidation
from organisation.import_stagiaires.analyse import analyser
from organisation.import_stagiaires.confirmation import confirmer
from organisation.models import Session
from organisation.services.session import ServiceSession
from planification.jeu_recette.donnees import (
    CODE_LIEU_IMPOSSIBLE,
    COMPTES,
    IDENTIFIANT_ADMINISTRATEUR,
    LIBELLE_FORMATION_PAGINATION,
    NOMBRE_SESSIONS_PAGINATION,
)
from planification.jeu_recette.fichiers_import import constructeur
from referentiel.models import Formation
from ressources.models import Instructeur, Lieu, ModePartage

pytestmark = pytest.mark.django_db


# --- Chargement nominal, idempotence, --reinitialiser ----------------------


def test_chargement_nominal_pose_les_etats_du_paragraphe_2():
    call_command("charger_jeu_recette")

    identifiants = {donnees.identifiant for donnees in COMPTES}
    assert get_user_model().objects.filter(username__in=identifiants).count() == 5
    assert Formation.objects.get(intitule="Formation archivée").archive is True
    f4 = Formation.objects.get(intitule="Formation sans référentiel")
    assert f4.elements_referentiel.count() == 0
    assert Instructeur.objects.get(nom="I4").archive is True
    assert Lieu.objects.get(intitule__startswith="L6").archive is True
    assert Lieu.objects.get(intitule__startswith="L4").mode_partage == ModePartage.SIMULTANE
    assert Lieu.objects.get(intitule__startswith="L5").mode_partage == ModePartage.SEQUENTIEL
    assert not Lieu.objects.filter(intitule__startswith=f"{CODE_LIEU_IMPOSSIBLE} —").exists()
    f2 = Formation.objects.get(intitule="Chef de poste")
    element_m5 = f2.elements_referentiel.get(matiere__code="M5")
    assert element_m5.prerequis_directs.filter(element_prerequis__matiere__code="M4").exists()


def test_idempotence_sans_reinitialiser():
    call_command("charger_jeu_recette")
    total_formations = Formation.objects.count()
    total_comptes = get_user_model().objects.count()

    call_command("charger_jeu_recette")

    assert Formation.objects.count() == total_formations
    assert get_user_model().objects.count() == total_comptes


def test_reinitialiser_recharge_a_l_identique_sans_recreer_les_comptes():
    call_command("charger_jeu_recette")
    pk_admin_avant = get_user_model().objects.get(username=IDENTIFIANT_ADMINISTRATEUR).pk
    formations_avant = set(Formation.objects.values_list("intitule", flat=True))

    call_command("charger_jeu_recette", reinitialiser=True)

    pk_admin_apres = get_user_model().objects.get(username=IDENTIFIANT_ADMINISTRATEUR).pk
    assert pk_admin_apres == pk_admin_avant
    assert set(Formation.objects.values_list("intitule", flat=True)) == formations_avant


def test_pagination_cree_vingt_cinq_sessions_sur_une_formation_dediee():
    call_command("charger_jeu_recette", pagination=True)

    formation = Formation.objects.get(intitule=LIBELLE_FORMATION_PAGINATION)
    assert Session.objects.filter(formation=formation).count() == NOMBRE_SESSIONS_PAGINATION
    assert not Session.objects.exclude(formation=formation).exists()


def test_refuse_hors_developpement(monkeypatch):
    monkeypatch.setenv("DJANGO_SETTINGS_MODULE", "cit.reglages.production")

    with pytest.raises(CommandError, match="production"):
        call_command("charger_jeu_recette")

    assert not get_user_model().objects.filter(username=IDENTIFIANT_ADMINISTRATEUR).exists()


def test_transaction_atomique_si_le_chargement_echoue_en_cours_de_route(monkeypatch):
    def _echoue(*args, **kwargs):
        raise RuntimeError("échec simulé pour tester l'atomicité")

    monkeypatch.setattr(
        "planification.management.commands.charger_jeu_recette.charger_lieux", _echoue
    )

    with pytest.raises(RuntimeError):
        call_command("charger_jeu_recette")

    assert not get_user_model().objects.filter(username=IDENTIFIANT_ADMINISTRATEUR).exists()
    assert Formation.objects.count() == 0


# --- --verifier --------------------------------------------------------


def test_verifier_detecte_un_objet_manquant_et_un_objet_mal_etat():
    call_command("charger_jeu_recette")
    Instructeur.objects.filter(nom="I3").delete()
    Formation.objects.filter(intitule="Formation archivée").update(archive=False)

    tampon = io.StringIO()
    call_command("charger_jeu_recette", verifier=True, stdout=tampon)
    sortie = tampon.getvalue()

    assert "[MANQUANT] Instructeur I3 présent" in sortie
    assert "[MANQUANT] Formation F3 archivée=True" in sortie


# --- Fichiers d'import : § 3 ------------------------------------------
#
# Chaque test génère dans `tmp_path`, jamais dans le dépôt : les fichiers suivis
# de docs/recette/fichiers-import/ sont la recette figée (voir P-40).


@pytest.fixture
def dossier_fichiers(tmp_path):
    dossier = tmp_path / "fichiers-import"
    constructeur.generer(dossier, io.StringIO())
    return dossier


def test_generer_produit_les_treize_fichiers_et_le_lisez_moi(dossier_fichiers):
    for nom in constructeur.NOMS_FICHIERS:
        assert (dossier_fichiers / nom).exists()
    assert len(constructeur.NOMS_FICHIERS) == 13
    assert (dossier_fichiers / "00-LISEZ-MOI.md").exists()


@pytest.mark.parametrize(
    "nom, nb_lignes",
    [
        ("01-valide-10.csv", 10),
        ("02-valide-5.xlsx", 5),
        ("03-valide-45-colonnes-permutees.csv", 45),
        ("04-encodage-utf8-bom.csv", 5),
        ("05-encodage-cp1252.csv", 5),
        ("06-valide-colonnes-permutees.csv", 5),
        ("07-valide-entetes-majuscules.csv", 5),
    ],
)
def test_fichiers_valides_acceptes_sans_anomalie_par_le_vrai_parseur(
    nom, nb_lignes, formation_f1, dossier_fichiers
):
    contenu = (dossier_fichiers / nom).read_bytes()
    session = _session(formation_f1)

    rapport = analyser(session, contenu, nom)

    assert len(rapport.lignes_valides) == nb_lignes
    assert not rapport.anomalies


def test_fichiers_04_et_05_decodent_les_memes_identites(formation_f1, dossier_fichiers):
    session = _session(formation_f1)
    contenu_04 = (dossier_fichiers / "04-encodage-utf8-bom.csv").read_bytes()
    contenu_05 = (dossier_fichiers / "05-encodage-cp1252.csv").read_bytes()

    noms_04 = [
        ligne.donnees["nom"] for ligne in analyser(session, contenu_04, "04.csv").lignes_valides
    ]
    noms_05 = [
        ligne.donnees["nom"] for ligne in analyser(session, contenu_05, "05.csv").lignes_valides
    ]

    assert noms_04 == noms_05
    assert all(nom.startswith("Éçàôù") for nom in noms_04)


def test_fichier_08_colonne_matricule_absente_refusee(formation_f1, dossier_fichiers):
    session = _session(formation_f1)
    contenu = (dossier_fichiers / "08-colonne-matricule-absente.csv").read_bytes()

    with pytest.raises(ErreurValidation):
        analyser(session, contenu, "08.csv")


def test_fichier_09_matricule_manquant_signale_a_la_ligne_12(formation_f1, dossier_fichiers):
    """R2-SES05-16 (cahier de recette sprint 2, § 5.5) : « la ligne 12 »."""
    session = _session(formation_f1)
    contenu = (dossier_fichiers / "09-matricule-manquant-ligne-12.csv").read_bytes()

    rapport = analyser(session, contenu, "09.csv")

    anomalie = next(a for a in rapport.anomalies if a.numero_ligne == 12)
    assert "matricule" in anomalie.motif.lower()
    assert len(rapport.lignes_valides) == 13


def test_fichier_10_doublon_dans_le_fichier_exclu_et_signale(formation_f1, dossier_fichiers):
    session = _session(formation_f1)
    contenu = (dossier_fichiers / "10-doublon-dans-le-fichier.csv").read_bytes()

    rapport = analyser(session, contenu, "10.csv")

    assert len(rapport.lignes_valides) == 5
    assert len(rapport.anomalies) == 1


def test_fichier_11_doublon_en_base_seulement_apres_import_du_fichier_01(
    formation_f1, redacteur_recette, dossier_fichiers
):
    session = _session(formation_f1)
    contenu_01 = (dossier_fichiers / "01-valide-10.csv").read_bytes()
    confirmer(redacteur_recette, session, contenu_01, "01.csv")
    contenu_11 = (dossier_fichiers / "11-doublon-en-base.csv").read_bytes()

    rapport = analyser(session, contenu_11, "11.csv")

    matricules_doublons = {d.matricule for d in rapport.doublons_en_base}
    assert matricules_doublons == {"REC-001", "REC-002"}
    assert len(rapport.lignes_valides) == 3


def test_fichier_12_une_anomalie_par_ligne(formation_f1, dossier_fichiers):
    session = _session(formation_f1)
    contenu = (dossier_fichiers / "12-un-champ-vide-par-ligne.csv").read_bytes()

    rapport = analyser(session, contenu, "12.csv")

    assert not rapport.lignes_valides
    assert len(rapport.anomalies) == 5


def test_fichier_13_faux_fichier_refuse(formation_f1, dossier_fichiers):
    session = _session(formation_f1)
    contenu = (dossier_fichiers / "13-faux-fichier.csv").read_bytes()

    with pytest.raises(ErreurValidation):
        analyser(session, contenu, "13-faux-fichier.csv")


def _cellules(chemin):
    classeur = openpyxl.load_workbook(chemin)
    return {
        feuille.title: [[cellule.value for cellule in ligne] for ligne in feuille.iter_rows()]
        for feuille in classeur.worksheets
    }


def _octets_sans_fin_de_ligne(chemin):
    """Fins de ligne normalisées : le dépôt stocke du LF, la copie de travail
    Windows du CRLF (core.autocrlf), et le module csv écrit du CRLF."""
    return chemin.read_bytes().replace(b"\r\n", b"\n")


def test_fichiers_suivis_correspondent_au_generateur(dossier_fichiers):
    """Si le générateur change, ce test échoue : on régénère alors explicitement
    (`charger_jeu_recette --regenerer-fichiers-import`), on ne le subit pas."""
    suivis = constructeur.DOSSIER
    for nom in (*constructeur.NOMS_FICHIERS, "00-LISEZ-MOI.md"):
        if nom.endswith(".xlsx"):
            assert _cellules(dossier_fichiers / nom) == _cellules(suivis / nom), nom
        else:
            assert _octets_sans_fin_de_ligne(dossier_fichiers / nom) == (
                _octets_sans_fin_de_ligne(suivis / nom)
            ), nom


# --- Commande : génération explicite uniquement -----------------------------


def test_commande_ne_regenere_les_fichiers_que_sur_option_explicite(monkeypatch, tmp_path):
    cible = tmp_path / "fichiers-import"
    monkeypatch.setattr("planification.management.commands.charger_jeu_recette.DOSSIER", cible)
    call_command("charger_jeu_recette", stdout=io.StringIO())
    assert not cible.exists()

    tampon_err = io.StringIO()
    call_command(
        "charger_jeu_recette",
        regenerer_fichiers_import=True,
        stdout=io.StringIO(),
        stderr=tampon_err,
    )
    assert (cible / "02-valide-5.xlsx").exists()
    assert "AVERTISSEMENT" in tampon_err.getvalue()


# --- Fixtures propres à ce module --------------------------------------


@pytest.fixture
def redacteur_recette():
    call_command("charger_jeu_recette")
    return get_user_model().objects.get(username="u_ped")


@pytest.fixture
def formation_f1(redacteur_recette):
    return Formation.objects.get(intitule="Exploitant radio")


def _session(formation):
    from datetime import timedelta

    from django.utils import timezone

    redacteur = get_user_model().objects.get(username="u_ped")
    debut = timezone.now().date()
    return ServiceSession.creer(
        redacteur,
        {
            "intitule": "Session de test — fichiers d'import",
            "formation": formation,
            "date_debut": debut,
            "date_fin": debut + timedelta(weeks=10),
            "effectif_attendu": 20,
        },
    )
