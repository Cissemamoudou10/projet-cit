"""US-REF-02 — Gérer le catalogue des matières, CU-P2-03."""

import pytest
from django.contrib.messages import get_messages
from django.db import IntegrityError, connection, transaction
from django.db.models import ForeignKey
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from administration.models import EntreeJournal, TypeAction
from noyau.exceptions import ErreurHabilitation, ErreurValidation
from referentiel.models import ElementReferentiel, Formation, Matiere, ObjectifPedagogique
from referentiel.services.matiere import ServiceMatiere
from referentiel.tests.conftest import donnees_element_referentiel


def _donnees(**supplement):
    donnees = {"intitule": "Électronique numérique", "code": "ELN01"}
    donnees.update(supplement)
    return donnees


def test_creation_sans_aucune_formation_est_acceptee(redacteur):
    matiere = ServiceMatiere.creer(redacteur, _donnees())

    assert matiere.pk is not None


def test_matiere_ne_porte_aucune_cle_etrangere_vers_formation():
    """Test de non-présence, § 8 : si quelqu'un ajoute ce lien plus tard,
    c'est ce test qui le signale — un catalogue indépendant est l'écart 1
    de la story.
    """
    cibles = {
        champ.related_model for champ in Matiere._meta.get_fields() if isinstance(champ, ForeignKey)
    }
    assert Formation not in cibles


def test_aucun_champ_de_categorie_de_lieu_sur_le_modele():
    """Test de non-présence, § 3.1 : la catégorie de lieu se déclare au
    rattachement (US-REF-03/04), jamais comme attribut de la matière.
    """
    noms_champs = {champ.name for champ in Matiere._meta.get_fields()}
    assert not any("categorie" in nom or "lieu" in nom for nom in noms_champs)


def test_aucun_champ_d_objectif_pedagogique_sur_le_modele():
    """Test de non-présence, § 3.2 : les objectifs pédagogiques forment une
    entité propre (US-REF-05), jamais un champ de la matière — `_meta.fields`
    ne porte que les colonnes réelles, pas la relation inverse légitime que
    `ObjectifPedagogique.matiere` y ajoute désormais dans `get_fields()`.
    """
    noms_champs = {champ.name for champ in Matiere._meta.fields}
    assert not any("objectif" in nom for nom in noms_champs)


def test_intitule_duplique_est_refuse_avec_l_existante(redacteur):
    ServiceMatiere.creer(redacteur, _donnees())

    with pytest.raises(ErreurValidation) as info:
        ServiceMatiere.creer(redacteur, _donnees(intitule="électronique numérique", code="AUTRE"))

    assert "Électronique numérique" in str(info.value)


def test_unicite_de_l_intitule_est_imposee_en_base_en_contournant_l_orm(db):
    Matiere.objects.create(**_donnees())

    with pytest.raises(IntegrityError), transaction.atomic():
        Matiere.objects.create(**_donnees(intitule="ÉLECTRONIQUE NUMÉRIQUE", code="AUTRE"))


def test_unicite_du_code_est_imposee_en_base_en_contournant_l_orm(db):
    Matiere.objects.create(**_donnees())

    with pytest.raises(IntegrityError), transaction.atomic():
        Matiere.objects.create(**_donnees(intitule="Autre matière", code="eln01"))


def test_deux_matieres_sans_code_sont_acceptees(db):
    """La contrainte d'unicité du code est partielle (`code != ''`) : deux
    matières sans code renseigné ne sont pas deux doublons.
    """
    Matiere.objects.create(intitule="Sans code un", code="")

    Matiere.objects.create(intitule="Sans code deux", code="")  # ne lève pas


def test_code_duplique_est_refuse_en_designant_le_bon_doublon(redacteur):
    ServiceMatiere.creer(redacteur, _donnees())

    with pytest.raises(ErreurValidation) as info:
        ServiceMatiere.creer(
            redacteur, _donnees(intitule="Une matière bien différente", code="eln01")
        )

    assert "eln01" in str(info.value)
    assert "Électronique numérique" in str(info.value)


