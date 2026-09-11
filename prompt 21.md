# Prompt 21 — US-SES-02 · Constituer les brigades d'une session

Sprint 2, story 2 sur 12. Must, 5 points. Lot WBS 5.2.3.

## 0. Étape 0 — vérifications avant toute ligne de code

Comme au prompt précédent : ce prompt énonce des hypothèses, le code réel fait
foi, tout écart se consigne dans `docs/suivi/DECISIONS.md` AVANT de coder.

1. LE POINT BLOQUANT DE CETTE STORY. Lis
   `tests/architecture/test_couches.py::DEPENDANCES_AUTORISEES` et dis-moi
   explicitement quel sens est autorisé entre `organisation` et `ressources`.
   La question n'est pas rhétorique : `Brigade` porte une salle attitrée vers
   `ressources.Lieu` dans CLS-00, tandis que `PeriodeCalendrier` (`ressources`,
   US-PLAN-01, ce sprint) cible `Session` et `Brigade`. Les deux associations
   traversent la frontière en sens contraires ; une seule des deux peut être
   posée là où le diagramme la place. C'est le cas exact que D-52 a résolu pour
   `Qualification`, et dont la dernière ligne annonçait que « le paquetage
   organisation en aura probablement besoin ».
   Tu ne résous PAS ce problème dans cette story. Tu le documentes, tu poses
   dans `DECISIONS.md` les deux options avec leurs conséquences, et tu me le
   remontes pour arbitrage avant US-SES-03.
2. Comment `ServiceReferentiel` gère-t-il une sous-ressource (`ElementReferentiel`
   composé depuis l'écran d'une formation) : héritage du patron ou fonctions
   libres `decrire_opposants` / `valider_instance` (D-32) ? Habilitation et
   journalisation, comment sont-elles câblées dans ce cas ? Les brigades sont la
   même figure, et cette story suit ce précédent, pas un autre.
3. Le mécanisme d'avertissement posé à US-SES-01 : signature réelle, et où il
   vit. C'est sa deuxième utilisation ; si elle demande de le tordre, c'est qu'il
   n'était pas générique — dis-le au lieu de le contourner.
4. `Session` telle qu'elle a été livrée : nom exact des champs, du service, des
   adresses, du gabarit de fiche, et l'emplacement « Brigades » réservé.
5. La suite `pytest` complète est-elle verte avant que tu commences ? Si non,
   arrête-toi là et rends-m'en compte.

## 1. Ce que porte cette story

Besoin BF-SES-02. Cas d'utilisation CU-P3-02. Règles RG-12, RG-15, RG-16.
Classe `Brigade` (CLS-00, paquetage P3). Acteur en écriture : cellule pédagogique.

Critères d'acceptation du backlog v8 :

1. Les brigades sont saisies manuellement : le système enregistre la répartition
   décidée sans la calculer.
2. Toute session comporte au minimum une brigade.
3. Chaque brigade porte un intitulé et un effectif.
4. La somme des effectifs des brigades est comparée à l'effectif de la session ;
   un écart est signalé.
5. Une brigade dont le programme est en cours ne peut être supprimée.

HORS PÉRIMÈTRE, explicitement :

- La salle attitrée. C'est US-SES-03, un cas d'utilisation autonome porté par un
  AUTRE ACTEUR — la cellule planification, détentrice du catalogue des lieux
  (terrain du 23 août). Les points 4 à 6 du scénario nominal de CU-P3-02, les
  exceptions E1 et E2, et les règles RG-13 et RG-14 n'appartiennent pas à cette
  story. N'anticipe rien, pas même la clé étrangère (§ 0.1).
- L'écran de composition de session avec taux d'occupation : US-SES-04.
- L'affectation des stagiaires et l'effectif réel : US-SES-05 et US-SES-06.

## 2. Le modèle

`app/organisation/models.py`, `Meta.db_table = "organisation_brigade"`.

`Brigade`, d'après CLS-00 :

