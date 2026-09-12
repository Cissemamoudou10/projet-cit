# Prompt 25 — US-SES-06 · Affecter les stagiaires aux brigades

Sprint 2, story 6 sur 12. Must, 5 points. Lot WBS 5.2.7.

## 0. Étape 0 — vérifications avant toute ligne de code

1. Le mécanisme d'état transitoire retenu à US-SES-05 pour l'import en deux
   temps : où vit-il, quelle est sa signature, est-il réutilisable tel quel pour
   une proposition de répartition ? S'il faut le tordre, c'est qu'il avait été
   taillé pour un seul usage — dis-le et corrige-le au bon niveau plutôt que de
   le dupliquer.
2. Comment les indisponibilités de lieu (US-PLAN-02) expriment-elles leur
   contrainte de non-chevauchement : contrainte d'exclusion `EXCLUDE` avec
   `btree_gist`, index unique partiel, ou contrôle en couche services ? Cite le
   fichier et la migration. Cette story pose une contrainte de même nature (§ 3)
   et doit suivre le même précédent, pas en inventer un second.
3. `Brigade` : nom exact du champ d'effectif prévisionnel, et l'emplacement
   « effectif réel » réservé à US-SES-02 puis US-SES-04 — où est-il, comment est-il
   commenté ?
4. La propriété exposée par `ressources` à US-SES-03 pour lire la capacité de la
   salle attitrée depuis `organisation` sans import : nom exact, et ce qu'elle
   renvoie quand la brigade n'a pas de salle.
5. `Stagiaire` tel que livré à US-SES-05 : champs de radiation, et comment les
   listes actives les filtrent.
6. Suite `pytest` verte avant de commencer.

## 1. Ce que porte cette story

Besoin BF-SES-06. Cas d'utilisation CU-P3-06, fiche détaillée. Règles RG-19 et
RG-20. Acteur en écriture : cellule pédagogique.

Critères d'acceptation du backlog v8 :

1. Le système propose une répartition automatique remplissant les brigades
   successivement jusqu'à leur effectif déclaré.
2. La répartition proposée est intégralement modifiable : un stagiaire peut être
   déplacé d'une brigade à une autre.
3. L'effectif réel de chaque brigade est comparé à sa capacité et à celle de sa
   salle attitrée ; tout dépassement est signalé.
4. Un stagiaire ne peut être affecté qu'à une seule brigade au sein d'une session.
5. Les stagiaires non affectés sont listés séparément.

HORS PÉRIMÈTRE : la consultation de la liste des stagiaires par brigade et son
export (US-SES-07). Ici, on affecte ; là, on consulte.

## 2. La contradiction du critère 1 — arbitrage rendu, à consigner soigneusement

Le critère 1 du backlog dit « remplissant les brigades SUCCESSIVEMENT JUSQU'À
LEUR EFFECTIF DÉCLARÉ ». La fiche CU-P3-06 dit « une répartition ÉQUILIBRÉE des
stagiaires non affectés entre les brigades ». Ce sont deux algorithmes
différents, pas deux formulations du même.

APPLIQUE LE BACKLOG : remplissage séquentiel jusqu'à l'effectif déclaré de chaque
brigade.

Motif, à écrire dans ta décision parce qu'il sera relu. Avec 58 stagiaires et des
brigades déclarées à 20, 20 et 18, le remplissage séquentiel donne 20/20/18 et
respecte le découpage décidé par la cellule pédagogique. L'équilibrage donnerait
19/19/20 et RECALCULERAIT la composition des brigades — exactement ce que RG-12
interdit au système : « le nombre et la composition des brigades relèvent d'une
décision humaine ; le système enregistre ce découpage sans le calculer ».

Signale explicitement que cet arbitrage RENVERSE le précédent suivi jusqu'ici.
D-26, puis le taux d'occupation d'US-SES-04, ont fait prévaloir la fiche sur le
backlog parce qu'elle était plus précise. Ici la fiche est plus VAGUE, et sa
lecture littérale heurte une règle métier structurante. Ce n'est donc pas le
document qui arbitre mais la règle. Écris-le en ces termes : un lecteur qui aura
vu les deux arbitrages opposés demandera la cohérence, et elle existe.

Ordre de remplissage : par désignation de brigade, déterministe et documenté.
Ordre des stagiaires : par nom, déterministe lui aussi. Une proposition qui
change à chaque rafraîchissement est inexploitable.

Deux cas à traiter sans surprise :

- stagiaires plus nombreux que la somme des effectifs déclarés : le surplus RESTE
  NON AFFECTÉ et figure dans la liste séparée du critère 5. Ne force personne
  dans une brigade pleine, et n'invente pas de brigade supplémentaire — ce serait
  RG-12 violée une seconde fois.
