"""Formulaire de la signature du programme (US-VAL-04, C2).

La date et le nom sont validés ici pour leur forme seulement ; la règle (date
comprise entre la validation et aujourd'hui, nom non vide) reste au moteur.
"""

from django import forms


class FormulaireSignature(forms.Form):
    date_signature = forms.DateField(
        label="Date de signature",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    signataire = forms.CharField(label="Nom du signataire", max_length=150)
