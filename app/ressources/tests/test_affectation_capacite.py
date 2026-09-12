"""US-SES-06 — RG-19, contrôle de capacité avec une salle attitrée réelle
(Prompt 25, § 12, Groupe B/D). Vit dans `app/ressources/tests`, pas
`app/organisation/tests` : ces scénarios ont besoin d'un vrai
`SalleAttitree`, qu'`organisation` ne peut pas construire (D-85) — méthode
déjà retenue à US-SES-04. Données entièrement fictives.
"""

import pytest

from noyau.exceptions import ErreurValidation
from organisation.repartition.proposition import proposer
from organisation.repartition.validation import valider
from organisation.services.affectation import ServiceAffectation
from organisation.services.brigade import ServiceBrigade
from organisation.services.stagiaire import ServiceStagiaire
from organisation.tests.conftest import donnees_stagiaire
from ressources.services.salle_attitree import ServiceSalleAttitree


def _remplir(redacteur, session, brigade, nombre):
    stagiaires = [
        ServiceStagiaire.creer(
            redacteur, session, donnees_stagiaire(matricule=f"M{i:03d}", nom=f"Nom{i:03d}")
        )
        for i in range(nombre)
    ]
    for stagiaire in stagiaires:
        ServiceAffectation.affecter(redacteur, stagiaire, brigade)
    return stagiaires


def test_b4_rg19_capacite_de_la_salle_atteinte_refus_marge_chiffree(
    redacteur, planificateur, session, brigade, lieu
):
    """`lieu` (conftest ressources) : capacité 30."""
    ServiceSalleAttitree.attribuer(planificateur, brigade, lieu)
    _remplir(redacteur, session, brigade, 30)
    dernier = ServiceStagiaire.creer(redacteur, session, donnees_stagiaire(matricule="M999"))

    with pytest.raises(ErreurValidation) as info:
        ServiceAffectation.affecter(redacteur, dernier, brigade)

    assert "30" in str(info.value)
    assert "marge restante 0" in str(info.value).lower()


def test_b5_rg19_cas_limite_effectif_reel_porte_exactement_a_la_capacite_acceptee(
    redacteur, planificateur, session, brigade, lieu
):
    ServiceSalleAttitree.attribuer(planificateur, brigade, lieu)
    _remplir(redacteur, session, brigade, 29)
    dernier = ServiceStagiaire.creer(redacteur, session, donnees_stagiaire(matricule="M999"))

    affectation = ServiceAffectation.affecter(redacteur, dernier, brigade)

    assert affectation.date_fin is None
    assert ServiceBrigade.effectif_reel(brigade) == 30


def test_b6_depassement_effectif_declare_salle_assez_grande_acceptee_avec_avertissement(
    redacteur, planificateur, session, brigade, lieu
):
    """`brigade` (conftest) : effectif prévisionnel 20 — la salle (30 places)
    reste assez grande pour un 21e stagiaire."""
    ServiceSalleAttitree.attribuer(planificateur, brigade, lieu)
    _remplir(redacteur, session, brigade, 20)
    vingt_et_unieme = ServiceStagiaire.creer(
        redacteur, session, donnees_stagiaire(matricule="M999")
    )

    affectation = ServiceAffectation.affecter(redacteur, vingt_et_unieme, brigade)

    assert affectation.date_fin is None
    codes = [a["code"] for a in affectation.avertissements]
    assert "effectif_declare_depasse" in codes


def test_d4_revalidation_capacite_salle_remplacee_par_une_plus_petite_detectee_a_la_validation(
    redacteur, planificateur, session, brigade, lieu
):
    """D4, Groupe D, Prompt 25 § 12 : la capacité réelle du lieu est réduite
    entre la proposition et la validation (correction de terrain sur le
    lieu, indépendante de l'attribution) — le dépassement doit être détecté
    à la revalidation, jamais supposé acquis depuis le temps 1. La capacité
    ne peut pas être réduite en passant par `ServiceSalleAttitree.modifier`,
    qui refuse RG-13 dès l'attribution (§ 4, Prompt 22) : mise à jour directe
    du lieu, hors du chemin d'écriture normal, pour isoler ce qui est
    revalidé."""
    ServiceSalleAttitree.attribuer(planificateur, brigade, lieu)
    for i in range(20):
        ServiceStagiaire.creer(
            redacteur, session, donnees_stagiaire(matricule=f"M{i:03d}", nom=f"Nom{i:03d}")
        )
    proposition = proposer(session)
    type(lieu).objects.filter(pk=lieu.pk).update(capacite=5)

    rapport = valider(redacteur, session, proposition)

    assert len(rapport.enregistrees) == 5
    assert len(rapport.refusees) == 15
    assert ServiceBrigade.effectif_reel(brigade) == 5
