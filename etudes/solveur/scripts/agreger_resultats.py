#!/usr/bin/env python3
"""Agrège `resultats_bruts.jsonl` en tableaux MÉDIANE / PIRE CAS (§ 8) —
Markdown sur la sortie standard, à coller dans `RESULTATS.md`. Aucune
interprétation ici : ce script ne fait que résumer les lignes brutes.

Usage : python scripts/agreger_resultats.py [resultats_bruts.jsonl]
"""

import json
import statistics
import sys

REGIMES = ["SATISFACTION", "REMPLISSAGE", "EQUILIBRAGE"]
NB_MO = 1024  # ko -> Mo


def _lire(chemin):
    with open(chemin, encoding="utf-8") as fichier:
        return [json.loads(ligne) for ligne in fichier if ligne.strip()]


def _par_combinaison(lignes):
    groupes = {}
    for ligne in lignes:
        c = ligne["combinaison"]
        groupes.setdefault((c["demande_lieux_partages"], c["densite_qualification"]), []).append(
            ligne
        )
    return dict(sorted(groupes.items()))


def _mp(valeurs, pire=max, decimales=2):
    """`méd/pire` — « — » si aucune valeur."""
    valeurs = [v for v in valeurs if v is not None]
    if not valeurs:
        return "—"
    mediane, extreme = statistics.median(valeurs), pire(valeurs)
    if decimales == 0:
        return f"{mediane:.0f}/{extreme:.0f}"
    return f"{mediane:.{decimales}f}/{extreme:.{decimales}f}"


def _pct(valeurs, pire=min):
    valeurs = [v for v in valeurs if v is not None]
    return f"{statistics.median(valeurs):.1%}/{pire(valeurs):.1%}" if valeurs else "—"


def tableau_solveur(groupes):
    print(
        "| Demande | Densité | Régime | Statuts | 1ère sol. s (méd/pire) | Temps final s (méd/pire) "
        "| Écart optim. (méd/pire) | Remplissage (méd/pire) |"
    )
    print("|---|---|---|---|---|---|---|---|")
    for (demande, densite), lot in groupes.items():
        for regime in REGIMES:
            m = [ligne[f"solveur_{regime}"] for ligne in lot]
            statuts = ",".join(sorted({x["statut"] for x in m}))
            print(
                f"| {demande:.0%} | {densite} | {regime} | {statuts} | "
                f"{_mp([x['temps_premiere_solution'] for x in m])} | "
                f"{_mp([x['temps_final'] for x in m])} | "
                f"{_mp([x['ecart_optimalite'] for x in m], decimales=0)} | "
                f"{_pct([x['taux_remplissage'] for x in m])} |"
            )


def tableau_demande(groupes):
    """Demande RÉELLE en lieux partagés (V1) : ce que l'instance demande,
    ce que chaque méthode en utilise, et le plafond arithmétique du
    remplissage dû aux seuls lieux (cases − dépassement de capacité)."""
    print(
        "| Demande | Densité | Séances à lieu demandées | Capacité (espaces × créneaux) "
        "| Plafond arithmétique de remplissage (lieux seuls) "
        "| Séances à lieu placées : solveur REMPL. (méd/pire) | heuristique (méd/pire) "
        "| Remplissage heuristique (méd/pire) |"
    )
    print("|---|---|---|---|---|---|---|---|")
    for (demande, densite), lot in groupes.items():
        meta = lot[0]["meta_instance"]
        total, avec_lieu = meta["seances_a_pourvoir"], meta["seances_a_pourvoir_avec_lieu"]
        capacite = lot[0]["capacite_lieux_partages"]
        plafond = (total - max(0, avec_lieu - capacite)) / total
        rempl = [ligne["solveur_REMPLISSAGE"]["seances_avec_lieu"] for ligne in lot]
        heur = [ligne["heuristique"] for ligne in lot]
        print(
            f"| {demande:.0%} | {densite} | {avec_lieu} | {capacite} | {plafond:.1%} | "
            f"{_mp(rempl, decimales=0)} | {_mp([h['seances_avec_lieu'] for h in heur], decimales=0)} | "
            f"{_pct([h['taux_remplissage'] for h in heur])} |"
        )


def tableau_equilibrage(groupes):
    print(
        "| Demande | Densité | Écart de charge : solveur (méd/pire) | heuristique (méd/pire) "
        "| Charge max : solveur (méd/pire) | heuristique (méd/pire) "
        "| Temps heuristique s (méd/pire) |"
    )
    print("|---|---|---|---|---|---|---|")
    for (demande, densite), lot in groupes.items():
        eq = [ligne["solveur_EQUILIBRAGE"] for ligne in lot]
        heur = [ligne["heuristique"] for ligne in lot]
        print(
            f"| {demande:.0%} | {densite} | "
            f"{_mp([x['ecart_charge'] for x in eq], decimales=0)} | "
            f"{_mp([h['ecart_charge'] for h in heur], decimales=0)} | "
            f"{_mp([x['charge_max'] for x in eq], decimales=0)} | "
            f"{_mp([h['charge_max'] for h in heur], decimales=0)} | "
            f"{_mp([h['temps_total'] for h in heur], decimales=3)} |"
        )


def tableau_memoire(groupes):
    """Une résolution par processus neuf : le pic EST celui de la résolution.
    « Supplément » = pic − ligne de base (interpréteur et bibliothèques)."""
    print("| Demande | Densité | Régime | Pic Mo (méd/pire) | Supplément vs base Mo (méd/pire) |")
    print("|---|---|---|---|---|")
    for (demande, densite), lot in groupes.items():
        for regime in REGIMES:
            m = [ligne[f"solveur_{regime}"] for ligne in lot]
            pics = [x["memoire_max_ko"] / NB_MO for x in m if x["memoire_max_ko"] is not None]
            supplements = [
                (x["memoire_max_ko"] - x["memoire_baseline_ko"]) / NB_MO
                for x in m
                if x["memoire_max_ko"] is not None and x["memoire_baseline_ko"] is not None
            ]
            print(
                f"| {demande:.0%} | {densite} | {regime} | {_mp(pics, decimales=0)} | "
                f"{_mp(supplements, decimales=0)} |"
            )


if __name__ == "__main__":
    lignes = _lire(sys.argv[1] if len(sys.argv) > 1 else "resultats_bruts.jsonl")
    groupes = _par_combinaison(lignes)
    print(f"<!-- {len(lignes)} instances, {len(groupes)} combinaisons -->\n")
    print("### Solveur — par régime\n")
    tableau_solveur(groupes)
    print("\n### Demande réelle en lieux partagés\n")
    tableau_demande(groupes)
    print("\n### Équilibrage de charge — solveur contre heuristique\n")
    tableau_equilibrage(groupes)
    print("\n### Mémoire — une résolution par processus neuf\n")
    tableau_memoire(groupes)
