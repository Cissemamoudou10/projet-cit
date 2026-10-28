# RECETTE-05 — Transverse, bout en bout et jeu volumineux

**Objet.** Ce qui ne relève d'aucun paquetage en particulier mais de l'ensemble :
- les habilitations croisées des cinq profils ;
- le journal ;
- tous les documents imprimés et exportés ;
- un scénario de bout en bout qui traverse les trois cellules ;
- la mesure de l'objectif OS5 ;
- l'observation de l'application à la taille réelle du centre.

Ce cahier se termine par la **synthèse des objectifs SMART**, qui conditionne le prononcé de C3.

**Stories.** Toutes, vues sous l'angle transverse : US-ADM-03 et US-ADM-04 en premier lieu, BNF-01, 02, 04, 05, 09, 10, 14, 15.

**Cadre.** Plan `PLAN-DE-TESTS-PHASE-6.md`. Jeu `complet` pour les sections 3 à 6, jeu **volumineux** pour la section 7. Joué **par les deux équipiers** (plan, § 7).

| Date d'exécution | Recetteurs | Navigateur | Date système | Lundi de W0 |
|---|---|---|---|---|
| | | | | |

---

## 1. Préparation

**Sections 3 à 6** : `.\outils\recette\reinitialiser_base_recette.ps1 -Etat complet`. Application sous Windows, ou dans le conteneur pour les contrôles **[PDF]** (`outils/recette/lancer_recette_conteneur.ps1`).

**Section 7** : `.\outils\recette\reinitialiser_base_recette.ps1 -Etat volume`, puis lancement sur `config.settings.volume`. Les comptes du jeu volumineux sont `v_ped`, `v_plan`, `v_exa`, `v_df` et `v_adm`. Leur mot de passe est donné par le chargeur (`comptes_volume.py`) : notez-le ici ______.

**Le jeu volumineux et le jeu de recette sont deux bases différentes.** Pendant la section 7, aucune autre commande ne doit toucher PostgreSQL (leçon P-51).

---

## 2. Matrice d'habilitation de référence

Elle est extraite du dossier des cas d'utilisation (§ 11.2) et des corrections D-44, D-264, D-265 et D-284 (la matrice fait foi sur un critère incomplet). **É** = écriture, **L** = lecture, **—** = refus.

| Domaine | `u_ped` | `u_plan` | `u_exa` | `u_df` | `u_adm` |
|---|---|---|---|---|---|
| Comptes, habilitations, journal | — | — | — | — | É |
| Référentiel | É | L | L | L | — |
| Sessions, brigades, stagiaires | É | L | L | L | — |
| Instructeurs, qualifications | É | L | — | L | — |
| Lieux, calendrier, grilles, indisponibilités | L | É | L | L | — |
| Génération et modification du programme | — | É | — | L | — |
| Validation du programme | É | L (soumettre, signer, afficher) | — | L | — |
| Évaluations : création, sujets, notes, moyennes | — | — | É | — | — |
| Procès-verbaux (consulter, télécharger) | — | — | É | L | — |
| Suivi : rapprochement, alertes, tableau de bord (consultation) | L | L | L | L | — |
| Suivi : déclaration d'une non-exécution, progression réalisée | — | É | — | — | — |

---

## 3. Habilitations croisées

Pour chaque ligne : ouvrir l'écran avec chaque profil, tenter une lecture, puis une écriture **par l'interface et par l'adresse directe**.

