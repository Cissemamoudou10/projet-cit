# Prompt 29 — US-PLAN-12 · Gérer les grilles horaires et désigner la grille active

Sprint 2, story 10 sur 12. Must, 5 points. Application `ressources`, paquetage P4.

## 0. Étape 0 — vérifications avant toute ligne de code

1. LES PARAMÈTRES PROVISOIRES DE D-33. Où sont
   `VOLUME_HORAIRE_HEBDOMADAIRE_REFERENCE` et
   `SEUIL_ECART_VOLUME_REFERENTIEL_POURCENT`, et QUI LES CONSOMME aujourd'hui ?
   Cherche tous les appelants : `ServiceReferentiel.ecart()` posé à US-REF-03, le
   calcul de l'exception E2 d'US-SES-01, et tout autre usage. Cette story les
   remplace (§ 7) ; il faut d'abord savoir ce qu'on touche.
2. LE MÉCANISME D'ARCHIVAGE. Quel mixin ou quelle classe de base porte
   `archive` / `archivee` sur `Formation`, `Matiere` et `Instructeur` ? Quelles
   entités en héritent, lesquelles ne l'héritent pas et pourquoi (D-37, D-49) ?
   Cette story l'applique à `GrilleHoraire` (§ 3).
3. Le patron de gestion et sa gestion des SOUS-RESSOURCES — comment
   `ElementReferentiel` est composé depuis l'écran d'une formation (D-32), et
   comment les brigades le sont depuis une session (US-SES-02). `CreneauType` est
   la même figure.
4. Le domaine d'habilitation de la cellule planification, celui du calendrier.
5. Suite `pytest` verte avant de commencer.

## 1. Ce que porte cette story

Besoin BF-PLAN-13. Cas d'utilisation CU-P4-07. Règles RG-62, RG-63, RG-64.
Séquence SEQ-01. Classe CLS-03. Acteur : cellule planification.

Critères d'acceptation du backlog v8 :

1. Une grille est un ensemble de créneaux types, définis par un jour de semaine,
   un rang, une heure de début et une heure de fin.
2. Les créneaux d'un même jour ne se recouvrent pas ; un jour sans créneau est
   non programmable par défaut, sans être interdit.
3. Plusieurs grilles coexistent ; une seule est active à la fois, et l'activation
   d'une grille désactive la précédente.
4. L'activation est datée et rattachée à l'agent qui la décide ; elle n'est jamais
   déduite du calendrier.
5. Une grille en service se clôture, elle ne se supprime pas ; une grille sans
   créneau ne peut être activée.
6. Changer de grille active ne modifie pas les séances passées, qui portent leurs
   heures réelles. — Portée réelle au § 8.

TROIS NOTIONS À NE JAMAIS CONFONDRE, la fiche y insiste et le diagramme la
reprend mot pour mot :

- la GRILLE HORAIRE est le squelette de la semaine, sans matière ni instructeur ;
- le CRÉNEAU TYPE est une case de ce squelette — lundi, deuxième créneau, de
  10:10 à 12:00 — porteur d'un jour de semaine, d'un rang, d'une heure de début
  et d'une heure de fin, ET D'AUCUNE DATE. « Type » a le sens de modèle : un
  patron répété chaque semaine ;
- la SÉANCE est ce qui remplit une case un jour donné, et elle porte des dates
  réelles.

Si un attribut de date apparaît sur `CreneauType`, la conception est perdue.

## 2. Les modèles

`app/ressources/models.py`.

`GrilleHoraire`, `Meta.db_table = "ressources_grille_horaire"` :

- `intitule` — texte, unique, insensible à la casse (D-21, D-26).
- `active` — booléen, faux par défaut.
- `date_activation` — horodatage, facultatif.
- `activee_par` — clé étrangère vers l'utilisateur, facultative,
  `on_delete=PROTECT`, `related_name="grilles_activees"`. CLS-03 :
  « Utilisateur 0..1 -- 0..* GrilleHoraire : activée par ».
- archivage, § 3.

`CreneauType`, `Meta.db_table = "ressources_creneau_type"` :

- `grille` — clé étrangère vers `GrilleHoraire`, `on_delete=CASCADE`,
  `related_name="creneaux"`.