- `session` — clé étrangère vers `Session`, `on_delete=PROTECT`,
  `related_name="brigades"`.
- `designation` — texte court, obligatoire (EXP1, R.INFO 1, CDP...).
- `effectif_previsionnel` — entier, strictement positif.

Hérite de la classe de base d'horodatage et de rattachement à l'auteur.
Pas de mixin d'archivage : une brigade se supprime ou se conserve, elle ne
s'archive pas.

`PROTECT` sur `session` et non `CASCADE` : supprimer une session emporterait ses
brigades, donc à terme les affectations de stagiaires, les programmes et les
notes qui en dépendent. `.claude/rules/modeles.md` ne prescrit `CASCADE` qu'en
composition stricte, et le refus explicite avec énumération des opposants est ce
qu'exige E3 de la fiche générique. Conséquence assumée à consigner : une session
constituée devient non supprimable tant que ses brigades existent.

INTERDIT : aucun champ `effectif_reel` stocké. C'est un attribut dérivé de CLS-00
— nombre d'affectations ouvertes de stagiaires non radiés — et le § 9 du
diagramme de classes interdit de le stocker. Il n'est pas calculable aujourd'hui
(`Stagiaire` arrive à US-SES-05) : réserve son emplacement à l'écran, vide et
commenté, et note-le pour US-SES-06.

INTERDIT également : aucune méthode qui calcule un nombre de brigades ou une
répartition. RG-12 est structurante — « le nombre et la composition des brigades
relèvent d'une décision humaine ; le système enregistre ce découpage sans le
calculer ». Une règle structurante ne se réinterprète jamais. Ne propose pas
d'effectif par défaut égal à l'effectif attendu divisé par le nombre de brigades,
même « pour rendre service » : ce serait un calcul de composition déguisé en
confort de saisie.

À ne pas confondre avec US-SES-06, qui propose bien une répartition automatique —
mais des STAGIAIRES dans des brigades DÉJÀ CONSTITUÉES. La fiche CU-P3-06
signale elle-même que les deux se ressemblent et que la confusion est facile.

## 3. Contraintes : ce qui descend en base, ce qui reste en services

En base, noms conformes à la note d'implémentation § 2.1 :

- `ck_brigade_effectif` — `effectif_previsionnel > 0`.
- `uq_brigade_session_designation` — unicité composite sur
  `(session_id, UPPER(designation))`, insensible à la casse comme D-21 et D-26.

  ATTENTION, écart assumé avec un livrable, à consigner soigneusement. La note
  d'implémentation § 5.5 prescrit une unicité de la désignation AU SEIN DU TYPE
  DE FORMATION, remontant par la session et la formation jusqu'au type, et la
  classe en couche services parmi les sept contraintes non descendables. Prise à
  la lettre, elle refuserait de créer une brigade EXP1 dans la session 2027 parce
  que la session 2026 de la même formation en porte déjà une — ce qui interdit
  purement et simplement les sessions annuelles successives. Les progressions
  d'instruction établissent que l'unicité n'est pas globale ; elles n'établissent
  pas qu'elle remonte jusqu'au type.
  Implante l'unicité au sein de la SESSION, en base. Consigne l'écart avec la
  note d'implémentation, l'argument ci-dessus, et deux conséquences : c'est une
  question à poser au chef de bureau pédagogique, et le décompte « sept
  contraintes en couche services » du mémoire et du dossier d'architecture passe
  à six. Cette seconde conséquence n'est pas cosmétique : ce décompte est un
  argument de soutenance sur la justification de la couche services.

En couche services :

- Critère 4 / RG-15 — comparaison de la somme des effectifs prévisionnels à
  l'effectif attendu de la session : porte sur un agrégat.
- Critère 2 — au moins une brigade par session constituée : voir § 4.
- A3 — brigade ajoutée après le démarrage de la session.

## 4. Le critère 2 : une postcondition, pas un invariant

