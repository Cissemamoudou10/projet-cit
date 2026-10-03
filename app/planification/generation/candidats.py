"""Construction des cases à pourvoir et de leurs candidates — § 4, étapes 1
à 3, Prompt 31.

Lit `Contexte` (`ServiceContraintes.contexte`) pour ÉCARTER D'EMBLÉE les
matières sans issue (volume épuisé, prérequis inachevé, salle attitrée
manquante) — LES MÊMES NOMBRES QUE RG-39/RG-37, jamais une réimplantation de
la règle : ce module ne DÉCIDE rien, il évite des essais voués à l'échec et
motive le compte rendu (critère 3, § 5). La seule autorité qui accepte ou
refuse une candidate reste `ServiceContraintes.verifier` (C6) — voir
`planification.generation.gloutonne`.

Blocage calendaire (étape 2) : réutilise `_portee_couvre`/`se_recouvrent`
de `regles_calendrier`/`regles_instructeur` TELS QUELS — même fonctions que
RG-38, jamais une copie.
"""

import datetime

from django.utils import timezone

from noyau.intervalles import se_recouvrent
from planification.services.contraintes import Candidate
from planification.services.regles_calendrier import _portee_couvre
from referentiel.models import CategorieLieu

JOURS_OFFSET = {
    "lundi": 0,
    "mardi": 1,
    "mercredi": 2,
    "jeudi": 3,
    "vendredi": 4,
    "samedi": 5,
    "dimanche": 6,
}


def projeter_creneaux(creneaux, lundi_de_semaine):
    """Étape 1 : un `(jour_semaine, debut, fin)` par créneau type de la
    grille active, daté sur la semaine du programme."""
    projections = []
    for creneau in creneaux:
        jour = lundi_de_semaine + datetime.timedelta(days=JOURS_OFFSET[creneau.jour_semaine])
        debut = timezone.make_aware(datetime.datetime.combine(jour, creneau.heure_debut))
        fin = timezone.make_aware(datetime.datetime.combine(jour, creneau.heure_fin))
        projections.append((debut, fin))
    return projections


def creneau_bloque(brigade, debut, fin, periodes_bloquantes):
    """Étape 2 : un créneau dont la portée d'une période bloquante couvre
    cette brigade n'engendre aucune case pour elle. `periodes_bloquantes` :
    même forme que `Contexte.periodes_bloquantes` — appelable AVANT qu'un
    `ProgrammeHebdomadaire` existe (E1, § 6), ou après via le contexte."""
    for entree in periodes_bloquantes:
        periode = entree["periode"]
        if se_recouvrent(debut, fin, periode.debut, periode.fin) and _portee_couvre(
            entree, brigade
        ):
            return True
    return False


def construire_cases(brigades, creneaux_projetes, periodes_bloquantes):
    """Étapes 1-2 combinées : une `Case` par (brigade, créneau projeté) NON
    bloqué. `creneaux_projetes` : sortie de `projeter_creneaux`."""
    from planification.generation.strategie import Case

    cases = []
    for brigade in brigades:
        for debut, fin in creneaux_projetes:
            if not creneau_bloque(brigade, debut, fin, periodes_bloquantes):
                cases.append(Case(brigade=brigade, debut=debut, fin=fin))
    return cases


def _volume_restant(element, contexte):
    deja_programme = contexte.volume_programme_par_element.get(element.pk, 0)
    return element.volume_horaire_prescrit - deja_programme


def _prerequis_inacheves(element, brigade, contexte):
    manquants = []
    for prerequis in contexte.prerequis_par_element.get(element.pk, []):
        cle = (prerequis.pk, brigade.pk)
        programme = contexte.volume_programme_par_element_brigade.get(cle, 0)
        if programme < prerequis.volume_horaire_prescrit:
            manquants.append(prerequis)
    return manquants


def matieres_programmables(brigade, elements, contexte):
    """Étape 3 : `(programmables, ecartees)` — `ecartees` porte le motif
    exact (critère 3), jamais un simple filtrage muet."""
    programmables = []
    ecartees = []
    for element in elements:
        volume_restant = _volume_restant(element, contexte)
        if volume_restant <= 0:
            ecartees.append(_ecartee(brigade, element, _motif_volume_epuise(element)))
            continue
        manquants = _prerequis_inacheves(element, brigade, contexte)
        if manquants:
            ecartees.append(_ecartee(brigade, element, _motif_prerequis(manquants)))
            continue
        if element.categorie_lieu == CategorieLieu.SALLE_ATTITREE and not _a_une_salle_attitree(
            brigade, contexte
        ):
            ecartees.append(_ecartee(brigade, element, _motif_sans_salle(brigade)))
            continue
        programmables.append(element)
    return programmables, ecartees


def _a_une_salle_attitree(brigade, contexte):
    return contexte.salles_attitrees.get(brigade.pk) is not None


def _motif_volume_epuise(element):
    return (
        f"Volume prescrit de {element.matiere} déjà atteint "
        f"({element.volume_horaire_prescrit} h)."
    )


def _motif_prerequis(manquants):
    noms = ", ".join(str(p.matiere) for p in manquants)
    return f"Prérequis non achevé(s) : {noms}."


def _motif_sans_salle(brigade):
    return f"{brigade} n'a aucune salle attitrée ; matière exigeant une salle attitrée."


def _ecartee(brigade, element, motif):
    from planification.generation.strategie import MatiereEcartee

    return MatiereEcartee(brigade=brigade, element=element, motif=motif)


def lieux_compatibles(element, preparation):
    """Lieux candidats pour une matière LIEU_PARTAGE — chargés une fois par
    l'appelant (`ServiceGeneration`), jamais requêtés par case."""
    if element.categorie_lieu != CategorieLieu.LIEU_PARTAGE:
        return []
    return preparation.lieux_partages_par_type.get(element.type_lieu_partage, [])


def candidates_pour_case(case, matieres, contexte, preparation):
    """Construit toutes les `Candidate` envisageables pour une case — une
    par combinaison matière programmable × instructeur qualifié × lieu
    compatible. Aucun tri ici, voir `planification.generation.tri`."""
    candidates = []
    for element in matieres:
        for instructeur in preparation.instructeurs_qualifies.get(element.matiere.pk, []):
            candidates += _candidates_pour_matiere(case, element, instructeur, contexte, preparation)
    return candidates


def _candidates_pour_matiere(case, element, instructeur, contexte, preparation):
    categorie = element.categorie_lieu
    if categorie == CategorieLieu.SALLE_ATTITREE:
        # La CANDIDATE porte la vraie salle (nécessaire à l'écriture) ;
        # `ServiceContraintes` la revérifie indépendamment sur
        # `contexte.salles_attitrees`, jamais en faisant confiance à ce
        # champ seul (§ 5, Prompt 30) — les deux ne divergent jamais ici
        # puisque c'est la même source.
        salle = contexte.salles_attitrees.get(case.brigade.pk)
        if salle is None:
            return []
        return [_candidate(case, element, instructeur, salle)]
    if categorie == CategorieLieu.LIEU_PARTAGE:
        lieux = lieux_compatibles(element, preparation)
        return [_candidate(case, element, instructeur, lieu) for lieu in lieux]
    return [_candidate(case, element, instructeur, None)]


def _candidate(case, element, instructeur, lieu):
    return Candidate(
        brigade=case.brigade,
        element_referentiel=element,
        instructeur=instructeur,
        debut=case.debut,
        fin=case.fin,
        lieu=lieu,
    )
