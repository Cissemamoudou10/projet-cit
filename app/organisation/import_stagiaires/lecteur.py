"""Lecture d'un fichier tabulaire de stagiaires — CSV ou XLSX (§ 5, Prompt 24).

Produit des lignes brutes numérotées comme le fichier RÉEL, en-tête compris
dans le décompte (§ 8, B8) : la première ligne de données porte le numéro 2.
Ne valide aucune règle métier — c'est le rôle d'`organisation.
import_stagiaires.analyse`, seul endroit qui décide qu'une ligne est une
anomalie.
"""

import csv
import io

import openpyxl

from noyau.exceptions import ErreurValidation
from organisation.import_stagiaires.constantes import (
    CHAMPS_OBLIGATOIRES,
    CHAMPS_PAR_ENTETE_NORMALISE,
    normaliser_texte,
)

ENCODAGES_ESSAYES = ("utf-8-sig", "cp1252")

MESSAGE_FORMAT_NON_RECONNU = (
    "Format de fichier non reconnu : déposez un fichier .csv ou .xlsx, au format "
    "du modèle téléchargeable."
)


def lire_fichier(contenu, nom_fichier):
    """Retourne `(champs_manquants, lignes)`. `lignes` est une liste de
    `(numero_ligne, {champ: valeur})` ; vide si `champs_manquants` est non
    vide — E2 est un refus global, jamais un import partiel."""
    extension = nom_fichier.rsplit(".", 1)[-1].lower() if "." in nom_fichier else ""
    if extension == "csv":
        lignes_brutes = _lire_csv(contenu)
    elif extension in ("xlsx", "xlsm"):
        lignes_brutes = _lire_xlsx(contenu)
    else:
        raise ErreurValidation(MESSAGE_FORMAT_NON_RECONNU)
    return _mapper_colonnes(lignes_brutes)


def _decoder(contenu):
    for encodage in ENCODAGES_ESSAYES:
        try:
            return contenu.decode(encodage)
        except UnicodeDecodeError:
            continue
    raise ErreurValidation(
        "Encodage du fichier non reconnu : enregistrez-le en UTF-8 ou en "
        "Windows-1252 (encodage par défaut d'Excel), et réessayez."
    )


def _lire_csv(contenu):
    texte = _decoder(contenu)
    echantillon = texte[:4096]
    try:
        dialecte = csv.Sniffer().sniff(echantillon, delimiters=";,")
    except csv.Error:
        dialecte = csv.excel
        dialecte.delimiter = ";" if echantillon.count(";") >= echantillon.count(",") else ","
    return list(csv.reader(io.StringIO(texte), dialecte))


def _lire_xlsx(contenu):
    try:
        classeur = openpyxl.load_workbook(io.BytesIO(contenu), read_only=True, data_only=True)
        feuille = classeur.worksheets[0]
        lignes = [
            [_valeur_texte(valeur) for valeur in ligne] for ligne in feuille.iter_rows(values_only=True)
        ]
        classeur.close()
    except ErreurValidation:
        raise
    except Exception as erreur:
        raise ErreurValidation(MESSAGE_FORMAT_NON_RECONNU) from erreur
    return lignes


def _valeur_texte(valeur):
    """Un matricule purement numérique saisi dans Excel est lu comme un
    nombre à virgule flottante (`12345.0`), jamais comme le texte attendu —
    reconverti ici en entier avant `str()` pour ne pas polluer la donnée."""
    if valeur is None:
        return ""
    if isinstance(valeur, float) and valeur.is_integer():
        return str(int(valeur))
    return str(valeur).strip()


def _mapper_colonnes(lignes_brutes):
    if not lignes_brutes:
        return [], []
    entete = lignes_brutes[0]
    correspondance = {}
    for indice, libelle in enumerate(entete):
        champ = CHAMPS_PAR_ENTETE_NORMALISE.get(normaliser_texte(libelle))
        if champ:
            correspondance[champ] = indice
    manquants = [champ for champ in CHAMPS_OBLIGATOIRES if champ not in correspondance]
    if manquants:
        return manquants, []
    return [], _extraire_lignes(lignes_brutes, correspondance)


def _extraire_lignes(lignes_brutes, correspondance):
    lignes = []
    for decalage, ligne_brute in enumerate(lignes_brutes[1:], start=2):
        if not any(str(valeur).strip() for valeur in ligne_brute):
            continue
        valeurs = {
            champ: (str(ligne_brute[indice]).strip() if indice < len(ligne_brute) else "")
            for champ, indice in correspondance.items()
        }
        lignes.append((decalage, valeurs))
    return lignes
