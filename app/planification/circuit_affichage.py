"""Actions du circuit proposées sur la consultation (prompt 40, § 0.3).

L'admission vient de la table du moteur (`motif_refus_action`), l'habilitation
de `a_permission`. Deux préconditions ne sont pas dans la table — une séance
pour soumettre (A9), une signature complète pour afficher (RG-46) — : l'écran
masque alors le bouton, par souci de lisibilité seulement. Le moteur les vérifie
toujours et refuse si l'action est forcée (D-229).
"""

from dataclasses import dataclass

from noyau.habilitations import a_permission
from planification.models import Avenant, Seance
from planification.selectors_circuit import motif_rejet_visible
from planification.services.circuit import (
    AFFICHER,
    ANNULER_VALIDATION,
    PERMISSION_PAR_EVENEMENT,
    REJETER,
    REPRENDRE,
    RETIRER_SOUMISSION,
    SIGNER,
    SOUMETTRE,
    VALIDER,
    motif_refus_action,
)


@dataclass(frozen=True)
class ActionCircuit:
    evenement: str
    libelle: str
    url_nom: str


LIBELLES_ACTIONS = {
    SOUMETTRE: ("Soumettre à validation", "planification:soumettre"),
    RETIRER_SOUMISSION: ("Retirer la soumission", "planification:retirer_soumission"),
    VALIDER: ("Valider le programme", "planification:valider"),
    REJETER: ("Rejeter le programme", "planification:rejeter"),
    REPRENDRE: ("Reprendre en correction", "planification:reprendre"),
    SIGNER: ("Enregistrer la signature", "planification:signer"),
    AFFICHER: ("Afficher le programme", "planification:afficher"),
    ANNULER_VALIDATION: ("Annuler la validation", "planification:annuler_validation"),
}


def _preconditions_remplies(evenement, programme):
    if evenement == SOUMETTRE:
        return Seance.objects.filter(programme=programme).exists()
    if evenement == AFFICHER:
        return programme.date_signature is not None and bool(programme.signataire)
    return True


def actions_disponibles(programme, utilisateur):
    """Actions qu'il est utile de proposer à `utilisateur` sur `programme`."""
    actions = []
    for evenement, (libelle, url_nom) in LIBELLES_ACTIONS.items():
        if not a_permission(utilisateur, PERMISSION_PAR_EVENEMENT[evenement]):
            continue
        if motif_refus_action(evenement, programme.etat) is not None:
            continue
        if not _preconditions_remplies(evenement, programme):
            continue
        actions.append(ActionCircuit(evenement, libelle, url_nom))
    return actions


def contexte_circuit(programme, utilisateur):
    """Données du bloc « circuit » de la consultation : actions et motif."""
    return {
        "actions_circuit": actions_disponibles(programme, utilisateur),
        "motif_rejet_visible": motif_rejet_visible(programme),
        "avenants": Avenant.objects.filter(seance__programme=programme)
        .select_related("seance__element_referentiel__matiere")
        .order_by("pk"),
    }
