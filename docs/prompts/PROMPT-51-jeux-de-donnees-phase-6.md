# Prompt 51 — Jeux de données de la phase 6 : état `complet` et jeu volumineux

**Nature.** Outillage de recette. **Aucune règle métier n'est modifiée.** Tu écris des chargeurs de données, des scripts, des tests de chargeurs et une documentation. Si une étape semble exiger de changer un service, un modèle ou une vue, **arrête-toi et signale-le** : la recette doit porter sur le code tel qu'il est au J3.

**Contexte.** La phase 6 (recette) va du 26/10 au jalon C3 du 02/11. Le plan de tests (`docs/recette/PLAN-DE-TESTS-PHASE-6.md`, fourni avec ce prompt) découpe la recette en six cahiers indépendants, qui reposent sur trois jeux de données, chacun sur **sa propre base** :

| Jeu | Base | État |
|---|---|---|
| Recette, état `socle` | `pfe_cit_recette` | Existe déjà : `charger_jeu_recette` (prompt 34, `docs/recette/JEU-RECETTE.md`) |
| Recette, état `complet` | `pfe_cit_recette` | **À créer** (Temps 2) |
| Volumineux | `pfe_cit_volume` | **À créer** (Temps 3) |

Dépose d'abord dans `docs/recette/` les deux fichiers fournis par l'étudiant : `PLAN-DE-TESTS-PHASE-6.md` et `RECETTE-00-SOCLE.md`. S'ils sont absents, arrête-toi et demande-les.

---

## Règles communes aux deux chargeurs — à lire avant d'écrire une ligne

1. **Tout passe par les services**, jamais par `Model.objects.create` ni par du SQL brut, pour tout objet qui porte une règle : sessions, brigades, affectations, salles attitrées, génération, transitions du circuit, signature, évaluations, sujets, organisation, notes, procès-verbaux, non-exécutions, avenants, regroupements, indisponibilités. Un jeu de données qui contourne une règle produit un état que l'application ne peut pas atteindre, et la recette vérifierait alors une fiction. Le chargement en masse direct n'est permis que pour les objets **sans règle au-delà des contraintes de base** (stagiaires en volume, objectifs pédagogiques), et seulement s'il passe les mêmes validations de modèle (`full_clean`).
2. **Si un service refuse une opération du plan de chargement, ne la contourne pas.** Arrête le chargement, rapporte le refus avec son message, et propose une donnée conforme. Un refus pendant le chargement est une information, parfois une anomalie de recette avant l'heure.
3. **Dates relatives.** Tout est daté par rapport à une date de référence `D`, par défaut le jour du chargement (option `--date-reference AAAA-MM-JJ`). `W0` = semaine (lundi) qui contient `D` ; `W-1`, `W+1`, etc.
4. **Le passé s'obtient par une horloge simulée, jamais en contournant une garde.** Plusieurs services refusent légitimement d'agir dans le passé : générer une semaine échue, déclarer une évaluation à une date passée hors exception, signer à une date future, etc. Pour fabriquer des semaines passées affichées, le chargeur **déplace l'horloge** (`timezone.now`/`localdate`, par exemple avec `freezegun` en dépendance de **développement uniquement**, ou un mécanisme équivalent déjà présent dans le dépôt) au moment où chaque étape aurait eu lieu dans la vie réelle : générer W-2 le jeudi de W-3, la valider le vendredi, la signer et l'afficher le samedi, etc. Les entrées du journal porteront ces dates : c'est voulu, cela reproduit une histoire plausible. Documente le mécanisme. Si l'horloge simulée ne suffit pas pour une étape, arrête-toi et signale-le.
5. **Déterminisme.** Une graine fixe (option `--graine`, défaut 2026). Deux chargements avec la même date et la même graine produisent le même contenu, au même identifiant métier près.
6. **Garde-fous** (repris du prompt 34) : refus si `DJANGO_SETTINGS_MODULE` contient « production » ; refus sur une base qui contient des comptes que ce chargeur n'a pas créés ; jamais de coexistence entre le jeu de recette, le jeu de démonstration et le jeu volumineux.
7. **Données fictives et manifestement inventées** (registre v8, R28). Aucune liste de noms réels. Noms construits de façon visiblement artificielle : syllabes générées, préfixe `FICT`, matricules au format `FX-000000`. Le jeu de recette garde ses désignations courtes (`I6`, `EXP1`…).
8. **Contrôle de sortie** : `--verifier`, en lecture seule, rapporte chaque objet attendu et contrôle les invariants : aucune violation de RG-34 (instructeur sur deux séances simultanées), de RG-37 (lieu partagé surbooké, capacité), de RG-39 (volume programmé au-delà du prescrit) ; un seul programme par semaine ; états du circuit cohérents avec ETA-01. Le rapport se termine par `N/N conformes`.

