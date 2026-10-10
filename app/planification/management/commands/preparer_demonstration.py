"""Commande d'administration : prépare la base de démonstration J2 —
Prompt 43, § A3.

Rejouable sans option : remet la base à zéro à CHAQUE appel (jamais
idempotente comme les deux jeux existants — cette base reçoit en direct ce
que la démonstration produit, un reste de la fois précédente fausserait la
suivante). Refuse de s'exécuter sur une autre base que `pfe_cit_demo_j2`
(garde-fou, voir `jeu_demonstration_j2.garde`). S'arrête au début de
l'étape 1 du scénario (`docs/demonstration/DEMO-J2.md`) : aucun programme,
aucune séance n'est créé ici.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from planification.jeu_demonstration_j2.chargement import charger_tout
from planification.jeu_demonstration_j2.garde import verifier_environnement_sur
from planification.jeu_demonstration_j2.rapport import Chronometre, imprimer_compte_rendu
from planification.jeu_demonstration_j2.reinitialisation import vider_donnees_demonstration


class Command(BaseCommand):
    help = "Prépare la base de démonstration J2 (prompt 43) — remise à zéro à chaque appel."

    def handle(self, *args, **options):
        verifier_environnement_sur()
        chronometre = Chronometre()
        with transaction.atomic():
            vider_donnees_demonstration(self.stdout)
            resultat = charger_tout(self.stdout)
        compteurs = {
            "Comptes": len(resultat["comptes"]),
            "Instructeurs": len(resultat["instructeurs"]),
            "Session": str(resultat["session"]),
            "Brigade": str(resultat["brigade"]),
        }
        imprimer_compte_rendu(self.stdout, compteurs, chronometre)
