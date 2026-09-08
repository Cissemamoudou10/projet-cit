"""US-REF-01 — Gérer les formations, CU-P2-02."""

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.db import IntegrityError, connection, transaction
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from administration.models import EntreeJournal, TypeAction
from noyau.exceptions import ErreurHabilitation, ErreurModificationConcurrente, ErreurValidation
from referentiel.models import ElementReferentiel, Formation, Matiere, TypeFormation
from referentiel.services.formation import ServiceFormation
from referentiel.services.type_formation import ServiceTypeFormation
from referentiel.tests.conftest import donnees_element_referentiel


@pytest.fixture
def type_officiers(db):
    return TypeFormation.objects.create(intitule="Officiers")


@pytest.fixture
def type_sous_officiers(db):
    return TypeFormation.objects.create(intitule="Sous-officiers")


def _donnees(type_formation, **supplement):
    donnees = {
        "intitule": "Formation initiale",
        "specialite": "Transmissions",
        "duree_semaines": 12,
        "type_formation": type_formation,
    }
    donnees.update(supplement)
    return donnees


def test_meme_intitule_dans_deux_types_differents_est_accepte(
    redacteur, type_officiers, type_sous_officiers
):
    """Écart 1 : l'unicité porte sur le couple type-intitulé, pas sur
    l'intitulé seul — deux publics légitimement distincts.
    """
    ServiceFormation.creer(redacteur, _donnees(type_officiers))

    ServiceFormation.creer(redacteur, _donnees(type_sous_officiers))  # ne lève pas


def test_meme_intitule_dans_le_meme_type_est_refuse_avec_l_existante(redacteur, type_officiers):
    ServiceFormation.creer(redacteur, _donnees(type_officiers))

    with pytest.raises(ErreurValidation) as info:
        ServiceFormation.creer(redacteur, _donnees(type_officiers, intitule="formation initiale"))

    assert "Formation initiale" in str(info.value)
    assert "Officiers" in str(info.value)


def test_unicite_composite_est_imposee_en_base_en_contournant_l_orm(type_officiers):
    Formation.objects.create(**_donnees(type_officiers))

    with pytest.raises(IntegrityError), transaction.atomic():
        Formation.objects.create(**_donnees(type_officiers, intitule="FORMATION INITIALE"))


def test_creation_sans_type_est_refusee(redacteur):
    with pytest.raises(ErreurValidation):
        ServiceFormation.creer(
            redacteur,
            {"intitule": "Sans type", "specialite": "Transmissions", "duree_semaines": 12},
        )


@pytest.mark.parametrize("duree", [0, -1])
def test_duree_nulle_ou_negative_est_refusee_en_base(type_officiers, duree):
    with pytest.raises(IntegrityError), transaction.atomic():
        Formation.objects.create(**_donnees(type_officiers, duree_semaines=duree))


def test_suppression_d_un_type_portant_une_formation_est_refusee_avec_enumeration(
    redacteur, type_officiers
):
    formation = ServiceFormation.creer(redacteur, _donnees(type_officiers))

    with pytest.raises(ErreurValidation) as info:
        ServiceTypeFormation.supprimer(redacteur, type_officiers.pk)

    assert formation.intitule in str(info.value)


def test_formation_archivee_absente_de_la_selection_presente_en_consultation(
    redacteur, type_officiers
):
    formation = ServiceFormation.creer(redacteur, _donnees(type_officiers))
    ServiceFormation.archiver(redacteur, formation.pk)

    disponibles = ServiceFormation.disponibles_pour_selection()
    page_consultation = ServiceFormation.lister(redacteur, {}, None)

    assert formation.pk not in disponibles.values_list("pk", flat=True)
    assert formation.pk in [ligne.pk for ligne in page_consultation]


def test_la_liste_se_filtre_par_type(redacteur, type_officiers, type_sous_officiers):
    ServiceFormation.creer(redacteur, _donnees(type_officiers))
    ServiceFormation.creer(redacteur, _donnees(type_sous_officiers, intitule="Autre formation"))

    page = ServiceFormation.lister(redacteur, {"type_formation": type_officiers.pk}, None)

    assert [formation.type_formation_id for formation in page] == [type_officiers.pk]


