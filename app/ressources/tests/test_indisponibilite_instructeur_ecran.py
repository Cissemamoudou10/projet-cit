"""US-INS-03 — cycle HTTP réel (Prompt 27, § 9, Groupe D), restructuré par
DECISIONS.md D-115 : l'écran est autonome, l'instructeur est un champ du
formulaire (`declarer_indisponibilite_instructeur`,
`confirmer_fusion_indisponibilite` ne prennent plus de segment d'URL), et la
lecture des indisponibilités passe par la liste autonome
(`liste_indisponibilites_instructeurs`), jamais par la fiche instructeur.
D6 (garde du sprint 1) est couvert une fois pour toutes par
tests/architecture/test_ecrans_ecriture.py, vérifié passer sans
modification — non dupliqué ici. Données entièrement fictives.
"""

import datetime

from django.urls import reverse

from ressources.models import IndisponibiliteInstructeur
from ressources.services.indisponibilite_instructeur import ServiceIndisponibiliteInstructeur


def _instant(jour, heure, minute=0):
    return datetime.datetime(2026, 10, jour, heure, minute, tzinfo=datetime.UTC)


def _valeur(instant):
    return instant.strftime("%Y-%m-%dT%H:%M")


def _donnees(instructeur, debut, fin, motif):
    return {"instructeur": instructeur.pk, "debut": _valeur(debut), "fin": _valeur(fin), "motif": motif}


# --- D1 — chemin nominal, profil planification -----------------------------


def test_d1_declaration_sans_chevauchement_reussit_depuis_l_ecran(
    client, planificateur, instructeur
):
    client.force_login(planificateur)

    reponse = client.post(
        reverse("ressources:declarer_indisponibilite_instructeur"),
        _donnees(instructeur, _instant(5, 8), _instant(5, 12), "Mission"),
    )

    assert reponse.status_code == 302
    assert instructeur.indisponibilites.count() == 1


def test_d1_declaration_avec_chevauchement_puis_confirmation_de_fusion(
    client, planificateur, instructeur
):
    ServiceIndisponibiliteInstructeur.confirmer(
        planificateur, instructeur, _instant(3, 8), _instant(10, 8), "Mission"
    )
    client.force_login(planificateur)

    reponse_proposition = client.post(
        reverse("ressources:declarer_indisponibilite_instructeur"),
        _donnees(instructeur, _instant(8, 8), _instant(15, 8), "Permission"),
    )
    assert reponse_proposition.status_code == 200

    reponse_confirmation = client.post(
        reverse("ressources:confirmer_fusion_indisponibilite"),
        _donnees(instructeur, _instant(8, 8), _instant(15, 8), "Permission"),
    )

    assert reponse_confirmation.status_code == 302
    assert instructeur.indisponibilites.count() == 1
    restante = instructeur.indisponibilites.get()
    assert restante.debut == _instant(3, 8)
    assert restante.fin == _instant(15, 8)


def test_d1_modification_reussit_depuis_l_ecran(client, planificateur, instructeur):
    indisponibilite = ServiceIndisponibiliteInstructeur.confirmer(
        planificateur, instructeur, _instant(5, 8), _instant(5, 12), "Mission"
    )
    client.force_login(planificateur)

    reponse = client.post(
        reverse("ressources:modifier_indisponibilite_instructeur", args=[indisponibilite.pk]),
        {
            "debut": _valeur(_instant(5, 8)),
            "fin": _valeur(_instant(5, 12)),
            "motif": "Motif corrigé",
        },
    )

    assert reponse.status_code == 302
    indisponibilite.refresh_from_db()
    assert indisponibilite.motif == "Motif corrigé"


def test_d1_suppression_reussit_depuis_l_ecran(client, planificateur, instructeur):
    indisponibilite = ServiceIndisponibiliteInstructeur.confirmer(
        planificateur, instructeur, _instant(5, 8), _instant(5, 12), "Mission"
    )
    client.force_login(planificateur)

    reponse = client.post(
        reverse("ressources:supprimer_indisponibilite_instructeur", args=[indisponibilite.pk])
    )

    assert reponse.status_code == 302
    assert not IndisponibiliteInstructeur.objects.filter(pk=indisponibilite.pk).exists()


# --- D2 — la proposition de fusion affiche réellement bornes et absorbées --


def test_d2_ecran_de_fusion_affiche_bornes_et_periodes_absorbees(
    client, planificateur, instructeur
):
    ServiceIndisponibiliteInstructeur.confirmer(
        planificateur, instructeur, _instant(3, 8), _instant(10, 8), "Mission initiale"
    )
    client.force_login(planificateur)

    reponse = client.post(
        reverse("ressources:declarer_indisponibilite_instructeur"),
        _donnees(instructeur, _instant(8, 8), _instant(15, 8), "Permission"),
    )
    contenu = reponse.content.decode()

    assert "Mission initiale" in contenu
    assert "03/10/2026" in contenu
    assert "15/10/2026" in contenu


# --- D3/D4 — asymétrie des deux domaines ------------------------------------


def test_d3_pedagogique_lecture_accordee_ecriture_refusee(client, redacteur, instructeur):
    client.force_login(redacteur)

    reponse_lecture = client.get(reverse("ressources:detail_instructeur", args=[instructeur.pk]))
    reponse_ecriture = client.post(
        reverse("ressources:declarer_indisponibilite_instructeur"),
        _donnees(instructeur, _instant(5, 8), _instant(5, 12), "Mission"),
    )

    assert reponse_lecture.status_code == 200
    assert reponse_ecriture.status_code == 403


