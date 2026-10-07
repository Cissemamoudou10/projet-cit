---
paths:
  - "**/models.py"
  - "**/models/**.py"
---

# Modèles du domaine

Le diagramme de classes fait foi : `docs/conception/13-diagramme-classes.md`.
Trente classes, douze énumérations, deux classes d'association.

## Nommage

Classes en français, `PascalCase` : `ElementReferentiel`, `LigneProgramme`.
Champs en `snake_case` sans accent : `volume_horaire_prescrit`, `date_heure_debut`.
Tables préfixées par l'application : `referentiel_element_referentiel`.

**Chaque modèle déclare explicitement son `db_table` dans sa `Meta`.** Le nom de
table par défaut de Django concatène l'application et le nom de la classe sans
séparateur — `referentiel_elementreferentiel` — ce qui viole la convention
`snake_case` de la note d'implémentation §2.1. Ne compte jamais sur le nom par
défaut :

```python
class ElementReferentiel(models.Model):
    ...

    class Meta:
        db_table = "referentiel_element_referentiel"
```

## Interdits

**Aucun attribut dérivé n'est stocké.** Les neuf suivants se calculent —
propriété Python pour un objet isolé, annotation de requête pour un agrégat :

| Grandeur | Classe | Calcul |
|---|---|---|
| volume programmé | ElementReferentiel | somme des durées des séances |
| volume réalisé | ElementReferentiel | idem, programmes affichés, moins les non-exécutions |
| volume restant | ElementReferentiel | prescrit moins programmé |
| effectif réel | Brigade | affectations ouvertes de stagiaires non radiés |
| charge hebdomadaire | Instructeur | durées de ses séances, séance regroupée comptée une fois |
| portée | PeriodeCalendrier | centre si aucune cible, sinon sessions ou brigades |
| durée | Seance | fin moins début |
| est regroupée | Seance | vrai si plus d'une ligne de programme |
| volume cumulé | LigneProgramme | volume dispensé à cette brigade pour cette matière |

Les stocker créerait autant d'occasions de divergence avec la réalité.

## Types

`DecimalField` pour les notes et les coefficients, **jamais `FloatField`** : une
moyenne pondérée en flottant peut donner 11,999999 là où le calcul exact donne 12,
et la mention change.

`DateTimeField` toujours avec fuseau. Le Maroc pratique le changement d'heure ;
sans fuseau, deux heures par an sont ambiguës, dont celles du journal.

Énumérations en `TextChoices`, avec une contrainte de vérification en base.
Exception : `NatureEvenement` est une **table**, pas une énumération — le terrain
doit pouvoir ajouter une nature sans intervention sur le code.

## Suppression

`PROTECT` par défaut sur toute clé étrangère vers une entité de référence.
`CASCADE` uniquement en composition stricte : créneau type vers grille, ligne de
programme vers séance, sujet vers évaluation, surveillance vers organisation
d'épreuve, non-exécution vers son porteur. L'avenant (US-PLAN-05) est
l'exception : `PROTECT` vers la séance, puisqu'il est la trace d'une décision
qui ne doit jamais disparaître avec elle, même quand la séance s'efface par un
autre chemin (D-237).
`SET_NULL` pour les références facultatives : séance vers créneau type, séance
vers évaluation.

Une cascade posée par commodité efface silencieusement des données dont personne
n'avait mesuré la portée.

## Les deux classes d'association

`ElementReferentiel` entre Formation et Matiere, unicité composite sur le couple,
clé primaire technique. Elle porte volume prescrit, coefficient, catégorie de
lieu requise, poids formatif et poids certificatif.

`Qualification` entre Instructeur et Matiere — la matière du **catalogue**, jamais
un élément de référentiel : l'habilitation est indépendante de la formation.
