# Prompt 45 — Sprint 4 : trois correctifs, puis US-SUI-06

Phase 5, sprint 4. Deux temps, deux commits au moins, **un seul rendu à la fin**.
Règles inchangées : arrêt sur les seules conditions écrites ici ; pour le reste,
tu tranches selon les trois principes d'arbitrage, tu consignes, tu continues ;
aucun numéro de décision cité de mémoire ; heure de début écrite avant toute
autre action ; auteur des décisions = porteur inscrit dans `sprint-4.md`.

---

## Temps 1 — Trois correctifs, avant toute story

### 1.1 La suite doit redevenir verte (P-43)

Un échec reproductible cinq fois sur cinq n'est pas un échec intermittent :
c'est un test rouge. La suite était entièrement verte à J2 (deux exécutions
complètes le 10 octobre) ; ce test échoue sans aucun changement du prompt 44.
Hypothèse la plus probable : **un test dépendant de la date du jour**, qui
place un jour d'examen relativement à « aujourd'hui » et franchit une borne
(semaine, mois, bornes de session) depuis le 10 octobre.

1. Établis la cause, en lisant le test et ce qu'il appelle — pas par hypothèse.
2. Si c'est la date : le test fige sa date de référence ; il ne dépend plus du
   jour d'exécution. Cherche dans toute la suite les autres tests qui construisent
   leurs données à partir de la date du jour sans la figer, et dresse-en la liste ;
   corrige ceux qui peuvent franchir une borne de semaine ou de mois.
3. Si c'est un défaut du code : corrige le code, pas le test.
4. Suite complète verte, puis consigne P-43 (constat, cause, résolution, leçon).

### 1.2 La marge de requêtes ne se consomme pas en silence

La génération est passée de 47 à 49 requêtes : la marge de 2 est entièrement
consommée. La règle posée au prompt 36 (A8) s'applique : on ne laisse pas la
marge s'épuiser, on **relève la référence** avec une note datée. Porte
`REQUETES_REFERENCE_US_PLAN_03` à **49**, marge maintenue à 2, note datée dans
le code et dans `MESURES-REFERENCE.md` (cause : chargement du réalisé pour le
contrôle des prérequis, deux chargements du contexte par génération).

Ajoute à `MESURES-REFERENCE.md` la série complète 41 → 43 → 45 → 47 → 49 avec
la cause de chaque pas. Ce n'est pas une dérive tant que chaque pas est constant
et expliqué ; c'est ce tableau qui le prouve.

### 1.3 D-264 est révisée : la matrice d'habilitation fait foi

L'erreur vient du prompt 44, qui ne citait que deux profils pour la lecture du
suivi. Le backlog a déjà connu trois fois ce défaut d'omission (US-REF-07,
US-SES-04, fiche CU-P3-05), et la règle arrêtée chaque fois est la même : **la
matrice d'habilitation fait foi** sur un critère qui omet un profil. Elle donne
la lecture du domaine « suivi » à la planification, aux examens et à la
Direction de Formation, l'écriture à la pédagogique. La planification en a
d'ailleurs besoin : c'est elle qui déclare les non-exécutions et qui édite la
progression réalisée.

1. Rétablis la matrice telle que § 11.2 la porte, et ses tests.
2. Nouvelle décision qui révise D-264, cite la règle de précédent et nomme la
   cause : un critère d'acceptation incomplet, pas un choix de conception.
3. Écart au registre : le critère C5 d'US-SUI-01 au backlog v10 omet deux
   profils — correction à porter au backlog v11.

### 1.4 `AVANCEMENT.md`

Recalcule les indicateurs cumulés : stories et points livrés sur tout le projet
(176 points attendus après le prompt 44 : 169 + 7), sprint 4 à 2 stories sur 14.

Commit : `fix: test daté (P-43), référence de requêtes, matrice du suivi`.

---

## Temps 2 — US-SUI-06 : Éditer la progression réalisée hebdomadaire

3 points · Must · BF-SUI-06 · RG-58, RG-60 · maquette MAQ-05.

**Critères (backlog v10)**

| # | Critère |
|---|---|
| C1 | Pour chaque brigade et chaque matière : volume programmé de la semaine et volume effectivement dispensé |
| C2 | Les écarts sont détaillés : non-exécutions avec leur motif, séances reportées, avenants de la semaine avec leur nature et leur motif |
| C3 | Une séance reportée puis tenue n'est pas un écart : le réalisé est inchangé |
| C4 | Le document est entièrement calculé ; aucune donnée n'y est saisie deux fois |
| C5 | Le système enregistre la date d'édition et l'agent ; s'il est signé, la date et le nom du signataire |
| C6 | Le document est produit à partir d'un gabarit paramétrable |

