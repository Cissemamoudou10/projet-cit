"""US-REF-01 — Gérer les formations, CU-P2-02."""

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.urls import reverse

from administration.models import EntreeJournal, TypeAction
from noyau.exceptions import ErreurHabilitation, ErreurModificationConcurrente, ErreurValidation
from referentiel.models import Formation, TypeFormation
from referentiel.services.formation import ServiceFormation
from referentiel.services.type_formation import ServiceTypeFormation


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
