from django.apps import AppConfig


class RessourcesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ressources"
    verbose_name = "Ressources"

    def ready(self):
        """Installe `ressources` comme fournisseur du volume horaire
        hebdomadaire de référence (§ 7, Prompt 29) — point de câblage
        unique, voir `noyau.services.parametres`. Import différé,
        obligatoire ici : au chargement des applications, les modèles
        d'autres applications ne sont pas encore prêts."""
        from noyau.services.parametres import ResolveurVolumeHoraireReference
        from ressources.services.grille_horaire import ServiceGrilleHoraire

        ResolveurVolumeHoraireReference.installer_fournisseur(
            ServiceGrilleHoraire.volume_hebdomadaire_reference
        )