- `jour_semaine` — énumération `JourSemaine`, les sept jours.
- `ordre` — entier, le rang du créneau dans la journée.
- `heure_debut`, `heure_fin` — HEURES SEULES, sans date.

`CASCADE` et non `PROTECT`, contrairement à tout ce qu'on a posé jusqu'ici : un
créneau type n'a aucune existence hors de sa grille, c'est une composition
stricte, et `.claude/rules/modeles.md` réserve `CASCADE` exactement à ce cas.
Écris-le, parce que la règle générale du projet est l'inverse et qu'un lecteur
demandera pourquoi celle-ci y déroge.

En base :

- `uq_grille_horaire_intitule` — unicité insensible à la casse.
- `uq_creneau_type_grille_jour_ordre` — unicité du rang dans un jour d'une grille.
- `ck_creneau_type_heures` — `heure_fin > heure_debut`.
- UNE SEULE GRILLE ACTIVE (RG-62) : index unique partiel sur `active`, restreint
  aux lignes où `active` est vrai — `UniqueConstraint(fields=["active"],
  condition=Q(active=True))` ou son équivalent. Vérifie que la migration produit
  bien un index partiel et non une unicité globale sur le booléen, ce qui
  interdirait d'avoir deux grilles inactives.
- Cohérence de l'activation : `active` vrai implique `date_activation` et
  `activee_par` renseignés. Même figure que `ck_stagiaire_radiation` à US-SES-05.

LE NON-RECOUVREMENT DES CRÉNEAUX D'UN MÊME JOUR RESTE EN COUCHE SERVICES. Motif
à consigner : les trois modèles de période posés jusqu'ici — indisponibilité de
lieu, affectation de brigade, indisponibilité d'instructeur — portent des
horodatages et se contraignent avec `btree_gist` sur un intervalle daté.
`CreneauType` porte des HEURES SANS DATE : PostgreSQL n'a pas de type d'intervalle
horaire natif, et fabriquer un `int4range` de minutes depuis minuit pour poser
une contrainte d'exclusion coûterait une colonne dérivée et une conversion à
chaque écriture, pour quatre lignes par jour éditées en bloc. Le contrôle vaut en
services.

Ce constat répond aussi à la question laissée ouverte au § 10 du prompt 27 sur
une abstraction commune aux modèles de période : voici un quatrième cas de forme
voisine et de nature différente. Consigne-le comme argument supplémentaire contre
l'abstraction, ou pour, si tu penses le contraire — mais réponds à la question,
elle est encore ouverte.

## 3. « Clôturer » une grille, c'est l'archiver

Le critère 5 dit qu'une grille en service se clôture et ne se supprime pas.
`GrilleHoraire` n'a pas d'état de clôture dans CLS-03. N'en invente pas un
troisième : c'est le mécanisme d'ARCHIVAGE déjà en place sur `Formation`,
`Matiere` et `Instructeur` (§ 0.2), et il dit exactement la bonne chose — une
entité retirée du service, conservée pour l'historique, non réutilisable en
l'état.

Règles qui en découlent, toutes testées :

- une grille ARCHIVÉE ne peut pas être activée ;
- la grille ACTIVE ne peut pas être archivée : il faut d'abord en activer une
  autre. C'est E2, transposé ;
- la grille active ne peut pas être supprimée non plus (E2 au sens littéral) ;
- une grille QUI A ÉTÉ ACTIVÉE au moins une fois — `date_activation`
  renseignée — ne peut plus être supprimée, seulement archivée. C'est le « en
  service » du critère 5 : des séances en sont issues, leur origine doit rester
  lisible ;
- une grille JAMAIS ACTIVÉE et non archivée peut être supprimée. C'est un
  brouillon, rien n'en dépend.

A2 de la fiche confirme la lecture : « la grille de Ramadan est CONSERVÉE pour
l'année suivante ». Conservée et inactive, pas archivée — l'archivage vise la
grille devenue obsolète, pas la grille saisonnière.

Consigne l'écart avec CLS-03 : le diagramme ne porte pas l'archivage sur
`GrilleHoraire`, le backlog l'exige en substance. Ligne « Impact sur les
livrables ».

## 4. L'activation — RG-62 et RG-63

