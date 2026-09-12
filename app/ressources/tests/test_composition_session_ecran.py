"""US-SES-04 — cycle HTTP réel de la fiche de session avec une salle
attitrée réelle, Groupe B (Prompt 23, § 11). Vit dans `app/ressources/tests`,
pas `app/organisation/tests` : ces scénarios ont besoin d'un vrai
`SalleAttitree`, qu'`organisation` ne peut pas construire (D-85, sens de
dépendance) — méthode déjà retenue à US-SES-03. Les cas ne nécessitant
aucune salle réelle vivent dans
`app/organisation/tests/test_composition_session_ecran.py`.
"""

from django.urls import reverse

from organisation.services.brigade import ServiceBrigade
from ressources.services.salle_attitree import ServiceSalleAttitree


def test_b1_taux_nominal_visible_sur_la_fiche_de_session(client, planificateur, session, brigade, lieu):
    """A1 porté à l'écran : effectif 20, capacité 30 — 67 %."""
    ServiceSalleAttitree.attribuer(planificateur, brigade, lieu)
    client.force_login(planificateur)

    reponse = client.get(reverse("organisation:detail_session", args=[session.pk]))
    contenu = reponse.content.decode()

    assert reponse.status_code == 200
    assert lieu.intitule in contenu
    assert "67 %" in contenu


def test_a4_taux_superieur_a_100_pourcent_signale_avec_les_deux_nombres_sur_la_fiche(
    client, planificateur, redacteur, session, lieu
):
    """A4 porté à l'écran, test central du § 4 : la brigade est attitrée
    quand son effectif tient dans la salle, puis son effectif prévisionnel
    est relevé après coup au-delà de la capacité — signalé, avec les deux
    nombres, couleur doublée d'un mot."""
    brigade = ServiceBrigade.creer(
        redacteur, session, {"designation": "EXP-DEP", "effectif_previsionnel": 20}
    )
    ServiceSalleAttitree.attribuer(planificateur, brigade, lieu)
    ServiceBrigade.modifier(redacteur, brigade, {"designation": "EXP-DEP", "effectif_previsionnel": 40})
    client.force_login(redacteur)

    reponse = client.get(reverse("organisation:detail_session", args=[session.pk]))
    contenu = reponse.content.decode()

    assert "DÉPASSEMENT" in contenu
    assert "40" in contenu
    assert "30" in contenu


def test_b3_planification_le_lien_vers_la_salle_reste_present_quand_une_salle_est_deja_attitree(
    client, planificateur, session, brigade, lieu
):
    ServiceSalleAttitree.attribuer(planificateur, brigade, lieu)
    client.force_login(planificateur)

    reponse = client.get(reverse("organisation:detail_session", args=[session.pk]))

    assert reverse("ressources:affecter_salle", args=[brigade.pk]) in reponse.content.decode()


def test_c7_referentiel_complet_affiche_les_matieres_reelles(client, planificateur, session):
    client.force_login(planificateur)

    reponse = client.get(reverse("organisation:detail_session", args=[session.pk]))
    contenu = reponse.content.decode()

    assert "Antennes" in contenu
    assert "40 h" in contenu
