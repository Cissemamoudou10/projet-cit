"""Chargement des lieux de recette — Prompt 34, § 2. `L3` n'est pas chargé
— voir `donnees.CODE_LIEU_IMPOSSIBLE`/`MOTIF_LIEU_IMPOSSIBLE`."""

from evaluations.jeu_recette.donnees import LIEUX
from ressources.services.lieu import ServiceLieu


def charger_lieux(agissant, stdout):
    lieux = {}
    for donnees in LIEUX:
        lieu = ServiceLieu.creer(
            agissant,
            {
                "intitule": donnees.libelle,
                "capacite": donnees.capacite,
                "categorie": donnees.categorie,
                "type_partage": donnees.type_partage,
                "mode_partage": donnees.mode_partage,
            },
        )
        if donnees.archive:
            lieu = ServiceLieu.archiver(agissant, lieu.pk)
        lieux[donnees.code] = lieu
    nb_archives = sum(1 for donnees in LIEUX if donnees.archive)
    stdout.write(f"  {len(lieux)} lieux créés ({nb_archives} archivé) — L3 non chargé, voir § 2.")
    return lieux
