# -*- coding: utf-8 -*-
"""Contrôles d'architecture.

Ces tests vérifient ce que les consignes ne garantissent pas. Une instruction
écrite est suivie la plupart du temps ; un test qui échoue l'est toujours.

Lancer après chaque série d'éditions : pytest tests/architecture -q
"""

import ast
import pathlib
import re

RACINE = pathlib.Path(__file__).resolve().parents[2]
SRC = RACINE / "app"

APPLICATIONS = [
    "noyau",
    "administration",
    "referentiel",
    "organisation",
    "ressources",
    "planification",
    "evaluations",
]

# Ordre de dépendance arrêté en conception : une application ne peut importer
# que celles qui la précèdent. `organisation` (P3) précède `ressources` (P4)
# — sens inversé le 2026-09-11 (US-SES-03, D-85) : `SalleAttitree` et
# `PeriodeCalendrier` associent toutes deux `ressources` à `organisation`
# dans ce sens, jamais l'inverse. Voir docs/suivi/DECISIONS.md, D-78/D-85.
DEPENDANCES_AUTORISEES = {
    "noyau": set(),
    "administration": {"noyau"},
    "referentiel": {"noyau", "administration"},
    "organisation": {"noyau", "administration", "referentiel"},
    "ressources": {"noyau", "administration", "referentiel", "organisation"},
    "planification": {"noyau", "administration", "referentiel", "organisation", "ressources"},
    "evaluations": {
        "noyau",
        "administration",
        "referentiel",
        "organisation",
        "ressources",
        "planification",
    },
}

ATTRIBUTS_DERIVES = [
    "volume_programme",
    "volume_realise",
    "volume_restant",
    "effectif_reel",
    "charge_hebdomadaire",
    "portee",
    "duree_heures",
    "est_regroupee",
    "volume_cumule",
]

# § 11.2 du dossier des cas d'utilisation — neuf domaines, source :
# docs/suivi/HABILITATIONS.md. noyau n'y figure pas : c'est l'application
# technique, elle ne porte aucune opération soumise à une habilitation.
DOMAINES_CATALOGUE = {
    "administration",
    "referentiel",
    "organisation",
    "instructeurs_qualifications",
    "lieux_calendrier",
    "programme",
    "programme_validation",
    "evaluations",
    "suivi",
}


def fichiers(motif):
    if not SRC.exists():
        return []
    return [c for c in SRC.rglob(motif) if "migrations" not in c.parts]


def application_de(chemin):
    for partie in chemin.parts:
        if partie in APPLICATIONS:
            return partie
    return None


def test_aucune_vue_n_importe_un_modele():
    """Une vue appelle un service ; elle ne touche pas aux modèles."""
    fautifs = []
    for chemin in fichiers("views.py") + fichiers("views/*.py"):
        texte = chemin.read_text(encoding="utf-8")
        for noeud in ast.walk(ast.parse(texte)):
            if isinstance(noeud, ast.ImportFrom) and noeud.module:
                if noeud.module.endswith("models") or ".models" in noeud.module:
                    fautifs.append(
                        "%s ligne %d : %s"
                        % (chemin.relative_to(RACINE), noeud.lineno, noeud.module)
                    )
    assert not fautifs, "Import de modèle dans une vue :\n" + "\n".join(fautifs)


def test_aucun_service_ne_manipule_la_requete():
    """Un service ignore HTTP : il reçoit des objets, retourne des objets."""
    interdits = ("HttpResponse", "HttpRequest", "redirect(", "render(", "messages.")
    fautifs = []
    for chemin in fichiers("services.py") + fichiers("services/*.py"):
        texte = chemin.read_text(encoding="utf-8")
        for i, ligne in enumerate(texte.splitlines(), 1):
            if ligne.lstrip().startswith("#"):
                continue
            for terme in interdits:
                if terme in ligne:
                    fautifs.append("%s ligne %d : %s" % (chemin.relative_to(RACINE), i, terme))
    assert not fautifs, "Objet HTTP dans un service :\n" + "\n".join(fautifs)


