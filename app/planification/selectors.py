"""Lectures complexes séparées des services — .claude/rules/python.md.

`seances_futures_qualification` est installée comme fournisseur de
`noyau.services.parametres.ResolveurSeancesFuturesQualification` au
démarrage de l'application (`planification.apps.PlanificationConfig.ready`)
— c'est ce câblage qui referme réellement D-51 (RG-22), voir
docs/suivi/DECISIONS.md.

`apercu_regeneration`/`grille_consultation` servent les écrans de l'US-PLAN-03
(Prompt 31, § 9) — lecture seule, aucune règle métier : la vue les appelle
pour construire un contexte déjà prêt à afficher.
"""

import dataclasses

from django.db.models import Count, Q
from django.utils import timezone

from noyau.intervalles import filtre_recouvrement
from noyau.services.parametres import ResolveurSeancesDeControle
from organisation.models import Brigade
from planification.models import LigneProgramme, ProgrammeHebdomadaire, Seance
from planification.services.temps import duree_heures
from ressources.models import CreneauType, GrilleHoraire, Instructeur, Lieu

JOUR_SEMAINE_PAR_ISO = {
    "lundi": 1,
    "mardi": 2,
    "mercredi": 3,
    "jeudi": 4,
    "vendredi": 5,
    "samedi": 6,
    "dimanche": 7,
}
JOURS_OPERATIONNELS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"]


def grille_active_avec_creneaux():
    """Lecture seule utilisée par les vues (`.claude/rules/vues.md` — une
    vue n'importe jamais un modèle, elle appelle un sélecteur)."""
    grille = GrilleHoraire.objects.filter(active=True).first()
    creneaux = list(CreneauType.objects.filter(grille=grille)) if grille else []
    return grille, creneaux


def programme_de_la_semaine(lundi_de_semaine):
    return ProgrammeHebdomadaire.objects.filter(lundi_de_semaine=lundi_de_semaine).first()


def brigades_pour_filtre(brigade_pk=None, session_pk=None):
    """`effectif_reel` annoté — même formule qu'`organisation.services.
    brigade.ServiceBrigade.composition` — une requête pour toutes les
    brigades affichées, jamais une par ligne."""
    brigades = (
        Brigade.objects.select_related("session__formation__type_formation")
        .annotate(
            effectif_reel=Count(
                "affectations",
                filter=Q(affectations__date_fin__isnull=True, affectations__stagiaire__radie=False),
                distinct=True,
            )
        )
        .order_by("session__intitule", "designation")
    )
    if brigade_pk:
        return brigades.filter(pk=brigade_pk)
    if session_pk:
        return brigades.filter(session_id=session_pk)
    return brigades


def jours_disponibles():
    """Les six jours d'activité du centre (lundi à samedi, jamais dimanche)
    — un onglet par jour, TOUJOURS les six, que la grille active y porte ou
    non des créneaux (§ 9, Prompt 31 ; retour du 17/09 : le samedi doit
    rester atteignable pour une séance hors grille — `.claude/rules/
    tests.md` — même sans créneau standard ce jour-là)."""
    return list(JOURS_OPERATIONNELS)


@dataclasses.dataclass(frozen=True)
class EtatBrigadeSemaine:
    """Ce que le programme de la semaine porte déjà pour une brigade — §9,
    Prompt 31 : « l'agent doit savoir qu'il complète ou qu'il régénère
    AVANT de lancer », pas seulement à la confirmation qui suit l'envoi."""

    brigade: object
    total_seances: int = 0
    verrouillees: int = 0

    @property
    def non_verrouillees(self):
        return self.total_seances - self.verrouillees

    @property
    def a_des_seances(self):
        return self.total_seances > 0


def _etats_semaine(lundi_de_semaine, brigades):
    programme = programme_de_la_semaine(lundi_de_semaine) if lundi_de_semaine else None
    if programme is None:
        return {}
    brigades_par_pk = {brigade.pk: brigade for brigade in brigades}
    lignes = LigneProgramme.objects.filter(
        seance__programme=programme, brigade_id__in=brigades_par_pk
    ).values_list("brigade_id", "seance__verrouillee")
    comptes = {}
    for brigade_id, verrouillee in lignes:
        compte = comptes.setdefault(brigade_id, {"total": 0, "verrouillees": 0})
        compte["total"] += 1
        if verrouillee:
            compte["verrouillees"] += 1
    return {
        brigade_id: EtatBrigadeSemaine(
            brigade=brigades_par_pk[brigade_id],
            total_seances=compte["total"],
            verrouillees=compte["verrouillees"],
        )
        for brigade_id, compte in comptes.items()
    }


def brigades_groupees_par_session(lundi_de_semaine=None):
    """Brigades présentées par session (§ 9, critère 1), chacune portant
    l'état de ses séances pour la semaine ciblée si elle est connue."""
    brigades = list(brigades_pour_filtre())
    etats = _etats_semaine(lundi_de_semaine, brigades)
    groupes, ordre = {}, []
    for brigade in brigades:
        session = brigade.session
        if session.pk not in groupes:
            groupes[session.pk] = {"session": session, "etats": []}
            ordre.append(session.pk)
        groupes[session.pk]["etats"].append(
            etats.get(brigade.pk, EtatBrigadeSemaine(brigade=brigade))
        )
    return [groupes[pk] for pk in ordre]


