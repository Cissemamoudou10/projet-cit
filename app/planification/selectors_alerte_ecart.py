"""Être alerté des écarts significatifs — US-SUI-02, BF-SUI-02, `CU-P6-12`,
`RG-61`, prompt 48.

D-282 (Temps 0) ferme D-279 : la mise en évidence du rapprochement
d'US-SUI-01 (`decorer_rapprochement`) vit ici, pas dans
`selectors_ecart_volume.py` (US-PLAN-07, qui ne porte plus que le
programmé). Une seule fonction de statut, partagée avec PLAN-07 :
`planification.statut_volume.statut_volume` — un test d'architecture
interdit un second calcul.

A2 : en cours de session, la référence du RETARD est le PROGRAMMÉ ÉCHU
(`volumes_programme_echu_par_element_brigade`, nouveau), pas le prescrit —
sinon toute matière non encore enseignée paraîtrait en retard. À la fin de
session (même borne que D-278), cette référence devient le prescrit. Le
réalisé lui-même n'est JAMAIS recalculé ici : `ligne.realise`, déjà porté
par `LigneRapprochement` (US-SUI-01), est réutilisé tel quel.

D-311 (RECETTE-03, R03-SUI02-06) : le DÉPASSEMENT, lui, se vérifie toujours
contre le PRESCRIT, quel que soit l'état de la session — voir `_decorer_
ligne`. Avant cette correction, le dépassement n'était jamais atteignable
avant la fin de session (la référence alors en vigueur, l'échu, ne peut
jamais être dépassée par construction) ; une réduction rétroactive du
prescrit (R04-PLAN07-03) pendant qu'une session tourne encore passait donc
inaperçue, contrairement à ce que D-283 demande.
"""

import dataclasses

from django.conf import settings
from django.utils import timezone

from planification.selectors_rapprochement import rapprochement
from planification.services.contraintes import volumes_programme_echu_par_element_brigade
from planification.statut_volume import CONFORME, DEPASSEMENT, RETARD, statut_volume


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


def _decorer_ligne(ligne, reference_retard, seuil):
    """D-311 (RECETTE-03, R03-SUI02-06) précise A2/D-283 : le réalisé ne
    peut jamais dépasser le programmé échu par construction (les séances
    réalisées en sont un sous-ensemble) — mais rien n'empêche qu'une
    réduction rétroactive du prescrit (R04-PLAN07-03) laisse le réalisé
    au-dessus de LUI pendant que la session tourne encore, ce que D-283
    demande de signaler sans attendre la fin de session. Le dépassement
    contre le prescrit est donc vérifié EN PREMIER, indépendamment de
    l'état de la session ; seul le « sinon » retombe sur la référence de
    retard choisie par l'appelant (programmé échu en cours de session,
    prescrit une fois celle-ci terminée, D-282) — un dépassement que ce
    second appel produirait (réalisé en avance sur l'échu, jamais sur le
    prescrit) n'est qu'une avance de rythme, jamais une sur-programmation :
    ramené à `conforme`."""
    if ligne.realise > ligne.prescrit:
        statut, ecart_pourcent = statut_volume(ligne.prescrit, ligne.realise, True, seuil)
    else:
        statut, ecart_pourcent = statut_volume(reference_retard, ligne.realise, True, seuil)
        if statut == DEPASSEMENT:
            statut = CONFORME
    return LigneRapprochementDecoree(ligne=ligne, statut=statut, ecart_pourcent=ecart_pourcent)


def _decorer_groupe(groupe, jour, echu_par_cle, seuil):
    if groupe.sans_programme_affiche:
        return GroupeRapprochementDecore(
            brigade=groupe.brigade, lignes=[], sans_programme_affiche=True
        )
    termine = groupe.brigade.session.date_fin <= jour
    lignes = []
    for ligne in groupe.lignes:
        if termine:
            reference_retard = ligne.prescrit
        else:
            reference_retard = echu_par_cle.get(
                (ligne.element_referentiel.pk, groupe.brigade.pk), 0
            )
        lignes.append(_decorer_ligne(ligne, reference_retard, seuil))
    return GroupeRapprochementDecore(brigade=groupe.brigade, lignes=lignes)


def decorer_rapprochement(groupes, a_la_date=None) -> list:
    """A1/A2 : décore les groupes déjà calculés par
    `selectors_rapprochement.rapprochement` (US-SUI-01) — une seule requête
    de plus (le programmé échu), jamais une par brigade ni un second calcul
    du réalisé lui-même.

    `a_la_date` : un instant AWARE (« sinon maintenant », même défaut que
    `rapprochement.periode_fin`) — jamais une simple date : un `date` nu
    passé tel quel à `volumes_programme_echu_par_element_brigade`
    (`Seance.fin__lte`) forçait Django à le convertir en minuit NAÏF, un
    `RuntimeWarning` pervasif dans la suite (K7, prompt 58, RECETTE-01) —
    et un « échu » calculé à minuit plutôt qu'à l'instant réel du
    rapprochement, sous-comptant toute séance déjà terminée plus tôt le
    même jour. `jour`, un simple `date`, reste nécessaire pour la
    comparaison avec `session.date_fin`."""
    instant = a_la_date or timezone.now()
    jour = timezone.localtime(instant).date()
    seuil = seuil_alerte_pourcent()
    brigade_ids = [groupe.brigade.pk for groupe in groupes if not groupe.sans_programme_affiche]
    echu_par_cle = volumes_programme_echu_par_element_brigade(instant, brigade_ids=brigade_ids)
    return [_decorer_groupe(groupe, jour, echu_par_cle, seuil) for groupe in groupes]


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
