# Prompt 27 — US-INS-03 · Enregistrer les indisponibilités transmises

Sprint 2, story 8 sur 12. Must, 3 points. Application `ressources`, paquetage P4.

## 0. Étape 0 — vérifications avant toute ligne de code

1. LE MODÈLE VOISIN. `IndisponibiliteLieu`, livré à US-PLAN-02 : champs exacts,
   bornes en DATE ou en DATE-HEURE, contrainte de non-chevauchement présente ou
   absente, service et écrans associés. Cite fichier et migration. Cette story
   pose un modèle jumeau ; il ne doit pas diverger sans raison écrite.
2. L'EXTENSION. `btree_gist` a été installée au sprint 1 EXPLICITEMENT POUR
   RG-24 (D-56), et n'a jamais servi depuis. Vérifie qu'elle est bien présente
   dans la migration initiale et opérationnelle sur la base de test. Cette story
   est son premier usage réel : si quelque chose cloche, c'est maintenant qu'on
   le découvre, pas au déploiement.
3. LE PRÉCÉDENT DE CONTRAINTE DE PÉRIODE. Comment `AffectationBrigade`
   (US-SES-06) exprime-t-elle son non-chevauchement : `ExclusionConstraint` avec
   `btree_gist`, index unique partiel, ou couche services ? Suis ce précédent.
4. LE DOMAINE D'HABILITATION. Lis `DOMAINES_CATALOGUE`,
   `docs/suivi/HABILITATIONS.md` et la matrice § 11.2. Dans quel domaine la
   cellule PLANIFICATION écrit-elle, et dans quel domaine vivent les
   instructeurs et les qualifications ? Voir § 5 : c'est le point le plus
   risqué de cette story.
5. `Instructeur` : nom exact des champs, mécanisme d'archivage, et confirme
   qu'AUCUNE relation ne lie un instructeur à un compte utilisateur (§ 4).
6. Suite `pytest` verte avant de commencer.

## 1. Ce que porte cette story

Besoin BF-INS-03. Cas d'utilisation CU-P4-03. Règles RG-23 et RG-24 (RG-25 est
reportée, § 8). Séquence SEQ-04. Classe CLS-04.
ACTEUR : CELLULE PLANIFICATION. Acteur métier hors système : l'instructeur, qui
transmet l'information par les canaux en vigueur au CIT.

Critères d'acceptation du backlog v8 :

1. L'instructeur ne dispose d'aucun accès au système : la saisie est effectuée
   par la cellule planification à partir d'une transmission externe.
2. Une indisponibilité comporte une date de début, une date de fin et un motif.
3. La saisie est horodatée et rattachée à l'utilisateur qui l'effectue, et non à
   l'instructeur concerné.
4. Les indisponibilités sont prises en compte comme contrainte lors de la
   génération du programme.
5. Une indisponibilité déclarée sur un créneau déjà affecté déclenche une alerte
   signalant les séances concernées.
6. Les indisponibilités passées sont conservées à des fins d'historique.

LES CRITÈRES 4 ET 5 SONT DES REPORTS. Voir § 8. Dis-le explicitement dans ton
compte rendu : cette story sera cochée livrée alors que la moitié de son effet
métier n'est observable nulle part avant le sprint 3.

HORS PÉRIMÈTRE : le traitement des séances impactées, c'est-à-dire le
remplacement, la substitution et la déprogrammation. C'est CU-P5-07, US-PLAN-09,
sprint 3. Ici on ENREGISTRE, là on TRAITE.

## 2. Le modèle

`app/ressources/models.py`, `Meta.db_table = "ressources_indisponibilite_instructeur"`.

`IndisponibiliteInstructeur` :

- `instructeur` — clé étrangère vers `Instructeur`, `on_delete=PROTECT`,
  `related_name="indisponibilites"`.
- `debut`, `fin` — bornes de la période, EN DATE-HEURE. Voir ci-dessous.
- `motif` — le déclencheur de la fiche nomme mission, permission, stage,
  indisponibilité médicale. Décide entre énumération fermée et texte libre, et
  justifie : une énumération se filtre et se compte, un texte libre encaisse les
  cas non prévus. Si tu retiens l'énumération, prévois une valeur « autre » avec
  précision libre, faute de quoi la première mission atypique sera saisie sous un
  motif faux.

Hérite de la classe de base d'horodatage et de rattachement à l'auteur — c'est
elle qui porte RG-23 (§ 4).

