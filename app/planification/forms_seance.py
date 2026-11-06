"""Formulaire de modification d'une séance (US-PLAN-05, M3 et M9).

Validation de forme seulement : les contraintes, la garde et l'avenant sont
décidés par la porte (`ServiceEcritureSeance.modifier_seance`). La nature de
l'avenant n'a aucune valeur présélectionnée (M9) : le choix est humain.

K8, prompt 59 (RECETTE-01 A2) : le créneau se CHOISIT parmi ceux de la
grille active, jamais une heure libre — RG-64 amendée (D-310) : la grille
contraint désormais aussi la saisie manuelle, pas seulement ce que la
génération propose. Une heure libre acceptée en silence (ex. 14:45, hors
du créneau 14:40–16:00) produisait une séance ensuite invisible sur la
grille de consultation (`selectors_consultation.py`, qui ne visite que les
créneaux réels).
"""

import datetime

from django import forms
from django.utils import timezone

from organisation.models import Brigade
from planification.models import NatureAvenant
from planification.selectors import JOUR_SEMAINE_PAR_ISO, grille_active_avec_creneaux
from referentiel.models import ElementReferentiel
from ressources.models import Instructeur, Lieu

LIBELLES_JOUR = {1: "Lundi", 2: "Mardi", 3: "Mercredi", 4: "Jeudi", 5: "Vendredi", 6: "Samedi"}

CHOIX_NATURE = [("", "— choisir une nature —")] + list(NatureAvenant.choices)

# `.claude/rules/gabarits.md` : classes Tailwind reprises à l'identique de la
# charte (§ 3.17/3.20/3.22/3.23) — posées ici sur les widgets pour que
# `{{ champ }}` les porte sans reconstruction manuelle du HTML en gabarit
# (qui perdrait le format ISO que Django applique déjà à `type="date"`).
CLASSE_CHAMP = (
    "h-controle w-full rounded border border-gris-trait bg-fond-bloc px-2.5 text-sm "
    "outline-none hover:border-marine-700 focus:border-marine-700 focus:ring-2 focus:ring-focus"
)
CLASSE_CHAMP_HEURE = (
    "h-controle w-28 rounded border border-gris-trait bg-fond-bloc px-2.5 text-sm tabular-nums "
    "outline-none hover:border-marine-700 focus:border-marine-700 focus:ring-2 focus:ring-focus"
)
CLASSE_ZONE_TEXTE = (
    "w-full resize-y rounded border border-gris-trait bg-fond-bloc px-2.5 py-2 text-sm "
    "leading-normal outline-none focus:border-marine-700 focus:ring-2 focus:ring-focus"
)
CLASSE_CASE = "h-3.5 w-3.5 accent-marine-900"
CLASSE_CHAMP_MULTIPLE = (
    "w-full rounded border border-gris-trait bg-fond-bloc px-2.5 py-2 text-sm outline-none "
    "hover:border-marine-700 focus:border-marine-700 focus:ring-2 focus:ring-focus"
)


class ChampsAvenantMixin(forms.Form):
    """Les deux champs de l'avenant et leur validation croisée (motif exige
    une nature, nature exige un motif), partagés par tout formulaire qui
    peut porter un avenant — modification, ajout, association (M3, M9)."""

    nature_avenant = forms.ChoiceField(
        choices=CHOIX_NATURE,
        required=False,
        label="Nature de l'avenant",
        widget=forms.Select(attrs={"class": CLASSE_CHAMP}),
    )
    motif_avenant = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 2, "class": CLASSE_ZONE_TEXTE}),
        label="Motif de l'avenant",
    )

    def clean(self):
        donnees = super().clean()
        if donnees.get("motif_avenant", "").strip() and not donnees.get("nature_avenant"):
            self.add_error("nature_avenant", "Un avenant exige une nature.")
        if donnees.get("nature_avenant") and not donnees.get("motif_avenant", "").strip():
            self.add_error("motif_avenant", "Un avenant exige un motif.")
        return donnees

    def motif_et_nature_avenant(self):
        """(motif, nature) si un avenant est demandé, sinon None."""
        donnees = self.cleaned_data
        if not donnees.get("motif_avenant", "").strip():
            return None
        return donnees["motif_avenant"].strip(), donnees["nature_avenant"]


