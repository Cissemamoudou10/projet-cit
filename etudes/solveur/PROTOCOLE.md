# Protocole de mesure — étude de faisabilité CP-SAT (R6)

**Figé le 2026-09-17, avant la première mesure.** Prompt 32 § 3 à § 8. Toute
correction ultérieure se fait par ajout daté, jamais par réécriture d'une
section déjà figée.

## § 3 — Les trois tailles

| Taille | Sessions | Brigades | Instructeurs | Modules | Salles ordinaires | Lieux partagés | Créneaux | Rôle |
|---|---|---|---|---|---|---|---|---|
| CONTRÔLE | 1 | 3 | proportionnel | proportionnel | proportionnel | proportionnel | 20 | vérifie que le modèle est correct, jamais qu'il passe à l'échelle |
| **RÉELLE** | 15 | 33 | 100 | 85 | 35 | 7 | 20 | **seule taille qui décide du go/no-go** — valeurs médianes de `HYPOTHESES.md` |
| HAUTE | 15 | 35 | 120 | 100 | 38 | 8 | 20 | bornes hautes des fourchettes relevées |

Pas de « taille double » : la marge de sécurité se prend sur le régime de
contrainte (§ 4), pas sur le volume.

## § 4 — Axes de sensibilité

Les instructeurs sont confortables en agrégé (570–700 cases pour 1 520–2 400
créneaux-instructeur, soit 25–45 % d'occupation) : ce n'est pas là que le
problème devient difficile. Deux axes mal connus décident, et sont donc
variés :

**Demande en lieux partagés** — proportion des séances exigeant un lieu
spécialisé ou extérieur : mesurée à **10 %, 15 %, 20 %, 25 %**. Repère : à
15 %, la demande atteint ≈100 créneaux pour 114–160 disponibles (70–85 %
d'occupation) ; à 25 %, la demande dépasse probablement la capacité —
INFAISABLE attendu, résultat exploitable en soi (temps jusqu'au constat
d'infaisabilité).

**Densité de qualification** — nombre moyen d'instructeurs qualifiés par
module : mesurée à **2, 4, 8**, chaque valeur croisée avec une fraction de
modules « rares » (un seul instructeur qualifié) à **5 % puis 15 %**.

Priorité si le temps manque : taille RÉELLE seule, sur les 4 valeurs de
demande en lieux × 3 densités de qualification = **12 combinaisons, 5
instances chacune** (60 instances). Le reste (CONTRÔLE, HAUTE, densités
croisées avec fractions rares) est du confort, mesuré si le temps le permet.

## § 5 — Le modèle

Base : `docs/suivi/CONTRAINTES-SOLVEUR.md` (six contraintes dures RG-34 à
RG-39, produit à US-PLAN-04). Lu en entier pour cette étude — cohérent avec
l'implantation `ServiceContraintes`, aucune correction nécessaire à ce stade.

**Formulation retenue** — décomposition booléenne avec contraintes de
liaison :
- une variable par couple (brigade, créneau, matière) ;
- une variable par (brigade, créneau, instructeur), restreinte aux
  instructeurs qualifiés (RG-35, restriction de domaine, pas une contrainte) ;
- une variable par (brigade, créneau, lieu), restreinte aux séances exigeant
  un lieu partagé (RG-37, sous-cas lieu partagé).

Ordre de grandeur attendu à la taille RÉELLE : 10 000 à 50 000 variables
booléennes. Le nombre réel sera rapporté avant le lancement de la matrice de
mesures (§ 11 du prompt) ; un dépassement net de cette fourchette signalerait
une formulation qui n'exploite pas les restrictions de domaine RG-35/RG-37,
et serait signalé avant de mesurer, pas après.

**Simplifications déclarées** (effet probable sur les mesures) :
- pas de regroupement de brigades (US-PLAN-06, sprint 3) — chaque brigade
  occupe sa propre case même quand un regroupement réel l'aurait libérée ;
  tend à SURESTIMER la demande en lieux partagés et en instructeurs par
  rapport au système réel une fois US-PLAN-06 livrée ;
- prérequis traités par pré-filtrage des matières programmables (comme
  l'heuristique), pas par contrainte de précédence RG-39(b) — cohérent avec
  ce que fait `app/planification` aujourd'hui, mais ne mesure pas le coût
  d'une précédence modélisée dans le solveur ;
- une séance par créneau, jamais de fusion, comme à US-PLAN-03 — aucune
  variable de fusion temporelle, cohérent avec la portée actuelle du système.

**Ajout du 2026-09-18, avant tout code — deux simplifications supplémentaires,
nécessaires pour construire le modèle, non listées par le prompt initial :**
- **RG-36 (indisponibilités d'instructeurs) non modélisée** : les instances
  synthétiques n'en génèrent aucune — § 2 la classe « non encore relevé »,
  hors des deux axes de sensibilité retenus au § 4 ; l'ajouter mesurerait un
  troisième axe non demandé sans rien enseigner sur les deux qui comptent ;
- **RG-38 (créneau ouvert / périodes bloquantes) non modélisée** : aucune
  période bloquante dans les instances synthétiques, même motif ;
- **RG-37, sous-cas salle attitrée, non contraignant par construction** :
  le générateur attribue à chaque brigade une salle attitrée de capacité
  toujours suffisante — cohérent avec RG-37 (« aucune variable de solveur »
  pour ce sous-cas, un préfiltre hors modèle), mais qui ne peut donc jamais,
  dans ce prototype, produire le refus que l'observation de terrain de
  `HYPOTHESES.md` (32 à 38 salles pour 30 à 35 brigades) signale comme réel.

**Effet combiné sur la lecture des résultats** : ces trois simplifications
retirent des sources de contrainte que le système réel connaît. Le prototype
mesure donc un problème AU MOINS AUSSI FACILE que le problème réel — un
GO ne se généralise pas automatiquement (le système réel pourrait être plus
dur), un NO-GO ou un INFAISABLE, en revanche, tient a fortiori (le système
réel ne peut être plus facile). À rappeler explicitement dans
`RECOMMANDATION.md`.

**Trois régimes, mesurés séparément :**
1. **SATISFACTION** — une solution admissible, sans objectif.
2. **REMPLISSAGE** — maximiser le nombre de cases pourvues.
3. **ÉQUILIBRAGE** — remplissage puis minimisation de l'écart de charge entre
   instructeurs. Seul régime qui justifierait réellement le solveur face à
   l'heuristique : à 25–45 % d'occupation agrégée, trouver UNE solution n'est
   pas l'enjeu, bien répartir l'est.

**Instabilité `ortools` constatée et contournée, 2026-09-18 — à consigner
pour l'analyse coût/bénéfice (§ 8/`RECOMMANDATION.md`).** Le régime
ÉQUILIBRAGE provoquait un `Segmentation fault` natif reproductible, sous
Windows (venv local) ET sous Linux (conteneur `python:3.14.4-slim-bookworm`,
la plateforme cible), à chaque appel à `CpSolver.Solve()`. Deux causes
distinctes isolées par diagnostic direct (inspection de `CpModelProto` en
Python, en évitant le formateur natif qui crashait à la place de rapporter
l'erreur) :
1. `AddMaxEquality`/`AddMinEquality` — écartées par précaution (remplacées
   par une linéarisation `>=`/`<=` standard), sans que leur responsabilité
   ait pu être confirmée isolément.
2. **Cause confirmée** : relire `IntVar.Proto()` sur des variables déjà
   créées PUIS continuer à ajouter des variables au modèle corrompt en
   mémoire les variables relues plus tôt (domaine vidé, nom illisible) —
   reproduit et éliminé en calculant la borne de charge une fois, à la
   création (`_creer_charge`), plutôt qu'en la relisant depuis le modèle en
   cours de construction (`modele.py`, `VariablesModele.borne_charge`).

**Portée du constat** : narrow — un seul patron d'usage (relire `.Proto()`
en cours de construction) déclenche le bogue ; aucun autre endroit du
modèle ne le fait. Mais c'est un bogue MÉMOIRE, pas une erreur de
validation propre : la roue `ortools-9.15.6755` pour `cp314-manylinux` sur
cette plateforme n'est donc pas exempte de défauts natifs. À peser dans le
coût de la dépendance (§ 1/D-160) : au-delà du poids en mégaoctets, un
paquet compilé récent sur une version de Python elle-même très récente
(3.14, sortie il y a quelques mois) porte un risque de maturité, distinct
du risque de poids.

## § 6 — Comparaison avec l'heuristique

Un générateur d'instances (`etudes/solveur/`) produit une description JSON
neutre d'un problème complet, paramétrée par § 3/§ 4, graine aléatoire fixée
et consignée avec chaque instance. Le modèle CP-SAT et une réimplantation
courte de l'heuristique de `app/planification` lisent la même instance.

Limite déclarée : la réimplantation peut diverger de celle de l'application ;
la comparaison porte sur les APPROCHES, pas sur les implantations.

**Contrôle de réalité — mesuré le 2026-09-18, report refermé.** Le prompt
s'appuyait sur « les quatre mesures relevées à US-PLAN-03 § 10 », listées
`reportées` à la clôture de la story (`prompt 31.md` § 13, ligne 450, aucune
fermeture trouvée dans `DECISIONS.md`/`PROBLEMES.md`). Prises maintenant, sur
un jeu représentatif conforme au § 10 (trois sessions, dix brigades, semaine
complète — `app/planification/tests/test_generation_performance.py`,
`test_mesures_de_reference_us_plan_03_paragraphe_10`) :

| Mesure | Valeur |
|---|---|
| Temps total de génération | 0,616 s |
| Requêtes SQL | 1 239 |
| Appels à `ServiceContraintes.verifier` | 360 |
| Taux de remplissage | 100,0 % (200/200 cases) |

Remplissage à 100 % : ce jeu de dix brigades est généreusement qualifié
(2 instructeurs par matière, RG-35 jamais serré) — délibéré, ce test mesure
la ligne de base du système actuel, pas un cas limite. La comparaison au § 6
avec la réimplantation heuristique du prototype se fait donc sur un ordre de
grandeur (temps par case, requêtes par séance écrite), pas sur un taux de
remplissage identique — attendu puisque la matrice de sensibilité du
prototype (§ 4) vise délibérément des combinaisons plus tendues (jusqu'à
25 % de demande en lieux partagés, densité de qualification à 2).
`DECISIONS.md`, D-161.

Cinq instances par combinaison.

## § 7 — Seuils de décision (figés)

**GO** — le solveur est retenu si, à la taille RÉELLE, dans le PIRE CAS des
instances testées, pour les combinaisons de sensibilité où le problème est
faisable :
- première solution admissible en moins de 30 s ;
- taux de remplissage à 5 min ≥ celui de l'heuristique ;
- régime ÉQUILIBRAGE : écart de charge entre instructeurs significativement
  meilleur que l'heuristique ;
- la roue `ortools` est installable hors ligne sur la plateforme cible
  (**vérifié le 2026-09-17, voir § 1 du prompt — GO sur ce point précis**).

**NO-GO** — l'heuristique reste la réponse définitive si, à la taille
RÉELLE :
- aucune solution admissible en 300 s sur une combinaison faisable ;
- taux de remplissage < heuristique ;
- empaquetage hors ligne impossible (déjà écarté, voir ci-dessus).

**GO CONDITIONNEL** — cas intermédiaire : solveur retenu comme option,
heuristique par défaut, bascule par `GENERATION_STRATEGIE` (posé à
US-PLAN-03).

**Facteur de prudence — machine de mesure non représentative du serveur
cible.** Mesures conduites dans un conteneur `python:3.14.4-slim-bookworm`
(l'image exacte de `Dockerfile`) sur poste de développement : Intel Core
Ultra 7 165H, 16 cœurs physiques / 22 fils, 16 Go de mémoire alloués au
conteneur (31,4 Go sur l'hôte). Les caractéristiques du serveur cible du CIT
ne sont pas connues — question de terrain ouverte, hors de portée de cette
étude. Un serveur de salle serveur militaire est raisonnablement supposé
moins véloce qu'un poste de développement mobile récent. **Facteur de
prudence retenu : ×3 sur les deux seuils de temps du § 7** — 30 s devient
90 s pour le GO, 300 s devient 900 s pour le NO-GO. Ce facteur est une
hypothèse, pas une mesure ; si les temps observés sont proches de ces seuils
ajustés, la conclusion devra être qualifiée de fragile plutôt que tranchée.

## § 8 — Mesures rapportées

Pour chaque combinaison, chaque régime, chaque instance :
temps jusqu'à première solution admissible · temps jusqu'à preuve
d'optimalité ou dépassement de borne · statut (optimal / admissible /
INFAISABLE / indéterminé) · taux de remplissage · écart d'optimalité restant
à 5 min · écart de charge entre instructeurs (régime ÉQUILIBRAGE) · mémoire
maximale. Pour l'heuristique, sur les mêmes instances : temps total, taux de
remplissage, écart de charge.

Rapporté : MÉDIANE et PIRE CAS des 5 instances.

**Machine de mesure** : conteneur Docker `python:3.14.4-slim-bookworm`
(image de production), hôte Intel Core Ultra 7 165H, 16 cœurs / 22 fils,
mémoire plafonnée à 16 Go côté conteneur. Non représentative du serveur
cible (inconnu) — facteur de prudence ×3 appliqué ci-dessus.