def test_colonnes_formations_et_objectifs_sont_exactes(redacteur, formation):
    """Prompt 17, § 2.1. Le compteur d'instructeurs qualifiés (relation vers
    `ressources`) est vérifié séparément dans
    `ressources/tests/test_qualification.py` : `referentiel` ne peut pas
    importer `ressources` (ordre des dépendances)."""
    matiere = ServiceMatiere.creer(redacteur, _donnees())
    ElementReferentiel.objects.create(
        formation=formation, matiere=matiere, **donnees_element_referentiel()
    )
    ObjectifPedagogique.objects.create(matiere=matiere, libelle="Un objectif", ordre=1)
    ObjectifPedagogique.objects.create(matiere=matiere, libelle="Un autre", ordre=2)

    page = ServiceMatiere.lister(redacteur, {}, None)
    ligne = next(m for m in page if m.pk == matiere.pk)

    assert ligne.nombre_formations == 1
    assert ligne.nombre_objectifs == 2


def test_nombre_de_requetes_de_la_liste_ne_depend_pas_du_nombre_de_lignes(client, redacteur):
    """Prompt 17, § 2.6 — le test obligatoire : compter les requêtes sur
    cinq lignes puis sur vingt, le nombre doit être identique."""
    client.force_login(redacteur)
    url = reverse("referentiel:liste_matieres")
    for i in range(5):
        ServiceMatiere.creer(redacteur, {"intitule": f"Matière {i:02d}", "code": ""})
    with CaptureQueriesContext(connection) as capture_cinq:
        client.get(url)

    for i in range(5, 20):
        ServiceMatiere.creer(redacteur, {"intitule": f"Matière {i:02d}", "code": ""})
    with CaptureQueriesContext(connection) as capture_vingt:
        client.get(url)

    assert len(capture_vingt) == len(capture_cinq)


def test_la_liste_des_matieres_reste_en_portrait_a_l_impression(client, redacteur):
    """K6 (recette, prompt 54) : seule la liste des instructeurs passe en
    paysage (`impression_paysage`, posé par sa seule vue) — les autres
    écrans qui partagent `noyau/gestion/liste.html` restent en portrait."""
    client.force_login(redacteur)

    contenu = client.get(reverse("referentiel:liste_matieres")).content.decode()

    assert 'data-impression="paysage"' not in contenu


def test_liste_paginee_au_dela_de_vingt_matieres(redacteur):
    for i in range(21):
        ServiceMatiere.creer(redacteur, {"intitule": f"Matière {i:02d}", "code": ""})

    page = ServiceMatiere.lister(redacteur, {}, None)

    assert page.has_next()


def test_recherche_par_intitule(redacteur):
    ServiceMatiere.creer(redacteur, _donnees())
    ServiceMatiere.creer(redacteur, {"intitule": "Mathématiques appliquées", "code": ""})

    page = ServiceMatiere.lister(redacteur, {"recherche": "Électro"}, None)

    assert [matiere.intitule for matiere in page] == ["Électronique numérique"]


def test_methode_d_enumeration_des_bloquants_existe_et_ne_trouve_rien(redacteur):
    matiere = ServiceMatiere.creer(redacteur, _donnees())

    ServiceMatiere.supprimer(redacteur, matiere.pk)  # ne lève pas

    assert not Matiere.objects.filter(pk=matiere.pk).exists()


# P-25 / D-30, refermé pour de bon (docs/suivi/DECISIONS.md, docs/suivi/
# PROBLEMES.md) : la fiche d'une matière indique désormais réellement les
# formations qui l'utilisent, critère 3 d'US-REF-02.


