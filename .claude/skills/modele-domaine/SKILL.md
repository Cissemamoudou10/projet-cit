---
name: modele-domaine
description: Les trente classes du modèle du domaine, leurs associations et leurs cardinalités. À consulter avant d'écrire ou de modifier un modèle Django, de créer une migration, ou de décider où placer un attribut.
---

# Modèle du domaine

Trente classes, douze énumérations, deux classes d'association, neuf attributs
dérivés. Le diagramme complet fait foi : `docs/conception/13-diagramme-classes.md`.

## Répartition en applications

| Application | Classes |
|---|---|
| `noyau` | *aucune entité métier* — horodatage, habilitation, gabarits |
| `administration` | Utilisateur, EntreeJournal |
| `referentiel` | TypeFormation, Formation, Matiere, ElementReferentiel, ObjectifPedagogique |
| `organisation` | Session, Brigade, Stagiaire, AffectationBrigade |
| `ressources` | Instructeur, Qualification, Indisponibilite, Lieu, GrilleHoraire, CreneauType, PeriodeCalendrier, NatureEvenement |
| `planification` | ProgrammeHebdomadaire, Seance, LigneProgramme, NonExecution, Avenant |
| `evaluations` | Evaluation, Sujet, OrganisationEpreuve, Surveillance, Note, ProcesVerbal |

**Ordre de dépendance :** P1 ne dépend de rien · P2 de P1 · P3 de P2 et P4 · P4
de P2 · P5 de P2, P3 et P4 · P6 de P3 et P5. Ne crée jamais de dépendance
inverse.

## Les associations qui comptent

**ElementReferentiel** — classe d'association entre `Formation` et `Matiere`,
unicité composite sur le couple, clé primaire technique. Elle porte
`volume_horaire_prescrit`, `coefficient`, `categorie_lieu_requise`,
`poids_formatif`, `poids_certificatif`. C'est le **pivot du modèle** : les
séances, les évaluations et le suivi la référencent — jamais la matière seule.

**Prerequis** — association réflexive sur `ElementReferentiel`, et non sur
`Matiere`. Deux éléments liés appartiennent donc nécessairement au même
référentiel : la règle est portée par la structure, pas par du code.

**Qualification** — classe d'association entre `Instructeur` et `Matiere` **du
catalogue**. Un instructeur habilité pour une matière l'est indépendamment de la
formation où elle est enseignée.

**AffectationBrigade** — rattachement **historisé** d'un stagiaire à une brigade,
avec date d'effet et date de fin facultative. La brigade courante est celle dont
la date de fin est vide. Un index unique partiel garantit au plus une affectation
ouverte par stagiaire.

**Seance et LigneProgramme** — la séance est l'événement, la ligne la rattache à
une brigade. Une séance porte une à plusieurs lignes. Cette distinction est ce
qui empêche de surévaluer la charge d'un instructeur sur une séance regroupée.

**PeriodeCalendrier** — porte **deux ensembles de cibles**, sessions et brigades,
tous deux éventuellement vides. Les deux vides : la portée est le centre entier.
La portée est **dérivée**, jamais stockée.

**Evaluation** — porte `session` et `brigade`, tous deux facultatifs, avec une
contrainte imposant qu'**exactement un des deux** soit renseigné selon le
périmètre.

**Surveillance** — porte `instructeur` facultatif **et** `nom_libre` facultatif,
l'un excluant l'autre.

**Matiere → Instructeur** — association facultative « chef de module », avec une
date de désignation portée par la matière.

## Machine à états du programme

`brouillon → soumis → validé ou rejeté` · `rejeté → brouillon` · `validé →
affiché` après enregistrement de la signature · `validé ou affiché → brouillon`
uniquement lors d'un traitement d'indisponibilité avant affichage.

Après affichage, une modification **ne fait pas retomber à brouillon** : la séance
porte un avenant.

## Ce qui n'existe pas et ne doit pas être créé

- Pas d'entité « session d'examens » : la période bloquante du calendrier en tient
  lieu, et le regroupement des épreuves se calcule par filtre sur la période.
- Pas d'attribut de modalité d'enseignement : le projet de fin d'études est un
  module enseigné comme les autres.
- Pas de dates de session dans le calendrier : elles sont projetées depuis
  `Session`, seule source de vérité.
- Pas de candidats aux tests d'admission : la story est de priorité Could et
  l'entité n'est pas modélisée.
