# Prompt 37 — Sprint 3 : correctif de mesure, puis US-EVAL-03

Phase 5, sprint 3. Deux temps, deux commits :
- **Temps 1** — un correctif de dette, hors story, révélé par ton § 0.2 du
  prompt 36.
- **Temps 2** — **US-EVAL-03** · 5 points · Must · BF-EVAL-03 · CU-P6-03 ·
  RG-50, RG-50 bis, RG-51 · BNF-02 · CLS-05.

Les arbitrages sont RENDUS. Si le code réel en rend un inexprimable,
ARRÊTE-TOI et signale-le avant d'écrire la suite.

---

## Temps 1 — La mesure de P-38 n'est gardée par rien

Ton § 0.2 du prompt 36 : `test_mesures_de_reference_us_plan_03_paragraphe_10`
« journalise sans asserter ». Or la leçon 3 du sprint 2
(`LECONS-SPRINT-2.md`) affirme l'inverse : « le test doit porter une
assertion sur le CHIFFRE lui-même… `test_mesures_de_reference_us_plan_03_
paragraphe_10` le fait désormais ». Si ton constat est exact, la mesure
corrective de la leçon 3 n'existe pas, et un retour de P-38 (6 requêtes par
séance) ne ferait échouer aucun test. C'est le motif même de la leçon :
une affirmation que rien ne mesure.

1. **Vérifie d'abord** : cherche le test qui prouve la « pente nulle de 40 à
   200 séances » annoncée dans la résolution de P-38 (`PROBLEMES.md`) — en
   ouvrant les tests de `ServiceEcritureSeance` et de la génération, pas par
   une seule recherche de motif. Cite-le s'il existe.
2. S'il n'existe pas, écris
   `test_p38_nombre_de_requetes_independant_du_nombre_de_seances_ecrites` :
   `creer_seances` sur 40 puis sur 200 séances, **égalité stricte** des deux
   nombres de requêtes. C'est la dimension qui avait échappé à I3. Vérifie
   qu'il échoue en réintroduisant temporairement l'écriture séance par séance,
   puis retire la réintroduction ; dis-le dans le rendu.
3. Transforme le test des mesures de référence : assertion
   `nombre_de_requetes <= REQUETES_REFERENCE_US_PLAN_03 + MARGE_REQUETES`,
   deux constantes nommées en tête du module (43 et 2), le commentaire
   disant d'où vient 43 (D-161 puis US-EVAL-02, D-185 et suivantes). Le temps
   reste journalisé sans assertion : il dépend de la machine.
4. `LECONS-SPRINT-2.md`, leçon 3 : ajoute un erratum daté — l'affirmation
   était fausse à la clôture du sprint 2, corrigée ce jour, par quel test.
   Ne réécris pas le texte d'origine.
5. Joins les deux corrections restées en suspens après US-EVAL-01, si elles
   ne sont pas faites : date unique de la ligne d'US-EVAL-01 dans
   `heures-sprint-3.md` ; erratum 1 430 → 1 432 dans
   `MESURES-REFERENCE.md`.

Une entrée `PROBLEMES.md` (P-suivant) : constat, cause (une assertion
annoncée en clôture sans relecture du test), résolution, leçon.

Commit : `test(planification): garde réelle de la mesure P-38`.

---

## Temps 2 — US-EVAL-03 : Enregistrer les sujets et sélectionner celui retenu

### 0. Vérifications préalables — lecture seule

Même règle : arrêt sur condition d'arrêt seulement, sinon enchaîne.

1. Le mécanisme de journal : peut-il consigner une **consultation** (une
   lecture), ou seulement des écritures ? Natures existantes ; précédent
   d'ajout d'une nature hors RG-26 (D-153).
2. Qui lit le journal aujourd'hui (profils, écrans, export) ?
3. `app/evaluations/admin.py` et l'admin Django en général : quels modèles
   y sont enregistrés, quels profils y accèdent ?
4. **Condition d'arrêt** : si le journal ne peut consigner qu'une écriture et
   que l'y faire entrer une consultation suppose de modifier le contrat
   d'un service de `noyau` utilisé partout, rends-moi le code et j'arbitre.

### 1. Le besoin

