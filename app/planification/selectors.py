"""Lectures complexes séparées des services — .claude/rules/python.md.

`seances_futures_qualification` est installée comme fournisseur de
`noyau.services.parametres.ResolveurSeancesFuturesQualification` au
démarrage de l'application (`planification.apps.PlanificationConfig.ready`)
— c'est ce câblage qui referme réellement D-51 (RG-22), voir
docs/suivi/DECISIONS.md.
"""

from django.utils import timezone

from planification.models import Seance


def seances_futures_qualification(instructeur, matiere) -> list[str]:
    """Séances NON ENCORE TERMINÉES (`fin > maintenant`) de cet instructeur
    sur cette matière du catalogue — RG-22. Rendu en chaînes déjà formées :
    `ressources` n'a besoin de rien connaître de `Seance` au-delà de ce
    texte, le résolveur de `noyau` ne transporte que la donnée, jamais
    l'objet."""
    seances = (
        Seance.objects.filter(
            instructeur=instructeur,
            element_referentiel__matiere=matiere,
            fin__gt=timezone.now(),
        )
        .select_related("element_referentiel__matiere")
        .order_by("debut")
    )
    return [str(seance) for seance in seances]