---

## Temps 0 — Relevé d'heure

Une ligne dans `docs/suivi/heures-phase-6.md`, l'heure de début notée avant d'ouvrir le premier fichier.

## Temps 1 — Script de remise à zéro

Écris `outils/recette/reinitialiser_base_recette.ps1` (PowerShell, le poste est sous Windows) avec un paramètre `-Etat {socle|complet|volume}` :
1. supprime puis recrée la base cible (`pfe_cit_recette`, ou `pfe_cit_volume` pour `volume`) avec les mêmes rôles et privilèges que dans `JEU-RECETTE.md` ;
2. `migrate` avec le rôle `pfe_cit_migration` ;
3. `initialiser_habilitations`, `initialiser_gabarits_documents`, `initialiser_grilles_horaires` ;
4. le chargeur de l'état demandé, puis son `--verifier`.

Il demande une confirmation **qui nomme la base** avant de la supprimer, refuse toute base dont le nom n'est pas exactement l'une des deux autorisées, et s'arrête à la première erreur. Ajoute `config.settings.volume` sur le modèle de `config.settings.recette`, la base fixée en dur à `pfe_cit_volume`.

## Temps 2 — État `complet` du jeu de recette

`charger_jeu_recette --etat complet` = l'état `socle` inchangé (le contenu de `JEU-RECETTE.md` ne bouge pas, RECETTE-00 en dépend), **plus** ce qui suit. Garde `--etat socle` comme comportement par défaut.

### 2.1 Référentiel ajouté

| Objet | Contenu |
|---|---|
| Matières | `M6` salle attitrée · `M7` lieu partagé (laboratoire) · `M8` salle attitrée · `M9` salle attitrée |
| Formation | `F6` Opérateur transmissions (TF1) |
| Référentiel F6 | M1 40 h (coefficient 3, poids formatif 1 et certificatif 2) · M2 30 h · M3 20 h · M6 40 h (coefficient 2) · M7 30 h · M8 20 h · M9 20 h — total 200 h. **M6 prérequis de M8** |
| Objectifs | deux objectifs pédagogiques sur M6 |

200 h, c'est plus de six semaines pleines pour une brigade : la génération de quatre semaines n'épuisera pas le référentiel. C'est voulu, à la différence de F1 (40 h), qui s'épuise exprès dans RECETTE-00.

### 2.2 Ressources ajoutées

| Objet | Contenu |
|---|---|
| Instructeurs | `I6` (M6, M8) · `I7` (M7) · `I8` (M6, M9) · `I9` (M3, M9), tous militaires du centre. Ajoute la qualification M1 à `I3` |
| Lieux | `L7` attitrée, capacité 12 · `L8` attitrée, capacité 20 · `L9` amphithéâtre partagé **simultané**, capacité 60 |
| Indisponibilité passée | `I3`, tout le mardi de W-1, motif « stage » |
| Calendrier | Conférence centre entier, mercredi de W-1, 08:00–09:45, bloquante · Congé centre entier, vendredi de W+3, bloquant · Bivouac ciblant la brigade `EXP2`, jeudi et vendredi de W+2, bloquant |

### 2.3 Organisation

| Session | Formation | Dates | Brigades (effectif, salle attitrée) | Stagiaires |
|---|---|---|---|---|
| `S1` | F6 | lundi W-3 → vendredi W+8 | `EXP1` (20, L1) · `EXP2` (15, L2) | 35 affectés + 3 non affectés + 1 radié |
| `S2` | F2 | lundi W-3 → vendredi W+6 | `CDP1` (12, L7) | 12 affectés |
| `S3` | F2 | lundi W-12 → vendredi W-5 | `CDP9` (8, L8) | 8 affectés ; **aucune évaluation** |

S3 sert à la clôture réussie (US-SES-09) ; S1 à la clôture refusée (évaluations non finalisées). Pour les stagiaires, utilise les noms fictifs générés du Temps 3, mais en petit nombre.

### 2.4 Programmes

| Semaine | Brigades | Contenu particulier | État final | Chronologie simulée |
|---|---|---|---|---|
| W-2 | EXP1, EXP2, CDP1 | — | **affiché** | générée jeudi W-3, soumise et validée vendredi W-3, signée et affichée samedi W-3 |
| W-1 | EXP1, EXP2, CDP1 | Une séance de M2 **regroupant EXP1 et EXP2** dans L9 (35 ≤ 60) | **affiché** | même chronologie, une semaine plus tard |
| W0 | EXP1, EXP2, CDP1 | Après affichage : un avenant « déplacement » (une séance M6 de EXP1 déplacée du lundi au jeudi) et un avenant « remplacement d'instructeur » (I6 → I8 sur M6) | **affiché** | générée jeudi W-1, affichée samedi W-1, avenants le lundi de W0 |
| W+1 | EXP1, EXP2, CDP1 | Contient la séance verrouillée du contrôle E2 (§ 2.5) | **brouillon** | générée le jour D |

