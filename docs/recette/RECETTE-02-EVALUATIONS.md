# RECETTE-02 — Évaluations

**Objet.** Le circuit d'une évaluation, de la création au procès-verbal : type et périmètre, date d'examen final, sujets, organisation d'une épreuve, notes, moyennes et classement, procès-verbaux.

**Stories.** US-EVAL-01 à US-EVAL-07 — toutes Must. Deux types seulement : **formative** (contrôle, examen partiel) et **certificative** (examen final). C'est la correction de terrain du 25 août : l'objectif OS3 en annonçait trois.

**Cadre.** Plan `PLAN-DE-TESTS-PHASE-6.md`. Jeu `complet`, décrit dans `JEUX-DE-DONNEES-PHASE-6.md`.

| Date d'exécution | Recetteur | Relecteur | Navigateur | Date système | Lundi de W0 |
|---|---|---|---|---|---|
| | | | | | |

---

## 1. Préparation

1. `.\outils\recette\reinitialiser_base_recette.ps1 -Etat complet` : vérification à 73/73 et 47/47.
2. **Deux façons de lancer l'application** :
   - sous Windows, pour tout le cahier sauf les contrôles marqués **[PDF]** : `python app\manage.py runserver --settings=config.settings.recette` ;
   - **dans le conteneur de l'image de production** pour les contrôles **[PDF]** : WeasyPrint ne s'exécute pas sous Windows (P-44), et la génération d'un procès-verbal produit un PDF. La commande est fournie par le prompt 52 (`outils/recette/lancer_recette_conteneur.ps1`), sur la **même base** `pfe_cit_recette`. On peut basculer de l'un à l'autre en cours de cahier sans recharger la base.
3. `u_plan` génère W+1 pour EXP1, EXP2 et CDP1 : certains contrôles ont besoin de séances en W+1.

## 2. Données utilisées

| Évaluation | Type | Module, périmètre | Date (semaine du 26/10) | État au chargement |
|---|---|---|---|---|
| **E1** | formative | M1, brigade EXP1 | jeudi W-1 (22/10), séance verrouillée | **19 notes et 1 absence**, avec au moins deux ex aequo. Pas de procès-verbal |
| **E5** | formative | M4, brigade CDP1 | jeudi W-1 (22/10), séance verrouillée | **10 notes sur 12** : deux manquantes |
| **E2** | formative | M2, brigade EXP2 | mercredi W+1 (04/11), séance verrouillée en W+1 | Aucune note |
| **E3** | certificative | M6, session S1 | mardi W+5 (01/12) | Sujets `SUJ-E3-A` (**retenu**) et `SUJ-E3-B`. Organisation **partielle** : EXP1 en L9 ; EXP2 non organisée. Surveillants de EXP1 prévus par le prompt 51 : I8 et l'extérieur « FICT Surveillant-A ». `JEUX-DE-DONNEES` ne les confirme pas : vérifier à l'écran (R02-EVAL04-01) |
| **E4** | certificative | M3, session S1 | mercredi W+6 (09/12) | Aucun sujet, aucune organisation |

Référentiel de F6 : M1 a le **coefficient 3** et les poids formatif 1 et certificatif 2 ; les autres matières ont les valeurs par défaut. La session S2 (CDP1) n'a qu'**une évaluation, E5** : une fois E5 complète, son procès-verbal de fin de formation devient possible (section 9).

---

## 3. Créer une évaluation — US-EVAL-01

Profil : `u_exa`.

