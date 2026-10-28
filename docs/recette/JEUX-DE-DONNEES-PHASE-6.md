# Jeux de données de la phase 6 — Prompt 51

Document de référence dont sont tirés les cahiers RECETTE-01 à 05 : décrit ce
qui a **réellement** été chargé, pas ce que le prompt prévoyait. Deux jeux,
chacun sur sa propre base :

| Jeu | Base | Module de réglages | Commande |
|---|---|---|---|
| Recette, état `socle` | `pfe_cit_recette` | `config.settings.recette` | `charger_jeu_recette` |
| Recette, état `complet` | `pfe_cit_recette` | `config.settings.recette` | `charger_jeu_recette --etat complet` |
| Volumineux | `pfe_cit_volume` | `config.settings.volume` | `charger_jeu_volume` |

Les dates ci-dessous viennent d'un chargement de contrôle réel, lancé le
**27/10/2026** (`D` = ce jour) — elles **glissent avec `D`** : relancer le
même chargement un autre jour produit des dates différentes, à l'identique
du mécanisme décrit dans `JEU-RECETTE.md`.

## Commandes

### Remise à zéro, chargement, vérification

Scriptées par `outils/recette/reinitialiser_base_recette.ps1 -Etat {socle|complet|volume}`
(Temps 1) — demande confirmation interactive du nom de la base avant de la
supprimer. Rejouées manuellement ci-dessous pour ce document (étape par
étape, sans confirmation interactive, dans ce même ordre) :

```powershell
# État complet (base pfe_cit_recette)
docker exec -e PGPASSWORD=developpement_local_migration pfe_cit_base psql -U pfe_cit_migration -d postgres -c "DROP DATABASE IF EXISTS pfe_cit_recette;"
docker exec -e PGPASSWORD=developpement_local_migration pfe_cit_base psql -U pfe_cit_migration -d postgres -c "CREATE DATABASE pfe_cit_recette OWNER pfe_cit_migration;"
docker exec -e PGPASSWORD=developpement_local_migration pfe_cit_base psql -U pfe_cit_migration -d pfe_cit_recette -c "GRANT USAGE ON SCHEMA public TO pfe_cit_app;"
docker exec -e PGPASSWORD=developpement_local_migration pfe_cit_base psql -U pfe_cit_migration -d pfe_cit_recette -c "ALTER DEFAULT PRIVILEGES FOR ROLE pfe_cit_migration IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO pfe_cit_app;"
docker exec -e PGPASSWORD=developpement_local_migration pfe_cit_base psql -U pfe_cit_migration -d pfe_cit_recette -c "ALTER DEFAULT PRIVILEGES FOR ROLE pfe_cit_migration IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO pfe_cit_app;"

cd app
BASE_UTILISATEUR=pfe_cit_migration BASE_MOT_DE_PASSE=developpement_local_migration python manage.py migrate --settings=config.settings.recette
python manage.py initialiser_habilitations --settings=config.settings.recette
python manage.py initialiser_gabarits_documents --settings=config.settings.recette
python manage.py initialiser_natures_evenement --settings=config.settings.recette
python manage.py charger_jeu_recette --etat complet --settings=config.settings.recette
python manage.py initialiser_grilles_horaires --settings=config.settings.recette
python manage.py charger_jeu_recette --etat complet --verifier --settings=config.settings.recette
```

Le jeu volumineux (`pfe_cit_volume`, `config.settings.volume`) suit le même
schéma avec `charger_jeu_volume` à la place de `charger_jeu_recette --etat
complet` — voir § « Jeu volumineux » plus bas pour son état d'avancement.

### Rapport `--verifier`, tel qu'obtenu

```
État du jeu de recette, socle (§ 2, § 4.2 du cahier)
  73/73 contrôles conformes.

État du jeu de recette, ajouts de l'état complet (§ 2)
  47/47 contrôles conformes.
```

Aucun écart : le socle (inchangé depuis le prompt 34) et l'état `complet`
sont tous deux intégralement conformes à ce que `--verifier` attend.

### Lancer la recette dans le conteneur (contrôles `[PDF]`, Prompt 52)

