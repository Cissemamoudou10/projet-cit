"""Dates relatives à une date de référence `D` — Prompt 51, règle commune
n° 3. `W0` est le lundi de la semaine qui contient `D` ; `W-1`, `W+1`, etc. se
comptent en semaines entières à partir de ce lundi. Jamais de dépendance à
`timezone.now()` ici : `D` est toujours un paramètre explicite, passé par
l'appelant (l'horloge simulée en dépend, voir `horloge.py`)."""

import datetime


def lundi_de_semaine(date_reference: datetime.date) -> datetime.date:
    return date_reference - datetime.timedelta(days=date_reference.weekday())


def semaine(date_reference: datetime.date, decalage: int) -> datetime.date:
    """Lundi de `W{decalage}` par rapport à `D` (`decalage=0` -> W0)."""
    return lundi_de_semaine(date_reference) + datetime.timedelta(weeks=decalage)


def jour_de_semaine(date_reference: datetime.date, decalage: int, jour_iso: int) -> datetime.date:
    """`jour_iso` : 1 = lundi … 7 = dimanche, au sens `datetime.date.isoweekday()`."""
    return semaine(date_reference, decalage) + datetime.timedelta(days=jour_iso - 1)