| Code | Contrôle | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|
| R02-EVAL01-01 | Ouvrir le formulaire de création | Deux types proposés, formative et certificative ; aucun troisième | US-EVAL-01 c.1 | ☐ | |
| R02-EVAL01-02 | Choisir formative, puis certificative ; regarder le périmètre proposé ; choisir le périmètre session | Défaut : brigade pour la formative, session pour la certificative, modifiable. Le périmètre session déclenche un **avertissement** (sujet commun aux brigades) | US-EVAL-01 c.3 | ☐ | |
| R02-EVAL01-03 | Formative, module **M4**, brigade EXP1 | Refus : M4 n'appartient pas au référentiel de F6 | US-EVAL-01 c.2, RG-52 | ☐ | |
| R02-EVAL01-04 | Formative, M1, EXP1, **jeudi de W+1** à 10:10 | Créée ; une **séance verrouillée** est insérée dans W+1 et signalée comme contrôle | US-EVAL-01 c.4 | ☐ | |
| R02-EVAL01-05 | Formative, M3, EXP1, sur le même créneau que le contrôle 04 | Refus, avec son motif (créneau occupé) | US-EVAL-01 c.4 | ☐ | |
| R02-EVAL01-06 | Formative, M3, EXP2, date du lundi de W-1, **sans motif**, puis avec le motif « déclarée après coup » | Sans motif : refus. Avec motif : créée, **sans aucune séance** | US-EVAL-01 c.5 | ☐ | |
| R02-EVAL01-07 | Certificative, M7, session S1, date passée ; puis date postérieure à la fin de S1 (25/12) | Les deux refus | US-EVAL-01 c.6 | ☐ | |
| R02-EVAL01-08 | Sur l'évaluation du contrôle 04, chercher à modifier le type ou le périmètre | Impossible | US-EVAL-01 c.8 | ☐ | |
| R02-EVAL01-09 | Supprimer l'évaluation du contrôle 04 ; puis tenter de supprimer **E3** | Première supprimée, ainsi que sa séance. E3 refusée : elle est organisée et a un sujet retenu | US-EVAL-01 c.8 | ☐ | |
| R02-EVAL01-10 | `u_plan` soumet W+1 ; `u_exa` crée une formative M1 sur EXP1 en W+1 ; `u_plan` retire la soumission | Insertion refusée tant que W+1 est soumis | D-170, RG-41 | ☐ | |

## 4. Date d'examen final — US-EVAL-02

| Code | Contrôle | Profil | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|---|
| R02-EVAL02-01 | Ouvrir E4 | `u_exa` | La date est identifiée comme **imposée par le 3ᵉ bureau** | US-EVAL-02 c.1 | ☐ | |
| R02-EVAL02-02 | Chercher la modification de la date de E4 | `u_ped`, `u_plan` | Absente pour les deux | US-EVAL-02 c.2 | ☐ | |
| R02-EVAL02-03 | Modifier la date de E4 sans motif ; puis au mardi de W+1, avec le motif « notification du 3ᵉ bureau n° 12 » | `u_exa` | Sans motif : refus. Avec motif : acceptée, et les **séances déjà programmées ce mardi pour EXP1 et EXP2 sont signalées**, sans être supprimées | US-EVAL-02 c.2, c.4 | ☐ | |
| R02-EVAL02-04 | Journal de E4 | `u_adm` | Ancienne et nouvelle date, motif, auteur | US-EVAL-02 c.2 | ☐ | |
| R02-EVAL02-05 | Remettre E4 au mercredi de W+6 (motif), puis générer W+6 pour EXP1 (`u_plan`) | `u_exa`, `u_plan` | Aucune séance de EXP1 le mercredi de W+6 : le jour est fermé par **projection** de la date, sans période créée au calendrier | US-EVAL-02 c.3 | ☐ | |
| R02-EVAL02-06 | Vue annuelle et vue mensuelle du calendrier | `u_plan` | Les jours de E3 et E4 y apparaissent | US-EVAL-02 c.5 | ☐ | |

## 5. Sujets — US-EVAL-03

Profil : `u_exa` sauf indication contraire.

