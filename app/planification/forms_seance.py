"""Formulaire de modification d'une séance (US-PLAN-05, M3 et M9).

Validation de forme seulement : les contraintes, la garde et l'avenant sont
décidés par la porte (`ServiceEcritureSeance.modifier_seance`). La nature de
l'avenant n'a aucune valeur présélectionnée (M9) : le choix est humain.
"""

import datetime

from django import forms
from django.utils import timezone

from organisation.models import Brigade
from planification.models import NatureAvenant
from referentiel.models import ElementReferentiel
from ressources.models import Instructeur, Lieu

CHOIX_NATURE = [("", "— choisir une nature —")] + list(NatureAvenant.choices)


class FormulaireSeance(forms.Form):
    element_referentiel = forms.ModelChoiceField(
        queryset=ElementReferentiel.objects.select_related("matiere"), label="Matière"
    )
    instructeur = forms.ModelChoiceField(queryset=Instructeur.objects.all(), label="Instructeur")
    lieu = forms.ModelChoiceField(
        queryset=Lieu.objects.all(), required=False, empty_label="Sans lieu", label="Lieu"
    )
    date_seance = forms.DateField(label="Date", widget=forms.DateInput(attrs={"type": "date"}))
    heure_debut = forms.TimeField(label="Début", widget=forms.TimeInput(attrs={"type": "time"}))
    heure_fin = forms.TimeField(label="Fin", widget=forms.TimeInput(attrs={"type": "time"}))
    confirmee = forms.BooleanField(required=False, label="Je confirme la modification")
    nature_avenant = forms.ChoiceField(
        choices=CHOIX_NATURE, required=False, label="Nature de l'avenant"
    )
    motif_avenant = forms.CharField(
        required=False, widget=forms.Textarea(attrs={"rows": 2}), label="Motif de l'avenant"
    )

    def clean(self):
        donnees = super().clean()
        debut, fin = donnees.get("date_seance"), None
        if debut and donnees.get("heure_debut") and donnees.get("heure_fin"):
            fin = self._instant(debut, donnees["heure_fin"])
            donnees["debut_instant"] = self._instant(debut, donnees["heure_debut"])
            donnees["fin_instant"] = fin
            if fin <= donnees["debut_instant"]:
                raise forms.ValidationError("L'heure de fin doit suivre l'heure de début.")
        if donnees.get("motif_avenant", "").strip() and not donnees.get("nature_avenant"):
            self.add_error("nature_avenant", "Un avenant exige une nature.")
        if donnees.get("nature_avenant") and not donnees.get("motif_avenant", "").strip():
            self.add_error("motif_avenant", "Un avenant exige un motif.")
        return donnees

    @staticmethod
    def _instant(jour, heure):
        return timezone.make_aware(datetime.datetime.combine(jour, heure))

    def changements(self):
        """Nouvelles valeurs de la séance, depuis les données propres du formulaire."""
        donnees = self.cleaned_data
        return {
            "element_referentiel": donnees["element_referentiel"],
            "instructeur": donnees["instructeur"],
            "lieu": donnees.get("lieu"),
            "debut": donnees["debut_instant"],
            "fin": donnees["fin_instant"],
        }

    def motif_et_nature_avenant(self):
        """(motif, nature) si un avenant est demandé, sinon None."""
        donnees = self.cleaned_data
        if not donnees.get("motif_avenant", "").strip():
            return None
        return donnees["motif_avenant"].strip(), donnees["nature_avenant"]


class FormulaireAjoutSeance(FormulaireSeance):
    """Ajout manuel (C4, prompt 42) : la brigade se choisit ici, elle n'a
    pas encore de ligne sur le programme."""

    brigade = forms.ModelChoiceField(queryset=Brigade.objects.all(), label="Brigade")
