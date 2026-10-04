"""US-INS-01 — écrans de gestion des instructeurs. Le modèle et le service
sont testés dans test_instructeur.py.
"""

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from ressources.models import Instructeur
from ressources.services.instructeur import ServiceInstructeur
from ressources.tests.test_instructeur import _donnees


def test_acces_direct_a_la_liste_refuse_a_la_cellule_examens(client, cellule_examens):
    """§ 4.1 du Prompt 12 : appel direct par adresse, pas seulement masquage
    de menu — voir la note du même nom dans test_instructeur.py."""
    client.force_login(cellule_examens)

    reponse = client.get(reverse("ressources:liste_instructeurs"))

    assert reponse.status_code == 403


def test_planification_consulte_la_liste_et_la_fiche(client, planificateur, redacteur):
    instructeur = ServiceInstructeur.creer(redacteur, _donnees())
    client.force_login(planificateur)

    reponse_liste = client.get(reverse("ressources:liste_instructeurs"))
    reponse_fiche = client.get(reverse("ressources:detail_instructeur", args=[instructeur.pk]))

    assert reponse_liste.status_code == 200
    assert reponse_fiche.status_code == 200
    assert "Zalbrok" in reponse_fiche.content.decode()


def test_planification_ne_voit_ni_creer_ni_modifier_ni_archiver(client, planificateur, redacteur):
    instructeur = ServiceInstructeur.creer(redacteur, _donnees())
    client.force_login(planificateur)

    reponse_liste = client.get(reverse("ressources:liste_instructeurs")).content.decode()
    reponse_fiche = client.get(
        reverse("ressources:detail_instructeur", args=[instructeur.pk])
    ).content.decode()

    assert "Créer un instructeur" not in reponse_liste
    assert 'title="Modifier"' not in reponse_liste
    assert "Modifier" not in reponse_fiche


def test_le_nom_dans_la_liste_lie_vers_la_fiche(client, redacteur):
    instructeur = ServiceInstructeur.creer(redacteur, _donnees())
    client.force_login(redacteur)

    contenu = client.get(reverse("ressources:liste_instructeurs")).content.decode()

    assert reverse("ressources:detail_instructeur", args=[instructeur.pk]) in contenu


def test_planification_ne_peut_pas_creer_par_appel_direct(client, planificateur):
    client.force_login(planificateur)

    reponse = client.post(reverse("ressources:creer_instructeur"), _donnees())

    assert reponse.status_code == 403


def test_le_badge_de_statut_distingue_les_trois_valeurs_par_le_mot(client, redacteur):
    """§ 1.2 de la charte : la couleur est doublée d'un mot — le badge doit
    donc afficher le libellé du statut en toutes lettres, pas seulement une
    couleur, pour rester lisible à l'impression monochrome.
    """
    ServiceInstructeur.creer(redacteur, _donnees(statut="militaire_du_centre"))
    ServiceInstructeur.creer(redacteur, _donnees(nom="Alaoui", matricule=None, statut="vacataire"))
    ServiceInstructeur.creer(redacteur, _donnees(nom="Bramvel", matricule=None, statut="civil"))
    client.force_login(redacteur)

    contenu = client.get(reverse("ressources:liste_instructeurs")).content.decode()

    assert "MILITAIRE DU CENTRE" in contenu
    assert "VACATAIRE" in contenu
    assert "CIVIL" in contenu


def test_creer_par_l_ecran_cree_reellement_l_instructeur(client, redacteur):
    """Bloc D.2 du Prompt 19 — priorité 3 : preuve d'un effet réel, pas d'un
    code de retour (P-21)."""
    client.force_login(redacteur)

    client.post(reverse("ressources:creer_instructeur"), _donnees())

    assert Instructeur.objects.filter(matricule="M12345").exists()


