from django import forms

from noyau.forms import FormulaireGestion
from organisation.models import Brigade, Session
from ressources.models import (
    EffetPeriode,
    GrilleHoraire,
    Instructeur,
    JourSemaine,
    Lieu,
    NatureEvenement,
)

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

CLASSES_SELECTION_MULTIPLE = (
    "w-full rounded border border-gris-trait bg-fond-bloc px-2.5 py-1.5 text-sm "
    "outline-none hover:border-marine-700 "
    "focus:border-marine-700 focus:ring-2 focus:ring-focus"
)

CLASSES_CHAMP_HEURE = (
    "h-controle w-full rounded border border-gris-trait bg-fond-bloc px-2.5 text-sm "
    "tabular-nums outline-none hover:border-marine-700 "
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


class FormulaireNatureEvenement(FormulaireGestion):
    """Patron de gestion, même famille que `FormulaireTypeFormation`
    (US-REF-00) — CLS-03 marque `NatureEvenement` `<<paramétrable>>`
    (§ 3, Prompt 28)."""

    class Meta:
        model = NatureEvenement
        fields = ["libelle", "effet_par_defaut"]
        labels = {"libelle": "Libellé", "effet_par_defaut": "Effet par défaut"}
        widgets = {
            "libelle": forms.TextInput(attrs={"class": CLASSES_CHAMP_TEXTE}),
            "effet_par_defaut": forms.Select(attrs={"class": CLASSES_LISTE_DEROULANTE}),
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


class FormulaireIndisponibiliteInstructeur(forms.Form):
    """Modification d'une période d'indisponibilité d'instructeur existante
    (§ 2, Prompt 27) — l'instructeur d'une période déjà créée ne se
    réaffecte pas depuis ce formulaire, il vient de l'objet en base."""

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


class FormulaireDeclarationIndisponibiliteInstructeur(forms.Form):
    """Écran autonome « Indisponibilités des instructeurs » (DECISIONS.md,
    D-115) : l'instructeur est un champ du formulaire, jamais un segment
    d'URL — la saisie s'amorce aussi bien depuis la liste que depuis un lien
    pré-rempli sur la fiche d'un instructeur (`?instructeur=<pk>`)."""

    FORMAT_DATE_HEURE = "%Y-%m-%dT%H:%M"

    instructeur = forms.ModelChoiceField(
        queryset=Instructeur.objects.filter(archive=False).order_by("nom", "prenom"),
        label="Instructeur",
        widget=forms.Select(attrs={"class": CLASSES_LISTE_DEROULANTE}),
    )
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


class FormulaireDeclarationPeriodeCalendrier(forms.Form):
    """Saisie d'une période de calendrier — CU-P4-05, Prompt 28.
    `forms.Form`, jamais `ModelForm` : `effet` vide n'est pas une valeur du
    modèle (`PeriodeCalendrier.effet` n'admet pas de blanc), c'est un signal
    pour le service — « reprendre l'effet par défaut de la nature » (§ 3) —
    jamais tranché dans le gabarit ni par du JavaScript de préremplissage,
    la charte excluant tout script hors des ressources déjà en place."""

    FORMAT_DATE_HEURE = "%Y-%m-%dT%H:%M"

    nature = forms.ModelChoiceField(
        queryset=NatureEvenement.objects.order_by("libelle"),
        label="Nature",
        widget=forms.Select(attrs={"class": CLASSES_LISTE_DEROULANTE}),
    )
    intitule = forms.CharField(
        label="Intitulé",
        widget=forms.TextInput(attrs={"class": CLASSES_CHAMP_TEXTE}),
    )
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
    effet = forms.ChoiceField(
        label="Effet",
        required=False,
        choices=[("", "Reprendre l'effet par défaut de la nature")] + EffetPeriode.choices,
        widget=forms.Select(attrs={"class": CLASSES_LISTE_DEROULANTE}),
    )
    sessions = forms.ModelMultipleChoiceField(
        queryset=Session.objects.order_by("intitule"),
        label="Sessions ciblées",
        required=False,
        widget=forms.SelectMultiple(attrs={"class": CLASSES_SELECTION_MULTIPLE, "size": 6}),
    )
    brigades = forms.ModelMultipleChoiceField(
        queryset=Brigade.objects.order_by("designation"),
        label="Brigades ciblées",
        required=False,
        widget=forms.SelectMultiple(attrs={"class": CLASSES_SELECTION_MULTIPLE, "size": 6}),
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
        capacites = {
            candidat["lieu"].pk: candidat["capacite_suffisante"] for candidat in salles_candidates
        }
        super().__init__(*args, **kwargs)
        self.fields["lieu"].capacites_suffisantes = capacites
        self.fields["lieu"].queryset = Lieu.objects.filter(pk__in=capacites.keys()).order_by(
            "intitule"
        )


class FormulaireGrilleHoraire(FormulaireGestion):
    """Patron de gestion — création et modification de l'intitulé d'une
    grille. Les autres champs (`active`, `date_activation`, `activee_par`)
    ne se saisissent jamais ici : ils sont posés par `ServiceGrilleHoraire.
    activer` (§ 4, Prompt 29)."""

    class Meta:
        model = GrilleHoraire
        fields = ["intitule"]
        labels = {"intitule": "Intitulé"}
        widgets = {"intitule": forms.TextInput(attrs={"class": CLASSES_CHAMP_TEXTE})}


class FormulaireDuplicationGrilleHoraire(forms.Form):
    """`forms.Form`, pas `ModelForm` : la grille source vient de l'URL,
    jamais de la saisie — même patron que `FormulaireAttitrerSalle`. A3,
    Prompt 29 : point de départ réel d'une nouvelle grille."""

    intitule = forms.CharField(
        label="Intitulé de la nouvelle grille",
        widget=forms.TextInput(attrs={"class": CLASSES_CHAMP_TEXTE}),
    )


class FormulaireCreneauType(forms.Form):
    """`forms.Form`, pas `ModelForm` : `grille` vient de l'URL, jamais de la
    saisie — sous-ressource composée depuis la fiche de sa grille (§ 0.3,
    Prompt 29), même patron que `FormulaireRattachementMatiere`."""

    FORMAT_HEURE = "%H:%M"

    jour_semaine = forms.ChoiceField(
        label="Jour",
        choices=JourSemaine.choices,
        widget=forms.Select(attrs={"class": CLASSES_LISTE_DEROULANTE}),
    )
    ordre = forms.IntegerField(
        label="Rang",
        min_value=1,
        widget=forms.NumberInput(attrs={"class": CLASSES_CHAMP_UNITE, "inputmode": "numeric"}),
    )
    heure_debut = forms.TimeField(
        label="Début",
        input_formats=[FORMAT_HEURE],
        widget=forms.TimeInput(attrs={"type": "time", "class": CLASSES_CHAMP_HEURE}),
    )
    heure_fin = forms.TimeField(
        label="Fin",
        input_formats=[FORMAT_HEURE],
        widget=forms.TimeInput(attrs={"type": "time", "class": CLASSES_CHAMP_HEURE}),
    )