| Code | Écran | Attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|
| R05-HAB-01 | Gestion des comptes | Seul `u_adm` | US-ADM-02 c.5 | ☐ | |
| R05-HAB-02 | Référentiel de F6 | Conforme à la matrice | US-REF-07 | ☐ | |
| R05-HAB-03 | Stagiaires de S1 | Conforme ; `u_exa` en lecture (saisie des notes) | US-SES-07 c.4 | ☐ | |
| R05-HAB-04 | Matrice de qualification | `u_exa` refusé | matrice | ☐ | |
| R05-HAB-05 | Indisponibilités | Écriture pour `u_plan` seulement | US-INS-03 | ☐ | |
| R05-HAB-06 | Consultation du programme W0 | Conforme ; noter le comportement pour `u_exa` | D-280 | ☐ | |
| R05-HAB-07 | Saisie des notes de E1 | Seule `u_exa` | US-EVAL-05 c.6 | ☐ | |
| R05-HAB-08 | Sujets de E3 | Seule `u_exa`, **`u_df` refusée** | US-EVAL-03 c.6 | ☐ | |
| R05-HAB-09 | Rapprochement de S1 | `u_ped`, `u_plan`, `u_exa`, `u_df` ; `u_adm` refusé | US-SUI-01 c.5 | ☐ | |
| R05-HAB-10 | Avec chaque profil, examiner le menu de navigation | Chaque profil voit les rubriques auxquelles il a accès, et seulement celles-là | US-ADM-03 c.6 | ☐ | |
| R05-HAB-11 | Avec `u_df`, parcourir tous les écrans accessibles | Aucune commande d'écriture nulle part, pas même grisée | US-ADM-03 c.2 | ☐ | |
| R05-HAB-12 | Se déconnecter et appeler directement trois adresses d'écriture : générer, valider, saisir une note | Redirection vers l'authentification ; aucune action exécutée | US-ADM-03 c.6 | ☐ | |
| R05-HAB-13 | `u_adm` : modifier dans l'écran des habilitations un droit de `u_plan` (retirer la lecture du référentiel), vérifier l'effet, puis rétablir | Effet immédiat, sans modifier le code ; chaque changement est journalisé | RG-02 bis, BF-ADM-03 | ☐ | |

## 4. Journal

| Code | Contrôle | Attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|
| R05-JOU-01 | `u_adm` : vérifier les entrées des sections 3 et 5 de ce cahier | Chaque refus d'accès, chaque modification sensible : auteur et horodatage | RG-26, BNF-14 | ☐ | |
| R05-JOU-02 | Avec chaque profil, `u_adm` compris, chercher à modifier ou supprimer une entrée | Impossible pour tous | RG-27, US-ADM-04 c.4 | ☐ | |
| R05-JOU-03 | Chercher dans le journal le nom d'un stagiaire et la référence `SUJ-E3-A` | Absents : un import ou un export se journalise par un **nombre** de lignes, un sujet par son **rang** | BNF-02, données nominatives | ☐ | |
| R05-JOU-04 | Journal de W-2 | Les entrées portent les dates simulées de la chronologie (jeudi, vendredi, samedi de W-3) | JEUX-DE-DONNEES § 2.4 | ☐ | Vérifie que l'horloge simulée a laissé une histoire cohérente |

## 5. Documents imprimés et exportés

