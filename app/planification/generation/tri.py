"""L'ordre de priorité — § 4, Prompt 31. Le cœur de la story.

RÈGLE, en cinq lignes lisibles par un non-informaticien (§ 15, à reprendre
telle quelle dans le mémoire) :

    On place d'abord ce qui est le plus difficile à placer. Une matière que
    peu d'instructeurs savent enseigner, ou qui exige une salle rare, passe
    avant une matière que n'importe qui peut donner n'importe où. Une
    matière en retard sur son volume, par rapport au temps qu'il reste pour
    la rattraper, passe avant une matière confortable. Entre deux
    instructeurs également possibles, on retient celui qui a le moins de
    séances cette semaine, pour répartir la charge. Le programme ne dépend
    jamais de l'ordre dans lequel les données ont été saisies : à égalité
    stricte, l'identifiant tranche.

POIDS D'UNE MATIÈRE — tuple trié par ordre croissant (plus petit = plus
prioritaire), trois critères combinés dans l'ordre de poids du § 4 :
1. nombre d'instructeurs qualifiés ET disponibles, croissant ;
2. rareté du lieu requis (peu de lieux compatibles = plus prioritaire) ;
3. volume restant rapporté au temps restant dans la session, décroissant
   (urgence) — inversé en négatif pour trier par ordre croissant.
Département stable : `element.pk`.

CHARGE D'INSTRUCTEUR — un critère de préférence EMPRUNTÉ à RG-43 (le
classement des remplaçants, US-PLAN-09/10, non implantée), PAS son
implantation : RG-43 porte d'autres critères (antériorité, statut) qui n'ont
de sens qu'avec un historique d'affectations réel. Reste dans ce module, ne
devient jamais un service partagé qu'US-PLAN-09 hériterait à moitié fait
(directive utilisateur, Prompt 31, point 2 — voir docs/suivi/DECISIONS.md).
Portée : LA SEMAINE EN COURS DE GÉNÉRATION SEULEMENT (jamais l'historique
complet, qui pénaliserait à vie un instructeur très sollicité l'an dernier),
PLUS le cumul provisoire de cette génération (sans quoi les premières cases
iraient toutes au même instructeur, qui paraîtrait le moins chargé à chaque
essai — c'est le point qui fait ou défait l'équilibrage).
"""

from django.utils import timezone

from planification.services.regles_instructeur import _se_recouvrent
from planification.services.temps import duree_heures

SENTINELLE_AUCUN_LIEU = 10**6


def _nb_instructeurs_qualifies_disponibles(element, case, contexte, preparation):
    candidats = preparation.instructeurs_qualifies.get(element.matiere.pk, [])
    disponibles = 0
    for instructeur in candidats:
        indisponibilites = contexte.indisponibilites_instructeur.get(instructeur.pk, [])
        if any(_se_recouvrent(case.debut, case.fin, d, f) for d, f in indisponibilites):
            continue
        disponibles += 1
    return disponibles


def _rarete_lieu(element, preparation):
    from referentiel.models import CategorieLieu

    if element.categorie_lieu == CategorieLieu.AUCUN_LIEU:
        return SENTINELLE_AUCUN_LIEU
    if element.categorie_lieu == CategorieLieu.SALLE_ATTITREE:
        return 1
    lieux = preparation.lieux_partages_par_type.get(element.type_lieu_partage, [])
    return len(lieux) or SENTINELLE_AUCUN_LIEU


def _ratio_urgence(element, brigade, contexte, aujourd_hui):
    volume_restant = element.volume_horaire_prescrit - contexte.volume_programme_par_element.get(
        element.pk, 0
    )
    temps_restant_jours = max((brigade.session.date_fin - aujourd_hui).days, 1)
    return volume_restant / temps_restant_jours


def poids_matiere(element, brigade, case, contexte, preparation):
    aujourd_hui = timezone.localdate()
    return (
        _nb_instructeurs_qualifies_disponibles(element, case, contexte, preparation),
        _rarete_lieu(element, preparation),
        -_ratio_urgence(element, brigade, contexte, aujourd_hui),
        element.pk,
    )


def charge_instructeur(instructeur, contexte, provisoires):
    """Séances de LA SEMAINE (`contexte.seances_existantes`, déjà bornées
    au programme) + candidates déjà retenues dans CETTE génération."""
    total = sum(
        duree_heures(s.debut, s.fin)
        for s in contexte.seances_existantes
        if s.instructeur_id == instructeur.pk
    )
    total += sum(
        duree_heures(c.debut, c.fin) for c in provisoires if c.instructeur.pk == instructeur.pk
    )
    return total


def cle_tri_candidate(candidate, poids_matiere_candidate, contexte, provisoires):
    lieu_pk = candidate.lieu.pk if candidate.lieu is not None else 0
    return (
        poids_matiere_candidate,
        charge_instructeur(candidate.instructeur, contexte, provisoires),
        lieu_pk,
        candidate.instructeur.pk,
    )
