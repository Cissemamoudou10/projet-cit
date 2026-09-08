# Catalogue et matrice d'habilitation — US-ADM-03

Source unique : § 11.2 du dossier des cas d'utilisation. Le code vérifiable
est `app/noyau/models.py` (`Habilitation.Meta.permissions`) pour le
catalogue, et `app/administration/management/commands/initialiser_habilitations.py`
(`MATRICE`) pour le rattachement aux groupes.

## Le catalogue — 18 permissions

Toutes préfixées `noyau.` pour `has_perm()` (le modèle sans table vit dans
`noyau`).

| Domaine § 11.2 | Code | Lecture | Écriture |
|---|---|---|---|
| P1 — Administration | `administration` | `noyau.administration_lecture` | `noyau.administration_ecriture` |
| P2 — Référentiel | `referentiel` | `noyau.referentiel_lecture` | `noyau.referentiel_ecriture` |
| P3 — Organisation | `organisation` | `noyau.organisation_lecture` | `noyau.organisation_ecriture` |
| P4 — Instructeurs et qualifications | `instructeurs_qualifications` | `noyau.instructeurs_qualifications_lecture` | `noyau.instructeurs_qualifications_ecriture` |
| P4 — Lieux et calendrier | `lieux_calendrier` | `noyau.lieux_calendrier_lecture` | `noyau.lieux_calendrier_ecriture` |
| P5 — Génération et modification du programme | `programme` | `noyau.programme_lecture` | `noyau.programme_ecriture` |
| P5 — Validation du programme | `programme_validation` | `noyau.programme_validation_lecture` | `noyau.programme_validation_ecriture` |
| P6 — Évaluations | `evaluations` | `noyau.evaluations_lecture` | `noyau.evaluations_ecriture` |
| P6 — Suivi | `suivi` | `noyau.suivi_lecture` | `noyau.suivi_ecriture` |

Noms de domaine composés (`instructeurs_qualifications`, `lieux_calendrier`) :
voir `docs/suivi/DECISIONS.md`, D-11.

## La matrice de rattachement, croisement par croisement

**É** = lecture + écriture. **L** = lecture seule. Case vide = aucune des deux.
Reproduit tel quel depuis § 11.2 — aucun écart.

| Domaine | Pédagogique | Planification | Examens | Direction | Administrateur |
|---|---|---|---|---|---|
| `administration` | — | — | — | — | **É** |
| `referentiel` | **É** | L | L | L | — |
| `organisation` | **É** | L | L | L | — |
| `instructeurs_qualifications` | **É** | L | — | L | — |
| `lieux_calendrier` | L | **É** | L | L | — |
| `programme` | — | **É** | — | L | — |
| `programme_validation` | **É** | L | — | L | — |
| `evaluations` | — | — | **É** | L | — |
| `suivi` | **É** | L | L | L | — |

**Vérification croisée** (27 croisements marqués sur 45 possibles — 5 groupes
× 9 domaines : 9 en écriture, 18 en lecture — correction du 2026-09-08, la
version précédente confondait croisements marqués et octrois de permission,
voir ci-dessous) : chaque ligne porte exactement un **É**, jamais deux —
c'est ce qui porte la validation croisée entre planification (écrit le
programme, § P5 génération) et pédagogique (le valide, § P5 validation), sans
qu'aucun profil ne cumule les deux.

## Total de permissions par groupe

| Groupe | Nombre de permissions | Détail |
|---|---|---|
| Administrateur | 2 | `administration` (É) |
| Cellule pédagogique | 11 | `referentiel`(É), `organisation`(É), `instructeurs_qualifications`(É), `lieux_calendrier`(L), `programme_validation`(É), `suivi`(É) |
| Cellule planification | 9 | `referentiel`(L), `organisation`(L), `instructeurs_qualifications`(L), `lieux_calendrier`(É), `programme`(É), `programme_validation`(L), `suivi`(L) |
| Cellule examens | 6 | `referentiel`(L), `organisation`(L), `lieux_calendrier`(L), `evaluations`(É), `suivi`(L) |
| Direction de formation | 8 | `referentiel`(L), `organisation`(L), `instructeurs_qualifications`(L), `lieux_calendrier`(L), `programme`(L), `programme_validation`(L), `evaluations`(L), `suivi`(L) — **uniquement de la lecture**, conforme au critère 2 |

Somme : 2 + 11 + 9 + 6 + 8 = 36 octrois, cohérente avec le décompte des
cellules marquées dans la matrice (9 × **É** valant deux octrois + 18 × **L**
valant un octroi = 18 + 18 = 36).

## Écarts à § 11.2

Aucun. La matrice ci-dessus est une transcription mécanique, croisement par
croisement, sans interprétation ni simplification — la scission P4/P5 en
neuf lignes (pas six paquetages) est conservée telle quelle, comme le prompt
l'exige explicitement.