Chaque document est imprimé en aperçu. Pour chacun, on note le format naturel (portrait ou paysage), le **débordement mesuré** (en pixels, avec l'outil de mesure du navigateur) et la lisibilité.

| Code | Document | Format | Débordement | Lisible | Trace | Rés. | Obs. |
|---|---|---|---|---|---|---|---|
| R05-IMP-01 | **Programme hebdomadaire W0** (trois brigades) | | | | RG-33 bis, D-155 | ☐ | **Anomalie n° 1 connue** (R22, D-291) : déborde dès le 3ᵉ créneau. Mesurer en portrait **et** en paysage : c'est le critère de décision entre un simple passage en paysage et l'impression par journée |
| R05-IMP-02 | Liste des instructeurs | | | | K3 | ☐ | 168 px mesurés le 26/10 |
| R05-IMP-03 | Liste des lieux | | | | K3 | ☐ | |
| R05-IMP-04 | Fiche de composition de S1 | | | | D-63 | ☐ | |
| R05-IMP-05 | Liste des stagiaires de S1 | | | | US-SES-07 | ☐ | |
| R05-IMP-06 | Vue annuelle du calendrier | | | | US-PLAN-01 c.7 | ☐ | |
| R05-IMP-07 | Fiche d'une grille horaire | | | | US-PLAN-12 | ☐ | |
| R05-IMP-08 | Convocation de E3 | | | | US-EVAL-04 c.8 | ☐ | Aucune mention de sujet |
| R05-IMP-09 | [PDF] Procès-verbal d'une évaluation | | | | US-EVAL-07 c.5 | ☐ | |
| R05-IMP-10 | [PDF] Progression réalisée W-1 | | | | US-SUI-06 c.7 | ☐ | |
| R05-IMP-11 | Export CSV des stagiaires, ouvert dans un tableur | | | | US-SES-07 c.3 | ☐ | Accents corrects |

## 6. Scénario de bout en bout — une semaine de W+1, à travers les trois cellules

Il vérifie les **passages de relais** entre cellules, que les autres cahiers testent chacun de leur côté. Il se joue d'une traite, sur une base fraîchement remise à zéro (`complet`).

| Code | Étape | Profil | Attendu | Rés. | Obs. |
|---|---|---|---|---|---|
| R05-BEB-01 | Générer W+1 pour EXP1, EXP2, CDP1 | `u_plan` | Brouillon ; le contrôle E2 est conservé | ☐ | |
| R05-BEB-02 | Créer une formative M6 pour EXP1 le jeudi de W+1 | `u_exa` | Séance verrouillée insérée dans W+1 ; elle apparaît chez `u_plan` | ☐ | |
| R05-BEB-03 | Soumettre W+1 | `u_plan` | La cellule pédagogique est informée (compteur) | ☐ | |
| R05-BEB-04 | Rejeter avec motif | `u_ped` | La planification voit le motif | ☐ | |
| R05-BEB-05 | Corriger, resoumettre | `u_plan` | — | ☐ | |
| R05-BEB-06 | Valider | `u_ped` | — | ☐ | |
| R05-BEB-07 | Enregistrer la signature, afficher | `u_plan` | Affiché ; consultable par `u_df` | ☐ | |
| R05-BEB-08 | Déclarer I1 indisponible le mercredi de W+1 ; traiter ses séances | `u_plan` | Remplacements avec avenant ; W+1 reste affiché | ☐ | |
| R05-BEB-09 | Consulter le rapprochement de S1 | `u_ped` | Le programmé intègre W+1 ; le réalisé n'en tient pas encore compte (séances futures) | ☐ | |
| R05-BEB-10 | Tableau de bord | `u_df` | Cohérent avec le rapprochement | ☐ | |
| R05-BEB-11 | Journal du scénario | `u_adm` | Chaque relais apparaît dans l'ordre, avec son auteur | ☐ | |

## 7. Jeu volumineux — l'application à la taille du centre

Base `pfe_cit_volume`. Il s'agit ici d'**observer**, pas de vérifier des valeurs ligne à ligne. Les chronomètres se mesurent avec l'outil réseau du navigateur (temps de chargement de la page).

| Code | Observation | Attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|
| R05-VOL-01 | Liste des stagiaires (≈ 800), recherche, pagination | Moins de 2 s ; pagination et recherche fluides | BNF-05, BNF-15 | ☐ | Temps : ______ |
| R05-VOL-02 | Consultation du programme W0 (32 brigades) | Moins de 2 s ; lisible à l'écran | BNF-05 | ☐ | Temps : ______ |
| R05-VOL-03 | Générer W+4 pour les 32 brigades (`v_plan`) | Moins de 5 minutes ; le compte rendu reste exploitable | BNF-04 | ☐ | Temps : ______ ; non pourvues : ____ % |
| R05-VOL-04 | Compte rendu de W+1 : relever les motifs des cases non pourvues | Les motifs nomment des instructeurs ou des lieux saturés (constat du prompt 51 bis) | MESURES-REFERENCE | ☐ | Matières et instructeurs les plus touchés : ______ |
| R05-VOL-05 | Rapprochement de la plus grosse session ; tableau de bord des 32 brigades | Moins de 2 s ; tableau de bord lisible avec 32 brigades | BNF-05 | ☐ | |
| R05-VOL-06 | Charge d'un instructeur très sollicité ; comparaison de plusieurs instructeurs | Moins de 2 s ; les dépassements de seuil sont visibles | BNF-05, US-INS-04 | ☐ | |
| R05-VOL-07 | Impression du programme W0 (32 brigades) | Noter l'ampleur du débordement : elle dimensionne la correction de l'anomalie n° 1 | R22 | ☐ | |
| R05-VOL-08 | Navigation libre, chaque profil (dix minutes chacun) | Noter toute lenteur, incohérence ou écran inexploitable à cette taille | — | ☐ | |

**Réserve à écrire telle quelle au mémoire** : le jeu volumineux est calibré au plus contraint de la plage du terrain (80 instructeurs). La saturation constatée à partir de W+1 est une **propriété de ce calibrage**, et non un défaut. À 120 instructeurs, elle serait moindre ; elle n'a pas été mesurée.

## 8. Mesure de l'objectif OS5

Protocole (plan, § 9.2). **Une seule des deux branches est jouée.**

**Branche A — séance avec la cellule planification (jeudi 29/10, si elle est accordée).**

| Code | Étape | Mesure |
|---|---|---|
| R05-OS5-A1 | Semaine test choisie avec la cellule : brigades, contraintes réelles de la semaine | — |
| R05-OS5-A2 | La cellule construit la semaine avec sa méthode actuelle, chronomètre en main | Temps méthode actuelle : ______ |
| R05-OS5-A3 | Le binôme construit la même semaine avec le système : génération, ajustements, jusqu'au programme soumis | Temps système : ______ |
| R05-OS5-A4 | Comparaison | Gain : ______ % (cible OS5 : moins de deux heures ; K12 : gain d'au moins 50 %) |
| R05-OS5-A5 | Remarques de la cellule, consignées sans être intégrées (R11) | — |

**Branche B — sans séance.**

| Code | Étape | Mesure |
|---|---|---|
| R05-OS5-B1 | Sur le jeu `complet` : de la sélection des brigades de W+1 jusqu'au programme soumis, ajustements compris, par un équipier qui ne connaît pas la semaine à l'avance | Temps : ______ |
| R05-OS5-B2 | Même mesure sur le jeu volumineux (32 brigades, W+4) | Temps : ______ |
| R05-OS5-B3 | Comparaison au point de départ **déclaré** par la cellule en phase 1 : « au moins une journée » | Conclusion, avec la limite : référence déclarative, non mesurée |

## 9. Synthèse des objectifs SMART

À remplir une fois les six cahiers dépouillés. Elle alimente le prononcé de C3 et le chapitre « Tests et résultats » du mémoire.

| Objectif | Mesure prévue en phase 1 | Résultat observé | Source | Atteint ? |
|---|---|---|---|---|
| Principal | Trois cellules couvertes, besoins Must satisfaits | | Six cahiers | ☐ oui ☐ partiel ☐ non |
| OS1 — Référentiel centralisé | Formations et matières consultables, sans double saisie | | RECETTE-00, R05-HAB | ☐ ☐ ☐ |
| OS2 — Génération assistée | Programme sans violation de contrainte dure, validé avant affichage | | RECETTE-00, 01, R05-VOL | ☐ ☐ ☐ |
| OS3 — Évaluations | Notes et résultats d'une formation test, accès restreint. *Deux circuits et non trois : écart déclaré* | | RECETTE-02 | ☐ ☐ ☐ |
| OS4 — Prescrit et réalisé | Écart calculé et affiché par matière, avec alerte | | RECETTE-03 | ☐ ☐ ☐ |
| OS5 — Gain de temps | Une semaine test : système contre méthode actuelle ; cible moins de 2 h | | § 8 | ☐ ☐ ☐ |
| OS6 — Suggestion de remplaçant | Liste ordonnée | **SO** : US-PLAN-10 en réserve ; liste non ordonnée livrée (US-PLAN-09) | RECETTE-01 | ☐ SO |

---

## 10. Dépouillement

| Section | Contrôles | C | NC majeur | NC mineur | B | SO |
|---|---|---|---|---|---|---|
| 3. Habilitations | 13 | | | | | |
| 4. Journal | 4 | | | | | |
| 5. Documents | 11 | | | | | |
| 6. Bout en bout | 11 | | | | | |
| 7. Jeu volumineux | 8 | | | | | |
| **Total** | **47** | | | | | |

La section 8 (OS5) et la section 9 (synthèse) sont des mesures : elles ne se notent pas en C ou NC.

☐ Prononcée ☐ Prononcée sous réserve (rejeu le ______) ☐ Refusée

**Observations :**

## 11. Fiche d'anomalie

Modèle commun : `RECETTE-00-SOCLE.md`, § 12 (code `R05-…`).

---

*RECETTE-05 — version 1 du 28 octobre 2026. Lot WBS 6.3, 6.5 et 6.6.*
