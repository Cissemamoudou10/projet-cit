"""Chargement des lieux et indisponibilités — Prompt 15, § 3.10."""

import datetime

from django.utils import timezone

from ressources.jeu_demonstration.donnees import LIEU_INDISPONIBILITES, LIEU_RECOUVREMENT, LIEUX
from ressources.services.indisponibilite_lieu import ServiceIndisponibiliteLieu
from ressources.services.lieu import ServiceLieu


def charger_lieux(agissant, stdout):
    lieux = {}
    for donnees in LIEUX:
        lieu = ServiceLieu.creer(
            agissant,
            {
                "intitule": donnees.intitule,
                "capacite": donnees.capacite,
                "categorie": donnees.categorie,
                "type_partage": donnees.type_partage,
            },
        )
        if donnees.archive:
            lieu = ServiceLieu.archiver(agissant, lieu.pk)
        lieux[donnees.intitule] = lieu
    stdout.write(f"  {len(lieux)} lieux créés (1 archivé).")
    return lieux


def charger_indisponibilites(agissant, lieux, stdout):
    """Trois périodes sur le même lieu — passée, future, contiguë à la
    future —, plus une période sur un second lieu qui recouvre la fenêtre
    future du premier (§ 3.10) : la contrainte porte sur le couple lieu et
    période, jamais sur la période seule. Dates relatives à l'exécution
    (§ 4 du prompt), jamais en dur.
    """
    fenetres = _fenetres(timezone.now())
    lieu = lieux[LIEU_INDISPONIBILITES]
    ServiceIndisponibiliteLieu.declarer(agissant, lieu, *fenetres["passee"], "Travaux de peinture")
    ServiceIndisponibiliteLieu.declarer(
        agissant, lieu, *fenetres["future"], "Maintenance électrique programmée"
    )
    ServiceIndisponibiliteLieu.declarer(
        agissant, lieu, *fenetres["contigue"], "Inventaire annuel du matériel"
    )
    second_lieu = lieux[LIEU_RECOUVREMENT]
    ServiceIndisponibiliteLieu.declarer(
        agissant, second_lieu, *fenetres["recouvrement"], "Désinfection annuelle des locaux"
    )
    stdout.write("  4 indisponibilités déclarées (passée, future, contiguë, recouvrement croisé).")


def _fenetres(maintenant):
    semaine = datetime.timedelta(weeks=1)
    future_debut, future_fin = maintenant + 2 * semaine, maintenant + 3 * semaine
    return {
        "passee": (maintenant - 3 * semaine, maintenant - 2 * semaine),
        "future": (future_debut, future_fin),
        "contigue": (future_fin, future_fin + semaine),
        "recouvrement": (
            future_debut + datetime.timedelta(days=3),
            future_fin + datetime.timedelta(days=3),
        ),
    }
