from django import forms

from noyau.forms import FormulaireGestion
from referentiel.models import CategorieLieu, Formation, Matiere, TypeFormation, TypeLieuPartage
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


class FormulaireMatiere(FormulaireGestion):
    class Meta:
        model = Matiere
        fields = ["intitule", "code"]
        labels = {"intitule": "Intitulé", "code": "Code"}
        widgets = {
            "intitule": forms.TextInput(attrs={"class": CLASSES_CHAMP_TEXTE}),
            "code": forms.TextInput(attrs={"class": CLASSES_CHAMP_TEXTE}),
        }


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


class FormulaireRattachementMatiere(forms.Form):
    """A2/E1 non couverts ici : ce formulaire ne fait que saisir, la
    cohérence catégorie/type de lieu et le doublon (E1) sont tranchés par
    `ServiceReferentiel`, seul juge — voir .claude/rules/vues.md.
    """

    matiere = forms.ModelChoiceField(
        queryset=Matiere.objects.none(),
        label="Matière",
        widget=forms.Select(attrs={"class": CLASSES_LISTE_DEROULANTE}),
    )
    volume_horaire_prescrit = forms.IntegerField(
        label="Volume horaire prescrit",
        min_value=1,
        widget=forms.NumberInput(attrs={"class": CLASSES_CHAMP_UNITE, "inputmode": "numeric"}),
    )
    categorie_lieu = forms.ChoiceField(
        choices=CategorieLieu.choices,
        label="Catégorie de lieu",
        widget=forms.Select(attrs={"class": CLASSES_LISTE_DEROULANTE}),
    )
    type_lieu_partage = forms.ChoiceField(
        choices=TypeLieuPartage.choices,
        label="Type de lieu partagé",
        required=False,
        widget=forms.Select(attrs={"class": CLASSES_LISTE_DEROULANTE}),
    )

    def __init__(self, *args, matieres_disponibles, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["matiere"].queryset = matieres_disponibles.order_by("intitule")


class FormulaireElementReferentiel(forms.Form):
    """A2 : modification en place d'un rattachement existant — mêmes trois
    champs que le rattachement, sans la matière, qui ne change jamais.
    """

    volume_horaire_prescrit = forms.IntegerField(
        label="Volume horaire prescrit",
        min_value=1,
        widget=forms.NumberInput(attrs={"class": CLASSES_CHAMP_UNITE, "inputmode": "numeric"}),
    )
    categorie_lieu = forms.ChoiceField(
        choices=CategorieLieu.choices,
        label="Catégorie de lieu",
        widget=forms.Select(attrs={"class": CLASSES_LISTE_DEROULANTE}),
    )
    type_lieu_partage = forms.ChoiceField(
        choices=TypeLieuPartage.choices,
        label="Type de lieu partagé",
        required=False,
        widget=forms.Select(attrs={"class": CLASSES_LISTE_DEROULANTE}),
    )
