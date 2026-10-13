"""La matrice — Prompt 03 § 9, table « matrice » : reproduction littérale de
§ 11.2 du dossier de conception, croisement par croisement, indépendante de
`MATRICE` (services/matrice_habilitations.py) pour détecter toute dérive de
transcription entre les deux.

Blanc = (False, False) ; L = (True, False) ; É = (True, True) — l'écriture
implique toujours la lecture (§ 6).
"""

import pytest
from django.contrib.auth.models import Group

from administration.services.matrice_habilitations import SLUGS_GROUPES

TABLE_REFERENCE_11_2 = {
    ("administration", "pedagogique"): (False, False),
    ("administration", "planification"): (False, False),
    ("administration", "examens"): (False, False),
    ("administration", "direction"): (False, False),
    ("administration", "administrateur"): (True, True),
    ("referentiel", "pedagogique"): (True, True),
    ("referentiel", "planification"): (True, False),
    ("referentiel", "examens"): (True, False),
    ("referentiel", "direction"): (True, False),
    ("referentiel", "administrateur"): (False, False),
    ("organisation", "pedagogique"): (True, True),
    ("organisation", "planification"): (True, False),
    ("organisation", "examens"): (True, False),
    ("organisation", "direction"): (True, False),
    ("organisation", "administrateur"): (False, False),
    ("instructeurs_qualifications", "pedagogique"): (True, True),
    ("instructeurs_qualifications", "planification"): (True, False),
    ("instructeurs_qualifications", "examens"): (False, False),
    ("instructeurs_qualifications", "direction"): (True, False),
    ("instructeurs_qualifications", "administrateur"): (False, False),
    ("lieux_calendrier", "pedagogique"): (True, False),
    ("lieux_calendrier", "planification"): (True, True),
    ("lieux_calendrier", "examens"): (True, False),
    ("lieux_calendrier", "direction"): (True, False),
    ("lieux_calendrier", "administrateur"): (False, False),
    # Révisé par D-233 (prompt 40, A8) : la pédagogique lit le programme ; écart 34.
    ("programme", "pedagogique"): (True, False),
    ("programme", "planification"): (True, True),
    ("programme", "examens"): (False, False),
    ("programme", "direction"): (True, False),
    ("programme", "administrateur"): (False, False),
    ("programme_validation", "pedagogique"): (True, True),
    ("programme_validation", "planification"): (True, False),
    ("programme_validation", "examens"): (False, False),
    ("programme_validation", "direction"): (True, False),
    ("programme_validation", "administrateur"): (False, False),
    ("evaluations", "pedagogique"): (False, False),
    ("evaluations", "planification"): (False, False),
    ("evaluations", "examens"): (True, True),
    ("evaluations", "direction"): (True, False),
    ("evaluations", "administrateur"): (False, False),
    ("suivi", "pedagogique"): (True, True),
    # Révisé par D-264 (prompt 44, Temps 3) : § 11.2 croisait « L », jamais
    # consommé avant US-SUI-01 ; le backlog v10 (C5) et son prompt ne
    # donnent la lecture du rapprochement qu'à la pédagogique et à la
    # Direction — corrigé ici et dans `MATRICE`, pas seulement l'écran.
    ("suivi", "planification"): (False, False),
    ("suivi", "examens"): (False, False),
    ("suivi", "direction"): (True, False),
    ("suivi", "administrateur"): (False, False),
}


@pytest.mark.parametrize(
    ("domaine", "slug_groupe", "attendu"),
    [(domaine, slug, attendu) for (domaine, slug), attendu in TABLE_REFERENCE_11_2.items()],
)
def test_croisement_conforme_a_la_matrice_11_2(groupes_habilitation, domaine, slug_groupe, attendu):
    lecture_attendue, ecriture_attendue = attendu
    groupe = Group.objects.get(name=SLUGS_GROUPES[slug_groupe])
    codenames = set(groupe.permissions.values_list("codename", flat=True))

    assert (f"{domaine}_lecture" in codenames) == lecture_attendue
    assert (f"{domaine}_ecriture" in codenames) == ecriture_attendue


def test_direction_n_a_aucune_ecriture(groupes_habilitation):
    """§ 11.2 : la Direction lit presque tout, n'écrit nulle part — les
    actions d'écriture doivent aussi disparaître de son interface (§ 8).
    """
    groupe = Group.objects.get(name="Direction de formation")
    codenames = set(groupe.permissions.values_list("codename", flat=True))

    assert not any(codename.endswith("_ecriture") for codename in codenames)


def test_planification_lit_le_referentiel_sans_l_ecrire(groupes_habilitation):
    groupe = Group.objects.get(name="Cellule planification")
    codenames = set(groupe.permissions.values_list("codename", flat=True))

    assert "referentiel_lecture" in codenames
    assert "referentiel_ecriture" not in codenames


def test_planification_n_a_aucun_acces_aux_evaluations(groupes_habilitation):
    groupe = Group.objects.get(name="Cellule planification")
    codenames = set(groupe.permissions.values_list("codename", flat=True))

    assert "evaluations_lecture" not in codenames
    assert "evaluations_ecriture" not in codenames


def test_planification_ecrit_le_programme_mais_pas_sa_validation(groupes_habilitation):
    groupe = Group.objects.get(name="Cellule planification")
    codenames = set(groupe.permissions.values_list("codename", flat=True))

    assert "programme_ecriture" in codenames
    assert "programme_validation_ecriture" not in codenames
