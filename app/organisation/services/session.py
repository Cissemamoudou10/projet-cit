"""Ouverture d'une session de formation — CU-P3-01, RG-11, RG-65.

Les dépendances vers `administration` s'injectent par attributs de classe et
ne s'importent jamais dans `noyau` — D-19.
"""

from django.conf import settings
from django.db.models import Count

from administration.habilitations import verifier_habilitation
from administration.models import TypeAction
from administration.services.journal import DonneesEntreeJournal, ServiceJournal
from noyau.exceptions import ErreurValidation
from noyau.services.gestion import ServiceGestion, avertissement
from organisation.models import EtatSession, Session
from referentiel.services.referentiel import ServiceReferentiel

PERMISSION_LECTURE = "noyau.organisation_lecture"
PERMISSION_ECRITURE = "noyau.organisation_ecriture"


class ServiceSession(ServiceGestion):
    DOMAINE = "organisation"
    MODELE = Session
    CHAMP_UNICITE = "intitule"
    CHAMPS_RECHERCHE = ("intitule",)
    CHAMPS_FILTRABLES = ("formation", "etat")
    CHAMPS_JOURNALISES = (
        "intitule",
        "formation_id",
        "date_debut",
        "date_fin",
        "effectif_attendu",
        "etat",
    )
    OBJET_TYPE = "session"

    PERMISSION_LECTURE = PERMISSION_LECTURE
    PERMISSION_ECRITURE = PERMISSION_ECRITURE
    VERIFIER_HABILITATION = staticmethod(verifier_habilitation)
    ENREGISTRER_JOURNAL = staticmethod(ServiceJournal.enregistrer_detaillee)
    DONNEES_JOURNAL = DonneesEntreeJournal
    NATURE_CREATION = TypeAction.CREATION_ELEMENT_GESTION
    NATURE_MODIFICATION = TypeAction.MODIFICATION_ELEMENT_GESTION
    NATURE_SUPPRESSION = TypeAction.SUPPRESSION_ELEMENT_GESTION

    @classmethod
    def _queryset(cls):
        """La liste affiche le type de formation et signale une session sans
        aucune brigade (critère 2, US-SES-02) ; sans l'annotation, une
        requête par ligne pour compter les brigades."""
        return cls.MODELE.objects.select_related(
            "formation", "formation__type_formation"
        ).annotate(nombre_brigades=Count("brigades"))

    @classmethod
    def disponibles_pour_selection(cls):
        """`Session` n'a pas de mixin d'archivage (§ 2, Prompt 20) : le
        filtre `archive=False` du patron n'a pas de colonne à interroger.
        Surchargé pour ne pas hériter d'un comportement qui suppose une
        colonne absente de ce modèle — rien n'appelle encore cette méthode
        pour `Session`, c'est une garde, pas un besoin de cette story.
        """
        return cls.MODELE.objects.all()

    @classmethod
    def choix_etat(cls):
        """Choix pour le filtre de liste — la vue ne doit jamais importer
        `organisation.models` directement, voir .claude/rules/vues.md.
        """
        return EtatSession.choices

    @staticmethod
    def libelle_etat(valeur):
        return EtatSession(valeur).label

    @classmethod
    def _capturer(cls, instance):
        """Le patron ne sérialise pas les valeurs qu'il capture (§ 4) :
        aucune autre entité du projet ne journalise encore de `DateField`.
        `EntreeJournal.valeur_avant`/`valeur_apres` passe par `json.dumps`
        sans encodeur Django, qui ne sait pas sérialiser un `datetime.date`
        — même contournement que `ressources.services.indisponibilite_lieu.
        _capturer` pour un `DateTimeField`."""
        capture = super()._capturer(instance)
        for champ in ("date_debut", "date_fin"):
            if capture.get(champ) is not None:
                capture[champ] = capture[champ].isoformat()
        return capture

    @classmethod
    def _valider(cls, instance):
        super()._valider(instance)
        cls._verifier_periode(instance)
        cls._verifier_formation(instance.formation)

    @staticmethod
    def _verifier_periode(instance):
        """E1 — `full_clean(validate_constraints=False)` ne vérifie jamais
        les `Meta.constraints`, seulement les validateurs de champ : la
        comparaison de deux champs doit donc être écrite ici, la contrainte
        `ck_session_dates` restant le juge final en base."""
        if instance.date_fin <= instance.date_debut:
            raise ErreurValidation("La date de fin doit être postérieure à la date de début.")

    @staticmethod
    def _verifier_formation(formation):
        """Critère 4 et E4 — conditionnels à l'état d'une ligne liée ou à un
        agrégat de lignes filles : SQL ne sait pas les dire, voir § 3 du
        Prompt 20."""
        if formation.archive:
            raise ErreurValidation(
                f"La formation « {formation} » est archivée ; désarchivez-la ou "
                "choisissez une autre formation."
            )
        if not formation.elements_referentiel.exists():
            raise ErreurValidation(
                f"La formation « {formation} » n'a pas de référentiel composé : "
                "complétez son référentiel avant d'ouvrir une session."
            )

    @classmethod
    def _erreur_unicite(cls, instance):
        """Le patron ne connaît qu'une unicité à un seul champ (§ 4) :
        l'unicité réelle porte sur `(formation, intitule)`, surchargée pour
        désigner le doublon dans la bonne formation."""
        existant = (
            cls.MODELE.objects.filter(
                formation=instance.formation, intitule__iexact=instance.intitule
            )
            .exclude(pk=instance.pk)
            .first()
        )
        return ErreurValidation(
            f"« {instance.intitule} » est déjà attribué à {existant} de la même formation."
        )

    @classmethod
    def _avertissements(cls, instance):
        """E2, RG-65 — jamais un refus. Volume attendu = nombre de semaines
        de la période × volume hebdomadaire de référence (D-33) ; avertit
        seulement si le volume prescrit le DÉPASSE au-delà du seuil (E2 :
        un volume prescrit inférieur n'est pas signalé, à la différence de
        `ServiceReferentiel.ecart`, symétrique, qui répond à une question
        différente — voir docs/suivi/DECISIONS.md).

        Calcul provisoire par construction : la vraie réponse est la grille
        horaire active (US-PLAN-12) et le calendrier (US-PLAN-01), tous deux
        du sprint 2.
        """
        nombre_jours = (instance.date_fin - instance.date_debut).days
        if nombre_jours <= 0:
            return []
        nombre_semaines = nombre_jours / 7
        volume_attendu = nombre_semaines * settings.VOLUME_HORAIRE_HEBDOMADAIRE_REFERENCE
        volume_prescrit = ServiceReferentiel.total_volume(instance.formation)
        if not volume_attendu:
            return []
        ecart_pourcent = (volume_prescrit - volume_attendu) / volume_attendu * 100
        if ecart_pourcent <= settings.SEUIL_ECART_VOLUME_REFERENTIEL_POURCENT:
            return []
        return [
            avertissement(
                "volume_excede_heures_ouvrables",
                f"Le volume horaire prescrit ({volume_prescrit} h) dépasse le volume "
                f"disponible estimé sur la période ({volume_attendu:.0f} h) au-delà du "
                f"seuil de {settings.SEUIL_ECART_VOLUME_REFERENTIEL_POURCENT} % (RG-65).",
            )
        ]

    @staticmethod
    def referentiel_resume(agissant, session):
        """Nombre de matières et volume horaire total prescrit du
        référentiel de la formation de `session` — étape 2 du scénario
        nominal et bloc « Référentiel appliqué » de la fiche. Délègue à
        `ServiceReferentiel` ; n'interroge jamais les modèles de
        `referentiel` en direct et ne recopie rien (§ 4, Prompt 20).
        """
        elements = ServiceReferentiel.lister(agissant, session.formation)
        return {
            "nombre_matieres": len(elements),
            "volume_total": ServiceReferentiel.total_volume(session.formation),
        }
