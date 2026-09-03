"""US-REF-05 — réordonnancement des objectifs pédagogiques, § 2.2 et § 6.1.

`uq_objectif_matiere_ordre` est `DEFERRABLE INITIALLY DEFERRED` : elle n'est
vérifiée qu'au commit réel de la transaction SQL, jamais à chaque `save()`.
La fixture `db` de pytest-django enveloppe tout le test dans une transaction
jamais commitée — la contrainte différée n'y est donc jamais vérifiée, et un
test écrit avec `db` seul passerait même si la contrainte n'existait pas.
Seule `transactional_db` force de vrais commits ; elle est donc requise ici,
et incompatible avec les fixtures `redacteur`/`matiere` du conftest (qui
dépendent de `db`) — ce fichier redéclare ses propres fixtures.
"""

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.db import IntegrityError, transaction

from noyau.exceptions import ErreurValidation
from noyau.services.base import ServiceBase
from referentiel.models import Matiere, ObjectifPedagogique
from referentiel.services.objectif_pedagogique import ServiceObjectifPedagogique


@pytest.fixture
def redacteur(transactional_db):
    call_command("initialiser_habilitations")
    modele = get_user_model()
    utilisateur = modele.objects.create_user(
        username="redacteur-ref-ordre",
        password="x",
        grade="Lt",
        profil=modele.Profil.CELLULE_PEDAGOGIQUE,
    )
    utilisateur.groups.add(Group.objects.get(name="Cellule pédagogique"))
    utilisateur.doit_changer_mot_de_passe = False
    utilisateur.save()
    return utilisateur


@pytest.fixture
def matiere(transactional_db):
    return Matiere.objects.create(intitule="Électronique numérique", code="ELN01")


def test_deux_objectifs_de_meme_ordre_sur_deux_matieres_differentes_est_accepte(redacteur, matiere):
    autre_matiere = Matiere.objects.create(intitule="Transmissions radio", code="TRX01")
    ServiceObjectifPedagogique.ajouter(redacteur, matiere, "Premier objectif")
    ServiceObjectifPedagogique.ajouter(redacteur, autre_matiere, "Premier objectif ailleurs")

    assert ObjectifPedagogique.objects.filter(matiere=matiere, ordre=1).exists()
    assert ObjectifPedagogique.objects.filter(matiere=autre_matiere, ordre=1).exists()


def test_ordre_duplique_sur_la_meme_matiere_est_refuse_au_commit(redacteur, matiere):
    ServiceObjectifPedagogique.ajouter(redacteur, matiere, "Premier")

    with pytest.raises(IntegrityError), transaction.atomic():
        ObjectifPedagogique.objects.create(matiere=matiere, libelle="Doublon", ordre=1)


def test_echange_de_positions_dans_la_meme_transaction_reussit(redacteur, matiere):
    """La contrainte différée tolère l'état transitoire — deux objectifs de
    même ordre entre les deux `save()` — tant qu'il ne persiste pas au commit
    de la transaction qui l'a produit.
    """
    premier = ServiceObjectifPedagogique.ajouter(redacteur, matiere, "Premier")
    second = ServiceObjectifPedagogique.ajouter(redacteur, matiere, "Second")

    ServiceObjectifPedagogique.echanger_positions(redacteur, premier, second)

    premier.refresh_from_db()
    second.refresh_from_db()
    assert premier.ordre == 2
    assert second.ordre == 1


def test_conflit_d_ordre_a_l_ajout_donne_un_message_exploitable(redacteur, matiere):
    """Relecture de conception, US-REF-05 : `CHAMP_UNICITE` (« libelle ») ne
    porte aucune contrainte réelle — seule `uq_objectif_matiere_ordre`
    existe. Deux ajouts concurrents sur la même matière, disputant le même
    `ordre` calculé, sont le seul cas qui atteint `_erreur_unicite` ; le
    message générique du patron chercherait alors un doublon de libellé
    inexistant et produirait « ... est déjà attribué à None. ».
    """
    premier = ServiceObjectifPedagogique.ajouter(redacteur, matiere, "Premier")

    with pytest.raises(ErreurValidation) as info:
        ServiceObjectifPedagogique.creer(
            redacteur,
            {"matiere": matiere, "libelle": "Concurrent", "ordre": premier.ordre},
        )

    assert "None" not in str(info.value)


def test_meme_echange_hors_transaction_echoue(redacteur, matiere):
    """Preuve que la contrainte est réellement différée, pas absente : le
    même échange, réparti sur deux transactions distinctes plutôt qu'une
    seule, commit la première écriture isolément — la contrainte, vérifiée à
    ce commit, refuse alors le doublon d'ordre qu'elle voit encore.
    """
    premier = ServiceObjectifPedagogique.ajouter(redacteur, matiere, "Premier")
    second = ServiceObjectifPedagogique.ajouter(redacteur, matiere, "Second")

    premier.ordre, second.ordre = second.ordre, premier.ordre
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            ServiceBase.modifier(premier, redacteur)
        with transaction.atomic():
            ServiceBase.modifier(second, redacteur)
