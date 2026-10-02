# Leçons du sprint 2

Prompt 33, bloc H. Trois parties par leçon : ce qui s'est passé, ce qu'on en
retient, ce qu'on change.

## 1. Le dispositif de pilotage n'a pas tourné

**Ce qui s'est passé.** Deux jalons consécutifs, C1 (12 septembre) et C2
(26 septembre), atteints en contenu technique mais prononcés en retard ou pas
prononcés à l'heure — faute d'heures réelles relevées et de révision de la
clé de conversion. `AVANCEMENT.md` est resté à la date du 8 septembre
pendant tout le sprint 2, alors que le fichier lui-même existe précisément
pour donner une vue à jour.

**Ce qu'on en retient.** Ce n'est pas un oubli isolé : le mécanisme qui
aurait dû forcer la mise à jour n'existait pas. La clôture de sprint étant un
prompt séparé (comme celui-ci), rien ne relie l'achèvement d'une story à la
mise à jour du document consolidé — seul `sprint-2.md` (propre à chaque
story) était tenu à jour en continu.

**Ce qu'on change, concrètement, pour J2 (10 octobre).** Ajouter à la
définition de fini de CHAQUE story (pas seulement en fin de sprint) : cocher
la ligne dans `sprint-N.md` **et** ajouter la ligne correspondante au tableau
« Sprints » d'`AVANCEMENT.md` (story livrée, points, date) au moment même de
la clôture, pas en fin de sprint. Un relevé d'heures, même approximatif mais
CONTEMPORAIN (horodaté le jour même, pas reconstitué), à ajouter à ce même
geste — un fichier `docs/suivi/heures-sprint-N.md` ouvert dès le premier jour
du sprint, une ligne ajoutée à chaque clôture de story, jamais reconstitué
après coup. C'est la seule façon de rendre la clé de conversion mesurable un
jour.

## 2. Le défaut de déterminisme du générateur d'instances du solveur

**Ce qui s'est passé.** L'étude du risque R6 (Prompt 32) a construit une
matrice de mesures entière sur des instances synthétiques générées par un
processus enfant à chaque résolution. Une itération de `set` de chaînes,
dépendante de la graine de hachage Python (`PYTHONHASHSEED`, aléatoire par
défaut d'un processus à l'autre), faisait que l'instance mesurée pour le
régime SATISFACTION, ÉQUILIBRAGE et pour l'heuristique n'était PAS
rigoureusement la même — trois mesures censées être appariées ne l'étaient
pas. Repéré en vérifiant qu'un simple changement de formatage du code ne
changeait rien aux résultats : il en changeait.

**Ce qu'on en retient.** C'est la meilleure leçon du sprint — une matrice
entière avait failli être publiée, avec un GO en première version, sur des
mesures non appariées, sans qu'aucun test ne l'ait signalé. La cause n'était
pas un bogue de logique visible mais une propriété d'exécution invisible en
lecture de code (l'ordre d'itération d'un `set`).

**Ce qu'on change.** Toute génération synthétique comparée à travers
plusieurs processus porte désormais une empreinte vérifiable (SHA-256 du
contenu sérialisé, comparée entre processus, échec bruyant sinon) —
`Instance.empreinte()`, `etudes/solveur/solveur/instance.py`. Plus largement :
tout tri ou parcours d'une collection non ordonnée (`set`, `dict` avant
Python 3.7 — non applicable ici mais le principe reste) qui alimente une
mesure comparée doit être explicitement trié, jamais laissé à l'ordre
d'itération par défaut. À rédiger pour le mémoire — c'est un résultat de
méthode, pas seulement un correctif technique.

## 3. P-38 — troisième occurrence du motif « un critère de définition de fini jamais vraiment mesuré »

**Ce qui s'est passé.** US-PLAN-03 (§ 10) exigeait quatre mesures de
référence, dont le nombre de requêtes SQL. Le critère existait, un test
existait et l'affirmait conforme — mais la mesure sous-jacente
(« l'essentiel porté par l'écriture des séances, cohérent avec I3 ») n'avait
jamais été chiffrée précisément : `creer_seances` exécutait en réalité 6
requêtes par séance en boucle (1239 requêtes pour 200 séances), une
violation directe d'I3 (borné, indépendant du nombre de cases), découverte
seulement à la revue du Prompt 32, après la clôture d'US-PLAN-03. Corrigé le
jour même (P-38, `docs/suivi/PROBLEMES.md`) : `bulk_create`, 41 requêtes
constantes.

**Ce qu'on en retient.** Troisième occurrence du même motif dans ce projet :
un critère de définition de fini qui EXISTE et qui est FORMELLEMENT testé
peut rester faux si le test ne mesure pas la bonne dimension (ici : une
assertion qualitative — « cohérent avec I3 » — jamais chiffrée). Un test qui
affirme sans mesurer est un test qui ne protège rien.

**Ce qu'on change.** Pour tout critère non fonctionnel chiffrable (nombre de
requêtes, temps, mémoire), le test doit porter une assertion sur le CHIFFRE
lui-même (avec une marge nommée), jamais seulement sur une affirmation
qualitative dans un commentaire ou une docstring. `test_mesures_de_reference_
us_plan_03_paragraphe_10` le fait désormais.

