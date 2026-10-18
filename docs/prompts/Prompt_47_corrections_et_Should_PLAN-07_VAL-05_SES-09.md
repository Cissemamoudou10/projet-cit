# Prompt 47 — Sprint 4 : deux corrections, puis US-PLAN-07, US-VAL-05, US-SES-09

Phase 5, sprint 4. Le périmètre Must est livré. Ce prompt ouvre les stories
**Should** : 11 points, trois commits de story au moins, **un seul rendu à la
fin**. Point de décision du **mercredi 21 octobre au soir** : toute story Should
non commencée à cette date passe en réserve.

Règles inchangées : arrêt sur les seules conditions écrites ici ; pour le reste,
tu tranches selon les trois principes d'arbitrage, tu consignes, tu continues ;
aucun numéro de décision cité de mémoire ; heure de début écrite avant toute
autre action ; auteur des décisions = porteur inscrit dans `sprint-4.md`.

---

## Temps 1 — Deux corrections du prompt 46, et une mise à disposition

### 1.1 D-273 est à revoir : RG-59 bis existe bien

D-273 qualifie d'erronée la citation de RG-59 bis au point M5 du prompt 46.
Or le dossier des cas d'utilisation **v4** (§ 9.8, fiche CU-P6-07) porte bien
RG-59 bis : « un seul procès-verbal par fin de formation […] Le système énumère
alors les manquants **par module et par brigade** ». C'est exactement la source
de M5.

1. Vérifie dans `docs/conception/` la version des cas d'utilisation présente
   dans le dépôt. Si elle est antérieure à la v4, c'est elle qui manque RG-59
   bis — et c'est un écart à signaler : le dépôt porte une version périmée d'un
   livrable de conception.
2. Révise D-273 en conséquence, sans la supprimer : nouvelle décision qui la
   corrige, et rétablis la citation de RG-59 bis là où elle a été remplacée.

### 1.2 Le procès-verbal d'une évaluation rapporte l'évaluation, pas le module

