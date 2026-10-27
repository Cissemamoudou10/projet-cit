"""Calendrier du jeu volumineux — Prompt 51, Temps 3, § 3.1 : une année
(congés, conférences, bivouacs ciblés, semaines d'examen). Portée dérivée
(RG-30) : aucune cible = centre entier, une liste de brigades = ciblée —
jamais une session ciblée ici (le § 3.1 ne le demande pas pour ce jeu)."""

import dataclasses
import datetime

from django.utils import timezone

from ressources.models import NatureEvenement
from ressources.services.periode_calendrier import DonneesPeriode, ServicePeriodeCalendrier

NOMBRE_CONGES = 10
NOMBRE_CONFERENCES = 6
NOMBRE_BIVOUACS = 4
NOMBRE_SEMAINES_EXAMEN = 3


@dataclasses.dataclass(frozen=True)
class _PeriodeAPoser:
    nature_libelle: str
    intitule: str
    debut_jour: datetime.date
    duree_jours: int
    brigades: list


def _periode(agissant, a_poser: _PeriodeAPoser):
    debut = timezone.make_aware(datetime.datetime.combine(a_poser.debut_jour, datetime.time.min))
    fin = timezone.make_aware(
        datetime.datetime.combine(
            a_poser.debut_jour + datetime.timedelta(days=a_poser.duree_jours), datetime.time.min
        )
    )
    nature = NatureEvenement.objects.get(libelle=a_poser.nature_libelle)
    ServicePeriodeCalendrier.creer(
        agissant,
        DonneesPeriode(
            nature=nature, intitule=a_poser.intitule, debut=debut, fin=fin, effet="",
            sessions=[], brigades=a_poser.brigades,
        ),
    )


def charger_calendrier_volume(agissant, generateur, date_reference, brigades_actives, stdout):
    debut_annee = date_reference - datetime.timedelta(weeks=26)
    liste_brigades = list(brigades_actives.values())
    total = 0

    for indice in range(1, NOMBRE_CONGES + 1):
        jour = debut_annee + datetime.timedelta(weeks=indice * 4)
        _periode(agissant, _PeriodeAPoser("Congé", f"Congé volumineux {indice}", jour, 1, []))
        total += 1

    for indice in range(1, NOMBRE_CONFERENCES + 1):
        jour = debut_annee + datetime.timedelta(weeks=indice * 7)
        _periode(agissant, _PeriodeAPoser("Conférence", f"Conférence volumineuse {indice}", jour, 1, []))
        total += 1

    for indice in range(1, NOMBRE_BIVOUACS + 1):
        jour = debut_annee + datetime.timedelta(weeks=indice * 9 + 2)
        cibles = generateur.sample(liste_brigades, min(3, len(liste_brigades)))
        _periode(agissant, _PeriodeAPoser("Bivouac", f"Bivouac volumineux {indice}", jour, 3, cibles))
        total += 1

    for indice in range(1, NOMBRE_SEMAINES_EXAMEN + 1):
        jour = debut_annee + datetime.timedelta(weeks=indice * 15 + 5)
        _periode(agissant, _PeriodeAPoser("Examen", f"Semaine d'examen volumineuse {indice}", jour, 5, []))
        total += 1

    stdout.write(f"  {total} périodes de calendrier ajoutées (sur une année).")
