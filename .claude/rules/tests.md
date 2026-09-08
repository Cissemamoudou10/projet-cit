---
paths:
  - "**/tests/**.py"
  - "**/test_*.py"
  - "**/conftest.py"
---

# Tests

pytest. Un test par critère d'acceptation, écrit au fil du développement.

Nommage en français : `test_refuse_une_seance_sans_instructeur_qualifie`.

## Ce que le jeu d'essai doit contenir

Sans ces situations, les contraintes ne sont jamais exercées.

- trois sessions simultanées de formations différentes — résolution centre-entier
- une session à trois brigades aux progressions décalées
- une séance regroupant deux brigades en lieu partagé
- une séance regroupant trois brigades **sans lieu** — terrain de sport
- une séance couvrant deux créneaux consécutifs
- une séance hors grille, un samedi
- deux grilles horaires, une seule active
- une période de calendrier visant deux sessions et une brigade
- le projet de fin d'études évalué en formatif dans une formation, en certificatif
  dans une autre
- une évaluation certificative de périmètre session, trois salles
- un surveillant extérieur au système
- une non-exécution déclarée, et une séance reportée puis tenue

**Données entièrement fictives.** Aucun nom réel, aucun matricule réel.

## Vérifier une absence

Une recherche par motif qui ne trouve rien ne prouve pas que la chose
cherchée n'existe pas — seulement que le motif n'était pas le bon (troisième
occurrence : P-26, P-32, P-36, `docs/suivi/PROBLEMES.md`). Avant de conclure
à une absence dans le dépôt, vérifier par un second angle indépendant —
comment le mécanisme serait *chargé* ou *appelé*, pas seulement comment il
serait *écrit* littéralement.

## Contrôles d'architecture

`tests/architecture/` vérifie ce que les consignes ne garantissent pas : aucune
vue n'importe un modèle directement, aucune dépendance hors de la liste validée.
Lance-les après chaque série d'éditions.
