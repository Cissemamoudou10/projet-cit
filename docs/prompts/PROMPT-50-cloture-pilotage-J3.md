# Prompt 50 — Clôture documentaire du J3 et ouverture de la phase 6

**Nature.** Travail de suivi uniquement. **Aucun fichier sous `app/` ne doit être modifié**, aucune migration, aucun test. Si une étape semble exiger du code, arrête-toi et signale-le.

**Contexte.** Le développement est clos depuis le 20 octobre (prompt 49, étiquette `j3-fin-developpement`). Depuis, le chef de projet a produit hors du dépôt quatre documents :
- le backlog produit v11 (23/10) ;
- le registre des risques v8 (23/10) ;
- le classeur de pilotage v1.4 (25/10) ;
- le rapport d'avancement N°3, remis au commanditaire le 26/10.

Plusieurs fichiers de `docs/suivi/` contredisent aujourd'hui ces documents. Ce prompt les remet en cohérence **sans réécrire l'historique** : on ajoute des notes datées, on ne retouche pas les lignes existantes. Seules exceptions : l'en-tête et les tableaux d'état d'`AVANCEMENT.md`, qui décrivent un état courant.

La phase 6 (tests et recette) s'ouvre le 26 octobre et s'achève au jalon C3 du **2 novembre**. Le déploiement s'achève au jalon C4 du **10 novembre**.

---

## Temps 0 — Relevé d'heure

Crée `docs/suivi/heures-phase-6.md` sur le gabarit de `heures-sprint-4.md` (même colonnes, même règle). Note l'heure de début **avant d'ouvrir tout autre fichier**. La colonne « heures humaines » reste à la charge de l'étudiant.

## Temps 1 — Backlog v11 dans le dépôt

L'étudiant dépose le fichier `04_Backlog_produit_v11_2026-10-23.md` dans `docs/livrables/` avant de lancer ce prompt.
1. Vérifie sa présence. **S'il est absent, arrête-toi et demande-le** : ne reconstitue aucun critère de mémoire.
2. Ajoute une ligne à `docs/livrables/` (README existant, ou un `00-LISEZ-MOI.md` à créer) : « Backlog v11 déposé le 25/10/2026 — mesure du backlog v11, § 12 : la traçabilité critère → test s'établit désormais sur le texte intégral des critères. »
3. Ajoute en tête de `docs/suivi/TRACABILITE.md` une note datée du 25/10. Elle dit que le backlog v11 est désormais dans le dépôt et que la quinzaine de critères « non identifiés » sera revérifiée sur son texte pendant la phase 6. **Ne modifie pas l'inventaire lui-même.**

## Temps 2 — `AVANCEMENT.md`

Mets à jour l'**état courant** :
- **En-tête.** « Dernière mise à jour : 25 octobre 2026 (prompt 50) ». Le développement est clos depuis le 20/10 et la phase 6 s'ouvre le 26/10. Remplace le paragraphe du 2 octobre, devenu périmé.
- **Tableau des phases.**
  - Phase 5 : **Close** — J3 atteint le 20/10, quatre jours d'avance.
  - Phase 6 : **En cours à partir du 26/10**, C3 le 02/11.
  - Phase 7 : C4 le 10/11.
- **Indicateurs.**
  - Marge avant dépôt : **9 jours ouvrés, plus l'avance gagnée au J3** (registre v8, O1). Ajoute une phrase : la valeur « 14 jours ouvrés, intacte » était périmée depuis le 30/09, date à laquelle le registre v6 l'avait ramenée à 9.
  - Vélocité et clé de conversion : **définitivement non mesurées**. Aucune heure humaine n'a été relevée sur les 52 stories (registre v8, R23). Quatre sprints livrés à 100 % : c'est la seule mesure validée.