def test_formations_utilisatrices_liste_les_elements_referentiel_rattaches(
    redacteur, formation, matiere
):
    """Retourne des `ElementReferentiel`, pas des `Formation` nues (recette
    RECETTE-00, R00-REF-08) : `Formation` ne peut structurellement pas
    porter volume/coefficient/poids, qui vivent sur l'association."""
    assert list(ServiceMatiere.formations_utilisatrices(redacteur, matiere)) == []

    element = ElementReferentiel.objects.create(
        formation=formation, matiere=matiere, **donnees_element_referentiel()
    )

    resultat = list(ServiceMatiere.formations_utilisatrices(redacteur, matiere))
    assert resultat == [element]
    assert resultat[0].formation == formation


def test_la_fiche_affiche_reellement_la_formation_et_ses_volume_coefficient_poids(
    client, redacteur, formation, matiere
):
    """P-25 : la section affichait toujours l'état vide statique, quelle
    que soit la matière — vérifié par le vrai cycle HTTP, pas par le
    service seul (leçon du bloc C, Prompt 19). R00-REF-08 (recette) : le
    coefficient et les poids doivent être VISIBLES ici, pas seulement
    enregistrés."""
    ElementReferentiel.objects.create(
        formation=formation,
        matiere=matiere,
        **donnees_element_referentiel(
            coefficient="1.50", poids_formatif="2.00", poids_certificatif="0.50"
        ),
    )
    client.force_login(redacteur)

    contenu = client.get(reverse("referentiel:detail_matiere", args=[matiere.pk])).content.decode()

    assert formation.intitule in contenu
    assert "Aucun référentiel ne la cite encore" not in contenu
    assert "40 h" in contenu
    assert "coefficient 1,50" in contenu
    assert "poids 2,00/0,50" in contenu


def test_la_fiche_garde_l_etat_vide_quand_aucune_formation_ne_l_utilise(client, redacteur, matiere):
    client.force_login(redacteur)

    contenu = client.get(reverse("referentiel:detail_matiere", args=[matiere.pk])).content.decode()

    assert "Aucun référentiel ne la cite encore" in contenu


def test_suppression_d_une_matiere_rattachee_a_un_referentiel_est_refusee_par_le_service(
    redacteur, formation, matiere
):
    """Prompt 16, cause racine n° 3, critère 3 : US-REF-03 est livrée depuis,
    ce cas est désormais testable — voir referentiel/tests/test_referentiel.py
    pour l'équivalent en base (`matiere.delete()`, IntegrityError)."""
    ElementReferentiel.objects.create(
        formation=formation, matiere=matiere, **donnees_element_referentiel()
    )

    with pytest.raises(ErreurValidation) as info:
        ServiceMatiere.supprimer(redacteur, matiere.pk)
    assert formation.intitule in str(info.value)
    assert Matiere.objects.filter(pk=matiere.pk).exists()


def test_suppression_d_une_matiere_jamais_utilisee_reussit_depuis_l_ecran(client, redacteur):
    """Prompt 16, cause racine n° 3 : aucune route de suppression n'existait
    pour les matières."""
    matiere = ServiceMatiere.creer(redacteur, _donnees())
    client.force_login(redacteur)

    reponse_get = client.get(reverse("referentiel:supprimer_matiere", args=[matiere.pk]))
    assert reponse_get.status_code == 200

    reponse_post = client.post(reverse("referentiel:supprimer_matiere", args=[matiere.pk]))

    assert reponse_post.status_code == 302
    assert not Matiere.objects.filter(pk=matiere.pk).exists()


# Bloc D.2 du Prompt 19 — priorité 3 : preuve d'un effet réel, pas d'un code
# de retour (P-21).


def test_creer_par_l_ecran_cree_reellement_la_matiere(client, redacteur):
    client.force_login(redacteur)

    client.post(reverse("referentiel:creer_matiere"), _donnees())

    assert Matiere.objects.filter(intitule="Électronique numérique").exists()