« Toute session comporte au minimum une brigade » ne peut pas être vrai à tout
instant : US-SES-01 crée des sessions sans aucune brigade, et c'est le
déroulement normal du métier — on ouvre la session, puis on la découpe. Une
contrainte de cardinalité minimale en base aurait rendu US-SES-01 inécrivable.

C'est donc une postcondition de CU-P3-02, à porter en deux temps :

- Refus de supprimer la DERNIÈRE brigade d'une session : message désignant
  l'action corrective (créer une autre brigade d'abord, ou supprimer la session
  entière). Testé.
- Signalement, à l'écran des brigades d'une session et sur la liste des sessions,
  d'une session qui n'a encore aucune brigade. Signalement, pas blocage : une
  session ouverte ce matin et découpée cet après-midi n'est pas en faute.

Consigne cette lecture du critère 2 dans `DECISIONS.md` avec le raisonnement :
elle sera relue en soutenance et doit tenir toute seule.

## 5. RG-15 — un indicateur permanent, pas un message qui passe

L'écart entre la somme des effectifs prévisionnels et l'effectif attendu de la
session est un ÉTAT, pas un événement. Pendant la constitution il est normal :
après la première brigade sur trois, la somme est nécessairement inférieure.
Un message flash à chaque enregistrement produirait un avertissement systématique,
donc un avertissement qu'on apprend à ignorer en trois jours.

Rends-le en indicateur permanent en tête de l'écran des brigades : effectif
attendu de la session, somme des effectifs prévisionnels, écart signé. Neutre
quand les deux coïncident, signalé sinon — couleur TOUJOURS doublée d'un mot,
règle de la charte rappelée par D-63. Jamais de blocage : RG-15 est souple, et
l'effectif attendu est prévisionnel par nature, l'effectif réel n'étant connu
qu'à l'inscription des stagiaires.

Réemploie le mécanisme d'avertissement posé à US-SES-01. C'est sa deuxième
utilisation, donc son premier vrai test de généricité : s'il faut le tordre pour
qu'il serve ici, c'est qu'il ne servira pas non plus à US-SES-06 ni à
US-PLAN-07 — dans ce cas, corrige le mécanisme dans `noyau`, jamais par une
variante locale dans `organisation`, et consigne la correction.

L'enchaînement A3 relève du même registre : une brigade créée après la date de
début de sa session donne lieu à un avertissement rappelant que sa progression
démarrera en décalage, ce qui est normal au regard de RG-16 et ne doit jamais
être « rattrapé ». La part de A3 qui annonce que le programme reste à générer
suppose `ProgrammeHebdomadaire` : hors périmètre, à noter pour US-PLAN-03.

## 6. Le service

`app/organisation/services/brigade.py`.

Suis le précédent de `ServiceReferentiel` identifié à l'étape 0.2 : les brigades
sont une sous-ressource composée depuis l'écran d'une session, comme les éléments
de référentiel le sont depuis l'écran d'une formation. Elles n'ont pas d'écran de
premier niveau, pas de pagination (une session porte deux à six brigades), pas de
recherche texte libre. Si `ServiceReferentiel` n'hérite pas du patron, celui-ci
n'en hérite pas non plus, et réutilise les mêmes fonctions libres de
`noyau/services/gestion.py`.

Ce qu'il porte :

- `lister(agissant, session)` — les brigades d'une session, ordonnées par
  désignation, avec l'indicateur d'écart du § 5.
- `creer`, `modifier`, `supprimer` — habilitation vérifiée, opérations
  journalisées, `ProtectedError` intercepté et opposants énumérés.
- Le refus de suppression de la dernière brigade (§ 4).
- `DOMAINE` identique à celui de `ServiceSession` : les brigades appartiennent au
  même domaine d'habilitation P3, pas à un domaine propre.

## 7. Écrans

