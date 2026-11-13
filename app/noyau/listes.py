"""Filtrage et tri partagés par les écrans qui appliquent recherche/filtre/
tri à une liste DÉJÀ calculée par un service — jamais une requête, jamais un
second calcul métier (`.claude/rules/services.md`). Centralisé ici, à côté
de `noyau.pagination`, qui reçoit le même traitement pour la pagination —
relecture `relecteur-conception` d'US-IHM-03 (prompt 64) : `views_moyennes`
et `views_proces_verbal` dupliquaient ces quatre fonctions à l'identique.
"""


def correspond_recherche(texte, recherche):
    if not recherche:
        return True
    return recherche.lower() in str(texte).lower()


def correspond_filtre(valeur, filtre):
    if not filtre:
        return True
    return str(valeur) == filtre


def etat_tri(tri_actuel, colonne):
    if tri_actuel == colonne:
        return {"aria": "ascending", "suivant": f"-{colonne}", "sens": "asc"}
    if tri_actuel == f"-{colonne}":
        return {"aria": "descending", "suivant": colonne, "sens": "desc"}
    return {"aria": "none", "suivant": colonne, "sens": None}


def colonne_triee(tri_actuel, cle, libelle):
    etat = etat_tri(tri_actuel, cle)
    return {
        "libelle": libelle, "cle_tri": cle,
        "tri_suivant": etat["suivant"], "sens": etat["sens"], "aria": etat["aria"],
    }
