"""US-SES-04 — taux d'occupation, couche services (Prompt 23, § 11, Groupe A).

`ServiceBrigade.taux_occupation` ne lit `salle_attitree`/`lieu` que par
attribut (relation inverse, D-52) : les stand-ins `SimpleNamespace` ci-dessous
exercent exactement ce contrat, sans qu'`organisation` importe jamais
`ressources.models` — impossible depuis D-85 (sens de dépendance).
Un vrai `SalleAttitree` attribué s'exerce depuis `app/ressources/tests`, seule
application autorisée à importer les deux côtés (US-SES-03, même méthode).
"""

from types import SimpleNamespace

from organisation.services.brigade import ServiceBrigade
from organisation.tests.conftest import donnees_brigade


def _brigade_avec_salle(effectif_previsionnel, capacite):
    lieu = SimpleNamespace(intitule="Salle de test", capacite=capacite)
    salle = SimpleNamespace(lieu=lieu)
    return SimpleNamespace(effectif_previsionnel=effectif_previsionnel, salle_attitree=salle)


def test_a1_taux_nominal_effectif_18_capacite_24_soit_75_pourcent():
    brigade = _brigade_avec_salle(effectif_previsionnel=18, capacite=24)

    occupation = ServiceBrigade.taux_occupation(brigade)

    assert occupation["taux"] == 75
    assert occupation["depasse"] is False


def test_a2_brigade_sans_salle_attitree_mention_explicite_aucun_taux_aucune_erreur(
    redacteur, session
):
    brigade = ServiceBrigade.creer(redacteur, session, donnees_brigade())

    occupation = ServiceBrigade.taux_occupation(brigade)

    assert occupation["salle"] is None
    assert occupation["taux"] is None
    assert occupation["depasse"] is False


def test_a3_salle_sans_capacite_renseignee_mention_explicite():
    brigade = _brigade_avec_salle(effectif_previsionnel=20, capacite=None)

    occupation = ServiceBrigade.taux_occupation(brigade)

    assert occupation["salle"] is not None
    assert occupation["capacite"] is None
    assert occupation["taux"] is None


def test_a4_taux_superieur_a_100_pourcent_effectif_releve_apres_attribution_signale():
    """Test central du § 4 (Prompt 23) : RG-13 refuse ce cas à l'attribution
    (US-SES-03), mais un effectif relevé APRÈS coup — `organisation` ne
    pouvant pas rappeler `ServiceSalleAttitree`, D-90 — le rend possible.
    C'est ici, à la lecture, que le dépassement se constate."""
    brigade = _brigade_avec_salle(effectif_previsionnel=25, capacite=20)

    occupation = ServiceBrigade.taux_occupation(brigade)

    assert occupation["taux"] == 125
    assert occupation["depasse"] is True
    assert occupation["capacite"] == 20