Activer une grille est UNE SEULE TRANSACTION : la grille précédemment active est
désactivée, la nouvelle est activée, `date_activation` et `activee_par` sont
renseignés, l'opération est journalisée avec l'ancienne et la nouvelle grille.
Tout ou rien : un état où deux grilles sont actives, ou aucune alors qu'il y en
avait une, est inacceptable.

Refus d'activer : une grille SANS AUCUN CRÉNEAU (E3, critère 5) — « aucune
génération ne serait possible » ; une grille ARCHIVÉE (§ 3).

`date_activation` de l'ancienne grille : NE L'EFFACE PAS. Elle enregistre la
dernière fois où cette grille a servi, information utile et non contradictoire.
Dis-le, sinon quelqu'un la remettra à zéro par souci de propreté.

AUCUNE ENTITÉ D'HISTORIQUE D'ACTIVATION. Le diagramme est explicite : « deux
attributs suffisent, aucune entité n'est créée ». L'historique des activations
successives vit dans le journal, qui est immuable et fait pour ça. C'est le
contraire de la décision prise à US-SES-06 pour `AffectationBrigade`, où RG-20
exigeait une table datée : là, la règle métier l'imposait ; ici, un livrable
l'écarte nommément. Consigne le contraste, c'est la troisième fois que la
question se pose dans ce sprint et il faut qu'on sache selon quoi elle se tranche.

RG-63, à ne pas trahir : « l'activation n'est JAMAIS DÉDUITE DU CALENDRIER : le
passage à l'horaire de Ramadan est un acte de commandement, non une conséquence
d'une date ». N'écris aucune association entre `GrilleHoraire` et
`PeriodeCalendrier`, aucune tâche périodique, aucune bascule automatique. Le
mécanisme alternatif a été examiné et écarté en phase 4 ; ne le réintroduis pas
« pour rendre service ». Un test doit constater qu'aucune relation ne lie les
deux, sur le modèle du test d'architecture posé à US-INS-03 pour l'absence de
lien entre instructeur et compte utilisateur.

ZÉRO GRILLE ACTIVE est un état légitime au démarrage, avant la première
activation. N'écris aucun mécanisme qui en activerait une d'office. Le refus de
GÉNÉRER sans grille active appartient à US-PLAN-03 — reporte-le, ne l'anticipe
pas.

## 5. Les créneaux

Édités depuis l'écran de leur grille, comme les éléments de référentiel depuis
une formation et les brigades depuis une session (§ 0.3). Pas d'écran de premier
niveau, pas de pagination — une grille compte quatre à cinq créneaux par jour.

Contrôles :

- E1, non-recouvrement dans un même jour : refus, créneau en conflit désigné
  avec ses heures ;
- bornes contiguës — un créneau finissant à 12:00 et le suivant commençant à
  12:00 — ACCEPTÉES. Cohérent avec le choix de bornes semi-ouvertes fait à
  US-INS-03 et US-PLAN-01. Si ces deux stories ont retenu autre chose, aligne-toi
  sur elles et signale la divergence ;
- `heure_fin > heure_debut` ;
- unicité du rang dans le jour ;
- A4, JOUR SANS CRÉNEAU : parfaitement valide. Le samedi et le dimanche reçoivent
  une liste vide, « ce qui les rend non programmables par défaut SANS LES
  INTERDIRE ». N'exige aucun créneau minimum par jour, et écris un test qui le
  prouve — quelqu'un ajoutera sinon une validation « au moins un créneau par
  jour » en croyant bien faire. Le vendredi porte sa propre liste, plus courte.

A3, DUPLICATION : « une grille existante sert de point de départ à une nouvelle,
puis est ajustée ». Implante-la, c'est peu de code et c'est le parcours réel —
la grille de Ramadan se construit en partant de l'ordinaire. La copie porte un
nouvel intitulé, est inactive, non archivée, et duplique tous les créneaux.

## 6. Les deux grilles réelles — données de départ

Les progressions d'instruction établissent deux grilles au chiffre près. Charge-les
comme données de départ, par le même mécanisme que les natures d'événement
d'US-PLAN-01 (vérifie lequel a été retenu) :

- ORDINAIRE — 08:00–09:45 · 10:10–12:00 · 13:00–14:15 · 14:40–16:00
- RAMADAN — 08:30–09:50 · 10:00–11:20 · 11:30–12:50 · 13:10–14:30

