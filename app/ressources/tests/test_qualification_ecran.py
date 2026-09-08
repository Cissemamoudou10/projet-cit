"""US-INS-02 — écrans de la matrice de qualification. Le modèle et le
service sont testés dans test_qualification.py.
"""

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from referentiel.models import ElementReferentiel, Matiere
from referentiel.tests.conftest import donnees_element_referentiel as _donnees_element
from ressources.models import Instructeur
from ressources.services.qualification import ServiceQualification


def test_entree_instructeur_liste_le_catalogue_avec_etat(client, redacteur, instructeur, matiere):
    client.force_login(redacteur)

    reponse = client.get(reverse("ressources:qualifications_instructeur", args=[instructeur.pk]))
    contenu = reponse.content.decode()

    assert reponse.status_code == 200
    assert "Électronique numérique" in contenu
    assert "Qualifier" in contenu


def test_qualifier_depuis_l_entree_instructeur(client, redacteur, instructeur, matiere):
    client.force_login(redacteur)

    reponse = client.post(
        reverse("ressources:ajouter_qualification_instructeur", args=[instructeur.pk, matiere.pk])
    )

    assert reponse.status_code == 302
    assert instructeur.qualifications.filter(matiere=matiere).exists()


def test_entree_matiere_liste_les_instructeurs_non_archives(
    client, redacteur, instructeur, matiere
):
    Instructeur.objects.create(
        nom="Archivé",
        prenom="Ancien",
        matricule=None,
        grade="Lt",
        specialite="Transmissions",
        statut="civil",
        archive=True,
    )
    client.force_login(redacteur)

    reponse = client.get(reverse("ressources:qualifications_matiere", args=[matiere.pk]))
    contenu = reponse.content.decode()

    assert "Ziani" in contenu
    assert "Archivé" not in contenu.replace("État", "")


def test_qualifier_depuis_l_entree_matiere(client, redacteur, instructeur, matiere):
    client.force_login(redacteur)

    reponse = client.post(
        reverse("ressources:ajouter_qualification_matiere", args=[matiere.pk, instructeur.pk])
    )

    assert reponse.status_code == 302
    assert instructeur.qualifications.filter(matiere=matiere).exists()


def test_planification_ne_voit_aucun_bouton_qualifier(client, planificateur, instructeur, matiere):
    client.force_login(planificateur)

    contenu = client.get(
        reverse("ressources:qualifications_instructeur", args=[instructeur.pk])
    ).content.decode()

    assert "Qualifier" not in contenu


def test_planification_ne_peut_pas_qualifier_par_appel_direct(
    client, planificateur, instructeur, matiere
):
    client.force_login(planificateur)

    reponse = client.post(
        reverse("ressources:ajouter_qualification_instructeur", args=[instructeur.pk, matiere.pk])
    )

    assert reponse.status_code == 403


def test_cellule_examens_n_a_aucun_acces_a_l_ecran(client, cellule_examens, instructeur):
    client.force_login(cellule_examens)

    reponse = client.get(reverse("ressources:qualifications_instructeur", args=[instructeur.pk]))

    assert reponse.status_code == 403


def test_retirer_depuis_la_matiere_retire_reellement_des_deux_cotes(
    client, redacteur, instructeur, matiere
):
    """Bloc D.2 du Prompt 19 — priorité 3 : `retirer_qualification_
    instructeur` a un test HTTP réel ci-dessous, `retirer_qualification_
    matiere` (même vue, `origine="matiere"`) n'en avait aucun. Une seule
    ligne `Qualification` : le retrait doit disparaître des deux relations
    inverses (`instructeur.qualifications`, `matiere.qualifications`), pas
    seulement de l'une des deux vues qui les affichent.
    """
    qualification = ServiceQualification.ajouter(redacteur, instructeur, matiere)
    client.force_login(redacteur)

    client.post(reverse("ressources:retirer_qualification_matiere", args=[qualification.pk]))

    assert not instructeur.qualifications.filter(matiere=matiere).exists()
    assert not matiere.qualifications.filter(instructeur=instructeur).exists()


def test_retrait_affiche_la_confirmation_puis_aboutit(client, redacteur, instructeur, matiere):
    qualification = ServiceQualification.ajouter(redacteur, instructeur, matiere)
    client.force_login(redacteur)

    reponse_get = client.get(
        reverse("ressources:retirer_qualification_instructeur", args=[qualification.pk])
    )
    assert reponse_get.status_code == 200
    assert "décision de commandement" in reponse_get.content.decode()

    reponse_post = client.post(
        reverse("ressources:retirer_qualification_instructeur", args=[qualification.pk])
    )
    assert reponse_post.status_code == 302
    assert not instructeur.qualifications.filter(matiere=matiere).exists()


def test_couverture_signale_une_matiere_sans_instructeur_qualifie_par_un_mot(
    client, redacteur, formation, matiere
):
    """§ 1.2 de la charte : la couleur est doublée d'un mot — pas seulement
    une couleur, pour rester lisible à l'impression monochrome."""
    ElementReferentiel.objects.create(formation=formation, matiere=matiere, **_donnees_element())
    client.force_login(redacteur)

    contenu = client.get(
        reverse("ressources:couverture_qualifications", args=[formation.pk])
    ).content.decode()

    assert "AUCUN INSTRUCTEUR QUALIFIÉ" in contenu


def test_le_signalement_apparait_aussi_sur_l_ecran_de_composition_du_referentiel(
    client, redacteur, formation, matiere
):
    ElementReferentiel.objects.create(formation=formation, matiere=matiere, **_donnees_element())
    client.force_login(redacteur)

    contenu = client.get(
        reverse("referentiel:referentiel_formation", args=[formation.pk])
    ).content.decode()

    assert "AUCUN INSTRUCTEUR QUALIFIÉ" in contenu


def test_le_compte_de_couverture_est_exact(client, redacteur, instructeur, formation, matiere):
    autre_instructeur = Instructeur.objects.create(
        nom="Alaoui",
        prenom="Yassine",
        matricule=None,
        grade="Lt",
        specialite="Transmissions",
        statut="vacataire",
    )
    ElementReferentiel.objects.create(formation=formation, matiere=matiere, **_donnees_element())
    ServiceQualification.ajouter(redacteur, instructeur, matiere)
    ServiceQualification.ajouter(redacteur, autre_instructeur, matiere)
    client.force_login(redacteur)

    reponse = client.get(reverse("ressources:couverture_qualifications", args=[formation.pk]))

    assert reponse.context["elements"][0].nombre_instructeurs_qualifies == 2


def test_le_compte_de_couverture_ne_fait_aucune_requete_par_ligne(client, redacteur, formation):
    """§ 7.4 : compter matière par matière dans une boucle produirait une
    requête par ligne — l'annotation en fait une seule. Comparé plutôt que
    fixé en dur : le nombre exact de requêtes de session/habilitation
    n'a pas à être connu, seulement qu'il n'augmente pas avec les lignes.
    """
    client.force_login(redacteur)
    url = reverse("ressources:couverture_qualifications", args=[formation.pk])

    ElementReferentiel.objects.create(
        formation=formation,
        matiere=Matiere.objects.create(intitule="Matière 1"),
        **_donnees_element(),
    )
    with CaptureQueriesContext(connection) as capture_une:
        client.get(url)

    for i in range(2, 6):
        ElementReferentiel.objects.create(
            formation=formation,
            matiere=Matiere.objects.create(intitule=f"Matière {i}"),
            **_donnees_element(),
        )
    with CaptureQueriesContext(connection) as capture_cinq:
        client.get(url)

    assert len(capture_cinq) == len(capture_une)
