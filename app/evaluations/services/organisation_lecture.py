"""Lecture de l'organisation d'épreuve — complétude (A4), « prête » (C10), synthèse
pour l'écran et la convocation (A11). Calculé, jamais stocké. Prompt 38.
"""

from evaluations.models import OrganisationEpreuve
from evaluations.services.conflits import conflits_de_l_epreuve
from evaluations.services.evaluation import Perimetre
from evaluations.services.sujet import ServiceSujet
from organisation.selectors import effectifs_reels


def _perimetre(evaluation):
    return Perimetre(
        element=evaluation.element_referentiel,
        session=evaluation.session,
        brigade=evaluation.brigade,
    )


class LectureOrganisationEpreuve:
    DOMAINE = "evaluations"

    @staticmethod
    def incompletudes(evaluation) -> list:
        """A4 : ce qui manque à l'organisation. Calculé, jamais stocké."""
        if evaluation.heure_debut is None:
            return ["le créneau n'est pas fixé"]
        perimetre = _perimetre(evaluation)
        brigades = perimetre.brigades_visees
        organisations = list(
            OrganisationEpreuve.objects.filter(evaluation=evaluation).values(
                "pk", "brigade_id", "effectif_attendu"
            )
        )
        sans_surveillant = set(
            OrganisationEpreuve.objects.filter(
                evaluation=evaluation, surveillances__isnull=True
            ).values_list("pk", flat=True)
        )
        reels = effectifs_reels([brigade.pk for brigade in brigades])
        manques = []
        for brigade in brigades:
            attendus = [o for o in organisations if o["brigade_id"] == brigade.pk]
            if not attendus:
                manques.append(f"« {brigade} » n'a pas d'organisation")
            elif sum(o["effectif_attendu"] for o in attendus) != reels[brigade.pk]:
                manques.append(
                    f"« {brigade} » : effectifs répartis ≠ effectif réel ({reels[brigade.pk]})"
                )
        if any(o["pk"] in sans_surveillant for o in organisations):
            manques.append("une organisation n'a aucun surveillant")
        if conflits_de_l_epreuve(evaluation):
            manques.append("des conflits restent à lever")
        return manques

    @staticmethod
    def organisations_convocation(evaluation) -> list:
        """A11 : organisations et surveillants pour la convocation. N'appelle
        aucun service de sujet : ni `sujet_retenu`, ni `est_prete`."""
        return list(
            OrganisationEpreuve.objects.filter(evaluation=evaluation)
            .select_related("brigade", "lieu")
            .prefetch_related("surveillances__instructeur")
            .order_by("brigade__designation", "pk")
        )

    @staticmethod
    def synthese(evaluation) -> dict:
        """Lecture de l'écran d'organisation : organisations, complétude, « prête »."""
        incompletudes = LectureOrganisationEpreuve.incompletudes(evaluation)
        return {
            "organisations": LectureOrganisationEpreuve.organisations_convocation(evaluation),
            "incompletudes": incompletudes,
            "prete": not incompletudes and ServiceSujet.sujet_retenu(evaluation) is not None,
        }

    @staticmethod
    def est_complete(evaluation) -> bool:
        return not LectureOrganisationEpreuve.incompletudes(evaluation)

    @staticmethod
    def est_prete(evaluation) -> bool:
        """C10 / A1 : complète ET sujet retenu (`sujet_retenu`, garde booléenne)."""
        return (
            LectureOrganisationEpreuve.est_complete(evaluation)
            and ServiceSujet.sujet_retenu(evaluation) is not None
        )
