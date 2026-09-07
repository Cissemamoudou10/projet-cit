"""Réinitialisation du jeu de démonstration — Prompt 15, § 1.3.

Ne touche ni au journal ni aux comptes. Le journal, d'abord : la migration
`0007_revoquer_ecriture_journal` (RG-27) retire au rôle applicatif tout
privilège `UPDATE`/`DELETE` sur `administration_entree_journal` — un vidage y
échouerait de toute façon, et un journal qui s'efface à chaque rechargement
contredirait son rôle de trace d'audit. Les comptes, ensuite, et par voie de
conséquence : chacun a déjà signé une entrée de journal comme `auteur`
(`SET_NULL`), et Django tenterait de la mettre à jour au moment de le
supprimer — même privilège manquant. Voir `comptes.py`, dont
`recuperer_comptes` relit les comptes déjà en place plutôt que d'en recréer.
"""

from referentiel.models import (
    ElementReferentiel,
    Formation,
    Matiere,
    ObjectifPedagogique,
    Prerequis,
    TypeFormation,
)
from ressources.models import IndisponibiliteLieu, Instructeur, Lieu, Qualification


def vider_donnees_demonstration(stdout):
    """Supprime dans l'ordre qui respecte les `PROTECT` du modèle : les
    classes d'association et les entités dépendantes avant leurs catalogues.
    """
    Prerequis.objects.all().delete()
    ObjectifPedagogique.objects.all().delete()
    Qualification.objects.all().delete()
    ElementReferentiel.objects.all().delete()
    IndisponibiliteLieu.objects.all().delete()
    Instructeur.objects.all().delete()
    Lieu.objects.all().delete()
    Formation.objects.all().delete()
    TypeFormation.objects.all().delete()
    Matiere.objects.all().delete()
    stdout.write("Données de démonstration vidées (comptes et journal conservés — RG-27).")
