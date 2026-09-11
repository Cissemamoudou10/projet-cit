# Prompt 22 — US-SES-03 · Affecter une salle attitrée à chaque brigade

Sprint 2, story 3 sur 12. Must, 3 points. Lot WBS 5.2.4.

## 0. Étape 0 — vérifications avant toute ligne de code

1. ARBITRAGE RENDU, à vérifier contre le code avant d'en tirer les conséquences.
   L'association « salle attitrée » vit dans `ressources`, PAS dans
   `organisation`. Aucune clé étrangère vers `Lieu` n'est posée sur `Brigade`.
   Motifs, à reprendre dans ta décision :
   (a) l'acteur en écriture est la cellule planification (terrain du 23 août),
       qui n'a que la lecture sur P3 — porter la colonne sur `Brigade`
       obligerait à lui ouvrir l'écriture sur tout le paquetage Organisation ;
   (b) précédent D-52, qui place l'association du côté qui dépend ;
   (c) l'ordre des paquetages est P3 avant P4 — `ressources` dépend
       d'`organisation`, ce que confirme `PeriodeCalendrier` ciblant sessions et
       brigades (US-PLAN-01, ce sprint).
   Vérifie que `DEPENDANCES_AUTORISEES` porte bien `ressources` → `organisation`
   et NON l'inverse. Si le fichier dit l'inverse, ne le retourne pas d'autorité :
   vérifie d'abord qu'`organisation` n'importe réellement rien de `ressources`
   (US-SES-01 et US-SES-02 l'interdisaient), puis corrige le sens, puis
   consigne-le comme décision d'architecture avec les trois motifs ci-dessus.
   Si `organisation` importe déjà quelque chose de `ressources`, arrête-toi et
   rends-m'en compte : c'est un cycle, et il se traite avant cette story.

2. Lis le modèle `Lieu` réellement livré à US-PLAN-02 : nom exact des champs,
   valeurs de `CategorieLieu` (deux, D-53), caractère facultatif ou non de la
   capacité, existence et nom du modèle d'indisponibilité de lieu, et
   `ServiceLieu`. Ne code pas d'après ce prompt sur ces points.

3. Relis D-52 en entier. Sa méthode est celle de cette story : les vues
   symétriques vivent du côté qui dépend, les gabarits de l'autre côté ne
   portent que des `{% url %}`, et les lectures inverses passent par des chaînes
   résolues par l'ORM, jamais par un `import`.

4. Le mécanisme d'avertissement du patron : troisième utilisation ici. Si elle
   demande de le tordre, corrige le mécanisme, pas l'usage.

5. Suite `pytest` verte avant de commencer. Sinon, arrête-toi.

## 1. Ce que porte cette story

Besoin BF-SES-03. Cas d'utilisation CU-P3-03 (fiche générique + écarts), dont le
scénario est détaillé aux points 4 à 6 de CU-P3-02. Règles RG-13 et RG-14.
ACTEUR EN ÉCRITURE : LA CELLULE PLANIFICATION, et elle seule.

Critères d'acceptation du backlog v8 :

1. Une salle attitrée est affectée à une brigade pour toute la durée de la
   session.
2. La capacité de la salle doit être supérieure ou égale à l'effectif de la
   brigade ; le cas contraire est refusé.
3. Une salle attitrée ne peut être affectée simultanément à deux brigades dont
   les sessions se chevauchent.
4. La salle attitrée est utilisée par défaut pour toutes les matières ne
   requérant pas de lieu particulier.

Le critère 4 est HORS PÉRIMÈTRE : il décrit un comportement du moteur de
génération, pas une donnée à saisir. Voir § 8.

Enchaînement A2 de CU-P3-02 — changement de salle en cours de session : DANS le
périmètre. La nouvelle salle est vérifiée disponible sur la PÉRIODE RESTANTE, et
le changement est journalisé.

Exceptions E1 (capacité insuffisante, avec indication de l'écart) et E2 (salle
déjà attitrée sur une période sécante, avec désignation de la brigade occupante)
de CU-P3-02 : dans le périmètre.

## 2. Le modèle

`app/ressources/models.py`, `Meta.db_table = "ressources_salle_attitree"`.

`SalleAttitree` :

- `brigade` — `OneToOneField` vers `organisation.Brigade`, `on_delete=PROTECT`,
  `related_name="salle_attitree"`.
- `lieu` — clé étrangère vers `Lieu`, `on_delete=PROTECT`,
  `related_name="brigades_attitrees"`.

Hérite de la classe de base d'horodatage et de rattachement à l'auteur.

`OneToOne` et non clé étrangère : une brigade a au plus une salle attitrée. Le
`related_name` choisi permet à `organisation` de lire `brigade.salle_attitree`
par la relation inverse, sans le moindre `import ressources` — c'est la méthode
de D-52, et c'est ce qui rendra possible l'écran de composition d'US-SES-04.

`PROTECT` sur `lieu` : c'est lui qui referme le volet brigade de D-54.
`PROTECT` sur `brigade` : supprimer une brigade dotée d'une salle doit être un
refus explicite avec énumération, pas une suppression silencieuse en cascade.

PAS d'historisation. Contraste voulu avec `AffectationBrigade` (US-SES-06), qui
porte une date d'effet parce que RG-20 exige de dater les changements de brigade
d'un stagiaire. Ici, A2 demande seulement que le changement soit journalisé : le
journal immuable suffit, et une table d'historique ajouterait une structure que
rien n'exige. Consigne ce contraste, il sera relu.

PAS de dénormalisation de la période de la session sur cette table, même pour
rendre RG-14 exprimable en contrainte d'exclusion (§ 3). Même raisonnement que la
note d'implémentation § 5.5 : une redondance qu'il faudrait maintenir, et qui
divergerait à la première modification des dates d'une session.

## 3. Où vivent les deux règles

RG-13 — capacité supérieure ou égale à l'effectif : COUCHE SERVICES. La capacité
vit sur `lieu`, l'effectif sur `brigade` ; aucune contrainte SQL ne compare deux
colonnes de deux tables tierces. C'est déjà la position du tableau des treize
contraintes de la phase 4.

RG-14 — une salle attitrée à une seule brigade sur une période sécante : COUCHE
SERVICES. La période vit sur `Session`, deux niveaux au-dessus de
`SalleAttitree` ; une contrainte d'exclusion ne traverse pas de jointure, même
avec `btree_gist`.

À CONSIGNER, point d'analyse : RG-14 NE FIGURE PAS dans le tableau des treize
contraintes du diagramme de classes (§ 8), qui ne recense que RG-13 et RG-19 pour
les lieux. C'est une contrainte réelle omise par l'analyse de phase 4. Note-le
comme un écart de complétude du livrable, avec sa conséquence arithmétique : le
décompte « sept contraintes en couche services », descendu à six après l'arbitrage
d'US-SES-02 sur la désignation de brigade, revient à sept avec RG-14. Le dossier
d'architecture et la note d'implémentation sont à reprendre sur ce point au
prochain relevé du mémoire.

En base, une seule chose : l'unicité portée par le `OneToOneField`
(`uq_salle_attitree_brigade`, généré par Django — vérifie son nom réel dans la
migration et renomme-le si la convention § 2.1 l'exige).

## 4. Le service

`app/ressources/services/salle_attitree.py`.

`DOMAINE` : celui des lieux et du calendrier (`lieux_calendrier`, D-11 — vérifie
le code exact au catalogue). PAS le domaine de l'organisation. C'est le cœur de
cette story : l'affectation est un acte de la cellule planification sur une
ressource qu'elle détient, appliqué à une brigade qu'elle ne peut pas modifier.

Contrôles à l'affectation, dans cet ordre, et tous testés :

1. Le lieu est de catégorie « salle attitrée » (D-53, deux valeurs). Un lieu
   partagé n'est pas attribuable à demeure : refus.
2. Le lieu n'est pas archivé : refus.
3. La capacité du lieu est DÉCLARÉE. Si elle ne l'est pas, refus avec message
   correctif : « La capacité de la salle X n'est pas renseignée ; renseignez-la
   avant de l'attribuer. » RG-13 est une règle dure, et une règle dure qu'on ne
   peut pas vérifier ne doit jamais être silencieusement sautée. Consigne cette
   décision ET la question de terrain qu'elle soulève : toutes les salles du
   centre ont-elles une capacité connue, ou certaines sont-elles réellement sans
   capacité déclarable ?
4. RG-13 : capacité supérieure ou égale à l'EFFECTIF PRÉVISIONNEL de la brigade.
   Refus avec indication chiffrée de l'écart (E1), jamais « capacité
   insuffisante » tout court (BNF-10).
   Ne confonds pas avec RG-19, qui comparera la capacité à l'effectif RÉEL à
   US-SES-06. Deux règles distinctes, deux grandeurs distinctes, deux moments
   distincts.
5. RG-14 : aucune autre brigade ne se voit attribuer ce lieu sur une période
   sécante. La période d'une brigade est celle de sa session. Refus avec
   désignation de la brigade occupante, de sa session et de la période en
   conflit (E2).
   Nuance de RG-14 à ne pas perdre : la salle demeure mobilisable comme lieu
   ponctuel pour des séances d'autres brigades si sa typologie l'autorise.
   L'exclusion porte sur les salles ATTITRÉES entre elles, jamais sur les
   séances. Ne code aucun contrôle vers les séances — elles n'existent pas, et
   quand elles existeront, ce sera RG-37, ailleurs.

Changement de salle (A2) : `modifier` vérifie la disponibilité de la nouvelle
salle sur la PÉRIODE RESTANTE — de la date du jour, si la session a commencé, à
sa date de fin ; de la date de début sinon. Pas sur toute la période de la
session : une salle occupée par une autre brigade jusqu'à la semaine dernière
n'empêche pas de la reprendre aujourd'hui. Journalisé, avec l'ancienne et la
nouvelle valeur.

Retrait d'une salle attitrée : autorisé, journalisé. Une brigade sans salle
attitrée est un état transitoire légitime — c'est celui de toute brigade entre
sa création par la cellule pédagogique et son attribution par la cellule
planification.

Avertissement, non bloquant, troisième usage du mécanisme : si le lieu porte des
indisponibilités déclarées recouvrant la période de la session, la salle est
attribuée MALGRÉ TOUT, avec signalement des périodes concernées. Une salle
indisponible deux semaines reste la salle attitrée de la brigade ; ce sont les
séances de ces deux semaines qui devront être placées ailleurs, et c'est une
affaire de planification, pas d'attribution.

Expose une propriété lisible depuis `organisation` par la relation inverse, sans
import : l'écart entre la capacité du lieu et l'effectif prévisionnel de la
brigade, pour qu'US-SES-04 puisse l'afficher. Si l'effectif d'une brigade est
relevé après l'attribution, `organisation` ne peut pas rappeler ce service — le
sens de dépendance l'interdit. Le dépassement se constate donc à la lecture, sur
l'écran, et non par un refus au moment où l'effectif change. Consigne cette
limite explicitement : c'est le prix de l'arbitrage du § 0.1, et il vaut mieux
qu'il soit écrit que découvert.

## 5. Écrans

Écran d'affectation, dans `ressources`, atteignable depuis l'écran des brigades
d'une session (US-SES-02) par un lien visible pour qui détient l'écriture sur le
domaine des lieux. Le gabarit d'`organisation` ne porte qu'un `{% url %}` vers
une adresse `ressources:` — méthode D-52, aucun import.

Il présente : la brigade, sa session, son effectif prévisionnel ; la salle
actuellement attitrée s'il y en a une ; et la liste des salles attitrables sur la
période, avec leur capacité, conformément au point 4 du scénario nominal de
CU-P3-02. « Attribuables » veut dire : catégorie salle attitrée, non archivées,
capacité renseignée, libres sur la période. Les salles écartées pour capacité
insuffisante restent visibles mais signalées comme telles — retirer silencieuse-
ment une information à un lecteur qui n'a aucun moyen de savoir qu'elle manque
est le défaut que D-63 a explicitement refusé.

Ce filtrage est un confort. Le service refuse indépendamment, et les tests le
vérifient en court-circuitant le formulaire.

Sur la fiche d'un `Lieu` : une section énumérant les brigades auxquelles il est
attitré, avec leur session et la période. Elle sert deux fins — la lisibilité, et
la compréhension immédiate du refus de suppression que le `PROTECT` va désormais
produire.

Sur l'écran des brigades d'une session : la salle attitrée de chaque brigade,
lue par la relation inverse, et un tiret explicite quand il n'y en a pas.

## 6. Habilitations — le point à ne pas rater

Domaine des lieux et du calendrier, matrice § 11.2 : planification en écriture ;
pédagogique, examens et Direction de Formation en lecture ; administrateur aucun
accès.

Cela produit une asymétrie qui doit être testée dans LES DEUX SENS, parce qu'elle
matérialise la répartition décidée par le terrain :

- un utilisateur du profil PÉDAGOGIQUE crée des brigades mais NE PEUT PAS leur
  attribuer de salle ;
- un utilisateur du profil PLANIFICATION attribue les salles mais NE PEUT PAS
  créer, modifier ni supprimer une brigade.

Écris les deux tests, nomme-les de façon qu'un lecteur comprenne qu'il s'agit
d'une règle d'organisation et non d'un oubli de permission.

## 7. Journalisation

Attribution, changement et retrait journalisés, avec l'ancienne et la nouvelle
salle pour le changement (A2 l'exige nommément). Vérifie le câblage réel plutôt
que de le supposer.

## 8. Ce que cette story referme, ce qu'elle reporte

REFERME — D-54, volet brigade : « un lieu affecté à une brigade ne peut être
supprimé ». Le `PROTECT` sur `lieu` le rend vrai et testable. C'est l'un des
reports que la revue du 26 septembre vérifie nommément : la preuve est un test
qui supprime réellement, pas une déclaration dans `DECISIONS.md`. Souviens-toi
que D-50 a déclaré un report refermé qui ne l'était pas, et qu'il a fallu quatre
jours pour s'en apercevoir.

Le volet séance de D-54 reste ouvert jusqu'à US-PLAN-03. Ne l'écris pas refermé.

Corrige `docs/suivi/AVANCEMENT.md` : le volet brigade de D-54 se referme ICI, à
US-SES-03, et non à US-SES-02 comme le tableau l'annonçait.

REPORTE — critère 4 : « la salle attitrée est utilisée par défaut pour toutes les
matières ne requérant pas de lieu particulier ». Ce n'est pas une donnée à saisir
mais une règle de choix du moteur de génération, qui lira la salle attitrée de la
brigade quand la matière ne requiert aucun lieu particulier (`CategorieLieu` du
référentiel, US-REF-04, valeur « sans lieu »). Aucun code ici. Consigne le report
vers US-PLAN-03 / US-PLAN-04, sur le modèle de D-23, et note qu'il se vérifiera
en constatant que le moteur affecte bien la salle attitrée dans ce cas.

## 9. Tests attendus

Groupe A — couche services

A1. Attribution nominale : enregistrée, journalisée.
A2. Lieu de catégorie « lieu partagé » — refus.
A3. Lieu archivé — refus.
A4. Lieu sans capacité renseignée — refus, message nommant la salle et l'action
    corrective.
A5. RG-13 : capacité strictement inférieure à l'effectif prévisionnel — refus,
    écart chiffré dans le message. Et capacité ÉGALE à l'effectif — ACCEPTÉE
    (la règle dit « supérieure ou égale » ; ce test protège contre le classique
    décalage d'une unité).
A6. RG-14 : même salle, deux brigades de deux sessions dont les périodes se
    chevauchent — second refus, brigade occupante et période nommées.
A7. RG-14, cas limite : périodes strictement contiguës, la seconde session
    commençant le lendemain de la fin de la première — ACCEPTÉE. Définis et
    documente le comportement des bornes, puis teste-le ; ne le laisse pas
    dépendre d'un hasard d'implémentation.
A8. RG-14 : même salle, deux brigades de la MÊME session — refus.
A9. A2 : changement de salle en cours de session, la nouvelle salle étant occupée
    sur une période déjà écoulée — ACCEPTÉE, parce que seule la période restante
    compte. Test central de cette story, nomme-le clairement.
A10. Retrait d'une salle attitrée — accepté, journalisé.
A11. Avertissement : salle portant des indisponibilités recouvrant la période —
    attribution ENREGISTRÉE, avertissement présent, périodes énumérées.
A12. Suppression d'un lieu attitré à une brigade — refus, brigades énumérées.
    C'est la fermeture de D-54.
A13. Suppression d'une brigade dotée d'une salle attitrée — refus, énumération.

Groupe B — base

Unicité effective du `OneToOne` vérifiée par insertion directe court-circuitant
le service.

Groupe C — cycle HTTP réel

C1. Chemin nominal, profil PLANIFICATION : GET de l'écran d'affectation, POST
    attribution, POST changement, POST retrait, chacun vérifié en base.
C2. Profil PÉDAGOGIQUE : lecture accordée, ÉCRITURE REFUSÉE sur les trois
    adresses. C'est le test qui matérialise le partage décidé par le terrain.
C3. Profil PLANIFICATION sur les adresses d'écriture des BRIGADES
    (`organisation`) : refusé. Le pendant du précédent.
C4. Examens et Direction de Formation : lecture accordée, écriture refusée.
    Administrateur : aucun accès.
C5. Test de garde du sprint 1 — toute adresse d'écriture figure à la table des
    refus — passe sans modification.
C6. Navigation : l'écran d'affectation est atteignable depuis l'écran des
    brigades d'une session pour un profil planification, et le lien est absent
    pour un profil qui n'a pas l'écriture.
C7. La salle attitrée de chaque brigade est réellement affichée sur l'écran des
    brigades, lue par la relation inverse. Leçon de P-25.
C8. La fiche d'un lieu affiche réellement les brigades auxquelles il est attitré.
C9. Le refus de suppression d'un lieu attitré se produit aussi PAR LE CYCLE HTTP,
    depuis l'écran de suppression d'un lieu (`ressources/tests/...`). Leçon de
    P-30 : le service testé ne prouve pas que l'écran y mène.

Groupe D — architecture

`tests/architecture` passe en entier. En particulier : aucun import de
`ressources` dans `organisation`. Si le test échoue de ce côté, c'est que tu as
contourné l'arbitrage du § 0.1 au lieu de l'appliquer.

## 10. Définition de fini

Implanté, testé, relu par le sous-agent, commité. Suite `pytest` complète verte.
Écrans vérifiés dans un navigateur. `DECISIONS.md` à jour le jour même (R19).
`AVANCEMENT.md` corrigé sur D-54. Case d'US-SES-03 cochée dans
`docs/suivi/sprint-2.md`.

## 11. Ce que tu ne touches pas

Le backlog, le cahier des charges, le registre des risques, le diagramme de
classes de référence.

Le modèle `Brigade` : aucune colonne ajoutée, aucun import. Seul le
`related_name` posé depuis `ressources` le rend lisible, et c'est suffisant.

US-SES-04 (composition et taux d'occupation), US-SES-06 (RG-19, effectif réel),
le moteur de génération (critère 4).

## 12. Ce que tu me rends

- Le résultat du § 0.1 : sens de dépendance constaté, corrigé ou non, et comment.
- Les entrées `DECISIONS.md` : arbitrage d'architecture et ses trois motifs,
  absence d'historisation et contraste avec `AffectationBrigade`, refus en
  l'absence de capacité déclarée et question de terrain associée, omission de
  RG-14 au tableau des treize contraintes et retour du compte à sept, limite de
  la revérification de RG-13 après modification d'effectif, report du critère 4,
  fermeture de D-54 volet brigade.
- Le comportement retenu pour les bornes de période (A7), énoncé en une phrase.
- Le compte des tests par groupe et le total de la suite.
- Le temps réellement passé, à la demi-heure près. Troisième mesure : avec
  US-SES-01 et US-SES-02, 13 points livrés — de quoi trancher la clé de
  conversion avant la revue plutôt qu'à la revue.