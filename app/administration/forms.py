"""Validation de forme uniquement — aucune règle métier. La comparaison des
identifiants vit dans `ServiceAuthentification` ; le gabarit rend les champs
à la main (docs/charte, § 3.17), les classes n'ont pas besoin de vivre ici.
"""

from django import forms

from administration.models import Profil


class FormulaireConnexion(forms.Form):
    identifiant = forms.CharField(max_length=150, label="Identifiant")
    mot_de_passe = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")


class FormulaireCompte(forms.Form):
    identifiant = forms.CharField(max_length=150, label="Identifiant")
    grade = forms.CharField(max_length=50, label="Grade")
    prenom = forms.CharField(max_length=150, label="Prénom", required=False)
    nom = forms.CharField(max_length=150, label="Nom")
    profil = forms.ChoiceField(choices=Profil.choices, label="Profil")


class FormulaireCreationCompte(FormulaireCompte):
    mot_de_passe = forms.CharField(widget=forms.PasswordInput, label="Mot de passe initial")


class FormulaireChangementMotDePasse(forms.Form):
    ancien_mot_de_passe = forms.CharField(widget=forms.PasswordInput, label="Ancien mot de passe")
    nouveau_mot_de_passe = forms.CharField(widget=forms.PasswordInput, label="Nouveau mot de passe")
    confirmation = forms.CharField(widget=forms.PasswordInput, label="Confirmation")

    def clean(self):
        nettoyees = super().clean()
        nouveau = nettoyees.get("nouveau_mot_de_passe")
        confirmation = nettoyees.get("confirmation")
        if nouveau and confirmation and nouveau != confirmation:
            self.add_error(
                "confirmation", "La confirmation ne correspond pas au nouveau mot de passe."
            )
        return nettoyees
