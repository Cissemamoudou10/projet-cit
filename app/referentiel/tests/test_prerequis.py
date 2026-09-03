"""US-REF-06 — Déclarer les prérequis du référentiel, CU-P2-07. Le graphe et
le service, sans navigateur — les écrans et RG-07 sont dans
test_prerequis_ecran.py.
"""

import pytest
from django.db import IntegrityError, transaction

from noyau.exceptions import ErreurHabilitation, ErreurValidation
from referentiel.models import Formation, Prerequis
from referentiel.services.prerequis import ServicePrerequis, ordre_topologique, trouver_chemin
from referentiel.tests.conftest import creer_element

# --- Ajout, nominal et refus ---


def test_ajout_simple_entre_deux_matieres_du_meme_referentiel(redacteur, formation):
    a = creer_element(formation, "Analyse de signal")
    b = creer_element(formation, "Bases électroniques")

    lien = ServicePrerequis.ajouter(redacteur, formation, a, b)

    assert lien.element == a
    assert lien.element_prerequis == b


def test_cycle_direct_est_refuse(redacteur, formation):
    a = creer_element(formation, "Analyse de signal")
    b = creer_element(formation, "Bases électroniques")
    ServicePrerequis.ajouter(redacteur, formation, a, b)  # A exige B

    with pytest.raises(ErreurValidation):
        ServicePrerequis.ajouter(redacteur, formation, b, a)  # B exige A : cycle

    assert not Prerequis.objects.filter(element=b, element_prerequis=a).exists()


def test_cycle_indirect_est_refuse(redacteur, formation):
    a = creer_element(formation, "Analyse de signal")
    b = creer_element(formation, "Bases électroniques")
    c = creer_element(formation, "Câblage")
    ServicePrerequis.ajouter(redacteur, formation, a, b)  # A exige B
    ServicePrerequis.ajouter(redacteur, formation, b, c)  # B exige C

    with pytest.raises(ErreurValidation):
        ServicePrerequis.ajouter(redacteur, formation, c, a)  # C exige A : cycle indirect


def test_le_refus_de_cycle_rend_la_chaine_complete_dans_l_ordre(redacteur, formation):
    """Le test le plus important de la story (§ 8) : un refus qui ne montre
    pas le chemin satisfait RG-10 mais échoue à E1.
    """
    a = creer_element(formation, "Analyse de signal")
    b = creer_element(formation, "Bases électroniques")
    c = creer_element(formation, "Câblage")
    ServicePrerequis.ajouter(redacteur, formation, a, b)
    ServicePrerequis.ajouter(redacteur, formation, b, c)

    with pytest.raises(ErreurValidation) as info:
        ServicePrerequis.ajouter(redacteur, formation, c, a)

    message = str(info.value)
    position_a = message.index("Analyse de signal")
    position_b = message.index("Bases électroniques")
    position_c = message.index("Câblage")
    assert position_c < position_a < position_b


def test_auto_prerequis_est_refuse_en_base(formation):
    """E3 — `ck_prerequis_non_reflexif` n'est pas différée."""
    a = creer_element(formation, "Analyse de signal")

    with pytest.raises(IntegrityError), transaction.atomic():
        Prerequis.objects.create(element=a, element_prerequis=a)


def test_auto_prerequis_est_refuse_par_le_service(redacteur, formation):
    a = creer_element(formation, "Analyse de signal")

    with pytest.raises(ErreurValidation):
        ServicePrerequis.ajouter(redacteur, formation, a, a)


def test_matiere_d_un_autre_referentiel_est_refusee(redacteur, formation, type_officiers):
    autre_formation = Formation.objects.create(
        intitule="Formation continue",
        specialite="Transmissions",
        duree_semaines=4,
        type_formation=type_officiers,
    )
    a = creer_element(formation, "Analyse de signal")
    hors_referentiel = creer_element(autre_formation, "Hors référentiel")

    with pytest.raises(ErreurValidation) as info:
        ServicePrerequis.ajouter(redacteur, formation, a, hors_referentiel)

    assert "RG-09" in str(info.value) or "référentiel" in str(info.value).lower()


