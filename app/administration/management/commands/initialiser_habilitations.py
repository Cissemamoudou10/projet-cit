"""Commande d'administration : crée les cinq groupes d'habilitation et leur
attache les permissions de la matrice § 11.2 du dossier des cas
d'utilisation — RG-02, RG-02 bis.

Vit dans `administration`, pas `noyau` (où le socle l'avait posée) :
`--reinitialiser` journalise l'opération, ce qui exige `ServiceJournal` —
même contrainte que `verifier_habilitation`, voir docs/suivi/DECISIONS.md,
D-09. Les permissions elles-mêmes restent portées par `noyau.Habilitation`
(§ 2.1) ; cette commande ne fait que les rattacher aux groupes.

Idempotente sans écraser un réglage administrateur (§ 5) : la matrice n'est
appliquée qu'aux groupes dépourvus de toute permission. `--reinitialiser`
force le retour aux valeurs de la matrice pour tous les groupes.
"""

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from administration.constantes import GROUPES, MATRICE
from administration.models import TypeAction
from administration.services.journal import DonneesEntreeJournal, ServiceJournal


class Command(BaseCommand):
    help = "Crée les cinq groupes d'habilitation et leur attache les permissions de § 11.2."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reinitialiser",
            action="store_true",
            help="Force le retour de tous les groupes aux valeurs de la matrice § 11.2.",
        )

    def handle(self, *args, **options):
        for nom in GROUPES:
            _, cree = Group.objects.get_or_create(name=nom)
            if cree:
                self.stdout.write(self.style.SUCCESS(f"Groupe créé : {nom}"))

        for nom in GROUPES:
            self._appliquer_matrice(nom, force=options["reinitialiser"])

    def _appliquer_matrice(self, nom, *, force):
        groupe = Group.objects.get(name=nom)
        if not force and groupe.permissions.exists():
            self.stdout.write(f"{nom} : permissions déjà réglées, non modifiées.")
            return

        permissions = Permission.objects.filter(
            content_type__app_label="noyau",
            content_type__model="habilitation",
            codename__in=MATRICE[nom],
        )
        groupe.permissions.set(permissions)
        self.stdout.write(
            self.style.SUCCESS(f"{nom} : {permissions.count()} permissions appliquées (§ 11.2).")
        )
        if force:
            ServiceJournal.enregistrer_detaillee(
                DonneesEntreeJournal(
                    type_action=TypeAction.MODIFICATION_HABILITATIONS,
                    identifiant_saisi="",
                    detail=f"Groupe « {nom} » réinitialisé aux valeurs de la matrice § 11.2.",
                    cible=nom,
                    objet_type="groupe_habilitation",
                    objet_identifiant=nom,
                )
            )
