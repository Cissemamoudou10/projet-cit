"""L10, prompt 61 (listes filtrées, RECETTE-01 et 02) — instructeurs
qualifiés et lieux compatibles selon la matière, filtrés CÔTÉ CLIENT dans
les formulaires d'ajout et de modification d'une séance (`FormulaireSeance`,
`champs_seance.html`). Données entièrement fictives.
"""

import json

from django.urls import reverse

from planification.selectors import filtres_seance_par_element
from planification.tests.conftest import creer_element, qualifier
from referentiel.models import CategorieLieu as CategorieLieuReferentiel
from referentiel.models import Matiere, TypeLieuPartage
from ressources.models import Lieu


def test_filtres_par_element_instructeurs_et_lieux_compatibles(
    formation, instructeur, autre_instructeur, lieu_partage
):
    matiere_partagee = Matiere.objects.create(intitule="Guerre électronique", code="GE01")
    element_partage = creer_element(
        formation,
        matiere_partagee,
        categorie=CategorieLieuReferentiel.LIEU_PARTAGE,
        type_lieu_partage=TypeLieuPartage.AMPHITHEATRE,
    )
    qualifier(instructeur, matiere_partagee)
    salle = Lieu.objects.create(intitule="Salle fictive", capacite=20, categorie="salle_attitree")
    matiere_attitree = Matiere.objects.create(intitule="Procédures", code="PROC01")
    element_salle = creer_element(
        formation, matiere_attitree, categorie=CategorieLieuReferentiel.SALLE_ATTITREE
    )

    filtres = filtres_seance_par_element([element_partage, element_salle])

    assert filtres[element_partage.pk]["instructeurs"] == [instructeur.pk]
    assert autre_instructeur.pk not in filtres[element_partage.pk]["instructeurs"]
    assert lieu_partage.pk in filtres[element_partage.pk]["lieux"]
    assert salle.pk not in filtres[element_partage.pk]["lieux"]
    assert salle.pk in filtres[element_salle.pk]["lieux"]
    assert lieu_partage.pk not in filtres[element_salle.pk]["lieux"]


def test_filtres_par_element_aucun_lieu_liste_vide(formation, matiere):
    element = creer_element(formation, matiere)  # catégorie AUCUN_LIEU par défaut

    filtres = filtres_seance_par_element([element])

    assert filtres[element.pk]["lieux"] == []


def test_http_ajouter_seance_embarque_les_filtres(client, circuit):
    client.force_login(circuit.acteurs.planificateur)

    reponse = client.get(reverse("planification:ajouter_seance", args=[circuit.programme.pk]))

    contenu = reponse.content.decode("utf-8")
    assert 'id="filtres-seance"' in contenu
    debut = contenu.index('id="filtres-seance"')
    fin = contenu.index("</script>", debut)
    filtres = json.loads(contenu[contenu.index(">", debut) + 1 : fin])
    assert str(circuit.cours.element.pk) in filtres


def test_http_modifier_seance_embarque_les_filtres(client, circuit):
    from planification.tests.aide_circuit import seance_dans
    from planification.tests.conftest import instant

    seance = seance_dans(
        circuit.programme, circuit.cours, circuit.brigade,
        instant(circuit.programme.lundi_de_semaine, 0, 8),
    )
    client.force_login(circuit.acteurs.planificateur)

    reponse = client.get(reverse("planification:modifier_seance", args=[seance.pk]))

    assert 'id="filtres-seance"' in reponse.content.decode("utf-8")
