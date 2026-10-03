"""Génère les treize fichiers d'import de test — Prompt 34, § 3. Chaque
fichier sert un scénario précis du parseur réel (US-SES-05,
`organisation.import_stagiaires.analyse.analyser`) : mêmes en-têtes
(`ENTETES_MODELE`), même sniffing d'encodage/séparateur que la production —
un fichier généré ici doit être accepté (ou refusé) exactement comme un
fichier déposé à la main par le recetteur.

Matricules déterministes, jamais réels : préfixe `REC-`, plage numérique
propre à chaque fichier (documentée dans `00-LISEZ-MOI.md`, régénéré avec
eux) — un recetteur qui relit un rapport d'anomalie doit pouvoir remonter au
fichier et à la ligne sans ambiguïté.

`DOSSIER` est ancré sur `settings.BASE_DIR` (le dossier `app/`), jamais sur le
répertoire courant : un chemin relatif au cwd écrirait dans `app/docs/...` au
lieu de `docs/...` si la commande est lancée depuis `app/` plutôt que depuis
la racine du dépôt — piège vécu pendant le développement de ce jeu.
"""

import csv
import io
from dataclasses import dataclass

import openpyxl
from django.conf import settings

from organisation.import_stagiaires.constantes import ENTETES_MODELE

DOSSIER = settings.BASE_DIR.parent / "docs" / "recette" / "fichiers-import"

CONTENU_FICHIER_NON_TABLEUR = b"%PDF-1.4 ceci n'est pas un tableur, teste E1 (B3)"


def _csv(lignes, *, entetes=ENTETES_MODELE, separateur=";", encodage="utf-8"):
    tampon = io.StringIO()
    ecrivain = csv.writer(tampon, delimiter=separateur)
    ecrivain.writerow(entetes)
    ecrivain.writerows(lignes)
    return tampon.getvalue().encode(encodage)


def _xlsx(lignes, *, entetes=ENTETES_MODELE):
    classeur = openpyxl.Workbook()
    feuille = classeur.active
    feuille.append(entetes)
    for ligne in lignes:
        feuille.append(ligne)
    tampon = io.BytesIO()
    classeur.save(tampon)
    return tampon.getvalue()


@dataclass(frozen=True)
class GabaritIdentite:
    nom: str = "Nom"
    prenom: str = "Prenom"
    grade: str = "Sdt"
    unite: str = "Unité de recette"


GABARIT_PAR_DEFAUT = GabaritIdentite()
GABARIT_ACCENTUE = GabaritIdentite(nom="Éçàôù", prenom="Frédéric")


def _ligne(matricule, indice, gabarit=GABARIT_PAR_DEFAUT):
    return [
        matricule,
        f"{gabarit.nom}{indice:03d}",
        f"{gabarit.prenom}{indice:03d}",
        gabarit.grade,
        gabarit.unite,
    ]


def _plage(prefixe, debut, fin, gabarit=GABARIT_PAR_DEFAUT):
    return [_ligne(f"{prefixe}-{i:03d}", i, gabarit) for i in range(debut, fin + 1)]


def _01_valide_10():
    return _csv(_plage("REC", 1, 10))


def _02_valide_5_xlsx():
    return _xlsx(_plage("REC", 11, 15))


def _03_valide_45_colonnes_permutees():
    entetes = ["Unité", "Grade", "Prénom", "Nom", "Matricule"]
    lignes = [
        [ligne[4], ligne[3], ligne[2], ligne[1], ligne[0]] for ligne in _plage("REC", 101, 145)
    ]
    return _csv(lignes, entetes=entetes, separateur=",")


def _06_valide_colonnes_permutees_petit_lot():
    entetes = ["Prénom", "Unité", "Matricule", "Nom", "Grade"]
    lignes = [
        [ligne[2], ligne[4], ligne[0], ligne[1], ligne[3]] for ligne in _plage("REC", 501, 505)
    ]
    return _csv(lignes, entetes=entetes)


def _07_valide_entetes_majuscules():
    entetes = ["MATRICULE", "NOM", "PRENOM", "GRADE", "UNITE"]
    return _csv(_plage("REC", 601, 605), entetes=entetes)


def _lignes_accentuees(debut, fin):
    return _plage("REC", debut, fin, GABARIT_ACCENTUE)


def _04_encodage_utf8_bom():
    return _csv(_lignes_accentuees(401, 405), encodage="utf-8-sig")


def _05_encodage_cp1252():
    return _csv(_lignes_accentuees(401, 405), encodage="cp1252")


def _08_colonne_matricule_absente():
    lignes = [ligne[1:] for ligne in _plage("REC", 951, 955)]
    return _csv(lignes, entetes=["Nom", "Prénom", "Grade", "Unité"])


def _09_matricule_manquant_ligne_12():
    """R2-SES05-16 : « la ligne 12 » compte l'en-tête comme ligne 1
    (§ 8, `organisation.import_stagiaires`) — donc la 11e ligne de données,
    indice 10 dans `lignes` (0-based)."""
    lignes = _plage("REC", 701, 714)
    lignes[10][0] = ""
    return _csv(lignes)


def _10_doublon_dans_le_fichier():
    lignes = _plage("REC", 201, 205)
    lignes.insert(1, _ligne("REC-201", 201))
    return _csv(lignes)


