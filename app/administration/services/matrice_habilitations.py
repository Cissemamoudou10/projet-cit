"""Configuration de la matrice d'habilitations — RG-02 bis, Prompt 03 § 6.

Un service ne connaît pas la requête HTTP — voir .claude/rules/services.md.
"""

from dataclasses import dataclass

from django.contrib.auth.models import Group, Permission
from django.db import transaction

from administration.constantes import GROUPES, MATRICE
from administration.habilitations import verifier_habilitation
from administration.models import TypeAction
from administration.services.comptes import PERMISSION_GESTION_COMPTES
from administration.services.journal import ServiceJournal
from noyau.exceptions import ErreurValidation


@dataclass(frozen=True)
class CroisementModifie:
    """Un croisement soumis par l'écran de configuration (§ 6)."""

    nom_groupe: str
    domaine: str
    niveau: str
    valeur: bool


@dataclass
class _ContextePermissions:
    """État préchargé une seule fois pour tout un lot de croisements — voir
    `appliquer_changements`. `a_ajouter`/`a_retirer` accumulent les
    permissions M2M à écrire, groupe par groupe, pour ne les écrire qu'une
    fois par groupe en fin de traitement plutôt qu'une fois par croisement.
    """

    groupes: dict
    etats: dict
    permissions: dict
    a_ajouter: dict
    a_retirer: dict


# § 11.2 — neuf domaines dans l'ordre de la matrice, code puis libellé
# d'affichage. Voir docs/suivi/HABILITATIONS.md pour le détail.
DOMAINES = [
    ("administration", "P1 — Administration"),
    ("referentiel", "P2 — Référentiel"),
    ("organisation", "P3 — Organisation"),
    ("instructeurs_qualifications", "P4 — Instructeurs et qualifications"),
    ("lieux_calendrier", "P4 — Lieux et calendrier"),
    ("programme", "P5 — Génération et modification du programme"),
    ("programme_validation", "P5 — Validation du programme"),
    ("evaluations", "P6 — Évaluations"),
    ("suivi", "P6 — Suivi"),
]

# Les noms de groupe portent des espaces et des accents : un identifiant
# court et stable pour les champs de formulaire et l'URL.
SLUGS_GROUPES = {
    "pedagogique": "Cellule pédagogique",
    "planification": "Cellule planification",
    "examens": "Cellule examens",
    "direction": "Direction de formation",
    "administrateur": "Administrateur",
}


