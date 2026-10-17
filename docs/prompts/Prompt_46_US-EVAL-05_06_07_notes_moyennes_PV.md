# Prompt 46 — Sprint 4 : US-EVAL-05, 06, 07 — notes, moyennes, procès-verbal

Phase 5, sprint 4. Dernières stories **Must** du projet : 15 points, trois
commits, **un seul rendu à la fin**. Après ce prompt, tout le périmètre Must
(194 points) est livré.

Règles inchangées : arrêt sur les seules conditions écrites ici ; pour le reste,
tu tranches selon les trois principes d'arbitrage, tu consignes, tu continues ;
aucun numéro de décision cité de mémoire ; heure de début écrite avant toute
autre action ; auteur des décisions = porteur inscrit dans `sprint-4.md` ; toute
story qui produit un PDF exécute `pytest -m pdf` dans le conteneur.

Sources : backlog v10 (US-EVAL-05 à 07), cas d'utilisation v4 (CU-P6-05,
CU-P6-06, CU-P6-07), RG-54 à RG-59 bis, CLS-05 (`Note`, `ProcesVerbal`).

---

## 0. Préalables, sans arrêt

1. **Échéance du 16 octobre (R1).** Vérifie que `DECISIONS.md` porte la
   décision datée du 16/10 sur ETA-01. Si elle manque, écris-la : sans retour
   des cellules à l'échéance, le circuit implanté sur les réponses par défaut
   aux quatre questions de la note du 30/09 fait référence ; toute réponse
   ultérieure sera instruite comme une demande d'évolution (R11). Auteur :
   « Lt Cissé (chef de projet) ».
2. **`ServiceDocument` et son domaine.** Tu l'as rattaché au domaine
   « administration ». Vérifie que seule la **gestion des gabarits** exige ce
   domaine, et que **la production d'un document** est gardée par la permission
   de l'acte métier appelant (planification pour la progression, examens pour
   le procès-verbal). Si `produire` exige l'administration, corrige-le avant
   d'écrire le procès-verbal.
3. **Lecture seule** : sur `ElementReferentiel`, la présence et le nom exact
   du coefficient, du poids formatif et du poids certificatif ; le calcul de
   l'effectif réel (stagiaires non radiés) ; le mécanisme d'état transitoire
   utilisé par l'import des stagiaires (validation en deux temps) ; la
   convention D-219 sur les lectures sensibles.

**Condition d'arrêt** : si l'un des trois attributs de pondération de
`ElementReferentiel` n'existe pas, arrête-toi et montre-moi le modèle.

---

## 1. US-EVAL-05 — Saisir et vérifier les notes

5 points · Must · BF-EVAL-05 · CU-P6-05 · RG-54, RG-55 · BNF-02.

**Critères (backlog v10)** : saisie par évaluation pour tous les stagiaires du
périmètre ; note entre zéro et la note maximale de l'évaluation ; absence
distinguée d'une note nulle ; double vérification avant enregistrement ; toute
modification journalisée avec sa valeur précédente ; seule la cellule examens
saisit ; consultation journalisée.

**Arbitrages**

- **N1 — Modèle.** `Note` : évaluation, stagiaire, valeur (décimale, nulle),
  absent (booléen). Unique par (évaluation, stagiaire). En base : valeur
  positive ou nulle ; exactement une des deux situations, une valeur **ou**
  une absence. Une note non saisie n'a pas de ligne. `Evaluation` reçoit une
  **note maximale**, 20 par défaut, strictement positive. La borne supérieure,
  inter-tables, est vérifiée en service.
- **N2 — Stagiaires concernés.** Ceux du périmètre de l'évaluation, brigade ou
  session, résolus à la lecture, **non radiés** (E3). Un stagiaire radié après
  la saisie garde sa note mais n'apparaît plus au calcul ni au procès-verbal.
- **N3 — Double vérification (CU-P6-05, étapes 5 et 6).** Première étape : la
  saisie est contrôlée et présentée en récapitulatif — notes saisies, notes
  manquantes, absences, valeurs extrêmes, moyenne de l'évaluation — **sans rien
  écrire**. Seconde étape : confirmation, écriture en une transaction. Réutilise
  le mécanisme d'état transitoire de l'import des stagiaires, ne le réécris pas.
  La saisie partielle (A3) est admise : les notes confirmées restent, les
  manquantes sont listées.
- **N4 — Journal.** Chaque création, modification ou suppression d'une note est
  journalisée avec l'ancienne et la nouvelle valeur (RG-55), que seuls les
  profils qui lisent le journal consultent.
