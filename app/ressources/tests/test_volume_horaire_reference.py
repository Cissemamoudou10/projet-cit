"""US-PLAN-12, Groupe E — volume horaire hebdomadaire de référence, remboursement
de D-33 (Prompt 29, § 7). `noyau.services.parametres.ResolveurVolumeHoraireReference`
est le point de résolution unique, câblé au démarrage par
`ressources.apps.RessourcesConfig.ready()` — voir docs/suivi/DECISIONS.md.
Données entièrement fictives.
"""

import datetime

import pytest
from django.conf import settings
from django.test import override_settings

from noyau.services.parametres import ResolveurVolumeHoraireReference
from organisation.services.session import ServiceSession
from organisation.tests.conftest import donnees_session
from referentiel.models import ElementReferentiel
from referentiel.services.referentiel import ServiceReferentiel
from ressources.models import GrilleHoraire, JourSemaine
from ressources.services.grille_horaire import ServiceCreneauType, ServiceGrilleHoraire


def _heure(texte):
    heure, minute = texte.split(":")
    return datetime.time(int(heure), int(minute))


JOURS_OUVRES = [
    JourSemaine.LUNDI,
    JourSemaine.MARDI,
    JourSemaine.MERCREDI,
    JourSemaine.JEUDI,
    JourSemaine.VENDREDI,
]


def _charger_grille(planificateur, intitule, creneaux):
    grille = GrilleHoraire.objects.create(intitule=intitule)
    for jour in JOURS_OUVRES:
        for ordre, (debut, fin) in enumerate(creneaux, start=1):
            ServiceCreneauType.ajouter(
                planificateur,
                grille,
                {
                    "jour_semaine": jour,
                    "ordre": ordre,
                    "heure_debut": _heure(debut),
                    "heure_fin": _heure(fin),
                },
            )
    return grille


def _activer_ordinaire(planificateur):
    grille = _charger_grille(
        planificateur,
        "Ordinaire",
        [("08:00", "09:45"), ("10:10", "12:00"), ("13:00", "14:15"), ("14:40", "16:00")],
    )
    return ServiceGrilleHoraire.activer(planificateur, grille.pk)


def _activer_ramadan(planificateur):
    grille = _charger_grille(
        planificateur,
        "Ramadan",
        [("08:30", "09:50"), ("10:00", "11:20"), ("11:30", "12:50"), ("13:10", "14:30")],
    )
    return ServiceGrilleHoraire.activer(planificateur, grille.pk)


# --- E1/E2 — volume calculé selon la grille active --------------------------


def test_e1_grille_ordinaire_active_le_volume_calcule_vaut_30_heures(planificateur):
    _activer_ordinaire(planificateur)

    volume = ServiceGrilleHoraire.volume_hebdomadaire_reference()

    assert volume == pytest.approx(30 + 50 / 60, abs=1e-6)


def test_e2_grille_ramadan_active_le_volume_calcule_differe_de_30(planificateur):
    _activer_ramadan(planificateur)

    volume = ServiceGrilleHoraire.volume_hebdomadaire_reference()

    assert volume == pytest.approx(320 * 5 / 60, abs=1e-6)
    assert volume != pytest.approx(30, abs=0.01)


# --- E3 — activer une autre grille change le volume utilisé par ecart() -----


def test_e3_activer_une_autre_grille_change_le_volume_utilise_par_ecart(planificateur, formation):
    _activer_ordinaire(planificateur)
    attendu_ordinaire = ServiceReferentiel.ecart(formation)["attendu"]

    _activer_ramadan(planificateur)
    attendu_ramadan = ServiceReferentiel.ecart(formation)["attendu"]

    assert attendu_ordinaire != attendu_ramadan
    assert attendu_ordinaire == pytest.approx(formation.duree_semaines * (30 + 50 / 60), abs=1e-6)
    assert attendu_ramadan == pytest.approx(formation.duree_semaines * (320 * 5 / 60), abs=1e-6)


# --- E4 — aucune grille active : repli sur le paramètre, sans erreur --------


def test_e4_aucune_grille_active_repli_sur_le_parametre_sans_erreur(db):
    assert (
        ResolveurVolumeHoraireReference.resoudre() == settings.VOLUME_HORAIRE_HEBDOMADAIRE_REFERENCE
    )


@override_settings(VOLUME_HORAIRE_HEBDOMADAIRE_REFERENCE=42)
def test_e4_repli_utilise_bien_le_parametre_courant(db):
    assert ResolveurVolumeHoraireReference.resoudre() == 42


# --- E5 — tous les appelants relevés au § 0.1 donnent le même chiffre -------


def test_e5_referentiel_ecart_utilise_le_meme_chiffre_que_le_resolveur(planificateur, formation):
    _activer_ordinaire(planificateur)

    resolu = ResolveurVolumeHoraireReference.resoudre()
    attendu = ServiceReferentiel.ecart(formation)["attendu"]

    assert attendu == pytest.approx(formation.duree_semaines * resolu, abs=1e-6)


def test_e5_session_e2_utilise_le_meme_chiffre_que_le_resolveur(redacteur, planificateur):
    """RG-65 : même mécanisme que `ServiceReferentiel.ecart`, un chiffre trop
    élevé pour déclencher l'avertissement et en lire le volume attendu dans
    le message — `_avertissements` n'est pas exposé autrement."""
    from referentiel.models import CategorieLieu, Formation, Matiere, TypeFormation

    _activer_ordinaire(planificateur)
    resolu = ResolveurVolumeHoraireReference.resoudre()

    type_formation = TypeFormation.objects.create(intitule="Officiers E5")
    formation = Formation.objects.create(
        intitule="Formation E5",
        specialite="Transmissions",
        duree_semaines=10,
        type_formation=type_formation,
    )
    ElementReferentiel.objects.create(
        formation=formation,
        matiere=Matiere.objects.create(intitule="Matière E5", code="E5001"),
        volume_horaire_prescrit=100000,
        categorie_lieu=CategorieLieu.SALLE_ATTITREE,
        type_lieu_partage=None,
    )

    session = ServiceSession.creer(
        redacteur,
        donnees_session(
            formation,
            date_debut=datetime.date(2026, 1, 5),
            date_fin=datetime.date(2026, 1, 12),
        ),
    )

    assert len(session.avertissements) == 1
    volume_attendu_affiche = float(
        session.avertissements[0]["message"].split("estimé sur la période (")[1].split(" h)")[0]
    )
    nombre_semaines = (session.date_fin - session.date_debut).days / 7
    assert volume_attendu_affiche == pytest.approx(nombre_semaines * resolu, abs=0.6)


# --- E9 : ResolveurVolumeHoraireReference réellement branché au démarrage --


def test_le_fournisseur_de_ressources_est_installe_au_demarrage_et_remplace_le_defaut():
    """Sans câblage réel, `ResolveurVolumeHoraireReference` répondrait
    toujours le paramètre de repli, même une fois une grille active — ce
    test échouerait silencieusement d'une façon indiscernable d'un repli
    correct sans lui. Voir directive utilisateur, § « installer_fournisseur
    »."""
    assert (
        ResolveurVolumeHoraireReference._fournisseur
        == ServiceGrilleHoraire.volume_hebdomadaire_reference
    )
