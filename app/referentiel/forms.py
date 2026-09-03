from django import forms

from noyau.forms import FormulaireGestion
from referentiel.models import TypeFormation

CLASSES_CHAMP_TEXTE = (
    "h-controle w-full rounded border border-gris-trait bg-fond-bloc px-2.5 text-sm "
    "text-encre outline-none hover:border-marine-700 "
    "focus:border-marine-700 focus:ring-2 focus:ring-focus"
)


class FormulaireTypeFormation(FormulaireGestion):
    class Meta:
        model = TypeFormation
        fields = ["intitule"]
        labels = {"intitule": "Intitulé"}
        widgets = {"intitule": forms.TextInput(attrs={"class": CLASSES_CHAMP_TEXTE})}
