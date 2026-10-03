"""Formulaires de l'organisation d'épreuve — US-EVAL-04, Prompt 38. Aucune règle
métier ici (.claude/rules/vues.md) : chaque règle est vérifiée par
`evaluations.services.organisation.ServiceOrganisationEpreuve`.
"""

from django import forms

from evaluations.forms import CLASSES_CHAMP_DATE, CLASSES_LISTE_DEROULANTE
from organisation.models import Brigade
from ressources.models import Instructeur, Lieu

CLASSE_CHAMP_TEXTE = CLASSES_LISTE_DEROULANTE
FORMAT_HEURE = "%H:%M"


class FormulaireCreneau(forms.Form):
    heure_debut = forms.TimeField(
        label="Heure de début",
        input_formats=[FORMAT_HEURE],
        widget=forms.TimeInput(
            format=FORMAT_HEURE, attrs={"type": "time", "class": CLASSES_CHAMP_DATE}
        ),
    )
    heure_fin = forms.TimeField(
        label="Heure de fin",
        input_formats=[FORMAT_HEURE],
        widget=forms.TimeInput(
            format=FORMAT_HEURE, attrs={"type": "time", "class": CLASSES_CHAMP_DATE}
        ),
    )


class FormulaireOrganisation(forms.Form):
    brigade = forms.ModelChoiceField(
        queryset=Brigade.objects.order_by("designation"),
        label="Brigade",
        widget=forms.Select(attrs={"class": CLASSE_CHAMP_TEXTE}),
    )
    lieu = forms.ModelChoiceField(
        queryset=Lieu.objects.filter(archive=False).order_by("intitule"),
        required=False,
        label="Lieu (vide pour une épreuve pratique)",
        widget=forms.Select(attrs={"class": CLASSE_CHAMP_TEXTE}),
    )
    effectif_attendu = forms.IntegerField(
        min_value=1,
        label="Effectif attendu sur ce lieu",
        widget=forms.NumberInput(attrs={"class": CLASSE_CHAMP_TEXTE}),
    )


class FormulaireSurveillant(forms.Form):
    """A8 : un sélecteur réduit au nom et au grade de TOUS les instructeurs non
    archivés (un surveillant n'a pas à être qualifié)."""

    instructeur = forms.ModelChoiceField(
        queryset=Instructeur.objects.filter(archive=False).order_by("nom", "prenom"),
        required=False,
        label="Instructeur référencé",
        widget=forms.Select(attrs={"class": CLASSE_CHAMP_TEXTE}),
    )
    nom_libre = forms.CharField(
        required=False,
        max_length=150,
        label="Ou personne extérieure (nom seul)",
        widget=forms.TextInput(attrs={"class": CLASSE_CHAMP_TEXTE}),
    )
