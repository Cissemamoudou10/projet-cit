from django import forms

from noyau.forms import FormulaireGestion
from ressources.models import Instructeur, Lieu

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

CLASSES_CHAMP_DATETIME = (
    "h-controle w-full rounded border border-gris-trait bg-fond-bloc px-2.5 text-sm "
    "tabular-nums outline-none hover:border-marine-700 "
    "focus:border-marine-700 focus:ring-2 focus:ring-focus"
)

CLASSES_ZONE_TEXTE = (
    "w-full resize-y rounded border border-gris-trait bg-fond-bloc px-2.5 py-2 "
    "text-sm leading-normal outline-none "
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


class FormulaireLieu(FormulaireGestion):
    """Deux colonnes (§ 3.24) : Identification — intitulé, capacité — et
    Nature — catégorie, type. Les deux champs de Nature restent toujours
    visibles, patron déjà retenu à US-REF-03/04 pour la même paire
    catégorie/type (arbitrage § 8 du Prompt 14) : la cohérence est tranchée
    en service et par la contrainte en base, jamais masquée côté client.
    """

    class Meta:
        model = Lieu
        fields = ["intitule", "capacite", "categorie", "type_partage"]
        labels = {
            "intitule": "Intitulé",
            "capacite": "Capacité",
            "categorie": "Catégorie",
            "type_partage": "Type de lieu partagé",
        }
        widgets = {
            "intitule": forms.TextInput(attrs={"class": CLASSES_CHAMP_TEXTE}),
            "capacite": forms.NumberInput(
                attrs={"class": CLASSES_CHAMP_UNITE, "inputmode": "numeric", "unite": "places"}
            ),
            "categorie": forms.Select(attrs={"class": CLASSES_LISTE_DEROULANTE}),
            "type_partage": forms.Select(attrs={"class": CLASSES_LISTE_DEROULANTE}),
        }


class FormulaireDeclarationIndisponibilite(forms.Form):
    """Déclaration d'une période d'indisponibilité (§ 8 du Prompt 14) —
    `forms.Form` et non `ModelForm` : `lieu` vient de l'URL, jamais de la
    saisie, et le service `ServiceIndisponibiliteLieu.declarer` reçoit des
    valeurs, pas une instance — même patron que `FormulaireRattachementMatiere`.
    """

    FORMAT_DATE_HEURE = "%Y-%m-%dT%H:%M"

    debut = forms.DateTimeField(
        label="Début",
        input_formats=[FORMAT_DATE_HEURE],
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": CLASSES_CHAMP_DATETIME},
            format=FORMAT_DATE_HEURE,
        ),
    )
    fin = forms.DateTimeField(
        label="Fin",
        input_formats=[FORMAT_DATE_HEURE],
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": CLASSES_CHAMP_DATETIME},
            format=FORMAT_DATE_HEURE,
        ),
    )
    motif = forms.CharField(
        label="Motif",
        widget=forms.Textarea(attrs={"class": CLASSES_ZONE_TEXTE, "rows": 4, "maxlength": 500}),
    )


class ChampSalleAttitrable(forms.ModelChoiceField):
    """N'affiche jamais silencieusement une salle de capacité insuffisante
    (§ 5, Prompt 22) : elle reste proposée, signalée dans son propre
    libellé — même raisonnement que D-63."""

    def __init__(self, *args, capacites_suffisantes=None, **kwargs):
        self.capacites_suffisantes = capacites_suffisantes or {}
        super().__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        libelle = f"{obj.intitule} ({obj.capacite} places)"
        if not self.capacites_suffisantes.get(obj.pk, True):
            libelle += " — capacité insuffisante"
        return libelle


class FormulaireAttitrerSalle(forms.Form):
    """`forms.Form`, pas `ModelForm` : `brigade` vient de l'URL, jamais de
    la saisie — même patron que `FormulaireRattachementMatiere`, la salle
    attitrée étant une sous-ressource composée depuis l'écran d'affectation
    (US-SES-03, étape 0.2)."""

    lieu = ChampSalleAttitrable(
        queryset=Lieu.objects.none(),
        label="Salle",
        widget=forms.Select(attrs={"class": CLASSES_LISTE_DEROULANTE}),
    )

    def __init__(self, *args, salles_candidates, **kwargs):
        capacites = {candidat["lieu"].pk: candidat["capacite_suffisante"] for candidat in salles_candidates}
        super().__init__(*args, **kwargs)
        self.fields["lieu"].capacites_suffisantes = capacites
        self.fields["lieu"].queryset = Lieu.objects.filter(pk__in=capacites.keys()).order_by("intitule")
