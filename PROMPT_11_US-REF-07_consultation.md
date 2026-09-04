# Prompt Claude Code — 11 · US-REF-07 · Consulter le référentiel depuis les autres cellules

> Sprint 1, ligne WBS 5.1.13. Must, 2 points, 2,6 h estimées.
> Prérequis : US-REF-06 est finie. **Dernière story du paquetage P2.**
> À coller dans une session neuve, après `/clear`.

---

Nous développons **US-REF-07 — Consulter le référentiel depuis les autres cellules**,
cas d'utilisation **CU-P2-08**, fiche **générique plus écarts**.

Deux points seulement, et ils le resteront **si tu ne construis pas d'écrans
parallèles**. Voir § 2.1 : c'est la décision qui fait toute cette story.

Tu suis les huit étapes du workflow `/story`, avec arrêt obligatoire sur ma validation.

## Traçabilité

`BF-REF-07 → US-REF-07 → CU-P2-08 → RG-02 → CLS-02`

---

# 1 · Le besoin

*En tant que membre de la cellule planification ou examens, je veux consulter le
référentiel en lecture seule, afin de disposer d'une information fiable sans risquer de
l'altérer.*

## Critères d'acceptation — backlog v7

1. Les formations, matières, volumes horaires et prérequis sont consultables par les
   cellules planification et examens.
2. **Aucun bouton** de création, de modification ou de suppression n'est accessible à
   ces profils.
3. Une tentative de modification **par appel direct** est refusée **côté serveur**.
4. Toute modification du référentiel par la cellule pédagogique est **immédiatement
   visible** par les autres cellules.

## L'écart à la fiche générique

*Lecture seule, sans exception : aucune action de modification n'est offerte aux profils
planification, examens **et Direction de Formation**. La consultation présente le
référentiel **complet** : volumes prescrits, catégories de lieu, objectifs pédagogiques
et prérequis.*

**Note d'écart.** Le critère 1 ne nomme que planification et examens ; la fiche et la
matrice § 11.2 accordent aussi la lecture à la Direction de Formation. La matrice fait
foi — c'est elle qui a servi à construire le catalogue des permissions à US-ADM-03.
Les trois profils lisent. Signale-le, sans en faire une affaire : c'est une omission de
rédaction du backlog, pas une contradiction de fond.

---

# 2 · Deux décisions déjà tranchées

## 2.1 · Aucun écran parallèle. Les écrans existants s'adaptent.

La tentation est d'écrire un jeu d'écrans en lecture seule à côté de ceux de la cellule
pédagogique. **Ne le fais pas.**

La raison est mécanique : le jour où un champ s'ajoute au référentiel, il sera ajouté à
l'écran d'édition et oublié dans la copie en lecture. Les deux divergeront sans qu'aucun
test ne le signale, et la cellule planification travaillera sur une vue incomplète du
cursus — exactement ce que le critère 4 cherche à empêcher.

Les écrans d'US-REF-01, US-REF-02, US-REF-03 et US-REF-06 **sont** les écrans de
consultation. Ce qui change selon le profil :

| Élément | Profil pédagogique | Les trois autres |
|---|---|---|
| Tableau éditable en ligne (§ 3.16) | Édition sur place | **Tableau dense (§ 3.08)**, lecture |
| Boutons créer, modifier, supprimer | Présents | Absents |
| Boutons d'action de ligne (§ 3.40) | Présents | Absents |
| Jetons de prérequis retirables | Retirables | Simples jetons |
| Formulaires et dialogues | Accessibles | Inaccessibles, y compris par adresse directe |

Le basculement se fait par `a_permission` — l'appel **silencieux** posé à US-ADM-03, pas
`verifier_habilitation`, qui journaliserait un refus à chaque affichage.

Une seule chose s'ajoute : **un écran de consultation consolidé**, § 3.

## 2.2 · Le critère 4 n'appelle aucun code, et interdit d'en écrire

*Toute modification est immédiatement visible par les autres cellules.* Il n'y a aucun
mécanisme de rafraîchissement, de notification ou de synchronisation à implanter. Le
critère est satisfait par construction dès lors que la consultation **lit la base**.

Il est violé si quelqu'un ajoute un cache, une vue matérialisée, une copie de travail ou
un instantané « pour ne pas recharger à chaque fois ».

C'est la même famille de piège que le critère 6 d'US-REF-02, où le danger était de
recopier l'intitulé d'une matière. Ici, le danger est de mettre en cache.

**Écris un test qui modifie une donnée puis la relit par le chemin de consultation**, et
consigne l'interdiction dans `docs/suivi/` : *aucune mise en cache du référentiel, à
aucun niveau*. Sur un intranet isolé servant quelques dizaines d'agents, il n'y a aucun
problème de performance à résoudre — donc aucune raison d'en créer un de cohérence.

---

# 3 · L'écran consolidé

L'écart exige que la consultation présente **le référentiel complet**. Aujourd'hui,
l'information est répartie sur quatre écrans : la formation, ses matières et volumes,
les objectifs, les prérequis. Une cellule planification qui prépare un programme n'a pas
à naviguer entre quatre pages.

Un écran unique, en lecture, organisé en onglets (§ 3.42) ou en sections :

