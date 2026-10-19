"""US-SES-09, C3 (prompt 47) : une session clôturée disparaît de la
sélection de brigades proposée à la génération — à l'écran ET au service
(`.claude/rules/vues.md`, trouvé en relecture : un filtre de formulaire
seul ne protège pas un appel direct). Données entièrement fictives.
"""

import pytest

from noyau.exceptions import ErreurValidation
from organisation.services.cloture import ServiceClotureSession
from planification.selectors import brigades_groupees_par_session
from planification.services.generation import ServiceGeneration


def test_brigade_d_une_session_cloturee_absente_de_la_selection_de_generation(
    redacteur, brigade_formation
):
    ServiceClotureSession.cloturer(redacteur, brigade_formation.session)

    groupes = brigades_groupees_par_session()

    pks = {brigade.pk for groupe in groupes for brigade in [e.brigade for e in groupe["etats"]]}
    assert brigade_formation.pk not in pks


def test_generation_refusee_pour_une_brigade_de_session_cloturee_meme_par_appel_direct(
    redacteur, planificateur, brigade_formation, lundi_semaine
):
    """Contourne le formulaire (identifiant de brigade connu) : le service
    doit refuser lui-même, pas seulement filtrer la liste affichée."""
    ServiceClotureSession.cloturer(redacteur, brigade_formation.session)

    with pytest.raises(ErreurValidation, match="clôturée"):
        ServiceGeneration.generer(planificateur, lundi_semaine, [brigade_formation])
