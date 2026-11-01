# Prompt 54 — Corrections de RECETTE-00 et RECETTE-00 bis

**Contexte.** RECETTE-00 (sections 3 à 7, étiquette `recette-phase-6`) et RECETTE-00 bis (étiquette `recette-phase-6-c1`) sont jouées. Le chef de projet a décidé de corriger tous leurs constats en une seule fois, ici. RECETTE-00 est **prononcée sous réserve** (1 NC majeur), RECETTE-00 bis est **prononcée**. RECETTE-01 ne commence qu'après ce prompt et le rejeu.

Dépose d'abord dans `docs/recette/` les fichiers fournis : `RECETTE-00-SOCLE.md` et `RECETTE-00-BIS-PLANIFICATION.md` (résultats remplis).

**Règle de conduite.** Chaque correction commence par **la cause**, établie dans le code, avant tout changement. Ne corrige rien d'autre que la liste ci-dessous. Si tu trouves autre chose, consigne-le dans `PROBLEMES.md` sans le corriger.

---

## Temps 0 — Relevé d'heure

Une ligne dans `docs/suivi/heures-phase-6.md`, notée avant d'ouvrir le premier fichier.

## Temps 1 — Les corrections

Ordre de traitement : le NC majeur d'abord, puis les NC mineurs, puis les observations.

| N° | Constat | Qualif. | Attendu après correction | Trace |
|---|---|---|---|---|
| K1 | **R00-SES-15 / SES-14 b** : déplacer ou retirer un stagiaire affecté **le jour même** est refusé, il faut attendre le lendemain | **NC majeur** | Une affectation peut être déplacée ou retirée le jour même. L'historique reste exact (RG-20) : on doit pouvoir dire à quelle brigade appartenait le stagiaire à toute date passée, et le déplacement apparaît dans l'historique. Explique comment l'historisation traite une affectation qui commence et finit le même jour, et pourquoi ce choix ne casse pas RG-20 | US-SES-06 c.4, RG-20 |
| K2 | **R00-SES-14 b** : baisser l'effectif déclaré d'une brigade en dessous du nombre de stagiaires déjà affectés ne donne aucune alerte | NC mineur | **Accepté avec un avertissement** qui donne les deux nombres (déclaré, affectés réels). La règle du backlog ne change pas : l'effectif déclaré reste prévisionnel. Le refus reste réservé à la capacité de la salle (SES-14 a) | US-SES-06 c.3 |
| K3 | **R00-REF-08 / REF-15** : le coefficient et les deux poids d'une matière rattachée n'apparaissent pas dans la liste des matières de la filière, et le formulaire de modification ne les pré-remplit pas | NC mineur | Coefficient et poids **affichés** dans la liste ; formulaire de modification **pré-rempli** avec les valeurs en vigueur | US-REF-03 |
| K4 | **R00-RES-02** : le refus d'un instructeur « militaire du centre » sans matricule a un message imprécis | NC mineur | Message rattaché au champ, qui dit la cause et l'action : « Le matricule est obligatoire pour un militaire du centre. Saisissez-le, ou choisissez le statut vacataire. » | US-INS-01 c.1, BNF-10 |
| K5 | **R00B-TRV-07** : les boutons (Modifier, Supprimer…) apparaissent à l'impression | NC mineur | Aucun bouton ni colonne « Actions » sur l'aperçu d'impression. **Une seule règle d'impression dans la charte**, appliquée par une classe commune, et non une correction écran par écran. Vérifie sur toutes les listes et fiches, pas seulement les deux du cahier | D-63, BNF ergonomie |
| K6 | **Débordement de la liste des instructeurs à l'impression** (168 px, défaut connu) | NC mineur | Le tableau tient dans la largeur d'une page A4 à l'aperçu d'impression | K3 de la revue |
| K7 | **R00B-SUP-08** : après « retirer la soumission », aucun message ne confirme l'action | NC mineur | Un message de confirmation après chaque transition du circuit (soumettre, retirer, rejeter, valider, signer, afficher) et après la suppression d'un brouillon. Vérifie qu'aucune transition n'en manque | BNF-10 |
| K8 | **R00B-GEN-06** : le créneau bloqué par la conférence est une case vide sur le programme | Observation retenue | Sur la consultation **et** sur l'impression du programme, un créneau bloqué par un événement du calendrier porte **le libellé de l'événement** (ex. « Conférence »), avec un style distinct d'une séance. **Pas de nouveau champ** (lieu, responsable) : hors périmètre. Requêtes constantes avec le nombre de brigades | US-PLAN-04 c.5, US-PLAN-12 |
| K9 | **Impression du programme hebdomadaire** (anomalie n°1 de `PROBLEMES.md`) | NC mineur | Relis la fiche de l'anomalie et traite-la telle qu'elle y est décrite (orientation, puis découpage par journée, D-155). Si la fiche et D-155 se contredisent, arrête-toi et signale-le | D-155 |
| K10 | **R00-SES-10** : le backlog (c.5) interdit l'import partiel, la fiche CU-P3-05 (E4) l'autorise ; l'application suit la fiche | NC mineur **documentaire** | **Aucun changement de code.** Un écart dans `ECARTS-LIVRABLES-PHASE-6.md` : le critère c.5 de US-SES-05 sera réécrit dans le backlog v12 | US-SES-05 c.5 |