def test_aucun_attribut_derive_n_est_un_champ():
    """Les neuf grandeurs dérivées se calculent et ne sont jamais stockées."""
    fautifs = []
    for chemin in fichiers("models.py") + fichiers("models/*.py"):
        texte = chemin.read_text(encoding="utf-8")
        for i, ligne in enumerate(texte.splitlines(), 1):
            for nom in ATTRIBUTS_DERIVES:
                if re.match(r"\s*%s\s*=\s*models\." % nom, ligne):
                    fautifs.append("%s ligne %d : %s" % (chemin.relative_to(RACINE), i, nom))
    assert not fautifs, "Attribut dérivé stocké en base :\n" + "\n".join(fautifs)


def test_aucune_note_en_flottant():
    """Une moyenne en flottant peut donner 11,999999 : la mention change."""
    fautifs = []
    for chemin in fichiers("models.py") + fichiers("models/*.py"):
        texte = chemin.read_text(encoding="utf-8")
        for i, ligne in enumerate(texte.splitlines(), 1):
            if "FloatField" in ligne:
                fautifs.append("%s ligne %d" % (chemin.relative_to(RACINE), i))
    assert not fautifs, "FloatField employé — utiliser DecimalField :\n" + "\n".join(fautifs)


def est_dataclass(noeud):
    """Un porte-données (`@dataclass`) n'est pas un service : il n'agit pas,
    il ne fait que transporter un lot de valeurs entre deux méthodes.
    """
    for decorateur in noeud.decorator_list:
        cible = decorateur.func if isinstance(decorateur, ast.Call) else decorateur
        if isinstance(cible, ast.Name) and cible.id == "dataclass":
            return True
        if isinstance(cible, ast.Attribute) and cible.attr == "dataclass":
            return True
    return False


def test_toute_classe_de_service_declare_un_domaine():
    """Prompt 03, § 2.4 : chaque service se range dans un domaine du
    catalogue par construction, pas par vigilance. noyau exclu — voir
    DOMAINES_CATALOGUE.
    """
    fautifs = []
    for chemin in fichiers("services.py") + fichiers("services/*.py"):
        if application_de(chemin.relative_to(SRC)) == "noyau":
            continue
        arbre = ast.parse(chemin.read_text(encoding="utf-8"))
        for noeud in ast.walk(arbre):
            if not isinstance(noeud, ast.ClassDef) or est_dataclass(noeud):
                continue
            domaine = None
            for element in noeud.body:
                if not isinstance(element, ast.Assign):
                    continue
                for cible in element.targets:
                    if (
                        isinstance(cible, ast.Name)
                        and cible.id == "DOMAINE"
                        and isinstance(element.value, ast.Constant)
                    ):
                        domaine = element.value.value
            if domaine is None:
                fautifs.append(
                    "%s ligne %d : %s sans DOMAINE"
                    % (chemin.relative_to(RACINE), noeud.lineno, noeud.name)
                )
            elif domaine not in DOMAINES_CATALOGUE:
                fautifs.append(
                    "%s ligne %d : %s, domaine %r hors catalogue"
                    % (chemin.relative_to(RACINE), noeud.lineno, noeud.name, domaine)
                )
    assert not fautifs, "Service sans domaine valide du catalogue :\n" + "\n".join(fautifs)


def test_aucun_controle_de_profil_ecrit_en_dur():
    """Prompt 03, § 2.5 : les droits reposent sur le catalogue d'habilitations
    (`noyau.Habilitation`, codes en `_lecture`/`_ecriture`), jamais sur une
    permission de modèle Django générée automatiquement (`add_`, `change_`,
    `delete_`, `view_`) — signe d'un contrôle de profil resté écrit en dur au
    lieu de passer par `a_permission`/`verifier_habilitation`.
    """
    motif = re.compile(r"""["'][a-z_]+\.(add|change|delete|view)_[a-z_]+["']""")
    fautifs = []
    for chemin in fichiers("*.py"):
        texte = chemin.read_text(encoding="utf-8")
        for i, ligne in enumerate(texte.splitlines(), 1):
            if ligne.lstrip().startswith("#"):
                continue
            if motif.search(ligne):
                fautifs.append("%s ligne %d : %s" % (chemin.relative_to(RACINE), i, ligne.strip()))
    assert not fautifs, "Contrôle de profil écrit en dur (permission de modèle) :\n" + "\n".join(
        fautifs
    )


