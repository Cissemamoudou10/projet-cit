from django.apps import AppConfig


class EvaluationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "evaluations"
    verbose_name = "Évaluations"

    def ready(self):
        from evaluations import selectors
        from evaluations.reinitialisation_demonstration_j2 import (
            vider_evaluations_demonstration_j2,
        )
        from noyau.services.parametres import (
            ResolveurJoursExamen,
            ResolveurOccupationsEpreuves,
            ResolveurReinitialisationEvaluations,
            ResolveurSeancesDeControle,
        )

        ResolveurSeancesDeControle.installer_fournisseur(selectors.seances_de_controle_parmi)
        ResolveurJoursExamen.installer_fournisseur(selectors.jours_d_examen)
        ResolveurOccupationsEpreuves.installer_fournisseur(selectors.occupations_epreuves)
        ResolveurReinitialisationEvaluations.installer_fournisseur(
            vider_evaluations_demonstration_j2
        )
