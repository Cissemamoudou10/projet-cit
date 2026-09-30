# Heures réelles du sprint 2 et clé de conversion

Prompt 33, bloc A. **À lire avant le tableau : ce relevé est intégralement une
RECONSTITUTION, pas une mesure.** Aucune heure n'a été pointée en temps réel
pendant le sprint 2 — le même défaut que le sprint 1 (voir
`docs/suivi/AVANCEMENT.md`, indicateur « Vélocité mesurée : non mesurée »).
La seule donnée disponible est l'horodatage des commits Git, dont la
granularité elle-même est grossière : contrairement au sprint 1 (des commits
français, atomiques, un par sous-tâche — voir le journal du 8 septembre), le
sprint 2 a été committé en gros blocs « feat: Implement X », un par story
environ. La méthode ci-dessous — écart entre le commit qui clôt une story et
celui qui clôt la précédente — est **celle que le prompt lui-même qualifie de
« la moins fausse »**, pas une mesure fiable. Elle **surestime fortement** :
l'écart calendaire entre deux commits inclut les nuits, les repas, les autres
activités et tout travail non committé aussitôt — rien ne le distingue du
temps réellement passé sur la story suivante.

**Correction sur une citation du prompt** : le Prompt 33 attribue la clé
provisoire de 1,3 h/point à D-33. Vérifié : D-33 (`docs/suivi/DECISIONS.md`)
porte sur `VOLUME_HORAIRE_HEBDOMADAIRE_REFERENCE` et le seuil d'écart de
référentiel — un paramètre métier sans rapport. Le chiffre 1,3 h/point
n'existe que dans `docs/suivi/AVANCEMENT.md` (tableau « Indicateurs »),
**sans entrée `DECISIONS.md` qui en explique l'origine ou la justifie** —
lui-même un symptôme du même défaut de traçabilité que ce bloc documente.

## Tableau — une ligne par story, plus l'étude du solveur

Repère de méthode : l'horodatage retenu pour une story est celui du commit qui
la clôt ; la durée est l'écart avec le commit précédent (dernière story
close, ou clôture du sprint 1 pour la première ligne). Aucune ligne n'est un
relevé contemporain.

| Story | Points | Heures relevées | Heures par point | Source du relevé |
|---|---|---|---|---|
| US-SES-01 — Ouvrir une session | 5 | 22,1 h | 4,42 | Reconstitution — écart entre `f97b97d` (clôture sprint 1, 08/09 22:03) et `d6a8e97`/`c2cd2f5` (09/09 20:09–20:19) |
| US-SES-02 — Constituer les brigades | 5 | 43,1 h | 8,63 | Reconstitution — écart jusqu'à `0466890` (11/09 15:27). Span de 43 h suspect : couvre très probablement une interruption non liée à la story (autre activité, ou travail non committé avant le 11) |
| US-SES-03 — Salle attitrée | 3 | 1,7 h | 0,57 | Reconstitution — écart jusqu'à `13d8c6f` (11/09 17:09) |
| US-SES-04 — Consulter la composition | 3 | *non isolable* | *non isolable* | **Aucun commit dédié.** Story « largement pré-livrée » par US-SES-01/02/03 (le prompt le dit lui-même) — son temps, s'il existe, est noyé dans la ligne suivante |
| US-SES-05 — Enregistrer les stagiaires | 5 | 14,9 h (bloc commun avec US-SES-04) | 2,98 (si tout attribué à 05 seule) | Reconstitution — écart jusqu'à `50b7bdb` (12/09 08:01), qui porte le message « add Prompt 25 » mais contient en réalité l'implantation de l'import (`organisation/forms.py`, réglage `openpyxl`) : le nom des commits sprint 2 décrit la CRÉATION du prompt suivant, pas la story livrée dans le même commit — piège de lecture, signalé en leçon (bloc H) |
| US-SES-06 — Affecter aux brigades | 5 | 2,6 h | 0,53 | Reconstitution — écart jusqu'à `805d444` (12/09 10:39) |
| US-SES-07 — Consulter la liste | 3 | 1,9 h | 0,63 | Reconstitution — écart jusqu'à `78fae57` (12/09 12:33). Écart court, cohérent avec une story pré-livrée n'exigeant qu'un complément (export) |
| US-INS-03 — Indisponibilités | 3 | 2,0 h | 0,68 | Reconstitution — écart jusqu'à `7ebe7bc` (12/09 14:35) |
| US-PLAN-01 — Calendrier annuel | 8 | 11,4 h | 1,43 | Reconstitution — écart jusqu'à `5739e31` (13/09 01:59) |
| US-PLAN-12 — Grilles horaires | 5 | 45,8 h | 9,16 | Reconstitution — écart jusqu'à `d004ab1` (14/09 23:46). Span de 45 h : très probablement une coupure de plus d'une journée, sans rapport avec l'effort réel de la story |
| US-PLAN-04 — Contraintes dures | 8 | 37,4 h | 4,68 | Reconstitution — écart jusqu'à `9fa38fb` (16/09 13:11). **Absorbe une partie du travail de conception d'US-PLAN-03** (les modèles RG-34/35/37 du paquetage P5, voir D-134) : ce chiffre est surestimé pour US-PLAN-04 seule et sous-estimé pour US-PLAN-03 |
| US-PLAN-03 — Génération du programme | 8 | 9,1 h | 1,13 | Reconstitution — écart jusqu'à `25d597c` (16/09 22:15). Anormalement bas pour une story de 8 points : confirme le déplacement de charge vers US-PLAN-04 ci-dessus — les deux lignes ne doivent pas être lues séparément |
| **Étude du solveur (Prompt 32)** | **0 — hors points** | **64,98 h** | *sans objet, aucun point* | Reconstitution — trois segments (`25d597c`→`6d420e5` 23,4 h, `6d420e5`→`e249fea` 26,1 h, `e249fea`→`fd13947` 15,5 h). Sous-estime très probablement : les trois révisions successives de la matrice de mesures (v1 invalidée, v2 non appariée, v3 retenue) et la relecture décrite dans `DECISIONS.md` D-162 représentent un travail itératif difficile à réduire à trois horodatages de commit |