Du lundi au vendredi ; samedi et dimanche vides. La grille ordinaire est active.

Les durées sont INÉGALES et les pauses IRRÉGULIÈRES : 1h45, 1h50, 1h15, 1h20 pour
l'ordinaire. Aucune arithmétique ne les engendre — c'est le motif pour lequel la
saisie explicite est imposée. Ne « corrige » pas ces valeurs, ne les arrondis pas,
ne génère pas les créneaux par une boucle à pas constant. Elles viennent du
terrain.

Question de terrain à poser au passage : la grille ordinaire relevée date de mai,
la grille de Ramadan de février. Sont-ce les deux seules en vigueur, ou existe-t-il
un horaire d'été ou de période d'examens ?

## 7. Ce que cette story rembourse — le point le plus important

D-33 a posé deux paramètres PROVISOIRES pour comparer un volume prescrit à une
durée : `VOLUME_HORAIRE_HEBDOMADAIRE_REFERENCE`, fixé à 30 heures faute de mieux,
et `SEUIL_ECART_VOLUME_REFERENTIEL_POURCENT`. US-REF-03 les a introduits,
US-SES-01 les a réutilisés pour l'exception E2, et la décision d'US-SES-01
consigne noir sur blanc que le remplacement est à faire dès qu'US-PLAN-12 et
US-PLAN-01 seraient livrées. LES DEUX LE SONT.

Remplace donc la constante par un CALCUL : le volume horaire hebdomadaire de
référence est la somme des durées des créneaux de la GRILLE ACTIVE, sur la
semaine entière. Avec la grille ordinaire, c'est cinq jours × (1h45 + 1h50 + 1h15
+ 1h20), soit 30 heures — la constante de D-33 se trouve être juste, ce qui est
rassurant, mais elle cesse d'être une hypothèse.

Trois exigences :

- si AUCUNE grille n'est active, le calcul retombe sur le paramètre. Zéro grille
  active est légitime (§ 4), et le calcul ne doit pas échouer ;
- le paramètre RESTE, comme valeur de repli, avec un commentaire disant qu'il ne
  sert plus que dans ce cas ;
- `SEUIL_ECART_VOLUME_REFERENTIEL_POURCENT` ne change pas : c'est une tolérance,
  pas une donnée du terrain.

Vérifie que tous les appelants relevés au § 0.1 passent par le calcul et non plus
par la constante — un seul oublié, et deux écrans donneront deux chiffres
différents.

Cela referme aussi, par le code, l'une des trois questions de terrain en attente
depuis le début du sprint : le volume horaire hebdomadaire de référence n'a plus
besoin d'être demandé, il se lit dans la grille. Dis-le explicitement dans ton
compte rendu.

## 8. RG-64 et le critère 6 — ce qui ne se code pas

RG-64 : « La grille contraint ce que la génération PROPOSE, jamais ce que la
saisie manuelle décide. Une séance porte ses heures réelles et une référence
FACULTATIVE au créneau type dont elle est issue. »

Trois comportements en dépendent : une séance peut couvrir plusieurs créneaux
consécutifs ; une séance peut être placée hors grille, un samedi ou à un horaire
décalé ; changer de grille active ne réécrit pas l'historique.

Rien à coder ici — `Seance` n'existe pas. Mais deux choses à faire :

- consigner RG-64 comme CONTRAINTE DE CONCEPTION pour US-PLAN-03 : la relation
  entre `Seance` et `CreneauType` sera facultative, et la séance portera ses
  heures réelles. Écris-le dans `DECISIONS.md` en le rattachant nommément à
  US-PLAN-03, faute de quoi la story suivante posera une relation obligatoire par
  facilité ;
- le CRITÈRE 6 se vérifie par l'ABSENCE de code : aucune méthode de cette story
  ne touche à quoi que ce soit d'autre que les grilles et leurs créneaux. Il
  deviendra réellement testable au sprint 3. Reporte-le en le disant ainsi — un
  report dont la fermeture consistera à constater qu'on n'a rien écrit.

## 9. Écrans

Domaine du calendrier, zone où vivent lieux, indisponibilités et périodes.

- Liste des grilles : intitulé, nombre de créneaux, état — active, disponible,
  archivée —, date de dernière activation et agent. Filtre par état.
