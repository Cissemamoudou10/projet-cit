"""US-SES-01 — Groupe D (Prompt 20, § 11) : fermeture de D-23 (critère 4
d'US-REF-01, « une formation disposant de sessions ouvertes ne peut être
supprimée »). Vit dans `organisation`, pas `referentiel` : le test importe
`organisation.services.session`, et `referentiel` ne peut pas dépendre de
`organisation` (tests/architecture/test_couches.py::DEPENDANCES_AUTORISEES).
"""

import pytest
from django.urls import reverse

from noyau.exceptions import ErreurValidation
from organisation.models import EtatSession
from organisation.services.session import ServiceSession
from organisation.tests.conftest import donnees_session
from referentiel.services.formation import ServiceFormation


def test_d1_formation_portant_une_session_ouverte_ne_peut_etre_supprimee(redacteur, formation):
    session = ServiceSession.creer(redacteur, donnees_session(formation))

    with pytest.raises(ErreurValidation) as info:
        ServiceFormation.supprimer(redacteur, formation.pk)

    assert session.intitule in str(info.value)


def test_d2_meme_refus_par_le_vrai_cycle_http_depuis_l_ecran_de_formation(
    client, redacteur, formation
):
    ServiceSession.creer(redacteur, donnees_session(formation))
    client.force_login(redacteur)

    client.post(reverse("referentiel:supprimer_formation", args=[formation.pk]))

    assert ServiceFormation.obtenir(formation.pk) is not None


def test_d3_formation_portant_une_session_cloturee_est_aussi_protegee(redacteur, formation):
    """Écart consigné entre le libellé du critère (« sessions ouvertes ») et
    le mécanisme réel (`PROTECT`, indifférent à l'état) — § 10, Prompt 20."""
    session = ServiceSession.creer(redacteur, donnees_session(formation))
    session.etat = EtatSession.CLOTUREE
    session.save(update_fields=["etat"])

    with pytest.raises(ErreurValidation):
        ServiceFormation.supprimer(redacteur, formation.pk)
