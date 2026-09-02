# Prompt Claude Code — 03 · US-ADM-03 · Restreindre l'accès selon le profil

> Sprint 1, ligne WBS 5.1.4. Must, 5 points, 6,5 h estimées. Story en **binômage**.
> Prérequis : US-ADM-02 est finie.
> À coller dans une session neuve, après `/clear`.

---

Nous développons **US-ADM-03 — Restreindre l'accès selon le profil**.

**Ce n'est pas un cas d'utilisation.** Les livrables le disent explicitement : c'est
une contrainte transversale qui s'applique à *tous* les cas d'utilisation du système,
formalisée par RG-02 et par la matrice profils / paquetages de la section 11.2 du
dossier des cas d'utilisation. Il n'y a donc ni scénario nominal, ni exception à
implanter : il y a un mécanisme, un catalogue de permissions, un écran de
configuration, et la reprise des contrôles déjà écrits.

Tu suis les huit étapes du workflow `/story`, avec arrêt obligatoire sur ma
validation avant l'implantation.

## Traçabilité

`BF-ADM-03 → US-ADM-03 → RG-02, RG-02 bis, RG-26 → matrice § 11.2`

---

# 1 · Le besoin

*En tant que responsable de la sécurité, je veux que chaque utilisateur n'accède
qu'aux fonctionnalités et données de son profil, afin de protéger les informations
sensibles.*

## Critères d'acceptation — backlog v7

1. Cinq profils sont définis : pédagogique, planification, examens, Direction de
   Formation et administrateur.
2. Le profil Direction de Formation dispose d'un accès **en lecture seule** aux
   tableaux de bord et à la traçabilité, sans droit de modification.
3. Un utilisateur de la cellule planification consulte le référentiel **sans pouvoir
   le modifier**.
4. Un utilisateur de la cellule planification **n'accède à aucune note ni résultat
   d'évaluation**.
5. Toute tentative d'accès à une ressource non autorisée renvoie un **refus
   explicite** et est **journalisée**.
6. Les restrictions sont appliquées **côté serveur** et non uniquement par masquage de
   l'interface.

## Les deux règles

| Code | Énoncé |
|---|---|
| **RG-02** | Le profil de l'acteur l'habilite, ou non, à chaque cas d'utilisation |
| **RG-02 bis** | Le mécanisme est **configurable par l'administrateur** : les droits attachés aux profils sont des données, modifiables sans toucher au code |

## La matrice — § 11.2, source unique

**É** écriture, **L** lecture seule, case vide accès refusé.

| Domaine | Pédagogique | Planification | Examens | Direction | Administrateur |
|---|---|---|---|---|---|
| P1 — Administration | | | | | **É** |
| P2 — Référentiel | **É** | L | L | L | |
| P3 — Organisation | **É** | L | L | L | |
| P4 — Instructeurs et qualifications | **É** | L | | L | |
| P4 — Lieux et calendrier | L | **É** | L | L | |
| P5 — Génération et modification du programme | | **É** | | L | |
| P5 — Validation du programme | **É** | L | | L | |
| P6 — Évaluations | | | **É** | L | |
| P6 — Suivi | **É** | L | L | L | |

Neuf domaines, pas six paquetages : P4 et P5 sont scindés parce que le détenteur de
l'écriture y diffère selon le domaine. **C'est cette scission qui porte la validation
croisée** — la cellule planification écrit le programme sans pouvoir le valider, la
cellule pédagogique le valide sans pouvoir l'écrire. Ne la simplifie sous aucun
prétexte.

---

# 2 · Cinq décisions déjà tranchées

## 2.1 · Les permissions sont par domaine, pas par modèle

Django crée automatiquement quatre permissions par modèle. Sept des neuf domaines de
la matrice appartiennent à des applications qui n'ont **aucun modèle** : elles seront
écrites aux sprints 2 à 4. Un catalogue fondé sur les permissions de modèle serait
donc incomplet aujourd'hui, et devrait être repris à chaque story — c'est-à-dire
oublié une fois sur trois.

Le catalogue est donc **fondé sur les neuf domaines de la matrice**, avec deux niveaux
chacun : lecture et écriture. Dix-huit permissions, définies une fois, valables pour
tout le projet.

Déclare-les dans `app/noyau/models.py`, sur un modèle sans table :

```
class Habilitation(models.Model):
    class Meta:
        managed = False          # aucune table
        default_permissions = () # pas d'add/change/delete/view
        permissions = [ ... ]    # les dix-huit
```

Ce n'est pas un détournement : c'est l'idiome prévu par Django pour des permissions
qui ne portent pas sur des lignes. Aucune migration de table n'en résulte.

