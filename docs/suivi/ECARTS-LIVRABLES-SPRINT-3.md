# Écarts avec les livrables — sprint 3

Prompt 34 (ETA-01, tâche 5.3.17), § 7. Les livrables de conception se
contredisent entre eux sur la machine à états du programme hebdomadaire ;
les dix arbitrages ci-dessous, rendus par le chef de projet au § 2 du
prompt et consignés dans `docs/suivi/DECISIONS.md` (D-165 à D-173), tranchent
chaque contradiction. Même gabarit que `ECARTS-LIVRABLES-SPRINT-2.md`, pour
que le chef de projet puisse les reporter en un seul passage.

| # | Livrable concerné | Ce qu'il dit | Ce qui fait foi (ETA-01) | Décision | Action attendue du chef de projet |
|---|---|---|---|---|---|
| 1 | Fiche CU-P5-11 (RG-44) | « Validé ou affiché → brouillon » | AFFICHÉ ne retombe jamais à BROUILLON ; une modification après affichage est un avenant (RG-42, récapitulatif § 11.3) | D-165 | Corriger CU-P5-11 : texte antérieur et obsolète |
| 2 | Fiche CU-P5-07 (RG-42, A4) | « Validé ou affiché » annule la validation | Seul VALIDÉ→BROUILLON existe (T9) ; AFFICHÉ n'annule jamais | D-165 | Corriger CU-P5-07 : contredit le récapitulatif RG-42 qui fait foi |
| 3 | SEQ-04 v3, commentaire « L'annulation de validation » | Reprend « validé ou affiché » | Même correction qu'aux lignes 1 et 2 | D-165 | Corriger le commentaire, qui contredit le paragraphe de SEQ-04 qui le précède |
| 4 | SEQ-02 v3 | Soumission possible depuis « brouillon ou rejeté » | On ne soumet que depuis BROUILLON (T2) ; REJETÉ repasse par BROUILLON (T6) d'abord | D-166 | Corriger SEQ-02 : REJETÉ est un état stable, pas un alias de BROUILLON |
| 5 | Backlog, US-VAL-02 c.3 | « Le rejet fait revenir à brouillon » | Le rejet fait passer à REJETÉ (T5) ; la reprise (T6) ramène à BROUILLON | D-166 | Corriger le critère 3 d'US-VAL-02 |
| 6 | Backlog, US-VAL-03 c.2, et RG-44 | Ne mentionnent pas T3, T6, T7, T9, T10 | Les dix transitions T1 à T10 sont toutes nécessaires à la machine à états | D-165, D-166, D-167, D-168, D-169 | Compléter US-VAL-03 c.2 et RG-44 avec les transitions manquantes |
| 7 | Fiche CU-P5-03, enchaînement E2 | « Faire rejeter le programme » comme issue pour un programme déjà validé | VALIDÉ→REJETÉ n'existe pas ; l'issue est l'annulation de validation (T9) | D-168 | Corriger CU-P5-03 E2 |
| 8 | Matrice § 11.2, ligne « P5 — validation » | Planification en lecture seulement sur ce domaine | La planification signe (T7) et affiche (T8) — deux actes, pas une simple lecture | D-169 | Annoter la matrice : la ligne ne couvre pas la signature/l'affichage |
| 9 | Prompt 31 § G5 / D-154 | Question laissée ouverte : la cellule pédagogique ne peut pas lire `programme_lecture` | Elle lit via `programme_validation_lecture`, déjà présent dans la matrice, jamais utilisé | D-172 | Aucune sur la matrice (déjà complète) ; mise en œuvre laissée à US-VAL-02 |
| 10 | D-140 (volume programmé, RG-39 a) | Exclut les programmes REJETÉS du volume programmé | Tous les états comptent, y compris REJETÉ ; seul le programme évalué reste exclu | D-171 | Aucune sur un livrable de conception ; correction de code à la charge d'US-VAL-03 |

## US-EVAL-01 (Prompt 35) — à la suite, numérotés à partir de 11

| # | Livrable concerné | Ce qu'il dit | Ce qui fait foi | Décision | Action attendue du chef de projet |
|---|---|---|---|---|---|
| 11 | Backlog v9, US-EVAL-01 c.1, 6, 7, 8 | Trois types d'évaluation (contrôle simple, partiel, final) | C.2 et CU-P6-01/BF-EVAL-01 n'en retiennent que deux (formative, certificative) — correction de terrain du 25 août ajoutée en v7 sans retrait des anciens critères | D-184 | Retirer les critères 1, 6, 7, 8 qui portent la troisième valeur ; aligner sur le critère 2 |
| 12 | CLS-05 (diagramme de classes) | `Evaluation.perimetre : PerimetreEvaluation`, attribut stocké en plus de `session`/`brigade` | Propriété calculée, jamais stockée (A1) — un attribut dérivé stocké en plus des deux rattachements | D-175 | Corriger CLS-05 : `perimetre` n'est pas un attribut, c'est une propriété calculée |
| 13 | CLS-05 | `Evaluation.date`, sans mention d'exclusivité avec `seance` | Exactement un des deux (A2) — `date` ne se lit que sans séance | D-176 | Annoter CLS-05 : `date` et `seance` sont mutuellement exclusifs |
| 14 | Objectifs SMART, OS3 | « Trois circuits » d'évaluation | Deux circuits (formative, certificative) — même correction que la ligne 11 | D-184 | Corriger OS3 pour reprendre deux circuits, pas trois |