- **N5 — Confidentialité (BNF-02, convention D-219 cas a).** Les notes sont des
  données sensibles : l'écran de saisie et de consultation des notes est réservé
  à la cellule examens, refusé en 403 à tout autre profil, Direction de
  Formation comprise ; chaque affichage de la grille est journalisé. La
  Direction lira les résultats par le procès-verbal (US-EVAL-07).
- **N6 — Absence (A1).** Le traitement de l'absence au calcul est un paramètre
  BNF-13 à deux valeurs : compter zéro, ou exclure l'évaluation du calcul du
  module pour ce stagiaire. Valeur par défaut : **compter zéro**, la plus
  défavorable, donc celle qui ne peut pas avantager un stagiaire par erreur.
  Question ajoutée au terrain.
- **N7 — Verrou (RG-55).** Toute écriture sur une note d'une évaluation couverte
  par un procès-verbal est refusée. Le prédicat « verrouillée » est **calculé**
  (existence d'un procès-verbal couvrant l'évaluation), jamais stocké : CLS-05
  porte un booléen `notesVerrouillees`, écart à consigner.

**Tests** : base (doublon, valeur et absence ensemble, ni l'une ni l'autre,
valeur négative, note maximale nulle) ; service (note au-dessus du maximum,
stagiaire hors périmètre, stagiaire radié, saisie partielle, modification
journalisée avec ancienne et nouvelle valeur, refus après verrouillage) ;
confidentialité (403 pour les quatre autres profils, une entrée de journal par
affichage, aucune par refus) ; HTTP (étape de vérification sans écriture, puis
confirmation ; nombre de requêtes constant pour 10 et 40 stagiaires).

Commit : `feat(evaluations): US-EVAL-05 saisie et vérification des notes`.

---

## 2. US-EVAL-06 — Calculer moyennes et classement

5 points · Must · BF-EVAL-06 · RG-56, RG-57.

**Critères (backlog v10)** : moyenne selon les coefficients du référentiel de la
formation ; coefficient propre au couple formation-matière ; second niveau, le
poids du type d'évaluation dans la note du module ; coefficients paramétrables
sans code ; classement au niveau de la session, rang en brigade calculable ;
égalités traitées selon une règle explicite ; une note manquante empêche le
calcul et est signalée.

**Arbitrages**

- **M1 — Rien n'est stocké.** Moyennes et rangs sont calculés à la demande, par
  un service unique. Le procès-verbal fige le résultat (US-EVAL-07), pas ce
  service.
- **M2 — Normalisation.** Chaque note est ramenée sur 20 avant tout calcul
  (valeur ÷ note maximale × 20).
- **M3 — Note d'un module (second niveau).** Pour un stagiaire et un module :
  moyenne simple des évaluations formatives, moyenne simple des évaluations
  certificatives, puis moyenne de ces deux moyennes pondérée par le poids
  formatif et le poids certificatif de l'élément du référentiel. Un type sans
  évaluation est retiré du calcul et son poids avec lui. Absence : selon N6.
- **M4 — Moyenne générale (premier niveau).** Moyenne des notes de module
  pondérée par les coefficients. Un module **sans aucune évaluation** n'entre
  pas dans la moyenne et est signalé ; un module évalué mais incomplet bloque.
- **M5 — Note manquante.** Un stagiaire du périmètre sans note ni absence sur
  une évaluation concernée bloque le calcul ; la liste des manquants est rendue
  **par module et par brigade** (RG-59 bis).
- **M6 — Égalités.** Classement de compétition : deux ex aequo partagent le
  même rang, le suivant prend le rang augmenté du nombre d'ex aequo (1, 2, 2,
  4). Comparaison sur la moyenne arrondie à deux décimales, l'arrondi étant
  celui qui sera imprimé. Ordre d'affichage des ex aequo : alphabétique. Règle
  écrite dans la décision et affichée sous le classement.
- **M7 — Rang en brigade** : même règle, restreinte à la brigade.
- **M8 — Écran.** Aperçu des moyennes et du classement d'une session pour la
  cellule examens, avant tout procès-verbal ; requêtes constantes pour 2 et 10
  brigades.

**Tests** : un jeu calculé à la main dans le test, et non par le code testé :
deux formations, coefficients différents pour une même matière, poids
formatif et certificatif, une évaluation sur 10 ramenée sur 20, une absence
sous les deux valeurs de N6, deux ex aequo ; module sans évaluation ignoré et
signalé ; manquants énumérés par module et par brigade ; rang en brigade.

Commit : `feat(evaluations): US-EVAL-06 moyennes et classement`.

---

## 3. US-EVAL-07 — Générer les procès-verbaux de résultats

5 points · Must · BF-EVAL-07 · CU-P6-07 · RG-58, RG-59, RG-59 bis · R18.