def test_couple_deja_declare_est_refuse_en_base(formation):
    a = creer_element(formation, "Analyse de signal")
    b = creer_element(formation, "Bases électroniques")
    Prerequis.objects.create(element=a, element_prerequis=b)

    with pytest.raises(IntegrityError), transaction.atomic():
        Prerequis.objects.create(element=a, element_prerequis=b)


def test_couple_deja_declare_est_refuse_par_le_service(redacteur, formation):
    a = creer_element(formation, "Analyse de signal")
    b = creer_element(formation, "Bases électroniques")
    ServicePrerequis.ajouter(redacteur, formation, a, b)

    with pytest.raises(ErreurValidation):
        ServicePrerequis.ajouter(redacteur, formation, a, b)


def test_suppression_d_un_lien_ne_declenche_aucun_controle(redacteur, formation):
    a = creer_element(formation, "Analyse de signal")
    b = creer_element(formation, "Bases électroniques")
    lien = ServicePrerequis.ajouter(redacteur, formation, a, b)

    ServicePrerequis.retirer(redacteur, lien)  # ne lève pas

    assert not Prerequis.objects.filter(pk=lien.pk).exists()


# --- Ordre topologique ---


def test_ordre_topologique_les_prerequis_precedent_toujours(redacteur, formation):
    a = creer_element(formation, "Analyse de signal")
    b = creer_element(formation, "Bases électroniques")
    c = creer_element(formation, "Câblage")
    ServicePrerequis.ajouter(redacteur, formation, a, b)  # A exige B
    ServicePrerequis.ajouter(redacteur, formation, b, c)  # B exige C

    ordre = ordre_topologique(formation)

    assert ordre.index(c) < ordre.index(b) < ordre.index(a)


def test_le_meme_graphe_rend_deux_fois_le_meme_ordre(redacteur, formation):
    a = creer_element(formation, "Analyse de signal")
    b = creer_element(formation, "Bases électroniques")
    c = creer_element(formation, "Câblage")
    ServicePrerequis.ajouter(redacteur, formation, a, c)
    ServicePrerequis.ajouter(redacteur, formation, b, c)

    assert ordre_topologique(formation) == ordre_topologique(formation)


def test_graphe_sans_aucun_lien_rend_l_ordre_par_la_regle_de_departage(formation):
    b = creer_element(formation, "Bases électroniques")
    a = creer_element(formation, "Analyse de signal")

    ordre = ordre_topologique(formation)

    assert ordre == [a, b]


def test_graphe_a_trente_sommets_reste_immediat(redacteur, formation):
    elements = [creer_element(formation, f"Matière {i:02d}") for i in range(30)]
    for precedent, suivant in zip(elements, elements[1:], strict=False):
        ServicePrerequis.ajouter(redacteur, formation, suivant, precedent)

    ordre = ordre_topologique(formation)

    assert ordre == elements


def test_les_deux_fonctions_de_graphe_sont_appelables_sans_contexte_d_ecran(formation):
    """§ 3.2 bis : importées depuis l'extérieur du module des prérequis,
    appelées sans agissant, sans habilitation, sans requête — exactement ce
    que fera le moteur de génération du sprint 3.
    """
    a = creer_element(formation, "Analyse de signal")
    b = creer_element(formation, "Bases électroniques")
    Prerequis.objects.create(element=a, element_prerequis=b)  # A exige B

    assert trouver_chemin(a, b, formation) == [a, b]
    assert ordre_topologique(formation) == [b, a]


# --- Habilitation ---


def test_cellule_pedagogique_ecrit(redacteur, formation):
    a = creer_element(formation, "Analyse de signal")
    b = creer_element(formation, "Bases électroniques")

    ServicePrerequis.ajouter(redacteur, formation, a, b)  # ne lève pas


def test_planification_examens_direction_lisent_seulement(lecteur, formation):
    a = creer_element(formation, "Analyse de signal")
    b = creer_element(formation, "Bases électroniques")

    ServicePrerequis.lister(lecteur, formation)  # ne lève pas

    with pytest.raises(ErreurHabilitation):
        ServicePrerequis.ajouter(lecteur, formation, a, b)
