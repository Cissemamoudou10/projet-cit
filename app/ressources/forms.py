from django import forms

from noyau.forms import FormulaireGestion
from ressources.models import Instructeur

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


class FormulaireInstructeur(FormulaireGestion):
    """Deux colonnes (§ 3.24) : Identité — nom, prénom, matricule, grade —
    et Rattachement — spécialité, statut. Le regroupement se fait au
    gabarit ; le formulaire ne porte que les champs.
    """

    class Meta:
        model = Instructeur
        fields = ["nom", "prenom", "matricule", "grade", "specialite", "statut"]
        labels = {
            "nom": "Nom",
            "prenom": "Prénom",
            "matricule": "Matricule",
            "grade": "Grade",
            "specialite": "Spécialité",
            "statut": "Statut",
        }
        widgets = {
            "nom": forms.TextInput(attrs={"class": CLASSES_CHAMP_TEXTE}),
            "prenom": forms.TextInput(attrs={"class": CLASSES_CHAMP_TEXTE}),
            "matricule": forms.TextInput(attrs={"class": CLASSES_CHAMP_TEXTE + " font-mono"}),
            "grade": forms.TextInput(attrs={"class": CLASSES_CHAMP_TEXTE}),
            "specialite": forms.TextInput(attrs={"class": CLASSES_CHAMP_TEXTE}),
            "statut": forms.Select(attrs={"class": CLASSES_LISTE_DEROULANTE}),
        }
