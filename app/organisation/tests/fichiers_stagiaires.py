"""Constructeurs de fichiers de test pour l'import de stagiaires — pas des
fixtures : chaque test a besoin d'un contenu différent (Prompt 24, Groupe B).
Données entièrement fictives.
"""

import csv
import io

import openpyxl

from organisation.import_stagiaires.constantes import ENTETES_MODELE


def construire_csv(lignes, *, entetes=None, separateur=";", encodage="utf-8"):
    entetes = entetes if entetes is not None else ENTETES_MODELE
    tampon = io.StringIO()
    ecrivain = csv.writer(tampon, delimiter=separateur)
    ecrivain.writerow(entetes)
    for ligne in lignes:
        ecrivain.writerow(ligne)
    return tampon.getvalue().encode(encodage)


def construire_xlsx(lignes, *, entetes=None):
    entetes = entetes if entetes is not None else ENTETES_MODELE
    classeur = openpyxl.Workbook()
    feuille = classeur.active
    feuille.append(entetes)
    for ligne in lignes:
        feuille.append(ligne)
    tampon = io.BytesIO()
    classeur.save(tampon)
    return tampon.getvalue()


LIGNE_TYPE = ["M001", "Zalbrok", "Kelvar", "Lt", "1er RTR"]