Les transitions se font avec les bons comptes : `u_plan` soumet, signe et affiche ; `u_ped` valide. Le signataire enregistré est « Directeur de la formation (fictif) ».

### 2.5 Évaluations

| Code | Type | Module, périmètre | Date | État à charger |
|---|---|---|---|---|
| `E1` | formative | M1, EXP1 | jeudi W-1 | Créée dans la chronologie simulée (séance verrouillée dans W-1). **Notes complètes** : 19 notes et 1 absence. Pas de procès-verbal |
| `E2` | formative | M2, EXP2 | mercredi W+1 | Séance verrouillée insérée dans W+1 (brouillon). Aucune note |
| `E3` | certificative | M6, session S1 | mardi W+5 | Deux sujets (références fictives `SUJ-E3-A`, `SUJ-E3-B`), **A retenu par la commission**. Organisation **partielle** : EXP1 dans L9, surveillant I8 et un surveillant extérieur « FICT Surveillant-A » ; EXP2 non organisée. Donc incomplète, non prête |
| `E4` | certificative | M3, session S1 | mercredi W+6 | Aucun sujet, aucune organisation |
| `E5` | formative | M4, CDP1 | jeudi W-1 | Créée dans la chronologie simulée. Notes **incomplètes** : 10 sur 12, deux manquantes |

Les notes sont des valeurs fixes, issues de la graine. Au moins **deux stagiaires ex aequo** sur E1, pour que le classement de RECETTE-02 ait un cas d'égalité à montrer.

### 2.6 Suivi

| Objet | Contenu |
|---|---|
| Non-exécutions | (a) une séance de EXP2 en W-2, motif « instructeur en mission » ; (b) sur la séance **regroupée** de W-1, la ligne de **EXP2 seulement**, motif « brigade de garde » |
| Progression réalisée | Une édition de W-2, produite par `u_plan`, non signée |

### 2.7 Ce que l'état `complet` ne charge pas, exprès

- aucun procès-verbal (RECETTE-02 les génère) ;
- aucune session clôturée (RECETTE-03 clôture S3) ;
- aucune indisponibilité qui toucherait W+1 (RECETTE-01 la déclare pour exercer US-PLAN-09) ;
- aucune duplication (RECETTE-04 la fait).

### 2.8 Tests du chargeur

Un test par état : il charge l'état sur la base de test et passe `--verifier` à `N/N`. Ajoute aussi un test de déterminisme (deux chargements, même graine, même empreinte des identifiants métier) et un test des garde-fous. Ce sont des tests d'outillage : ils ne comptent dans aucune story.

## Temps 3 — Jeu volumineux `charger_jeu_volume`

**But.** Voir l'application à la taille réelle du CIT. C'est indépendant des recettes : ce jeu ne sert à aucun contrôle des cahiers 00 à 04, seulement à RECETTE-05 (mesures, démonstration). Lis d'abord `etudes/solveur/HYPOTHESES.md` et cale les volumes ci-dessous sur ce qu'il établit. S'il diverge, **c'est lui qui fait foi** : signale l'écart dans le rendu.

### 3.1 Volumes cibles

| Domaine | Cible |
|---|---|
| Comptes | un par profil (`v_ped`, `v_plan`, `v_exa`, `v_df`, `v_adm`), plus un second compte pédagogique et planification |
| Types de formation | 4 |
| Formations | 10, dont 1 archivée |
| Catalogue des matières | ≈ 70 ; référentiels de 8 à 15 matières, 150 à 400 h, avec des prérequis (graphes acycliques de profondeur 2 à 3) |
| Instructeurs | ≈ 55 : militaires du centre, vacataires et civils ; 2 à 5 qualifications chacun ; quelques archivés |
| Lieux | 36 salles attitrées (capacités de 15 à 30) ; 8 lieux partagés : 2 amphithéâtres simultanés, 3 laboratoires séquentiels, 3 salles spécialisées |
| Sessions | 7 en cours et 3 terminées |
| Brigades en cours | **32**, réparties sur les 7 sessions en cours, chacune avec sa salle attitrée |
| Stagiaires | ≈ 900, dont une vingtaine de radiés et quelques non affectés |
| Grilles | Ordinaire active, Ramadan inactive |
| Calendrier | une année : congés, conférences, bivouacs ciblés, semaines d'examen |
| Indisponibilités | ≈ 40, passées et à venir |
| Programmes | **8 semaines passées affichées** (W-8 à W-1), avec ≈ 5 % de séances sous avenant et ≈ 3 % de non-exécutions ; W0 affichée ; W+1 validée ; W+2 soumise ; W+3 brouillon |
| Évaluations | formatives par brigade sur les semaines passées, notes complètes ; certificatives à venir, organisées en partie |
| Sessions terminées | notes complètes et procès-verbal de fin de formation généré, pour 2 des 3 |

