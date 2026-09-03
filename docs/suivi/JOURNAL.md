# Journal des actions sensibles — US-ADM-04

Source unique : RG-26, RG-27, CU-P1-03. Le code vérifiable est
`app/administration/models.py` (`TypeAction`, `EntreeJournal`) et
`app/administration/services/journal.py` (`ServiceJournal`).

## Le catalogue des natures — 14 valeurs

Cinq natures RG-26, dont trois pas encore atteignables (objets hors
périmètre — voir `docs/suivi/DECISIONS.md`, D-17), plus trois extensions
hors RG-26 (D-16).

| Code | Libellé | Origine | Atteignable |
|---|---|---|---|
| `echec_authentification` | Échec d'authentification | RG-26 | oui (US-ADM-01) |
| `creation_compte` | Création de compte | RG-26 | oui (US-ADM-02) |
| `modification_compte` | Modification de compte | RG-26 | oui (US-ADM-02) |
| `changement_profil` | Changement de profil | RG-26 | oui (US-ADM-02) |
| `desactivation_compte` | Désactivation de compte | RG-26 | oui (US-ADM-02) |
| `reactivation_compte` | Réactivation de compte | RG-26 | oui (US-ADM-02) |
| `saisie_note` | Saisie d'une note | RG-26 | non — note inexistante |
| `modification_note` | Modification d'une note | RG-26 | non — note inexistante |
| `validation_programme` | Validation d'un programme | RG-26 | non — programme inexistant |
| `rejet_programme` | Rejet d'un programme | RG-26 | non — programme inexistant |
| `selection_sujet` | Sélection d'un sujet d'examen | RG-26 | non — sujet inexistant |
| `acces_refuse` | Accès refusé | hors RG-26 | oui (US-ADM-03) |
| `modification_habilitations` | Modification des habilitations | hors RG-26 | oui (US-ADM-03) |
| `consultation_journal` | Consultation du journal | hors RG-26 | oui (US-ADM-04) |

## Le couple objet concerné

`objet_type`/`objet_identifiant` — champs libres, jamais une clé étrangère
(D-15). Valeurs actuellement posées par les services existants :

| `objet_type` | `objet_identifiant` | Posé par |
|---|---|---|
| `utilisateur` | identifiant du compte | `ServiceCompte` (création, modification, changement de profil, désactivation, réactivation) |
| `permission` | code de la permission refusée | `verifier_habilitation` |
| `groupe_habilitation` | nom du groupe | `initialiser_habilitations --reinitialiser` |
| `croisement_habilitation` | `<groupe>:<domaine>` | `ServiceMatriceHabilitations` |

Toute nouvelle nature qui désigne un objet réel choisit un `objet_type`
court et stable (même esprit que les codes de domaine d'habilitation, D-11) —
pas de convention imposée au-delà de la cohérence avec ce tableau.

## Contrat d'adresse — A1, accès ciblé depuis un objet

`GET /journal/?objet_type=<type>&objet_identifiant=<identifiant>` présélectionne
le filtre sur l'objet concerné (formulaire pré-rempli, jeton de filtre actif,
résultat déjà restreint). Aucun autre paramètre requis. Une future fiche
(évaluation, programme…) n'a qu'à construire ce lien avec le `objet_type`
qu'elle utilise pour journaliser ses propres actions — pas de mécanisme
supplémentaire à prévoir côté écran de consultation.

## `valeur_avant`/`valeur_apres`

Liste blanche déclarée par le service appelant (D-15, § 2.6 du Prompt 04) —
jamais une sérialisation d'objet. Peuplés aujourd'hui pour deux natures qui
ont un avant/après réel :

| Nature | `valeur_avant` / `valeur_apres` |
|---|---|
| `changement_profil` | `{"profil": <code>}` |
| `modification_habilitations` (croisement de matrice) | `{"lecture": bool, "ecriture": bool}` |

Les autres natures existantes n'ont pas d'avant/après naturel (création,
désactivation, réactivation, accès refusé, consultation) et laissent ces
deux champs à `null`.

## Réponse à la question de l'Étape 0 — seconde connexion de test

Voir `docs/suivi/DECISIONS.md`, D-13 : la configuration de test **ne
permettait pas** une seconde connexion sous `pfe_cit_app` avant correctif
(`conftest.py` racine) — `pfe_cit_app` n'avait aucun privilège du tout sur
`test_pfe_cit`, vérifié empiriquement avant d'écrire un seul test.

## Écarts à RG-26 / RG-27

Aucun quant à l'immuabilité (RG-27, prouvée par connexion réelle sous
`pfe_cit_app`). Trois natures hors RG-26 signalées ci-dessus et en D-16, à
porter au cahier des charges.
