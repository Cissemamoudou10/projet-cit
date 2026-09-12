"""Modèle de fichier téléchargeable pour l'import de stagiaires — produit par
le système (§ 5, Prompt 24), jamais rédigé à la main : un modèle qui diverge
du format réellement attendu par `organisation.import_stagiaires.lecteur`
serait pire que pas de modèle.

Format XLSX : « le terrain transmettra des .xlsx, c'est certain » (§ 3).
"""

import io

import openpyxl

from organisation.import_stagiaires.constantes import ENTETES_MODELE

NOM_FICHIER_MODELE = "modele_import_stagiaires.xlsx"


def generer_modele_xlsx():
    classeur = openpyxl.Workbook()
    feuille = classeur.active
    feuille.title = "Stagiaires"
    feuille.append(ENTETES_MODELE)
    tampon = io.BytesIO()
    classeur.save(tampon)
    return tampon.getvalue()
