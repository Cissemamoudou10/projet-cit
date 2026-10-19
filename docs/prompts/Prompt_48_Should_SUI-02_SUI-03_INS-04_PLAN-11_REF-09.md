# Prompt 48 — Sprint 4 : les cinq dernières stories Should

Phase 5, sprint 4, à 9 stories sur 14 (36 points sur 55). Ce prompt porte les
cinq stories Should restantes, soit 19 points, **dans l'ordre imposé
ci-dessous**. Il faut au moins un commit par story et **un seul rendu à la fin**.

Règles inchangées : arrêt sur les seules conditions écrites ici ; pour le reste,
tu tranches selon les trois principes d'arbitrage, tu consignes, tu continues ;
aucun numéro de décision cité de mémoire ; heure de début écrite avant toute
autre action ; auteur des décisions = porteur inscrit dans `sprint-4.md` ; la
matrice d'habilitation fait foi quand un critère omet un profil.

**Condition d'arrêt — le point de décision du mercredi 21 octobre au soir.**
Avant de commencer chaque story, lis la date et l'heure du système. Si l'on est
après le **mercredi 21 octobre 2026 à 20 h 00**, ne commence pas la story :
porte-la, avec toutes les suivantes, en réserve dans `sprint-4.md`, puis passe
directement au rendu. Une story déjà commencée à cette heure est terminée.

---

## Temps 0 — D-279 est tranchée

PLAN-07 et SUI-02 partagent le vocabulaire de RG-61, mais elles ne mesurent pas
la même chose :

| | US-PLAN-07 (livrée) | US-SUI-02 |
|---|---|---|
| Volume comparé au prescrit | **programmé** | **réalisé** |
| Lecteur premier | planification, avant soumission | pédagogique, en cours de formation |
| Écran | consultation de la semaine | rapprochement d'US-SUI-01 et liste d'alertes |

1. **Une seule fonction de statut.** Les statuts conforme, en cours, retard et
   dépassement sont calculés par une seule fonction, qui reçoit le volume
   mesuré. PLAN-07 lui passe le programmé, SUI-02 le réalisé. Si PLAN-07 a
   écrit son propre calcul, factorise-le ; un test d'architecture interdit un
   second calcul.
2. **Le rapprochement d'US-SUI-01 montre le statut du réalisé** : la mise en
   évidence que PLAN-07 y a ajoutée passe sous SUI-02. La consultation de la
   semaine garde celui du programmé.
3. **Deux seuils**, l'un pour le programmé, l'autre pour l'alerte : ils servent
   deux usages différents. Le seuil de PLAN-07 ne change pas.
4. Écris une décision qui ferme D-279.

---

## Story 1 — US-SUI-02 : Être alerté des écarts significatifs

3 points · Should · BF-SUI-02 · CU-P6-12 · RG-61.

**Critères (backlog v10)** : seuil d'alerte paramétrable, en pourcentage du
prescrit ; les matières au-delà du seuil apparaissent dans une liste
d'alertes ; retards et dépassements distingués ; l'alerte disparaît quand
l'écart repasse sous le seuil.

**Arbitrages**
- **A1 — L'alerte est calculée, jamais stockée.** Il n'y a ni table ni tâche
  planifiée : c'est ainsi que l'alerte « disparaît » (critère 4).
- **A2 — Le retard avant la fin de session.** La story veut une alerte
  « avant la fin de la formation » : le prescrit seul ne peut pas servir de
  référence en cours de route, sinon toute matière paraîtrait en retard. En
  cours de session, la matière est en **retard** quand le réalisé est inférieur
  au **programmé échu** (séances terminées avant T de programmes affichés),
  d'un écart supérieur au seuil. Cet écart correspond donc aux non-exécutions.
  À la fin de session (même borne que D-278), la référence devient le
  prescrit. Le **dépassement** compare le réalisé au prescrit. Les contraintes
  dures le rendent normalement impossible ; il reste affiché s'il survient,
  par exemple quand le prescrit est réduit après coup. Consigne cet arbitrage :
  aucun livrable ne le tranche.
- **A3 — La liste d'alertes** est filtrable par session et par brigade, et
  chaque ligne mène au détail de la matière dans le rapprochement. Le nombre
  d'alertes apparaît dans la navigation de la pédagogique, comme le compteur
  des programmes en attente.
- **A4 — Habilitations** : la lecture du domaine « suivi », selon la matrice.

