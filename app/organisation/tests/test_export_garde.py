"""Export des stagiaires (D-219, exception b) : la liste d'export est gardée en appel
direct, pas seulement par la vue. Données entièrement fictives.
"""

import pytest

from noyau.exceptions import ErreurHabilitation
from organisation.services.stagiaire import ServiceStagiaire


def test_liste_d_export_refusee_sans_lecture_des_organisations(administrateur, session, stagiaire):
    with pytest.raises(ErreurHabilitation):
        ServiceStagiaire.lister_pour_export(administrateur, session, {})


def test_export_refuse_sans_lecture_et_rien_n_est_journalise(administrateur, session, stagiaire):
    from administration.models import EntreeJournal, TypeAction

    avant = EntreeJournal.objects.filter(type_action=TypeAction.EXPORT_DONNEES).count()
    with pytest.raises(ErreurHabilitation):
        ServiceStagiaire.exporter(administrateur, session, {}, "tous")
    assert EntreeJournal.objects.filter(type_action=TypeAction.EXPORT_DONNEES).count() == avant