GRANULARITÉ HORAIRE, pas journalière. La fiche est explicite : « sa granularité
horaire — d'une demi-journée à plusieurs semaines ». Une indisponibilité d'un
après-midi doit pouvoir coexister avec des séances du matin ; des bornes en date
seule rendraient cette distinction impossible et fausseraient le moteur de
génération dès qu'il existera.

SI `IndisponibiliteLieu` EST EN DATE SEULE (§ 0.1), signale-le comme une
incohérence entre deux modèles jumeaux, dans `PROBLEMES.md`, avec sa conséquence :
le moteur devra traiter deux granularités différentes pour la même notion de
ressource occupée. NE LA CORRIGE PAS ici — ce serait modifier un livrable du
sprint 1 hors périmètre, et la correction appartient au chef de projet.

En base :

- Contrainte d'exclusion exprimant RG-24 : deux périodes du même instructeur ne
  peuvent se recouvrir. `ExclusionConstraint` avec `btree_gist` sur
  `(instructeur, =)` et l'intervalle `(debut, fin)` avec chevauchement. C'est
  l'usage exact pour lequel l'extension a été installée au sprint 1.
  Nomme-la selon la convention § 2.1 de la note d'implémentation.
- `ck_indisponibilite_instructeur_bornes` — `fin > debut`. C'est E1.

Décide et documente le comportement des BORNES : une période finissant à 12h00 et
une autre commençant à 12h00 se chevauchent-elles ? Avec un intervalle
semi-ouvert `[debut, fin)`, non — et c'est ce qu'il faut, sans quoi deux
demi-journées consécutives seraient déclarées sécantes. Écris-le, teste-le, ne le
laisse pas dépendre d'un réglage par défaut.

## 3. RG-24 — la fusion, et non le refus

RG-24 : « Les périodes d'indisponibilité d'un même instructeur ne se chevauchent
pas ; deux périodes sécantes sont FUSIONNÉES. » E2 le confirme : le système
PROPOSE LA FUSION plutôt que la création d'un doublon.

C'EST L'INVERSE DE RG-14. À US-SES-03, deux salles attitrées sur des périodes
sécantes donnaient un refus. Ici, un chevauchement n'est pas une erreur de
l'agent : c'est le signe que la même indisponibilité arrive par deux canaux, ou
qu'une mission s'est prolongée. Le refus ferait ressaisir, la fusion enregistre
la réalité. Ne transforme pas la fusion en refus par réflexe de symétrie ;
consigne au contraire pourquoi deux règles voisines divergent.

Déroulé attendu :

1. l'agent saisit une période ;
2. le système détecte le chevauchement avec une ou plusieurs périodes existantes
   du même instructeur ;
3. il PRÉSENTE la fusion qu'il propose — bornes résultantes, périodes absorbées —
   et demande confirmation (BNF-09) ;
4. à la confirmation, la fusion est enregistrée EN UNE SEULE TRANSACTION :
   périodes absorbées supprimées, période résultante écrite. Tout ou nulle part.

Bornes résultantes : la plus précoce des débuts, la plus tardive des fins. Une
période nouvelle entièrement contenue dans une existante ne produit aucun
changement de bornes — dis-le à l'agent plutôt que d'enregistrer silencieusement
un non-événement.

LE MOTIF DE LA PÉRIODE FUSIONNÉE — ni le backlog ni la fiche ne le tranchent, et
c'est une vraie question : une mission du 3 au 10 et une permission du 8 au 15
fusionnent en une seule période du 3 au 15, dont le motif ne peut être ni l'un ni
l'autre sans mentir. Trois voies, choisis et justifie :

- le motif est demandé à l'agent sur l'écran de confirmation, pré-rempli avec le
  nouveau — le plus honnête, un geste de plus ;
- les motifs sont concaténés — conserve l'information, salit la donnée et rend
  le filtrage par motif inexploitable ;
- la fusion n'est proposée que pour des motifs identiques, un chevauchement de
  motifs différents étant refusé avec invitation à ajuster les bornes — le plus
  strict, mais il rejette un cas réel.

Quel que soit ton choix, JOURNALISE LE CONTENU DES PÉRIODES ABSORBÉES avant leur
disparition : bornes et motif. Une fusion détruit de l'information, et le journal
est le seul endroit où elle survit.

Ne t'appuie pas sur la seule contrainte en base pour détecter le chevauchement :
une `IntegrityError` ne te dit pas AVEC QUOI il y a conflit, et E2 exige de
nommer les périodes concernées. Détecte en couche services POUR PROPOSER, et
laisse la contrainte en base garantir — deux rôles distincts, comme à US-SES-05
entre l'analyse et la confirmation.