| Code | Contrôle | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|
| R02-EVAL03-01 | Ouvrir les sujets de E3 | Deux **références** (`SUJ-E3-A` retenu, `SUJ-E3-B`), jamais un contenu | US-EVAL-03 c.2 | ☐ | |
| R02-EVAL03-02 | Ajouter un troisième sujet à E3 | Refus | US-EVAL-03 c.3 | ☐ | |
| R02-EVAL03-03 | Changer le sujet retenu de E3 vers B, sans motif ; puis avec le motif « décision de la commission du … » | Sans motif : refus. Avec motif : accepté, horodaté, rattaché à `u_exa` | US-EVAL-03 c.4, c.5 | ☐ | |
| R02-EVAL03-04 | E4 : enregistrer **un seul** sujet, puis le désigner comme retenu | Avertissement, puis confirmation explicite exigée ; sélection acceptée après confirmation | US-EVAL-03 c.4 | ☐ | |
| R02-EVAL03-05 | E2 (formative) : enregistrer un sujet, puis un second | Le premier accepté, sans mécanisme de sélection ; le second refusé | US-EVAL-03 c.3 | ☐ | |
| R02-EVAL03-06 | Ouvrir l'écran des sujets de E3 avec `u_ped`, `u_plan` et `u_df` | Refus pour les trois, **Direction de Formation comprise** | US-EVAL-03 c.6 | ☐ | |
| R02-EVAL03-07 | `u_adm` : journal des consultations de sujets | Chaque consultation des contrôles 01 à 05 est journalisée ; le sujet y est désigné **par son rang**, jamais par sa référence | US-EVAL-03 c.6 | ☐ | |

## 6. Organiser une épreuve — US-EVAL-04

Profil : `u_exa`. Sur E3.

| Code | Contrôle | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|
| R02-EVAL04-01 | Ouvrir E3 | **Incomplète** (EXP2 non organisée), donc **non prête**. EXP1 : L9, I8 et « FICT Surveillant-A » | US-EVAL-04 c.6 | ☐ | |
| R02-EVAL04-02 | Organiser EXP2 dans **L7** (capacité 12, effectif 15) | Refus, avec l'écart de capacité | US-EVAL-04 c.3 | ☐ | |
| R02-EVAL04-03 | Organiser EXP2 dans L4 (30), **sans surveillant** | Saisie possible par étapes ; l'épreuve reste incomplète (lieu sans surveillant) | US-EVAL-04 c.6 | ☐ | |
| R02-EVAL04-04 | `u_plan` déclare I7 indisponible le jour de E3 ; `u_exa` désigne I7 surveillant de EXP2 | Refus : surveillant référencé indisponible | US-EVAL-04 c.3, c.4 | ☐ | |
| R02-EVAL04-05 | Désigner comme surveillant une personne extérieure, « FICT Surveillant-B » | Acceptée sans contrôle de disponibilité. E3 devient **complète**, et **prête** puisqu'elle a un sujet retenu | US-EVAL-04 c.4, c.6 | ☐ | |
| R02-EVAL04-06 | `u_ped` radie un stagiaire de EXP2 ; `u_exa` rouvre E3 | E3 redevient **incomplète** (effectif attendu ≠ effectif réel) : l'état est calculé | US-EVAL-04 c.6 | ☐ | |
| R02-EVAL04-07 | Corriger l'effectif attendu de EXP2 | E3 de nouveau complète et prête | US-EVAL-04 c.6, c.7 | ☐ | |
| R02-EVAL04-08 | `u_plan` consulte l'occupation de L4 et de I8 au créneau de E3 | L4 et I8 apparaissent occupés par l'épreuve | US-EVAL-04 c.5 | ☐ | Si aucun écran ne montre l'occupation, noter SO et passer à 09 |
| R02-EVAL04-09 | `u_plan` génère W+5 pour CDP1 (S2, hors périmètre de E3) | Aucune séance de CDP1 dans L4 ni avec I8 sur le créneau de l'épreuve | US-EVAL-04 c.5, RG-53 | ☐ | |
| R02-EVAL04-10 | Changer la date de E3 (motif du 3ᵉ bureau) vers un jour où L9 est occupé | Changement **accepté** ; l'organisation est revérifiée et ses conflits sont signalés | US-EVAL-04 c.7 | ☐ | Remettre la date d'origine ensuite |
| R02-EVAL04-11 | Ouvrir la convocation de E3 ; l'imprimer en aperçu ; l'ouvrir avec `u_df` | Consultable et imprimable, lisible par `u_df`, **sans aucune mention de sujet** | US-EVAL-04 c.8 | ☐ | |

