"""Formulaires de l'écran de génération — CU-P5-01, Prompt 31, § 9.

`forms.Form`, jamais `ModelForm` : la génération n'édite aucun modèle
directement, elle appelle `ServiceGeneration.generer` (.claude/rules/vues.md
— un contrôle en formulaire double un contrôle de service, il ne le
remplace jamais).
"""

import datetime

from django import forms

from organisation.models import Brigade

CLASSES_CHAMP_DATE = (
    "w-full border border-gris-trait bg-blanc px-2.5 py-1.5 text-sm text-encre "
    "focus:border-marine-700 focus:outline-none"
)
CLASSES_SELECTION_MULTIPLE = (
    "w-full border border-gris-trait bg-blanc px-2.5 py-1.5 text-sm text-encre "
    "focus:border-marine-700 focus:outline-none"
)


class FormulaireLancementGeneration(forms.Form):
    """`semaine` accepte n'importe quelle date de la semaine visée — normalisée
    au lundi (§ 2, Prompt 31), pour éviter d'exiger que l'agent pointe
    exactement un lundi sur le sélecteur."""

    semaine = forms.DateField(
        label="Semaine du",
        widget=forms.DateInput(attrs={"type": "date", "class": CLASSES_CHAMP_DATE}),
    )
    brigades = forms.ModelMultipleChoiceField(
        queryset=Brigade.objects.select_related("session").order_by(
            "session__intitule", "designation"
        ),
        label="Brigades — présentées par session",
        widget=forms.SelectMultiple(attrs={"class": CLASSES_SELECTION_MULTIPLE, "size": 10}),
    )
    confirme = forms.BooleanField(required=False, widget=forms.HiddenInput)

    def lundi_de_semaine(self):
        semaine = self.cleaned_data["semaine"]
        return semaine - datetime.timedelta(days=semaine.weekday())
