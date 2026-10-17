"""Valeurs de domaine de l'application `evaluations`."""

# US-EVAL-06, N6 : les deux valeurs admises pour `settings.TRAITEMENT_ABSENCE_NOTE`
# (BNF-13). Nommées ici plutôt qu'en chaînes littérales dans le service.
TRAITEMENT_ABSENCE_ZERO = "zero"
TRAITEMENT_ABSENCE_EXCLUSION = "exclusion"
TRAITEMENTS_ABSENCE_VALIDES = {TRAITEMENT_ABSENCE_ZERO, TRAITEMENT_ABSENCE_EXCLUSION}