class FormulaireSeance(ChampsAvenantMixin, forms.Form):
    element_referentiel = forms.ModelChoiceField(
        queryset=ElementReferentiel.objects.select_related("matiere"),
        label="Matière",
        widget=forms.Select(attrs={"class": CLASSE_CHAMP}),
    )
    instructeur = forms.ModelChoiceField(
        queryset=Instructeur.objects.all(),
        label="Instructeur",
        widget=forms.Select(attrs={"class": CLASSE_CHAMP}),
    )
    lieu = forms.ModelChoiceField(
        queryset=Lieu.objects.all(),
        required=False,
        empty_label="Sans lieu",
        label="Lieu",
        widget=forms.Select(attrs={"class": CLASSE_CHAMP}),
    )
    creneau = forms.ChoiceField(
        label="Créneau",
        widget=forms.Select(attrs={"class": CLASSE_CHAMP}),
    )
    confirmee = forms.BooleanField(
        required=False,
        label="Je confirme la modification",
        widget=forms.CheckboxInput(attrs={"class": CLASSE_CASE}),
    )

    def __init__(self, *args, formation=None, programme=None, **kwargs):
        """`formation` (prompt 58, RECETTE-01 A3) : borne les matières
        proposées à celles de la formation de la brigade concernée, posée
        par l'appelant qui connaît déjà la séance (modification) — jamais
        « Électronique numérique » de F1 confondue avec celle de F6.
        `None` par défaut : `FormulaireAjoutSeance` choisit encore sa
        brigade DANS le formulaire, son filtrage reste différé (E1).

        `programme` (K8, prompt 59) : construit les choix de `creneau`, un
        par créneau de la grille active projeté sur la semaine DE CE
        programme — jamais `None` en usage réel, seulement dans les tests
        qui ne s'intéressent pas à ce champ."""
        super().__init__(*args, **kwargs)
        if formation is not None:
            self.fields["element_referentiel"].queryset = ElementReferentiel.objects.filter(
                formation=formation
            ).select_related("matiere")
        self._jours_et_creneaux_par_pk = {}
        if programme is not None:
            self.fields["creneau"].choices = self._choix_creneaux(programme)

    def _choix_creneaux(self, programme):
        _, creneaux = grille_active_avec_creneaux()
        choix = []
        for creneau in sorted(
            creneaux, key=lambda c: (JOUR_SEMAINE_PAR_ISO[c.jour_semaine], c.ordre)
        ):
            jour_iso = JOUR_SEMAINE_PAR_ISO[creneau.jour_semaine]
            jour = programme.lundi_de_semaine + datetime.timedelta(days=jour_iso - 1)
            pk = str(creneau.pk)
            self._jours_et_creneaux_par_pk[pk] = (jour, creneau)
            libelle = (
                f"{LIBELLES_JOUR[jour_iso]} {jour:%d/%m} — "
                f"{creneau.heure_debut:%H:%M}–{creneau.heure_fin:%H:%M}"
            )
            choix.append((pk, libelle))
        return choix

    def clean(self):
        donnees = super().clean()
        valeur = donnees.get("creneau")
        if valeur:
            resolu = self._jours_et_creneaux_par_pk.get(valeur)
            if resolu is None:
                self.add_error("creneau", "Créneau invalide.")
            else:
                jour, creneau = resolu
                donnees["debut_instant"] = self._instant(jour, creneau.heure_debut)
                donnees["fin_instant"] = self._instant(jour, creneau.heure_fin)
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


class FormulaireAjoutSeance(FormulaireSeance):
    """Ajout manuel (C4, prompt 42) : la brigade se choisit ici, elle n'a
    pas encore de ligne sur le programme."""

    brigade = forms.ModelChoiceField(
        queryset=Brigade.objects.all(),
        label="Brigade",
        widget=forms.Select(attrs={"class": CLASSE_CHAMP}),
    )


class FormulaireAssociationBrigades(ChampsAvenantMixin, forms.Form):
    """US-PLAN-06 (R1, R5) : brigades à associer à une séance en lieu
    partagé. Le queryset des candidates se pose à l'instanciation (bornées
    au créneau), jamais fixé sur la classe."""

    brigades = forms.ModelMultipleChoiceField(
        queryset=Brigade.objects.none(),
        label="Brigades à associer",
        widget=forms.SelectMultiple(attrs={"class": CLASSE_CHAMP_MULTIPLE, "size": 6}),
    )
    confirmee = forms.BooleanField(
        required=False,
        label="Je confirme l'association",
        widget=forms.CheckboxInput(attrs={"class": CLASSE_CASE}),
    )

    def __init__(self, *args, brigades_candidates=None, **kwargs):
        super().__init__(*args, **kwargs)
        if brigades_candidates is not None:
            self.fields["brigades"].queryset = brigades_candidates