**Tests** : retard en cours de session sur une non-exécution ; aucune alerte
quand le réalisé suit le programmé ; retard sur le prescrit en fin de session ;
dépassement ; disparition après suppression de la non-exécution (réversibilité
d'US-SUI-05, session non clôturée) ; seuil modifié ; requêtes constantes avec
2 et 10 brigades ; HTTP.

Commit : `feat(suivi): US-SUI-02 alertes d'écart sur le réalisé`.

---

## Story 2 — US-SUI-03 : Consulter le tableau de bord des formations

5 points · Should · BF-SUI-03.

**Critères (backlog v10)** : taux d'avancement horaire de chaque brigade en
cours ; nombre de matières achevées, en cours et non commencées ; brigades
présentant des alertes mises en évidence ; accès pour la Direction de Formation
et la pédagogique.

**Arbitrages**
- **B1 — Brigade en cours** : brigade d'une session non clôturée dont la
  période couvre la date du jour.
- **B2 — Taux d'avancement** = réalisé cumulé ÷ prescrit cumulé de la brigade,
  avec la fonction du réalisé d'US-SUI-01 et aucun second calcul.
- **B3 — Matière achevée** : réalisé ≥ prescrit, la règle même du prérequis
  achevé, sur la même fonction. **En cours** : réalisé entre zéro et le
  prescrit, bornes exclues. **Non commencée** : réalisé nul.
- **B4 — Alertes** : la fonction de la story 1. Une brigade portant au moins
  une alerte est mise en évidence, avec son nombre d'alertes et un lien vers sa
  liste filtrée.
- **B5 — Présentation** : brigades groupées par session, puis par type de
  formation comme au programme. Écran en lecture seule, sans graphique
  imposé ; une barre de progression en CSS suffit, sans bibliothèque nouvelle
  (BNF-06).
- **B6 — Habilitations** : la matrice fait foi pour la lecture du domaine
  « suivi ». Le critère cite deux profils ; consigne l'écart s'il en résulte
  un accès plus large.

**Tests** : taux d'avancement calculé ; comptes achevées / en cours / non
commencées ; brigade d'une session clôturée absente ; brigade future absente ;
mise en évidence ; requêtes constantes avec 2 et 10 brigades ; HTTP.

Commit : `feat(suivi): US-SUI-03 tableau de bord des formations`.

---

## Story 3 — US-INS-04 : Consulter la charge d'un instructeur

3 points · Should · BF-INS-04.

**Critères (backlog v10)** : charge en heures sur une période sélectionnable ;
détail par matière ; instructeurs comparables sur la même période ; charge
au-delà d'un seuil paramétrable signalée ; séance regroupée comptée une fois.

**Arbitrages**
- **C1 — Ce qui compte** : les séances de l'instructeur dont le début tombe
  dans la période, quel que soit l'état du programme, comme les contraintes
  les voient. Une séance regroupée compte une fois. Les surveillances
  d'épreuve ne sont pas une charge d'enseignement : elles s'affichent dans une
  colonne séparée et ne s'additionnent pas.
- **C2 — Seuil** : paramètre BNF-13 en heures par semaine, comparé à la
  moyenne hebdomadaire de la période. Aucun livrable ne fixe la valeur : prends
  24 h par semaine par défaut et consigne-la comme **hypothèse à confirmer avec
  le terrain**.
- **C3 — Comparaison** : une vue liste tous les instructeurs non archivés sur la
  période, triable par charge, et chaque ligne ouvre le détail par matière.
- **C4 — Habilitations** : la planification et les profils qui lisent les
  instructeurs, selon la matrice.

**Tests** : regroupement compté une fois ; surveillance hors charge ; période
qui coupe une semaine ; seuil franchi ; requêtes constantes avec 5 et 50
instructeurs ; HTTP.

Commit : `feat(instructeurs): US-INS-04 charge d'enseignement`.

---

## Story 4 — US-PLAN-11 : Dupliquer un programme hebdomadaire

5 points · Should · BF-PLAN-11.

**Critères (backlog v10)** : séances reportées sur les créneaux équivalents ;
programme cible en brouillon, modifiable, et refus si la cible est soumise,
validée ou affichée ; toutes les contraintes dures vérifiées sur la cible ;
séances non reportables écartées et listées avec leur motif ; volume cumulé
comparé au prescrit, tout dépassement signalé ; une ou plusieurs brigades.

**Arbitrages**
- **D1 — Porte unique.** Chaque séance dupliquée s'écrit par
  `ServiceEcritureSeance` ; la garde d'état passe par `ServiceCircuitProgramme`.
  Une cible rejetée est d'abord ramenée à l'état brouillon par la transition de
  reprise, comme le fait la génération. Aucune écriture directe : un test
  d'architecture le vérifie.
- **D2 — Créneau équivalent** : même jour de semaine, mêmes heures. La séance
  garde ses heures réelles et la grille active n'est pas consultée : les
  séances passées gardent leurs heures, et une séance hors grille reste
  reportable.
- **D3 — Ce qui n'est pas dupliqué** : les séances d'un contrôle, liées à une
  évaluation datée, et les séances déclarées non exécutées. Elles sont listées
  avec ce motif.
- **D4 — Regroupements** : une séance regroupée est dupliquée regroupée, pour
  les seules brigades sélectionnées. Si une brigade est refusée par une
  contrainte, les autres sont reportées et le refus est listé ligne par ligne.
- **D5 — Verrouillage** : les séances dupliquées ne sont pas verrouillées. Ce
  sont des propositions, comme celles de la génération, et une régénération
  peut les remplacer.
- **D6 — Atomicité** : la duplication est tout ou rien au niveau technique. Les
  refus métier écartent des séances sans annuler l'opération ; une erreur
  inattendue annule tout.
- **D7 — Requêtes** : constantes, mesurées comme la génération avec 2 et 10
  brigades, avec une référence propre consignée dans `MESURES-REFERENCE.md`.
- **D8 — Habilitations** : la planification, avec la même permission que la
  génération.

**Tests** : duplication nominale ; cible soumise, validée ou affichée refusée ;
cible rejetée ramenée au brouillon ; refus d'instructeur indisponible, de
période bloquée et de jour d'examen sur la cible, listés ; contrôle non
dupliqué ; regroupement partiellement reporté ; dépassement de volume signalé ;
architecture ; requêtes ; HTTP.

Commit : `feat(planification): US-PLAN-11 duplication de programme`.

---

## Story 5 — US-REF-09 : Historiser les modifications du référentiel

3 points · Should · BF-REF-09.

**Critères (backlog v10)** : toute création, modification ou archivage est
enregistré avec son auteur et sa date ; historique consultable depuis la fiche
de la formation, de la matière ou du référentiel ; valeurs antérieures
conservées, notamment les volumes horaires ; historique non modifiable.

**Arbitrages**
- **E1 — Aucune dépendance nouvelle.** Le paquet hors ligne ne la supporterait
  pas sans nouvelle validation. Vérifie d'abord ce que le journal porte déjà :
  la modification d'une note y est enregistrée avec sa valeur précédente
  (US-ADM-04). Réutilise ce mécanisme, avec les valeurs avant et après de
  chaque champ modifié.
- **E2 — Périmètre** : formation, matière du catalogue, élément de référentiel
  (volume, coefficient, poids, catégorie de lieu) et prérequis. Les écritures
  passent par les services du référentiel ; un test d'architecture vérifie
  qu'aucune n'y échappe.
- **E3 — Non modifiable** : c'est déjà garanti par le journal ; vérifie-le par
  un test.
- **E4 — Antériorité** : l'historique commence à la livraison. Aucune reprise
  rétroactive : consigne-le comme limite.

**Tests** : modification du volume avec ses valeurs avant et après ; archivage ;
historique sur chacune des trois fiches ; tentative de modification refusée ;
architecture ; HTTP.

Commit : `feat(referentiel): US-REF-09 historique des modifications`.

---

## Suivi et rendu

Il te faut : des décisions, des reports, des écarts, une définition de fini
complète, une relecture `relecteur-conception` avant chaque commit, et
`AVANCEMENT.md` à jour après chaque story. **Ne commence pas la clôture du
sprint** : elle fera l'objet du prompt suivant.

Rendu final, en français, en une fois :
- les stories livrées et celles qui sont passées en réserve, avec l'heure
  constatée ;
- la suite complète et l'architecture ;
- les requêtes ;
- les décisions, dont la fermeture de D-279 ;
- les hypothèses à confirmer avec le terrain (le seuil de C2) ;
- ce que tu as tranché seul ;
- ce que tu n'as pas pu vérifier.
