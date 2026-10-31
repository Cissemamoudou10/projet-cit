# RECETTE-00 — Socle (sprints 1 et 2)

**Projet.** Création des activités du CIT — Centre d'instruction des transmissions.

**Objet.** Petite recette de non-régression du périmètre des sprints 1 et 2. Elle sert de **base** aux recettes des sprints 3 et 4 : si le socle (habilitations, référentiel, sessions, génération) est défaillant, toutes les recettes suivantes sont faussées.

**Cadre.** Ce cahier applique le plan `PLAN-DE-TESTS-PHASE-6.md` (conventions, notation, sévérité, anomalies) et ne les redéfinit pas.

**Référence.** Backlog v11 (23/10), cas d'utilisation v4, étiquette `recette-phase-6`.

| Date d'exécution | Recetteur | Relecteur | Navigateur | Date système (W0) |
|---|---|---|---|---|
| | | | | |

---

## 1. Portée

Les **27 stories** des sprints 1 et 2, couvertes **par échantillon**. Chaque story reçoit au moins un contrôle nominal et un contrôle de sa règle principale. Ce cahier ne remplace pas le détail :
- la recette du sprint 1 (4 septembre, 115 contrôles) n'est pas rejouée ;
- le cahier du sprint 2 (260 contrôles) reste la référence détaillée.

Ce qu'on cherche ici, c'est qu'**aucune livraison des sprints 3 et 4 n'ait cassé le socle**.

**Hors de ce cahier** : tout ce qui relève des sprints 3 et 4 (circuit de validation, modifications manuelles, évaluations, suivi). Ces contrôles sont dans RECETTE-01 à 05, sur le jeu `complet`.

## 2. Préparation

1. `.\outils\recette\reinitialiser_base_recette.ps1 -Etat socle`
2. `python app\manage.py charger_jeu_recette --verifier --settings=config.settings.recette` : le rapport doit annoncer tous les contrôles conformes.
3. `python app\manage.py runserver --settings=config.settings.recette`
4. Mot de passe des cinq comptes : `Transmissions#2026`.

### Données du jeu `socle` (rappel de `JEU-RECETTE.md`)

| Objet | Contenu |
|---|---|
| Comptes | `u_ped` pédagogique · `u_plan` planification · `u_exa` examens · `u_df` Direction de Formation · `u_adm` administrateur |
| Types de formation | `TF1` Formation initiale · `TF2` Formation de spécialité |
| Formations | `F1` Exploitant radio · `F2` Chef de poste · `F3` archivée · `F4` sans référentiel |
| Matières | `M1` salle attitrée · `M2` lieu partagé · `M3` sans lieu · `M4`, `M5` salle attitrée |
| Référentiels | `F1` : M1 20 h, M2 10 h, M3 10 h · `F2` : M4 10 h, M5 10 h, M4 prérequis de M5 · `F3` : M1 10 h |
| Instructeurs | `I1` (M1, M2, M3) · `I2` (M1) · `I3` (M2) · `I4` (M1, **archivé**) · `I5` (M4, M5) |
| Lieux | `L1` attitrée 20 · `L2` attitrée 15 · `L4` partagé simultané 30 · `L5` partagé séquentiel 30 · `L6` attitrée **archivé** |
| Grilles | Ordinaire **active** · Ramadan inactive |

### Notation des semaines

`W0` désigne la semaine du jour d'exécution, `W+1` la suivante, `W-1` la précédente. Les dates des contrôles s'expriment ainsi pour que le cahier puisse être rejoué n'importe quel jour.

### Ordre

Les sections s'exécutent **dans l'ordre**. La section 7 crée la session dont la section 8 a besoin. Un contrôle qui échoue et empêche les suivants entraîne un « B » sur ceux-ci, jamais un « NC ».

---

## 3. Paquetage Administration — US-ADM-01 à 04

Profil indiqué dans chaque ligne.