1. **Identification** — formation, type, spécialité, durée
2. **Matières et volumes** — tableau dense (§ 3.08) : matière, volume prescrit,
   catégorie de lieu, type de lieu partagé le cas échéant. Total en bloc de statistique
   (§ 3.35), avec l'avertissement d'écart s'il y a lieu, **en lecture**
3. **Objectifs pédagogiques** — par matière, en lignes dépliables (§ 3.15)
4. **Prérequis** — le tableau des liens directs et l'ordre de progression

**Tu réutilises les fragments de gabarit déjà écrits.** Si tu te surprends à recopier du
balisage, découpe le fragment d'origine en inclusions plutôt que de le dupliquer — la
raison est celle du § 2.1.

Cet écran est accessible à **tous les profils ayant `referentiel_lecture`**, y compris
la cellule pédagogique : une vue d'ensemble lui est utile aussi.

`npm run css:build` avant les tests d'interface.

---

# 4 · Étape 0 — Explorer

Lis les gabarits des quatre écrans du paquetage P2, `app/noyau/habilitations.py`, et
`.claude/rules/gabarits.md`.

**Rends-moi la liste des fragments réutilisables** et ceux qu'il faudra découper. Si la
réponse est longue, la story dépassera ses deux points, et je veux le savoir avant.

# 5 · Étape 1 — Planifier. Attends ma validation.

Plan complet. **N'écris rien avant mon accord.**

---

# 6 · Tests

## Le masquage — critère 2

Un test **paramétré sur les quatre profils**. Pour chacun, sur chacun des cinq écrans du
paquetage : le balisage rendu contient, ou ne contient pas, les commandes d'écriture.

| Profil | Attendu |
|---|---|
| Cellule pédagogique | Toutes les commandes présentes |
| Cellule planification | Aucune |
| Cellule examens | Aucune |
| Direction de Formation | Aucune |

Vingt combinaisons. Écris-les par paramétrage, pas à la main.

## Le refus serveur — critère 3

Pour chaque profil sans écriture, et pour **chaque adresse d'écriture du paquetage** —
création, modification, archivage, suppression, ajout et retrait de prérequis,
réordonnancement d'objectif : appel direct, refus attendu.

| Test | Vérifie |
|---|---|
| Appel direct en écriture par un profil en lecture → refus | Critère 3 |
| Le refus est journalisé une fois | US-ADM-03, § 2.2 |
| L'affichage d'un écran masqué **ne journalise rien** | US-ADM-03, § 2.2 |
| Le refus ne divulgue pas l'existence de l'élément | E4 de la fiche générique |

Le troisième est facile à casser : il suffit d'employer `verifier_habilitation` au lieu
d'`a_permission` pour masquer un bouton, et le journal se remplit à chaque page.

## La fraîcheur — critère 4

| Test | Vérifie |
|---|---|
| Modification par la pédagogie, relecture par la planification → valeur à jour | Critère 4 |
| Aucun cache n'est configuré sur les vues de consultation | § 2.2 |

## L'écran consolidé — critère 1 et écart

| Test | Vérifie |
|---|---|
| Il présente formations, matières, volumes, catégories de lieu, objectifs et prérequis | Écart |
| Les trois profils en lecture y accèdent | Critère 1, matrice § 11.2 |
| Aucune commande d'écriture n'y figure, pour aucun profil | Écart, *sans exception* |

## Non-régression

La suite complète des dix stories précédentes passe sans modification. **Elle est ici
plus qu'une formalité** : cette story touche aux gabarits de tout le paquetage.

---

# 7 · Vérification et livraison

- Les quinze tests d'architecture passent
- `ruff check` et `ruff format --check` propres
- **Aucune migration** : cette story n'ajoute aucune donnée
- `npm run css:build` rejoué
- Relecture par le sous-agent `relecteur-conception`
- `docs/suivi/` : l'interdiction de mise en cache, la note d'écart sur la Direction de
  Formation, les fragments découpés, le temps réel passé
- Commit portant la ligne de traçabilité

---

# 8 · Clôture du paquetage P2

Cette story terminée, le paquetage référentiel est complet, à l'exception d'US-REF-09
— historique des modifications, Should, sprint 4.

**Rends-moi un état des reports consignés depuis US-REF-00** : lesquels sont refermés,
lesquels restent ouverts, et vers quelle story chacun pointe. Ils devront tous être
vérifiés à la revue de sprint du 12 septembre, et c'est la matrice de traçabilité qui
sera regardée.

---

# 9 · Hors périmètre

- L'historique des modifications → **US-REF-09**, Should, sprint 4
- L'export ou l'impression du référentiel : aucun critère ne l'exige. Si tu juges que la
  feuille d'impression de la charte s'applique naturellement à l'écran consolidé,
  **propose-le sans l'implanter**
- Toute notification aux autres cellules lors d'une modification : voir § 2.2

# 10 · Définition de fini

Les quatre critères sont couverts par un test nommé, aucun écran parallèle n'a été créé,
le masquage emploie l'appel silencieux et non celui qui journalise, chaque adresse
d'écriture du paquetage refuse les profils en lecture, aucun cache n'existe sur le
chemin de consultation, l'écran consolidé présente le référentiel complet, et l'état des
reports du paquetage est rendu.

Commence par l'étape 0.
