# Jeu de données de démonstration — Sprint 1

Prompt 15, WBS 5.1.17. Chargé par `python manage.py charger_jeu_demonstration`
(`--reinitialiser` pour recharger le référentiel et les ressources — jamais les
comptes ni le journal, voir D-59/P-28). Code : `app/ressources/jeu_demonstration/`
et `app/ressources/management/commands/charger_jeu_demonstration.py`.

Toutes les données sont fictives (§ 1.1 du prompt) : aucun nom, matricule ou
intitulé réel du CIT.

**Mot de passe commun** : `Transmissions#2026`

## Comptes

| Identifiant | Profil | État particulier | Démontre |
|---|---|---|---|
| `adm.demo` | Administrateur | — | Accès complet, gestion des comptes, journal |
| `ped.demo` | Cellule pédagogique | — | Écriture sur le référentiel et les instructeurs |
| `pla.demo` | Cellule planification | — | Écriture sur les lieux, lecture du référentiel |
| `exa.demo` | Cellule examens | — | Lecture du référentiel, aucun accès aux instructeurs |
| `dir.demo` | Direction de formation | — | Lecture partout, écriture nulle part |
| `ped.inactif` | Cellule pédagogique | Désactivé | Critère 3, US-ADM-02 |
| `ped.nouveau` | Cellule pédagogique | Changement de mot de passe exigé | Intergiciel d'US-ADM-02 |
| `ver.demo` | Cellule pédagogique | Verrouillé (déverrouillage dans le futur) | RG-03, critère E3 de CU-P1-01 |

Le journal est peuplé au chargement : créations des huit comptes, une
modification (`pla.demo`), un cycle désactivation → réactivation →
désactivation sur `ped.inactif`, un refus d'habilitation (`exa.demo` tente de
lister les instructeurs), le verrouillage de `ver.demo` (cinq échecs
consécutifs, seuil `AUTH_SEUIL_ECHECS`), et deux échecs suivis d'un succès sur
`ped.demo`. Neuf natures distinctes au total — de quoi démontrer les filtres
de l'écran US-ADM-04.

## Types de formation — US-REF-00

`Officiers`, `Sous-officiers`, `CAT-2`, et `Perfectionnement civil` (archivé) :
démontre qu'un type archivé disparaît des listes de sélection sans disparaître
de la consultation.

## Formations — US-REF-01

| Intitulé | Type | Durée | Démontre |
|---|---|---|---|
| Formation initiale | Officiers | 20 sem. | Référentiel complet, prérequis |
| Formation initiale | Sous-officiers | 24 sem. | Écart 1 (CU-P2-02) — même intitulé, type différent |
| Perfectionnement radio | CAT-2 | 8 sem. | Écran d'orientation des prérequis, vide |
| Spécialisation chiffre | Officiers | 6 sem. | Écart volume/durée au-delà du seuil, critère 5 US-REF-03 |
| Stage transmissions | CAT-2 | 4 sem. | Archivée |

## Matières — US-REF-02

Douze au catalogue. Huit sont rattachées normalement à un ou plusieurs
référentiels (Procédures radio, Chiffre et sécurité, Topographie, Réseaux de
campagne, Ordre serré, Éducation physique, Transmissions de données,
Protection électronique). Les quatre restantes ont un rôle précis :

| Matière | Démontre |
|---|---|
| Secourisme | Rattachée à deux formations (Officiers, Sous-officiers) avec des volumes différents — critère 3, US-REF-03 |
| Règlement de discipline | Rattachée à un référentiel (Spécialisation chiffre) sans aucun instructeur qualifié — critère 4, US-INS-02 |
| Anglais technique | Rattachée à rien : seule matière du jeu que la recette peut supprimer |
| Entretien du matériel | Archivée |

## Composition des référentiels — US-REF-03, US-REF-04

Chaque formation non archivée reçoit cinq à huit matières. Les trois
catégories de lieu apparaissent : salle attitrée (majorité des rattachements),
lieu partagé — un exemple de chacun des trois types (Topographie/salle
spécialisée, Secourisme/laboratoire, Chiffre et sécurité/amphithéâtre dans
Perfectionnement radio) —, et aucun lieu requis (Ordre serré, Éducation
physique). Les volumes se calculent depuis `VOLUME_HORAIRE_HEBDOMADAIRE_
REFERENCE` (jamais en dur) : exacts pour Officiers, Sous-officiers et
Perfectionnement radio (`depasse_seuil = False`), délibérément 50 % excédentaires
pour Spécialisation chiffre (`depasse_seuil = True`).

