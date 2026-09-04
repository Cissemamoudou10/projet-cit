"""Vue de configuration de la matrice d'habilitations — orchestre, ne
décide rien. Toute la logique métier vit dans
administration.services.matrice_habilitations.
"""

from django.contrib import messages
from django.shortcuts import redirect, render

from administration.habilitations import exige_habilitation
from administration.navigation import onglets_administration
from administration.services.comptes import PERMISSION_GESTION_COMPTES
from administration.services.matrice_habilitations import (
    DOMAINES,
    SLUGS_GROUPES,
    CroisementModifie,
    ServiceMatriceHabilitations,
)


@exige_habilitation(PERMISSION_GESTION_COMPTES)
def vue_habilitations(request):
    if request.method == "POST":
        _traiter_soumission(request)
        return redirect("administration:habilitations")

    onglets, onglet_actif = onglets_administration(request.user, "habilitations")
    return render(
        request,
        "administration/habilitations.html",
        {
            "matrice": ServiceMatriceHabilitations.matrice(request.user),
            "onglets": onglets,
            "onglet_actif": onglet_actif,
        },
    )


def _traiter_soumission(request):
    etat_avant = {
        (colonne["slug"], ligne["code"]): colonne
        for ligne in ServiceMatriceHabilitations.matrice(request.user)
        for colonne in ligne["colonnes"]
    }
    changements = []
    for code, _ in DOMAINES:
        for slug, nom_groupe in SLUGS_GROUPES.items():
            etat = etat_avant[(slug, code)]
            for niveau in ("lecture", "ecriture"):
                valeur = f"{slug}-{code}-{niveau}" in request.POST
                if valeur != etat[niveau]:
                    changements.append(CroisementModifie(nom_groupe, code, niveau, valeur))

    erreurs = ServiceMatriceHabilitations.appliquer_changements(request.user, changements)

    if erreurs:
        for erreur in erreurs:
            messages.error(request, erreur)
    else:
        messages.success(request, "Habilitations mises à jour.")