**Erratum daté (2026-10-02, Prompt 37, Temps 1).** La dernière phrase
ci-dessus était inexacte au moment où elle a été écrite : jusqu'à cette date,
`test_mesures_de_reference_us_plan_03_paragraphe_10` capturait le nombre de
requêtes (`CaptureQueriesContext`) et le JOURNALISAIT (`_journaliser`), mais
ne l'ASSERTAIT jamais — la leçon affirmait un correctif qui n'avait pas
réellement été fait, quatrième occurrence du même motif qu'elle décrit.
Corrigé : l'assertion porte maintenant sur `REQUETES_REFERENCE_US_PLAN_03 =
43` et `MARGE_REQUETES = 2` (`app/planification/tests/
test_generation_performance.py`). Par le même constat, aucun test ne
comparait non plus le nombre de requêtes de `ServiceEcritureSeance.
creer_seances` entre deux volumes de séances écrites (la « pente nulle » de
P-38 elle-même) — ajouté au même moment : `test_p38_nombre_de_requetes_
independant_du_nombre_de_seances_ecrites` (`app/planification/tests/
test_ecriture.py`), vérifié capable d'échouer (réintroduction temporaire
d'une boucle par séance, 252 contre 1212 requêtes, puis retrait). Une
première version de ce test mesurait une égalité coïncidentale (deux
programmes partagés, deux effets de cache s'annulant) — corrigée par deux
programmes distincts et vierges, détectée par `relecteur-conception`
avant tout commit (`docs/suivi/PROBLEMES.md`, P-39).

## 4. L'inversion d'US-PLAN-03 et US-PLAN-04

**Ce qui s'est passé.** US-PLAN-04 (contraintes dures) a été développée
avant US-PLAN-03 (génération), alors que le backlog les présente dans l'ordre
inverse — CU-P5-02 (contrôle des contraintes) est un cas d'utilisation
INCLUS, appelé par CU-P5-01 (génération), qui l'inclut. Développer l'inclus
avant l'inclus rend l'inclus immédiatement testable en isolation, et la
génération qui l'appelle ensuite hérite d'un service déjà éprouvé plutôt que
d'un service à construire en même temps que son premier appelant.

**Ce qu'on en retient.** L'ordre du backlog reflète un ordre de valeur
métier (l'utilisateur voit d'abord « générer », pas « les règles qui
protègent la génération »), pas nécessairement le meilleur ordre de
construction technique. Les deux peuvent diverger sans que ce soit une
erreur de planification — juste une information que le backlog seul ne
porte pas.

**Ce qu'on change.** Rien d'obligatoire — cette inversion a été un choix
défendu et documenté (D-134), pas un accident. À garder en tête pour le
sprint 3 : quand une story inclut un cas d'utilisation qu'une autre story
appelle, envisager explicitement l'ordre de construction, pas seulement
l'ordre du backlog.

## 5. Trois principes d'arbitrage backlog contre livrables, à énoncer ensemble

**Ce qui s'est passé.** Seize écarts entre backlog, fiches de cas
d'utilisation, diagramme de classes et note d'implémentation ont été
tranchés pendant le sprint (`docs/suivi/ECARTS-LIVRABLES-SPRINT-2.md`), sans
qu'un principe unique les gouverne. En les relisant ensemble, trois principes
distincts ont en réalité été appliqués, chacun dans des cas différents : la
fiche la plus précise l'emporte sur un backlog plus vague (ex. écart #5,
CU-P3-06 contre le critère 1 — non, l'inverse ici, le critère l'emporte sur
la fiche) ; une règle structurante (RG-nn) l'emporte sur la formulation d'un
critère qui la contredit (ex. écart #8, § 5.4 du diagramme contre le critère
4 du backlog) ; une règle doit être exprimable sur le modèle réellement
implanté, pas sur un modèle que le livrable supposait (ex. écart #4,
l'unicité de désignation ne peut pas vivre au niveau du type de formation
sans interdire les sessions annuelles successives).

**Ce qu'on en retient.** Pris séparément, ces seize arbitrages ressemblent à
des décisions au cas par cas, potentiellement arbitraires vus de l'extérieur
(en soutenance, notamment). Énoncés ensemble comme trois principes
explicites, ils forment une méthode cohérente.

**Ce qu'on change.** Les trois principes sont maintenant formulés
explicitement ici, prêts pour le mémoire : (1) une fiche de cas
d'utilisation plus précise qu'un critère de backlog l'emporte ; (2) une
règle de gestion structurante l'emporte sur la formulation d'un critère qui
la contredirait ; (3) une règle doit rester exprimable sur le modèle
réellement implanté — si elle ne l'est plus après un arbitrage de modèle
antérieur, elle est reformulée, pas ignorée.

## 6. P-36, troisième occurrence — une recherche par motif qui ne trouve rien n'est pas une preuve d'absence

**Ce qui s'est passé.** Ce prompt lui-même en fournit un nouvel exemple :
deux reports de critères (D-91, D-83) existaient dans `DECISIONS.md` depuis
le 11 septembre, chacun disant explicitement « à ajouter au tableau de suivi
des reports » — jamais fait. Une simple recherche du texte de ces décisions
dans `AVANCEMENT.md` (ce que ce prompt aurait pu faire, plus vite) n'aurait
rien trouvé — pas parce qu'elles n'existent pas, mais parce que personne ne
les y avait recopiées. Seul un parcours complet de `DECISIONS.md`, décision
par décision, sur toute la plage du sprint, les a fait apparaître.

**Ce qu'on en retient.** C'est la troisième occurrence documentée de ce
motif (après P-26, P-32). La leçon générale (`.claude/rules/tests.md`,
« Vérifier une absence ») s'applique aussi hors du code : un document de
suivi qui ne mentionne pas quelque chose ne prouve pas que cette chose
n'existe pas ailleurs dans le dépôt.

**Ce qu'on change.** Pour toute clôture de sprint future, le bloc
« reports » ne doit jamais se contenter de mettre à jour les lignes déjà
connues du tableau : il doit reparcourir `DECISIONS.md` en entier sur la
plage du sprint, comme fait ici — c'est désormais la méthode attendue, pas
une vérification optionnelle.