**Arbitrages**

- **P1 — Le document est calculé, seule l'édition est enregistrée.** Un modèle
  `EditionProgression` : semaine, édité le, édité par, et, facultativement, date
  de signature et signataire (même règle qu'au programme : tous deux ou aucun,
  date non future, garanti en base). Aucune ligne du document n'est stockée :
  rééditer recalcule. Plusieurs éditions d'une même semaine sont possibles et
  toutes conservées ; la plus récente fait foi.
- **P2 — Une seule définition du réalisé.** Le dispensé d'une ligne est la
  fonction posée à US-SUI-01, à la date T = fin de la semaine ou instant de
  l'édition si celle-ci a lieu avant. Une séance pas encore terminée figure
  comme « à venir » et ne compte pas au dispensé. Aucun second calcul.
- **P3 — « Reportée » se lit sur les avenants.** Il n'existe pas d'entité de
  report. Sur un programme affiché, une séance déplacée dans la semaine porte un
  avenant de nature « déplacement » : c'est cela, une séance reportée au sens de
  C2, et elle compte au dispensé si elle a eu lieu (C3). Un report vers une autre
  semaine passe par une non-exécution suivie d'un ajout la semaine suivante :
  le document de chaque semaine le montre tel quel. Consigne-le comme écart de
  vocabulaire avec BF-SUI-06.
- **P4 — Programme affiché seulement.** L'édition est refusée pour une semaine
  dont le programme n'est pas affiché : il n'y a pas de dispensé sans programme
  affiché (RG-60).
- **P5 — Le gabarit paramétrable (RG-58), posé ici pour toute la suite.** Vérifie
  d'abord ce qui existe (gabarit d'impression de la convocation, paramètres
  d'impression, WeasyPrint). Le document est produit **en PDF par WeasyPrint**,
  bibliothèque arrêtée au jalon C1. En-tête, mentions et bloc de signature sont
  des **données** : un modèle de gabarit par type de document, éditable par
  l'administrateur, avec un jeu initial chargé par commande (jamais par
  migration de données, leçon de D-122). US-EVAL-07 (procès-verbal) réutilisera
  ce mécanisme : conçois-le pour deux types au moins. **Condition d'arrêt** :
  si WeasyPrint n'est pas installable ou ne s'exécute pas dans l'environnement
  de test, arrête-toi et montre-le-moi — le procès-verbal en dépend.
- **P6 — Mise en page.** Une section par brigade, saut de page entre brigades,
  brigades groupées par type de formation comme le programme. Polices
  embarquées, aucune ressource en ligne (BNF-06).
- **P7 — Habilitations.** Éditer et enregistrer la signature : la cellule
  planification, avec la même permission que la déclaration de non-exécution
  (US-SUI-05) — aligne-toi sur ce que le prompt 44 a retenu, ne crée pas une
  troisième voie. Consulter et télécharger une édition : lecture du domaine
  « suivi », donc les quatre profils de la matrice rétablie au temps 1.3.
- **P8 — Journal.** L'édition est journalisée ; une nature existante si l'une
  convient.

**Tests attendus**
- calcul : programmé et dispensé par brigade et matière ; non-exécution
  retranchée avec son motif ; avenant listé avec nature et motif ; déplacement
  dans la semaine compté au dispensé (C3) ; séance à venir non comptée ;
  séance regroupée comptée pour chaque brigade
- base : signature incomplète refusée ; date de signature future refusée
- service : édition refusée hors programme affiché ; deux éditions conservées
- gabarit : en-tête et mentions modifiés par l'administrateur apparaissent dans
  le PDF suivant, sans changement de code
- PDF : le document se génère ; il contient les intitulés attendus (extraction
  de texte) ; aucune requête réseau
- HTTP : édition par la planification, téléchargement par la Direction ;
  édition par la pédagogique refusée ; requêtes de la génération du document
  constantes avec 2 et 10 brigades
- architecture : aucun calcul de dispensé hors de la fonction d'US-SUI-01

Commit : `feat(suivi): US-SUI-06 progression réalisée hebdomadaire`.

---

## Suivi et rendu

Décisions, reports, écarts (dont P3 et le critère C5 d'US-SUI-01), définition
de fini complète, relecture `relecteur-conception` avant chaque commit.

Rendu final, en français, en une fois : cause de P-43 et liste des tests datés ;
suite complète ; requêtes ; état de WeasyPrint ; décisions ; reports ; ce que
tu as tranché seul ; ce que tu n'as pas pu vérifier, dont le rendu visuel du PDF.
