# Leçons du sprint 3

Prompt 43, § B3. Même gabarit que `LECONS-SPRINT-2.md` : trois parties par
leçon — ce qui s'est passé, ce qu'on en retient, ce qu'on change.

## 1. La garde à la porte unique a tenu face au premier appelant étranger

**Ce qui s'est passé.** US-EVAL-01 a ouvert le premier appel à la porte
unique (`ServiceEcritureSeance`) depuis une application **autre** que
`planification` — `inserer_seance_de_controle`, appelée par `evaluations`
pour insérer la séance d'un contrôle (D-177). C'était la première mise à
l'épreuve réelle de l'affirmation « un seul chemin écrit `Seance`/
`LigneProgramme` » face à un appelant qui n'avait jamais été anticipé au
moment où la garde mécanique (`tests/architecture/test_couches.py::
test_seule_la_porte_d_ecriture_instancie_seance_ou_ligne_programme`) a été
écrite.

**Ce qu'on en retient.** Le test d'architecture a tenu sans aucune
modification : il scanne tout le projet par AST, pas une liste d'exceptions
tenue à la main, donc un appelant venu d'une application qu'on n'avait pas
en tête au moment d'écrire le test n'ouvre aucun angle mort. C'est
exactement la leçon du sprint 1 (36 refus d'habilitation manquants,
`.claude/rules/tests.md`) appliquée une seconde fois, avec succès cette
fois : une garde mécanique généralisable bat une liste d'exceptions.

**Ce qu'on change.** Rien à corriger ; à consigner comme un résultat de
méthode pour le mémoire — la garde par balayage AST plutôt que par
énumération des appelants connus est le patron à répéter pour toute future
porte unique (US-PLAN-09 l'a d'ailleurs réutilisé tel quel pour le lot).

## 2. Des tests qui passaient pour une mauvaise raison, démasqués seulement par un témoin

**Ce qui s'est passé.** Deux occurrences distinctes. P-38 (Temps 1, prompt
37) : le nombre de requêtes de l'écriture d'un programme généré n'était
comparé nulle part entre deux tailles de lot — une boucle par séance
réintroduite puis retirée l'a confirmé capable de faire échouer le test une
fois ajouté (252 contre 1212 requêtes), preuve que son absence était un
vrai trou, pas une précaution superflue. US-EVAL-04 (test D3, génération
avec épreuve organisée) : la première version comparait une génération
AVEC épreuve à elle-même, sans témoin SANS épreuve — une case qui échoue à
la présélection par coïncidence (aucune séance dans ce lieu, pour une autre
raison que l'épreuve) aurait fait passer le test sans que la règle RG-37
soit réellement exercée.

**Ce qu'on en retient.** Un test qui compare un scénario à une attente fixe
peut passer sans que le MÉCANISME attendu soit celui qui produit le
résultat — la coïncidence imite la règle. Ce n'est démasqué qu'en comparant
le scénario à un TÉMOIN qui ne devrait PAS déclencher la règle (même jeu de
données, un paramètre en moins). US-PLAN-09 (prompt 42) a repris ce patron
sans le nommer : `test_lot_avec_une_seance_en_conflit_rien_n_est_ecrit`
prouve l'atomicité en vérifiant que la PREMIÈRE séance du lot, déjà
acceptée avant l'échec de la seconde, n'a PAS été écrite non plus — sans ce
témoin, un lot à une seule séance en échec aurait aussi bien pu passer par
chance.

**Ce qu'on change.** Pour toute règle dont le test vérifie un refus ou un
effet de bord (atomicité, exclusion, requêtes constantes), exiger un
témoin — le même scénario, UN paramètre retiré — dans la définition de fini
de la story, pas seulement pour les contraintes dures déjà couvertes par
`ServiceContraintes`.

## 3. Les erreurs de citation de décisions, et leur cause commune

**Ce qui s'est passé.** Plusieurs occurrences pendant le sprint : D-190
citait la mauvaise décision (corrigé en relecture, US-EVAL-02) ; D-205
s'est corrigée elle-même en cours de sprint (« fausse sur ce point ») ;
trois lignes du tableau des reports d'`AVANCEMENT.md` (D-39 volet saisie
manuelle, D-121 E2 et A3, D-181) étaient fermées depuis plusieurs jours,
parfois depuis un prompt antérieur, sans que la ligne ne soit jamais
corrigée — découvert seulement en reparcourant `DECISIONS.md` en entier
pour ce prompt (§ B1), pas par une relecture ciblée. Un saut de
numérotation (D-252, jamais utilisé) s'est aussi glissé sans qu'aucune
relecture ne le remarque, puisqu'un saut ne casse rien à l'exécution.

