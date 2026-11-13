# Prompt 58 — Corrections de RECETTE-01 (lots 1 et 2)

**Contexte.** Diagnostic du prompt 57 reçu et arbitré. Une correction s'impose sur A1, au vu d'un **constat nouveau du recetteur** (04/11, début de RECETTE-02, état `complet` fraîchement rechargé) : **avant** la génération de W+1, le contrôle E2 de EXP2 est visible le mercredi ; **après** la génération, il a disparu, remplacé par une séance générée sur le même créneau. A1 n'est donc pas un problème de navigation : **c'est A10**. La génération pose une séance sur le créneau d'une séance verrouillée de la même brigade, et l'affichage écrase la séance verrouillée. A1 est un **NC majeur**, de même cause que A10 et A6 (b).

**Organisation, impérative.** Le recetteur joue RECETTE-02 sur cette machine pendant que tu travailles.
- Travaille dans un **worktree git séparé** (`git worktree add`). Ne modifie jamais le répertoire de travail principal : `runserver` y tourne.
- Pendant le développement : **tests ciblés seulement**, sur la base de test, jamais sur `pfe_cit_recette`. **Aucune remise à zéro, aucune migration** sur `pfe_cit_recette`.
- La **suite complète** (P-51), `-m pdf` et `-m navigateur` ne se lancent **qu'après mon feu vert** : je te dirai quand RECETTE-02 est finie.
- Ensuite seulement, fusion dans la branche principale et étiquette.

Temps 0 : une ligne dans `heures-phase-6.md`.

---

## Lot 1 — défauts (NC majeurs et parcours bloqués)

| N° | Correction | Exigences |
|---|---|---|
| **K1 = A10, A1, A6 (b)** | **Une brigade ne peut pas avoir deux séances qui se chevauchent.** Aujourd'hui aucune contrainte ne l'interdit : RG-34 porte sur l'instructeur, RG-37 sur le lieu. | (1) **Contrainte dure** dans `ServiceContraintes`, donc appliquée à la génération, la modification manuelle, le regroupement, la substitution et la duplication. Une séance regroupée occupe le créneau pour chacune de ses brigades. Numéro de règle relu, pas supposé. (2) `construire_cases` exclut aussi les (brigade, créneau) déjà occupés, pour la performance et la clarté du compte rendu. (3) **L'affichage ne doit plus jamais écraser une séance en silence** : si deux lignes se chevauchent (données anciennes), les deux s'affichent avec un signalement visible. (4) Dis si `pfe_cit_volume` ou l'historique du chargeur `complet` contiennent de tels doublons : le chargeur, qui passe par les services, n'en produira plus. (5) Le refus de capacité de RG-40 doit redevenir atteignable dans le regroupement (R01-PLAN06-02) |
| **K2 = A4** | Salle attitrée | Comparer `candidate.lieu` à la salle attitrée de la brigade ; refuser la salle attitrée d'une **autre** brigade, et toute salle autre que celle de la brigade pour une matière « salle attitrée ». Même règle partout (une seule implantation) |
| **K3 = A3** | Élément de référentiel par la formation de la brigade | `FormulaireSeance` et `FormulaireSubstitutionSeance` : queryset filtré sur la formation de la brigade. Le volume affiché doit être celui de F6 pour EXP1 (M1 = 40 h) |
| **K4 = A6 (a)** | Regroupement | Brigades candidates filtrées par le référentiel de la matière (CDP1 non proposée pour M2) |
| **K5 = A11** | Lien « Y aller » | Mène à la consultation du programme concerné, où se trouve le vrai formulaire POST |
| **K6 = B1** | Chargeur `complet` | L'avenant « déplacement » doit être posé de façon fiable (RECETTE-03 en dépend). Si W0 n'a aucun créneau libre pour EXP1, choisis une solution qui garde l'avenant **en W0** (par exemple déplacer vers un créneau libéré par le chargeur lui-même), plutôt que de le poser dans une autre semaine. Le chargeur échoue bruyamment s'il ne peut pas poser l'avenant, au lieu d'avertir seulement. Ajoute à `--verifier` : « deux avenants sur la séance M6 de EXP1 en W0 » |
| **K7 = B2** | Fuseau horaire | Africa/Casablanca repasse à UTC+1 **après le 11/11**, en pleine recette (RECETTE-03 à 05). Trouve la source exacte de l'avertissement « naive datetime » et corrige-la si c'est le code de production. Teste une période bloquante à une date où le fuseau est à +1 |

## Lot 2 — ergonomie retenue

| N° | Correction | Exigences |
|---|---|---|
| **K8 = A2, E1 (créneau)** | Choix du créneau dans la grille active | Dans l'ajout et la modification manuelle, remplace la saisie des heures par **le choix d'un créneau de la grille active**. Mets à jour RG-64 (D-133) en le disant, par une nouvelle décision. **En plus**, une séance déjà hors grille (données anciennes, duplication depuis une autre grille) s'affiche dans une ligne « hors grille » du jour : plus jamais de séance invisible |
| **K9 = A5** | Avenants | Visibles sur l'écran de la séance (« Modifier ») ; dans la liste du programme, chaque avenant nomme sa séance (jour, créneau, brigade, matière) |
| **K10 = A7** | Non-exécution | Sur une séance d'un programme affiché qui n'est pas encore passée, un message dit pourquoi la déclaration de non-exécution n'est pas encore disponible et quand elle le sera |
| **K11 = A9** | Traitement en lot | Groupes par **matière et par semaine**, de sorte qu'on traite « M1 de I1 en W+2 » seule. Vérifie et teste le refus de l'ensemble quand le remplaçant est occupé sur une séance (US-PLAN-09 c.5) |

## Reporté (ne pas faire)

- **E1, listes filtrées par AJAX** (instructeurs qualifiés, matières du référentiel, lieux compatibles), qui couvre aussi A8. Le serveur refuse déjà les choix invalides : c'est du confort. Consigne-le en perspective dans `ECARTS-LIVRABLES-PHASE-6.md`.
- **Redirection vers le jour de la séance verrouillée** après génération (A1, option) : sans objet une fois K1 corrigé.

## Tests

- K1 : génération qui ne pose rien sur le créneau d'une séance verrouillée de la même brigade, **E2 conservée et visible après génération** (le scénario exact du recetteur) ; refus en modification manuelle et en regroupement ; séance regroupée qui occupe le créneau de chaque brigade ; affichage de deux lignes qui se chevauchent.
- Un test par autre correction. K7 : un test daté après le passage à UTC+1.
- La preuve sur la session entière (prompt 56) doit toujours passer.

## Fin

1. Relecture par `relecteur-conception` de K1, K2 et K8.
2. **Attends mon feu vert**, puis suite complète seule sur la machine, `-m pdf` en conteneur et `-m navigateur`.
3. Commits séparés : K1 ; K2-K3-K4 ; K5 ; K6 ; K7 ; lot 2 ; documentation (`PROBLEMES.md` pour chaque anomalie, décisions, écarts pour le backlog v12).
4. Fusion, puis étiquette **`recette-phase-6-c5`**.
5. Donne : les rapports `--verifier` des quatre états ; la liste des contrôles de RECETTE-01 à rejouer ; ce que tu as tranché seul.

**Temps limité** : estime le total avant de commencer. S'il dépasse 14 heures, arrête-toi et propose ce qu'on retire du lot 2.
