"""Être alerté des écarts significatifs — US-SUI-02, BF-SUI-02, `CU-P6-12`,
`RG-61`, prompt 48.

D-282 (Temps 0) ferme D-279 : la mise en évidence du rapprochement
d'US-SUI-01 (`decorer_rapprochement`) vit ici, pas dans
`selectors_ecart_volume.py` (US-PLAN-07, qui ne porte plus que le
programmé). Une seule fonction de statut, partagée avec PLAN-07 :
`planification.statut_volume.statut_volume` — un test d'architecture
interdit un second calcul.

A2 : en cours de session, la référence du retard est le PROGRAMMÉ ÉCHU
(`volumes_programme_echu_par_element_brigade`, nouveau), pas le prescrit —
sinon toute matière non encore enseignée paraîtrait en retard. À la fin de
session (même borne que D-278), la référence devient le prescrit. Le
réalisé lui-même n'est JAMAIS recalculé ici : `ligne.realise`, déjà porté
par `LigneRapprochement` (US-SUI-01), est réutilisé tel quel.
"""

import dataclasses

from django.conf import settings
from django.utils import timezone

from planification.selectors_rapprochement import rapprochement
from planification.services.contraintes import volumes_programme_echu_par_element_brigade
from planification.statut_volume import DEPASSEMENT, RETARD, statut_volume


@dataclasses.dataclass(frozen=True)
class LigneRapprochementDecoree:
    """Décore une `LigneRapprochement` (US-SUI-01) de son statut d'alerte,
    sans toucher à ses champs d'origine."""

    ligne: object
    statut: str
    ecart_pourcent: float


@dataclasses.dataclass(frozen=True)
class GroupeRapprochementDecore:
    brigade: object
    lignes: list
    sans_programme_affiche: bool = False


def seuil_alerte_pourcent() -> float:
    return float(settings.SEUIL_ALERTE_ECART_REALISE)


def _decorer_ligne(ligne, reference, seuil):
    """A2 : `reference_echue` vaut toujours `True` — la référence choisie
    par l'appelant (programmé échu, ou prescrit après la fin de session)
    est par construction déjà entièrement constituée (D-282)."""
    statut, ecart_pourcent = statut_volume(reference, ligne.realise, True, seuil)
    return LigneRapprochementDecoree(ligne=ligne, statut=statut, ecart_pourcent=ecart_pourcent)


def decorer_rapprochement(groupes, a_la_date=None) -> list:
    """A1/A2 : décore les groupes déjà calculés par
    `selectors_rapprochement.rapprochement` (US-SUI-01) — une seule requête
    de plus (le programmé échu), jamais une par brigade ni un second calcul
    du réalisé lui-même."""
    a_la_date = a_la_date or timezone.localdate()
    seuil = seuil_alerte_pourcent()
    brigade_ids = [groupe.brigade.pk for groupe in groupes if not groupe.sans_programme_affiche]
    echu_par_cle = volumes_programme_echu_par_element_brigade(a_la_date, brigade_ids=brigade_ids)

    decores = []
    for groupe in groupes:
        if groupe.sans_programme_affiche:
            decores.append(
                GroupeRapprochementDecore(
                    brigade=groupe.brigade, lignes=[], sans_programme_affiche=True
                )
            )
            continue
        termine = groupe.brigade.session.date_fin <= a_la_date
        lignes = []
        for ligne in groupe.lignes:
            if termine:
                reference = ligne.prescrit
            else:
                reference = echu_par_cle.get((ligne.element_referentiel.pk, groupe.brigade.pk), 0)
            lignes.append(_decorer_ligne(ligne, reference, seuil))
        decores.append(GroupeRapprochementDecore(brigade=groupe.brigade, lignes=lignes))
    return decores


def alertes(formation_id=None, session_id=None, brigade_id=None, a_la_date=None) -> list:
    """A1/A3 : liste d'alertes — calculée, jamais stockée (A1), filtrable
    par session et par brigade (A3), en réutilisant la résolution de
    brigades du rapprochement (US-SUI-01), jamais une seconde recopie du
    filtre. Chaque groupe garde sa brigade, pour le lien vers le détail du
    rapprochement (A3)."""
    groupes = rapprochement(formation_id=formation_id, session_id=session_id, brigade_id=brigade_id)
    decores = decorer_rapprochement(groupes, a_la_date=a_la_date)
    resultat = []
    for groupe in decores:
        lignes_en_alerte = [
            ligne for ligne in groupe.lignes if ligne.statut in (RETARD, DEPASSEMENT)
        ]
        if lignes_en_alerte:
            resultat.append(
                GroupeRapprochementDecore(brigade=groupe.brigade, lignes=lignes_en_alerte)
            )
    return resultat


def compte_alertes() -> int:
    """A3 : nombre d'alertes pour la navigation, comme le compteur des
    programmes en attente (`planification.selectors_circuit.
    compte_en_attente`) — même borne de requêtes que `alertes()`, jamais
    recalculé en boucle."""
    return sum(len(groupe.lignes) for groupe in alertes())