def test_archiver_par_l_ecran_le_retire_reellement_de_la_selection(client, redacteur):
    instructeur = ServiceInstructeur.creer(redacteur, _donnees())
    client.force_login(redacteur)

    client.post(reverse("ressources:archiver_instructeur", args=[instructeur.pk]))

    assert instructeur.pk not in [i.pk for i in ServiceInstructeur.disponibles_pour_selection()]


def test_desarchiver_par_l_ecran_le_rend_reellement_a_la_selection(client, redacteur):
    instructeur = ServiceInstructeur.creer(redacteur, _donnees())
    ServiceInstructeur.archiver(redacteur, instructeur.pk)
    client.force_login(redacteur)

    client.post(reverse("ressources:desarchiver_instructeur", args=[instructeur.pk]))

    assert instructeur.pk in [i.pk for i in ServiceInstructeur.disponibles_pour_selection()]


def test_modifier_par_le_vrai_formulaire_html_ne_declenche_pas_a_tort_e5(client, redacteur):
    """Voir referentiel/tests/test_matiere.py — même bug (P-23), même
    correctif, exercé ici pour la première fois hors du référentiel.
    """
    instructeur = ServiceInstructeur.creer(redacteur, _donnees())
    client.force_login(redacteur)

    reponse_get = client.get(reverse("ressources:modifier_instructeur", args=[instructeur.pk]))
    modifie_le_attendu = reponse_get.context["modifie_le_attendu"]

    reponse_post = client.post(
        reverse("ressources:modifier_instructeur", args=[instructeur.pk]),
        {**_donnees(), "grade": "Cne", "modifie_le_attendu": modifie_le_attendu.isoformat()},
    )

    assert reponse_post.status_code == 302
    instructeur.refresh_from_db()
    assert instructeur.grade == "Cne"


def test_la_rubrique_ressources_apparait_pour_la_cellule_pedagogique(client, redacteur):
    client.force_login(redacteur)

    reponse = client.get(reverse("noyau:accueil"))

    assert "Ressources" in reponse.content.decode()


def test_la_rubrique_ressources_est_surlignee_active_sur_les_ecrans_d_instructeurs(
    client, planificateur
):
    """Symétrique du test côté lieux (test_lieu_ecran.py) : même mécanisme,
    onglet « instructeurs » cette fois."""
    client.force_login(planificateur)

    reponse = client.get(reverse("ressources:liste_instructeurs"))

    assert reponse.context["rubrique_active"] == "ressources"
    assert reponse.context["onglet_actif"] == "instructeurs"


def test_la_rubrique_ressources_pointe_vers_les_lieux_pour_la_cellule_examens(
    client, cellule_examens
):
    """D-57 : la cellule examens lit `lieux_calendrier` mais pas
    `instructeurs_qualifications` (§ 4.1 du Prompt 12) — la rubrique reste
    visible, une seule, et son lien mène directement aux lieux."""
    client.force_login(cellule_examens)

    reponse = client.get(reverse("noyau:accueil")).content.decode()

    assert "Ressources" in reponse
    assert reverse("ressources:liste_lieux") in reponse


def test_nombre_de_requetes_de_la_liste_des_instructeurs_ne_depend_pas_du_nombre_de_lignes(
    client, redacteur
):
    """Prompt 17, § 2.6 — le test obligatoire."""
    client.force_login(redacteur)
    url = reverse("ressources:liste_instructeurs")
    for i in range(5):
        ServiceInstructeur.creer(
            redacteur, _donnees(nom=f"Instructeur {i:02d}", matricule=f"M{i:05d}")
        )
    with CaptureQueriesContext(connection) as capture_cinq:
        client.get(url)

    for i in range(5, 20):
        ServiceInstructeur.creer(
            redacteur, _donnees(nom=f"Instructeur {i:02d}", matricule=f"M{i:05d}")
        )
    with CaptureQueriesContext(connection) as capture_vingt:
        client.get(url)

    assert len(capture_vingt) == len(capture_cinq)