- **« Ce qu'il faut surveiller ».** Remplace les points échus par l'état au 25/10, chaque point avec sa source :
  - les points de décision des 7 et 21 octobre sont tenus ;
  - R1 et R10 : réponses par défaut retenues le 16/10 (D-268), toute réponse tardive sera traitée comme une évolution ;
  - R6 éteint (D-289) ;
  - risques actifs de la phase 6, d'après le registre v8 : **R16 critique** (porteurs, voir Temps 4), **R29** (recette sans les cellules), **R22** (impression du programme hebdomadaire, anomalie n°1) ;
  - **décision du chef de projet du 25/10** : aucune installation sur un serveur du CIT n'est envisagée. Le déploiement de la phase 7 se fait sur une **machine virtuelle isolée**, hors ligne, reproduisant le serveur du réseau interne, avec le protocole déjà éprouvé le 7 septembre (`INSTALLATION-HORS-LIGNE.md`). R15 (accès au poste du CIT) devient sans objet. La procédure livrée doit rester applicable telle quelle à un serveur du centre. **Ouvre pour cela une décision dans `DECISIONS.md`**, au numéro qui suit le dernier du fichier (relu, pas supposé), auteur : chef de projet. C'est la seule décision de ce prompt.
  - Supprime la note qui hésitait entre R1 et R10 : le registre v8 tranche. R1 porte le silence du commanditaire, R10 la justesse du circuit.

Ajoute ensuite à la fin de la section des reports **un recompte daté**, sans toucher aux recomptes antérieurs : « Recompte du 25/10/2026 (prompt 50), d'après le backlog v11 ». Il doit dire :
- **D-212** et **D-215** ne sont pas orphelins : ce sont les critères 2 et 1 d'**US-EVAL-11**, en réserve depuis le backlog v10 (§ 9, note v11) ;
- **D-182** est classé **Won't** depuis le backlog v10 (§ 11.2), ce qui ferme le report ;
- **net : aucun report orphelin**. La revue du sprint 4 en comptait trois parce que le backlog n'était pas dans le dépôt : c'est exactement le défaut que corrige le Temps 1.

**Questions de terrain.** Ajoute les quatre valeurs par défaut soumises au commanditaire par le rapport N°3, avec une réponse attendue au 02/11 :
- seuil d'admission à 10/20 ;
- note absente comptée zéro ;
- ex aequo classés au même rang ;
- seuil de charge d'un instructeur à 24 h par semaine.

## Temps 3 — `sprint-4.md`

Ne coche **que ce qui est vrai**, en le vérifiant dans le dépôt. Ne coche rien sur la foi de ce prompt.
- « Registre des risques mis à jour » : coche-la, en citant le registre v8 du 23/10, tenu hors dépôt.
- « `AVANCEMENT.md` mis à jour » : coche-la après le Temps 2, en citant ce prompt.
- « Heures réelles saisies » et « Vélocité mesurée, clé révisée » : **ne les coche pas**. Ajoute en dessous : « Non tenu — aucune heure humaine relevée (registre v8, R23, réalisé et définitif). »
- Tâches transverses : vérifie chacune dans le dépôt.
  - Gabarits imprimables : `GabaritDocument`, `pdf/progression_realisee.html`, gabarits des procès-verbaux.
  - Wireframes Évaluations : cherche un fichier qui les contient réellement.
  - Contrôle K3 : vérifie si les écrans Instructeurs et Lieux ont été corrigés depuis le 08/09.

  Coche une tâche **seulement** si un fichier la prouve, et cite ce fichier. Sinon, laisse la case vide et écris ce qui manque. Une tâche non faite part au cahier de recette comme anomalie : ne la corrige pas ici.

## Temps 4 — Attribution rétrospective des porteurs (mesure de R16)