- stagiaires moins nombreux : les brigades ne sont simplement pas pleines. Ce
  n'est ni une erreur ni un avertissement.

## 3. Le modèle

`app/organisation/models.py`, `Meta.db_table = "organisation_affectation_brigade"`.

`AffectationBrigade` :

- `stagiaire` — clé étrangère vers `Stagiaire`, `on_delete=PROTECT`,
  `related_name="affectations"`.
- `brigade` — clé étrangère vers `Brigade`, `on_delete=PROTECT`,
  `related_name="affectations"`.
- `date_effet` — date, obligatoire.
- `date_fin` — date, facultative. Nulle tant que l'affectation est OUVERTE.

Hérite de la classe de base d'horodatage et de rattachement à l'auteur.

POURQUOI UNE TABLE D'HISTORIQUE ICI ALORS QUE `SalleAttitree` N'EN A PAS. À
US-SES-03 j'ai écarté toute historisation : rien ne l'exigeait, et le journal
immuable suffisait. Ici, RG-20 l'exige nommément — « un changement de brigade est
daté et historisé, il ne crée pas une seconde affectation » — et CLS-00 définit
l'effectif réel comme les affectations OUVERTES de stagiaires NON RADIÉS, ce qui
suppose des affectations qui se ferment. Consigne ce contraste : deux
associations voisines, deux traitements opposés, et une raison écrite pour
chacune. C'est une question de soutenance probable.

En base :

- Contrainte de non-chevauchement exprimant RG-20 : un stagiaire ne peut avoir
  deux affectations dont les périodes se recouvrent. Suis le précédent identifié
  au § 0.2. Si les indisponibilités de lieu utilisent une contrainte d'exclusion
  `EXCLUDE` avec `btree_gist` sur un intervalle de dates, fais de même — c'est
  l'usage exact pour lequel l'extension a été installée au sprint 1, et une
  affectation ouverte s'exprime par une borne supérieure non bornée. Si le
  précédent est un index unique partiel, un index unique sur `stagiaire_id`
  restreint aux lignes dont `date_fin` est nulle exprime déjà le point essentiel
  — au plus une affectation ouverte par stagiaire — et le contrôle du
  chevauchement historique reste en couche services. Choisis, justifie, ne panache
  pas.
- `ck_affectation_dates` — `date_fin` nulle ou strictement postérieure à
  `date_effet`.

À NE PAS FAIRE : aucun champ `effectif_reel` stocké sur `Brigade`. C'est un
attribut dérivé de CLS-00 et le § 9 du diagramme de classes interdit de le
stocker. Il se calcule : nombre d'affectations ouvertes dont le stagiaire n'est
pas radié.

## 4. Les trois contrôles à l'affectation

Dans cet ordre, et tous testés.

REFUS — le stagiaire est radié. On n'affecte pas quelqu'un qui a quitté la
formation.

REFUS — RG-20 : le stagiaire a déjà une affectation ouverte dans cette session.
La fiche est explicite (E2) : le système PROPOSE LE DÉPLACEMENT, qui est un
enchaînement distinct. Le message doit donc nommer la brigade actuelle et offrir
le déplacement, jamais se contenter de « déjà affecté ».

REFUS — RG-19 : l'affectation porterait l'effectif réel de la brigade au-delà de
la CAPACITÉ DE SA SALLE ATTITRÉE. Message indiquant la MARGE RESTANTE, chiffrée
(E1, BNF-10). C'est une règle dure : le nombre de places dans une salle est un
fait physique.

AVERTISSEMENT, jamais refus — l'effectif réel dépasse l'EFFECTIF DÉCLARÉ de la
brigade. Celui-ci est déclaratif : famille RG-65, comme RG-15 à US-SES-02.

Le critère 3 du backlog met les deux plafonds sur le même plan en disant que tout
dépassement est « signalé ». Il a tort sur le second : RG-19 est une règle métier
explicite et la fiche impose un refus. Consigne l'écart.

AVERTISSEMENT — la brigade n'a pas de salle attitrée : RG-19 est invérifiable,
l'affectation est acceptée avec signalement. Une brigade sans salle est un état
transitoire légitime, assumé à US-SES-03 : la cellule pédagogique constitue, la
planification loge, et les deux gestes ne sont pas simultanés. N'exige pas la
salle comme préalable à l'affectation.

AVERTISSEMENT — E3 : des stagiaires restent non affectés au moment de valider.
Le système avertit et les ÉNUMÈRE ; la validation reste possible, l'affectation
pouvant se poursuivre plus tard.