## 4. RG-23 — la saisie déléguée

« L'indisponibilité est saisie de manière déléguée. Elle est horodatée et
rattachée à l'AGENT DE LA CELLULE PLANIFICATION qui l'enregistre, JAMAIS à
l'instructeur concerné. La responsabilité de l'exactitude incombe à la cellule
qui saisit. »

C'est déjà ce que fait la classe de base d'horodatage et de rattachement à
l'auteur. Rien de spécial à coder — mais un test explicite, nommé de façon que la
règle soit lisible sans aller la chercher : l'auteur enregistré est l'utilisateur
connecté, et il n'existe AUCUN champ reliant l'indisponibilité à un compte de
l'instructeur.

Le critère 1 — « l'instructeur ne dispose d'aucun accès au système » — ne demande
aucun code : il demande qu'on n'en écrive pas. Aucun écran de déclaration en
libre-service, aucune notification à l'instructeur, aucune relation entre
`Instructeur` et le modèle utilisateur. Vérifie l'absence de cette relation (§ 0.5)
et écris un test d'architecture qui la constate, sur le modèle des tests de
couches : c'est une contrainte de conception durable, pas une préférence du
moment.

Instructeur ARCHIVÉ : refus d'enregistrer une indisponibilité, avec message
correctif. Même raisonnement que la formation archivée à US-SES-01.

## 5. Le domaine d'habilitation — le point le plus risqué

L'objet concerne un instructeur ; l'acteur est la cellule PLANIFICATION.

Si tu classes cette indisponibilité dans le domaine des instructeurs et
qualifications — où la cellule PÉDAGOGIQUE écrit — il faudra ouvrir l'écriture de
ce domaine à la planification, donc lui donner le droit de créer, modifier et
supprimer des instructeurs et de toucher à la matrice de qualification. Le
critère 5 d'US-INS-02 dit exactement l'inverse : « la cellule planification
consulte la matrice sans pouvoir la modifier. »

L'indisponibilité appartient donc au domaine où la planification écrit — celui
des lieux et du calendrier, qui porte déjà `IndisponibiliteLieu`. C'est cohérent :
ce domaine regroupe la disponibilité des ressources, salles et instructeurs
confondus, et non la gestion des instructeurs eux-mêmes.

VÉRIFIE-LE CONTRE LA MATRICE § 11.2 (§ 0.4) avant d'appliquer. Si la matrice
prévoit un troisième domaine, c'est elle qui fait foi. Si elle place les
indisponibilités dans le domaine des instructeurs, NE CODE PAS : remonte-moi la
contradiction avec le critère 5 d'US-INS-02, c'est un arbitrage de chef de projet.

Matrice attendue pour ce domaine : planification en écriture ; pédagogique,
examens et Direction de Formation en lecture ; administrateur aucun accès.

Teste l'asymétrie dans les deux sens, comme à US-SES-03 :
- la cellule PÉDAGOGIQUE gère les instructeurs mais NE PEUT PAS enregistrer une
  indisponibilité ;
- la cellule PLANIFICATION enregistre les indisponibilités mais NE PEUT PAS
  modifier un instructeur ni une qualification.

## 6. Les enchaînements

A2 — INDISPONIBILITÉ ANNULÉE. La période est supprimée, journalisée. La fiche
précise que les séances antérieurement remplacées NE SONT PAS RÉTABLIES
automatiquement : le remplacement est un fait accompli qui a pu être communiqué.
Aucun code aujourd'hui, mais consigne la règle : quelqu'un, dans trois mois,
trouvera « logique » de rétablir, et il aura tort.

A3 — INDISPONIBILITÉ PROLONGÉE. La période est étendue par modification des
bornes. La recherche des séances impactées ne devra porter QUE SUR L'EXTENSION,
pas sur toute la période — sans quoi l'agent se verra represser des séances déjà
traitées. Reporté avec le critère 5, mais note la subtilité : elle sera perdue si
elle n'est écrite nulle part.

A4 — INDISPONIBILITÉ RÉTROACTIVE. Une période couvrant des dates passées est
ACCEPTÉE, sans avertissement ni refus. C'est un cas normal : l'information arrive
après les faits. Le critère 6 va dans le même sens — les indisponibilités passées
sont conservées. N'ajoute donc aucun contrôle de date minimale, et écris un test
qui le prouve, faute de quoi quelqu'un ajoutera « au moins aujourd'hui » un jour
en croyant bien faire.

