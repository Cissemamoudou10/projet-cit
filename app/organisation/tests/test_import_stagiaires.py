"""US-SES-05 — analyse et confirmation de l'import de stagiaires, Groupes B
et C (Prompt 24, § 12). Données entièrement fictives.
"""

from unittest.mock import patch

import pytest
from django.db import IntegrityError

from administration.models import EntreeJournal, TypeAction
from noyau.exceptions import ErreurValidation
from organisation.import_stagiaires.analyse import analyser
from organisation.import_stagiaires.confirmation import confirmer
from organisation.import_stagiaires.modele import generer_modele_xlsx
from organisation.models import Stagiaire
from organisation.services.stagiaire import ServiceStagiaire
from organisation.tests.conftest import donnees_stagiaire
from organisation.tests.fichiers_stagiaires import construire_csv, construire_xlsx

LIGNES_TROIS_STAGIAIRES = [
    ["M001", "Zalbrok", "Kelvar", "Lt", "1er RTR"],
    ["M002", "Bramvel", "Yasmine", "Cne", "2e RTR"],
    ["M003", "Chraibi", "Omar", "Sgt", "3e RTR"],
]


def test_b1_fichier_csv_valide_compte_rendu_exact_zero_stagiaire_en_base(session):
    contenu = construire_csv(LIGNES_TROIS_STAGIAIRES)

    rapport = analyser(session, contenu, "stagiaires.csv")

    assert len(rapport.lignes_valides) == 3
    assert not rapport.anomalies
    assert not rapport.doublons_en_base
    assert Stagiaire.objects.filter(session=session).count() == 0


def test_b2_fichier_xlsx_valide_meme_resultat(session):
    contenu = construire_xlsx(LIGNES_TROIS_STAGIAIRES)

    rapport = analyser(session, contenu, "stagiaires.xlsx")

    assert len(rapport.lignes_valides) == 3
    assert Stagiaire.objects.filter(session=session).count() == 0


def test_b3_e1_format_non_reconnu_refus_propre(session):
    """Un PDF renommé en `.xlsx` : `openpyxl` échoue à l'ouvrir (ce n'est pas
    une archive zip valide) — refus propre, jamais une trace technique."""
    contenu_pdf_renomme = b"%PDF-1.4 ceci n'est pas un tableur"

    with pytest.raises(ErreurValidation) as info:
        analyser(session, contenu_pdf_renomme, "stagiaires.xlsx")

    assert "format" in str(info.value).lower()


def test_b3_e1_extension_non_reconnue_refus_propre(session):
    contenu = construire_csv(LIGNES_TROIS_STAGIAIRES)

    with pytest.raises(ErreurValidation):
        analyser(session, contenu, "stagiaires.pdf")


def test_b4_e2_colonne_obligatoire_absente_refus_global_colonnes_nommees(session):
    contenu = construire_csv(
        [["M001", "Zalbrok", "Kelvar", "Lt"]], entetes=["Matricule", "Nom", "Prénom", "Grade"]
    )

    with pytest.raises(ErreurValidation) as info:
        analyser(session, contenu, "stagiaires.csv")

    assert "unité" in str(info.value).lower()


def test_b5_e3_toutes_les_lignes_en_anomalie_compte_rendu_aucune_confirmation_possible(session):
    contenu = construire_csv([["", "", "", "", ""]])

    rapport = analyser(session, contenu, "stagiaires.csv")

    assert not rapport.lignes_valides
    assert rapport.peut_confirmer is False


def test_b6_e4_matricule_en_doublon_dans_le_fichier_ligne_signalee_et_exclue(session):
    contenu = construire_csv(
        [
            ["M001", "Zalbrok", "Kelvar", "Lt", "1er RTR"],
            ["M001", "Bramvel", "Yasmine", "Cne", "2e RTR"],
            ["M002", "Chraibi", "Omar", "Sgt", "3e RTR"],
        ]
    )

    rapport = analyser(session, contenu, "stagiaires.csv")

    assert len(rapport.lignes_valides) == 2
    assert len(rapport.anomalies) == 1
    assert rapport.anomalies[0].numero_ligne == 3


def test_b7_a2_matricule_deja_present_en_base_signale_ignore_distinct_de_b6(redacteur, session):
    ServiceStagiaire.creer(redacteur, session, donnees_stagiaire(matricule="M001"))
    contenu = construire_csv([["M001", "Zalbrok", "Kelvar", "Lt", "1er RTR"]])

    rapport = analyser(session, contenu, "stagiaires.csv")

    assert not rapport.lignes_valides
    assert not rapport.anomalies
    assert len(rapport.doublons_en_base) == 1
    assert rapport.doublons_en_base[0].matricule == "M001"


def test_b8_numeros_de_ligne_exacts_en_tete_compris_dans_le_decompte(session):
    """En-tête = ligne 1 (§ 8) : la dixième ligne de données, en anomalie,
    est donc annoncée en ligne 11, pas en ligne 10."""
    lignes = [[f"M{i:03d}", "Zalbrok", "Kelvar", "Lt", "1er RTR"] for i in range(10)]
    lignes[9][0] = ""  # matricule manquant sur la dixième ligne de données
    contenu = construire_csv(lignes)

    rapport = analyser(session, contenu, "stagiaires.csv")

    anomalie = next(a for a in rapport.anomalies if a.numero_ligne == 11)
    assert "matricule" in anomalie.motif.lower()