### 3.2 Exigences propres au jeu volumineux

- **Même règle des services** que l'état `complet`. Si la génération heuristique ne parvient pas à remplir une semaine (lieux partagés saturés par exemple), on garde ce qu'elle produit : c'est une **mesure**, pas un défaut à masquer. Si RG-14 (salles attitrées) bloque la constitution des brigades, c'est le risque R24 qui se matérialise : signale-le au lieu d'ajouter des salles en silence.
- **Mesures**, consignées dans `MESURES-REFERENCE.md` (section « Jeu volumineux ») :
  - temps de génération de chaque semaine pour les 32 brigades (BNF-04 : moins de 5 minutes) ;
  - taux de créneaux non pourvus et leurs motifs dominants ;
  - durée totale du chargement ;
  - nombre de requêtes et temps de rendu de six écrans, mesurés par le client de test sur cette base : liste des stagiaires, consultation du programme W0, rapprochement prescrit/réalisé de la plus grosse session, tableau de bord, liste des programmes, charge d'un instructeur (BNF-05 : moins de 2 secondes).

  Ces mesures sont un relevé. Ne corrige rien dans ce prompt, même si un seuil est dépassé : un dépassement devient une anomalie de RECETTE-05.
- `--verifier` contrôle les mêmes invariants que l'état `complet`, à l'échelle.
- Durée : si le chargement dépasse 30 minutes, propose un mode `--semaines N` pour réduire le nombre de semaines passées, sans toucher au reste.

## Temps 4 — Documentation de référence

Écris `docs/recette/JEUX-DE-DONNEES-PHASE-6.md`. Les cahiers RECETTE-01 à 05 seront rédigés **à partir de ce document**, qui doit donc décrire ce qui a **réellement** été chargé et non ce que ce prompt prévoyait :
- pour l'état `complet`, les tableaux des § 2.1 à 2.6 **tels que chargés**, avec, pour chaque semaine de programme, la liste des séances par brigade (jour, créneau, matière, instructeur, lieu) et les identifiants de la séance regroupée, des avenants et des non-exécutions ;
- les dates calendaires obtenues pour la date de référence du chargement de contrôle, en précisant qu'elles glissent avec `D` ;
- pour le jeu volumineux, les volumes obtenus et les mesures du Temps 3 ;
- les commandes (remise à zéro, chargement, vérification, lancement) ;
- **tout écart** entre ce prompt et le chargé, avec sa cause : refus d'un service, règle non anticipée, horloge simulée insuffisante.

Mets aussi à jour `JEU-RECETTE.md`, avec un renvoi vers ce document et l'option `--etat`.

## Temps 5 — Étiquette, contrôle et commit

1. Suite complète, **seule sur la machine** (leçon P-51), plus `pytest -m pdf` en conteneur. Elle doit rester verte : tu n'as touché aucun code applicatif.
2. Relis le diff : aucun fichier sous `app/<application>/services/`, `models/` ou `views*` ne doit être modifié. Seuls `app/*/jeu_recette/`, `app/*/management/commands/`, `config/settings/volume.py`, `outils/recette/`, les tests du chargeur et `docs/` peuvent apparaître. Toute autre modification est une erreur : annule-la et signale-la.
3. Relecture par le sous-agent `relecteur-conception`, centrée sur un point : **aucun contournement de service** dans les chargeurs.
4. Commits séparés : chargeur `complet` ; jeu volumineux ; scripts et documentation.
5. Pose l'étiquette `recette-phase-6` sur le dernier commit.
6. Clôture la ligne de `heures-phase-6.md`.

## Rendu attendu

- Les commandes exactes pour remettre la base à zéro dans chaque état.
- Le rapport de `--verifier` pour les deux jeux (`N/N`).
- Pour l'état `complet` : tout écart avec le § 2, et sa cause.
- Pour le jeu volumineux : les volumes obtenus, l'écart avec `HYPOTHESES.md`, les mesures du Temps 3 et tout seuil dépassé (relevé, sans correction).
- Le mécanisme d'horloge simulée retenu, et toute étape où il n'a pas suffi.
- Ce que tu as tranché seul, et ce que tu n'as pas pu vérifier.