def test_la_liste_deroulante_du_formulaire_n_offre_pas_les_types_archives(
    client, redacteur, type_officiers, type_sous_officiers
):
    ServiceTypeFormation.archiver(redacteur, type_sous_officiers.pk)
    client.force_login(redacteur)

    reponse = client.get(reverse("referentiel:creer_formation"))

    choix = list(reponse.context["form"].fields["type_formation"].queryset)
    assert type_officiers in choix
    assert type_sous_officiers not in choix


def test_cellule_pedagogique_ecrit(redacteur, type_officiers):
    ServiceFormation.creer(redacteur, _donnees(type_officiers))  # ne lève pas


def test_le_bandeau_referentiel_est_visible_pour_la_cellule_pedagogique(client, redacteur):
    """La rubrique de navigation, injectée par
    noyau.context_processors.contexte_application, ne s'affiche que si
    l'utilisateur a `noyau.referentiel_lecture` — c'est l'accès principal à
    l'écran des types de formation pour un utilisateur qui ne connaît pas
    l'URL par cœur.
    """
    client.force_login(redacteur)

    reponse = client.get(reverse("referentiel:liste_types_formation"))

    slugs = [rubrique["slug"] for rubrique in reponse.context["rubriques"]]
    assert "referentiel" in slugs


def test_la_rubrique_referentiel_est_surlignee_sur_ses_propres_pages(client, redacteur):
    """`rubrique_active` se déduit de l'URL résolue, jamais renseigné par la
    vue — voir noyau/context_processors.py.
    """
    client.force_login(redacteur)

    reponse = client.get(reverse("referentiel:liste_types_formation"))
    contenu = reponse.content.decode()

    assert 'aria-current="page"' in contenu
    index = contenu.index('aria-current="page"')
    assert "Référentiel" in contenu[index : index + 200]


def test_les_listes_de_types_et_de_formations_sont_croisees(client, redacteur):
    """Sans lien croisé, un utilisateur qui arrive sur l'un des deux écrans
    du référentiel n'a aucun moyen visible d'atteindre l'autre — seul le
    bandeau de navigation mène aux types de formation, pas aux formations.
    """
    client.force_login(redacteur)

    reponse_types = client.get(reverse("referentiel:liste_types_formation"))
    reponse_formations = client.get(reverse("referentiel:liste_formations"))

    assert reverse("referentiel:liste_formations").encode() in reponse_types.content
    assert reverse("referentiel:liste_types_formation").encode() in reponse_formations.content


def test_le_bouton_modifier_de_la_liste_n_est_pas_casse_par_le_lien_de_l_intitule(
    client, redacteur, type_officiers
):
    """La cellule « intitulé » de la liste est un lien cliquable (HTML sûr,
    via format_html) — s'il fuit tel quel dans l'attribut `aria-label` du
    bouton Modifier, les guillemets qu'il contient referment l'attribut en
    plein milieu et cassent le balisage qui suit. `aria-label` doit donc
    utiliser le libellé texte brut, jamais la cellule affichée.
    """
    ServiceFormation.creer(redacteur, _donnees(type_officiers))
    client.force_login(redacteur)

    reponse = client.get(reverse("referentiel:liste_formations"))
    contenu = reponse.content.decode()

    assert 'aria-label="Modifier Formation initiale"' in contenu
    assert "<a" not in contenu.split('aria-label="Modifier')[1].split('"')[0]


@pytest.mark.parametrize(
    "nom_groupe", ["Cellule planification", "Cellule examens", "Direction de formation"]
)
def test_les_trois_autres_profils_lisent_seulement(db, nom_groupe, type_officiers):
    call_command("initialiser_habilitations")
    modele = get_user_model()
    utilisateur = modele.objects.create_user(
        username=f"lecteur-{nom_groupe}",
        password="x",
        grade="Lt",
        profil=modele.Profil.ADMINISTRATEUR,
    )
    utilisateur.groups.add(Group.objects.get(name=nom_groupe))

    ServiceFormation.lister(utilisateur, {}, None)  # ne lève pas

    with pytest.raises(ErreurHabilitation):
        ServiceFormation.creer(utilisateur, _donnees(type_officiers))


