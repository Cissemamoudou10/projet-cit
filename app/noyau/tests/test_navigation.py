"""Rubriques « Évaluations » et « Suivi » du menu principal — correctif de
navigation, prompt 49 (hors backlog). `docs/conception/16-maquettes.md`
(MAQ-01 à MAQ-05) fixe un menu à six rubriques se terminant par « … |
Planification | Évaluations | Suivi » ; ni l'une ni l'autre n'avait
d'entrée de menu propre. « Évaluations » n'était liée depuis AUCUN écran du
site (ni le menu, ni la fiche session) — un domaine entier atteignable
seulement en tapant l'URL à la main. « Suivi » n'était atteint que par la
cellule pédagogique, via le badge « Alertes » (`suivi_ecriture`,
`planification/context_processors.py`), jamais les trois autres profils de
lecture (planification, examens, Direction de Formation)."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.template.loader import render_to_string
from django.urls import reverse


def _requete_avec_permissions(rf, *codenames):
    modele_utilisateur = get_user_model()
    utilisateur = modele_utilisateur(
        username=f"essai-{'-'.join(codenames) or 'anonyme'}",
        grade="Lt",
        profil=modele_utilisateur.Profil.ADMINISTRATEUR,
        last_name="Essai",
    )
    utilisateur.set_unusable_password()
    utilisateur.save()
    for codename in codenames:
        permission = Permission.objects.get(content_type__app_label="noyau", codename=codename)
        utilisateur.user_permissions.add(permission)

    requete = rf.get("/")
    requete.user = utilisateur
    return requete


def _contenu_rendu(rf, *codenames):
    return render_to_string("noyau/base.html", request=_requete_avec_permissions(rf, *codenames))


def test_evaluations_lecture_rend_la_rubrique_evaluations_cliquable(rf, db):
    contenu = _contenu_rendu(rf, "evaluations_lecture")
    assert "Évaluations" in contenu
    assert "/evaluations/" in contenu


def test_sans_aucune_permission_la_rubrique_evaluations_est_absente(rf, db):
    contenu = _contenu_rendu(rf)
    assert "Évaluations" not in contenu


def test_suivi_lecture_rend_la_rubrique_suivi_cliquable(rf, db):
    contenu = _contenu_rendu(rf, "suivi_lecture")
    assert "Suivi" in contenu
    assert "/planification/tableau-de-bord/" in contenu


def test_sans_aucune_permission_la_rubrique_suivi_est_absente(rf, db):
    contenu = _contenu_rendu(rf)
    assert "Suivi" not in contenu


def test_suivi_ecriture_seule_ne_rend_pas_la_rubrique_suivi(rf, db):
    """`suivi_ecriture` (badge « Alertes », réservé à la pédagogique) et
    `suivi_lecture` (rubrique « Suivi », quatre profils) sont deux
    permissions distinctes du même domaine — l'une n'accorde jamais
    l'autre (RG-02 bis, `noyau.models.Habilitation`, dix-huit permissions
    indépendantes)."""
    contenu = _contenu_rendu(rf, "suivi_ecriture")
    assert "Suivi" not in contenu


def test_suivi_lecture_et_suivi_ecriture_sont_deux_permissions_distinctes():
    from noyau.models import Habilitation

    codenames = {codename for codename, _ in Habilitation._meta.permissions}
    assert "suivi_lecture" in codenames
    assert "suivi_ecriture" in codenames


def _utilisateur_connecte(client, *codenames):
    modele_utilisateur = get_user_model()
    utilisateur = modele_utilisateur(
        username=f"client-{'-'.join(codenames) or 'anonyme'}",
        grade="Lt",
        profil=modele_utilisateur.Profil.ADMINISTRATEUR,
        last_name="Client",
    )
    utilisateur.set_unusable_password()
    utilisateur.doit_changer_mot_de_passe = False  # sans quoi l'intergiciel redirige
    utilisateur.save()
    for codename in codenames:
        permission = Permission.objects.get(content_type__app_label="noyau", codename=codename)
        utilisateur.user_permissions.add(permission)
    client.force_login(utilisateur)
    return utilisateur


def test_tableau_bord_surligne_la_rubrique_suivi_pas_planification(client, db):
    """Correctif de navigation, prompt 50 : `tableau_bord` et
    `alertes_ecart` vivent dans l'app Django `planification` (pas d'app
    `suivi` dédiée) — `rubrique_active` doit les reclasser explicitement,
    sinon le menu surligne « Planification » pour un clic sur « Suivi »."""
    _utilisateur_connecte(client, "suivi_lecture")

    reponse = client.get(reverse("planification:tableau_bord"))
    contenu = reponse.content.decode()

    index = contenu.index('aria-current="page"')
    assert "Suivi" in contenu[index : index + 200]
    assert "Planification" not in contenu[index : index + 80]


def test_alertes_surligne_la_rubrique_suivi_pas_planification(client, db):
    _utilisateur_connecte(client, "suivi_lecture")

    reponse = client.get(reverse("planification:alertes_ecart"))
    contenu = reponse.content.decode()

    index = contenu.index('aria-current="page"')
    assert "Suivi" in contenu[index : index + 200]


def test_consultation_programme_surligne_bien_planification(client, db):
    """Témoin : un écran de planification qui n'appartient PAS au domaine
    Suivi doit continuer à surligner « Planification »."""
    _utilisateur_connecte(client, "programme_lecture")

    reponse = client.get(reverse("planification:consultation_programme"))
    contenu = reponse.content.decode()

    index = contenu.index('aria-current="page"')
    assert "Planification" in contenu[index : index + 200]