def apercu_regeneration(lundi_de_semaine, brigades) -> dict:
    """BNF-09 : nombre de séances NON VERROUILLÉES qu'une régénération
    supprimerait pour chaque brigade sélectionnée — vide si aucun programme
    n'existe encore pour cette semaine (première génération, rien à
    régénérer)."""
    etats = _etats_semaine(lundi_de_semaine, brigades)
    return {
        etat.brigade: etat.non_verrouillees for etat in etats.values() if etat.non_verrouillees > 0
    }


@dataclasses.dataclass(frozen=True)
class CelluleProgramme:
    ligne: object = None
    volume_cumule: float = 0.0
    autres_brigades: str = ""
    est_controle: bool = False
    creneau: object = None

    @property
    def seance(self):
        return self.ligne.seance if self.ligne else None

    @property
    def libelle_vide(self):
        return "AD/GROUPEMENT"


def _lignes_du_programme(programme, brigades):
    return (
        LigneProgramme.objects.filter(seance__programme=programme, brigade__in=brigades)
        .select_related(
            "brigade", "seance__element_referentiel__matiere", "seance__instructeur", "seance__lieu"
        )
        .prefetch_related("seance__lignes__brigade")
    )


def _volumes_cumules(lignes_cibles):
    """Volume cumulé (`.claude/rules/modeles.md`, LigneProgramme) de chaque
    ligne affichée, calculé EN BLOC — `LigneProgramme.volume_cumule`
    interroge la base à chaque accès, une requête par cellule affichée
    violerait « aucune requête dans une boucle » (.claude/rules/python.md)
    sur une grille qui en compte plusieurs dizaines."""
    cibles_pk = {ligne.pk for ligne in lignes_cibles}
    paires = {(ligne.brigade_id, ligne.seance.element_referentiel_id) for ligne in lignes_cibles}
    if not paires:
        return {}
    filtre = Q()
    for brigade_id, element_id in paires:
        filtre |= Q(brigade_id=brigade_id, seance__element_referentiel_id=element_id)
    historique = (
        LigneProgramme.objects.filter(filtre).select_related("seance").order_by("seance__debut")
    )
    cumul, resultat = {}, {}
    for ligne in historique:
        cle = (ligne.brigade_id, ligne.seance.element_referentiel_id)
        cumul[cle] = cumul.get(cle, 0) + duree_heures(ligne.seance.debut, ligne.seance.fin)
        if ligne.pk in cibles_pk:
            resultat[ligne.pk] = cumul[cle]
    return resultat


def _autres_brigades(ligne):
    autres = [
        str(autre.brigade)
        for autre in ligne.seance.lignes.all()
        if autre.brigade_id != ligne.brigade_id
    ]
    if not autres:
        return ""
    return "regroupée — " + " + ".join([str(ligne.brigade)] + autres)


def grille_consultation(programme, creneaux, brigades):
    """Groupée par type de formation, une ligne par brigade, une colonne
    par créneau (§ 9) — `creneaux` porte déjà UN SEUL JOUR, sélectionné par
    la vue (onglets), pour tenir en largeur (retour utilisateur, jamais les
    sept jours à la fois)."""
    lignes_qs = list(_lignes_du_programme(programme, brigades))
    volumes = _volumes_cumules(lignes_qs)
    controles = ResolveurSeancesDeControle.resoudre({ligne.seance_id for ligne in lignes_qs})
    par_brigade_horaire = {}
    for ligne in lignes_qs:
        debut_local = timezone.localtime(ligne.seance.debut)
        cle = (ligne.brigade_id, debut_local.isoweekday(), debut_local.time())
        par_brigade_horaire[cle] = ligne

    groupes, brigades_par_type = [], {}
    for brigade in brigades:
        type_formation = brigade.session.formation.type_formation
        brigades_par_type.setdefault(type_formation, []).append(brigade)

    for type_formation, brigades_du_type in brigades_par_type.items():
        lignes_affichees = []
        for brigade in brigades_du_type:
            cellules = []
            for creneau in creneaux:
                cle = (brigade.pk, JOUR_SEMAINE_PAR_ISO[creneau.jour_semaine], creneau.heure_debut)
                ligne = par_brigade_horaire.get(cle)
                cellules.append(
                    CelluleProgramme(
                        ligne=ligne,
                        volume_cumule=volumes.get(ligne.pk, 0) if ligne else 0,
                        autres_brigades=_autres_brigades(ligne) if ligne else "",
                        est_controle=ligne.seance_id in controles if ligne else False,
                        creneau=creneau,
                    )
                )
            lignes_affichees.append({"brigade": brigade, "cellules": cellules})
        groupes.append({"type_formation": type_formation, "lignes": lignes_affichees})
    return groupes


