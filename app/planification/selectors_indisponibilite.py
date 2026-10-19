"""Lectures du traitement d'une indisponibilité déclarée — US-PLAN-09
(prompt 42, partie 3, I2 et I4). Fichier séparé de `selectors.py` pour
rester sous 400 lignes (même raison que `selectors_circuit.py`).
"""

from django.utils import timezone

from noyau.intervalles import filtre_recouvrement
from noyau.services.parametres import ResolveurOccupationsEpreuves
from planification.models import Seance
from planification.selectors_occupation import seances_occupant_instructeurs
from ressources.models import IndisponibiliteInstructeur, Instructeur


def seances_impactees_par_indisponibilite(indisponibilite):
    """I2 : séances NON COMMENCÉES de l'instructeur indisponible dont le
    créneau recoupe la période — définition unique du recouvrement
    (`noyau/intervalles.py`), toutes brigades confondues, avec l'état de
    leur programme. Affichée à l'enregistrement de l'indisponibilité (C1)
    et consultable ensuite ; une séance déjà commencée n'y figure jamais,
    elle relève de la non-exécution (même frontière que
    `modification._refuser_si_commencee`)."""
    return list(
        Seance.objects.filter(instructeur=indisponibilite.instructeur, debut__gt=timezone.now())
        .filter(filtre_recouvrement("debut", "fin", indisponibilite.debut, indisponibilite.fin))
        .select_related("programme", "element_referentiel__matiere", "lieu")
        .prefetch_related("lignes__brigade")
        .order_by("debut")
    )


def instructeurs_remplacants(matiere, debut, fin):
    """I4 : instructeurs qualifiés pour `matiere`, libres sur `[debut, fin)`
    — ni déjà en séance, ni indisponibles, ni surveillants d'une épreuve
    sécante. Une requête par source, en nombre constant quel que soit
    l'effectif qualifié : qualification, occupation
    (`seances_occupant_instructeurs`, déjà bornée), indisponibilité
    (`IndisponibiliteInstructeur`), occupation d'épreuve
    (`ResolveurOccupationsEpreuves` — seul chemin vers `evaluations`,
    `planification` ne peut pas l'importer, même raison que D-121 E2).
    Ordre alphabétique : le classement de RG-43 dépend d'US-PLAN-08,
    déclassée."""
    qualifies_ids = list(
        Instructeur.objects.filter(archive=False, qualifications__matiere=matiere)
        .values_list("pk", flat=True)
        .distinct()
    )
    if not qualifies_ids:
        return Instructeur.objects.none()
    occupes = set(seances_occupant_instructeurs(qualifies_ids, debut, fin))
    indisponibles = set(
        IndisponibiliteInstructeur.objects.filter(instructeur_id__in=qualifies_ids)
        .filter(filtre_recouvrement("debut", "fin", debut, fin))
        .values_list("instructeur_id", flat=True)
    )
    surveillants = {
        instructeur_id
        for occupation in ResolveurOccupationsEpreuves.resoudre(debut, fin)
        for instructeur_id in occupation["instructeurs"]
    }
    exclus = occupes | indisponibles | surveillants
    return (
        Instructeur.objects.filter(pk__in=qualifies_ids)
        .exclude(pk__in=exclus)
        .order_by("nom", "prenom")
    )
