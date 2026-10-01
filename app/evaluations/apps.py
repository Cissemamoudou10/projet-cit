from django.apps import AppConfig


class EvaluationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "evaluations"
    verbose_name = "Évaluations"

    def ready(self):
        from evaluations import selectors
        from noyau.services.parametres import ResolveurSeancesDeControle

        ResolveurSeancesDeControle.installer_fournisseur(selectors.seances_de_controle_parmi)