| Code | Contrôle | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|
| R00-ADM-01 | `u_ped` se connecte avec le bon mot de passe | Accès à l'accueil de la cellule pédagogique | US-ADM-01 c.1 | C | |
| R00-ADM-02 | `u_ped` saisit un mauvais mot de passe | Message générique, sans dire lequel des deux éléments est faux | US-ADM-01 c.2 | C | |
| R00-ADM-03 | Saisir un identifiant inexistant | **Exactement le même message** qu'au contrôle 02 : l'existence du compte n'est pas révélée | US-ADM-01 c.2, CU-P1-01 E1 | C | |
| R00-ADM-04 | Avec `u_exa`, cinq échecs consécutifs, puis le bon mot de passe | Compte verrouillé ; le bon mot de passe est refusé pendant la durée de verrouillage | RG-03 | C | Noter la durée observée. `u_exa` doit être déverrouillé (attente ou administrateur) avant R00-SES-17 |
| R00-ADM-05 | Depuis trois écrans différents, chercher la déconnexion | Présente partout ; après déconnexion, le retour arrière ne rouvre pas la session | US-ADM-01 c.5 | C | |
| R00-ADM-06 | `u_adm` crée le compte `u_test` (profil Cellule examens), puis un second compte `u_test` | Premier compte créé ; doublon refusé avec un message explicite | US-ADM-02 c.1, c.4 | C | |
| R00-ADM-07 | `u_adm` désactive `u_test` ; tentative de connexion avec `u_test` | Compte conservé, connexion refusée | US-ADM-02 c.2, c.3 | C | |
| R00-ADM-08 | `u_ped` saisit directement l'adresse de la gestion des comptes | Refus explicite côté serveur ; la tentative est journalisée | US-ADM-02 c.5, US-ADM-03 c.5, c.6 | C | |
| R00-ADM-09 | `u_adm` ouvre le journal et filtre par utilisateur (`u_ped`), puis par type d'action, puis par date | Les trois filtres opèrent ; on retrouve l'échec du contrôle 02 et le refus du contrôle 08 | US-ADM-04 c.5, RG-26 | C | |
| R00-ADM-10 | `u_adm` cherche une commande de modification ou de suppression d'une entrée du journal | Aucune | US-ADM-04 c.4, RG-27 | C | |

## 4. Paquetage Référentiel — US-REF-00 à 07

Profil : `u_ped` sauf indication contraire.

| Code | Contrôle | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|
| R00-REF-01 | Lister les formations, filtrer par type `TF1` | F1 et F4 présentées ; F3 présentée comme archivée, ou absente des listes de sélection | US-REF-00 c.4, US-REF-01 c.3 | C | |
| R00-REF-02 | Supprimer le type `TF1` | Refus ; les formations qui l'utilisent sont énumérées | US-REF-00 c.3 | C | |
| R00-REF-03 | Créer une formation « Exploitant radio » sous `TF2`, puis une seconde « Exploitant radio » sous `TF1` | La première est acceptée (homonyme dans un autre type) ; la seconde est refusée (même type que F1) | US-REF-01 c.2 | C | |
| R00-REF-04 | Supprimer la formation « Exploitant radio » de `TF2` créée au contrôle 03 | Acceptée : elle ne porte aucune session | US-REF-01 c.4 | C | |
| R00-REF-05 | Ouvrir la fiche de `M1` | Les formations qui l'utilisent sont indiquées : F1 et F3 | US-REF-02 c.3 | C | |
| R00-REF-06 | Supprimer `M1`, puis créer une matière dont l'intitulé est celui de `M1` | Les deux refus ; la suppression énumère les référentiels qui l'utilisent | US-REF-02 c.2, c.5 | C | |
| R00-REF-07 | Référentiel de F1 : vérifier le total, puis rattacher `M4` avec un volume de 0 h | Total affiché : 40 h. Le rattachement à 0 h est refusé | US-REF-03 c.4, c.5 | C | Le champ lui-même refuse 0 au moment de rattacher |
| R00-REF-08 | Rattacher `M4` à F1 avec 10 h, puis porter son coefficient à 0, puis ses deux poids à 0 | 10 h acceptées ; coefficient nul refusé ; deux poids nuls refusés | US-REF-03 c.7 | C | Les champs refusent 0 à la validation. **Mais le coefficient et les poids ne s'affichent pas dans la liste des matières rattachées** : il faut les ressaisir à chaque modification. Candidat NC, à qualifier à la séance de corrections |
| R00-REF-09 | Retirer `M4` du référentiel de F1 | Accepté après confirmation : rien ne la référence | US-REF-03 c.6, BNF-09 | C | |
| R00-REF-10 | Ouvrir `M2` dans le référentiel de F1 | Catégorie « lieu partagé » avec son type attendu (amphithéâtre, laboratoire ou salle spécialisée) | US-REF-04 c.1, c.2 | C | Déjà visible dans la liste des matières rattachées |
| R00-REF-11 | Ajouter deux objectifs pédagogiques à `M3`, ordres 1 et 2, puis consulter le référentiel de F1 | Objectifs visibles sur la fiche de M3 **et** depuis le référentiel de F1, dans l'ordre | US-REF-05 c.1 à c.3 | C | |
| R00-REF-12 | Référentiel de F2 : déclarer `M5` prérequis de `M4` | Refus : cycle, avec la **chaîne de matières** qui le forme | US-REF-06 c.2, CU-P2-07 E1 | C | |
| R00-REF-13 | Avec `u_plan`, ouvrir le référentiel de F1 | Formations, matières, volumes et prérequis consultables ; aucun bouton d'écriture | US-REF-07 c.1, c.2 | C | |
| R00-REF-14 | Avec `u_plan`, saisir directement l'adresse de modification du référentiel de F1 | Refus côté serveur, journalisé une fois, sans révéler de donnée | US-REF-07 c.3 | C | |
| R00-REF-15 | Avec `u_ped`, porter M1 de F1 à 25 h ; avec `u_plan`, recharger le référentiel ; avec `u_ped`, remettre 20 h | La valeur de 25 h est visible immédiatement côté planification ; 20 h rétablies | US-REF-07 c.4 | C | Même défaut qu'en REF-08 : coefficient et poids non affichés dans la liste, à ressaisir à chaque modification |