## 7. Écrans

Pas de nouvelle rubrique de navigation : les indisponibilités d'instructeur
vivent là où vivent les instructeurs et les lieux. Suis exactement l'organisation
retenue pour `IndisponibiliteLieu` (§ 0.1) — deux écrans jumeaux qui se
ressemblent valent mieux que deux écrans voisins qui diffèrent sans raison.

- Sur la fiche d'un instructeur : ses indisponibilités, à venir et passées,
  distinguées et triées. Le critère 6 impose de conserver les passées ; les
  conserver sans les montrer ne servirait à rien.
- Écran de saisie : instructeur, bornes avec heures, motif. Confirmation de
  fusion le cas échéant (§ 3).
- Sur la liste des instructeurs : une colonne d'indisponibilité courante ou à
  venir, si l'écran des lieux en porte une équivalente — la symétrie compte plus
  que l'élégance. Colonne de DONNÉE, donc imprimée (D-63).
- Modification et suppression, journalisées.

Mesure la largeur imprimable des écrans touchés et reporte-la dans
`IMPRESSION-ANALYSE.md`. L'écran Instructeurs débordait déjà de 33 px au
2026-09-08 : une colonne de plus l'aggravera. Ne corrige pas ici, mets la mesure
à jour pour le sprint 4.

## 8. Ce que cette story referme, ce qu'elle reporte

REFERME — aucun report ouvert du tableau.

REPORTE — trois choses, à consigner sur le modèle de D-23 :

- CRITÈRE 4 et RG-25, prise en compte comme contrainte dure à la génération et à
  toute nouvelle affectation. Vers US-PLAN-04 (contraintes dures) et le moteur.
- CRITÈRE 5, points 4 et 5 du scénario nominal : recherche des séances
  programmées recoupant la période, énumération avec brigade, matière et
  créneau, enchaînement proposé vers CU-P5-07. Vers US-PLAN-03 puis US-PLAN-09
  (sprint 3).
- A3, restriction de la recherche à la seule extension ; A4, signalement des
  séances passées comme relevant du suivi prescrit/réalisé. Mêmes destinations.

Ces reports portent sur DES CRITÈRES D'ACCEPTATION, donc ils entrent au tableau
suivi en revue. Dis explicitement combien il en compte après cette story, en
repartant du compte vérifié sur le code dans `AVANCEMENT.md` et non de celui
annoncé en revue — l'écart entre les deux est déjà un point à l'ordre du jour du
26 septembre.

Écris aussi, en une phrase, ce qui reste OBSERVABLE de cette story une fois les
reports retirés : une saisie, une fusion, un historique. C'est ce que la revue
pourra constater ; le reste se vérifiera au sprint 3.

## 9. Tests attendus

Groupe A — modèle et enregistrement

A1. Enregistrement nominal, journalisé, auteur = utilisateur connecté.
A2. RG-23 : l'auteur est l'agent, et aucun champ ne relie l'indisponibilité à un
    compte de l'instructeur. Nomme le test pour que la règle soit lisible.
A3. E1 : fin antérieure au début, puis fin ÉGALE au début — refus.
A4. Instructeur archivé — refus, message correctif.
A5. A4 : période entièrement dans le passé — ACCEPTÉE, sans avertissement.
A6. Période à cheval sur aujourd'hui — acceptée.
A7. Granularité : deux indisponibilités d'un même jour, matin et après-midi, sur
    des heures disjointes — ACCEPTÉES toutes deux. Ce test tombe si quelqu'un
    ramène les bornes à des dates.

Groupe B — base

B1. La contrainte d'exclusion rejette deux périodes sécantes du même instructeur,
    PAR INSERTION DIRECTE court-circuitant le service. Premier usage réel de
    `btree_gist` : si ce test ne passe pas, l'extension n'a jamais fonctionné et
    on l'apprend ici.
B2. Deux périodes sécantes d'instructeurs DIFFÉRENTS — acceptées.
B3. Bornes contiguës, fin de l'une égale au début de l'autre — ACCEPTÉES.
    Documente le comportement retenu au § 2 et vérifie-le.
B4. `ck_indisponibilite_instructeur_bornes`, par insertion directe.

Groupe C — fusion

C1. Chevauchement partiel : la fusion proposée porte les bornes attendues, ET
    RIEN N'EST ÉCRIT avant confirmation. Les deux assertions.