Cinquième et sixième usages du mécanisme d'avertissement du patron. S'il ne les
absorbe pas sans effort, corrige-le dans `noyau`, jamais localement.

## 5. La proposition n'écrit rien

Même figure qu'à US-SES-05, et c'est voulu : proposer, ajuster, valider.

TEMPS 1 — le système propose (§ 2). RIEN N'EST ÉCRIT EN BASE.
TEMPS 2 — la cellule pédagogique ajuste intégralement (critère 2).
TEMPS 3 — validation : les affectations sont enregistrées en une seule
transaction et journalisées.

La règle d'US-SES-05 s'applique mot pour mot : LA PROPOSITION EST UN APERÇU,
JAMAIS UNE SOURCE DE VÉRITÉ. La validation revalide intégralement les trois
contrôles du § 4, dans la transaction. Entre la proposition et la validation, un
stagiaire a pu être radié par un autre agent, une brigade voir son effectif
déclaré modifié, une salle être changée. Variante de P-31, et la contrainte en
base reste la seule garantie qui tienne.

Tout ou rien à la validation, comme RG-18 pour l'import : une répartition à
moitié enregistrée serait ingérable.

Réutilise le mécanisme d'état transitoire du § 0.1. Si tu dois en écrire un
second, c'est un défaut de généricité du premier : signale-le.

## 6. Le déplacement — enchaînement A2

Un stagiaire change de brigade en cours de session. RG-20 : l'affectation en
cours est FERMÉE à une date d'effet, une nouvelle est OUVERTE à cette même date.
Jamais deux affectations ouvertes, jamais une ligne écrasée.

Le système AVERTIT, au moment du déplacement, que les évaluations et la
progression du stagiaire restent rattachées à son parcours et que sa brigade
d'origine figurera dans son historique. C'est un avertissement informatif, pas un
obstacle : la fiche le demande explicitement parce que l'agent qui déplace doit
savoir ce qu'il ne casse pas.

Journalisé avec la date d'effet, l'ancienne et la nouvelle brigade.

Date d'effet par défaut : la date du jour. Modifiable ? Décide et justifie.
Argument à peser : une date d'effet dans le passé peut être légitime — le
stagiaire a physiquement changé de brigade lundi, la saisie a lieu jeudi — mais
elle rouvre la question du chevauchement avec l'affectation précédente. Une date
d'effet dans le futur, en revanche, créerait une affectation qui n'est pas encore
vraie tout en étant « ouverte », ce qui fausse l'effectif réel. Tranche, écris.

Le retrait pur et simple — fermer une affectation sans en ouvrir une autre — doit
exister : c'est le cas d'un stagiaire radié en cours de session. Traite
explicitement l'articulation : radier un stagiaire ferme-t-il automatiquement son
affectation, ou l'affectation reste-t-elle ouverte tandis que le calcul de
l'effectif réel l'exclut par la radiation ? CLS-00 dit « affectations ouvertes DE
STAGIAIRES NON RADIÉS », ce qui suggère la seconde lecture. Choisis-la ou
argumente contre, mais ne laisse pas les deux mécanismes se superposer sans
qu'on sache lequel fait foi.

## 7. Écrans

Accrochés à la session, rubrique Sessions. Pas de nouvelle rubrique.

ÉCRAN DE RÉPARTITION. Présente, conformément au scénario nominal : les brigades
avec leur effectif courant, leur effectif déclaré et la capacité de leur salle
attitrée ; la liste des stagiaires non affectés ; un bouton produisant la
proposition ; la possibilité de déplacer chaque stagiaire d'une brigade à
l'autre ; la validation.

PAS DE GLISSER-DÉPOSER. La charte exclut tout framework JavaScript, et un
déplacement par formulaire — sélection du stagiaire, choix de la brigade de
destination — fait le travail, s'imprime, et fonctionne sur le poste le plus
modeste du centre. Ne réintroduis pas une dépendance par la porte de l'ergonomie.

Les trois signalements du § 4 sont visibles à l'écran, chacun avec ses nombres :
effectif réel, effectif déclaré, capacité de la salle. Couleur toujours doublée
d'un mot (D-63).

LES DEUX EMPLACEMENTS RÉSERVÉS SE REMPLISSENT ICI :

- l'effectif réel sur l'écran des brigades d'une session (réservé à US-SES-02) ;
- l'effectif réel et le taux d'occupation sur effectif réel sur la fiche de
  composition (réservé à US-SES-04).