def test_archiver_par_l_ecran_la_retire_reellement_de_la_selection(client, redacteur):
    matiere = ServiceMatiere.creer(redacteur, _donnees())
    client.force_login(redacteur)

    client.post(reverse("referentiel:archiver_matiere", args=[matiere.pk]))

    assert matiere.pk not in [m.pk for m in ServiceMatiere.disponibles_pour_selection()]


def test_desarchiver_par_l_ecran_la_rend_reellement_a_la_selection(client, redacteur):
    matiere = ServiceMatiere.creer(redacteur, _donnees())
    ServiceMatiere.archiver(redacteur, matiere.pk)
    client.force_login(redacteur)

    client.post(reverse("referentiel:desarchiver_matiere", args=[matiere.pk]))

    assert matiere.pk in [m.pk for m in ServiceMatiere.disponibles_pour_selection()]


def test_suppression_d_une_matiere_rattachee_est_refusee_depuis_l_ecran_en_enumerant_la_formation(
    client, redacteur, formation, matiere
):
    """E3 : le refus énumère l'élément qui s'oppose, pas un refus sec."""
    ElementReferentiel.objects.create(
        formation=formation, matiere=matiere, **donnees_element_referentiel()
    )
    client.force_login(redacteur)

    reponse = client.post(reverse("referentiel:supprimer_matiere", args=[matiere.pk]))

    assert reponse.status_code == 302
    assert Matiere.objects.filter(pk=matiere.pk).exists()
    messages_affiches = [str(m) for m in get_messages(reponse.wsgi_request)]
    assert any(formation.intitule in message for message in messages_affiches)


def test_matiere_archivee_absente_de_la_selection_presente_en_consultation(redacteur):
    matiere = ServiceMatiere.creer(redacteur, _donnees())
    ServiceMatiere.archiver(redacteur, matiere.pk)

    disponibles = ServiceMatiere.disponibles_pour_selection()
    page_consultation = ServiceMatiere.lister(redacteur, {}, None)

    assert matiere.pk not in disponibles.values_list("pk", flat=True)
    assert matiere.pk in [ligne.pk for ligne in page_consultation]


def test_cellule_pedagogique_ecrit(redacteur):
    ServiceMatiere.creer(redacteur, _donnees())  # ne lève pas


def test_planification_examens_direction_lisent_seulement(lecteur):
    ServiceMatiere.lister(lecteur, {}, None)  # ne lève pas

    with pytest.raises(ErreurHabilitation):
        ServiceMatiere.creer(lecteur, _donnees())


def test_creation_modification_archivage_sont_journalises(redacteur):
    matiere = ServiceMatiere.creer(redacteur, _donnees())
    ServiceMatiere.modifier(redacteur, matiere.pk, _donnees(code="ELN02"), matiere.modifie_le)
    ServiceMatiere.archiver(redacteur, matiere.pk)

    natures = list(
        EntreeJournal.objects.filter(
            objet_type="matiere", objet_identifiant__icontains="électronique numérique"
        )
        .order_by("cree_le")
        .values_list("type_action", flat=True)
    )
    assert TypeAction.CREATION_ELEMENT_GESTION in natures
    assert TypeAction.MODIFICATION_ELEMENT_GESTION in natures
    assert TypeAction.ARCHIVAGE_ELEMENT_GESTION in natures


def test_suppression_est_journalisee(redacteur):
    """Prompt 16, cause racine n° 3, § 5 — relevé en relecture, voir
    referentiel/tests/test_type_formation.py."""
    matiere = ServiceMatiere.creer(redacteur, _donnees())

    ServiceMatiere.supprimer(redacteur, matiere.pk)

    assert EntreeJournal.objects.filter(
        objet_type="matiere",
        objet_identifiant__icontains="électronique numérique",
        type_action=TypeAction.SUPPRESSION_ELEMENT_GESTION,
    ).exists()


"""Les tests de cycle HTTP croisés, de modification concurrente et de
non-régression E5 vivent dans test_matiere_ecran.py (scission § 400 lignes,
.claude/rules/python.md, prompt 54)."""