## 7. Notes — US-EVAL-05

Profil : `u_exa` sauf indication contraire.

| Code | Contrôle | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|
| R02-EVAL05-01 | Ouvrir la saisie des notes de E1 | Les 20 stagiaires de EXP1 non radiés ; 19 notes et 1 absence | US-EVAL-05 c.1 | ☐ | |
| R02-EVAL05-02 | Saisir une note au-dessus de la note maximale, puis une note négative | Les deux refusées | US-EVAL-05 c.2 | ☐ | |
| R02-EVAL05-03 | Comparer le stagiaire absent et une note de 0 | Absence et zéro sont distingués partout | US-EVAL-05 c.3 | ☐ | |
| R02-EVAL05-04 | E5 : saisir les deux notes manquantes | Une **double vérification** est proposée avant l'enregistrement définitif ; E5 complète (12/12) | US-EVAL-05 c.4 | ☐ | |
| R02-EVAL05-05 | Modifier une note de E1, puis consulter le journal (`u_adm`) | La valeur précédente est journalisée ; confirmer la même valeur ne crée aucune entrée de plus | US-EVAL-05 c.5 | ☐ | |
| R02-EVAL05-06 | Ouvrir la saisie des notes de E1 avec `u_ped`, `u_plan` et `u_df` | Refus pour les trois | US-EVAL-05 c.6, US-ADM-03 c.4 | ☐ | |
| R02-EVAL05-07 | Ouvrir la fiche de E1 (écran partagé) avec `u_df` | Aucun résumé de notes visible | US-EVAL-05 c.6 (N5) | ☐ | |
| R02-EVAL05-08 | `u_adm` : journal | Chaque consultation des notes par `u_exa` est journalisée | US-EVAL-05 c.6 | ☐ | |

## 8. Moyennes et classement — US-EVAL-06

Profil : `u_exa`.

| Code | Contrôle | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|
| R02-EVAL06-01 | Ouvrir les moyennes de S1 | Les stagiaires bloqués par une note manquante sont signalés, et les manquants **énumérés par module et par brigade** (EXP2 : E2 sans notes) | US-EVAL-06 c.7 | ☐ | |
| R02-EVAL06-02 | Recalculer à la main la moyenne d'un stagiaire de EXP1 (E1 seule notée) | Égale à l'affichage, au centième ; le stagiaire absent est compté **zéro** (paramètre par défaut) | US-EVAL-06 c.1, c.3 | ☐ | |
| R02-EVAL06-03 | Classement | Établi au niveau de la session ; le rang dans la brigade reste disponible | US-EVAL-06 c.5 | ☐ | |
| R02-EVAL06-04 | Repérer les ex aequo de E1 | Même rang ; le rang suivant est sauté (classement « de compétition ») ; la règle est écrite à l'écran ou dans l'aide | US-EVAL-06 c.6 | ☐ | |
| R02-EVAL06-05 | `u_ped` porte le coefficient de M1 dans F6 de 3 à 2 ; `u_exa` recharge les moyennes | Moyennes recalculées sans autre action : rien n'est stocké. Remettre 3 | US-EVAL-06 c.1, c.2, c.4 | ☐ | |
| R02-EVAL06-06 | Ouvrir les moyennes avec `u_plan` | Refus | US-ADM-03 c.4 | ☐ | |

## 9. Procès-verbaux — US-EVAL-07

Profil : `u_exa`. **Contrôles [PDF] : application lancée dans le conteneur** (§ 1).