Aucune nouvelle rubrique de navigation. Les brigades vivent dans la rubrique
Sessions, sur un écran accroché à la fiche de session — l'emplacement réservé et
commenté par US-SES-01 se remplit ici. Souviens-toi de P-25 : un emplacement
réservé qu'on croit rempli et qui ne l'est pas reste ouvert quatre jours sans que
personne le voie. Vérifie à l'écran, pas seulement par un test.

L'écran présente, dans cet ordre : le rappel de la session (formation, période,
effectif attendu) — étape 2 du scénario nominal ; l'indicateur d'écart du § 5 ;
la liste des brigades constituées, avec pour chacune sa désignation, son effectif
prévisionnel, un emplacement « effectif réel » vide et commenté réservé à
US-SES-06, et ses actions ; le formulaire de création d'une brigade.

Colonne Actions masquée à l'impression par le gabarit générique (D-63), aucune
colonne de donnée masquée.

Confirmation explicite avant suppression (BNF-09). Messages d'erreur indiquant
l'action corrective (BNF-10) : « La brigade EXP1 est la seule de cette session »
et non « suppression impossible ».

Depuis la fiche de session, un lien vers cet écran ; depuis cet écran, un retour
vers la session. Leçon de P-26 : un écran doit être atteignable, et cela se teste.

## 8. Habilitations

Même domaine et même matrice qu'US-SES-01 (P3 — Organisation) : pédagogique en
écriture ; planification, examens et Direction de Formation en lecture ;
administrateur aucun accès. Rien de neuf à déclarer si le domaine est bien
partagé — vérifie-le plutôt que de le supposer.

## 9. Ce que cette story referme, ce qu'elle reporte

REFERME — rien. Aucun report ouvert ne se referme ici.

Corrige explicitement `docs/suivi/AVANCEMENT.md` sur ce point : la ligne « D-54,
volet brigade (lieu affecté à une brigade), referme US-SES-02 » est fausse tant
que la clé étrangère vers `Lieu` n'est pas posée, ce que cette story ne fait pas
(§ 0.1 et § 1). Ce volet se refermera à US-SES-03. C'est exactement le genre
d'écart que la revue du 26 septembre doit vérifier sur le code et non sur la
déclaration.

REPORTE — critère 5, « une brigade dont le programme est en cours ne peut être
supprimée ». `ProgrammeHebdomadaire` et `Seance` appartiennent à US-PLAN-03 et
US-PLAN-04. Aucun code spécifique : le `PROTECT` que ces stories poseront vers
`Brigade` produira le refus et l'énumération sans une ligne de plus dans
`organisation`. Consigne le report sur le modèle de D-23, avec un test qui
constate qu'aucun opposant n'existe aujourd'hui — précédent exact de D-54.

