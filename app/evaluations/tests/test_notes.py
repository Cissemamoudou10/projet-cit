"""US-EVAL-05 — Saisir et vérifier les notes, CU-P6-05, RG-54, RG-55. Le
modèle et ses contraintes en base, puis le service — le déroulement HTTP et
la confidentialité sont dans test_notes_ecran.py.
"""

import datetime

import pytest
from django.db import IntegrityError, transaction

from administration.models import EntreeJournal, TypeAction
from evaluations.models import Evaluation, Note
from evaluations.services.note import ServiceNote
from evaluations.tests.conftest import affecter_stagiaires
from noyau.exceptions import ErreurValidation
from organisation.models import Formation
from organisation.services.brigade import ServiceBrigade
from organisation.services.session import ServiceSession
from referentiel.models import CategorieLieu, ElementReferentiel, Matiere

# --- Base : contraintes en base, en contournant le service ---


def test_une_note_rattachee_deux_fois_a_la_meme_evaluation_est_refusee_en_base(
    certificative, brigade, redacteur
):
    stagiaire = affecter_stagiaires(redacteur, brigade, 1, prefixe="DB1")[0]
    Note.objects.create(evaluation=certificative, stagiaire=stagiaire, valeur=12)

    with pytest.raises(IntegrityError), transaction.atomic():
        Note.objects.create(evaluation=certificative, stagiaire=stagiaire, valeur=14)


def test_valeur_et_absence_ensemble_est_refuse_en_base(certificative, brigade, redacteur):
    stagiaire = affecter_stagiaires(redacteur, brigade, 1, prefixe="DB2")[0]
    with pytest.raises(IntegrityError), transaction.atomic():
        Note.objects.create(evaluation=certificative, stagiaire=stagiaire, valeur=12, absent=True)


def test_ni_valeur_ni_absence_est_refuse_en_base(certificative, brigade, redacteur):
    stagiaire = affecter_stagiaires(redacteur, brigade, 1, prefixe="DB3")[0]
    with pytest.raises(IntegrityError), transaction.atomic():
        Note.objects.create(
            evaluation=certificative, stagiaire=stagiaire, valeur=None, absent=False
        )


def test_valeur_negative_est_refusee_en_base(certificative, brigade, redacteur):
    stagiaire = affecter_stagiaires(redacteur, brigade, 1, prefixe="DB4")[0]
    with pytest.raises(IntegrityError), transaction.atomic():
        Note.objects.create(evaluation=certificative, stagiaire=stagiaire, valeur=-1)


def test_note_maximale_nulle_est_refusee_en_base(certificative):
    with pytest.raises(IntegrityError), transaction.atomic():
        Evaluation.objects.filter(pk=certificative.pk).update(note_maximale=0)
        certificative.refresh_from_db()
        certificative.save()


# --- Service : ServiceNote.verifier/confirmer ---


def test_note_au_dessus_du_maximum_est_refusee_par_le_service(
    certificative, brigade, redacteur, examens
):
    stagiaire = affecter_stagiaires(redacteur, brigade, 1, prefixe="SV1")[0]
    donnees = {str(stagiaire.pk): {"valeur": "25", "absent": False}}

    with pytest.raises(ErreurValidation) as info:
        ServiceNote.verifier(examens, certificative, donnees)

    assert "dépasse" in str(info.value).lower()


def test_stagiaire_hors_perimetre_est_refuse_par_le_service(
    certificative, redacteur, examens, type_officiers
):
    """E1 : un stagiaire d'une AUTRE session, soumis par un POST forgé —
    jamais une confiance implicite dans l'identifiant reçu."""
    autre_formation = Formation.objects.create(
        intitule="Autre formation notes",
        specialite="Transmissions",
        duree_semaines=10,
        type_formation=type_officiers,
    )
    autre_matiere = Matiere.objects.create(intitule="Matière hors périmètre EVAL", code="HPEV1")
    ElementReferentiel.objects.create(
        formation=autre_formation,
        matiere=autre_matiere,
        volume_horaire_prescrit=10,
        categorie_lieu=CategorieLieu.AUCUN_LIEU,
    )
    aujourd_hui = datetime.date.today()
    autre_session = ServiceSession.creer(
        redacteur,
        {
            "formation": autre_formation,
            "intitule": "Autre session notes",
            "date_debut": aujourd_hui - datetime.timedelta(days=10),
            "date_fin": aujourd_hui + datetime.timedelta(days=180),
            "effectif_attendu": 10,
        },
    )
    autre_brigade = ServiceBrigade.creer(
        redacteur, autre_session, {"designation": "HORS1", "effectif_previsionnel": 10}
    )
    intrus = affecter_stagiaires(redacteur, autre_brigade, 1, prefixe="HP1")[0]
    donnees = {str(intrus.pk): {"valeur": "12", "absent": False}}

    with pytest.raises(ErreurValidation) as info:
        ServiceNote.verifier(examens, certificative, donnees)

    assert "périmètre" in str(info.value).lower()


def test_stagiaire_radie_est_refuse_par_le_service(certificative, brigade, redacteur, examens):
    stagiaire = affecter_stagiaires(redacteur, brigade, 1, prefixe="RAD1")[0]
    stagiaire.radie = True
    stagiaire.motif_radiation = "Essai"
    stagiaire.date_radiation = datetime.date.today()
    stagiaire.save()
    donnees = {str(stagiaire.pk): {"valeur": "12", "absent": False}}

    with pytest.raises(ErreurValidation) as info:
        ServiceNote.verifier(examens, certificative, donnees)

    assert "périmètre" in str(info.value).lower()


