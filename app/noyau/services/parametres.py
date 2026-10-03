"""Résolution de données qu'une couche basse consomme mais que seule une
couche haute peut calculer — US-PLAN-12, § 7, Prompt 29 (arbitrage du chef
de projet, docs/suivi/DECISIONS.md).

`noyau` ne dépend d'aucune application (`tests/architecture/test_couches.py`)
et `referentiel`/`organisation` ne peuvent pas importer `ressources` (sens de
dépendance interdit — `ressources` importe déjà `organisation`, l'inverse
créerait un cycle réel, pas seulement une garantie affaiblie). La couche qui
détient la vraie donnée installe donc son fournisseur ICI, au démarrage de
l'application (`AppConfig.ready()`), jamais l'inverse — même sens que
l'injection de D-19, un nouveau point d'extension.

Un point de résolution par donnée, jamais un registre générique par clé :
plus simple à lire, et la règle de repli reste écrite une seule fois, à
côté de la donnée qu'elle concerne — jamais dupliquée chez chaque
consommateur (deux de plus arrivent : US-PLAN-03, US-SUI-06).
"""

from django.conf import settings


class ResolveurVolumeHoraireReference:
    """Volume horaire hebdomadaire de référence (BNF-13) — RG-65, consommé
    par `ServiceReferentiel.ecart` (US-REF-03) et l'exception E2 de
    `ServiceSession` (US-SES-01).

    Repli sur `settings.VOLUME_HORAIRE_HEBDOMADAIRE_REFERENCE` tant qu'aucun
    fournisseur n'est installé, ou si le fournisseur installé ne trouve
    aucune grille active (il retourne alors `None`) — cette règle de repli
    vit ICI et nulle part ailleurs.
    """

    _fournisseur = None

    @classmethod
    def installer_fournisseur(cls, fonction):
        cls._fournisseur = fonction

    @classmethod
    def resoudre(cls) -> float:
        if cls._fournisseur is not None:
            valeur = cls._fournisseur()
            if valeur is not None:
                return valeur
        return settings.VOLUME_HORAIRE_HEBDOMADAIRE_REFERENCE


class ResolveurSeancesFuturesQualification:
    """RG-22 (D-51, US-INS-02) : retirer une qualification est refusé tant
    que des séances futures l'exploitent — `ServiceQualification.retirer`
    (`ressources`) doit donc savoir si `planification.Seance` en porte,
    sans jamais importer `planification` (sens de dépendance interdit :
    `planification` importe déjà `ressources`, l'inverse créerait un cycle
    réel — même motif qu'à US-PLAN-12, D-128).

    Repli : aucun fournisseur installé ⇒ aucune séance future connue
    (liste vide) — c'est le comportement antérieur à cette story, où
    `Seance` n'existait pas encore.
    """

    _fournisseur = None

    @classmethod
    def installer_fournisseur(cls, fonction):
        cls._fournisseur = fonction

    @classmethod
    def resoudre(cls, instructeur, matiere) -> list:
        if cls._fournisseur is not None:
            return cls._fournisseur(instructeur, matiere)
        return []


class ResolveurSeancesDeControle:
    """A9, Prompt 35 (D-183) : le programme signale qu'une séance est un
    contrôle sans que `planification` importe `evaluations` (sens de
    dépendance interdit — `evaluations` importe déjà `planification`,
    l'inverse créerait un cycle réel, même motif qu'à D-128/D-143).

    Une seule requête pour tout l'ensemble de séances affichées, jamais une
    par séance (E2, Prompt 35) : `resoudre` reçoit la collection complète des
    identifiants à qualifier, pas un identifiant à la fois.

    Repli : aucun fournisseur installé ⇒ aucune séance connue comme
    contrôle (ensemble vide) — comportement antérieur à cette story, où
    `Evaluation` n'existait pas.
    """

    _fournisseur = None

    @classmethod
    def installer_fournisseur(cls, fonction):
        cls._fournisseur = fonction

    @classmethod
    def resoudre(cls, ids_seances) -> frozenset:
        if cls._fournisseur is not None:
            return cls._fournisseur(ids_seances)
        return frozenset()


class ResolveurJoursExamen:
    """A2, Prompt 36 : `planification` (RG-38) et `ressources` (vues du
    calendrier) ne peuvent pas importer `evaluations` — même motif que
    `ResolveurSeancesDeControle`. Un fournisseur, deux consommateurs.

    `resoudre(debut, fin)` rend, pour l'intervalle `[debut, fin)` (dates,
    bornes semi-ouvertes), une liste de `{"jour", "brigades", "libelle"}` —
    un élément par évaluation certificative dont la date tombe dans
    l'intervalle, le périmètre déjà résolu en identifiants de brigade (A4 :
    au moment de l'appel, jamais une liste recopiée).

    Repli : aucun fournisseur installé ⇒ aucun jour d'examen connu (liste
    vide) — `planification` et `ressources` restent testables seules.
    """

    _fournisseur = None

    @classmethod
    def installer_fournisseur(cls, fonction):
        cls._fournisseur = fonction

    @classmethod
    def resoudre(cls, debut, fin) -> list:
        if cls._fournisseur is not None:
            return cls._fournisseur(debut, fin)
        return []


class ResolveurOccupationsEpreuves:
    """A6, Prompt 38 : `planification` (RG-34, RG-37) ne peut pas importer
    `evaluations` — même motif que `ResolveurJoursExamen`. Un fournisseur, un
    consommateur qui lit la même date.

    `resoudre(debut, fin)` rend, pour `[debut, fin)` (instants), une liste de
    `{"debut", "fin", "lieux", "instructeurs", "libelle"}` : une entrée par
    épreuve certificative dont le créneau recouvre l'intervalle, avec les lieux
    occupés et les instructeurs surveillants. Repli : aucun fournisseur ⇒ aucune
    occupation.
    """

    _fournisseur = None

    @classmethod
    def installer_fournisseur(cls, fonction):
        cls._fournisseur = fonction

    @classmethod
    def resoudre(cls, debut, fin) -> list:
        if cls._fournisseur is not None:
            return cls._fournisseur(debut, fin)
        return []

