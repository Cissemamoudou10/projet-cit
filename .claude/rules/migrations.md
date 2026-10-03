---
paths:
  - "**/migrations/**.py"
---

# Migrations et contraintes en base

Le détail figure dans `docs/conception/14-note-implementation.md`, sections 5 et 8.
Une migration appliquée ailleurs que sur un poste de développement ne se modifie
plus : elle se corrige par une migration suivante.

## Nommage

| Type | Préfixe | Exemple |
|---|---|---|
| Vérification | `ck_` | `ck_evaluation_perimetre` |
| Unicité | `uq_` | `uq_grille_active` |
| Exclusion | `ex_` | `ex_indispo_chevauchement` |
| Index | `idx_` | `idx_seance_debut_fin` |

Un test d'architecture vérifie ce nommage.

## Contraintes de vérification

| Nom | Table | Objet |
|---|---|---|
| `ck_evaluation_perimetre` | evaluation | exactement un de `session_id` ou `brigade_id` renseigné |
| `ck_surveillance_nature` | surveillance | exactement un de `instructeur_id` ou `nom_libre` |
| `ck_prerequis_non_reflexif` | prerequis | un élément n'est pas son propre prérequis |
| `ck_volume_positif` | element_referentiel | volume horaire prescrit strictement positif |
| `ck_intervalle_*` | session, indisponibilite, periode_calendrier, seance, creneau_type | fin strictement postérieure au début |
| `ck_domaine_*` | toutes les énumérations | valeur dans la liste admise |

## Unicités composites

| Nom | Table | Colonnes | Règle |
|---|---|---|---|
| `uq_element_referentiel` | element_referentiel | formation, matiere | `RG-06` |
| `uq_qualification` | qualification | instructeur, matiere | une seule fois |
| `uq_prerequis` | prerequis | element_cible, element_requis | pas de doublon |
| `uq_stagiaire_matricule` | stagiaire | session, matricule | `RG-17` |
| `uq_programme_semaine` | programme_hebdomadaire | lundi_de_semaine | un seul par semaine, centre entier |
| `uq_creneau_type` | creneau_type | grille, jour_semaine, rang | pas de doublon de rang |
| `uq_ligne_programme` | ligne_programme | seance, brigade | une brigade une fois par séance |

**L'unicité de désignation d'une brigade au sein du type de formation ne descend
pas en base** : elle remonte trois niveaux de relations. Elle est en couche
services.

## Index uniques partiels

Construction propre à PostgreSQL, plus économe qu'un déclencheur.

| Nom | Table | Condition | Règle |
|---|---|---|---|
| `uq_grille_active` | grille_horaire | `WHERE active` | `RG-62` — une seule grille active |
| `uq_sujet_un_seul_retenu` | sujet | `WHERE retenu`, unique sur evaluation | `RG-50` — nom corrigé à l'implantation (US-EVAL-03, D-196) |
| `uq_affectation_ouverte` | affectation_brigade | `WHERE date_fin IS NULL`, unique sur stagiaire | `RG-20` — historisation sans perte d'invariant |

## Contrainte d'exclusion

`ex_indispo_chevauchement` sur `indisponibilite` : deux lignes de même instructeur
n'ont pas d'intervalles sécants (`RG-24`).

**Exige l'extension `btree_gist`**, à créer dans une migration distincte et
antérieure :

```python
from django.contrib.postgres.operations import BtreeGistExtension
operations = [BtreeGistExtension()]
```

**Toute migration posant une contrainte d'exclusion déclare une dépendance
explicite sur `("noyau", "0001_extensions")`** :

```python
dependencies = [
    ("ressources", "0003_precedente"),
    ("noyau", "0001_extensions"),
]
```

Sans cette ligne, l'ordre d'exécution des migrations n'est garanti par rien : le
graphe de Django ne relie pas deux migrations qui ne se référencent pas, et rien
n'empêche la contrainte d'exclusion d'être posée avant l'extension sur une base
neuve — c'est-à-dire exactement au moment du déploiement au CIT, jamais en
développement où l'ordre accidentel a de bonnes chances d'être le bon.

## Journal immuable

`RG-27` interdit toute modification et toute suppression d'une entrée de journal,
administrateur compris. Une règle applicative ne suffit pas : révoquer `UPDATE` et
`DELETE` sur `entree_journal` pour le rôle de connexion, l'insertion demeurant
permise. Une trace qu'on peut effacer ne prouve rien.

## Index de performance

Dictés par les lectures que les cas d'utilisation imposent, non ajoutés par
précaution. La génération lit toutes les séances de toutes les sessions actives
d'une semaine : c'est la requête la plus lourde, et BNF-04 la borne à cinq minutes.

| Nom | Table | Colonnes |
|---|---|---|
| `idx_seance_debut_fin` | seance | date_heure_debut, date_heure_fin |
| `idx_seance_instructeur_debut` | seance | instructeur, date_heure_debut |
| `idx_seance_lieu_debut` | seance | lieu, date_heure_debut |
| `idx_seance_element` | seance | element_referentiel |
| `idx_ligne_brigade` | ligne_programme | brigade |
| `idx_indispo_instructeur` | indisponibilite | instructeur, date_heure_debut |
| `idx_periode_debut_fin` | periode_calendrier | date_heure_debut, date_heure_fin |
| `idx_note_evaluation` | note | evaluation |
| `idx_note_stagiaire` | note | stagiaire |
| `idx_journal_horodatage` | entree_journal | `cree_le` décroissant (colonne réelle, voir docs/suivi/DECISIONS.md, D-04) |
| `idx_journal_nature_auteur` | entree_journal | type_action, auteur (posé en US-ADM-04, D-15 — pas `idx_journal_objet` : le filtre par objet ne porte pas d'index composé, `objet_type`/`objet_identifiant` existent mais sans index dédié) |

Django indexe seul les clés étrangères : n'ajoute que les index composites.

## Écriture

Les constructions sans équivalent déclaratif dans l'ORM — index partiels,
contrainte d'exclusion, révocation de privilèges — s'écrivent en SQL explicite,
commenté, et **réversible**.

**Ne crée jamais de migration de données contenant des valeurs réelles du CIT.**