## 5. Paquetage Ressources — US-INS-01 à 03, US-PLAN-02

| Code | Contrôle | Profil | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|---|
| R00-RES-01 | Liste des instructeurs : rechercher par nom, puis filtrer par statut | `u_ped` | Recherche et filtre opérants, liste paginée | US-INS-01 c.3 | C | |
| R00-RES-02 | Créer un instructeur « militaire du centre » sans matricule, puis un « vacataire » sans matricule | `u_ped` | Le premier est refusé, matricule obligatoire ; le second est accepté | US-INS-01 c.1 | C | Refus correct, mais le message n'est pas assez précis : NC mineur probable (BNF-10) |
| R00-RES-03 | Archiver le vacataire créé au contrôle 02 | `u_ped` | Archivé, toujours consultable, marqué comme tel | US-INS-01 c.2 | C | |
| R00-RES-04 | Matrice de qualification : consulter par matière `M2`, puis créer une matière `M10` sans aucune qualification | `u_ped` | M2 : I1 et I3. M10 signalée visuellement comme sans instructeur qualifié | US-INS-02 c.3, c.4 | C | Supprimer M10 ensuite |
| R00-RES-05 | Ouvrir la **matrice de qualification** des instructeurs (celle du contrôle 04 : quels instructeurs sont habilités à enseigner quelles matières) | `u_plan` | Consultable, aucune commande de modification | US-INS-02 c.5 | C | |
| R00-RES-06 | Liste des lieux : filtrer par catégorie, puis par capacité ≥ 20 | `u_plan` | Filtres opérants ; L4 affiché « simultané », L5 « séquentiel » | US-PLAN-02 c.2, c.5 | C | |
| R00-RES-07 | Déclarer `L5` indisponible du lundi au mardi de W+2 | `u_plan` | Période enregistrée et visible sur la fiche du lieu | US-PLAN-02 c.3 | C | |
| R00-RES-08 | Enregistrer une indisponibilité de `I1` le jeudi et le vendredi de W+1 (motif : mission), puis une seconde du vendredi au lundi suivant | `u_plan` | Première enregistrée, rattachée à `u_plan` et non à I1 ; la seconde déclenche une **proposition de fusion**, rien n'est écrit avant confirmation | US-INS-03 c.1 à c.3, RG-24 | C | Confirmer la fusion |