def seances_futures_qualification(instructeur, matiere) -> list[str]:
    """Séances NON ENCORE TERMINÉES (`fin > maintenant`) de cet instructeur
    sur cette matière du catalogue — RG-22. Rendu en chaînes déjà formées :
    `ressources` n'a besoin de rien connaître de `Seance` au-delà de ce
    texte, le résolveur de `noyau` ne transporte que la donnée, jamais
    l'objet."""
    seances = (
        Seance.objects.filter(
            instructeur=instructeur,
            element_referentiel__matiere=matiere,
            fin__gt=timezone.now(),
        )
        .select_related("element_referentiel__matiere")
        .order_by("debut")
    )
    return [str(seance) for seance in seances]


def instructeurs_qualifies_pour(matiere=None) -> list[tuple[int, str]]:
    """A6, Prompt 35 : expose `evaluations` (P6 dépend de P5) le strict
    nécessaire pour choisir un instructeur sur un contrôle — nom et grade,
    RIEN d'autre — sans que la cellule examens consulte le domaine
    `instructeurs_qualifications` (D-38, elle n'y a aucun accès). Choisir
    dans cette liste n'est pas consulter ce domaine : c'est `planification`,
    déjà autorisée à dépendre de `ressources`, qui lit et réduit.

    `matiere=None` : tout le catalogue des instructeurs qualifiés, toutes
    matières confondues — le formulaire de création d'un contrôle ne connaît
    pas encore le module choisi sans JavaScript ; RG-35 (`ServiceContraintes`)
    reste seule juge d'une qualification réellement adaptée au module."""
    qs = Instructeur.objects.filter(archive=False)
    qs = (
        qs.filter(qualifications__matiere=matiere)
        if matiere
        else qs.filter(qualifications__isnull=False)
    )
    lignes = qs.distinct().order_by("nom", "prenom").values_list("pk", "grade", "nom", "prenom")
    return [(pk, f"{grade} {nom} {prenom}") for pk, grade, nom, prenom in lignes]


def lieux_pour_choix() -> list[tuple[int, str]]:
    """A6 : même principe que `instructeurs_qualifies_pour`, réduit à
    l'intitulé — pas de fiche, pas de qualification affichée."""
    return list(
        Lieu.objects.filter(archive=False).order_by("intitule").values_list("pk", "intitule")
    )


def seances_recouvertes(brigades, debut, fin):
    """A7, Prompt 36 : signalement de C5, jamais une suppression — rend les
    séances des brigades données qui recouvrent `[debut, fin)`, programme et
    état déjà chargés. Appelée par `evaluations` à la saisie et à chaque
    modification de la date d'une certificative ; fermera D-121 E2 à
    US-PLAN-05, qui reste seul à trancher l'arbitrage explicite que ce
    report exige — ce sélecteur ne le referme pas lui-même."""
    return list(
        Seance.objects.filter(
            filtre_recouvrement("debut", "fin", debut, fin), lignes__brigade__in=brigades
        )
        .select_related("programme", "element_referentiel__matiere")
        .distinct()
    )


def brigades_de_la_periode(periode):
    """D-121 E2 : résout la portée d'une période de calendrier (RG-30) en
    brigades concrètes — centre entier si aucune cible, sinon l'union des
    sessions et des brigades déclarées. Même règle que `PeriodeCalendrier.
    portee`, qui ne fait que la décrire en texte."""
    sessions = list(periode.sessions.all())
    brigades = list(periode.brigades.all())
    if not sessions and not brigades:
        return list(Brigade.objects.all())
    return list(
        Brigade.objects.filter(
            Q(session__in=sessions) | Q(pk__in=[b.pk for b in brigades])
        ).distinct()
    )


def seances_occupant_lieux(ids_lieux, debut, fin) -> dict:
    """Lieu -> séances occupant ce lieu sur `[debut, fin)` — une requête pour N lieux."""
    resultat = {}
    if not ids_lieux:
        return resultat
    requete = (
        Seance.objects.filter(
            filtre_recouvrement("debut", "fin", debut, fin), lieu_id__in=list(ids_lieux)
        )
        .select_related("element_referentiel__matiere", "instructeur", "lieu")
        .order_by("debut")
    )
    for seance in requete:
        resultat.setdefault(seance.lieu_id, []).append(seance)
    return resultat


def seances_occupant_instructeurs(ids_instructeurs, debut, fin) -> dict:
    """Instructeur -> séances de cet instructeur sur `[debut, fin)` — une requête pour N."""
    resultat = {}
    if not ids_instructeurs:
        return resultat
    requete = (
        Seance.objects.filter(
            filtre_recouvrement("debut", "fin", debut, fin),
            instructeur_id__in=list(ids_instructeurs),
        )
        .select_related("element_referentiel__matiere", "instructeur", "lieu")
        .order_by("debut")
    )
    for seance in requete:
        resultat.setdefault(seance.instructeur_id, []).append(seance)
    return resultat