def test_saisie_partielle_est_admise(certificative, brigade, redacteur, examens):
    """A3 : les notes confirmées restent, les manquantes sont listées —
    jamais un tout-ou-rien."""
    un, deux = affecter_stagiaires(redacteur, brigade, 2, prefixe="PART")
    donnees = {str(un.pk): {"valeur": "15", "absent": False}}

    rapport = ServiceNote.confirmer(examens, certificative, donnees)

    assert len(rapport.saisies) == 1
    assert Note.objects.filter(evaluation=certificative, stagiaire=un, valeur=15).exists()
    assert not Note.objects.filter(evaluation=certificative, stagiaire=deux).exists()


def test_modification_est_journalisee_avec_ancienne_et_nouvelle_valeur(
    certificative, brigade, redacteur, examens
):
    stagiaire = affecter_stagiaires(redacteur, brigade, 1, prefixe="MOD1")[0]
    donnees_initiales = {str(stagiaire.pk): {"valeur": "10", "absent": False}}
    ServiceNote.confirmer(examens, certificative, donnees_initiales)

    donnees_modifiees = {str(stagiaire.pk): {"valeur": "14", "absent": False}}
    ServiceNote.confirmer(examens, certificative, donnees_modifiees)

    entree = EntreeJournal.objects.filter(type_action=TypeAction.MODIFICATION_NOTE).latest(
        "cree_le"
    )
    assert entree.valeur_avant == {"valeur": "10.00"}
    assert entree.valeur_apres == {"valeur": "14.00"}


def test_reconfirmer_la_meme_valeur_ne_journalise_rien_de_plus(
    certificative, brigade, redacteur, examens
):
    """N4 : « toute modification » — une reconfirmation sans changement
    n'en est pas une, elle ne doit rien écrire de plus (note.py,
    `_enregistrer_une_note`)."""
    stagiaire = affecter_stagiaires(redacteur, brigade, 1, prefixe="INCH1")[0]
    donnees = {str(stagiaire.pk): {"valeur": "12", "absent": False}}
    ServiceNote.confirmer(examens, certificative, donnees)
    avant = EntreeJournal.objects.filter(
        type_action__in=[TypeAction.SAISIE_NOTE, TypeAction.MODIFICATION_NOTE]
    ).count()

    ServiceNote.confirmer(examens, certificative, donnees)

    apres = EntreeJournal.objects.filter(
        type_action__in=[TypeAction.SAISIE_NOTE, TypeAction.MODIFICATION_NOTE]
    ).count()
    assert apres == avant


def test_creation_est_journalisee(certificative, brigade, redacteur, examens):
    stagiaire = affecter_stagiaires(redacteur, brigade, 1, prefixe="CRE1")[0]
    donnees = {str(stagiaire.pk): {"valeur": "11", "absent": False}}

    ServiceNote.confirmer(examens, certificative, donnees)

    assert EntreeJournal.objects.filter(
        type_action=TypeAction.SAISIE_NOTE, objet_type="note"
    ).exists()


def test_absence_est_enregistree_sans_valeur(certificative, brigade, redacteur, examens):
    stagiaire = affecter_stagiaires(redacteur, brigade, 1, prefixe="ABS1")[0]
    donnees = {str(stagiaire.pk): {"valeur": "", "absent": True}}

    ServiceNote.confirmer(examens, certificative, donnees)

    note = Note.objects.get(evaluation=certificative, stagiaire=stagiaire)
    assert note.absent is True
    assert note.valeur is None


def test_une_valeur_non_numerique_est_refusee_par_le_service(
    certificative, brigade, redacteur, examens
):
    stagiaire = affecter_stagiaires(redacteur, brigade, 1, prefixe="NUM1")[0]
    donnees = {str(stagiaire.pk): {"valeur": "abc", "absent": False}}

    with pytest.raises(ErreurValidation):
        ServiceNote.verifier(examens, certificative, donnees)


def test_note_negative_est_refusee_par_le_service(certificative, brigade, redacteur, examens):
    stagiaire = affecter_stagiaires(redacteur, brigade, 1, prefixe="NEG1")[0]
    donnees = {str(stagiaire.pk): {"valeur": "-3", "absent": False}}

    with pytest.raises(ErreurValidation):
        ServiceNote.verifier(examens, certificative, donnees)


def test_perimetre_brigade_resout_les_stagiaires_de_la_brigade(
    formative, brigade, redacteur, examens
):
    """N2, périmètre brigade (formative) — même résolution que le périmètre
    session, sur la brigade directement rattachée."""
    stagiaire = affecter_stagiaires(redacteur, brigade, 1, prefixe="BRI1")[0]
    donnees = {str(stagiaire.pk): {"valeur": "9", "absent": False}}

    rapport = ServiceNote.confirmer(examens, formative, donnees)

    assert len(rapport.saisies) == 1
    assert Note.objects.filter(evaluation=formative, stagiaire=stagiaire).exists()


def test_radiation_apres_la_saisie_garde_la_note(certificative, brigade, redacteur, examens):
    """N2 : un stagiaire radié APRÈS la saisie garde sa note — la radiation
    ne supprime jamais la ligne."""
    stagiaire = affecter_stagiaires(redacteur, brigade, 1, prefixe="RADAP")[0]
    donnees = {str(stagiaire.pk): {"valeur": "16", "absent": False}}
    ServiceNote.confirmer(examens, certificative, donnees)

    stagiaire.radie = True
    stagiaire.motif_radiation = "Essai radiation après saisie"
    stagiaire.date_radiation = datetime.date.today()
    stagiaire.save()

    assert Note.objects.filter(evaluation=certificative, stagiaire=stagiaire, valeur=16).exists()