def test_d4_planification_refusee_sur_les_adresses_d_ecriture_instructeurs(
    client, planificateur, instructeur
):
    """Le pendant du précédent : la preuve que le domaine du § 5 est bien
    choisi — planification écrit les indisponibilités, jamais les
    instructeurs ni les qualifications."""
    client.force_login(planificateur)

    reponse = client.post(
        reverse("ressources:modifier_instructeur", args=[instructeur.pk]),
        {"nom": "Autre", "prenom": "Nom", "grade": "Lt", "specialite": "Autre", "statut": "civil"},
    )

    assert reponse.status_code == 403


# --- D5 — examens et Direction de formation, administrateur -----------------
# DECISIONS.md D-115 : la lecture se vérifie désormais sur la liste autonome,
# jamais sur la fiche instructeur — cellule examens n'atteint plus cette
# dernière (voir les deux tests dédiés plus bas).


def test_d5_examens_et_direction_lecture_accordee_ecriture_refusee(
    client, cellule_examens, direction_formation, instructeur
):
    for utilisateur in (cellule_examens, direction_formation):
        client.force_login(utilisateur)
        reponse_lecture = client.get(reverse("ressources:liste_indisponibilites_instructeurs"))
        reponse_ecriture = client.post(
            reverse("ressources:declarer_indisponibilite_instructeur"),
            _donnees(instructeur, _instant(5, 8), _instant(5, 12), "Mission"),
        )
        assert reponse_lecture.status_code == 200
        assert reponse_ecriture.status_code == 403


def test_d5_administrateur_aucun_acces(client, administrateur, instructeur):
    client.force_login(administrateur)

    reponse_lecture = client.get(reverse("ressources:liste_indisponibilites_instructeurs"))
    reponse_ecriture = client.post(
        reverse("ressources:declarer_indisponibilite_instructeur"),
        _donnees(instructeur, _instant(5, 8), _instant(5, 12), "Mission"),
    )

    assert reponse_lecture.status_code == 403
    assert reponse_ecriture.status_code == 403


# --- Séparation des deux domaines (DECISIONS.md D-115) ----------------------


def test_examens_atteint_la_liste_autonome_des_indisponibilites_et_la_filtre_par_instructeur(
    client, cellule_examens, planificateur, instructeur
):
    """La donnée relève de `lieux_calendrier`, que cellule examens détient :
    la liste autonome, y compris filtrée par instructeur, lui reste ouverte —
    à l'inverse de la fiche instructeur (test suivant)."""
    ServiceIndisponibiliteInstructeur.confirmer(
        planificateur, instructeur, _instant(5, 8), _instant(5, 12), "Mission distincte"
    )
    client.force_login(cellule_examens)

    reponse = client.get(
        reverse("ressources:liste_indisponibilites_instructeurs"), {"instructeur": instructeur.pk}
    )

    assert reponse.status_code == 200
    assert "Mission distincte" in reponse.content.decode()


def test_examens_refuse_sur_la_fiche_instructeur_malgre_l_acces_a_la_liste_des_indisponibilites(
    client, cellule_examens, instructeur
):
    """Pendant du précédent : la fiche instructeur reste gardée par
    `instructeurs_qualifications_lecture`, domaine que cellule examens ne
    détient pas — l'accès accordé sur les indisponibilités ne s'étend jamais
    à la fiche de leur entité parente (DECISIONS.md D-115)."""
    client.force_login(cellule_examens)

    reponse = client.get(reverse("ressources:detail_instructeur", args=[instructeur.pk]))

    assert reponse.status_code == 403


# --- D7 — les passées sont réellement affichées, distinguées des futures ---


def test_d7_indisponibilites_passees_affichees_distinguees_des_futures(
    client, planificateur, instructeur
):
    hier = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=2)
    avant_hier = hier - datetime.timedelta(hours=4)
    demain = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=2)
    apres_demain = demain + datetime.timedelta(hours=4)
    ServiceIndisponibiliteInstructeur.confirmer(
        planificateur, instructeur, avant_hier, hier, "Passée"
    )
    ServiceIndisponibiliteInstructeur.confirmer(
        planificateur, instructeur, demain, apres_demain, "À venir"
    )
    client.force_login(planificateur)

    reponse = client.get(
        reverse("ressources:liste_indisponibilites_instructeurs"), {"instructeur": instructeur.pk}
    )
    contenu = reponse.content.decode()

    assert "Passée" in contenu
    assert "À venir" in contenu
    assert "PASSÉE" in contenu
    assert "À VENIR" in contenu


# --- D8 — navigation ---------------------------------------------------------


def test_d8_lien_vers_l_ecran_autonome_suit_la_lecture_jamais_l_ecriture(
    client, redacteur, instructeur
):
    """§ 2, DECISIONS.md D-115 : le lien depuis la fiche instructeur suit
    `lieux_calendrier_lecture`, jamais `lieux_calendrier_ecriture` — présent
    même pour cellule pédagogique, qui ne détient que la lecture de ce
    domaine (elle ne peut pas déclarer d'indisponibilité, mais peut les
    consulter depuis l'écran autonome)."""
    client.force_login(redacteur)

    reponse = client.get(reverse("ressources:detail_instructeur", args=[instructeur.pk]))

    url_liste_filtree = (
        f"{reverse('ressources:liste_indisponibilites_instructeurs')}?instructeur={instructeur.pk}"
    )
    assert url_liste_filtree in reponse.content.decode()
