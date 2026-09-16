from django.apps import AppConfig


class PlanificationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "planification"
    verbose_name = "Planification"

    def ready(self):
        from noyau.services.parametres import ResolveurSeancesFuturesQualification
        from planification.selectors import seances_futures_qualification

        ResolveurSeancesFuturesQualification.installer_fournisseur(seances_futures_qualification)