C2. Confirmation : une seule période subsiste, aux bornes fusionnées, les
    absorbées supprimées.
C3. Transaction : provoque un échec au milieu de la fusion, vérifie qu'aucune
    période n'a été supprimée ni créée. Une fusion à moitié appliquée détruirait
    une indisponibilité sans la remplacer.
C4. Fusion absorbant DEUX périodes existantes d'un coup.
C5. Période nouvelle entièrement contenue dans une existante : signalée comme
    sans effet, pas enregistrée en double.
C6. Le journal conserve les bornes et le motif des périodes absorbées.
C7. Motifs différents : le comportement que tu as retenu au § 3, testé et nommé.
C8. Le message de proposition NOMME les périodes concernées avec leurs bornes
    (E2), il ne dit pas « chevauchement détecté ».

Groupe D — cycle HTTP réel

D1. Chemin nominal, profil PLANIFICATION, sur chaque adresse d'écriture : saisie,
    confirmation de fusion, modification, suppression.
D2. L'écran de proposition de fusion affiche RÉELLEMENT les bornes et les
    périodes absorbées dans la réponse HTTP. Leçon de P-25.
D3. Profil PÉDAGOGIQUE : lecture accordée, ÉCRITURE REFUSÉE sur chaque adresse.
D4. Profil PLANIFICATION sur les adresses d'écriture des instructeurs et des
    qualifications : REFUSÉ. Le pendant du précédent, et la preuve que le domaine
    du § 5 est bien choisi.
D5. Examens et Direction de Formation : lecture accordée, écriture refusée.
    Administrateur : aucun accès.
D6. Test de garde du sprint 1 : passe sans modification.
D7. Les indisponibilités passées sont RÉELLEMENT affichées sur la fiche de
    l'instructeur, distinguées des futures (critère 6).
D8. Navigation : l'écran de saisie est atteignable pour un profil planification,
    absent pour qui n'a pas l'écriture.

Groupe E — architecture

E1. `tests/architecture` en entier.
E2. Le test d'absence de relation entre `Instructeur` et le modèle utilisateur
    (§ 4).

## 10. Troisième modèle de période — à évaluer, pas à imposer

Avec `IndisponibiliteLieu`, `AffectationBrigade` et celui-ci, le projet compte
trois modèles portant une période et une contrainte de non-chevauchement. C'est
le seuil où D-27 et D-32 ont fait remonter du code commun au patron.

Évalue, dis ce que tu recommandes, et N'IMPLANTE RIEN SANS MON ACCORD : une
abstraction posée sur trois cas qui divergeront demain coûte plus cher que trois
implantations claires. Les arguments contre sont réels — les trois modèles n'ont
ni la même granularité ni le même traitement du chevauchement, l'un fusionnant là
où les autres refusent. Argumente dans les deux sens et laisse-moi trancher.

## 11. Définition de fini

Implanté, testé, relu par le sous-agent, commité. Suite `pytest` complète verte.
Saisie et fusion essayées RÉELLEMENT dans un navigateur, avec une période à
cheval sur une autre. Mesure d'impression reportée. `DECISIONS.md` à jour le jour
même. Case cochée dans `docs/suivi/sprint-2.md`.

## 12. Ce que tu ne touches pas

Le backlog, le cahier des charges, le registre des risques, le diagramme de
classes.

`IndisponibiliteLieu` : aucune correction, même si le § 0.1 révèle une
incohérence de granularité. Signalement dans `PROBLEMES.md`, rien de plus.

Le traitement des séances impactées : c'est US-PLAN-09, sprint 3. Aucune
anticipation, pas même une méthode « qui servira ».

## 13. Ce que tu me rends

- Les réponses au § 0, en particulier le domaine retenu au § 5 et sa
  vérification contre la matrice.
- Le choix de motif à la fusion (§ 3) et les deux voies écartées.
- Le comportement des bornes retenu (§ 2), en une phrase.
- Ta recommandation sur le § 10, argumentée dans les deux sens.
- Les entrées `DECISIONS.md` : fusion plutôt que refus et pourquoi RG-24 diverge
  de RG-14, granularité horaire, non-rétablissement des séances après annulation,
  acceptation des périodes rétroactives, les trois reports.
- Le compte des reports au tableau après cette story, à partir du compte vérifié
  sur le code.
- Le compte des tests par groupe et le total de la suite.
- Le temps réellement passé, à la demi-heure près.