**Critères (backlog v10)** : liste des stagiaires, moyennes, rang, décision ;
admis et ajournés selon un seuil paramétrable ; format imprimable ; génération
journalisée ; procès-verbal non modifiable, toute correction donnant une
nouvelle version.

**Arbitrages**

- **V1 — Deux types**, comme CU-P6-07 : le **procès-verbal de fin de formation**,
  unique par session, toutes brigades (RG-59 bis) ; le **procès-verbal d'une
  évaluation** (A1). Modèle `ProcesVerbal` : type, session, évaluation (pour le
  second type seulement), numéro (saisi, facultatif), version, généré le,
  généré par, et **le fichier PDF produit**. En base : l'évaluation est
  renseignée si et seulement si le type est « évaluation ».
- **V2 — Le PDF est conservé.** La régénération « à l'identique » (A2) rend le
  fichier enregistré, sans rien recalculer : c'est la seule façon d'être
  réellement à l'identique quand le gabarit a changé entre-temps.
- **V3 — Verrouillage (RG-59).** Le procès-verbal est relié aux évaluations
  qu'il couvre, en plusieurs-à-plusieurs : une évaluation peut être couverte
  par son propre procès-verbal puis par celui de fin de formation. CLS-05 porte
  0..1 : écart à consigner.
- **V4 — Opération atomique (E3).** Calcul, production du PDF, enregistrement du
  procès-verbal et verrouillage dans une seule transaction : si le PDF échoue,
  rien n'est verrouillé.
- **V5 — Complétude (RG-59 bis, E1).** Une seule note manquante sur une
  évaluation concernée bloque la génération, avec la liste par module et par
  brigade (M5).
- **V6 — Seuil d'admission** : paramètre BNF-13, **10 sur 20** par défaut.
  Décision « Admis » si la moyenne est supérieure ou égale au seuil.
- **V7 — « Correction = nouvelle version. »** Les notes verrouillées ne se
  corrigent pas dans le système : la rectification relève de la réglementation
  (CU-P6-05, A4). Une nouvelle version naît d'une **correction du gabarit**
  (E2) : elle recalcule sur les mêmes notes, s'enregistre avec un numéro de
  version supérieur, et la précédente reste consultable. Consigne l'arbitrage
  entre le critère du backlog et la fiche (principe 1).
- **V8 — Gabarit.** Réutilise `GabaritDocument` et `ServiceDocument` posés à
  US-SUI-06 : un type « procès-verbal de fin de formation » et un type
  « procès-verbal d'évaluation », chargés par la commande des gabarits. Aucune
  ligne de mise en page dans le code.
- **V9 — Aperçu avant génération (CU-P6-07, étape 4)** : l'écran présente
  moyennes, rangs et décisions, puis la confirmation génère.
- **V10 — Habilitations.** Générer : cellule examens. Consulter et télécharger
  un procès-verbal : examens et Direction de Formation (`evaluations_lecture`).
  Chaque téléchargement est journalisé (donnée sensible, D-219). Aucun autre
  profil.
- **V11 — R18.** Le format réglementaire reste inconnu : le gabarit livré porte
  la mention « Modèle provisoire — format réglementaire non communiqué » dans
  son pied, modifiable par l'administrateur.

**Tests** : base (évaluation renseignée hors du type « évaluation ») ; service
(génération refusée sur note manquante avec liste ; notes verrouillées après
génération ; écriture de note refusée ensuite ; deux procès-verbaux sur la
même évaluation ; échec forcé du PDF, aucune note verrouillée ; régénération
rendant le même fichier ; nouvelle version après modification du gabarit,
l'ancienne conservée ; seuil modifié par paramètre) ; PDF (marqueur `pdf`,
conteneur : intitulés, rangs et décisions présents par extraction de texte,
aucune requête réseau) ; HTTP (aperçu, génération, téléchargement par la
Direction, refus pour planification et pédagogique, une entrée de journal par
téléchargement).

Commit : `feat(evaluations): US-EVAL-07 procès-verbaux de résultats`.

---

## Suivi et rendu

Pour chaque story : décisions, reports, écarts (CLS-05 sur N7 et V3 ; backlog
sur V7), définition de fini complète, relecture `relecteur-conception` avant
chaque commit. Questions de terrain ajoutées : traitement de l'absence (N6),
seuil d'admission (V6), règle d'égalité (M6).

Rendu final, en français, en une fois : les trois préalables ; suite complète
et `pytest -m pdf` dans le conteneur ; requêtes ; décisions ; reports ; ce que
tu as tranché seul ; ce que tu n'as pas pu vérifier.