def test_instructeur_n_a_aucune_relation_vers_utilisateur():
    """RG-23, § 4, Prompt 27 : l'instructeur n'a aucun accès au système —
    aucune saisie en libre-service, donc aucune relation, dans un sens ou
    dans l'autre, entre `Instructeur` et le modèle utilisateur. Contrainte
    de conception durable, pas une préférence du moment (§ 4).

    Deux angles indépendants (.claude/rules/tests.md, « vérifier une
    absence ») : les champs déclarés sur `Instructeur` lui-même, ET les
    relations inverses exposées par le modèle utilisateur. `cree_par`/
    `modifie_par` (`ModeleHorodate`) sont exclus : ils tracent l'AGENT qui a
    saisi la fiche, présents sur tous les modèles, pas un accès de
    l'instructeur — exactement la distinction que RG-23 pose.
    """
    from django.conf import settings

    from ressources.models import Instructeur

    champs_provenance = {"cree_par", "modifie_par"}
    champs_relation = [
        champ
        for champ in Instructeur._meta.get_fields()
        if champ.is_relation and champ.concrete and champ.name not in champs_provenance
    ]
    cibles = {champ.related_model._meta.label for champ in champs_relation if champ.related_model}
    assert (
        settings.AUTH_USER_MODEL not in cibles
    ), f"Instructeur porte une relation vers {settings.AUTH_USER_MODEL} : {cibles}"

    from django.contrib.auth import get_user_model

    relations_inverses = {
        champ.name
        for champ in get_user_model()._meta.get_fields()
        if champ.is_relation and champ.related_model is Instructeur
    }
    assert not relations_inverses, (
        "Le modèle utilisateur porte une relation vers Instructeur : "
        + ", ".join(relations_inverses)
    )


def test_grille_horaire_n_a_aucune_relation_vers_periode_calendrier():
    """RG-63, § 4, Prompt 29 : l'activation n'est jamais déduite du
    calendrier — le passage à l'horaire de Ramadan est un acte de
    commandement, non la conséquence d'une date. Aucune association, dans
    aucun sens, entre `GrilleHoraire`/`CreneauType` et `PeriodeCalendrier`.
    Même méthode que `test_instructeur_n_a_aucune_relation_vers_utilisateur`
    (deux angles indépendants) : les champs déclarés sur les grilles et les
    créneaux, ET les relations inverses exposées par `PeriodeCalendrier`.
    """
    from ressources.models import CreneauType, GrilleHoraire, PeriodeCalendrier

    for modele in (GrilleHoraire, CreneauType):
        cibles = {
            champ.related_model._meta.label
            for champ in modele._meta.get_fields()
            if champ.is_relation and champ.concrete and champ.related_model
        }
        assert (
            PeriodeCalendrier._meta.label not in cibles
        ), f"{modele.__name__} porte une relation vers PeriodeCalendrier : {cibles}"

    relations_inverses = {
        champ.name
        for champ in PeriodeCalendrier._meta.get_fields()
        if champ.is_relation and champ.related_model in (GrilleHoraire, CreneauType)
    }
    assert not relations_inverses, (
        "PeriodeCalendrier porte une relation vers une grille ou un créneau : "
        + ", ".join(relations_inverses)
    )


def test_ordre_des_dependances_entre_applications():
    """P1 → P2 → P3/P4 → P5 → P6. Aucune dépendance inverse."""
    fautifs = []
    for chemin in fichiers("*.py"):
        app = application_de(chemin.relative_to(SRC))
        if app is None:
            continue
        autorisees = DEPENDANCES_AUTORISEES[app] | {app}
        texte = chemin.read_text(encoding="utf-8")
        for noeud in ast.walk(ast.parse(texte)):
            module = getattr(noeud, "module", None)
            if isinstance(noeud, ast.ImportFrom) and module:
                for autre in APPLICATIONS:
                    if module.split(".")[0] == autre and autre not in autorisees:
                        fautifs.append(
                            "%s ligne %d : %s importe %s"
                            % (chemin.relative_to(RACINE), noeud.lineno, app, autre)
                        )
    assert not fautifs, "Dépendance inverse entre applications :\n" + "\n".join(fautifs)