VÉRIFIE-LES À L'ÉCRAN, DANS UN NAVIGATEUR, pas seulement par un test. P-25 :
un emplacement qu'on croit rempli et qui ne l'est pas est resté ouvert quatre
jours sans que personne le voie, et c'est le seul défaut du sprint 1 qui a
échappé à une recette de 115 contrôles.

Sur la liste des stagiaires d'une session (US-SES-05) : la brigade d'affectation
de chacun, ou une mention explicite quand il n'y en a pas.

Historique des affectations d'un stagiaire : consultable, avec les dates d'effet
et de fin. C'est ce que RG-20 demande de conserver ; le conserver sans pouvoir le
lire ne servirait à rien.

## 8. Habilitations

Domaine de l'organisation. Pédagogique en écriture ; planification, examens et
Direction de Formation en lecture ; administrateur aucun accès.

Attention à l'asymétrie déjà posée : la cellule planification LIT cette
répartition mais ne l'écrit pas, alors qu'elle écrit les salles attitrées. Et la
cellule pédagogique écrit la répartition sans pouvoir toucher aux salles. Les
deux tests existent depuis US-SES-03 ; vérifie qu'ils tiennent toujours.

## 9. Ce que cette story referme, ce qu'elle reporte

REFERME — les deux emplacements réservés du § 7, qui ne sont pas des reports de
critère au sens du tableau suivi en revue. Dis-le explicitement pour qu'ils ne
s'y glissent pas.

REPORTE — enchaînement A3, arrivée tardive : « le système signale le volume
horaire déjà dispensé dans cette brigade ». Suppose les séances et la progression
réalisée (US-PLAN-03, puis US-SUI-01 au sprint 4). La part implantable ici est
mince mais réelle : signaler qu'un stagiaire est affecté APRÈS la date de début
de la session, comme A3 d'US-SES-02 le fait pour une brigade créée tardivement.
Implante cette part, reporte le volume horaire, et consigne le report sur le
modèle de D-23 en nommant la story qui le referme.

## 10. Tests attendus

Groupe A — proposition, sans écriture

A1. Proposition nominale : 58 stagiaires, brigades déclarées à 20/20/18 —
    répartition 20/20/18, ET AUCUNE AFFECTATION EN BASE. La seconde assertion
    est celle qui compte.
A2. Stagiaires en surnombre : le surplus reste non affecté, aucune brigade ne
    dépasse son effectif déclaré, aucune brigade n'est créée.
A3. Stagiaires en nombre insuffisant : brigades non pleines, aucun avertissement.
A4. Déterminisme : deux appels successifs produisent la même proposition.
A5. Les stagiaires RADIÉS ne figurent pas dans la proposition.
A6. Les stagiaires DÉJÀ AFFECTÉS ne figurent pas dans la proposition.

Groupe B — contrôles à l'affectation

B1. Affectation nominale, journalisée.
B2. Stagiaire radié — refus.
B3. RG-20 : stagiaire déjà affecté dans la session — refus, brigade actuelle
    nommée, déplacement proposé.
B4. RG-19 : capacité de la salle atteinte — refus, marge restante chiffrée.
B5. RG-19, cas limite : affectation portant l'effectif réel EXACTEMENT à la
    capacité — ACCEPTÉE. Protège du décalage d'une unité, comme A5 d'US-SES-03.
B6. Dépassement de l'effectif DÉCLARÉ de la brigade, salle assez grande —
    ACCEPTÉE avec avertissement. Les deux assertions dans le même test : c'est la
    distinction du § 4, et elle ne se prouve pas autrement.
B7. Brigade sans salle attitrée — acceptée avec avertissement, pas de refus.
B8. E3 : validation avec des stagiaires non affectés — possible, avertissement
    présent, stagiaires restants énumérés.

Groupe C — base

C1. La contrainte de non-chevauchement du § 3, vérifiée PAR INSERTION DIRECTE
    court-circuitant le service : deux affectations ouvertes pour le même
    stagiaire — rejetées.
C2. Deux affectations historiques dont les périodes se recouvrent — rejetées si
    tu as retenu la contrainte d'exclusion ; sinon, test en couche services et
    mention explicite de ce que la base ne garantit pas.
C3. `ck_affectation_dates`, par insertion directe.
C4. Une affectation fermée et une ouverte pour le même stagiaire, périodes
    disjointes — ACCEPTÉES. C'est le cas normal après un déplacement.

Groupe D — validation transactionnelle

D1. Validation nominale : toutes les affectations enregistrées, journalisées.
D2. Tout ou rien : provoque un échec au milieu de la validation, vérifie
    qu'AUCUNE affectation n'a été écrite.