def test_creation_modification_archivage_sont_journalises(redacteur, type_officiers):
    formation = ServiceFormation.creer(redacteur, _donnees(type_officiers))
    ServiceFormation.modifier(
        redacteur,
        formation.pk,
        {**_donnees(type_officiers), "specialite": "Réseaux"},
        formation.modifie_le,
    )
    ServiceFormation.archiver(redacteur, formation.pk)

    natures = list(
        EntreeJournal.objects.filter(
            objet_type="formation", objet_identifiant__icontains="formation initiale"
        )
        .order_by("cree_le")
        .values_list("type_action", flat=True)
    )
    assert TypeAction.CREATION_ELEMENT_GESTION in natures
    assert TypeAction.MODIFICATION_ELEMENT_GESTION in natures
    assert TypeAction.ARCHIVAGE_ELEMENT_GESTION in natures


def test_suppression_est_journalisee(redacteur, type_officiers):
    """Prompt 16, cause racine n° 3, § 5 — relevé en relecture, voir
    referentiel/tests/test_type_formation.py."""
    formation = ServiceFormation.creer(redacteur, _donnees(type_officiers))

    ServiceFormation.supprimer(redacteur, formation.pk)

    assert EntreeJournal.objects.filter(
        objet_type="formation",
        objet_identifiant__icontains="formation initiale",
        type_action=TypeAction.SUPPRESSION_ELEMENT_GESTION,
    ).exists()


def test_modifier_par_le_vrai_formulaire_html_ne_declenche_pas_a_tort_e5(
    client, redacteur, type_officiers
):
    """Bug réel trouvé en usage (2026-09-03) : le champ caché
    `modifie_le_attendu` arrive du POST comme une chaîne, jamais comparable
    telle quelle à `instance.modifie_le` (un `datetime`) — voir
    docs/suivi/PROBLEMES.md. Passer une durée de 12 à 2 semaines déclenchait
    l'erreur E5 dès le tout premier essai, sans aucun conflit réel. Seul le
    vrai cycle GET puis POST exerce ce chemin — un appel direct au service
    avec un `datetime` Python ne l'aurait jamais révélé.
    """
    formation = ServiceFormation.creer(redacteur, _donnees(type_officiers, duree_semaines=12))
    client.force_login(redacteur)

    reponse_get = client.get(reverse("referentiel:modifier_formation", args=[formation.pk]))
    modifie_le_attendu = reponse_get.context["modifie_le_attendu"]

    reponse_post = client.post(
        reverse("referentiel:modifier_formation", args=[formation.pk]),
        {
            "intitule": formation.intitule,
            "specialite": formation.specialite,
            "type_formation": type_officiers.pk,
            "duree_semaines": 2,
            "modifie_le_attendu": modifie_le_attendu.isoformat(),
        },
    )

    assert reponse_post.status_code == 302
    formation.refresh_from_db()
    assert formation.duree_semaines == 2


def test_modification_concurrente_est_detectee(redacteur, type_officiers):
    formation = ServiceFormation.creer(redacteur, _donnees(type_officiers))
    modifie_le_initial = formation.modifie_le

    ServiceFormation.modifier(
        redacteur,
        formation.pk,
        {**_donnees(type_officiers), "specialite": "Réseaux"},
        modifie_le_initial,
    )

    with pytest.raises(ErreurModificationConcurrente) as info:
        ServiceFormation.modifier(
            redacteur,
            formation.pk,
            {**_donnees(type_officiers), "specialite": "Rejeu"},
            modifie_le_initial,
        )
    assert redacteur.username in str(info.value)


def test_la_colonne_nombre_de_formations_du_type_est_exacte(
    redacteur, type_officiers, type_sous_officiers
):
    ServiceFormation.creer(redacteur, _donnees(type_officiers))
    ServiceFormation.creer(redacteur, _donnees(type_officiers, intitule="Formation continue"))
    ServiceFormation.creer(redacteur, _donnees(type_sous_officiers, intitule="Autre formation"))

    page = ServiceTypeFormation.lister(redacteur, {}, None)

    comptes = {type_formation.pk: type_formation.nombre_formations for type_formation in page}
    assert comptes[type_officiers.pk] == 2
    assert comptes[type_sous_officiers.pk] == 1


