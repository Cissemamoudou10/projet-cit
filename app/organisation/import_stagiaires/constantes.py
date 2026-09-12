"""Constantes partagées entre la lecture/analyse d'un fichier de stagiaires
et la saisie individuelle (`organisation.services.stagiaire`) — RG-17, RG-18,
US-SES-05, Prompt 24. Un seul endroit pour le nom des colonnes : le modèle
téléchargeable, le lecteur de fichier et les messages d'erreur de la saisie
individuelle doivent toujours s'accorder.
"""

import unicodedata

CHAMPS_OBLIGATOIRES = ("matricule", "nom", "prenom", "grade", "unite")

LIBELLES_CHAMPS = {
    "matricule": "matricule",
    "nom": "nom",
    "prenom": "prénom",
    "grade": "grade",
    "unite": "unité",
}

# En-têtes du modèle téléchargeable, dans l'ordre — l'ordre réel importé est
# indifférent (§ 5, Prompt 24), celui-ci ne sert qu'à la présentation.
ENTETES_MODELE = ["Matricule", "Nom", "Prénom", "Grade", "Unité"]

CHAMPS_PAR_ENTETE_NORMALISE = {
    "matricule": "matricule",
    "nom": "nom",
    "prenom": "prenom",
    "grade": "grade",
    "unite": "unite",
}


def libelle_champ(champ):
    return LIBELLES_CHAMPS.get(champ, champ)


def normaliser_entete(valeur):
    """Accent et casse indifférents (§ 5) : « Prénom », « PRENOM » et
    « prénom » désignent la même colonne."""
    sans_accents = (
        unicodedata.normalize("NFKD", valeur or "").encode("ascii", "ignore").decode("ascii")
    )
    return sans_accents.strip().casefold()
