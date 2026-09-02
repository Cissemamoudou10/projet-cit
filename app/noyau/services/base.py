"""Base de la couche services — mécanique commune de renseignement de
l'auteur et de sauvegarde.

Un service ne connaît pas la requête HTTP — voir .claude/rules/services.md.
Chaque méthode qui écrit prend l'utilisateur en paramètre explicite : ni
signal, ni variable de fil d'exécution ne doivent le capturer implicitement.
"""

from django.db import transaction


class ServiceBase:
    @staticmethod
    @transaction.atomic
    def creer(instance, utilisateur):
        instance.cree_par = utilisateur
        instance.modifie_par = utilisateur
        instance.save()
        return instance

    @staticmethod
    @transaction.atomic
    def modifier(instance, utilisateur):
        instance.modifie_par = utilisateur
        instance.save()
        return instance
