"""Formulaires de l'écran de génération — CU-P5-01, Prompt 31, § 9.

`forms.Form`, jamais `ModelForm` : la génération n'édite aucun modèle
directement, elle appelle `ServiceGeneration.generer` (.claude/rules/vues.md
— un contrôle en formulaire double un contrôle de service, il ne le
remplace jamais).
"""

import datetime

from django import forms

from organisation.models import Brigade
from organisation.services.session import ServiceSession

CLASSES_CHAMP_DATE = (
    "w-full border border-gris-trait bg-blanc px-2.5 py-1.5 text-sm text-encre "
    "focus:border-marine-700 focus:outline-none"
)
FORMAT_DATE = "%Y-%m-%d"


def _champ_semaine():
    """`format=` explicite : `LANGUAGE_CODE = "fr-fr"` (§ settings) fait
    sinon rendre la valeur au format local (jj/mm/aaaa), qu'un `<input
    type="date">` HTML5 refuse silencieusement — champ vide à l'affichage
    malgré une valeur initiale posée. Même piège, même remède qu'à
    `FormulaireDeclarationPeriodeCalendrier` (`ressources.forms`)."""
    return forms.DateField(
        label="Semaine du",
        input_formats=[FORMAT_DATE],
        widget=forms.DateInput(
            attrs={"type": "date", "class": CLASSES_CHAMP_DATE}, format=FORMAT_DATE
        ),
    )


class FormulaireSemaine(forms.Form):
    """Sous-formulaire GET, isolé : changer de semaine ne doit jamais valoir
    soumission de la sélection de brigades (deux intentions, deux formulaires,
    § 9 — l'agent doit voir l'état de la semaine AVANT de choisir)."""

    semaine = _champ_semaine()

    def lundi_de_semaine(self):
        semaine = self.cleaned_data["semaine"]
        return semaine - datetime.timedelta(days=semaine.weekday())


class FormulaireLancementGeneration(forms.Form):
    """`semaine` accepte n'importe quelle date de la semaine visée — normalisée
    au lundi (§ 2, Prompt 31), pour éviter d'exiger que l'agent pointe
    exactement un lundi sur le sélecteur. `brigades` est rendu à la main
    dans le gabarit — checkbox par brigade, groupées par session avec l'état
    de leurs séances déjà à l'écran (§ 9, critère 1) — le widget déclaré ici
    ne sert qu'à la validation, jamais à l'affichage."""

    semaine = _champ_semaine()
    brigades = forms.ModelMultipleChoiceField(
        # US-SES-09, C3 : confort d'écran seulement — ServiceGeneration.generer
        # refuse aussi, au niveau service, toute brigade d'une session clôturée.
        queryset=Brigade.objects.filter(
            session__in=ServiceSession.disponibles_pour_selection()
        ).select_related("session"),
        label="Brigades",
        widget=forms.CheckboxSelectMultiple,
    )
    confirme = forms.BooleanField(required=False, widget=forms.HiddenInput)

    def lundi_de_semaine(self):
        semaine = self.cleaned_data["semaine"]
        return semaine - datetime.timedelta(days=semaine.weekday())