**Total stories (hors étude solveur) : 192,0 h relevées (reconstituées) pour 61 points.**

## Clé mesurée sur le sprint 2

**192,0 h ÷ 61 points = 3,15 h/point**, brut, sur la méthode ci-dessus.

## Clé recalculée en excluant US-SES-04 et US-SES-07, et en regroupant US-PLAN-03/04

- Points : 61 − 3 (US-SES-04) − 3 (US-SES-07) = **55 points**.
- Heures : 192,0 − 1,9 (US-SES-07, seule ligne isolable des deux exclusions —
  US-SES-04 n'a jamais eu de ligne propre à soustraire) = **190,1 h**.
- **190,1 ÷ 55 = 3,46 h/point.**

**Ce que ce recalcul change : presque rien (3,15 → 3,46), et c'est en soi le
résultat.** Retirer deux stories pré-livrées ne fait quasiment pas bouger la
clé, alors que ça devrait la faire baisser sensiblement si la méthode captait
un effort réel : la preuve que la clé brute est dominée par du bruit
calendaire (nuits, coupures), pas par l'effort des stories. Regrouper
US-PLAN-03/04 (37,4 + 9,1 = 46,5 h pour 16 points, soit 2,91 h/point sur le
couple) est plus défendable individuellement que les deux lignes séparées,
mais reste construit sur la même méthode fragile.

## Comparaison à la clé provisoire de 1,3 h/point

**Sans rapport direct** : les deux clés reconstituées (3,15 et 3,46 h/point)
sont 2,4 à 2,7 fois plus élevées que la clé provisoire de 1,3 h/point. Mais
rien n'indique que 1,3 était fausse — l'écart le plus probable vient de la
méthode de reconstitution elle-même (calendaire, pas travaillée), pas d'une
révision réelle du rythme de production. **Comparer les deux revient à
comparer une mesure et une non-mesure : la comparaison elle-même n'est pas
significative.**

## Projection sur les 108 points restants (sprints 3 et 4)

| Clé utilisée | Total | À combien de jours ouvrés | Fiabilité |
|---|---|---|---|
| 1,3 h/point (provisoire, inchangée) | 140,4 h | dépend de la disponibilité quotidienne réelle, non documentée dans les fichiers de suivi — à préciser par le chef de projet | Non révisée par ce prompt : rien de mesuré ne justifie de la changer |
| 3,15 h/point (reconstitution brute) | 340,2 h | idem | Bornée par une méthode connue pour surestimer — **borne haute, pas une estimation centrale** |

Aucune conversion en jours ouvrés n'est produite ici : `AVANCEMENT.md` ne
documente nulle part une disponibilité quotidienne de référence (heures par
jour ouvré) — seule une marge de 14 jours ouvrés avant dépôt est connue. Sans
ce chiffre, convertir des heures en jours ajouterait une précision inventée à
une donnée déjà reconstituée.

## Recommandation

**Ne pas réviser la clé de conversion sur la base de ce relevé.** Ni 1,3
h/point ni 3,15-3,46 h/point ne reposent sur une mesure fiable — la première
n'a jamais été justifiée dans `DECISIONS.md`, la seconde est structurellement
biaisée à la hausse par la méthode. La vraie action pour J2 (10 octobre) est
en bloc H : un mécanisme de relevé contemporain, pas une nouvelle clé
calculée sur des données aussi peu fiables que celles qui ont produit la
précédente. Si le chef de projet doit retenir un chiffre pour planifier les
sprints 3-4 dans l'immédiat, retenir 1,3 h/point comme hypothèse de travail
**non validée**, avec un premier recontrôle dès que 5 à 6 stories du sprint 3
auront un relevé contemporain réel.
