"""Commande d'administration : crée les cinq groupes d'habilitation. Le
groupe Administrateur reçoit dès US-ADM-02 les permissions de gestion des
comptes ; les autres groupes restent vides, leurs permissions seront
attachées story par story — RG-02 bis.

noyau ne dépend d'aucune application : les groupes et les permissions sont
résolus par leur nom, jamais par un import de administration.models.
"""

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

GROUPES = [
    "Administrateur",
    "Cellule pédagogique",
    "Cellule planification",
    "Cellule examens",
    "Direction de formation",
]

PERMISSIONS_ADMINISTRATEUR = [
    ("administration", "add_utilisateur"),
    ("administration", "change_utilisateur"),
]


class Command(BaseCommand):
    help = "Crée les cinq groupes d'habilitation et les permissions de base d'Administrateur."

    def handle(self, *args, **options):
        for nom in GROUPES:
            _, cree = Group.objects.get_or_create(name=nom)
            if cree:
                self.stdout.write(self.style.SUCCESS(f"Groupe créé : {nom}"))
            else:
                self.stdout.write(f"Groupe déjà présent : {nom}")

        self._attacher_permissions_administrateur()

    def _attacher_permissions_administrateur(self):
        groupe = Group.objects.get(name="Administrateur")
        for app_label, codename in PERMISSIONS_ADMINISTRATEUR:
            permission = Permission.objects.get(
                content_type__app_label=app_label, codename=codename
            )
            groupe.permissions.add(permission)
        self.stdout.write(
            self.style.SUCCESS("Permissions de gestion des comptes attachées à Administrateur")
        )