*En tant que membre de la cellule examens, je veux enregistrer les sujets que
l'instructeur m'a transmis hors système puis la décision de la commission sur
celui retenu, afin de limiter les risques de divulgation.*

| # | Critère | Source |
|---|---|---|
| C1 | L'instructeur n'a aucun accès : les sujets sont saisis par la cellule examens | US-EVAL-03 c.1 |
| C2 | Certificative : deux sujets au plus, un seul retenu. Formative : un sujet unique, sans sélection | RG-50, E1 |
| C3 | Le sujet retenu est une décision **de la commission**, enregistrée par la cellule examens, horodatée et rattachée à l'agent qui la saisit | RG-50 bis, US-EVAL-03 c.3 |
| C4 | Certificative à un seul sujet : avertissement et confirmation explicite, jamais de blocage | CU-P6-03 A2 |
| C5 | Changer le sujet retenu avant l'épreuve : admis, motif obligatoire mentionnant la décision de commission | A3 |
| C6 | Sélection ou changement à partir du jour de l'épreuve : refusé | E2 |
| C7 | Les sujets ne sont visibles que de la cellule examens ; chaque consultation est journalisée | RG-51, BNF-02, A4 |
| C8 | Une évaluation sans sujet est signalée « non prête » dans la liste des évaluations à venir | E3 |
| C9 | Aucune évaluation certificative ne peut être organisée sans sujet retenu — garde exposée ici, appliquée par US-EVAL-04 | US-EVAL-03 c.7 |

### 2. Arbitrages rendus

**A1 — Le système ne stocke qu'une référence, jamais le sujet.** CLS-05 :
`Sujet.reference` (texte) et `dateDepot`. Le sujet lui-même reste sur papier,
hors système : aucun téléversement, aucun contenu. La référence désigne le
document (« Sujet A — pli n° 12 »), elle ne le reproduit pas. C'est la
première protection de BNF-02 : ce qui n'est pas stocké ne fuit pas.

**A2 — Deux sujets au plus, garantis en base par un rang.** `Sujet.rang`
vaut 1 ou 2 (CHECK), unique par évaluation : un troisième sujet est
impossible en base, pas seulement refusé par le service. La limite à un sujet
pour une formative dépend du type, porté par une autre table : couche
services, testée.

**A3 — Un seul retenu, garanti en base.** Index unique partiel sur
l'évaluation, limité aux sujets retenus. Pour une formative, `retenu` reste
faux : le sujet unique n'est pas « sélectionné », il est le sujet (RG-50).
Refus en service, testé.

**A4 — Qui a retenu, quand : le journal, pas des colonnes.** L'horodatage et
l'agent de la sélection (C3) vivent dans l'entrée de journal, sur le précédent
de D-132. Pas de `retenu_le` ni `retenu_par` : ce serait un second
historique, incomplet dès le premier changement de sujet (C5). Le détail
affiche l'auteur et la date tirés du journal.

**A5 — La visibilité des sujets suit `evaluations_ecriture`.** La matrice
donne `evaluations_lecture` à la Direction de Formation, mais les sujets
doivent lui rester cachés. Pas de dix-neuvième permission : celui qui gère
les évaluations est celui qui détient les sujets. Les sujets vivent sur un
**écran dédié**, refusé en 403 à quiconque n'a pas `evaluations_ecriture` —
pas simplement masqué dans un gabarit. Le détail de l'évaluation, lisible par
la Direction de Formation, n'affiche que « 2 sujets enregistrés — sujet
retenu : oui / non », sans référence ni rang du retenu.

**A6 — Chaque affichage de l'écran des sujets est journalisé (RG-51).**
Nouvelle nature de journal `CONSULTATION_SUJETS`, hors RG-26, sur le patron
de D-153. Une entrée par GET réussi, y compris quand rien n'a changé — c'est
la consultation qu'on trace, pas la modification. Un GET refusé (403) n'en
crée pas.

**A7 — Le journal ne contient jamais une référence de sujet.** Les entrées
de sélection, de changement et de consultation désignent le sujet par son
**rang** (« sujet n° 2 »). Sinon, le journal deviendrait lui-même une copie
lisible des références, par d'autres profils que la cellule examens.