## Temps 2 — Points de ménage

1. **`statistique_volume.html`** : dis d'où vient ce fichier, quel commit l'a introduit, s'il est utilisé. S'il ne sert à rien, propose sa suppression **sans l'exécuter**.
2. **État `volume` sous Windows** : il ne se charge que depuis le conteneur (WeasyPrint, P-44). Documente-le dans `JEUX-DE-DONNEES-PHASE-6.md`, avec la commande exacte. Le script de remise à zéro doit refuser `-Etat volume` sous Windows avec ce message, au lieu d'échouer en cours de route.

## Temps 3 — Tests

- K1 : test par le vrai cycle HTTP (affecter puis déplacer le même jour ; affecter puis retirer le même jour) et un test de l'historique à une date passée.
- K2, K3, K4, K7 : un test par constat.
- K5, K6, K8 : vérification de la règle d'impression par un test sur le gabarit, plus `pytest -m pdf` en conteneur pour l'impression du programme.
- K8 : mesure du nombre de requêtes de la consultation du programme, inchangé avec le nombre de brigades.
- Les tests existants qui affirmaient l'ancien comportement (refus le jour même, K1) sont **modifiés en le disant**, pas supprimés.

## Temps 4 — Contrôle, étiquette, commit

1. Relecture par `relecteur-conception` de K1 et K8.
2. Suite complète, **seule sur la machine** (P-51), puis `pytest -m pdf` en conteneur.
3. Commits séparés : K1 ; K2 à K4 ; K5, K6, K8, K9 (impression et affichage) ; K7 ; documentation (K10, Temps 2).
4. Consigne chaque correction dans `PROBLEMES.md` (constat, cause, correction, commit), et la décision sur K1 dans `DECISIONS.md` (numéro relu, pas supposé).
5. Pose l'étiquette **`recette-phase-6-c2`** sur le dernier commit. `recette-phase-6` et `recette-phase-6-c1` ne bougent pas.
6. Vérifie que les états `complet` et `socle-planif` se chargent et se vérifient toujours entièrement.
7. Mets à jour le nombre de tests dans `AVANCEMENT.md` ; clôture la ligne d'heures.

## Rendu attendu

- Pour chaque constat K1 à K10 : la cause trouvée, la correction, le commit.
- La décision ouverte pour K1.
- Le résultat des suites (nombre de tests) et de `--verifier` pour `complet` et `socle-planif`.
- Le Temps 2 : origine de `statistique_volume.html` et ta proposition.
- Ce que tu as tranché seul, et ce que tu n'as pas pu vérifier.
