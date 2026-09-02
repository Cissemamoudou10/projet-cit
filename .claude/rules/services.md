---
paths:
  - "**/services/**.py"
  - "**/services.py"
---

# Couche services

Toute la logique métier vit ici. Les vues appellent des services, jamais l'inverse.

## Les sept contraintes qui ne descendent pas en base

Elles sont ici et nulle part ailleurs. Aucune ne s'exprime en SQL déclaratif.

1. **Acyclicité du graphe des prérequis** — parcours en profondeur à chaque ajout,
   et le message d'erreur affiche la chaîne formant le cycle, sans quoi la
   correction est impraticable sur un référentiel de trente matières.
2. **Nombre de sujets conditionnel au type** — deux si l'évaluation est
   certificative, un seul si elle est formative.
3. **Capacité du lieu comparée à l'effectif** — l'effectif est dérivé, il n'existe
   pas de colonne à comparer.
4. **Unicité d'affectation de l'instructeur** — l'exception de la séance regroupée
   l'exclut d'une contrainte d'exclusion en base.
5. **Créneau non bloqué par une période** — dépend de la portée, elle-même dérivée
   des cibles.
6. **Volume programmé n'excédant pas le prescrit** — porte sur une somme.
7. **Unicité de désignation de brigade par type de formation** — remonte trois
   niveaux de relations.

## Le service de contrôle des contraintes dures

`ServiceContraintes` est l'**implantation unique** des six règles RG-34 à RG-39.
Il est appelé par la génération, la modification manuelle, le regroupement et la
duplication. Ne duplique jamais ces contrôles ailleurs : un programme généré et
un programme saisi doivent obéir aux mêmes règles.

Il retourne **toutes** les règles violées, pas seulement la première, et désigne
l'élément en cause — l'instructeur déjà affecté et à quelle brigade, le lieu
occupé et par qui. Un refus non motivé est inexploitable.

## Les huit services

| Service | Responsabilité |
|---|---|
| `ServiceReferentiel` | matières programmables, volumes, prérequis, coefficients |
| `ServiceRessources` | disponibilité instructeurs et lieux, qualifications, calendrier, grille active |
| `ServiceGeneration` | construction du programme hebdomadaire |
| `ServiceContraintes` | les six contraintes dures |
| `ServiceValidation` | machine à états du programme, validation et signature |
| `ServiceEvaluation` | évaluations, sujets, notes, moyennes |
| `ServiceSuivi` | prescrit et réalisé, progression réalisée hebdomadaire |
| `ServiceDocument` | production des documents depuis les gabarits |

`ServiceRessources` appartient à l'application `ressources` et non à
`planification` : les évaluations l'appellent aussi. L'y placer créerait une
dépendance circulaire.

## Règle d'écriture

Un service ne connaît pas la requête HTTP. Il reçoit des objets ou des
identifiants, retourne des objets ou lève une exception métier. Aucun `request`,
aucun `HttpResponse`, aucun `messages.success`.
