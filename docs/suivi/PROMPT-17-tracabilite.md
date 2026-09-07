# Prompt 17 — traçabilité des évolutions (blocs B, C, D)

Les blocs B, C et D ne corrigent aucun critère d'acceptation existant : ils
ajoutent des fonctions demandées à la recette manuelle du 4 septembre, après
arbitrage du chef de projet (§ 6 du prompt). Le bloc A, lui, achève une
correction déjà ouverte (contrôle D4) — il est consigné comme défaut dans
`docs/suivi/PROBLEMES.md`, pas ici.

| Évolution | Contrôle de recette | Ce qui a été fait | Temps passé |
|---|---|---|---|
| Compteurs du catalogue des matières (Formations, Instructeurs, Objectifs) | F3, G1, I8 | `ServiceMatiere._queryset` annote les trois compteurs en une requête ; badge « AUCUN » repris d'US-INS-02 sur le compteur d'instructeurs | ~35 min |
| Nombre d'instructeurs qualifiés par matière, vue consolidée du référentiel | I11 | Colonne ajoutée à `formation_consultation.html` — donnée déjà annotée par `ServiceReferentiel.lister`, aucun changement de service | ~15 min |
| Compteurs de la liste des formations (Matières, Volume prescrit) | — (symétrie demandée avec US-REF-00) | `ServiceFormation._queryset` annote `nombre_matieres`/`volume_prescrit_total` | ~20 min |
| Compteur de la liste des instructeurs (Qualifications) | — (même principe que ci-dessus) | `ServiceInstructeur._queryset` annote `nombre_qualifications` | ~15 min |
| Compteur de la liste des lieux (Indisponibilités à venir) | — (même principe) | `ServiceLieu._queryset` annote `nombre_indisponibilites_a_venir`, filtré sur les périodes non terminées | ~20 min |
| Test de non-croissance des requêtes, cinq écrans | § 2.6, exigence transverse | Un test par écran (`CaptureQueriesContext`, 5 puis 20 lignes) | ~25 min |
| Filtre « objet » du journal en liste déroulante | D4 | `ServiceJournal.objet_types_disponibles()` — valeurs réellement présentes dans le journal, jamais une nomenclature figée (voir note ci-dessous) | ~25 min |
| Mention « sans objet » sur les colonnes valeur avant/après vides | D4 | Gabarit `journal.html`, remplacement du tiret par défaut | ~5 min |
| Modification d'une indisponibilité de lieu | remarque du parcours J | `ServiceIndisponibiliteLieu.modifier`, factorisé avec `declarer` ; piège du chevauchement avec soi-même couvert par un test dédié | ~40 min |

**Temps total, session du 2026-09-07** : environ 4 h (hors bloc A, environ 1 h
30, consigné séparément).

## § 2.2 — l'écran de couverture existait-il ?

Oui, mais pas au bon endroit : `ressources:couverture_qualifications`
(lié depuis l'écran de **composition** du référentiel, `formation_referentiel.html`)
affichait déjà le compteur, avec la même donnée annotée
(`ElementReferentiel.nombre_instructeurs_qualifies`). La « vue consolidée »
visée par le contrôle I11 est un écran distinct, `formation_consultation.html`
(US-REF-07, lecture seule, accessible aux cellules qui ne composent pas le
référentiel) — elle n'affichait pas le compteur. Traité comme l'ajout d'une
colonne à un écran existant, pas comme la création d'un nouvel écran : aucune
donnée nouvelle à calculer, seule la donnée déjà annotée par
`ServiceReferentiel.lister` restait invisible sur cet écran-là.

## § 2.7 — effet des nouvelles colonnes sur l'impression (contrôle K3)

Aucun. Vérifié par recherche (`print:`, `@media print`) : aucune règle
d'impression n'existe encore nulle part dans le dépôt — le contrôle K3 porte
sur un écran qui n'est pas construit avant le sprint 2/3 (progression
d'instruction, planification). Les cinq écrans modifiés par le bloc B
(matières, formations, instructeurs, lieux, vue consolidée du référentiel) ne
sont concernés ni par K3 ni par une feuille d'impression existante.

## Note — écart avec l'énoncé du prompt, § 3.1

Le prompt cite six types d'objet à titre d'exemple, dont « compte ». La
valeur réellement enregistrée par le journal pour un compte est
`objet_type="utilisateur"` (`administration/services/journal_comptes.py`),
jamais `"compte"` — c'est ce terme, correctement libellé « Compte » dans la
liste déroulante, qui a été retenu. La liste déroulante elle-même n'est pas
la nomenclature à six valeurs de l'énoncé : elle affiche les valeurs
**réellement présentes** dans le journal à l'instant de la consultation
(`ServiceJournal.objet_types_disponibles()`, `EntreeJournal.objects.exclude(
objet_type="").distinct()`), aujourd'hui dix valeurs distinctes (types de
formation, formations, matières, objectifs pédagogiques, prérequis,
instructeurs, lieux, indisponibilités de lieu, qualifications, comptes) — une
nomenclature figée aurait fini par diverger des services qui posent
`OBJET_TYPE`, qu'`administration` ne peut de toute façon pas importer (ordre
des dépendances).
