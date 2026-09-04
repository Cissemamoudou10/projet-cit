"""Vue de consultation du journal — orchestre, ne décide rien. Toute la
logique métier (filtres, tri, pagination, journalisation de la
consultation) vit dans administration.services.journal.ServiceJournal.

Contrat d'adresse (A1, CU-P1-03) : `?objet_type=<type>&objet_identifiant=<id>`
présélectionne le filtre sur l'objet concerné — une fiche future (évaluation,
programme) n'a qu'à construire cette URL, rien d'autre à prévoir ici.
"""

from django.shortcuts import render

from administration.habilitations import exige_habilitation
from administration.navigation import onglets_administration
from administration.services.journal import PERMISSION_CONSULTATION_JOURNAL, ServiceJournal


@exige_habilitation(PERMISSION_CONSULTATION_JOURNAL)
def vue_journal(request):
    tri_actuel = request.GET.get("tri", "")
    natures = ServiceJournal.natures_disponibles()
    filtres = {
        "nature": request.GET.get("nature", ""),
        "auteur": request.GET.get("auteur", ""),
        "debut": request.GET.get("debut", ""),
        "fin": request.GET.get("fin", ""),
        "objet_type": request.GET.get("objet_type", ""),
        "objet_identifiant": request.GET.get("objet_identifiant", ""),
        "tri": tri_actuel,
    }
    page = ServiceJournal.consulter(request.user, filtres, request.GET.get("page"))
    onglets, onglet_actif = onglets_administration(request.user, "journal")
    contexte = {
        "page": page,
        "filtres": filtres,
        "nature_libelle": dict(natures).get(filtres["nature"], filtres["nature"]),
        "natures": natures,
        "tri_horodatage": _etat_tri(tri_actuel, "horodatage"),
        "onglets": onglets,
        "onglet_actif": onglet_actif,
    }
    return render(request, "administration/journal.html", contexte)


def _etat_tri(tri_actuel, colonne):
    """§ 3.09 : même patron que `views/comptes.py::_etat_tri` — traduction
    d'un paramètre d'URL, aucune règle métier.
    """
    if tri_actuel == colonne:
        return {"aria": "ascending", "suivant": f"-{colonne}", "sens": "asc"}
    if tri_actuel == f"-{colonne}":
        return {"aria": "descending", "suivant": colonne, "sens": "desc"}
    return {"aria": "none", "suivant": colonne, "sens": None}