- Fiche d'une grille : ses créneaux organisés par jour, en tableau lisible comme
  une semaine type. Actions : activer, archiver, dupliquer, supprimer selon les
  règles du § 3, chacune conditionnée à la permission et confirmée (BNF-09).
- Édition des créneaux depuis cette fiche.
- Le bandeau ou la fiche indique clairement QUELLE GRILLE EST ACTIVE, et le
  volume hebdomadaire qu'elle représente — c'est le nombre du § 7, et le voir
  affiché quelque part évite qu'il redevienne invisible.

L'activation demande une confirmation explicite qui NOMME la grille désactivée :
« Activer la grille Ramadan désactivera la grille Ordinaire. » Un changement de
grille modifie le fonctionnement de tout le centre.

Mesure la largeur imprimable de la fiche de grille — une semaine type est un
document qu'on affiche — et reporte-la dans `IMPRESSION-ANALYSE.md`.

## 10. Habilitations

Domaine du calendrier. Planification en écriture ; pédagogique, examens,
Direction de Formation en lecture ; administrateur aucun accès. Vérifie contre la
matrice § 11.2.

L'ACTIVATION est une écriture à part entière, et une écriture lourde : elle doit
figurer à la table des refus comme les autres, et le test de garde du sprint 1
doit la voir.

## 11. Ce que cette story referme, ce qu'elle reporte

REFERME — les paramètres provisoires de D-33 dans leur usage nominal (§ 7). Ce
n'est pas un report du tableau suivi en revue, mais c'est une dette consignée
depuis US-REF-03 : dis-le, et mets à jour la décision d'origine pour qu'on ne la
relise pas comme encore ouverte.

REPORTE — trois, sur le modèle de D-23 :

- critère 6, séances passées inchangées par un changement de grille : vers
  US-PLAN-03, fermeture par constat d'absence de code ;
- RG-64, relation facultative entre séance et créneau type : contrainte de
  conception pour US-PLAN-03 ;
- refus de générer en l'absence de grille active : vers US-PLAN-03.

Donne le compte à jour du tableau des reports, à partir du compte vérifié sur le
code.

## 12. Tests attendus

Groupe A — grille

A1. Création nominale, journalisée. Grille inactive, sans date d'activation.
A2. Unicité de l'intitulé, casse indifférente.
A3. Duplication (A3) : nouvelle grille inactive, tous les créneaux copiés,
    l'originale inchangée.
A4. Suppression d'une grille jamais activée — acceptée.
A5. Suppression d'une grille déjà activée par le passé — REFUSÉE, message
    orientant vers l'archivage.
A6. Suppression de la grille active — refusée (E2).
A7. Archivage de la grille active — refusé.
A8. Archivage d'une grille inactive — accepté ; la grille reste consultable.

Groupe B — créneaux

B1. Ajout nominal, journalisé.
B2. E1 : deux créneaux du même jour qui se recouvrent — refus, créneau en conflit
    désigné avec ses heures.
B3. Créneaux contigus, fin de l'un égale au début du suivant — ACCEPTÉS.
B4. Même recouvrement horaire mais sur DEUX JOURS différents — accepté.
B5. Même recouvrement horaire, même jour, mais DEUX GRILLES différentes —
    accepté. Le contrôle est par grille et par jour, pas global.
B6. `heure_fin` antérieure ou égale à `heure_debut` — refus, vérifié aussi par
    insertion directe en base.
B7. Unicité du rang dans le jour, par insertion directe.
B8. A4 : une grille dont samedi et dimanche n'ont aucun créneau est VALIDE et
    ACTIVABLE. Nomme le test pour que l'intention survive.
B9. Aucun champ de date sur `CreneauType`. Vérifie-le explicitement — c'est
    l'interdit du § 1 et il ne se voit pas autrement.
B10. Suppression d'une grille : ses créneaux disparaissent avec elle (CASCADE).

Groupe C — activation

C1. Activation nominale : grille active, date et agent renseignés, journalisée.
C2. RG-62 : activer une seconde grille désactive la première, dans la même
    opération. Une seule active à l'arrivée.
C3. Transaction : provoque un échec au milieu de l'activation, vérifie qu'on ne
    se retrouve ni avec deux grilles actives ni avec aucune.