**A8 — Aucun accès par l'admin Django.** `Sujet` n'est pas enregistré dans
l'admin : il contournerait à la fois la restriction (A5) et la journalisation
(A6). Un test le garantit. Le `__str__` de `Sujet` ne renvoie pas la
référence, mais l'évaluation et le rang : un message d'erreur ou une trace ne
la divulguent pas.

**A9 — Le jour de l'épreuve est la borne (E2).** L'heure de l'épreuve
n'existe qu'avec l'organisation (US-EVAL-04). Sans elle, la seule borne sûre
est le jour : à partir du jour de l'épreuve, sélection, changement et
suppression du retenu sont refusés. Le choix penche vers la sécurité (RG-51)
plutôt que vers la souplesse d'un changement le matin même.

**A10 — Modifier et supprimer un sujet.** Un sujet non retenu se corrige ou
se supprime avant l'épreuve. Un sujet retenu ne se supprime pas : on change
d'abord la sélection (C5). Pour une formative, le sujet unique se corrige à
tout moment, y compris après coup (le contrôle déclaré après coup de
US-EVAL-01 admet son sujet ensuite).

**A11 — « Non prête » est calculé.** Certificative à venir sans sujet retenu,
ou formative à venir sans sujet : badge dans la liste. Jamais un champ.
Requête unique pour toute la liste.

**A12 — La garde de C9 est un prédicat.** `ServiceSujet.sujet_retenu(
evaluation)` rend le sujet retenu ou `None`. US-EVAL-04 refusera
l'organisation quand il rend `None` ; report vers US-EVAL-04, testé ici sur
le prédicat seul.

### 3. Modèle et contraintes en base

`Sujet` (application `evaluations`), sur la classe de base horodatée :

| Champ | Type |
|---|---|
| `evaluation` | FK `Evaluation`, `CASCADE` (un sujet n'a pas de sens sans son évaluation) |
| `rang` | entier, 1 ou 2 |
| `reference` | texte court |
| `date_depot` | date |
| `retenu` | booléen, faux par défaut |

| Contrainte | Règle | Contenu |
|---|---|---|
| `ck_sujet_rang` | RG-50 | rang ∈ {1, 2} |
| `uq_sujet_evaluation_rang` | RG-50, E1 | (évaluation, rang) unique — au plus deux sujets |
| `uq_sujet_un_seul_retenu` | RG-50 | évaluation unique parmi les sujets retenus (index partiel) |
| `ck_sujet_reference_non_vide` | C1 | référence non vide après suppression des blancs |
| `uq_sujet_reference` | — | (évaluation, référence) unique, insensible à la casse |

Hors base : formative limitée à un sujet et jamais retenu (type sur une autre
table) ; date de dépôt non future ; bornes du jour de l'épreuve. Services,
testés.

**Attention à `CASCADE`** : la suppression d'une évaluation n'est pas offerte
(report D-181 vers US-PLAN-05) ; quand elle le sera, elle emportera les
sujets. Vérifie qu'aucun `PROTECT` ailleurs ne contredit ce choix.

### 4. Fichiers

- `app/evaluations/models.py`, migration
- `app/evaluations/services/sujet.py` — `ServiceSujet` : `enregistrer`, `corriger`, `supprimer`, `retenir`, `changer_retenu`, `consulter`, `sujet_retenu`
- formulaires, vues, gabarits de l'écran des sujets ; badge « non prête » dans la liste ; résumé non sensible dans le détail
- nature de journal `CONSULTATION_SUJETS`
- tests

### 5. Cas de test attendus

**A — Base**
- A1 troisième sujet (rang 3) → `IntegrityError` ; A2 deux sujets de même rang → `IntegrityError`
- A3 deux sujets retenus pour une évaluation → `IntegrityError`
- A4 référence blanche → `IntegrityError` ; A5 même référence, casse différente → `IntegrityError`
- A6 aucune colonne `retenu_le` / `retenu_par` (constat du schéma, A4)

**B — Règles**
- B1 certificative : deux sujets enregistrés, un retenu ; journal avec auteur, date, rang — sans référence (A7)
- B2 formative : second sujet refusé ; tentative de retenir son sujet refusée
- B3 certificative à un seul sujet : `retenir` sans confirmation → refus porteur de l'avertissement ; avec confirmation → admis, journal mentionnant la dérogation à RG-50
- B4 changement de retenu avec motif → admis, journal ancien et nouveau rang ; sans motif ou motif blanc → refus
- B5 sélection, changement, suppression du retenu le jour de l'épreuve puis le lendemain → refus (A9)
- B6 date de dépôt future → refus
- B7 suppression d'un sujet retenu → refus ; d'un sujet non retenu avant l'épreuve → admise
- B8 formative déclarée après coup : sujet enregistré après sa date → admis (A10)
- B9 `sujet_retenu` rend `None` sans sélection, le sujet sinon (A12)

**C — Confidentialité**
- C1 chaque GET de l'écran des sujets par la cellule examens crée exactement une entrée `CONSULTATION_SUJETS` ; deux GET, deux entrées
- C2 GET refusé (403) : aucune entrée
- C3 aucune entrée de journal, toutes natures confondues, ne contient le texte d'une référence (recherche sur l'ensemble du journal après un scénario complet)
- C4 `Sujet` absent de l'admin Django (A8) ; `str(sujet)` ne contient pas la référence
- C5 détail de l'évaluation lu par la Direction de Formation : ni référence ni rang du retenu dans le HTML

