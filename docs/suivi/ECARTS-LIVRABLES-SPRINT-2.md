# Écarts avec les livrables — sprint 2

Prompt 33, bloc E. Consolidation des écarts entre livrables de conception
(backlog produit v8, fiches de cas d'utilisation, diagramme de classes v4,
note d'implémentation v3) et ce qui a été implanté — dispersés au fil du
sprint dans `docs/suivi/DECISIONS.md`, réunis ici pour que le chef de projet
puisse les reporter en un seul passage.

| # | Livrable concerné | Ce qu'il dit | Ce qui a été implanté | Décision | Action attendue du chef de projet |
|---|---|---|---|---|---|
| 1 | Backlog v8, titre US-PLAN-03 | « Générer le programme hebdomadaire **d'une brigade** » | Le programme est **centre entier** (RG-33 bis, une instance par semaine, jamais par brigade) | D-146 | Corriger le titre du backlog |
| 2 | Backlog v8, critère 3 US-SES-04 | Ne nomme que « les trois cellules » pour la lecture de la fiche de session | Quatre profils lisent, dont la Direction de Formation (matrice § 11.2) — **récidive de D-44** | D-93 | Relecture systématique du backlog sur ce point, pas une rustine par story |
| 3 | Tableau des écarts des cas d'utilisation | Taux d'occupation mentionné | Absent des critères d'acceptation d'US-SES-04 au backlog | D-94 | Aligner critères et tableau des écarts |
| 4 | Note d'implémentation § 5.5 | Unicité de désignation de brigade **au niveau du type de formation** | Implantée **au niveau de la session** (sinon interdirait les sessions annuelles successives) | D-80 | Corriger la note d'implémentation — **et** `.claude/rules/services.md` item 7 porte encore l'ancien libellé, non corrigé après D-80 |
| 5 | Fiche CU-P3-06 | Répartition **équilibrée** | Critère 1 du backlog (remplissage **séquentiel**) retenu, l'emporte sur la fiche | D-103 | Corriger la fiche CU-P3-06 pour reprendre le critère 1 |
| 6 | Backlog v8, critère 3 US-SES-06 | Refus sur les deux plafonds (capacité salle, effectif déclaré brigade) | RG-19 (capacité) **refuse** ; effectif déclaré **avertit seulement** | D-104 | Corriger le critère 3 : deux plafonds, deux traitements distincts |
| 7 | Fiche CU-P3-05 | Enchaînement A4 (radiation) présent | **Absent des critères** du backlog d'US-SES-05 — troisième récidive du même motif (D-44, D-93) | D-96 | Relecture systématique du backlog, motif récurrent |
| 8 | Backlog v8, critère 4 US-PLAN-01 vs diagramme de classes v4 § 5.4 | Backlog : aucun chevauchement de bornes toléré pour une même session. Diagramme § 5.4 : seul le **doublon exact** est refusé, le reste avertit | Le § 5.4 appliqué — fiche et diagramme déjà cohérents entre eux, seul le backlog porte l'ancienne règle | D-127 | Corriger le critère 4 du backlog pour reprendre RG-29/E1/E3 |
| 9 | CLS-03 (diagramme de classes) | Ne porte pas l'archivage sur `GrilleHoraire` | Critère 5 US-PLAN-12 (clôturer une grille) traité par l'**archivage** (`ModeleArchivable`) — le backlog l'exige en substance | D-129 | Ajouter l'archivage à CLS-03 |
| 10 | Tableau des treize contraintes, phase 4 | Ne recense, pour les lieux, que RG-13 et RG-19 | RG-14 (salle attitrée ↔ brigade, période sécante) implantée en couche services, absente du tableau | D-89 | Corriger le tableau ; voir aussi la ligne 14 pour le compte final |
| 11 | Cahier des charges | Trois natures hors RG-26 déjà signalées (D-16/D-17) | `GENERATION_PROGRAMME` ajoutée comme quatrième nature hors RG-26 (journalisation de l'acte de génération) | D-153 | Porter au cahier des charges avec les trois autres |
| 12 | Prompt 31 § G5 | Suppose quatre profils avec `programme_lecture` | La matrice n'en accorde que **deux** (planification écrit, direction lit) — la cellule pédagogique ne peut pas lire le programme de ses propres brigades | D-154 | Arbitrage à faire par le chef de projet, pas une correction automatique |
| 13 | RG-33 bis | Affirme l'impression « par journée » comme un format de sortie déjà couvert | **Mesuré, jamais implanté cette story** : semaine entière 2319 px (aucun format ne suffit), journée seule 504 px (tiendrait) | D-155 | Programmer l'implantation « par journée » (lot d'impression, sprint 4) |
| 14 | Dossier d'architecture / note d'implémentation, compte des contraintes en couche services | Compte mouvant pendant le sprint | **Deux comptes distincts, à ne pas confondre** : catalogue général `.claude/rules/services.md` — 7 (phase 4) → 6 (D-80) → 7 (D-89) → **8 aujourd'hui** (D-127, RG-29) ; `ServiceContraintes` (US-PLAN-04) — **six contraintes dures stables**, RG-34 à RG-39, jamais modifiées en nombre depuis leur pose | D-80, D-89, D-127 (catalogue général) ; `app/planification/services/contraintes.py` (les six dures) | Reprendre le dossier d'architecture avec le compte 8 pour le catalogue général, 6 pour les contraintes dures de génération — deux listes différentes, ne pas les additionner |
| 15 | Prompt 30/31 (ordre des stories) | US-PLAN-03 (génération) puis US-PLAN-04 (contraintes), ordre naturel du backlog | **Inversé** : US-PLAN-04 avant US-PLAN-03 — CU-P5-02 est un cas d'utilisation inclus, appelé par la génération | D-134 | Aucune, déjà justifiée et assumée — à noter pour le mémoire |
| 16 | Prompt 30 § 4 | Affirme que `Lieu.mode_partage` « existe depuis US-PLAN-02 » | **Faux** — le champ n'avait jamais été posé ; report orphelin de D-53, non repris par le tableau de suivi. Ajouté sur arbitrage explicite, D-53 refermé | D-136 | Aucune sur le diagramme de classes (déjà juste, `Lieu.modePartage` y figurait) — c'est le Prompt 30 qui affirmait à tort ; à ne pas reproduire dans un futur prompt |

## Écart supplémentaire trouvé en assemblant le bloc B

**Le critère 4 d'US-REF-01 (D-23) parle de « sessions ouvertes »** bloquant
la suppression d'une formation, mais le mécanisme réel (`Session.formation`
en `PROTECT`) bloque pour **n'importe quel état de session**, ouverte ou
clôturée — assumé délibérément (perte d'historique jugée pire qu'un refus
trop large), décision D-69. Recoupe exactement R2-NRG-01 (session ouverte,
refus) et R2-NRG-02 (session clôturée, refus aussi) du cahier de recette
sprint 2 — les deux comportements sont couverts et volontaires, seul le
libellé du critère est à corriger.

## Ce que cette liste ne couvre pas

Les seize points ci-dessus plus l'écart D-23/D-69 couvrent l'intégralité des
décisions à effet sur un livrable trouvées entre D-92 et D-163
(`docs/suivi/DECISIONS.md`). Les autres décisions de cette plage sont des
choix d'implémentation internes, sans effet sur un livrable de conception.