## 6. Paquetage Calendrier et grilles — US-PLAN-12, US-PLAN-01

Profil : `u_plan`.

| Code | Contrôle | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|
| R00-CAL-01 | Consulter les grilles | Ordinaire active (08:00–09:45 · 10:10–12:00 · 13:00–14:15 · 14:40–16:00) ; Ramadan inactive | US-PLAN-12 c.1 | C | |
| R00-CAL-02 | Activer Ramadan, puis réactiver Ordinaire | Confirmation qui nomme la grille désactivée ; une seule active à la fois ; date et agent de chaque activation enregistrés | US-PLAN-12 c.3, c.4 | C | |
| R00-CAL-03 | Créer une grille « Essai » avec deux créneaux du lundi qui se recouvrent | Refus, créneau en conflit désigné | US-PLAN-12 c.2 | C | |
| R00-CAL-04 | Tenter d'activer « Essai » sans aucun créneau valide | Refus | US-PLAN-12 c.5 | C | Supprimer « Essai » ensuite |
| R00-CAL-05 | Créer une période « Congé », vendredi de W+3, **sans cible** | Créée ; portée affichée « centre entier » | US-PLAN-01 c.4 | C | |
| R00-CAL-06 | Créer une conférence le mardi de W+1, de 08:00 à 09:45, effet bloquant | Créée ; le reste de la journée reste disponible | US-PLAN-01 c.2, c.3 | C | Utilisée en R00-GEN-04 |
| R00-CAL-07 | Recréer exactement la conférence du contrôle 06 (mêmes bornes, sans cible) | Refus : doublon exact, période en conflit désignée | US-PLAN-01 c.4 | C | Le cas « mêmes bornes, cibles différentes » se contrôle en R00-SES-19, une fois la session créée |

## 7. Paquetage Organisation — US-SES-01 à 07

Profil : `u_ped` sauf indication contraire.

