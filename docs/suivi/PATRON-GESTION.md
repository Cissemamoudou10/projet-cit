# Patron de gestion — US-REF-00

Source : Prompt 05, § 2.1. Code vérifiable : `app/noyau/services/gestion.py`
(`ServiceGestion`), `app/noyau/models.py` (`ModeleArchivable`),
`app/noyau/forms.py` (`FormulaireGestion`), `app/noyau/templates/noyau/gestion/`
(`liste.html`, `formulaire.html`, `confirmer_archivage.html`).

Premier usage : `app/referentiel/services/type_formation.py::ServiceTypeFormation`.
Second usage, réservé aux tests du patron lui-même (jamais en production) :
`app/essai_patron_gestion/`.

## Temps passé — § 2.1, § 8, § 10 du Prompt 05

Le prompt demande de relever le temps séparément entre le patron (investissement
au-delà des 2,6 h de la story, qui se rembourse sur US-REF-01/02/05/07) et la
story elle-même. Relevé que je ne peux pas faire à ta place — je n'ai pas
connaissance du temps réel écoulé.

- Temps sur le patron (`noyau/services/gestion.py`, mixin, gabarits génériques,
  `essai_patron_gestion/`) : **à compléter**
- Temps sur la story (`TypeFormation` et ce qui lui est propre) : **à compléter**

## Ce qu'une sous-classe déclare

| Attribut | Rôle |
|---|---|
| `MODELE` | Le modèle Django géré |
| `DOMAINE` | Domaine du catalogue d'habilitation (exigé par le test d'architecture posé en US-ADM-03) |
| `CHAMP_UNICITE` | Champ unique — sert aussi d'identifiant lisible dans le journal et dans le message d'E2 |
| `CHAMPS_RECHERCHE` | Champs interrogés par le filtre de recherche libre |
| `CHAMPS_JOURNALISES` | Liste blanche capturée dans `valeur_avant`/`valeur_apres` (§ 2.6, jamais une sérialisation complète) |
| `OBJET_TYPE` | Valeur du couple `objet_type` posé au journal pour chaque action |
| `PERMISSION_LECTURE`, `PERMISSION_ECRITURE` | Codes de permission `noyau.<domaine>_lecture`/`_ecriture` |
| `VERIFIER_HABILITATION`, `ENREGISTRER_JOURNAL`, `DONNEES_JOURNAL` | Injectés depuis `administration` — voir D-19 |
| `NATURE_CREATION`, `NATURE_MODIFICATION`, `NATURE_ARCHIVAGE` | Les trois valeurs génériques de `TypeAction` (D-18) |

`ServiceTypeFormation` n'ajoute strictement rien d'autre : la preuve que le
patron porte tout ce qui est générique.

## Pourquoi `noyau` peut journaliser et vérifier l'habilitation sans dépendre d'`administration`

Voir D-19. `ServiceGestion` ne contient **aucun** `import` d'`administration`,
ni en tête de fichier ni à l'intérieur d'une méthode (le test d'architecture
`test_ordre_des_dependances_entre_applications` le vérifie littéralement,
import différé compris — un import différé avait d'abord semblé suffire par
analogie avec D-14, il ne l'était pas). La sous-classe fournit les
fonctions par attribut de classe.

## Mécanisme d'archivage — ce qui est protégé, ce qui ne l'est pas

Voir D-20 : **seule la suppression** est conditionnelle
(`django.db.models.deletion.ProtectedError`, capturée nativement — aucun
pré-contrôle écrit à la main). **L'archivage est toujours possible**, quel
que soit le nombre de références. C'est un écart assumé par rapport au
libellé de la table de tests du Prompt 05 § 7, qui contredit sa propre § 2.3
— signalé, pas deviné.

## E2 — l'unicité remonte de la contrainte, jamais d'un contrôle préalable

Deux dispositifs à poser ensemble, sans quoi Django intercepte la violation
avant le service (voir P-19, `docs/suivi/PROBLEMES.md`) :

1. `ServiceGestion._valider` appelle `full_clean(validate_unique=False, validate_constraints=False)`.
2. Le formulaire hérite de `noyau.forms.FormulaireGestion`, qui répète
   `ModelForm._post_clean` à l'identique sauf ce même paramètre — sans quoi
   `formulaire.is_valid()` valide déjà `Meta.constraints` en interne, avant
   que la vue n'appelle le service.

Le message final désigne l'élément existant (`ServiceGestion._erreur_unicite`,
recherche `__iexact` sur `CHAMP_UNICITE`), jamais le message technique de
Django (« La contrainte « … » n'est pas respectée »).

## E5 — modification concurrente

`ServiceGestion.modifier(agissant, pk, donnees, modifie_le_attendu)` refetche
toujours l'instance depuis la base avant de comparer — jamais l'objet passé
par l'appelant, qui pourrait déjà être périmé. `modifie_le_attendu` vient du
champ caché du formulaire (§ 2.2), posé par `noyau/gestion/formulaire.html`.

## Ce que `ServiceCompte` gagnerait à reprendre du patron

Demandé en Étape 0, sans reprise dans cette story (décision séparée) :

- `lister`/`_ordre`/`CHAMPS_TRIABLES` — patron recherche/tri/pagination
  déjà écrit deux fois à l'identique (`ServiceCompte.lister`,
  `ServiceGestion.lister`) ; seule la recherche multi-champs diverge un peu
  (`ServiceCompte` cherche sur trois champs disjoints par nature — identifiant,
  nom, grade — quand le patron généralise `CHAMPS_RECHERCHE` correctement).
- `obtenir(pk)` — même squelette exact (`try/except ...DoesNotExist → ErreurIntrouvable`).
- Le squelette `créer`/`modifier` (habilitation, `transaction.atomic`,
  `IntegrityError → erreur nommant l'élément en conflit`).
- La désactivation/réactivation de compte **ressemble** à archiver/désarchiver
  mais n'en est pas un cas particulier : RG-04 interdit la suppression d'un
  compte ayant journalisé, alors que le patron autorise la suppression d'un
  élément jamais référencé — les deux règles divergent, une reprise mécanique
  serait fausse sur ce point précis.