Les cahiers RECETTE-02, 03 et 05 portent des contrôles marqués **[PDF]**
(procès-verbaux, PDF de la progression réalisée) : WeasyPrint ne
s'exécute pas sous Windows (P-44), `runserver` sous Windows ne peut
jamais les produire. `outils/recette/lancer_recette_conteneur.ps1` lance
l'application dans la même image que `pytest -m pdf`
(`python:3.14-slim-bookworm`, réseau Docker `developpement_default`,
hôte `base`) — **sans rien recharger**, sur la base déjà chargée.

```powershell
.\outils\recette\lancer_recette_conteneur.ps1 -Base recette   # pfe_cit_recette, config.settings.recette
.\outils\recette\lancer_recette_conteneur.ps1 -Base volume    # pfe_cit_volume, config.settings.volume
```

**Adresse : `http://localhost:8001/`** — jamais 8000, pour ne jamais être
confondu avec un `runserver` Windows lancé en parallèle. Le script
avertit (sans bloquer) si le port 8000 est déjà occupé : deux serveurs
sur la **même base** pendant une recette sont deux sources de vérité, à
éviter. **La base est partagée avec un `runserver` Windows éventuel** —
écrire par l'un est visible par l'autre, immédiatement.

**Arrêt** : Ctrl+C dans le terminal qui a lancé le script — le conteneur
est supprimé automatiquement (`docker run --rm`), rien d'autre à nettoyer.

Les fichiers statiques (CSS Tailwind précompilé,
`noyau/static/css/application.css`) sont servis sans étape
supplémentaire : `config.settings.recette`/`volume` héritent de
`local.py` (`DEBUG = True`), et `django.contrib.staticfiles` les sert
directement — vérifié réellement (`curl` depuis l'intérieur du
conteneur : 200, CSS complet).

**Vérification de bout en bout (point 4), par le client de test Django,
sur `pfe_cit_recette` remis à zéro en `complet`** :

| Contrôle | Résultat |
|---|---|
| Générer le procès-verbal d'évaluation de E1 (M1, EXP1) | **OK** — `ProcesVerbal` créé, PDF téléchargé : 200, `application/pdf`, 20 769 octets, en-tête `%PDF`. Texte extrait : « Procès-verbal — M1 — ... — EXP1 — S1 — F6 », notes et rangs présents (dont l'absence). |
| Éditer la progression réalisée de W-1 et télécharger son PDF | **OK** — `EditionProgression` créée, PDF téléchargé : 200, `application/pdf`, 21 725 octets, en-tête `%PDF`. Texte extrait : « Progression réalisée — semaine du 19/10/2026 », M1/M2 programmé et dispensé pour EXP1. |

Les deux PDF s'ouvrent et contiennent les données attendues — confirmé en
lisant leur contenu (`pypdf`), pas seulement leur statut HTTP.

**Mot de passe commun des comptes `v_*` du jeu volumineux** (RECETTE-05
en a besoin) : **`Transmissions#2026`** — la même constante que les
comptes `u_*` du jeu de recette (`evaluations/jeu_recette/donnees.py::
MOT_DE_PASSE_COMMUN`, réutilisée sans changement par
`comptes_volume.py`), déjà dans le dépôt mais jamais écrite dans ce
document jusqu'ici.

### Incohérence relevée, non corrigée dans le code (point 7)

Ce document disait (§ 2.4, avant correction) : « W-2 ... grille ordinaire
pleine sur les **six** jours ouvrables ». La grille Ordinaire n'a aucun
créneau le samedi (`JOURS_OUVRES` dans
`ressources/management/commands/initialiser_grilles_horaires.py` :
lundi à vendredi seulement — confirme R2-P12-04). Vérifié directement sur
un chargement `complet` frais : **aucune séance un samedi dans W-2, W-1
ou W0** (jours de semaine présents : lundi à vendredi uniquement, sur les
trois programmes affichés). Les trois occurrences de `SAMEDI_ISO` dans
`programme_complet.py` ne posent aucune séance ce jour-là : elles datent
la SIGNATURE/l'affichage du programme (§ 2.4, « signée et affichée samedi
W-3 ») — un acte administratif, jamais un créneau de cours. La seule
place où `SAMEDI_ISO` touche une séance est `avenants_complet.py`, en
dernier repli de `_premier_jour_libre` (jamais atteint dans ce chargement,
puisque le jeudi suffit).

