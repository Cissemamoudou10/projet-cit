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
