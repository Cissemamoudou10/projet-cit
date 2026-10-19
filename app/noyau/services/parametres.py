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


class ResolveurReinitialisationEvaluations:
    """Prompt 43, § A3 : la base de démonstration J2 reçoit en direct les
    évaluations que le scénario produit (contrôle, examen final) — le
    chargement de `planification.jeu_demonstration_j2` doit pouvoir les
    vider avant de recharger (§ A3, « rejouable ») sans que `planification`
    importe `evaluations` (DEPENDANCES_AUTORISEES, sens interdit). Un
    fournisseur (installé par `evaluations.apps.EvaluationsConfig.ready`),
    un seul consommateur. Repli : aucun fournisseur ⇒ rien à vider
    (`evaluations` non installée, ou tests isolés d'une seule application).
    """

    _fournisseur = None

    @classmethod
    def installer_fournisseur(cls, fonction):
        cls._fournisseur = fonction

    @classmethod
    def resoudre(cls) -> None:
        if cls._fournisseur is not None:
            cls._fournisseur()


class ResolveurVolumeRealiseBrigade:
    """R6, US-SUI-01 (prompt 44, D-108 refermé) : `ServiceAffectation.
    affecter` (`organisation`) signale le volume déjà réalisé par la
    brigade, toutes matières confondues, sans que `organisation` importe
    `planification` (sens de dépendance interdit — `planification` importe
    déjà `organisation`, même motif qu'ailleurs dans ce module).

    `resoudre(brigade)` rend le total en heures, à l'instant de l'appel.
    Repli : aucun fournisseur ⇒ 0 (aucun volume connu, comportement
    antérieur à cette story).
    """

    _fournisseur = None

    @classmethod
    def installer_fournisseur(cls, fonction):
        cls._fournisseur = fonction

    @classmethod
    def resoudre(cls, brigade) -> float:
        if cls._fournisseur is not None:
            return cls._fournisseur(brigade)
        return 0.0


class ResolveurEvaluationsNonFinalisees:
    """C2, US-SES-09 (prompt 47, Temps 4) : `ServiceSession.cloturer`
    (`organisation`) doit refuser la clôture d'une session portant des
    évaluations dont les notes ne sont pas verrouillées par un procès-verbal,
    sans qu'`organisation` importe `evaluations` (sens de dépendance
    interdit — `evaluations` importe déjà `organisation`, même motif
    qu'ailleurs dans ce module).

    `resoudre(session)` rend la liste des évaluations non finalisées du
    périmètre de la session, pour que le refus les énumère (C2 : « le refus
    énumère ces évaluations »). Repli : aucun fournisseur ⇒ liste vide
    (aucune évaluation connue, comportement antérieur à cette story)."""

    _fournisseur = None

    @classmethod
    def installer_fournisseur(cls, fonction):
        cls._fournisseur = fonction

    @classmethod
    def resoudre(cls, session) -> list:
        if cls._fournisseur is not None:
            return cls._fournisseur(session)
        return []


class ResolveurHeuresEnseignementParInstructeur:
    """C1, US-INS-04 (prompt 48) : `ressources.selectors_charge` (le
    domaine Instructeurs) a besoin des heures d'enseignement d'une période,
    par instructeur et par matière, sans que `ressources` importe
    `planification` (sens de dépendance interdit — `planification` importe
    déjà `ressources`, même motif qu'ailleurs dans ce module). Compte
    toutes les séances dont le DÉBUT tombe dans `[debut, fin)`, quel que
    soit l'état du programme (C1) ; une séance regroupée ne porte qu'UN
    instructeur par construction (`Seance.instructeur`), jamais comptée
    deux fois.

    `resoudre(debut, fin)` rend `{instructeur_id: [{"matiere": intitulé,
    "heures": total}, ...]}`, une seule requête. Repli : aucun fournisseur
    ⇒ dict vide (aucune séance connue, `planification` non installée ou
    tests isolés d'une seule application).
    """

    _fournisseur = None

    @classmethod
    def installer_fournisseur(cls, fonction):
        cls._fournisseur = fonction

    @classmethod
    def resoudre(cls, debut, fin) -> dict:
        if cls._fournisseur is not None:
            return cls._fournisseur(debut, fin)
        return {}


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