**Écart de conception supplémentaire (D-174)** : ETA-01 (`docs/diagrammes/
ETA-01_etats_programme.puml`, note aux cellules) décrit T1 (création du
programme en brouillon) comme déclenchée par la planification (génération
ou saisie manuelle) seulement. Depuis US-EVAL-01, la cellule examens peut
aussi la déclencher, par l'insertion de la séance d'un contrôle dans une
semaine sans programme. Le diagramme et la note ne sont **pas** modifiés
ici : leur validation par les cellules est en cours (retour attendu le 5
octobre) — l'écart sera reporté au diagramme à leur retour, pas avant.

## US-EVAL-02 (Prompt 36) — à la suite, numérotés à partir de 15

| # | Livrable concerné | Ce qu'il dit | Ce qui fait foi | Décision | Action attendue du chef de projet |
|---|---|---|---|---|---|
| 15 | Fiche CU-P5-02 et récapitulatif, RG-38 | Ne cite que les périodes du calendrier comme source de blocage | Un jour d'examen certificatif dont le périmètre couvre la brigade est une seconde source (A3) ; les six contraintes dures restent six | D-187 | Compléter RG-38 : deux sources, période bloquante et jour d'examen certificatif |
| 16 | Tableau des treize contraintes, phase 4 | Même recensement qu'au sprint 2 (lignes 1 et 14 ci-dessus), RG-38 à une seule source | Même ajout qu'à la ligne 15 ; le compte des contraintes elles-mêmes ne bouge pas | D-187 | Ajouter la seconde source de RG-38 au tableau, sans changer le compte |

## US-EVAL-03 (Prompt 37, Temps 2) — à la suite, numérotés à partir de 17

| # | Livrable concerné | Ce qu'il dit | Ce qui fait foi | Décision | Action attendue du chef de projet |
|---|---|---|---|---|---|
| 17 | CLS-05 (diagramme de classes) | `Sujet` sans multiplicité précisée sur son association à `Evaluation` | Multiplicité « au plus deux », garantie EN BASE par le rang (A2, `ck_sujet_rang`/`uq_sujet_evaluation_rang`), pas seulement par un commentaire du diagramme | D-195 | Annoter CLS-05 : l'association `Sujet`→`Evaluation` porte la multiplicité 0..2, garantie par contrainte |
| 18 | Cahier des charges / `HABILITATIONS.md`, décompte des extensions à RG-26 | Quatre extensions recensées avant cette story (texte du prompt 37 lui-même en annonçait cinq, vérifié faux) | Cinq extensions existaient déjà (`ACCES_REFUSE`, `MODIFICATION_HABILITATIONS`, `CONSULTATION_JOURNAL`, `EXPORT_DONNEES`, `GENERATION_PROGRAMME`) ; `CONSULTATION_SUJETS` (A6) en est la SIXIÈME, pas la cinquième (D-199, vérifié dans `administration/tests/test_contenu_journal.py::EXTENSIONS_HORS_RG26`) | D-199 | Porter le décompte des extensions à RG-26 à six, pas cinq, dans le cahier des charges et `HABILITATIONS.md` |

## US-EVAL-04 (Prompt 38) — à la suite, numérotés à partir de 19

| # | Livrable concerné | Ce qu'il dit | Ce qui fait foi | Décision | Action attendue du chef de projet |
|---|---|---|---|---|---|
| 19 | Backlog v9, US-EVAL-03 c.7 | « Aucune évaluation ne peut être organisée sans sujet sélectionné » | L'épreuve s'organise sans sujet ; elle n'est PRÊTE qu'avec un sujet retenu (A1, report C9) | D-208 | Corriger le critère c.7 en v10 |
| 20 | CLS-05 | `OrganisationEpreuve.effectifAttendu` lu comme l'effectif de la brigade | C'est la part de la brigade affectée au lieu (RG-53 bis, A3) | D-214 | Annoter CLS-05 |
| 21 | CLS-05 | Créneau non précisé sur l'épreuve | `heure_debut` et `heure_fin` sur `Evaluation`, certificatives seulement (A2) | D-213 | Ajouter le créneau à CLS-05 |
| 22 | Dossier d'architecture, § disponibilité | `ServiceRessources` (P4) porte la disponibilité commune | Répartie entre primitives de `ressources`, sélecteurs publics par application et un point de résolution de `noyau` (D-210, D-211) | D-210, D-211 | Décrire la répartition telle qu'implantée |
| 23 | Tableau des contraintes de la phase 4, RG-53 | Sources « épreuve » non recensées | Ajoutées aux deux contraintes d'occupation (RG-37 lieu, RG-34 instructeur) ; compte inchangé | D-211 | Compléter le tableau sans changer le compte |
| 24 | Fiche CLS-05 § 7.5 | Personne extérieure non décrite | Surveillant en nom libre, sans contrôle de disponibilité (A7) | D-216 | Préciser § 7.5 |

## Ce que cette liste ne couvre pas

Les huit arbitrages A1 à A8 (D-165 à D-172) portent sur des contradictions
**entre livrables de conception**. A9 et A10 (D-173) n'ont aucune source à
corriger — arbitrages du chef de projet, consignés comme tels dans
`DECISIONS.md`, absents de ce tableau à dessein.

Les écarts entre le diagramme ETA-01 et le **code actuel** (garde RG-41
absente, journal incomplet, écran de lancement D-159 muet sur l'état, classe
`Avenant` non implantée et sans story assignée) ne sont pas des défauts d'un
livrable de conception : le code n'a simplement pas encore été écrit pour
ce circuit. Ils sont consignés dans `docs/conception/ETA-01_audit_code.md`,
pas ici.
