"""Formulaire de l'écran de duplication — US-PLAN-11, Story 4 (prompt 48).

`forms.Form`, jamais `ModelForm` : la duplication n'édite aucun modèle
directement, elle appelle `ServiceDuplication.dupliquer`
(`.claude/rules/vues.md` — un contrôle en formulaire double un contrôle de
service, il ne le remplace jamais).
"""

from django import forms

from organisation.models import Brigade
from organisation.services.session import ServiceSession
from planification.forms import CLASSES_CHAMP_DATE, FORMAT_DATE


class FormulaireDuplication(forms.Form):
    """`semaine_source`/`semaine_cible` acceptent n'importe quelle date de
    la semaine visée — normalisées au lundi par les vues, comme
    `FormulaireLancementGeneration`."""

    semaine_source = forms.DateField(
        label="Semaine source",
        input_formats=[FORMAT_DATE],
        widget=forms.DateInput(attrs={"type": "date", "class": CLASSES_CHAMP_DATE}, format=FORMAT_DATE),
    )
    semaine_cible = forms.DateField(
        label="Semaine cible",
        input_formats=[FORMAT_DATE],
        widget=forms.DateInput(attrs={"type": "date", "class": CLASSES_CHAMP_DATE}, format=FORMAT_DATE),
    )
    brigades = forms.ModelMultipleChoiceField(
        queryset=Brigade.objects.filter(
            session__in=ServiceSession.disponibles_pour_selection()
        ).select_related("session"),
        label="Brigades",
        widget=forms.CheckboxSelectMultiple,
    )
