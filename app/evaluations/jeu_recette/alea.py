"""Génération déterministe de données manifestement inventées — Prompt 51,
règles communes n° 5 et 7. Un seul `random.Random`, créé une fois par la
commande à partir de `--graine` (2026 par défaut) et PASSÉ à chaque fonction
d'ici, jamais recréé en cours de route : deux chargements à la même graine
tirent dans le même ordre et produisent les mêmes valeurs — c'est tout le
déterminisme (§ 2.8, test dédié).

Noms et matricules « visiblement artificiels » (jamais une liste réelle du
CIT) : syllabes générées, préfixe `FICT`, matricules au format `FX-000000` —
tels que le registre des risques (v8, R28) les décrit.
"""

import random

DEFAUT_GRAINE = 2026

PREFIXE_NOM = "FICT"

SYLLABES = (
    "ba",
    "be",
    "bi",
    "bo",
    "bu",
    "da",
    "de",
    "di",
    "do",
    "du",
    "fa",
    "fe",
    "fi",
    "fo",
    "fu",
    "ga",
    "ge",
    "gi",
    "go",
    "gu",
    "ka",
    "ke",
    "ki",
    "ko",
    "ku",
    "la",
    "le",
    "li",
    "lo",
    "lu",
    "ma",
    "me",
    "mi",
    "mo",
    "mu",
    "na",
    "ne",
    "ni",
    "no",
    "nu",
    "ra",
    "re",
    "ri",
    "ro",
    "ru",
    "sa",
    "se",
    "si",
    "so",
    "su",
    "ta",
    "te",
    "ti",
    "to",
    "tu",
    "va",
    "ve",
    "vi",
    "vo",
    "vu",
)


def nouveau_generateur(graine: int) -> random.Random:
    return random.Random(graine)


def nom_fictif(generateur: random.Random, nombre_syllabes: int = 2) -> str:
    """`FICT Basoki`, par exemple — jamais un nom qui pourrait ressembler à
    un nom réel du CIT (consonne-voyelle répétée, impossible à confondre)."""
    syllabes = "".join(generateur.choice(SYLLABES) for _ in range(nombre_syllabes))
    return f"{PREFIXE_NOM} {syllabes.capitalize()}"


def matricule_fictif(generateur: random.Random) -> str:
    return f"FX-{generateur.randint(0, 999999):06d}"


def note_fictive(generateur: random.Random, minimum: float = 8.0, maximum: float = 18.0) -> float:
    """Une décimale, dans une fourchette plausible — jamais 0 ni 20 par
    défaut, pour qu'un relevé de notes de recette ne ressemble pas à un
    jeu de test trivial."""
    return round(generateur.uniform(minimum, maximum), 1)