def test_colonnes_matieres_et_volume_prescrit_sont_exactes(redacteur, type_officiers):
    """Prompt 17, § 2.3 — symétrie avec le compteur de formations par type
    (US-REF-00)."""
    formation = ServiceFormation.creer(redacteur, _donnees(type_officiers))
    formation_vide = ServiceFormation.creer(
        redacteur, _donnees(type_officiers, intitule="Formation continue")
    )
    ElementReferentiel.objects.create(
        formation=formation,
        matiere=Matiere.objects.create(intitule="Matière 1"),
        **donnees_element_referentiel(volume_horaire_prescrit=40),
    )
    ElementReferentiel.objects.create(
        formation=formation,
        matiere=Matiere.objects.create(intitule="Matière 2"),
        **donnees_element_referentiel(volume_horaire_prescrit=15),
    )

    page = ServiceFormation.lister(redacteur, {}, None)
    lignes = {f.pk: f for f in page}

    assert lignes[formation.pk].nombre_matieres == 2
    assert lignes[formation.pk].volume_prescrit_total == 55
    assert lignes[formation_vide.pk].nombre_matieres == 0
    assert lignes[formation_vide.pk].volume_prescrit_total is None


def test_nombre_de_requetes_de_la_liste_des_formations_ne_depend_pas_du_nombre_de_lignes(
    client, redacteur, type_officiers
):
    """Prompt 17, § 2.6 — le test obligatoire."""
    client.force_login(redacteur)
    url = reverse("referentiel:liste_formations")
    for i in range(5):
        ServiceFormation.creer(redacteur, _donnees(type_officiers, intitule=f"Formation {i:02d}"))
    with CaptureQueriesContext(connection) as capture_cinq:
        client.get(url)

    for i in range(5, 20):
        ServiceFormation.creer(redacteur, _donnees(type_officiers, intitule=f"Formation {i:02d}"))
    with CaptureQueriesContext(connection) as capture_vingt:
        client.get(url)

    assert len(capture_vingt) == len(capture_cinq)


def test_suppression_d_une_formation_jamais_utilisee_reussit_depuis_l_ecran(
    client, redacteur, type_officiers
):
    """Prompt 16, cause racine n° 3 : aucune route de suppression n'existait
    pour les formations."""
    formation = ServiceFormation.creer(redacteur, _donnees(type_officiers))
    client.force_login(redacteur)

    reponse_get = client.get(reverse("referentiel:supprimer_formation", args=[formation.pk]))
    assert reponse_get.status_code == 200

    reponse_post = client.post(reverse("referentiel:supprimer_formation", args=[formation.pk]))

    assert reponse_post.status_code == 302
    assert not Formation.objects.filter(pk=formation.pk).exists()


# Bloc D.2 du Prompt 19 — priorité 3 : preuve d'un effet réel, pas d'un code
# de retour (P-21).


def test_creer_par_l_ecran_cree_reellement_la_formation(client, redacteur, type_officiers):
    client.force_login(redacteur)

    client.post(
        reverse("referentiel:creer_formation"),
        {
            "intitule": "Formation initiale",
            "specialite": "Transmissions",
            "duree_semaines": 12,
            "type_formation": type_officiers.pk,
        },
    )

    assert Formation.objects.filter(intitule="Formation initiale").exists()


def test_archiver_par_l_ecran_la_retire_reellement_de_la_selection(
    client, redacteur, type_officiers
):
    formation = ServiceFormation.creer(redacteur, _donnees(type_officiers))
    client.force_login(redacteur)

    client.post(reverse("referentiel:archiver_formation", args=[formation.pk]))

    assert formation.pk not in [f.pk for f in ServiceFormation.disponibles_pour_selection()]


def test_desarchiver_par_l_ecran_la_rend_reellement_a_la_selection(
    client, redacteur, type_officiers
):
    formation = ServiceFormation.creer(redacteur, _donnees(type_officiers))
    ServiceFormation.archiver(redacteur, formation.pk)
    client.force_login(redacteur)

    client.post(reverse("referentiel:desarchiver_formation", args=[formation.pk]))

    assert formation.pk in [f.pk for f in ServiceFormation.disponibles_pour_selection()]