Crée `docs/suivi/PORTEURS-RETROSPECTIF.md` :
- **En-tête obligatoire** : « Attribution reconstituée après coup, le ___/___/2026, par le binôme. Elle est déclarée rétrospective : aucune ligne existante des suivis de sprint ni de `DECISIONS.md` n'a été réécrite. Motif : la colonne Porteur n'a pas été tenue pendant les sprints (registre v8, R16). »
- **Tableau des 52 stories livrées** avec les colonnes : sprint, code, titre, commit de clôture, **Porteur**, **Second (relecture ou binômage)**, observations.
  - Remplis sprint, code et titre depuis les fichiers `sprint-N.md`.
  - Remplis le commit de clôture **par `git log`**, en vérifiant chaque code. Le cas P-41 (deux stories dans un même commit au sprint 3) doit apparaître tel quel.
  - **Laisse Porteur et Second vides** : c'est l'étudiant et son binôme qui les rempliront. Tu n'as aucun moyen de connaître la contribution réelle, et la répartition prévue en phase 3 n'est pas la répartition réelle.
- Ajoute à la fin de chaque `sprint-N.md` (1 à 4) une ligne datée qui renvoie vers ce fichier. N'ajoute rien d'autre.
- Contrôle de cohérence : le tableau compte exactement 52 lignes, 15 + 12 + 11 + 14. Si `git log` ne retrouve pas un code de story, écris-le dans la colonne observations, sans corriger quoi que ce soit.

## Temps 5 — Addendum à la revue du sprint 4

À la fin de `REVUE-SPRINT-4.md`, ajoute une section « Addendum du 25/10/2026 (prompt 50) ». Ne modifie pas le corps de la revue. L'addendum dit :
1. Les trois reports « orphelins » sont rangés par le backlog v11 (voir le Temps 2) : il n'en reste aucun.
2. **Ligne US-REF-09 de `heures-sprint-4.md`** : l'étudiant ne peut pas confirmer s'il y a eu une pause. La ligne est tenue pour **non fiable** et ne sera citée comme temps de travail continu nulle part. `heures-sprint-4.md` n'est pas modifié.
3. **Jalon J3.** Le rapport d'avancement N°3, critère écrit du jalon, a été émis le 26/10, deux jours après l'échéance. Le contenu et les éléments de pilotage du dépôt étaient produits le 20/10. Le classeur v1.4 le consigne en réserve sur le jalon.
4. **Démonstration J2** : tenue le 10/10 devant les cellules (confirmé par l'étudiant le 25/10). Ses retours n'ont pas été consignés (registre v8, R17).

## Temps 6 — Contrôle et commit

1. `git status` et `git diff --stat` : **aucun fichier hors de `docs/`**. Si un autre fichier apparaît, annule sa modification et signale-le.
2. Relis chaque fichier modifié à sa destination (mesure de R19) : chaque note datée est présente, aucune ligne historique n'est altérée, chaque numéro de décision cité (D-182, D-212, D-215, D-268, D-289) a été **relu dans `DECISIONS.md`**. Aucun numéro ne doit être cité de mémoire. Ce prompt n'ouvre qu'une décision, celle du déploiement sur machine virtuelle (Temps 2) : si tu estimes qu'il en faut une autre, arrête-toi et demande.
3. Ne relance pas la suite de tests : aucun code n'est touché. Mentionne-le dans le commit.
4. Un seul commit : `Cloture documentaire du J3 et ouverture de la phase 6 (prompt 50)`.
5. Clôture la ligne de `heures-phase-6.md` avec l'heure de fin et le commit.

## Rendu attendu

- La liste des fichiers modifiés ou créés, avec une ligne par fichier.
- Pour le Temps 3 : chaque case, cochée ou non, avec sa preuve ou ce qui manque.
- Pour le Temps 4 : le nombre de lignes, les codes que `git log` n'a pas retrouvés, et le rappel que les colonnes Porteur et Second attendent le binôme.
- Le numéro attribué à la décision du déploiement sur machine virtuelle.
- Ce que tu as tranché seul, s'il y a eu quelque chose, et ce que tu n'as pas pu vérifier.
