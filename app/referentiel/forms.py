from django import forms

from noyau.forms import FormulaireGestion
from referentiel.models import Formation, TypeFormation
from referentiel.services.type_formation import ServiceTypeFormation

CLASSES_CHAMP_TEXTE = (
    "h-controle w-full rounded border border-gris-trait bg-fond-bloc px-2.5 text-sm "
    "text-encre outline-none hover:border-marine-700 "
    "focus:border-marine-700 focus:ring-2 focus:ring-focus"
)

CLASSES_LISTE_DEROULANTE = (
    "h-controle w-full rounded border border-gris-trait bg-fond-bloc px-2.5 text-sm "
    "outline-none hover:border-marine-700 "
    "focus:border-marine-700 focus:ring-2 focus:ring-focus"
)

CLASSES_CHAMP_UNITE = (
    "h-[30px] w-full border-0 bg-transparent px-2.5 text-right text-sm tabular-nums outline-none"
)


class FormulaireTypeFormation(FormulaireGestion):
    class Meta:
        model = TypeFormation
        fields = ["intitule"]
        labels = {"intitule": "Intitulé"}
        widgets = {"intitule": forms.TextInput(attrs={"class": CLASSES_CHAMP_TEXTE})}


class FormulaireFormation(FormulaireGestion):
    class Meta:
        model = Formation
        fields = ["intitule", "specialite", "type_formation", "duree_semaines"]
        labels = {
            "intitule": "Intitulé",
            "specialite": "Spécialité",
            "type_formation": "Type de formation",
            "duree_semaines": "Durée",
        }
        widgets = {
            "intitule": forms.TextInput(attrs={"class": CLASSES_CHAMP_TEXTE}),
            "specialite": forms.TextInput(attrs={"class": CLASSES_CHAMP_TEXTE}),
            "type_formation": forms.Select(attrs={"class": CLASSES_LISTE_DEROULANTE}),
            "duree_semaines": forms.NumberInput(
                attrs={"class": CLASSES_CHAMP_UNITE, "inputmode": "numeric"}
            ),
        }

    def __init__(self, *args, **kwargs):
        """§ 7 : la liste déroulante n'offre que les types non archivés — le
        type déjà rattaché reste proposé en modification, même archivé
        depuis, sans quoi la formation deviendrait invalidable sans y
        toucher.
        """
        super().__init__(*args, **kwargs)
        disponibles = ServiceTypeFormation.disponibles_pour_selection()
        if self.instance.pk and self.instance.type_formation_id:
            disponibles = disponibles | TypeFormation.objects.filter(
                pk=self.instance.type_formation_id
            )
        self.fields["type_formation"].queryset = disponibles.order_by("intitule")