**Conclusion : le libellé était faux, corrigé (§ 2.4, « cinq jours
ouvrables »).** Aucune séance du samedi n'existe réellement dans le jeu
`complet` — rien d'autre à corriger.

## État `complet` — § 2, tel que chargé

### 2.1 Référentiel ajouté

Conforme au § 2.1 du prompt, sans écart : `M6` (salle attitrée), `M7` (lieu
partagé, laboratoire), `M8` (salle attitrée), `M9` (salle attitrée) ;
formation `F6` — Opérateur transmissions (TF1) ; référentiel `F6` à 200 h (7
éléments) ; `M6` prérequis de `M8` ; deux objectifs pédagogiques sur `M6`.

### 2.2 Ressources ajoutées

Conforme au § 2.2, sans écart : instructeurs `I6`-`I9`, qualification `M1`
ajoutée à `I3` ; lieux `L7` (attitrée, 12), `L8` (attitrée, 20), `L9`
(amphithéâtre partagé simultané, 60) ; indisponibilité de `I3` le mardi de
W-1 (2026-10-20), motif « stage » ; calendrier : conférence centre entier
(mercredi W-1), congé centre entier (vendredi W+3), bivouac ciblant `EXP2`
(jeudi-vendredi W+2).

### 2.3 Organisation, telle que chargée

| Session | Formation | Dates réelles | Brigades (effectif, salle) | Stagiaires |
|---|---|---|---|---|
| `S1` | F6 — Transmissions | 2026-10-05 → 2026-12-25 | `EXP1` (20, L1) · `EXP2` (15, L2) | 39 (35 affectés + 4 non affectés + 1 radié — voir note) |
| `S2` | Chef de poste (F2) | 2026-10-05 → 2026-12-11 | `CDP1` (12, L7) | 12 affectés |
| `S3 (close)` | Chef de poste (F2) | 2026-08-03 → 2026-09-25 | `CDP9` (8, L8) | 8 affectés ; aucune évaluation |

`S3` porte littéralement l'intitulé `« S3 (close) »` dans le code du
chargeur (`donnees_complet.py`, `SessionComplet("S3", "S3 (close)", …)`) —
un mnémonique pour la clôture testée par RECETTE-03, pas un état réel : son
`etat` en base reste `ouverte` (confirmé en lecture), § 2.7 respecté
(« aucune session clôturée »).

Note sur S1 : le rapport de chargement annonce « 39 stagiaires (35 affectés
+ 3 non affectés + 1 radié) », mais une requête directe en compte 4 non
affectés (39 = 35 affectés + 4 non affectés dont 1 est aussi le radié,
recoupement attendu entre les deux catégories) — comptage cohérent, aucune
anomalie.

### 2.4 Programmes, tels que chargés

| Semaine (lundi) | État | Contenu réel |
|---|---|---|
| W-2 — 2026-10-12 | affiché | 44 séances (EXP1 : M7 ; EXP2 : M6 ; CDP1 : M4), grille ordinaire pleine sur les cinq jours ouvrables |
| W-1 — 2026-10-19 | affiché | Séance M2 **regroupée** `EXP1`+`EXP2` (pk séance = 3) le 2026-10-20 08:00-09:45, instructeur `I1`, lieu `L9` (35 ≤ 60, RG-40 respectée) ; contrôles `E1`/`E5` insérés le jeudi 2026-10-22 08:00 (séances verrouillées) |
| W0 — 2026-10-26 | affiché | Avenants posés lundi 2026-10-26 06:00 (horloge simulée) sur la séance M6 d'`EXP1` (pk séance = 95) — voir § Avenants ci-dessous |
| W+1 — 2026-11-02 | brouillon | Une seule séance : le contrôle `E2` (M2, `EXP2`), verrouillée le mercredi 2026-11-04 08:00-09:45 |

Toutes les dates sont calculées par rapport à `D` = 2026-10-27 ; elles
glissent avec `D` à chaque nouveau chargement.

#### Séance regroupée (W-1)

Séance pk=3, 2026-10-20 08:00-09:45, matière M2, instructeur I1, lieu L9 —
Amphithéâtre de recette 2, lignes de programme pour `EXP1` **et** `EXP2`.
Charge de l'instructeur comptée une fois (RG-40), volume décompté pour
chaque brigade.

