"""US-VAL-04, cycle HTTP réel (prompt 40 § 3) — signature et affichage. Données fictives."""

import datetime

from django.urls import reverse
from django.utils import timezone

from administration.models import EntreeJournal, TypeAction
from planification.models import EtatProgramme
from planification.tests.aide_circuit import SIGNATAIRE, amener_a

LIBELLE_AFFICHER = "Afficher le programme"


def _url(nom, programme):
    return reverse(nom, args=[programme.pk])


def _consultation(circuit):
    return reverse("planification:consultation_programme") + (
        f"?semaine={circuit.programme.lundi_de_semaine.isoformat()}"
    )


def _signature(date_signature, signataire=SIGNATAIRE):
    return {"date_signature": date_signature.isoformat(), "signataire": signataire}


def test_affichage_absent_sans_signature_et_forge_refuse_sans_changer_l_etat(client, circuit):
    programme = circuit.programme
    amener_a(EtatProgramme.VALIDE, circuit)
    client.force_login(circuit.acteurs.planificateur)

    avant = client.get(_consultation(circuit)).content.decode("utf-8")
    assert LIBELLE_AFFICHER not in avant

    reponse = client.post(_url("planification:afficher", programme), follow=True)

    programme.refresh_from_db()
    assert programme.etat == EtatProgramme.VALIDE
    assert "RG-46" in reponse.content.decode("utf-8")


def test_signatures_a_date_anterieure_puis_future_sont_refusees_avec_leur_regle(client, circuit):
    programme = circuit.programme
    amener_a(EtatProgramme.VALIDE, circuit)
    client.force_login(circuit.acteurs.planificateur)
    validation = timezone.localdate(programme.date_validation)

    anterieure = client.post(
        _url("planification:signer", programme),
        _signature(validation - datetime.timedelta(days=1)),
        follow=True,
    )
    future = client.post(
        _url("planification:signer", programme),
        _signature(timezone.localdate() + datetime.timedelta(days=1)),
        follow=True,
    )

    assert "précéder la validation" in anterieure.content.decode("utf-8")
    assert "postérieure à aujourd" in future.content.decode("utf-8")
    programme.refresh_from_db()
    assert programme.date_signature is None


def test_signature_puis_affichage_journalise_et_affiche_les_mentions(client, circuit):
    programme = circuit.programme
    amener_a(EtatProgramme.VALIDE, circuit)
    client.force_login(circuit.acteurs.planificateur)
    aujourd_hui = timezone.localdate()

    client.post(_url("planification:signer", programme), _signature(aujourd_hui))
    avant_affichage = timezone.now()
    client.post(_url("planification:afficher", programme))

    programme.refresh_from_db()
    assert programme.etat == EtatProgramme.AFFICHE
    assert programme.signataire == SIGNATAIRE
    entree = EntreeJournal.objects.get(
        objet_type="programme",
        objet_identifiant=str(programme.pk),
        type_action=TypeAction.TRANSITION_PROGRAMME,
        detail="T8",
    )
    assert entree.auteur == circuit.acteurs.planificateur
    assert avant_affichage <= entree.cree_le <= timezone.now()
    contenu = client.get(_consultation(circuit)).content.decode("utf-8")
    assert "Validé par" in contenu and str(programme.valide_par) in contenu
    assert programme.date_validation.astimezone().strftime("%d/%m/%Y %H:%M") in contenu
    assert "Signé par" in contenu and SIGNATAIRE in contenu
    assert "Affiché le" in contenu


def test_signature_sur_un_programme_affiche_est_refusee(client, circuit):
    programme = circuit.programme
    amener_a(EtatProgramme.AFFICHE, circuit)
    client.force_login(circuit.acteurs.planificateur)
    date_signature_avant = programme.date_signature

    reponse = client.post(
        _url("planification:signer", programme),
        _signature(timezone.localdate(), "Autre signataire fictif"),
        follow=True,
    )

    programme.refresh_from_db()
    assert programme.etat == EtatProgramme.AFFICHE
    assert programme.date_signature == date_signature_avant
    assert "pas possible sur un programme affiché" in reponse.content.decode("utf-8")


def test_signature_peut_etre_enregistree_de_nouveau_tant_que_non_affiche(client, circuit):
    programme = circuit.programme
    amener_a(EtatProgramme.VALIDE, circuit)
    client.force_login(circuit.acteurs.planificateur)

    client.post(_url("planification:signer", programme), _signature(timezone.localdate()))
    client.post(
        _url("planification:signer", programme),
        _signature(timezone.localdate(), "Second signataire fictif"),
    )

    programme.refresh_from_db()
    assert programme.etat == EtatProgramme.VALIDE
    assert programme.signataire == "Second signataire fictif"


def test_affichage_par_la_pedagogique_est_refuse_403(client, circuit):
    programme = circuit.programme
    amener_a(EtatProgramme.VALIDE, circuit)
    client.force_login(circuit.acteurs.planificateur)
    client.post(_url("planification:signer", programme), _signature(timezone.localdate()))
    client.force_login(circuit.acteurs.pedagogique)

    reponse = client.post(_url("planification:afficher", programme))

    assert reponse.status_code == 403
    programme.refresh_from_db()
    assert programme.etat == EtatProgramme.VALIDE
