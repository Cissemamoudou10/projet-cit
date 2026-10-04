---
paths:
  - "**/services/**.py"
  - "**/services.py"
---

# Couche services

Toute la logique métier vit ici. Les vues appellent des services, jamais l'inverse.

## Les huit contraintes qui ne descendent pas en base

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
8. **Doublon exact d'une période de calendrier** (RG-29, US-PLAN-01) — mêmes
   bornes, mêmes cibles (deux relations multiples indépendantes), même nature ;
   `ServicePeriodeCalendrier._analyser_chevauchement` compare une période
   proposée à toute période existante dont les bornes se recoupent, portée par
   portée. Voir `docs/suivi/DECISIONS.md`, D-127.

## Le service de contrôle des contraintes dures

`ServiceContraintes` est l'**implantation unique** des six règles RG-34 à RG-39.
Il est appelé par la génération, la modification manuelle, le regroupement et la
duplication. Ne duplique jamais ces contrôles ailleurs : un programme généré et
un programme saisi doivent obéir aux mêmes règles.

Il retourne **toutes** les règles violées, pas seulement la première, et désigne
l'élément en cause — l'instructeur déjà affecté et à quelle brigade, le lieu
occupé et par qui. Un refus non motivé est inexploitable.

Il **n'écrit rien** : un contrôle appelé pour prévisualiser une modification
envisagée doit pouvoir être appelé sans conséquence.

## La garde mécanique d'une porte d'écriture unique

Quand une story affirme qu'« un seul chemin » écrit une entité — le service de
contrôle est unique et l'ensemble des chemins d'affectation y passe, sans
exception (US-PLAN-04, § 5, Prompt 30) — l'affirmation ne vaut rien tant que
rien ne la vérifie : c'est la leçon du sprint 1 (36 refus d'habilitation
manquants, découverts seulement par un inventaire, refermés par un test de
garde inscrit en définition de fini, sur le modèle de la couverture HTTP,
`.claude/rules/tests.md`).

`planification.services.ecriture.ServiceEcritureSeance` est la seule méthode
du projet autorisée à instancier ou enregistrer `Seance`/`LigneProgramme` — un
test d'architecture (`tests/architecture/test_couches.py::
test_seule_la_porte_d_ecriture_instancie_seance_ou_ligne_programme`) scanne
tout le projet, hors migrations et fabriques de test, et échoue si ces deux
modèles sont construits ailleurs. Toute future entité pour laquelle plusieurs
cas d'utilisation (génération, saisie manuelle, regroupement, duplication...)
doivent produire le même contrôle suit ce patron : une porte d'écriture
nommée, un test d'architecture qui vérifie qu'elle est la seule.

## Les neuf services

`ServiceSujet` s'est détaché de `ServiceEvaluation` à US-EVAL-03 (D-206,
docs/suivi/DECISIONS.md) : la confidentialité des sujets (A5, visibilité
réservée à `evaluations_ecriture` seule, écran dédié) et leur journalisation
dédiée (A6) justifient une classe séparée plutôt qu'une méthode de plus sur
`ServiceEvaluation` — neuf services désormais, pas huit.

| Service | Responsabilité |
|---|---|
| `ServiceReferentiel` | matières programmables, volumes, prérequis, coefficients |
| `ServiceRessources` | disponibilité instructeurs et lieux, qualifications, calendrier, grille active |
| `ServiceGeneration` | construction du programme hebdomadaire |
| `ServiceContraintes` | les six contraintes dures |
| `ServiceCircuitProgramme` | machine à états du programme (US-VAL-03) : transitions, garde de modification, validation et signature |
| `ServiceEvaluation` | évaluations, notes, moyennes |
| `ServiceSujet` | sujets d'examen, sujet retenu (US-EVAL-03) |
| `ServiceSuivi` | prescrit et réalisé, progression réalisée hebdomadaire |
| `ServiceDocument` | production des documents depuis les gabarits |

`ServiceRessources` appartient à l'application `ressources` et non à
`planification` : les évaluations l'appellent aussi. L'y placer créerait une
dépendance circulaire.

## Règle d'écriture

Un service ne connaît pas la requête HTTP. Il reçoit des objets ou des
identifiants, retourne des objets ou lève une exception métier. Aucun `request`,
aucun `HttpResponse`, aucun `messages.success`.
