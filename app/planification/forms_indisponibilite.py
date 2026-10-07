"""Formulaires du traitement d'une indisponibilité déclarée — US-PLAN-09
(prompt 42, partie 3).

Validation de forme seulement : la garde, les contraintes et l'avenant
restent décidés par la porte (`ServiceEcritureSeance`), comme pour
`forms_seance.py`. Les candidats (remplaçant, matière) viennent toujours
d'un sélecteur posé à l'instanciation, jamais d'un queryset fixé sur la
classe (même principe que `FormulaireAssociationBrigades`).
"""

from django import forms

from planification.forms_seance import ChampsAvenantMixin
from planification.models import Seance
from referentiel.models import ElementReferentiel
from ressources.models import Instructeur


class FormulaireRemplacementInstructeur(ChampsAvenantMixin, forms.Form):
    """I1, C2, C3 : remplace l'instructeur de la séance — `instructeur` est
    borné à la liste des remplaçants (I4), posée à l'instanciation."""

    instructeur = forms.ModelChoiceField(
        queryset=Instructeur.objects.none(), label="Nouvel instructeur"
    )
    confirmee = forms.BooleanField(required=False, label="Je confirme le remplacement")

    def __init__(self, *args, remplacants=None, **kwargs):
        super().__init__(*args, **kwargs)
        if remplacants is not None:
            self.fields["instructeur"].queryset = remplacants


class FormulaireSubstitutionSeance(ChampsAvenantMixin, forms.Form):
    """I1, C2, C4 : place une autre matière du référentiel sur la séance,
    avec un autre instructeur si besoin (RG-35/RG-36 restent seules juges
    de la qualification et de la disponibilité, via `ServiceContraintes`)."""

    element_referentiel = forms.ModelChoiceField(
        queryset=ElementReferentiel.objects.select_related("matiere"), label="Nouvelle matière"
    )
    instructeur = forms.ModelChoiceField(
        queryset=Instructeur.objects.filter(archive=False),
        required=False,
        label="Nouvel instructeur (si besoin)",
    )
    confirmee = forms.BooleanField(required=False, label="Je confirme la substitution")

    def changements(self):
        changements = {"element_referentiel": self.cleaned_data["element_referentiel"]}
        if self.cleaned_data.get("instructeur"):
            changements["instructeur"] = self.cleaned_data["instructeur"]
        return changements


class FormulaireLotRemplacement(ChampsAvenantMixin, forms.Form):
    """I5, C5 : même remplaçant pour toutes les séances du lot choisies à
    l'écran (de la même matière) — confirmation globale, distincte de la
    confirmation par séance."""

    seances = forms.ModelMultipleChoiceField(queryset=Seance.objects.none(), label="Séances")
    instructeur = forms.ModelChoiceField(
        queryset=Instructeur.objects.none(), label="Nouvel instructeur"
    )
    confirmee = forms.BooleanField(required=False, label="Je confirme le remplacement en lot")

    def __init__(self, *args, seances_candidates=None, remplacants=None, **kwargs):
        super().__init__(*args, **kwargs)
        if seances_candidates is not None:
            self.fields["seances"].queryset = seances_candidates
        if remplacants is not None:
            self.fields["instructeur"].queryset = remplacants
