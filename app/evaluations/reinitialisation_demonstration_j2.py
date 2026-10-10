"""Fournisseur de `noyau.services.parametres.ResolveurReinitialisationEvaluations`
— Prompt 43, § A3. Vide les évaluations produites par le scénario de la
démonstration J2 (contrôle formatif, examen final) et tout ce qui en
dépend par cascade (`Sujet`, `OrganisationEpreuve`, `Surveillance`) — la
seule entité à vider ici, `Evaluation.seance` étant en `PROTECT`, c'est
`planification.jeu_demonstration_j2.reinitialisation` qui vide les séances
ensuite, dans l'ordre que ce `PROTECT` impose.
"""

from evaluations.models import Evaluation


def vider_evaluations_demonstration_j2():
    Evaluation.objects.all().delete()