C4. Contrainte en base : deux grilles actives par insertion directe — rejetées.
    Vérifie aussi que DEUX GRILLES INACTIVES sont acceptées, ce qui prouve que
    l'index est bien partiel.
C5. E3 : activation d'une grille sans créneau — refusée.
C6. Activation d'une grille archivée — refusée.
C7. La `date_activation` de la grille désactivée est CONSERVÉE.
C8. Cohérence en base : `active` vrai sans date d'activation — rejeté par
    insertion directe.
C9. Zéro grille active : état accepté, aucun mécanisme ne réactive d'office.

Groupe D — RG-63, aucune déduction du calendrier

D1. Aucune relation entre `GrilleHoraire` et `PeriodeCalendrier`. Test
    d'architecture, sur le modèle de celui posé à US-INS-03.
D2. Créer une période de calendrier ne change AUCUNE grille active.

Groupe E — volume hebdomadaire de référence (§ 7)

E1. Grille ordinaire active : le volume calculé vaut 30 heures.
E2. Grille de Ramadan active : le volume calculé vaut la somme de ses créneaux,
    différente de 30.
E3. Activer une autre grille CHANGE le volume de référence utilisé par
    `ServiceReferentiel.ecart()`. C'est le test qui prouve que le remplacement du
    § 7 est réellement branché ; sans lui, la constante pourrait subsister
    quelque part sans qu'on le voie.
E4. Aucune grille active : repli sur le paramètre, sans erreur.
E5. Tous les appelants relevés au § 0.1 donnent le MÊME chiffre. Un test par
    appelant si nécessaire.

Groupe F — cycle HTTP réel

F1. Chemin nominal, profil planification, sur chaque adresse d'écriture :
    création, créneaux, activation, archivage, duplication, suppression.
F2. L'activation par le vrai cycle HTTP, avec sa confirmation nommant la grille
    désactivée, réellement présente dans la réponse. Leçon de P-25.
F3. La fiche de grille affiche RÉELLEMENT la semaine type et le volume
    hebdomadaire.
F4. Refus d'habilitation sur chaque adresse d'écriture, activation comprise :
    pédagogique, examens, Direction de Formation, administrateur.
F5. Lecture accordée aux quatre profils habilités.
F6. Test de garde du sprint 1 : passe sans modification, activation incluse.
F7. Navigation : les écrans sont atteignables pour les profils habilités.

Groupe G — données de départ et architecture

G1. Les deux grilles du § 6 sont présentes après chargement, avec leurs heures
    EXACTES et la grille ordinaire active.
G2. `tests/architecture` en entier, aucune classe au-delà de 200 lignes.

## 13. Définition de fini

Implanté, testé, relu par le sous-agent, commité. Suite `pytest` complète verte.
Grilles regardées RÉELLEMENT dans un navigateur : bascule de l'ordinaire au
Ramadan, retour, duplication, jour vide. Mesure d'impression reportée.
`DECISIONS.md` à jour le jour même, D-33 mise à jour comme remboursée.
Case cochée dans `docs/suivi/sprint-2.md`.

## 14. Ce que tu ne touches pas

Le backlog, le cahier des charges, le registre des risques, le diagramme de
classes. Les écarts des § 3 et § 7 s'écrivent en « Impact sur les livrables ».

US-PLAN-03 et US-PLAN-04 : aucune anticipation. En particulier, aucune méthode
« créneaux disponibles pour telle semaine » — c'est le moteur, et il croise la
grille avec le calendrier, les indisponibilités et les affectations.

## 15. Ce que tu me rends

- L'inventaire du § 0.1 : tous les appelants des paramètres de D-33, avant et
  après remplacement.
- Ta réponse à la question restée ouverte du prompt 27 § 10, éclairée par ce
  quatrième cas.
- Les entrées `DECISIONS.md` : archivage plutôt que troisième état, `CASCADE` en
  composition stricte et pourquoi il déroge à la règle du projet, non-recouvrement
  en services et pourquoi `btree_gist` ne s'applique pas, absence d'entité
  d'historique d'activation et contraste avec `AffectationBrigade`, remboursement
  de D-33, RG-64 comme contrainte de conception pour US-PLAN-03, les trois
  reports.
- La question de terrain du § 6 sur l'existence d'autres grilles.
- Le compte des tests par groupe et le total de la suite.
- Le temps réellement passé, à la demi-heure près.