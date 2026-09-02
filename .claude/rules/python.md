---
paths:
  - "**/*.py"
---

# Qualité du code Python

## Taille — la modularité se mesure

| Élément | Limite | Si dépassée |
|---|---|---|
| Fichier | 400 lignes | Scinder en module : `services/generation.py`, `services/contraintes.py` |
| Fonction ou méthode | 40 lignes | Extraire des fonctions nommées |
| Classe | 200 lignes | Déplacer la logique dans un service |
| Paramètres d'une fonction | 5 | Regrouper dans un objet ou un dataclass |
| Niveaux d'imbrication | 3 | Sortie anticipée, extraction |

Un test d'architecture vérifie les deux premières. Ce ne sont pas des
recommandations.

## Organisation d'une application

```
referentiel/
├── models/            un fichier par agrégat si models.py dépasse 400 lignes
├── services/          un fichier par domaine fonctionnel, jamais de fourre-tout
├── views/
├── selectors.py       requêtes de lecture complexes, séparées des services
├── exceptions.py      hiérarchie d'exceptions métier de l'application
├── constantes.py      valeurs de domaine ; les valeurs paramétrables vont en base
├── forms.py  urls.py  admin.py
└── tests/
```

Un module `services.py` unique qui grossit est un défaut : le scinder dès qu'il
dépasse deux domaines fonctionnels.

## Erreurs

Chaque application définit sa hiérarchie dans `exceptions.py`, dérivée d'une
exception racine du projet :

```python
class ErreurReferentiel(ErreurMetier): ...
class MatiereDejaRattachee(ErreurReferentiel): ...
class CycleDePrerequis(ErreurReferentiel): ...
```

**Jamais de `ValueError` ni d'`Exception` nue** levée depuis un service : l'appelant
ne peut pas distinguer un refus métier d'un défaut technique.

Un message d'exception métier indique **l'action corrective**, pas seulement le
refus. Il porte les éléments en cause — la matière concernée, la chaîne du cycle,
l'instructeur déjà affecté et à quelle brigade.

## Transactions

**Toute opération écrivant dans plusieurs tables est encadrée par
`transaction.atomic`.** Sans exception.

Cas critiques : l'import de stagiaires — `RG-18` impose que tout soit enregistré
ou rien ; l'enregistrement d'un programme généré et de ses lignes ; la génération
d'un procès-verbal, qui verrouille les notes ; la transition d'état d'un programme
et sa journalisation.

Un import partiellement appliqué sur une liste nominative laisse un état
impossible à diagnostiquer.

## Requêtes

**Aucune requête dans une boucle.** C'est le défaut le plus coûteux du projet :
`SEQ-01` lit les séances de toutes les sessions actives, et BNF-04 fixe la
génération à cinq minutes.

`select_related` pour les clés étrangères, `prefetch_related` pour les relations
inverses et les plusieurs-à-plusieurs. Les vues de liste chargent en une requête
ce qu'elles afficheront.

Les filtres métier récurrents deviennent des méthodes de `QuerySet` :
`Seance.objects.de_la_semaine(lundi).du_centre()`. Elles se composent et se
testent.

Les lectures complexes vont dans `selectors.py`, pas dans les services : un
service décide, un sélecteur rapporte.

## Nombres et seuils

**Aucune valeur littérale sans nom.** Un `5` isolé dans le code est indéchiffrable
six semaines plus tard.

Trois destinations, dans cet ordre :

1. **Table de paramétrage** si le terrain doit pouvoir la changer — seuil d'alerte
   d'écart, durée de verrouillage de compte, poids par type d'évaluation, effet
   par défaut d'une nature d'événement (BNF-13)
2. **Réglages Django** si c'est technique et stable — durée maximale de génération
3. **Constante nommée** dans `constantes.py` sinon

## Signaux Django

**Aucune règle métier dans un signal.** Un signal exécute du code invisible depuis
l'appelant : impossible à suivre, difficile à tester, source de cascades
inattendues.

Ce qu'un service doit faire, un service le fait explicitement. Les signaux sont
tolérés pour des effets purement techniques — invalidation de cache — et jamais
pour une règle du domaine.

## Style

Ligne à 100 caractères. Imports triés : bibliothèque standard, tiers, projet.
`ruff` fait foi ; lance `ruff check` et `ruff format` avant de livrer.

**Annotations de type sur les signatures publiques des services.** Elles
documentent le contrat mieux qu'un commentaire et se vérifient.

Fonctions nommées par un verbe à l'infinitif : `composer_referentiel`,
`verifier_disponibilite`. Booléens préfixés : `est_regroupee`, `peut_afficher`.

## Commentaires

Un commentaire explique **pourquoi**, jamais **quoi**. Si le code demande un
commentaire pour être compris, renomme-le ou extrais une fonction.

Docstring sur les fonctions publiques d'un service, quand le contrat n'est pas
évident : ce que la fonction garantit, ce qu'elle lève.

**Un commentaire qui paraphrase le code est un défaut**, pas une politesse.

## Duplication

Deux occurrences d'une même logique : extraire. Trois : c'était déjà trop tard.

La règle vaut particulièrement pour les contrôles de contraintes : ils ont **une
seule implantation**, dans `ServiceContraintes`. Un contrôle recopié dans une vue
finit par diverger.