Nomme les permissions en français, sans accents, sur le motif
`referentiel_lecture`, `referentiel_ecriture`, `programme_validation_ecriture`.

## 2.2 · Deux appels distincts, et c'est ce qui empêche le journal de déborder

Le noyau expose déjà `verifier_habilitation`. Tu ajoutes un second point d'entrée, et
la distinction est la clé de cette story :

| Appel | Comportement | Emploi |
|---|---|---|
| `verifier_habilitation(utilisateur, permission)` | Lève `ErreurHabilitation` **et journalise le refus** | Couche services, à chaque opération |
| `a_permission(utilisateur, permission)` | Retourne un booléen, **silencieux** | Gabarits et navigation, pour masquer |

Sans cette séparation, chaque affichage d'un menu où une entrée est masquée écrirait
une entrée de journal. Le journal deviendrait illisible en une semaine, et le critère 5
perdrait tout intérêt : on ne journalise que les **tentatives**, pas les
non-affichages.

## 2.3 · Le masquage est une conséquence, jamais le mécanisme

Le critère 6 est explicite. L'ordre est : le service refuse, la vue traduit, le gabarit
masque. Un bouton absent n'est pas un contrôle — c'est un confort.

Corollaire à tester : **toute URL atteinte directement, sans passer par un lien, doit
être refusée avec la même rigueur.**

## 2.4 · Chaque service déclare son domaine

Pour que les stories des sprints 2 à 4 soient conformes par construction et non par
vigilance, chaque classe de service porte deux attributs de classe :

```
DOMAINE = "referentiel"
```

et un test d'architecture supplémentaire vérifie que **toute classe de service placée
sous `app/*/services/` déclare un domaine appartenant au catalogue**. Un service qui
en oublie un fait échouer la suite, immédiatement.

C'est le seul moyen d'éviter que la story suivante réintroduise un contrôle ad hoc.

## 2.5 · Les contrôles déjà écrits sont repris

`ServiceCompte` et `ServiceAuthentification` testent aujourd'hui le profil
administrateur en dur. Remplace ces tests par la permission `administration_ecriture`.
Le comportement observable ne change pas, les tests d'US-ADM-02 doivent passer sans
modification — **s'ils échouent, c'est la reprise qui est fautive, pas eux.**

Fais tourner la suite complète après cette reprise, pas seulement les tests de cette
story.

---

# 3 · Étape 0 — Explorer

Lis `app/noyau/habilitations.py`, `app/noyau/exceptions.py`, la commande
`initialiser_habilitations`, `app/administration/services/` en entier, les tests
existants, et `tests/architecture/`.

Dans `docs/charte/` : **3.08** (tableau dense), **3.23** (cases à cocher),
**3.25** (pied de formulaire), **3.30** (encadrés), **3.39** (boutons),
**3.13** (état vide).

Rends-moi l'état actuel du mécanisme et la liste des endroits où un contrôle de profil
est écrit en dur.

# 4 · Étape 1 — Planifier. Attends ma validation.

Plan complet, plus **la liste nominative des dix-huit permissions** et la matrice de
rattachement aux cinq groupes. Je la valide avant que tu écrives quoi que ce soit :
une erreur dans cette table se propagerait à toutes les stories suivantes.

---

# 5 · Le catalogue et son chargement

Étends la commande `initialiser_habilitations` du socle : elle crée les cinq groupes
— ce qu'elle fait déjà — **et leur attache les permissions de la matrice**.

Deux exigences qui se contredisent en apparence, et qu'il faut tenir ensemble :

- la commande est **idempotente** : deux exécutions donnent le même état
- elle **n'écrase pas** les réglages faits par l'administrateur, sinon RG-02 bis est
  vidée de son sens dès le premier redéploiement

Résolution : la commande n'applique la matrice qu'aux groupes **dépourvus de toute
permission**. Un drapeau `--reinitialiser` force le retour aux valeurs de la matrice,
et journalise l'opération.

---

# 6 · L'écran de configuration — RG-02 bis

`administration/templates/administration/habilitations.html`, réservé à
l'administrateur.

Un tableau (§ 3.08) : neuf lignes de domaine, cinq colonnes de profil, deux cases à
cocher par croisement — lecture et écriture (§ 3.23).

Trois exigences d'usage :

- **cocher l'écriture coche la lecture** : écrire sans pouvoir lire n'a pas de sens.
  Le contrôle est dans le service, pas seulement dans l'affichage
- un encadré (§ 3.30) rappelle que la matrice du dossier de conception est la
  référence, et signale visuellement tout croisement qui s'en écarte