def _11_doublon_en_base():
    """Ne signale un doublon QUE si `01-valide-10.csv` a déjà été importé
    dans la MÊME session (RG-18 : la détection est bornée à la session) —
    documenté dans `00-LISEZ-MOI.md` comme recette en deux temps."""
    lignes = [_ligne("REC-001", 1), _ligne("REC-002", 2), *_plage("REC", 801, 803)]
    return _csv(lignes)


def _12_un_champ_obligatoire_vide_par_ligne():
    lignes = _plage("REC", 901, 905)
    for indice_colonne, ligne in enumerate(lignes):
        ligne[indice_colonne] = ""
    return _csv(lignes)


def _13_faux_fichier():
    return CONTENU_FICHIER_NON_TABLEUR


FICHIERS = (
    ("01-valide-10.csv", _01_valide_10, "10 lignes valides (REC-001..010), séparateur « ; »."),
    ("02-valide-5.xlsx", _02_valide_5_xlsx, "5 lignes valides (REC-011..015), au format XLSX."),
    (
        "03-valide-45-colonnes-permutees.csv",
        _03_valide_45_colonnes_permutees,
        "45 lignes valides (REC-101..145), séparateur « , », colonnes dans un ordre permuté.",
    ),
    (
        "04-encodage-utf8-bom.csv",
        _04_encodage_utf8_bom,
        "5 lignes accentuées (REC-401..405), encodage UTF-8 avec BOM.",
    ),
    (
        "05-encodage-cp1252.csv",
        _05_encodage_cp1252,
        "Mêmes identités que 04 (REC-401..405), encodage CP1252 — mêmes noms décodés attendus.",
    ),
    (
        "06-valide-colonnes-permutees.csv",
        _06_valide_colonnes_permutees_petit_lot,
        "5 lignes valides (REC-501..505), colonnes permutées autrement qu'en 03.",
    ),
    (
        "07-valide-entetes-majuscules.csv",
        _07_valide_entetes_majuscules,
        "5 lignes valides (REC-601..605), en-têtes tout en majuscules, sans accent.",
    ),
    (
        "08-colonne-matricule-absente.csv",
        _08_colonne_matricule_absente,
        "5 lignes (REC-951..955) sans la colonne Matricule — refus global attendu.",
    ),
    (
        "09-matricule-manquant-ligne-12.csv",
        _09_matricule_manquant_ligne_12,
        "14 lignes (REC-701..714), matricule vidé sur la 12e ligne de données (ligne 13 avec l'en-tête).",
    ),
    (
        "10-doublon-dans-le-fichier.csv",
        _10_doublon_dans_le_fichier,
        "REC-201 répété deux fois + REC-202..205 — la seconde occurrence est en anomalie.",
    ),
    (
        "11-doublon-en-base.csv",
        _11_doublon_en_base,
        "REC-001/REC-002 (déjà dans 01) + REC-801..803 — doublon en base UNIQUEMENT si 01 a déjà été importé dans la même session.",
    ),
    (
        "12-un-champ-vide-par-ligne.csv",
        _12_un_champ_obligatoire_vide_par_ligne,
        "5 lignes (REC-901..905), une colonne obligatoire différente vidée à chaque ligne.",
    ),
    ("13-faux-fichier.csv", _13_faux_fichier, "Un PDF renommé en .csv — refus de format attendu."),
)

NOMS_FICHIERS = tuple(nom for nom, _fonction, _description in FICHIERS)


def generer(dossier, stdout):
    """Écrit les treize fichiers et le lisez-moi dans `dossier`, jamais ailleurs.
    Aucun appel ne doit pointer par défaut vers `DOSSIER` (dépôt suivi) : seule
    la commande `charger_jeu_recette --regenerer-fichiers-import` l'écrit."""
    dossier.mkdir(parents=True, exist_ok=True)
    for nom, fonction, _description in FICHIERS:
        (dossier / nom).write_bytes(fonction())
    (dossier / "00-LISEZ-MOI.md").write_bytes(_contenu_lisez_moi().encode("utf-8"))
    stdout.write(f"  {len(FICHIERS)} fichiers d'import générés dans {dossier}/.")


def _contenu_lisez_moi():
    lignes = [
        "# Fichiers d'import de recette — US-SES-05",
        "",
        "Générés par `charger_jeu_recette --regenerer-fichiers-import` (Prompt 34, § 3). "
        "Ne pas modifier à la main. Le chargement et les tests ne les réécrivent jamais : "
        "seule cette option les régénère, et leur diff se relit avant commit.",
        "",
        "| Fichier | Contenu | Résultat attendu à l'import |",
        "|---|---|---|",
    ]
    lignes += [f"| `{nom}` | {description} | |" for nom, _fonction, description in FICHIERS]
    lignes += [
        "",
        "## Fichier 11 — recette en deux temps",
        "",
        "`11-doublon-en-base.csv` ne produit un doublon en base (RG-18, "
        "détection bornée à la session) que si `01-valide-10.csv` a déjà été "
        "importé et confirmé dans la MÊME session. Séquence à suivre :",
        "",
        "1. Importer et confirmer `01-valide-10.csv` dans une session.",
        "2. Importer `11-doublon-en-base.csv` dans la MÊME session : "
        "`REC-001` et `REC-002` doivent apparaître en doublons en base, "
        "`REC-801` à `REC-803` en lignes valides.",
    ]
    return "\n".join(lignes) + "\n"