| Code | Contrôle | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|
| R00-SES-01 | Ouvrir la session `S0` sur F1 : début le lundi de W-1, fin le vendredi de W+10, effectif attendu 40 | Session ouverte ; le référentiel de F1 est présenté (matières et 40 h) | US-SES-01 c.1, c.2 | C | |
| R00-SES-02 | Ouvrir une session sur F3, puis sur F4 | Les deux refus : formation archivée ; référentiel vide | US-SES-01 c.4, CU-P3-01 E4 | C | F3 et F4 n'apparaissent même pas dans la liste de choix : l'erreur est empêchée en amont |
| R00-SES-03 | Ouvrir une session dont la fin précède le début | Refus | RG-11 | C | |
| R00-SES-04 | Dans S0, créer les brigades `EXP1` (effectif 20) et `EXP2` (effectif 15) | Créées ; l'écart 35 / 40 est signalé **sans blocage** | US-SES-02 c.3, c.4 | C | |
| R00-SES-05 | Supprimer EXP2, puis tenter de supprimer EXP1 ; recréer EXP2 (15) | Première suppression acceptée ; la seconde refusée (dernière brigade) | US-SES-02 c.2 | C | |
| R00-SES-06 | **Toujours connecté avec `u_ped`**, ouvrir la brigade EXP1 et chercher le bouton qui permet de lui attribuer une salle attitrée (L1, L2…) | Le bouton est **absent**, ou l'action est **refusée** : c'est la cellule planification qui attribue les salles, pas la pédagogique (contrôle suivant) | matrice § 11.2, CU-P3-03 | C | Test d'habilitation : on vérifie que `u_ped` **ne peut pas** faire l'action |
| R00-SES-07 | `u_plan` attribue L1 à EXP1 et L2 à EXP2, puis tente L2 pour EXP1, puis L4 pour EXP2 | L1 et L2 acceptées ; L2 pour EXP1 refusée **avec l'écart chiffré** ; L4 refusée (lieu partagé) | US-SES-03 c.2 | C | Une salle déjà attribuée et les lieux partagés n'apparaissent pas dans la liste des salles attitrables |
| R00-SES-08 | Fiche de composition de S0, avec `u_ped` puis avec `u_df` | Brigades, effectifs, salles, taux d'occupation 100 % ; `u_df` y accède en lecture, sans aucune commande | US-SES-04 c.1, c.3, c.4 | C | |
| R00-SES-09 | Importer `01-valide-10.csv` : étape d'analyse, puis confirmation | À l'analyse, 10 lignes valides et **aucun stagiaire créé** ; après confirmation, 10 créés | US-SES-05 c.3, c.5, RG-18 | C | |
| R00-SES-10 | Importer `09-matricule-manquant-ligne-12.csv` | Ligne **12** signalée avec son motif | US-SES-05 c.5 | NC mineur | **Point d'attention** : le backlog (c.5) dit « aucun import partiel tant que les erreurs subsistent », la fiche CU-P3-05 (E4) dit que les autres lignes restent importables. Noter le comportement observé ; s'il suit la fiche, NC **mineur documentaire**, à porter au backlog — Les lignes sans anomalie sont importées : écart documentaire entre le backlog (c.5) et CU-P3-05 (E4), à porter au backlog |
| R00-SES-11 | Importer `03-valide-45-colonnes-permutees.csv` | 45 lignes reconnues malgré les colonnes permutées ; total de la session : 55 | US-SES-05 c.3, c.4 | C | |
| R00-SES-12 | Radier un stagiaire (motif et date) ; comparer les commandes Radier et Supprimer | Stagiaire conservé, marqué radié ; libellés et confirmations distincts | US-SES-05 c.7, BNF-09 | C | |
| R00-SES-13 | Lancer la proposition de répartition | 20 dans EXP1, 15 dans EXP2, remplissage successif ; les non-affectés listés à part ; le radié absent ; **rien n'est enregistré** avant validation | US-SES-06 c.1, c.5 | C | Valider ensuite |
| R00-SES-14 | (a) Affecter un 16ᵉ stagiaire à EXP2 (salle L2, capacité 15). (b) Porter l'effectif déclaré de EXP1 à 18, désaffecter un de ses stagiaires (19 réels), puis en affecter un autre (20 réels) | (a) **Refus**, avec la marge restante : la capacité de la salle est un fait physique. (b) **Accepté avec avertissement** : l'effectif déclaré est prévisionnel | US-SES-06 c.3 | a : C · b : NC | Remettre l'effectif déclaré de EXP1 à 20 — b : réduire l'effectif déclaré d'une brigade pleine ne donne aucune alerte (un avertissement est attendu) ; et un retrait d'affectation exige d'attendre un jour |
| R00-SES-15 | Affecter à EXP2 un stagiaire déjà affecté à EXP1 | Refus ; la brigade actuelle est nommée, un déplacement est proposé | US-SES-06 c.4 | NC | Déplacer ou retirer un stagiaire affecté le jour même est refusé : il faut attendre un jour. Candidat NC majeur (historisation RG-20) |
| R00-SES-16 | Liste des stagiaires : filtrer sur EXP1, rechercher un nom accentué sans les accents, exporter en CSV | Filtre et recherche opérants ; l'export respecte le filtre, accents corrects | US-SES-07 c.1 à c.3 | C | |
| R00-SES-17 | Avec `u_exa`, ouvrir la liste des stagiaires de EXP1 | Accès en lecture | US-SES-07 c.4 | C | |
| R00-SES-18 | Supprimer F1, puis supprimer L1 | Les deux refus : F1 porte S0 ; L1 est attitrée à EXP1. Les opposants sont énumérés | US-REF-01 c.4, US-PLAN-02 c.4 | C | |
| R00-SES-19 | (`u_plan`) Vue annuelle du calendrier ; puis créer une période de mêmes bornes que la conférence de R00-CAL-06, **ciblant S0** | S0 apparaît en bande sans qu'aucune période n'ait été créée, le congé de W+3 est visible. La nouvelle période est acceptée **avec avertissement** (mêmes bornes, cibles différentes) | US-PLAN-01 c.4, c.7, RG-30 bis | C | Supprimer cette période ensuite |

## 8 et 9. Planification et contrôles transverses — déplacés