class ServiceMatriceHabilitations:
    DOMAINE = "administration"

    @staticmethod
    def matrice(agissant):
        """État courant, croisement par croisement, avec l'écart à la
        matrice de référence § 11.2 (§ 6 : l'encadré le signale visuellement).
        """
        verifier_habilitation(agissant, PERMISSION_GESTION_COMPTES)

        permissions_par_groupe = {
            groupe.name: {p.codename for p in groupe.permissions.all()}
            for groupe in Group.objects.filter(name__in=GROUPES).prefetch_related("permissions")
        }

        lignes = []
        for code, libelle in DOMAINES:
            colonnes = []
            for slug, nom_groupe in SLUGS_GROUPES.items():
                actuelles = permissions_par_groupe.get(nom_groupe, set())
                reference = set(MATRICE.get(nom_groupe, []))
                lecture = f"{code}_lecture" in actuelles
                ecriture = f"{code}_ecriture" in actuelles
                lecture_ref = f"{code}_lecture" in reference
                ecriture_ref = f"{code}_ecriture" in reference
                colonnes.append(
                    {
                        "slug": slug,
                        "groupe": nom_groupe,
                        "lecture": lecture,
                        "ecriture": ecriture,
                        "ecart": lecture != lecture_ref or ecriture != ecriture_ref,
                    }
                )
            lignes.append({"code": code, "libelle": libelle, "colonnes": colonnes})
        return lignes

    @staticmethod
    @transaction.atomic
    def appliquer_changements(agissant, changements: list[CroisementModifie]):
        """Précharge une bonne fois les cinq groupes et les dix-huit
        permissions du catalogue : l'écran de configuration (§ 6) peut
        soumettre jusqu'à 45 croisements en un seul aller-retour, et une
        requête par croisement violerait la règle « aucune requête dans une
        boucle » (.claude/rules/python.md).
        """
        verifier_habilitation(agissant, PERMISSION_GESTION_COMPTES)
        if not changements:
            return []

        contexte = ServiceMatriceHabilitations._precharger()
        erreurs = []
        for changement in changements:
            try:
                ServiceMatriceHabilitations._appliquer_un_changement(agissant, changement, contexte)
            except ErreurValidation as erreur:
                erreurs.append(str(erreur))
        ServiceMatriceHabilitations._ecrire_permissions_en_attente(contexte)
        return erreurs

    @staticmethod
    def _precharger() -> _ContextePermissions:
        groupes = {
            g.name: g
            for g in Group.objects.filter(name__in=GROUPES).prefetch_related("permissions")
        }
        permissions = {
            p.codename: p
            for p in Permission.objects.filter(
                content_type__app_label="noyau", content_type__model="habilitation"
            )
        }
        etats = {
            nom: {p.codename for p in groupe.permissions.all()} for nom, groupe in groupes.items()
        }
        return _ContextePermissions(
            groupes=groupes,
            etats=etats,
            permissions=permissions,
            a_ajouter={nom: set() for nom in groupes},
            a_retirer={nom: set() for nom in groupes},
        )

    @staticmethod
    def _ecrire_permissions_en_attente(contexte: _ContextePermissions):
        """Une seule écriture M2M par groupe et par sens (ajout/retrait),
        quel que soit le nombre de croisements traités — au plus dix
        requêtes pour un lot de 45 croisements sur cinq groupes.
        """
        for nom_groupe, groupe in contexte.groupes.items():
            a_ajouter = [contexte.permissions[code] for code in contexte.a_ajouter[nom_groupe]]
            a_retirer = [contexte.permissions[code] for code in contexte.a_retirer[nom_groupe]]
            if a_ajouter:
                groupe.permissions.add(*a_ajouter)
            if a_retirer:
                groupe.permissions.remove(*a_retirer)

    @staticmethod
    def _appliquer_un_changement(
        agissant, changement: CroisementModifie, contexte: _ContextePermissions
    ):
        if changement.niveau not in ("lecture", "ecriture"):
            raise ErreurValidation("Niveau d'habilitation inconnu.")

        etat_groupe = contexte.etats[changement.nom_groupe]
        codenames = {
            "lecture": f"{changement.domaine}_lecture",
            "ecriture": f"{changement.domaine}_ecriture",
        }
        ancien = {cle: code in etat_groupe for cle, code in codenames.items()}
        nouveau = ServiceMatriceHabilitations._etat_resultant(
            ancien, changement.niveau, changement.valeur
        )

        ServiceMatriceHabilitations._interdire_perte_administration_ecriture(
            changement.nom_groupe, changement.domaine, nouveau["ecriture"]
        )
        ServiceMatriceHabilitations._marquer_permissions(
            changement.nom_groupe, codenames, nouveau, etat_groupe, contexte
        )

        if nouveau != ancien:
            ServiceMatriceHabilitations._journaliser(
                agissant, changement.nom_groupe, changement.domaine, ancien, nouveau
            )

    @staticmethod
    def _etat_resultant(ancien, niveau, valeur):
        """Cocher l'écriture coche la lecture ; décocher la lecture décoche
        l'écriture — écrire sans pouvoir lire, ou refuser la lecture tout en
        gardant l'écriture, n'a pas de sens (§ 6).
        """
        nouveau = dict(ancien)
        if niveau == "ecriture":
            nouveau["ecriture"] = valeur
            if valeur:
                nouveau["lecture"] = True
        else:
            nouveau["lecture"] = valeur
            if not valeur:
                nouveau["ecriture"] = False
        return nouveau

    @staticmethod
    def _marquer_permissions(
        nom_groupe, codenames, nouveau, etat_groupe, contexte: _ContextePermissions
    ):
        """N'écrit rien : accumule dans `contexte` ce que
        `_ecrire_permissions_en_attente` écrira en une fois par groupe.
        """
        for cle, code in codenames.items():
            deja_present = code in etat_groupe
            if nouveau[cle] == deja_present:
                continue
            if nouveau[cle]:
                contexte.a_ajouter[nom_groupe].add(code)
                etat_groupe.add(code)
            else:
                contexte.a_retirer[nom_groupe].add(code)
                etat_groupe.discard(code)

    @staticmethod
    def _journaliser(agissant, nom_groupe, domaine, ancien, nouveau):
        ServiceJournal.enregistrer(
            type_action=TypeAction.MODIFICATION_HABILITATIONS,
            identifiant_saisi="",
            detail=(
                f"{nom_groupe} / {domaine} : lecture {ancien['lecture']}→{nouveau['lecture']}, "
                f"écriture {ancien['ecriture']}→{nouveau['ecriture']}."
            ),
            auteur=agissant,
            cible=f"{nom_groupe}:{domaine}",
        )

    @staticmethod
    def _interdire_perte_administration_ecriture(nom_groupe, domaine, ecriture_resultante):
        """Même logique que le dernier administrateur actif d'US-ADM-02
        (D-07) : le profil administrateur ne peut pas perdre l'écriture sur
        Administration, sous peine de système inconfigurable (§ 6).
        """
        if (
            nom_groupe == "Administrateur"
            and domaine == "administration"
            and not ecriture_resultante
        ):
            raise ErreurValidation(
                "Le profil administrateur ne peut pas perdre l'écriture sur Administration : "
                "le système deviendrait inconfigurable."
            )
