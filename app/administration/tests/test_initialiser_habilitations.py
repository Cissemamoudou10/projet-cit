"""Commande `initialiser_habilitations` — RG-02 bis, Prompt 03 § 5."""

from django.contrib.auth.models import Group, Permission
from django.core.management import call_command

from administration.constantes import GROUPES, MATRICE
from administration.models import EntreeJournal, TypeAction


def test_chaque_groupe_porte_exactement_les_permissions_de_la_matrice(db):
    call_command("initialiser_habilitations")

    for nom_groupe in GROUPES:
        groupe = Group.objects.get(name=nom_groupe)
        codenames_reels = set(groupe.permissions.values_list("codename", flat=True))
        assert codenames_reels == set(MATRICE[nom_groupe])


def test_la_commande_n_ecrase_pas_un_reglage_administrateur(db):
    call_command("initialiser_habilitations")
    groupe = Group.objects.get(name="Cellule examens")
    permission_hors_matrice = Permission.objects.get(
        content_type__app_label="noyau",
        content_type__model="habilitation",
        codename="suivi_ecriture",
    )
    groupe.permissions.add(permission_hors_matrice)  # réglage administrateur, hors matrice

    call_command("initialiser_habilitations")  # rejouée, sans --reinitialiser

    groupe.refresh_from_db()
    assert groupe.permissions.filter(codename="suivi_ecriture").exists()


def test_reinitialiser_restaure_la_matrice_et_journalise(db):
    call_command("initialiser_habilitations")
    groupe = Group.objects.get(name="Cellule examens")
    permission_hors_matrice = Permission.objects.get(
        content_type__app_label="noyau",
        content_type__model="habilitation",
        codename="suivi_ecriture",
    )
    groupe.permissions.add(permission_hors_matrice)

    call_command("initialiser_habilitations", "--reinitialiser")

    groupe.refresh_from_db()
    codenames_reels = set(groupe.permissions.values_list("codename", flat=True))
    assert codenames_reels == set(MATRICE["Cellule examens"])
    assert EntreeJournal.objects.filter(type_action=TypeAction.MODIFICATION_HABILITATIONS).exists()
