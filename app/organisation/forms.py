from django import forms

from noyau.forms import FormulaireGestion
from organisation.models import Session
from referentiel.models import Formation
from referentiel.services.formation import ServiceFormation

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

CLASSES_CHAMP_DATE = (
    "h-controle w-full rounded border border-gris-trait bg-fond-bloc px-2.5 text-sm "
    "tabular-nums outline-none hover:border-marine-700 "
    "focus:border-marine-700 focus:ring-2 focus:ring-focus"
)

FORMAT_DATE = "%Y-%m-%d"


class FormulaireSession(FormulaireGestion):
    """Deux colonnes (§ 7, Prompt 20) : « Rattachement » — la formation —
    et « Période et effectif » — intitulé, dates, effectif attendu. `etat`
    et `date_cloture` sont absents à dessein : ni l'un ni l'autre n'est
    modifiable par ce formulaire (US-SES-09, sprint 4)."""

    class Meta:
        model = Session
        fields = ["formation", "intitule", "date_debut", "date_fin", "effectif_attendu"]
        labels = {
            "formation": "Formation",
            "intitule": "Intitulé",
            "date_debut": "Date de début",
            "date_fin": "Date de fin",
            "effectif_attendu": "Effectif attendu",
        }
        widgets = {
            "formation": forms.Select(attrs={"class": CLASSES_LISTE_DEROULANTE}),
            "intitule": forms.TextInput(attrs={"class": CLASSES_CHAMP_TEXTE}),
            "date_debut": forms.DateInput(
                attrs={"type": "date", "class": CLASSES_CHAMP_DATE}, format=FORMAT_DATE
            ),
            "date_fin": forms.DateInput(
                attrs={"type": "date", "class": CLASSES_CHAMP_DATE}, format=FORMAT_DATE
            ),
            "effectif_attendu": forms.NumberInput(
                attrs={
                    "class": CLASSES_CHAMP_UNITE,
                    "inputmode": "numeric",
                    "unite": "stagiaires",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        """§ 7 : le sélecteur exclut les formations archivées et celles au
        référentiel vide — confort d'interface, PAS le contrôle : le
        service (`ServiceSession._verifier_formation`) refuse indépendamment,
        les tests le vérifient en court-circuitant ce formulaire."""
        super().__init__(*args, **kwargs)
        disponibles = ServiceFormation.disponibles_pour_selection().filter(
            elements_referentiel__isnull=False
        )
        if self.instance.pk and self.instance.formation_id:
            disponibles = disponibles | Formation.objects.filter(pk=self.instance.formation_id)
        self.fields["formation"].queryset = disponibles.distinct().order_by("intitule")


class FormulaireBrigade(forms.Form):
    """`forms.Form`, pas `ModelForm` : `session` vient de l'URL, jamais de la
    saisie — même patron que `FormulaireRattachementMatiere` (US-SES-02,
    étape 0.2), la brigade étant une sous-ressource composée depuis l'écran
    de la session, pas une entité de gestion autonome."""

    designation = forms.CharField(
        label="Désignation",
        max_length=50,
        widget=forms.TextInput(attrs={"class": CLASSES_CHAMP_TEXTE}),
    )
    effectif_previsionnel = forms.IntegerField(
        label="Effectif prévisionnel",
        min_value=1,
        widget=forms.NumberInput(attrs={"class": CLASSES_CHAMP_UNITE, "inputmode": "numeric"}),
    )
