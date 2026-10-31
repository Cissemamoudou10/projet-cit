"""Condensation du compte rendu de génération, pour persistance —
correction de NC R00-GEN-03 (évolution du prompt 53, Temps 3).

Construite UNE SEULE FOIS, immédiatement après la génération, à partir des
mêmes objets vivants que `compte_rendu.construire` (résultat de la
stratégie) — JAMAIS recalculée plus tard : les disponibilités
d'instructeurs et de lieux ont changé dès la consultation suivante, un
second calcul donnerait un résultat différent de ce qui s'est réellement
passé à la génération. Ce n'est pas une grandeur dérivée, c'est la trace
figée d'un acte passé (voir docs/suivi/DECISIONS.md).

C4 : les motifs restent ceux d'aujourd'hui (la règle violée — RG-34 à
RG-39, `.claude/rules/services.md` — et l'élément en cause, dans le détail
déplié) ; `LIBELLES_CODES_VIOLATION` ne fait QUE nommer la règle pour
l'en-tête du groupe condensé (C3), jamais une nouvelle catégorie de motif.
"""

LIBELLES_CODES_VIOLATION = {
    "RG-34": "Instructeur déjà affecté sur ce créneau",
    "RG-35": "Instructeur non qualifié pour la matière",
    "RG-36": "Instructeur indisponible",
    "RG-37": "Lieu indisponible ou capacité insuffisante",
    "RG-38": "Créneau bloqué par le calendrier",
    "RG-39": "Volume ou prérequis non satisfait",
}


def _cle_motif_sans_candidate(texte, brigade):
    """Les deux gabarits de `gloutonne.py::_motif_sans_candidate`
    n'interpolent que la brigade : la retirer du texte donne une clé
    stable, sans dépendre du contenu littéral des deux phrases."""
    return texte.replace(str(brigade), "{brigade}")


def _ligne_sans_candidate(non_placement, brigade):
    return {
        "motif_cle": _cle_motif_sans_candidate(non_placement.motif_sans_candidate, brigade),
        "motif_libelle": non_placement.motif_sans_candidate,
        "brigade": str(brigade),
        "matiere": None,
        "detail": non_placement.motif_sans_candidate,
    }


def _lignes_des_tentatives(non_placement, brigade):
    lignes = []
    for tentative in non_placement.tentatives:
        matiere = tentative.candidate.element_referentiel.matiere
        for violation in tentative.violations:
            lignes.append(
                {
                    "motif_cle": violation["code"],
                    "motif_libelle": LIBELLES_CODES_VIOLATION.get(violation["code"], violation["code"]),
                    "brigade": str(brigade),
                    "matiere": str(matiere),
                    "detail": (
                        f"{matiere} / {tentative.candidate.instructeur} — {violation['code']} "
                        f"({violation['origine']}) : {violation['message']}"
                    ),
                }
            )
    return lignes


def _lignes_du_non_placement(non_placement):
    """Une ligne par (motif, brigade, matière) retenue à l'étape suivante —
    AU PLUS une par violation tentée : une case à plusieurs tentatives
    rejetées compte pour chacune (C3, « on voit d'un coup d'œil pourquoi des
    cases sont vides » — pas seulement la première raison essayée)."""
    brigade = non_placement.case.brigade
    if not non_placement.tentatives:
        return [_ligne_sans_candidate(non_placement, brigade)]
    return _lignes_des_tentatives(non_placement, brigade)


def _regrouper(lignes):
    groupes = {}
    for ligne in lignes:
        cle = (ligne["motif_cle"], ligne["brigade"], ligne["matiere"])
        groupe = groupes.setdefault(
            cle,
            {
                "motif_libelle": ligne["motif_libelle"],
                "brigade": ligne["brigade"],
                "matiere": ligne["matiere"],
                "nombre": 0,
                "details": [],
            },
        )
        groupe["nombre"] += 1
        groupe["details"].append(ligne["detail"])
    return sorted(groupes.values(), key=lambda g: (-g["nombre"], g["brigade"], g["motif_libelle"]))


def _matieres_ecartees_json(matieres_ecartees):
    return [
        {"brigade": str(m.brigade), "matiere": str(m.element.matiere), "motif": m.motif}
        for m in matieres_ecartees
    ]


def condenser(resultat, brigades, auteur):
    """Condensé JSON-sûr (`CompteRenduGeneration.resume`) — voir le
    docstring du module : construit une fois, jamais recalculé."""
    lignes = [
        ligne
        for non_placement in resultat.non_placements
        for ligne in _lignes_du_non_placement(non_placement)
    ]
    return {
        "auteur": str(auteur),
        "brigades_traitees": [str(brigade) for brigade in brigades],
        "nombre_seances_placees": len(resultat.placements),
        "nombre_cases_non_placees": len(resultat.non_placements),
        "interrompu_par_la_borne": resultat.interrompue_par_la_borne,
        "groupes_non_places": _regrouper(lignes),
        "matieres_ecartees": _matieres_ecartees_json(resultat.matieres_ecartees),
    }