**Sortis de ce cahier le 30/10/2026**, à la demande du recetteur. La génération avait été lancée sur la mauvaise semaine (W0 au lieu de W+1), et aucun moyen n'existait pour défaire un brouillon. Ces contrôles sont rejoués dans **RECETTE-00 bis** (`RECETTE-00-BIS-PLANIFICATION.md`), sur un état de départ propre (`socle-planif`). La correspondance des codes est donnée au § 8 de RECETTE-00 bis.

R00-GEN-01 et R00-GEN-02 avaient été notés C, et R00-GEN-03 NC (compte rendu non consultable après coup, trop long), le 30/10. Ces résultats sont remplacés par ceux de RECETTE-00 bis.

---

## 10. Dépouillement

| Section | Contrôles | C | NC majeur | NC mineur | B | SO |
|---|---|---|---|---|---|---|
| 3. Administration | 10 | | | | | |
| 4. Référentiel | 15 | | | | | |
| 5. Ressources | 8 | | | | | |
| 6. Calendrier et grilles | 7 | | | | | |
| 7. Organisation | 19 | | | | | |
| **Total** | **59** | | | | | |

Les sections 8 et 9 (16 contrôles) sont dans RECETTE-00 bis. Les deux cahiers se prononcent ensemble, après la séance de corrections.

**Décision**

☐ **Prononcée** — aucun NC majeur

☐ **Prononcée sous réserve** — NC majeur corrigé, rejeu prévu le ________

☐ **Refusée** — NC majeur ouvert : RECETTE-01 à 05 ne commencent pas avant correction

*Exécution des sections 3 à 7 : 30/10/2026, sur l'étiquette `recette-phase-6`.*

**Observations :**

## 11. Matrice story → contrôles

*Les codes `GEN-` et `TRV-` ci-dessous renvoient désormais à RECETTE-00 bis (`R00B-GEN-`, `R00B-TRV-`, correspondance au § 8 de RECETTE-00 bis).*

| Story | Contrôles |
|---|---|
| US-ADM-01 | ADM-01 à 05 |
| US-ADM-02 | ADM-06 à 08 |
| US-ADM-03 | ADM-08, TRV-01 à 03 |
| US-ADM-04 | ADM-09, ADM-10, TRV-04 |
| US-REF-00 | REF-01, REF-02 |
| US-REF-01 | REF-03, REF-04, SES-18 |
| US-REF-02 | REF-05, REF-06 |
| US-REF-03 | REF-07 à 09 |
| US-REF-04 | REF-10 |
| US-REF-05 | REF-11 |
| US-REF-06 | REF-12 |
| US-REF-07 | REF-13 à 15 |
| US-INS-01 | RES-01 à 03 |
| US-INS-02 | RES-04, RES-05 |
| US-INS-03 | RES-08, GEN-05 |
| US-PLAN-02 | RES-06, RES-07, SES-18 |
| US-PLAN-12 | CAL-01 à 04 |
| US-PLAN-01 | CAL-05 à 07, SES-19, GEN-04 |
| US-SES-01 | SES-01 à 03 |
| US-SES-02 | SES-04, SES-05 |
| US-SES-03 | SES-06, SES-07 |
| US-SES-04 | SES-08 |
| US-SES-05 | SES-09 à 12 |
| US-SES-06 | SES-13 à 15 |
| US-SES-07 | SES-16, SES-17 |
| US-PLAN-03 | GEN-01 à 03, GEN-07, GEN-08 |
| US-PLAN-04 | GEN-04 à 07 |

Les 27 stories sont toutes couvertes par au moins un contrôle.

## 12. Fiche d'anomalie (modèle)

| Champ | Valeur |
|---|---|
| Code du contrôle | R00-___-__ |
| Date de constat | |
| Profil utilisé | |
| Écran | |
| Attendu | |
| Observé | |
| Étapes de reproduction | |
| Sévérité | ☐ majeur ☐ mineur |
| Règle ou critère violé | |
| Code `PROBLEMES.md` | P-__ |
| Correction (prompt, commit) | |
| Rejeu | ☐ C ☐ NC — date : |

---

*RECETTE-00 — version 1 du 26 octobre 2026. Lot WBS 6.3.*
