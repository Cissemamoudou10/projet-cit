"""Schéma d'instance neutre (JSON) — Prompt 32 § 6 : le générateur, le
modèle CP-SAT et l'heuristique de comparaison lisent tous la même
description, aucun des trois ne connaît les autres.

Simplification déclarée (PROTOCOLE.md § 5, au-delà des trois du prompt) :
la qualification (RG-35) est portée directement par le MODULE plutôt que
par la matière puis propagée à travers les éléments de référentiel qui la
composent — un module de cette instance correspond ici à un couple
(formation, matière) unique, comme `ElementReferentiel` dans l'application.
Aucun effet sur la combinatoire mesurée : la restriction de domaine
(instructeur qualifié) porte sur le même nombre d'objets, qu'on l'appelle
matière ou module.
"""

import dataclasses
import hashlib
import json

DUREE_CRENEAU_HEURES = 2.0  # constant, déclaré — grille ordinaire ≈ 1h45-2h
JOURS_OUVRES = ["lundi", "mardi", "mercredi", "jeudi", "vendredi"]


@dataclasses.dataclass(frozen=True)
class Creneau:
    id: int
    jour: str
    ordre: int


@dataclasses.dataclass(frozen=True)
class LieuPartage:
    id: str
    type: str
    capacite: int
    mode: str  # "SEQUENTIEL" | "SIMULTANE" — RG-37


@dataclasses.dataclass(frozen=True)
class Module:
    id: str
    formation_id: str
    volume_prescrit: float
    necessite_lieu_partage: bool
    type_lieu_partage: str | None
    prerequis_id: str | None
    # RG-39(a) — plafond GLOBAL, toutes brigades confondues (CONTRAINTES-
    # SOLVEUR.md, portée : « par élément de référentiel, toutes brigades
    # confondues » ; confirmé dans le code réel, regles_volume.py, la clé du
    # plafond est `element.pk` seul, jamais `(element.pk, brigade.pk)`).
    volume_deja_programme: float = 0.0


@dataclasses.dataclass(frozen=True)
class Brigade:
    id: str
    formation_id: str
    effectif: int
    # RG-39(b) — prérequis, PAR BRIGADE (portée différente du plafond ci-
    # dessus) : heures déjà acquises par CETTE brigade sur chaque module qui
    # sert de prérequis à un autre — simule la progression acquise avant
    # cette semaine, qu'aucune semaine antérieure réelle ne fournit dans une
    # instance synthétique d'une seule semaine.
    volume_deja_programme: dict
    # PROGRAMME CIBLE de la semaine (correction du 2026-09-18, revue du
    # Prompt 32) : module -> nombre de créneaux à pourvoir. C'est LUI qui
    # porte la demande en lieux partagés du § 4 — sur les SÉANCES À
    # POURVOIR, pas sur le catalogue : sans lui, le solveur choisissait
    # librement les modules et évitait ceux qui exigent un lieu, si bien que
    # la demande effective n'atteignait que le tiers de celle annoncée.
    programme_cible: dict = dataclasses.field(default_factory=dict)


@dataclasses.dataclass(frozen=True)
class Instructeur:
    id: str
    modules_qualifies: list


@dataclasses.dataclass(frozen=True)
class Instance:
    meta: dict
    creneaux: list
    lieux_partages: list
    modules: list
    brigades: list
    instructeurs: list

    def vers_dict(self):
        return {
            "meta": self.meta,
            "creneaux": [dataclasses.asdict(c) for c in self.creneaux],
            "lieux_partages": [dataclasses.asdict(lieu) for lieu in self.lieux_partages],
            "modules": [dataclasses.asdict(m) for m in self.modules],
            "brigades": [dataclasses.asdict(b) for b in self.brigades],
            "instructeurs": [dataclasses.asdict(i) for i in self.instructeurs],
        }

    def empreinte(self):
        """Empreinte du contenu : deux processus qui génèrent « la même »
        instance doivent obtenir la même empreinte, sans quoi les mesures d'une
        même ligne ne portent pas sur le même problème."""
        return hashlib.sha256(self.vers_json(indent=None).encode("utf-8")).hexdigest()[:16]

    def vers_json(self, indent=2):
        return json.dumps(self.vers_dict(), ensure_ascii=False, indent=indent)


def depuis_dict(donnees):
    return Instance(
        meta=donnees["meta"],
        creneaux=[Creneau(**c) for c in donnees["creneaux"]],
        lieux_partages=[LieuPartage(**lieu) for lieu in donnees["lieux_partages"]],
        modules=[Module(**m) for m in donnees["modules"]],
        brigades=[Brigade(**b) for b in donnees["brigades"]],
        instructeurs=[Instructeur(**i) for i in donnees["instructeurs"]],
    )


def depuis_json(texte):
    return depuis_dict(json.loads(texte))
