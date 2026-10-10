# Propositions pour le registre des risques — jalon J2

Prompt 43, § B4. Même principe que `RISQUES-PROPOSITIONS-C2.md` : ce
document **ne modifie pas** le registre — il propose seulement, le report
dans le registre reste au chef de projet.

## R10 — Diagramme d'états ETA-01, validation des cellules toujours en attente

| | Au 2 octobre (prompt 37) | Au 10 octobre (J2) |
|---|---|---|
| Probabilité | Retour demandé pour le 5 octobre, encore à venir | **Inchangée au mieux, plus probablement en hausse** — aucun retour des cellules n'est consigné dans `DECISIONS.md` ni `AVANCEMENT.md` à ce jour, cinq jours après l'échéance demandée |
| Impact | US-VAL-01/02 bloquées en attendant (prompt 34, § 7) | **En hausse** — US-VAL-01, 02 et 04 ont finalement été livrées sur les réponses par défaut aux quatre questions (D-165 à D-173), **et** US-PLAN-05, 06 et 09 sont construites par-dessus elles ; une réponse différente sur une seule des quatre questions (en particulier Q3, signature/affichage, qui touche spécifiquement US-VAL-04 selon la nuance déjà notée) referait désormais trois stories de plus que lors du dernier relevé |
| Criticité | Surveillée (`AVANCEMENT.md`, « Ce qu'il faut surveiller ») | **À revoir à la hausse** — la fenêtre pour corriger à moindre coût s'est refermée : le sprint 4 va construire encore par-dessus si rien n'est tranché |
| Mesure d'atténuation | Note aux cellules envoyée, retour attendu | **Proposée** : solliciter une réponse explicite avant toute story du sprint 4 qui dépend du circuit (toutes le font) ; à défaut de réponse, consigner le silence comme une validation tacite, datée, plutôt que de laisser la question ouverte indéfiniment |

## R23 — Mesure des heures réelles et de la vélocité

| | Au sprint 2 | Au sprint 3 (J2) |
|---|---|---|
| Probabilité | Heures jamais relevées, reconstituées après coup (biais à la hausse) | **Partiellement tenue** — `heures-sprint-3.md` existe, une heure de début réelle est désormais notée avant toute action pour chaque story depuis le prompt 41 (voir `LECONS-SPRINT-3.md`, leçon 5) ; les toutes premières stories du sprint (US-VAL-01 à 04, US-EVAL-04 partie 1) n'ont pas cette discipline |
| Impact | Vélocité et clé de conversion non mesurables | **Inchangé pour les heures humaines** — cette colonne n'a jamais été renseignée, sur onze stories ; **réduit pour les heures de session** — mesurables pour les cinq dernières stories du sprint (US-EVAL-01, 02, US-PLAN-05, 06, 09), permettant un calcul partiel (voir `REVUE-SPRINT-3.md`) |
| Criticité | Élevée | **Toujours élevée pour la clé de conversion elle-même** — aucune mesure fiable ne la justifie encore ; ne pas la réviser sur l'échantillon partiel de ce sprint (hétérogène, un seul point pèse 61 % du temps mesuré) |
| Mesure d'atténuation | `heures-sprint-3.md` ouvert dès le 30 septembre | **Proposée, nouvelle** : la colonne « heures humaines » dépend de l'étudiant, pas de l'outillage — ajouter un rappel explicite dans la définition de fini de CHAQUE story au sprint 4 (pas seulement « heure de début/fin de session », mais « heures humaines saisies le jour même »), faute de quoi elle restera vide comme ce sprint |

## Risque de capacité — Saturation des salles attitrées

**Inchangé depuis la proposition du 26 septembre**
(`RISQUES-PROPOSITIONS-C2.md`) : aucune story du sprint 3 ne touche aux
salles attitrées ni à leur ratio avec les brigades. La mesure
d'atténuation proposée alors (vérifier le ratio réel salles/brigades au
CIT avant le déploiement) n'a pas été engagée — hors périmètre de ce
sprint. Probabilité et impact restent à apprécier par le chef de projet ;
rien de nouveau à proposer.

## RISQUE NOUVEAU À PROPOSER — Ordre de verrouillage non déterministe du traitement en lot (US-PLAN-09)

**Constat du § A5 de ce prompt** (`docs/suivi/PROBLEMES.md`, P-42) : des
interblocages PostgreSQL intermittents sont apparus pendant la session du
prompt 42 ; la cause recherchée identifie que
`planification.services.indisponibilite.traiter_lot_remplacement` est le
seul chemin d'écriture du projet qui verrouille **plusieurs** programmes
hebdomadaires dans une même transaction, dans un ordre non garanti par
Django (`QuerySet.filter(pk__in=...)` sans `order_by` explicite). Chaque
autre chemin (génération, transitions du circuit, écriture individuelle
d'une séance) ne verrouille jamais qu'un seul programme par transaction.

- **Probabilité** : faible en usage normal (le lot cible une seule
  matière, rarement plusieurs programmes simultanément en pratique), mais
  réelle et non nulle — un défaut de conception, pas seulement un
  artefact d'environnement de test.
- **Impact** : un interblocage réel en production immobiliserait une
  transaction de traitement d'indisponibilité, avec retour utilisateur
  seulement (aucune perte de données : PostgreSQL annule une des deux
  transactions en conflit).
- **Mesure d'atténuation proposée** : trier les séances du lot par
  `programme_id` avant la boucle d'écriture (sprint 4) — correction
  simple et localisée, délibérément non appliquée aujourd'hui (§ A5 :
  « n'en corrige rien aujourd'hui »).

## RISQUE NOUVEAU À PROPOSER — Instabilité de la suite complète sous exécution prolongée

**Constat du § A5 de ce prompt.** Trois exécutions complètes de `pytest`
pendant ce prompt et le précédent ont chacune échoué différemment
(interblocages PostgreSQL une fois, un échec isolé sans rapport une autre
fois, dans des fichiers jamais touchés) ; non reproductible en isolant les
fichiers concernés, et la dernière exécution complète de ce prompt est
passée intégralement (deux fois, après correction des deux défauts
d'architecture trouvés par la première — voir le rendu final).

- **Probabilité** : à préciser par une mesure répétée (au moins cinq
  exécutions complètes consécutives) avant de conclure si c'est un
  artefact de cette session (machine partagée, exécutions très
  nombreuses et rapprochées) ou une fragilité réelle de l'environnement
  de test (Windows + Docker + PostgreSQL + psycopg3).
- **Impact** : si confirmé réel, un jury qui relance la suite complète
  pendant la soutenance pourrait observer un échec non reproductible,
  sans rapport avec le code présenté — risque de crédibilité, pas de
  correction.
- **Mesure d'atténuation proposée** : avant le dépôt, mesurer la
  fréquence réelle sur une machine dédiée et au repos (pas partagée avec
  d'autres processus comme pendant cette session) ; si confirmée, publier
  la procédure de contournement (relancer isolément) plutôt que de la
  laisser inexpliquée.
