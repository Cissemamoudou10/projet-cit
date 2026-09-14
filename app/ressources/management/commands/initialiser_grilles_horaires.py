"""Commande d'administration : crée les deux grilles horaires relevées sur
le terrain (US-PLAN-12, § 6, Prompt 29) — catalogue de RÉFÉRENCE, même
précédent qu'`initialiser_natures_evenement` (US-PLAN-01) et
`initialiser_habilitations` (`administration`), jamais une migration de
données (P-37, docs/suivi/PROBLEMES.md).

SEULEMENT DEUX GRILLES CONNUES à ce jour — rien n'affirme qu'il n'en existe
pas d'autres (horaire d'été, période d'examens) : question de terrain
ouverte, voir docs/suivi/AVANCEMENT.md. Une troisième grille se crée depuis
l'écran, sans toucher au code — c'est l'objet même de cette story.

Durées INÉGALES, pauses IRRÉGULIÈRES : aucune arithmétique ne les engendre,
elles viennent du terrain telles quelles, jamais arrondies.

Idempotente : une grille déjà présente (par intitulé) n'est ni recréée ni
modifiée. La grille ordinaire est activée UNE SEULE FOIS, à la création
initiale du jeu de données — un ré-appel de la commande ne réactive rien si
l'agent a depuis activé une autre grille lui-même.
"""

import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from noyau.services.base import ServiceBase
from ressources.models import CreneauType, GrilleHoraire, JourSemaine

JOURS_OUVRES = [
    JourSemaine.LUNDI,
    JourSemaine.MARDI,
    JourSemaine.MERCREDI,
    JourSemaine.JEUDI,
    JourSemaine.VENDREDI,
]

GRILLES_INITIALES = {
    "Ordinaire": [
        (datetime.time(8, 0), datetime.time(9, 45)),
        (datetime.time(10, 10), datetime.time(12, 0)),
        (datetime.time(13, 0), datetime.time(14, 15)),
        (datetime.time(14, 40), datetime.time(16, 0)),
    ],
    "Ramadan": [
        (datetime.time(8, 30), datetime.time(9, 50)),
        (datetime.time(10, 0), datetime.time(11, 20)),
        (datetime.time(11, 30), datetime.time(12, 50)),
        (datetime.time(13, 10), datetime.time(14, 30)),
    ],
}

GRILLE_ACTIVEE_PAR_DEFAUT = "Ordinaire"


class Command(BaseCommand):
    help = "Crée les deux grilles horaires relevées sur le terrain (critère 1, US-PLAN-12)."

    def handle(self, *args, **options):
        agent = self._agent_systeme()
        if agent is None:
            raise CommandError(
                "Aucun compte administrateur trouvé : créez le premier compte "
                "(INSTALLATION.md, § 9) avant d'exécuter cette commande — la grille "
                "ordinaire est activée à la création, et RG-63 exige un agent nommé."
            )
        for intitule, creneaux in GRILLES_INITIALES.items():
            self._charger_grille(agent, intitule, creneaux)

    @staticmethod
    def _agent_systeme():
        from django.contrib.auth import get_user_model

        return get_user_model().objects.filter(is_superuser=True).order_by("pk").first()

    def _charger_grille(self, agent, intitule, creneaux):
        if GrilleHoraire.objects.filter(intitule__iexact=intitule).exists():
            self.stdout.write(f"{intitule} : déjà présente, non modifiée.")
            return
        with transaction.atomic():
            grille = GrilleHoraire(intitule=intitule)
            ServiceBase.creer(grille, agent)
            for jour in JOURS_OUVRES:
                for ordre, (heure_debut, heure_fin) in enumerate(creneaux, start=1):
                    CreneauType.objects.create(
                        grille=grille,
                        jour_semaine=jour,
                        ordre=ordre,
                        heure_debut=heure_debut,
                        heure_fin=heure_fin,
                        cree_par=agent,
                        modifie_par=agent,
                    )
            if intitule == GRILLE_ACTIVEE_PAR_DEFAUT:
                from django.utils import timezone

                grille.active = True
                grille.date_activation = timezone.now()
                grille.activee_par = agent
                ServiceBase.modifier(grille, agent)
        self.stdout.write(self.style.SUCCESS(f"Grille créée : {intitule}"))