Le choix fait seul (« le PV d'une évaluation rapporte la note du module, et le
seuil s'y applique ») est à corriger. CU-P6-07 A1 : « le document **ne porte que
sur une évaluation** ». La note du module agrège d'autres évaluations qui ne
sont pas l'objet de ce document.

- Le procès-verbal d'une évaluation présente, pour chaque stagiaire du
  périmètre, **la note de cette évaluation** (sur sa note maximale, et ramenée
  sur 20), l'absence le cas échéant, et le rang sur cette évaluation (même
  règle d'égalité, D-271).
- **Aucune décision admis/ajourné** : la décision sanctionne la formation
  (BF-EVAL-07, « document officiel de sanction de la formation ») et n'existe
  qu'au procès-verbal de fin de formation.
- Tests corrigés en conséquence, `pytest -m pdf` dans le conteneur.
- Nouvelle décision qui remplace l'arbitrage pris seul ; mention dans le rendu.

### 1.3 Les PDF doivent être vus par un humain

Aucun PDF n'a encore été ouvert dans un lecteur. Avec le jeu de démonstration,
produis dans le conteneur **un exemplaire de chacun des trois documents** —
progression réalisée, procès-verbal d'une évaluation, procès-verbal de fin de
formation — et dépose-les dans `docs/demonstration/exemplaires/` (noms
inventés uniquement ; vérifie-le avant de les déposer). L'étudiant les relira
lui-même.

### 1.4 L'audit du diagramme de classes

Les trois écarts trouvés (`Qualification.dateAcquisition`, `Lieu.code`,
association « chef de module ») ne s'implantent pas ici. Porte-les au registre
des écarts, chacun avec son sort : le chef de module relève d'US-SES-08
(réserve) ; les deux attributs ne sont exigés par aucune story — le diagramme
de classes sera annoté au passage documentaire d'après sprint, pas le code
alourdi.

Commit : `fix(evaluations): PV d'évaluation, RG-59 bis, exemplaires PDF`.

---

## Temps 2 — US-PLAN-07 : Signaler les écarts de volume horaire

3 points · Should · BF-PLAN-07.

**Critères (backlog v10)** : pour chaque matière, volume prescrit et volume
programmé cumulé affichés ; écart au-delà d'un seuil paramétrable signalé ;
sous- et sur-programmation distinguées ; indicateur consultable avant la
soumission du programme.

**Arbitrages**
- **E1 — Aucun calcul nouveau.** Le programmé et le prescrit sont ceux
  d'US-SUI-01 ; réutilise ses fonctions. Un test d'architecture le vérifie.
- **E2 — Où.** Sur la consultation de la semaine, avant soumission : par
  brigade, les matières dont l'écart dépasse le seuil, avec le sens. Et sur
  le rapprochement d'US-SUI-01, la même mise en évidence.
- **E3 — Seuil.** Paramètre BNF-13 distinct de celui du référentiel, en
  pourcentage du prescrit, 10 % par défaut. Sur-programmation : programmé
  supérieur au prescrit au-delà du seuil. Sous-programmation : mesurée à la
  fin de la session seulement, sinon toute matière en cours paraîtrait en
  retard — avant la fin, la matière est signalée « en cours » et non en écart.
  Consigne cet arbitrage : il est nécessaire, aucun livrable ne le tranche.
- **E4 — Habilitations.** Lecture pour les profils qui lisent le programme.

**Tests** : sur- et sous-programmation, seuil modifié par paramètre, matière en
cours non signalée avant la fin de session, requêtes constantes avec 2 et 10
brigades, HTTP.

Commit : `feat(planification): US-PLAN-07 écarts de volume horaire`.

---

## Temps 3 — US-VAL-05 : Consulter les programmes et l'historique des validations

5 points · Should · BF-VAL-05, BF-VAL-03.

**Critères (backlog v10)** : liste des programmes de toutes les semaines avec
leur état, filtrable par état et par période, donnant accès à chacun ;
chaque changement d'état présenté avec auteur, date et motif ; historique
consultable depuis le programme ; cycles de rejet et de resoumission dans
l'ordre chronologique.

**Arbitrages**
- **H1 — L'historique se lit dans le journal**, qui porte déjà toutes les
  transitions (nature des transitions du programme, et natures de validation et
  de rejet). Aucune table d'historique nouvelle.
- **H2 — La liste** referme l'écart du critère 4 d'US-VAL-03 (pas de liste ni
  de fiche de programme) : liste paginée, état, semaine, dernière transition ;
  chaque ligne mène à la consultation de la semaine, qui reçoit un onglet ou
  une section « Historique ».
- **H3 — Requêtes** : liste et historique en nombre de requêtes constant.
- **H4 — Habilitations** : profils qui lisent le programme.

**Tests** : un cycle complet soumis, rejeté, repris, resoumis, validé, signé,
affiché, présenté dans l'ordre avec auteurs et motifs ; filtres ; requêtes
constantes avec 3 et 30 programmes ; HTTP.

Commit : `feat(planification): US-VAL-05 liste et historique des programmes`.

---

## Temps 4 — US-SES-09 : Clôturer une session

3 points · Should · BF-SES-09.

**Critères (backlog v10)** : une session clôturée disparaît des listes de
sélection actives ; brigades, programmes et résultats restent consultables ;
clôture enregistrée avec auteur et date ; une session portant des évaluations
non finalisées ne peut être clôturée.

**Arbitrages**
- **C1 — État existant.** Vérifie d'abord comment `Session` porte aujourd'hui
  son état ; ne crée pas un second mécanisme.
- **C2 — « Non finalisée »** : une évaluation de la session dont les notes ne
  sont pas verrouillées par un procès-verbal. Le refus énumère ces évaluations.
- **C3 — Effets.** Une session clôturée disparaît des sélections de la
  génération, de la création d'évaluation et de l'affectation des stagiaires ;
  rien n'est supprimé.
- **C4 — D-262 se referme ici.** La déclaration de non-exécution d'une séance
  d'une session clôturée devient irréversible, et la déclaration elle-même est
  refusée.
- **C5 — Habilitations** : la cellule pédagogique, qui a ouvert la session.
- **C6 — Réouverture** : non offerte. Une erreur de clôture se corrige hors de
  l'interface. Consigne-le comme limite.

**Tests** : refus avec évaluations non verrouillées, énumérées ; clôture
admise après procès-verbal ; session absente des trois sélections ; données
toujours consultables ; non-exécution refusée et irréversible après clôture
(ferme D-262) ; HTTP.

Commit : `feat(organisation): US-SES-09 clôture de session`.

---

## Suivi et rendu

Décisions, reports (D-262 fermé), écarts, définition de fini complète,
relecture `relecteur-conception` avant chaque commit, `AVANCEMENT.md` à jour
après chaque story.

Rendu final, en français, en une fois : les quatre points du temps 1 ; suite
complète et `pytest -m pdf` ; requêtes ; décisions ; reports ; ce que tu as
tranché seul ; ce que tu n'as pas pu vérifier.