| Code | Contrôle | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|
| R02-EVAL07-01 | [PDF] Générer le procès-verbal de **E1** | Pour chaque stagiaire de EXP1 : la note sur la note maximale **et** ramenée sur 20, l'absence, le rang ; **aucune décision d'admission** | US-EVAL-07 c.3 | ☐ | |
| R02-EVAL07-02 | Tenter de modifier une note de E1 | Refus : notes verrouillées par le procès-verbal | US-EVAL-07 c.4 | ☐ | |
| R02-EVAL07-03 | [PDF] Télécharger le procès-verbal de E1 ; `u_adm` consulte le journal | Document imprimable ; génération journalisée avec auteur et date | US-EVAL-07 c.5, c.6 | ☐ | |
| R02-EVAL07-04 | [PDF] Générer à nouveau le procès-verbal de E1 | Une **nouvelle version** ; l'ancienne reste consultable, inchangée | US-EVAL-07 c.7 | ☐ | |
| R02-EVAL07-05 | Demander le procès-verbal de **fin de formation de S1** | Refus : les notes manquantes sont énumérées **par module et par brigade** | US-EVAL-07 c.1 | ☐ | |
| R02-EVAL07-06 | [PDF] Après R02-EVAL05-04 (E5 complète), générer le procès-verbal de **fin de formation de S2** | Unique pour la session : stagiaires de CDP1, moyennes, rang et **décision admis/ajourné au seuil de 10/20** | US-EVAL-07 c.1, c.2, RG-59 bis | ☐ | |
| R02-EVAL07-07 | Recalculer à la main la décision de deux stagiaires de S2, l'un au-dessus et l'autre au-dessous de 10 | Conforme au seuil | US-EVAL-07 c.2 | ☐ | |
| R02-EVAL07-08 | Ouvrir les procès-verbaux avec `u_df`, puis avec `u_plan` | `u_df` consulte et télécharge ; `u_plan` refusé | V10, matrice | ☐ | |
| R02-EVAL07-09 | [PDF] Relire les deux PDF imprimés | En-tête, mentions, bloc de signature lisibles ; aucun code interne (RG-xx, codes de prompt) dans le texte imprimé ; aucun débordement | RG-58, R18 | ☐ | Jugement humain : noter toute remarque de mise en page |

---

## 10. Dépouillement

| Section | Contrôles | C | NC majeur | NC mineur | B | SO |
|---|---|---|---|---|---|---|
| 3. Création | 10 | | | | | |
| 4. Date d'examen final | 6 | | | | | |
| 5. Sujets | 7 | | | | | |
| 6. Organisation | 11 | | | | | |
| 7. Notes | 8 | | | | | |
| 8. Moyennes et classement | 6 | | | | | |
| 9. Procès-verbaux | 9 | | | | | |
| **Total** | **57** | | | | | |

☐ Prononcée ☐ Prononcée sous réserve (rejeu le ______) ☐ Refusée

**Observations :**

## 11. Matrice critère → contrôles

| Story | Critères | Contrôles |
|---|---|---|
| US-EVAL-01 | c.1 à c.8 | EVAL01-01 à 10 (c.7 : sous-entendu dans 05, 07 ; vérifié en RECETTE-05) |
| US-EVAL-02 | c.1 à c.5 | EVAL02-01 à 06 |
| US-EVAL-03 | c.1 à c.7 | EVAL03-01 à 07 ; c.1 (instructeur sans accès) : RECETTE-05 ; c.7 : EVAL04-05 |
| US-EVAL-04 | c.1 à c.8 | EVAL04-01 à 11 ; c.1 (créneau unique) se lit en EVAL04-01 |
| US-EVAL-05 | c.1 à c.6 | EVAL05-01 à 08 |
| US-EVAL-06 | c.1 à c.7 | EVAL06-01 à 06 |
| US-EVAL-07 | c.1 à c.7 | EVAL07-01 à 09 |

## 12. Fiche d'anomalie

Modèle commun : `RECETTE-00-SOCLE.md`, § 12 (code `R02-…`).

---

*RECETTE-02 — version 1 du 28 octobre 2026. Lot WBS 6.3.*