**Ce qu'on en retient.** La cause est la même dans tous les cas : un numéro
ou un statut écrit une fois n'est plus jamais revérifié contre la source
au fil du temps qui passe, pendant que le code, lui, continue d'avancer.
C'est précisément pourquoi la règle « aucun numéro de décision cité de
mémoire » existe dans les prompts — mais elle protège contre la citation
d'un numéro inventé, pas contre un numéro correct dont le STATUT a changé
depuis. Une table de suivi qui n'est mise à jour qu'à la fermeture d'un
report, jamais revérifiée à l'ouverture du suivant, dérive silencieusement.

**Ce qu'on change.** Le recompte de fin de sprint ne doit plus continuer
une chaîne de recomptes locaux sans revérifier sa propre base de départ
contre `DECISIONS.md` — ce que ce prompt a fait une fois (§ B1) devrait
devenir systématique à chaque clôture de sprint, pas seulement à J2/C-n.

## 4. La séparation moteur / écrans du circuit a tenu trois fois, failli la quatrième

**Ce qui s'est passé.** `ServiceCircuitProgramme` (le moteur, une table
`TRANSITIONS` unique) et `circuit_affichage.py` (l'écran, qui ne fait que
consulter `motif_refus_action`/`LIBELLES_ACTIONS`, jamais recoder une
condition d'état) ont servi sans incident aux quatre écrans d'US-VAL-01 à
04. US-PLAN-09 (partie 3, prompt 42) a néanmoins réécrit une table locale
de messages d'état (`MESSAGE_BLOCAGE`) en paraphrasant ce que le moteur
rendait déjà — confirmé par la relecture, qui a aussi relevé que la
décision consignée affirmait à tort que le moteur était déjà réutilisé.

**Ce qu'on en retient.** Le patron lui-même n'est pas en cause : une fois
pointé vers `motif_refus_action`, le correctif a tenu en quelques lignes.
Le risque n'est pas architectural, il est humain — sous la pression d'un
écran à livrer, il est plus rapide d'écrire trois lignes de dictionnaire
que de relire `circuit.py` pour trouver la fonction qui fait déjà le
travail, et rien dans le processus n'oblige à chercher avant d'écrire.

**Ce qu'on change.** Ajouter à la définition de fini de tout écran qui
affiche un refus d'état : chercher explicitement une fonction existante du
moteur concerné avant d'écrire un message — et le dire dans la décision
consignée, pour que la relecture puisse vérifier l'affirmation plutôt que
la supposer.

## 5. La mesure de R23 (heures contemporaines) : ce qui a tenu, ce qui n'a pas tenu

**Ce qui s'est passé.** `heures-sprint-3.md`, ouvert dès le 30 septembre
(leçon 1 du sprint 2), porte une ligne par story. Ce qui a tenu : à partir
d'US-PLAN-05 (prompt 41) et pour toutes les stories suivantes du sprint
(US-PLAN-05 fin, 06, 09, cette clôture), l'heure de début est écrite avant
toute autre action, comme l'exige chaque prompt depuis — aucune ligne
récente n'est reconstituée après coup. Ce qui n'a pas tenu : plusieurs
lignes antérieures (US-VAL-01 à 04, US-EVAL-04 partie 1) portent « non
relevée au moment » ou « non notée au moment » — la discipline n'était pas
encore systématique en milieu de sprint. Et sur la totalité du sprint, la
colonne « heures humaines » n'a **jamais** été renseignée : elle reste
partout « à saisir le jour même par l'étudiant ».

**Ce qu'on en retient.** Le mécanisme (un fichier, une ligne par story,
une règle écrite dans le prompt) a fini par s'imposer, mais seulement une
fois répété dans plusieurs prompts consécutifs — la leçon 1 du sprint 2
avait posé le fichier, il a fallu l'exiger de nouveau à plusieurs reprises
pour qu'il soit suivi sans faille. L'absence totale d'heures humaines,
elle, n'a pas de mécanisme correctif en place : rien dans le déroulé ne
force l'étudiant à les saisir, contrairement à l'heure de début/fin
technique que CLAUDE.md impose avant toute action.

**Ce qu'on change.** Rien à corriger dans l'outillage technique — le
fichier fonctionne. La vélocité de ce sprint se calcule donc en **heures de
session**, jamais en heures humaines (absentes), et la clé de conversion
(1,3 h/point) **n'est pas révisée** : aucune mesure fiable ne le justifie,
exactement la même conclusion qu'au sprint 2 — voir `REVUE-SPRINT-3.md`.
