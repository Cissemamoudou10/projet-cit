"""Formulaire de création d'une évaluation — CU-P6-01, Prompt 35.

Aucune règle métier ici (.claude/rules/vues.md) : la cohérence type/
périmètre/date/séance est entièrement vérifiée par
`evaluations.services.evaluation.ServiceEvaluation.creer`. Ce formulaire ne
fait que capter la saisie et proposer des choix.
"""

from django import forms

from evaluations.models import TypeEvaluation
from organisation.models import Brigade, Session
from planification.selectors import instructeurs_qualifies_pour, lieux_pour_choix
from referentiel.models import ElementReferentiel
from ressources.models import CreneauType, Instructeur, Lieu

CLASSES_LISTE_DEROULANTE = (
    "h-controle w-full rounded border border-gris-trait bg-fond-bloc px-2.5 text-sm "
    "outline-none hover:border-marine-700 "
    "focus:border-marine-700 focus:ring-2 focus:ring-focus"
)

CLASSES_CHAMP_DATE = (
    "h-controle w-full rounded border border-gris-trait bg-fond-bloc px-2.5 text-sm "
    "tabular-nums outline-none hover:border-marine-700 "
    "focus:border-marine-700 focus:ring-2 focus:ring-focus"
)

CLASSES_ZONE_TEXTE = (
    "w-full resize-y rounded border border-gris-trait bg-fond-bloc px-2.5 py-2 "
    "text-sm leading-normal outline-none "
    "focus:border-marine-700 focus:ring-2 focus:ring-focus"
)

FORMAT_DATE = "%Y-%m-%d"


class FormulaireEvaluation(forms.Form):
    element_referentiel = forms.ModelChoiceField(
        queryset=ElementReferentiel.objects.select_related("formation", "matiere").order_by(
            "formation__intitule", "matiere__intitule"
        ),
        label="Module",
        widget=forms.Select(attrs={"class": CLASSES_LISTE_DEROULANTE}),
    )
    type = forms.ChoiceField(
        choices=TypeEvaluation.choices,
        label="Type",
        widget=forms.Select(attrs={"class": CLASSES_LISTE_DEROULANTE}),
    )
    session = forms.ModelChoiceField(
        queryset=Session.objects.select_related("formation").order_by("intitule"),
        required=False,
        label="Session (périmètre)",
        widget=forms.Select(attrs={"class": CLASSES_LISTE_DEROULANTE}),
    )
    brigade = forms.ModelChoiceField(
        queryset=Brigade.objects.select_related("session").order_by("designation"),
        required=False,
        label="Brigade (périmètre)",
        widget=forms.Select(attrs={"class": CLASSES_LISTE_DEROULANTE}),
    )
    date = forms.DateField(
        required=False,
        label="Date",
        widget=forms.DateInput(
            attrs={"type": "date", "class": CLASSES_CHAMP_DATE}, format=FORMAT_DATE
        ),
    )
    creneau_type = forms.ModelChoiceField(
        queryset=CreneauType.objects.filter(grille__active=True)
        .select_related("grille")
        .order_by("jour_semaine", "ordre"),
        required=False,
        label="Créneau (contrôle à venir)",
        widget=forms.Select(attrs={"class": CLASSES_LISTE_DEROULANTE}),
    )
    instructeur = forms.TypedChoiceField(
        choices=(),
        coerce=int,
        required=False,
        label="Instructeur (contrôle à venir)",
        widget=forms.Select(attrs={"class": CLASSES_LISTE_DEROULANTE}),
    )
    lieu = forms.TypedChoiceField(
        choices=(),
        coerce=int,
        required=False,
        label="Lieu (si requis par le module)",
        widget=forms.Select(attrs={"class": CLASSES_LISTE_DEROULANTE}),
    )
    motif_date_passee = forms.CharField(
        required=False,
        label="Motif (contrôle à une date déjà passée)",
        widget=forms.Textarea(attrs={"class": CLASSES_ZONE_TEXTE, "rows": 3}),
    )

    def __init__(self, *args, **kwargs):
        """A6 : les deux listes viennent d'un sélecteur de `planification`,
        jamais d'une requête directe sur `ressources` — voir la docstring
        de `instructeurs_qualifies_pour`."""
        super().__init__(*args, **kwargs)
        vide = [("", "—")]
        self.fields["instructeur"].choices = vide + instructeurs_qualifies_pour()
        self.fields["lieu"].choices = vide + lieux_pour_choix()

    def clean_instructeur(self):
        pk = self.cleaned_data.get("instructeur")
        return Instructeur.objects.filter(pk=pk).first() if pk else None

    def clean_lieu(self):
        pk = self.cleaned_data.get("lieu")
        return Lieu.objects.filter(pk=pk).first() if pk else None
