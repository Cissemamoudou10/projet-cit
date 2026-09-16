"""Construction du compte rendu — § 7, Prompt 31. Résultat d'EXÉCUTION,
jamais enregistré en base (F4) : présenté à l'écran, imprimable, reconstruit
à chaque appel de `ServiceGeneration.generer`.
"""

import dataclasses

from planification.services.temps import duree_heures


@dataclasses.dataclass(frozen=True)
class LigneVolume:
    brigade: object
    element: object
    heures_cette_semaine: float
    volume_total_brigade: float
    volume_restant_element: float


@dataclasses.dataclass(frozen=True)
class CaseNonPourvue:
    brigade: object
    debut: object
    fin: object
    motifs: list
    proposition: str = ""


@dataclasses.dataclass(frozen=True)
class Regeneration:
    """Regroupe ce que la suppression chirurgicale (§ 2) a constaté — un
    seul objet plutôt que trois paramètres (.claude/rules/python.md)."""

    verrouillees_preservees: list
    a_cheval_preservees: list
    nombre_supprimees: int


@dataclasses.dataclass(frozen=True)
class CompteRendu:
    programme: object
    seances_par_brigade: dict
    cases_non_pourvues: list
    matieres_ecartees: list
    volumes: list
    seances_verrouillees_preservees: list
    seances_regroupees_a_cheval_preservees: list
    nombre_seances_supprimees: int
    interrompu_par_la_borne: bool


def _seances_par_brigade(placements):
    compte = {}
    for placement in placements:
        for candidate in placement.candidates:
            compte[candidate.brigade] = compte.get(candidate.brigade, 0) + 1
    return compte


def _motifs_case(non_placement):
    if not non_placement.tentatives:
        return [non_placement.motif_sans_candidate]
    motifs = []
    for tentative in non_placement.tentatives:
        for violation in tentative.violations:
            motifs.append(
                f"{tentative.candidate.element_referentiel.matiere} / "
                f"{tentative.candidate.instructeur} — {violation['code']} "
                f"({violation['origine']}) : {violation['message']}"
            )
    return motifs


def _cases_non_pourvues(non_placements):
    return [
        CaseNonPourvue(
            brigade=np.case.brigade,
            debut=np.case.debut,
            fin=np.case.fin,
            motifs=_motifs_case(np),
            proposition=np.proposition,
        )
        for np in non_placements
    ]


def _heures_par_brigade_element(placements):
    heures, elements = {}, {}
    for placement in placements:
        for candidate in placement.candidates:
            cle = (candidate.brigade.pk, candidate.element_referentiel.pk)
            heures[cle] = heures.get(cle, 0) + duree_heures(candidate.debut, candidate.fin)
            elements[cle] = candidate.element_referentiel
    return heures, elements


def _volumes(placements, brigades, contexte):
    """Volume PAR MATIÈRE ET PAR BRIGADE (§ 7) — `volume_restant_element`
    reste calculé au niveau de l'ÉLÉMENT (D-140 : le plafond RG-39 est
    global, pas par brigade), affiché à côté du volume propre à la brigade
    pour ne pas laisser croire à un plafond par brigade qui n'existe pas."""
    heures_par_cle, elements_par_cle = _heures_par_brigade_element(placements)
    brigades_par_pk = {brigade.pk: brigade for brigade in brigades}
    lignes = []
    for cle, heures in heures_par_cle.items():
        brigade_pk, element = cle[0], elements_par_cle[cle]
        avant = contexte.volume_programme_par_element_brigade.get(cle, 0)
        total_element = contexte.volume_programme_par_element.get(element.pk, 0)
        lignes.append(
            LigneVolume(
                brigade=brigades_par_pk[brigade_pk],
                element=element,
                heures_cette_semaine=heures,
                volume_total_brigade=avant + heures,
                volume_restant_element=element.volume_horaire_prescrit - (total_element + heures),
            )
        )
    return lignes


def construire(programme, resultat, contexte, brigades, regeneration):
    return CompteRendu(
        programme=programme,
        seances_par_brigade=_seances_par_brigade(resultat.placements),
        cases_non_pourvues=_cases_non_pourvues(resultat.non_placements),
        matieres_ecartees=resultat.matieres_ecartees,
        volumes=_volumes(resultat.placements, brigades, contexte),
        seances_verrouillees_preservees=list(regeneration.verrouillees_preservees),
        seances_regroupees_a_cheval_preservees=list(regeneration.a_cheval_preservees),
        nombre_seances_supprimees=regeneration.nombre_supprimees,
        interrompu_par_la_borne=resultat.interrompue_par_la_borne,
    )