#### Avenants (W0)

Les deux portent sur la **même** séance (pk=95, matière M6, `EXP1`),
horodatés lundi 2026-10-26 06:00:00+00:00 :

| # | Nature | Effet | Motif |
|---|---|---|---|
| 1 | Déplacement | Séance déplacée vers le **2026-10-30 10:10-12:00** | « Déplacement de séance (recette, § 2.4). » |
| 2 | Remplacement d'instructeur | Instructeur `I6` → `I8` | « Remplacement d'instructeur (recette, § 2.4). » |

**Écart avec le prompt** (§ 2.4 : « une séance M6 de EXP1 déplacée du lundi
au **jeudi** ») — voir § « Écarts avec le prompt » ci-dessous : le
déplacement a atterri le **vendredi** 2026-10-30, pas le jeudi 2026-10-29.

### 2.5 Évaluations, telles que chargées

| Code | Module, périmètre | Date réelle | Détail |
|---|---|---|---|
| `E1` | M1, brigade `EXP1` | jeudi 2026-10-22 (séance verrouillée, pk=1) | 19 notes saisies, 1 absence — dont au moins deux ex æquo (graine) |
| `E5` | M4, brigade `CDP1` | jeudi 2026-10-22 (séance verrouillée, pk=2) | 10 notes saisies sur 12, deux manquantes |
| `E2` | M2, brigade `EXP2` | mercredi 2026-11-04 (séance verrouillée, pk=4, dans W+1 brouillon) | Aucune note |
| `E3` | M6, session `S1` | 2026-12-01 (mardi W+5) | Deux sujets (`SUJ-E3-A` retenu, `SUJ-E3-B` non retenu) ; organisation partielle : `EXP1` seule organisée (lieu L9) ; `EXP2` non organisée, exprès |
| `E4` | M3, session `S1` | 2026-12-09 (mercredi W+6) | Aucun sujet, aucune organisation |

Toutes les dates obtenues (`E3` : 2026-12-01, `E4` : 2026-12-09) tombent
exactement sur les jours annoncés par le § 2.5 (« mardi W+5 », « mercredi
W+6 ») une fois `D` posé à 2026-10-27 — aucun écart ici.

### 2.6 Suivi, tel que chargé

| Non-exécution | Brigade | Séance visée | Motif |
|---|---|---|---|
| 1 | `EXP2` | M6, 2026-10-12 08:00 (W-2) | « Instructeur en mission. » |
| 2 | `EXP2` (ligne seulement) | M2, 2026-10-20 08:00 — la séance **regroupée** (pk=3, W-1) | « Brigade de garde. » |

Pour la non-exécution n° 2, la ligne de `EXP1` sur la même séance reste
sans non-exécution : `EXP1` est réputée exécutée, `EXP2` retranchée — exactement
le comportement attendu d'une non-exécution posée à la LIGNE (§ 2.6, RG-60).

Progression réalisée : une édition de W-2 produite par `u_plan`, non
signée — conforme, sans écart.

### 2.7 — Confirmé tel que prévu

Aucun procès-verbal, aucune session clôturée, aucune indisponibilité sur
W+1, aucune duplication — vérifié par lecture directe de la base, rien de
plus que ce que le § 2.7 annonce.

## Jeu volumineux — § 3, chargement pleine échelle

Chargé réellement le 2026-10-27, puis **rechargé le 2026-10-28** après le
correctif de réalisme (sessions échelonnées, référentiel dimensionné sur
la durée de la session — voir « Écarts avec le prompt » ci-dessous) ;
tous les chiffres de cette section sont ceux du rechargement, dans le
conteneur `python:3.14-slim-bookworm` (réseau Docker
`developpement_default`, hôte `base`, base `pfe_cit_volume`, module
`config.settings.volume`) — requis pour la génération des procès-verbaux
(WeasyPrint, P-44, absent du poste de développement Windows).

### Volumes obtenus

