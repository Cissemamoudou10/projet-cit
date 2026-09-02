"""`ServiceMatriceHabilitations.appliquer_changements` — comportement de lot :
couplage lecture/écriture entre plusieurs croisements du même groupe dans le
même appel, garde-fou administrateur qui ne bloque que le croisement fautif,
lot vide. La vue (`views/habilitations.py`) construit ce lot depuis le
formulaire ; ces tests exercent directement le service, sans passer par HTTP.
"""

from django.contrib.auth.models import Group

from administration.models import EntreeJournal, TypeAction
from administration.services.matrice_habilitations import (
    CroisementModifie,
    ServiceMatriceHabilitations,
)


def test_deux_croisements_du_meme_groupe_dans_le_meme_lot(administrateur):
    changements = [
        CroisementModifie("Cellule pédagogique", "lieux_calendrier", "ecriture", True),
        CroisementModifie("Cellule pédagogique", "programme", "ecriture", True),
    ]

    erreurs = ServiceMatriceHabilitations.appliquer_changements(administrateur, changements)

    assert erreurs == []
    groupe = Group.objects.get(name="Cellule pédagogique")
    codenames = set(groupe.permissions.values_list("codename", flat=True))
    # § 6 : cocher l'écriture coche la lecture, même quand le formulaire ne
    # soumettait que la case écriture.
    assert {
        "lieux_calendrier_lecture",
        "lieux_calendrier_ecriture",
        "programme_lecture",
        "programme_ecriture",
    } <= codenames
    assert (
        EntreeJournal.objects.filter(type_action=TypeAction.MODIFICATION_HABILITATIONS).count() == 2
    )


def test_le_croisement_bloque_n_empeche_pas_les_autres_du_meme_lot(administrateur):
    changements = [
        CroisementModifie("Administrateur", "administration", "ecriture", False),  # bloqué
        CroisementModifie("Cellule examens", "evaluations", "lecture", False),  # valide
    ]

    erreurs = ServiceMatriceHabilitations.appliquer_changements(administrateur, changements)

    assert len(erreurs) == 1
    assert "inconfigurable" in erreurs[0]

    groupe_admin = Group.objects.get(name="Administrateur")
    assert groupe_admin.permissions.filter(codename="administration_ecriture").exists()

    groupe_examens = Group.objects.get(name="Cellule examens")
    codenames = set(groupe_examens.permissions.values_list("codename", flat=True))
    assert "evaluations_lecture" not in codenames
    assert "evaluations_ecriture" not in codenames  # décocher lecture décoche aussi écriture


def test_lot_vide_ne_fait_rien(administrateur):
    erreurs = ServiceMatriceHabilitations.appliquer_changements(administrateur, [])

    assert erreurs == []
    assert not EntreeJournal.objects.filter(
        type_action=TypeAction.MODIFICATION_HABILITATIONS
    ).exists()