**D — Habilitations**
- D1 Direction de Formation : écran des sujets en 403, toutes actions refusées en service
- D2 planification, pédagogique, administrateur : 403
- D3 nouvelles vues ajoutées à `ECRANS_ECRITURE` et, pour l'écran de consultation, au test de lecture équivalent ; refus paramétrés verts

**E — Cycle HTTP réel**
- E1 POST de deux sujets puis POST de retenue par la cellule examens : redirection, écran des sujets marquant le retenu, deux entrées de journal d'écriture et une de consultation par affichage
- E2 POST de retenue à sujet unique sans case de confirmation : formulaire réaffiché avec l'avertissement, rien de retenu en base
- E3 POST d'un troisième sujet : formulaire réaffiché avec l'erreur, deux sujets en base
- E4 liste des évaluations à venir : badge « non prête » sur la certificative sans retenu ; nombre de requêtes identique avec 1 et 10 évaluations
- E5 GET de l'écran des sujets par la Direction de Formation : 403, aucune entrée de journal

### 6. Suivi

**`DECISIONS.md`** — une entrée par arbitrage A1 à A12, « imposée par le
prompt 37 ». **Numérote au moment d'écrire chaque entrée dans
`DECISIONS.md`, jamais dans un brouillon** : c'est la cause des deux erreurs
de citation relevées en relecture sur US-EVAL-01 et US-EVAL-02. Une citation
dans `AVANCEMENT.md` ou dans les écarts ne s'écrit qu'après l'entrée qu'elle
cite.

**Reports** — nouveau : C9, organisation refusée sans sujet retenu →
US-EVAL-04. Aucun fermé. Recompte.

**`ECARTS-LIVRABLES-SPRINT-3.md`** — à la suite :
- CLS-05 : `Sujet` sans rang ; la limite à deux y est une multiplicité, ici garantie en base par le rang (A2)
- cahier des charges : `CONSULTATION_SUJETS`, cinquième nature hors RG-26, à porter avec les quatre autres (écart 11 du sprint 2)

**Définition de fini (R23)** — case dans `sprint-3.md`, ligne au tableau des
sprints d'`AVANCEMENT.md`, ligne dans `heures-sprint-3.md` (une date par
jour réellement traversé, début noté avant le § 0, fin à l'heure du commit).
Le temps 1 a sa propre ligne, élément « correctif P-38 », sans points.

### 7. Avant de conclure

1. `pytest` complet et `pytest tests/architecture -q` : totaux et écart avec 1 515.
2. Relecture par `relecteur-conception` : A5 à A8 (confidentialité) en
   priorité, puis chaque numéro de décision cité contre `DECISIONS.md`.
3. Commit : `feat(evaluations): US-EVAL-03 sujets et sujet retenu`.
4. Rends-moi, sans que je le redemande : résultats du § 0, le test P-38
   trouvé ou écrit avec la preuve de son échec, totaux, reports, et ce que
   tu n'as pas pu vérifier.
