"""Prompt 17, § 1.5 — le test qui compte : la pagination doit produire le
même balisage sur un écran du patron `ServiceGestion` (référentiel) et sur
les deux écrans d'administration corrigés dans le même bloc (comptes,
journal), sans quoi le fragment est recopié plutôt que partagé.

Vit dans `referentiel/tests/`, pas `noyau/tests/` : `referentiel` peut
importer `administration` (ordre des dépendances), l'inverse est interdit.
"""

import re

from django.contrib.auth import get_user_model
from django.urls import reverse

from administration.models import EntreeJournal, TypeAction
from referentiel.models import TypeFormation

MOTIF_ARIA_LABEL = re.compile(r'aria-label="([^"]+)"')


def _superviseur(**supplement):
    modele = get_user_model()
    donnees = {
        "username": "superviseur-essai",
        "password": "un-mot-de-passe-suffisamment-long",
        "grade": "Cne",
        "profil": modele.Profil.ADMINISTRATEUR,
        "is_superuser": True,
        "is_staff": True,
    }
    donnees.update(supplement)
    compte = modele.objects.create_user(**donnees)
    compte.doit_changer_mot_de_passe = False
    compte.save()
    return compte


def _libelles_pagination(contenu):
    """Isole le bloc des liens de pagination (pas la ligne « Éléments X à Y
    sur Z », qui varie légitimement d'un modèle à l'autre) et renvoie la
    séquence des `aria-label`, seule preuve indépendante du gabarit d'où
    elle vient."""
    bloc = contenu.split('<div class="flex items-center gap-1">')[1].split("</div>")[0]
    return MOTIF_ARIA_LABEL.findall(bloc)


def test_le_journal_les_comptes_et_une_liste_du_referentiel_rendent_le_meme_balisage(
    db, client, settings
):
    settings.TAILLE_PAGE_DEFAUT = 1
    superviseur = _superviseur()  # compte le 3e du catalogue des comptes
    for i in range(3):
        TypeFormation.objects.create(intitule=f"Type {i:02d}")
        EntreeJournal.objects.create(
            type_action=TypeAction.ECHEC_AUTHENTIFICATION,
            identifiant_saisi=f"essai-{i:02d}",
            detail="",
            cible="authentification",
        )
    for i in range(2):
        get_user_model().objects.create_user(
            username=f"compte-{i:02d}",
            password="peu-importe-1234",
            grade="Sgt",
            profil=get_user_model().Profil.CELLULE_PEDAGOGIQUE,
        )
    client.force_login(superviseur)

    reponse_referentiel = client.get(reverse("referentiel:liste_types_formation"), {"page": 2})
    reponse_comptes = client.get(reverse("administration:liste_comptes"), {"page": 2})
    reponse_journal = client.get(reverse("administration:journal"), {"page": 2})

    libelles = _libelles_pagination(reponse_referentiel.content.decode())
    assert libelles == _libelles_pagination(reponse_comptes.content.decode())
    assert libelles == _libelles_pagination(reponse_journal.content.decode())
    assert libelles == ["Page précédente", "Page 1", "Page 2", "Page 3", "Page suivante"]