- **le profil administrateur ne peut pas perdre `administration_ecriture`** — même
  logique que le dernier administrateur actif d'US-ADM-02 : le système deviendrait
  inconfigurable

Toute modification est journalisée : qui, quand, quel croisement, ancienne et nouvelle
valeur.

---

# 7 · Le refus explicite — critère 5

Une page de refus, étendant `noyau/base.html` — l'utilisateur est authentifié, il a
droit à l'ossature complète.

Elle indique **ce qui est refusé et à qui s'adresser**, conformément à BNF-10. Elle ne
révèle ni le nom technique de la permission, ni l'existence de la donnée visée.

Le refus est journalisé par `verifier_habilitation` : auteur, horodatage, permission
demandée, adresse visée.

---

# 8 · Navigation

Les rubriques se filtrent par `a_permission`, silencieusement. Un profil ne voit que
ce à quoi il a droit.

C'est ici que la Direction de Formation devient visiblement particulière : elle voit
presque tout et ne peut écrire nulle part. **Les actions d'écriture doivent disparaître
de son interface** — boutons de création, de modification, d'action de ligne — sans que
cela dispense du contrôle serveur.

---

# 9 · Tests

## Le mécanisme

| Test | Vérifie |
|---|---|
| Les cinq groupes existent après initialisation | Critère 1 |
| Chacun porte exactement les permissions de la matrice | § 11.2 |
| `verifier_habilitation` lève et journalise | Critère 5 |
| `a_permission` retourne un booléen et **n'écrit rien au journal** | § 2.2 |
| La commande est idempotente | § 5 |
| La commande n'écrase pas un réglage administrateur | RG-02 bis |
| `--reinitialiser` restaure la matrice et journalise | § 5 |

## La matrice, profil par profil

Un test **par croisement de la matrice**, soit quarante-cinq assertions. C'est
fastidieux à écrire à la main : construis-les par paramétrage à partir d'une table
littérale reproduisant § 11.2. Cette table devient la spécification exécutable de la
matrice, et toute dérive future la fait échouer.

Quatre d'entre eux sont nommément exigés par les critères :

| Test | Critère |
|---|---|
| Direction de Formation n'a **aucune** permission d'écriture, sur aucun domaine | 2 |
| Planification lit le référentiel, ne l'écrit pas | 3 |
| Planification n'a **ni lecture ni écriture** sur le domaine Évaluations | 4 |
| Planification écrit le programme mais n'a pas la validation | § 11.2, validation croisée |

## Côté serveur — critère 6

| Test | Vérifie |
|---|---|
| URL atteinte directement, sans permission → refus | Critère 6 |
| La vue masque le bouton **et** le service refuse l'appel | Critère 6 |
| Le refus est journalisé une fois, pas à chaque affichage de page | § 2.2 |

## Architecture

| Test | Vérifie |
|---|---|
| Toute classe sous `app/*/services/` déclare un `DOMAINE` du catalogue | § 2.4 |
| Aucun contrôle de profil écrit en dur ne subsiste dans le code | § 2.5 |

## Non-régression

**La suite complète d'US-ADM-01 et US-ADM-02 passe sans modification.** Cette story
touche à tous les services déjà écrits ; c'est le seul contrôle qui dise que la reprise
est fidèle.

---

# 10 · Vérification et livraison

- Les quinze tests d'architecture passent — quatorze plus celui du § 2.4
- `ruff check` et `ruff format --check` propres
- Aucune migration de table ; vérifie que le modèle sans table n'en produit pas
- `npm run css:build` rejoué
- Relecture par le sous-agent `relecteur-conception`
- `docs/suivi/` : le catalogue des dix-huit permissions, la table de rattachement, les
  écarts éventuels à § 11.2, le temps réel passé
- Commit portant la ligne de traçabilité

---

# 11 · Hors périmètre

- Écran de consultation du journal → **US-ADM-04**
- Révocation des privilèges en base sur la table de journal → **US-ADM-04**
- Restriction au niveau de la ligne — par exemple *ne voir que sa propre session* :
  la matrice est par domaine, pas par enregistrement. Aucun besoin ne l'exige
- Interface de programmation et son habilitation propre → US-ADM-05, priorité Should

# 12 · Définition de fini

Les six critères sont couverts par un test nommé, les quarante-cinq croisements de la
matrice sont exercés par un test paramétré, aucun contrôle de profil en dur ne subsiste,
tout service déclare son domaine et un test d'architecture l'impose, l'administrateur
peut modifier les droits sans toucher au code, et la suite complète des deux stories
précédentes passe sans modification.

Commence par l'étape 0.
