"""Écriture d'un fichier tabulaire de stagiaires — l'export d'US-SES-07,
symétrique du lecteur (`lecteur.py`). RÉIMPORTABLE (§ 4, Prompt 26) : mêmes
en-têtes, même orthographe, même casse que `constantes.ENTETES_MODELE` — un
fichier exporté puis redéposé à l'import doit être accepté sans retouche.
Les colonnes Brigade/Statut, que le lecteur ne connaît pas, sont ajoutées
APRÈS : `lecteur._mapper_colonnes` ignore silencieusement tout en-tête non
reconnu (vérifié à l'étape 0 de cette story, aucune correction requise).

Aucune ligne de titre, aucun total, aucune cellule fusionnée (§ 4) : une
mise en page aurait cassé la réimportabilité.
"""

import csv
import io
import re
import unicodedata

import openpyxl
from django.utils import timezone

from organisation.import_stagiaires.constantes import ENTETES_MODELE

ENTETES_EXPORT = [*ENTETES_MODELE, "Brigade", "Statut"]


def ecrire_csv(stagiaires):
    """UTF-8 AVEC BOM (§ 3) : sans lui, Excel sous Windows ouvre les noms
    accentués en charabia. Point-virgule, cohérent avec les Excel
    configurés en français et lu par le parseur d'US-SES-05."""
    tampon = io.StringIO()
    ecrivain = csv.writer(tampon, delimiter=";")
    ecrivain.writerow(ENTETES_EXPORT)
    for stagiaire in stagiaires:
        ecrivain.writerow(_ligne(stagiaire))
    return tampon.getvalue().encode("utf-8-sig")


def ecrire_xlsx(stagiaires):
    classeur = openpyxl.Workbook()
    feuille = classeur.active
    feuille.title = "Stagiaires"
    feuille.append(ENTETES_EXPORT)
    for stagiaire in stagiaires:
        feuille.append(_ligne(stagiaire))
    tampon = io.BytesIO()
    classeur.save(tampon)
    return tampon.getvalue()


def _ligne(stagiaire):
    return [
        stagiaire.matricule,
        stagiaire.nom,
        stagiaire.prenom,
        stagiaire.grade,
        stagiaire.unite,
        stagiaire.brigade_designation or "Non affecté",
        "Radié" if stagiaire.radie else "Actif",
    ]


def nom_fichier_export(session, filtres, extension):
    """Le contexte se porte dans le NOM DU FICHIER, pas dans le contenu
    (§ 5, Prompt 26) : session, brigade si un filtre de brigade est actif,
    statut filtré, date d'export — déterministe, sans espace, accent ni
    caractère interdit sous Windows."""
    segments = [_translitterer(session.intitule)]
    brigade = filtres.get("brigade_libelle")
    if brigade:
        segments.append(_translitterer(brigade))
    segments.append(filtres.get("etat") or "tous")
    segments.append(timezone.localdate().isoformat())
    return "_".join(segments) + f".{extension}"


def _translitterer(texte):
    sans_accents = unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^A-Za-z0-9]+", "-", sans_accents).strip("-").lower()