REPORTE également, sans que ce soit un report de critère : l'effectif réel
(US-SES-06), le volet « programme à générer » de A3 (US-PLAN-03), la salle
attitrée (US-SES-03, sous réserve de l'arbitrage du § 0.1).

## 10. Tests attendus

Groupe A — couche services

A1. Création nominale d'une brigade : rattachée à sa session, journalisée.
A2. Effectif prévisionnel nul, puis négatif — refus.
A3. Désignation en doublon dans la MÊME session, casse indifférente — refus,
    message désignant la brigade existante.
A4. Même désignation dans une AUTRE session de la même formation — ACCEPTÉE.
    Ce test porte l'écart du § 3 ; nomme-le pour que son intention soit lisible
    sans lire la décision.
A5. Critère 4 / RG-15, trois cas dans trois tests : somme inférieure, somme
    égale, somme supérieure à l'effectif attendu. Dans les trois, les brigades
    SONT enregistrées ; dans le premier et le troisième, un écart est signalé.
A6. A3 de la fiche : brigade créée après la date de début de la session —
    enregistrée, avec avertissement de décalage.
A7. Critère 2 : suppression de la dernière brigade d'une session — refus.
A8. Suppression d'une brigade parmi plusieurs — acceptée et journalisée.
A9. Suppression d'une session portant des brigades — refusée, brigades
    énumérées.
A10. Aucun calcul de composition : vérifie qu'une création sans effectif saisi
    est refusée et qu'aucune valeur par défaut n'est proposée (RG-12).

Groupe B — contraintes réellement en base

Insertion court-circuitant le service, `IntegrityError` attendue, pour
`ck_brigade_effectif` et `uq_brigade_session_designation`. Une contrainte
déclarée en `Meta.constraints` mais absente de la migration passerait tout le
groupe A sans exister.

Groupe C — cycle HTTP réel (`reverse()` + `client`)

C1. Chemin nominal, profil pédagogique : GET de l'écran des brigades d'une
    session, POST création, POST modification, POST suppression, chacun vérifié
    en base après coup.
C2. Refus d'habilitation par le cycle HTTP sur chacune des trois adresses
    d'écriture : planification, examens, Direction de Formation, administrateur.
C3. Lecture accordée aux quatre profils habilités, refusée à l'administrateur.
C4. Le test de garde du sprint 1 — toute adresse d'écriture figure à la table des
    refus — passe sans modification. S'il échoue, c'est une adresse oubliée à la
    table, jamais le test à ajuster.
C5. Navigation : l'écran des brigades est atteignable depuis la fiche de session,
    et la fiche de session porte bien le lien.
C6. L'indicateur d'écart du § 5 est VISIBLE dans la réponse HTTP, avec les deux
    nombres et le mot qui double la couleur. Leçon de P-25 : un service testé ne
    prouve pas que l'écran affiche ce qu'il produit.
C7. Le signalement d'une session sans aucune brigade apparaît réellement, sur
    l'écran des brigades et sur la liste des sessions.
C8. Le refus de suppression de la dernière brigade se produit aussi par le vrai
    cycle HTTP, pas seulement en appelant le service. Leçon de P-30 : un service
    générique bien testé ne garantit pas que l'écran y mène.

Groupe D — architecture

`tests/architecture` passe en entier. En particulier
`test_ordre_des_dependances_entre_applications` : si tu as été tenté d'importer
quoi que ce soit de `ressources` dans `organisation`, il te le dira — et c'est le
signal que tu as commencé US-SES-03 sans le vouloir.

## 11. Définition de fini

Implanté, testé, relu par le sous-agent, commité. Suite `pytest` complète verte.
Écran vérifié dans un navigateur, pas seulement par `assertContains`.
`DECISIONS.md` à jour le jour même (R19). `AVANCEMENT.md` corrigé sur D-54.
Case d'US-SES-02 cochée dans `docs/suivi/sprint-2.md`.

## 12. Ce que tu ne touches pas

Le backlog, le cahier des charges, le registre des risques, le diagramme de
classes de référence : réservés au chef de projet par `.claude/rules`. Écris
l'impact dans `DECISIONS.md`, ligne « Impact sur les livrables ».

Le modèle `Session` livré à US-SES-01, sauf pour y ajouter le `related_name` et
ce que la relation exige strictement.

US-SES-03 et US-SES-04, y compris « juste la clé étrangère » ou « juste le taux
d'occupation, c'est trois lignes ». C'est le raisonnement constant de D-23, D-30,
D-45 et D-54 : pas de code par anticipation d'un modèle ou d'un arbitrage non
tranché.

## 13. Ce que tu me rends

- Ta réponse au § 0.1, avec les deux options d'arbitrage et leurs conséquences.
  C'est le livrable le plus important de ce prompt après le code lui-même.
- Les entrées `DECISIONS.md` : unicité au sein de la session et son écart avec la
  note d'implémentation, lecture du critère 2 en postcondition, rendu permanent
  de RG-15, report du critère 5, correction d'AVANCEMENT sur D-54, et le cas
  échéant la correction du mécanisme d'avertissement.
- Le compte des tests ajoutés par groupe, et le total de la suite.
- Le temps réellement passé, à la demi-heure près. Deuxième mesure de la clé de
  conversion : avec US-SES-01, on commencera à savoir si 1,3 heure par point
  tient.