## Objectifs pédagogiques — US-REF-05

- **Transmissions de données** : quatre objectifs, ordres 1 à 4 — matière sur
  laquelle la recette exerce l'échange de positions et la contrainte différée.
- **Procédures radio** : deux objectifs.
- **Topographie** : un objectif.
- Les neuf autres matières n'en portent aucun.

## Prérequis — US-REF-06

Dans le référentiel de *Formation initiale — Officiers* :
Procédures radio → Transmissions de données → Protection électronique, plus un
lien latéral (Protection électronique exige aussi Chiffre et sécurité) pour
que l'ordre topologique ne soit pas trivial. *Perfectionnement radio* n'a
aucun prérequis : démontre l'écran d'orientation vide.

Aucun cycle n'est chargé (§ 3.7 du prompt) — voir « Actions laissées à la
recette » ci-dessous.

## Instructeurs — US-INS-01

Dix instructeurs : six militaires du centre actifs avec matricule, un
militaire archivé (Sqalli Imane), deux vacataires, un civil. Spécialités
réparties sur cinq valeurs (transmissions, chiffre, électronique, sport,
langues) pour un filtre exploitable sans être un fouillis.

## Qualifications — US-INS-02

Couverture volontairement partielle :

| Cas | Objet | Démontre |
|---|---|---|
| Aucun instructeur qualifié | Règlement de discipline | Critère 4 — signalement visuel |
| Un seul instructeur qualifié | Protection électronique (Ouazzani Sara) | E2 — avertissement au retrait, laissé à la recette |
| Deux à quatre qualifiés | Les huit autres matières rattachées | Cas normal |
| Instructeur sans aucune qualification | Belhaj Omar | Fiche vide |

Les deux vacataires et le civil reçoivent chacun une qualification (Guessous
→ Topographie, Rifai → Éducation physique, Kabbaj → Chiffre et sécurité) :
Belhaj reste le seul instructeur actif « qualifié pour rien ». L'instructeur
archivé (Sqalli Imane) n'a également aucune qualification, mais n'apparaît
plus dans les écrans de qualification — sa fiche vide n'y est jamais visible.

## Lieux et indisponibilités — US-PLAN-02

Onze lieux : cinq salles attitrables (capacités 20 à 32), un amphithéâtre
(150), deux laboratoires (16, 18), deux salles spécialisées (12, 24), une
salle archivée. Capacités variées pour le filtre de capacité minimale (RG-37).

Quatre indisponibilités, dates calculées par rapport à l'exécution (jamais en
dur) :

- Salle 101 : une période passée, close.
- Salle 101 : une période future.
- Salle 101 : une période contiguë à la précédente (débute exactement quand
  elle finit) — acceptée, cas limite de la contrainte d'exclusion.
- Salle 102 : une période qui recouvre la fenêtre future de la Salle 101 —
  admise puisque le lieu diffère : la contrainte porte sur le couple
  (lieu, période), jamais sur la période seule.

## Actions vivantes laissées à la recette

Le prompt les réserve délibérément à un geste manuel, pas au chargement :

- Créer un cycle de prérequis sur le référentiel Officiers, pour voir le
  refus et la chaîne affichée (RG-09/RG-10).
- Retirer la qualification unique de Protection électronique, pour voir
  l'avertissement E2.
- Réordonner (monter/descendre) les objectifs de Transmissions de données.
- Supprimer la matière orpheline « Anglais technique ».
- Verrouiller un compte en trois tentatives manuelles depuis l'écran de
  connexion (le compte `ver.demo` du jeu est déjà verrouillé par le
  chargement, pour ne pas obliger la recette à le refaire).

## Critères non couverts

Aucun critère d'acceptation des quinze stories du sprint 1, parmi ceux
énumérés au § 3 du Prompt 15, ne reste sans donnée pour l'exercer. Les points
ci-dessus (« actions vivantes ») ne sont pas des lacunes : le prompt les
réserve explicitement à un geste de recette, pas au chargement automatique.
