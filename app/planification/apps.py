from django.apps import AppConfig


class PlanificationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "planification"
    verbose_name = "Planification"

    def ready(self):
        from noyau.services.parametres import (
            ResolveurSeancesFuturesQualification,
            ResolveurVolumeRealiseBrigade,
        )
        from planification.selectors import seances_futures_qualification
        from planification.selectors_suivi import volume_realise_total_brigade

        ResolveurSeancesFuturesQualification.installer_fournisseur(seances_futures_qualification)
        ResolveurVolumeRealiseBrigade.installer_fournisseur(volume_realise_total_brigade)