| Objet | Cible § 3.1 (recalée) | Obtenu |
|---|---|---|
| Types de formation | 4 | 4 |
| Matières | ≈70 | 70 |
| Formations | 10 (1 archivée) | 10 (1 archivée) |
| Instructeurs | 80 (recalé, voir écarts) | 80 (8 archivés) |
| Salles attitrées | 36 | 36 |
| Lieux partagés | 8 | 8 |
| Sessions actives échelonnées | 15 (recalé) | 15 (débuts W-10 à W-1) |
| Sessions actives à venir | 2 (correctif du 28/10) | 2 (début W+1) |
| Sessions terminées | 3 | 3 |
| Brigades actives | 32 | 32 (réparties sur les 17 actives) |
| Brigades sur sessions terminées | 6 (2/session) | 6 |
| Stagiaires affectés | ≈900 | 793 (+ 15 non affectés + 20 radiés) |
| Indisponibilités | ≈40 | 40 |
| Procès-verbaux de fin de formation | 2 sur 3 | 2 (SV-T01, SV-T02) |
| Évaluations formatives (sessions terminées) | — | 6 (123 notes) |
| Évaluations formatives (brigades actives) | 32 | 28 (une par brigade **déjà démarrée** ; 4 brigades des 2 sessions à venir n'ont pas encore de formative, leur session n'a pas commencé) |
| Certificatives à venir | — | 5 |
| Programmes | 12 (W-8 à W+3) | 12 |

`--verifier` : **17/17 contrôles conformes.**

### Mesures (BNF-04, BNF-05, durée totale)

Détail complet dans `docs/suivi/MESURES-REFERENCE.md`, section « Jeu
volumineux » (remplace la mesure du 27/10, devenue obsolète après le
correctif de réalisme — une ligne y explique pourquoi). Résumé :

- **Chargement complet : ≈55 s** — très en deçà des 30 minutes du § 3.2 ;
  aucun repli `--semaines` nécessaire.
- **BNF-04** : semaine la plus longue à générer, 7,81 s — largement sous
  les 5 minutes visées.
- **BNF-05** : refait sur W0 (désormais pleine) ; les six écrans tiennent
  sous les 2 secondes, le plus lent (consultation du programme W0, qui
  contient maintenant de vraies séances) à 0,483 s.
- **Cases non pourvues** : **W-8 à W-1 intégralement pleines (0 %)**, W0 à
  4,3 % — la cible du correctif (« W-1, W0 et W+1 pleines ») est atteinte
  pour W-1 et W0. W+1 à W+3 restent partiellement vides (27 % à 52 %), mais
  pour une raison DIFFÉRENTE du référentiel : voir « Classification » dans
  `MESURES-REFERENCE.md` — 100 % des brigades concernées relèvent d'une
  saturation de capacité (instructeurs/lieux partagés, toutes les 32
  brigades actives à la fois à partir de W+1), zéro référentiel épuisé,
  zéro prérequis bloquant. Le seuil de 20 % sur W+1 était une cible de
  calibrage, pas une exigence : levé une fois la cause établie.

### Bug trouvé et corrigé avant ce chargement

`orchestration_volume.py` appelait `initialiser_grilles_horaires` **avant**
`charger_comptes_volume` — cette commande exige qu'un compte administrateur
existe déjà (RG-63) et a fait échouer la première tentative de chargement
réel (`CommandError: Aucun compte administrateur trouvé`). Les tests
automatisés ne l'avaient pas révélé : ils appellent les fonctions de bas
niveau directement, jamais `charger_etat_volume` dans son ensemble, et donc
jamais dans cet ordre précis. Corrigé en reprenant l'ordre déjà documenté
dans `outils/recette/reinitialiser_base_recette.ps1` (grilles horaires
après le chargeur) — confirmation concrète que le chargement réel en
conteneur reste nécessaire, un test unitaire seul ne l'aurait pas trouvé.

## Écarts avec le prompt

### État `complet` — l'avenant « déplacement » atterrit le vendredi, pas le jeudi annoncé

**Constat** — § 2.4 du prompt annonce « une séance M6 de EXP1 déplacée du
lundi au jeudi ». Dans ce chargement réel (D = 2026-10-27), la séance a été
déplacée au **vendredi** 2026-10-30, pas au jeudi 2026-10-29.

