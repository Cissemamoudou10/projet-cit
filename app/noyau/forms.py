"""Formulaire de base du patron de gestion — Prompt 05, § 2.1.

`ModelForm.is_valid()` valide par défaut les contraintes du modèle
(`Meta.constraints`) pendant son propre `full_clean()` interne, avant que le
service n'ait la main. Le message d'unicité (E2, § 5) doit pourtant remonter
de la contrainte en base au moment de l'écriture, pas d'un contrôle
préalable dans le formulaire — vérifié réellement : sans ce correctif,
`form.is_valid()` intercepte la violation en premier et affiche le message
générique de Django (« La contrainte « … » n'est pas respectée »), jamais
celui construit par `noyau.services.gestion.ServiceGestion._erreur_unicite`,
qui désigne l'élément existant.

`_post_clean` ci-dessous reproduit `ModelForm._post_clean` (Django,
`django/forms/models.py`) à l'identique, à un seul paramètre près
(`validate_constraints=False`) : la construction de l'instance depuis les
données nettoyées (`construct_instance`) doit rester faite, sans quoi
`full_clean` validerait une instance encore vierge.
"""

from django import forms
from django.core.exceptions import ValidationError as ErreurValidationDjango
from django.forms.models import InlineForeignKeyField, construct_instance


class FormulaireGestion(forms.ModelForm):
    def _post_clean(self):
        options = self._meta
        exclude = self._get_validation_exclusions()
        for nom, champ in self.fields.items():
            if isinstance(champ, InlineForeignKeyField):
                exclude.add(nom)

        try:
            self.instance = construct_instance(self, self.instance, options.fields, options.exclude)
        except ErreurValidationDjango as erreur:
            self._update_errors(erreur)

        try:
            self.instance.full_clean(
                exclude=exclude, validate_unique=False, validate_constraints=False
            )
        except ErreurValidationDjango as erreur:
            self._update_errors(erreur)

        if self._validate_unique:
            self.validate_unique()
