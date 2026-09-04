"""US-INS-01 — écrans de gestion des instructeurs. Le modèle et le service
sont testés dans test_instructeur.py.
"""

from django.urls import reverse

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
    assert "Ziani" in reponse_fiche.content.decode()


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
    ServiceInstructeur.creer(redacteur, _donnees(nom="Bennani", matricule=None, statut="civil"))
    client.force_login(redacteur)

    contenu = client.get(reverse("ressources:liste_instructeurs")).content.decode()

    assert "MILITAIRE DU CENTRE" in contenu
    assert "VACATAIRE" in contenu
    assert "CIVIL" in contenu


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


def test_la_rubrique_ressources_est_masquee_pour_la_cellule_examens(client, cellule_examens):
    client.force_login(cellule_examens)

    reponse = client.get(reverse("noyau:accueil"))

    assert "Ressources" not in reponse.content.decode()
