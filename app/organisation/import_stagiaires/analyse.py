"""Analyse d'un fichier de stagiaires, SANS AUCUN ENREGISTREMENT — temps 1 du
scénario nominal (RG-18, § 4, Prompt 24). `analyser` est une fonction pure du
contenu du fichier et de l'état courant de la base (les matricules déjà
enregistrés sur la session) : rejouée À L'IDENTIQUE au temps 2 (confirmation),
jamais un aperçu qu'on se contenterait de croire — RÈGLE ABSOLUE du § 4, seule
garantie contre deux imports concurrents sur la même session (variante de P-31).
"""

from dataclasses import dataclass, field

from django.conf import settings

from noyau.exceptions import ErreurValidation
from organisation.import_stagiaires.constantes import CHAMPS_OBLIGATOIRES, libelle_champ
from organisation.import_stagiaires.lecteur import lire_fichier
from organisation.models import Stagiaire


@dataclass(frozen=True)
class AnomalieLigne:
    numero_ligne: int
    motif: str


@dataclass(frozen=True)
class DoublonEnBase:
    numero_ligne: int
    matricule: str


@dataclass(frozen=True)
class LigneValide:
    numero_ligne: int
    donnees: dict


@dataclass
class RapportImport:
    lignes_valides: list = field(default_factory=list)
    anomalies: list = field(default_factory=list)
    doublons_en_base: list = field(default_factory=list)

    @property
    def peut_confirmer(self):
        """E3 — aucun bouton de confirmation actif sur un compte rendu sans
        aucune ligne valide."""
        return bool(self.lignes_valides)


def analyser(session, contenu, nom_fichier):
    _verifier_volume(contenu)
    champs_manquants, lignes = lire_fichier(contenu, nom_fichier)
    if champs_manquants:
        libelles = ", ".join(libelle_champ(champ) for champ in champs_manquants)
        raise ErreurValidation(
            f"Colonne(s) obligatoire(s) absente(s) : {libelles}. Reprenez le modèle "
            "téléchargeable et complétez les en-têtes manquants."
        )
    if len(lignes) > settings.IMPORT_STAGIAIRES_LIGNES_MAX:
        raise ErreurValidation(
            f"Le fichier comporte {len(lignes)} lignes, au-delà du maximum autorisé "
            f"({settings.IMPORT_STAGIAIRES_LIGNES_MAX}) : scindez-le en plusieurs imports."
        )
    return _analyser_lignes(session, lignes)


def _verifier_volume(contenu):
    if len(contenu) > settings.IMPORT_STAGIAIRES_TAILLE_MAX_OCTETS:
        taille_kio = settings.IMPORT_STAGIAIRES_TAILLE_MAX_OCTETS // 1024
        raise ErreurValidation(
            f"Le fichier dépasse la taille maximale autorisée ({taille_kio} Kio) : "
            "scindez-le en plusieurs imports."
        )


def _analyser_lignes(session, lignes):
    matricules_en_base = _matricules_en_base(session)
    rapport = RapportImport()
    matricules_vus = {}
    for numero_ligne, valeurs in lignes:
        motif = _motif_anomalie(valeurs)
        if motif:
            rapport.anomalies.append(AnomalieLigne(numero_ligne, motif))
            continue
        matricule_normalise = valeurs["matricule"].upper()
        if matricule_normalise in matricules_vus:
            rapport.anomalies.append(
                AnomalieLigne(
                    numero_ligne,
                    "matricule en doublon dans le fichier (déjà utilisé ligne "
                    f"{matricules_vus[matricule_normalise]})",
                )
            )
            continue
        matricules_vus[matricule_normalise] = numero_ligne
        if matricule_normalise in matricules_en_base:
            rapport.doublons_en_base.append(DoublonEnBase(numero_ligne, valeurs["matricule"]))
            continue
        rapport.lignes_valides.append(LigneValide(numero_ligne, valeurs))
    return rapport


def _matricules_en_base(session):
    return {
        matricule.upper()
        for matricule in Stagiaire.objects.filter(session=session).values_list(
            "matricule", flat=True
        )
    }


def _motif_anomalie(valeurs):
    for champ in CHAMPS_OBLIGATOIRES:
        if not valeurs.get(champ):
            return f"{libelle_champ(champ)} absent"
    return None