D3. Revalidation : après une proposition, radie un stagiaire par un autre chemin,
    puis valide — la ligne le concernant est refusée ou ignorée, jamais
    enregistrée, et jamais une erreur technique brute. C'est la règle du § 5, et
    sa seule preuve.
D4. Revalidation sur la capacité : entre proposition et validation, la salle
    attitrée d'une brigade est remplacée par une plus petite — le dépassement est
    détecté à la validation.

Groupe E — déplacement et effectif réel

E1. A2 : déplacement — l'ancienne affectation est FERMÉE à la date d'effet, une
    nouvelle est OUVERTE, jamais deux ouvertes, jamais de ligne écrasée.
E2. L'avertissement d'A2 sur les évaluations et la progression est réellement
    produit.
E3. Effectif réel : trois affectations ouvertes dont une pour un stagiaire radié
    — l'effectif réel vaut deux. Test de la définition de CLS-00.
E4. Effectif réel après déplacement : la brigade d'origine décroît, la brigade de
    destination croît, dans la même opération.
E5. Historique d'un stagiaire déplacé deux fois : trois lignes, une seule ouverte,
    dates cohérentes.
E6. Aucun champ `effectif_reel` n'existe sur `Brigade` : vérifie-le explicitement,
    c'est l'interdit du § 3 et il ne se voit pas autrement.

Groupe F — cycle HTTP réel

F1. Chemin nominal, profil pédagogique, sur CHAQUE adresse d'écriture :
    proposition, affectation individuelle, déplacement, retrait, validation.
F2. Le parcours complet par le vrai cycle : GET de l'écran, POST de proposition,
    POST d'ajustement, POST de validation, affectations en base. Pas seulement
    des appels de service. Leçon de P-30.
F3. Les trois nombres — effectif réel, effectif déclaré, capacité — sont
    RÉELLEMENT présents dans la réponse HTTP de l'écran de répartition.
F4. L'effectif réel est RÉELLEMENT affiché sur l'écran des brigades (US-SES-02)
    et sur la fiche de composition (US-SES-04). Les deux emplacements réservés,
    testés là où ils se trouvent. Leçon de P-25.
F5. Refus d'habilitation sur chaque adresse d'écriture : planification, examens,
    Direction de Formation, administrateur.
F6. Lecture accordée aux quatre profils habilités, refusée à l'administrateur.
F7. Test de garde du sprint 1 : cette story ajoute plusieurs adresses d'écriture,
    dont la proposition et la validation. Il doit passer sans modification.
F8. Navigation : l'écran de répartition est atteignable depuis la fiche de
    session pour un profil pédagogique, absent pour qui n'a pas l'écriture.

Groupe G — architecture

`tests/architecture` en entier. Aucun import de `ressources` dans `organisation` :
la capacité de la salle attitrée se lit par la propriété du § 0.4, méthode D-52.
Aucune classe au-delà de 200 lignes — le service de répartition est le candidat.

## 11. Définition de fini

Implanté, testé, relu par le sous-agent, commité. Suite `pytest` complète verte.
Répartition essayée RÉELLEMENT dans un navigateur, sur une session d'une
soixantaine de stagiaires et trois brigades, déplacement compris. Les deux
emplacements réservés vérifiés à l'œil. Mesure d'impression de l'écran de
répartition reportée dans `IMPRESSION-ANALYSE.md`. `DECISIONS.md` à jour le jour
même. Case cochée dans `docs/suivi/sprint-2.md`.

## 12. Ce que tu ne touches pas

Le backlog, le cahier des charges, le registre des risques, le diagramme de
classes. L'arbitrage du § 2 s'écrit dans `DECISIONS.md`, ligne « Impact sur les
livrables » — le critère 1 du backlog et la fiche CU-P3-06 devront être mis en
cohérence par le chef de projet.

US-SES-07 : aucune vue de consultation par brigade, aucun export.
Le paquetage Évaluations : aucune anticipation, même si l'historique des
affectations lui servira.

## 13. Ce que tu me rends

- Les réponses au § 0, en particulier le précédent de contrainte de période
  retenu et pourquoi.
- Les entrées `DECISIONS.md` : arbitrage du critère 1 contre la fiche et pourquoi
  il renverse D-26 sans l'infirmer, refus contre avertissement sur les deux
  plafonds, historisation ici et non pour `SalleAttitree`, comportement de la
  date d'effet, articulation radiation / fermeture d'affectation, report d'A3.
- Le compte des tests par groupe et le total de la suite.
- Le temps réellement passé, à la demi-heure près. Sixième mesure, 26 points
  livrés sur les 61 du sprint : à ce stade la clé de conversion doit être
  tranchée, pas estimée.