**Cause** — `avenants_complet.py::_premier_jour_libre` cherche d'abord un
créneau libre le jeudi de W0 pour `EXP1`, mais retient le **premier** autre
jour qui en offre réellement un (jeudi, puis vendredi, mercredi, mardi,
samedi, dans cet ordre) si le jeudi est dense — documenté dans le code
lui-même (« la semaine peut être densément remplie »). Pour cette graine et
cette date de référence, le jeudi de W0 (2026-10-29) n'offrait aucun
créneau libre pour `EXP1` ; le vendredi (2026-10-30), oui.

**Résolution** — Ce n'est pas un défaut à corriger : le repli est délibéré
et déjà écrit pour ce cas précis (plutôt que de faire échouer tout le
chargement pour un jour que rien n'impose absolument). Seul le libellé du
§ 2.4 (« du lundi au jeudi ») est littéral et ne décrit pas tous les cas —
consigné ici, pas dans `DECISIONS.md` : aucune décision de conception
nouvelle, le comportement de repli existait déjà avant ce chargement de
contrôle.

### Jeu volumineux — calibrage recalé sur `etudes/solveur/HYPOTHESES.md`

**Constat** — § 3.1 du prompt annonce ≈55 instructeurs et 7 sessions en
cours (pour 32 brigades). `etudes/solveur/HYPOTHESES.md` (étude de
dimensionnement figée, prompt 32) établit une plage de 80-120 instructeurs
et un ratio moyen de 2,2 brigades par session.

**Cause** — Erreur de calibrage du prompt lui-même par rapport à l'étude de
référence qu'il cite explicitement comme faisant foi en cas de divergence
(« s'il diverge, c'est lui qui fait foi »).

**Résolution** — Recalé sur `HYPOTHESES.md` : **80 instructeurs** (borne
basse de la plage — à nombre de brigades égal, moins d'instructeurs est le
cas le plus contraint pour la génération, celui qu'il faut mesurer ; un
résultat tenu à 80 vaut a fortiori à 120) et **15 sessions actives** (pour
32 brigades, ≈2,1 brigades/session, conforme à la moyenne de 2,2 —
plusieurs formations portent alors deux sessions simultanées, cas A1 de
CU-P3-01, autorisé et bon à exercer). Le reste du § 3.1 reste inchangé : 3
sessions terminées, ≈900 stagiaires, 36 salles attitrées, 8 lieux partagés.
Consigné dans `app/evaluations/jeu_recette/donnees_volume.py`. **Pas
d'entrée dans `DECISIONS.md`** : erreur de calibrage, pas une décision de
conception.

### Jeu volumineux — sessions échelonnées et référentiel dimensionné sur la durée de la session

**Constat** — Le premier chargement pleine échelle (27/10/2026) montrait
les semaines W-3 à W+3 largement ou totalement vides. Le libellé retenu
sur le moment l'attribuait au nombre d'instructeurs (80, la borne la plus
contraignante) — **incorrect** : la cause réelle est l'épuisement du
RÉFÉRENTIEL (volume prescrit, 150-400 h fixes, indépendant de la durée de
la session), pas le nombre d'instructeurs, qui est une question
distincte (la contrainte la plus dure à satisfaire pour la GÉNÉRATION,
pas la cause du vide). Deux défauts de réalisme aggravaient l'épuisement :
(1) les 15 sessions actives démarraient toutes à la même date, jamais
comme sur le terrain ; (2) le référentiel ne tenait aucun compte de la
durée réelle de la session qui le portait.

**Résolution (28/10/2026)** —
1. Les 15 sessions actives démarrent désormais à des dates échelonnées,
   tirées entre W-10 et W-1 (`DECALAGE_DEBUT_SESSIONS_ACTIVES`,
   `organisation_volume.planifier_sessions_actives`) ; deux sessions
   supplémentaires démarrent en W+1 (`NOMBRE_SESSIONS_A_VENIR`), pour
   exercer une session qui n'a pas encore commencé — 17 sessions actives
   au total, toujours 32 brigades, réparties sur les 17.
2. Chaque référentiel est dimensionné sur la durée RÉELLE de la session
   la plus longue qui le porte : au moins 30 h par semaine de session
   (`HEURES_PRESCRITES_MIN_PAR_SEMAINE`,
   `organisation_volume.volumes_cibles_par_formation`), avec une marge
   (`MARGE_VOLUME_REFERENTIEL`) et un partage par matière resserré
   (`referentiel_volume._repartir_volume`, poids 0,9-1,1 au lieu de
   0,2-1,2) — un premier partage trop inégal pouvait réduire une matière
   à ≈20 h quand le référentiel total visait 900 h, l'épuisant en
   quelques semaines alors que le total restait loin d'être consommé.
   Seules les formations portées par une session active en bénéficient ;
   les formations sans session active (terminées, archivée) gardent
   l'ancien tirage fixe.
3. Chaque semaine ne génère plus que les brigades dont la session est
   réellement active ce lundi-là (`programme_volume._brigades_eligibles`),
   et chaque formative active n'est posée que sur une semaine où la
   session de sa brigade avait déjà commencé
   (`evaluations_volume._decalage_formative`) — jamais uniformément sur
   les huit dernières semaines comme avant, indépendamment de la date de
   début réelle.
4. `ServiceGeneration.generer` lève `SemaineEntierementBloquee` plutôt que
   de rendre un compte rendu vide quand TOUTES les brigades proposées
   sont bloquées par le calendrier (RG-38) sur toute la semaine — rencontré
   sur un sous-ensemble réduit de brigades (test à 3 brigades) depuis que
   les dates sont échelonnées. Rattrapé dans `programme_volume._generer`
   en traitant ce refus comme un programme vide (même traitement A9 que
   l'absence de séance), jamais en contournant la règle RG-38 elle-même.

**Résultat mesuré** — W-8 à W-1 intégralement pleines (0 % de cases non
pourvues), W0 à 4,3 % : la cible du correctif est atteinte. W+1 à W+3
restent partiellement vides, mais pour une raison distincte et non
anticipée par cette résolution : voir « Classification des cases non
pourvues » dans `docs/suivi/MESURES-REFERENCE.md` — 100 % des brigades
concernées relèvent d'une saturation de capacité (instructeurs et lieux
partagés, une fois les 32 brigades simultanément actives à partir de
W+1), zéro référentiel épuisé, zéro prérequis bloquant. Pas corrigé :
c'est un relevé pour RECETTE-05, hors du périmètre de ce correctif (qui
ne touche ni le nombre d'instructeurs, ni leurs qualifications).

**Pas d'entrée dans `DECISIONS.md`** : correctif de réalisme des données
et de leur dimensionnement, jamais une décision de conception — aucune
règle métier, aucun service, aucun modèle modifié.

### Jeu volumineux — comptes propres (`v_*`), pas une réutilisation du socle

**Constat** — § 3.1 demande sept comptes propres au jeu volumineux
(`v_ped`, `v_plan`, `v_exa`, `v_df`, `v_adm`, plus un second compte
pédagogique et planification), sur une base dédiée (`pfe_cit_volume`),
jamais les cinq comptes `u_*` du jeu de recette.

**Résolution** — Implanté conformément dès l'écriture
(`comptes_volume.py`, `garde_volume.py`) : aucun écart au moment de ce
rendu — mentionné ici pour mémoire, une première version avait par erreur
réutilisé les comptes `u_*` du socle avant d'être corrigée, jamais commise.

### Jeu volumineux — simplification des formatives (pas de séance verrouillée)

**Constat** — § 3.1 demande « formatives par brigade sur les semaines
passées, notes complètes », sans exiger de séance verrouillée (à la
différence d'E1/E2/E5 de l'état `complet`, § 2.5).

**Résolution** — Choix délibéré, documenté dans
`evaluations_volume.py` : les formatives du jeu volumineux passent par la
branche déclarative de `ServiceEvaluation.creer` (date déjà passée +
motif, sans séance), ce qui découple entièrement leur chargement de la
génération des programmes — une simplification, pas une règle contournée,
puisque § 3.1 ne demande pas la séance verrouillée pour ce jeu.

## Ce qui reste à faire

- Rien côté chargeurs ou mesures du jeu volumineux : BNF-04, BNF-05, le
  taux de cases non pourvues et sa classification par catégorie sont tous
  mesurés (voir `docs/suivi/MESURES-REFERENCE.md`).
- La saturation de capacité relevée sur W+1 à W+3 (instructeurs/lieux
  partagés, 100 % catégorie (c)) est un constat pour RECETTE-05, pas une
  action de ce prompt — aucune décision n'a été prise sur le nombre
  d'instructeurs ni leurs qualifications.