def test_b9_encodage_utf8_bom_noms_accentues_lus_correctement(session):
    contenu = construire_csv(
        [["M001", "Éçàôù", "Frédéric", "Lt", "École militaire"]], encodage="utf-8-sig"
    )

    rapport = analyser(session, contenu, "stagiaires.csv")

    assert rapport.lignes_valides[0].donnees["nom"] == "Éçàôù"


def test_b9_encodage_cp1252_noms_accentues_lus_correctement(session):
    contenu = construire_csv(
        [["M001", "Éçàôù", "Frédéric", "Lt", "École militaire"]], encodage="cp1252"
    )

    rapport = analyser(session, contenu, "stagiaires.csv")

    assert rapport.lignes_valides[0].donnees["nom"] == "Éçàôù"


def test_b10_separateur_point_virgule_accepte(session):
    contenu = construire_csv(LIGNES_TROIS_STAGIAIRES, separateur=";")

    rapport = analyser(session, contenu, "stagiaires.csv")

    assert len(rapport.lignes_valides) == 3


def test_b10_separateur_virgule_accepte(session):
    contenu = construire_csv(LIGNES_TROIS_STAGIAIRES, separateur=",")

    rapport = analyser(session, contenu, "stagiaires.csv")

    assert len(rapport.lignes_valides) == 3


def test_b11_ordre_des_colonnes_permute_accepte(session):
    entetes = ["Unité", "Grade", "Prénom", "Nom", "Matricule"]
    lignes = [["1er RTR", "Lt", "Kelvar", "Zalbrok", "M001"]]
    contenu = construire_csv(lignes, entetes=entetes)

    rapport = analyser(session, contenu, "stagiaires.csv")

    assert len(rapport.lignes_valides) == 1
    assert rapport.lignes_valides[0].donnees["matricule"] == "M001"


def test_b12_fichier_au_dela_du_seuil_refuse(settings, session):
    settings.IMPORT_STAGIAIRES_LIGNES_MAX = 2
    contenu = construire_csv(LIGNES_TROIS_STAGIAIRES)

    with pytest.raises(ErreurValidation) as info:
        analyser(session, contenu, "stagiaires.csv")

    assert "maximum" in str(info.value).lower()


def test_taille_au_dela_du_seuil_refusee(settings, session):
    settings.IMPORT_STAGIAIRES_TAILLE_MAX_OCTETS = 10
    contenu = construire_csv(LIGNES_TROIS_STAGIAIRES)

    with pytest.raises(ErreurValidation) as info:
        analyser(session, contenu, "stagiaires.csv")

    assert "taille" in str(info.value).lower()


def test_e7_modele_vide_accepte_comme_fichier_valide_a_zero_ligne(session):
    contenu = generer_modele_xlsx()

    rapport = analyser(session, contenu, "modele_import_stagiaires.xlsx")

    assert rapport.lignes_valides == []
    assert rapport.anomalies == []


# --- Groupe C — confirmation et transaction -------------------------------


def test_c1_confirmation_nominale_toutes_les_lignes_enregistrees_journal_porte_le_compte(
    redacteur, session
):
    contenu = construire_csv(LIGNES_TROIS_STAGIAIRES)

    rapport = confirmer(redacteur, session, contenu, "stagiaires.csv")

    assert len(rapport.lignes_valides) == 3
    assert Stagiaire.objects.filter(session=session).count() == 3
    entree = EntreeJournal.objects.get(objet_type="import_stagiaires")
    assert entree.valeur_apres["nombre_enregistres"] == 3
    assert "Zalbrok" not in str(entree.valeur_apres)
    assert "M001" not in str(entree.valeur_apres)


def test_c2_rg18_echec_au_milieu_de_l_enregistrement_aucune_ligne_ecrite(redacteur, session):
    contenu = construire_csv(LIGNES_TROIS_STAGIAIRES)
    appels = {"n": 0}
    original_save = Stagiaire.save

    def save_qui_echoue_a_la_deuxieme(self, *args, **kwargs):
        appels["n"] += 1
        if appels["n"] == 2:
            raise IntegrityError("échec simulé au milieu du lot")
        return original_save(self, *args, **kwargs)

    with patch.object(Stagiaire, "save", save_qui_echoue_a_la_deuxieme):
        with pytest.raises(ErreurValidation):
            confirmer(redacteur, session, contenu, "stagiaires.csv")

    assert Stagiaire.objects.filter(session=session).count() == 0


def test_c3_revalidation_a_la_confirmation_ignore_le_matricule_insere_entre_temps(
    redacteur, session
):
    """RÈGLE ABSOLUE du § 4 : le compte rendu du temps 1 n'est jamais une
    source de vérité — la confirmation revalide et exclut la ligne devenue
    un doublon, sans erreur technique ni doublon créé."""
    contenu = construire_csv(LIGNES_TROIS_STAGIAIRES)
    analyser(session, contenu, "stagiaires.csv")  # temps 1, ne doit rien écrire

    ServiceStagiaire.creer(redacteur, session, donnees_stagiaire(matricule="M002"))

    rapport = confirmer(redacteur, session, contenu, "stagiaires.csv")

    assert len(rapport.lignes_valides) == 2
    assert Stagiaire.objects.filter(session=session, matricule="M002").count() == 1


def test_c4_confirmation_jamais_envoyee_ne_laisse_rien_derriere_elle(session):
    contenu = construire_csv(LIGNES_TROIS_STAGIAIRES)

    analyser(session, contenu, "stagiaires.csv")

    assert Stagiaire.objects.filter(session=session).count() == 0
