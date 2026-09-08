# Sprint 1 — 31 août – 12 septembre 2026

**Objectif.** Socle technique, authentification et habilitations, référentiel de formation complet, instructeurs et qualifications, lieux.

**Périmètre.** 15 stories, 58 points.

**Jalon de sortie.** **C1 le 12 septembre** — premier point de vérité : heures réelles, vélocité, **test d'installation hors ligne**.

## Stories

Coche à la livraison : implantée, testée, relue par le sous-agent, commitée.

- [x] **US-ADM-01** — S'authentifier au système · 3 pts · Must
- [x] **US-ADM-02** — Gérer les comptes utilisateurs · 5 pts · Must
- [x] **US-ADM-03** — Restreindre l'accès selon le profil · 5 pts · Must
- [x] **US-ADM-04** — Journaliser les actions sensibles · 3 pts · Must
- [x] **US-REF-00** — Gérer les types de formation · 2 pts · Must
- [x] **US-REF-01** — Gérer les formations · 3 pts · Must
- [x] **US-REF-02** — Gérer le catalogue des matières · 3 pts · Must
- [x] **US-REF-03** — Composer le référentiel d'une formation · 8 pts · Must
- [x] **US-REF-04** — Déclarer la catégorie de lieu requise par matière · 3 pts · Must
- [x] **US-REF-05** — Associer des objectifs pédagogiques aux matières · 3 pts · Must
- [x] **US-REF-06** — Déclarer les prérequis d'un référentiel · 5 pts · Must
- [x] **US-REF-07** — Consulter le référentiel depuis les autres cellules · 2 pts · Must
- [x] **US-INS-01** — Gérer les instructeurs · 5 pts · Must
- [x] **US-INS-02** — Établir la matrice de qualification · 5 pts · Must
- [x] **US-PLAN-02** — Gérer les lieux d'enseignement · 3 pts · Must

## Tâches transverses

- [x] Squelette Django : sept applications, réglages, base PostgreSQL
- [x] Extension `btree_gist` installée et migration initiale
- [x] Tailwind précompilé, CSS versionné (`app/noyau/static/css/application.css`, 18 494 octets après US-INS-02)
- [x] Tests d'architecture en place et passants (confirmé par un vrai `pytest`, 17/17 après US-INS-02 — voir docs/suivi/PROBLEMES.md)
- [x] **Test d'installation hors ligne** — réussi le 2026-09-07 sur VM Debian 12 isolée (Prompt 18 v4) : pile conteneurisée (Docker Engine, images, moteur), migrations, tri accentué réel, rendu PDF, redémarrage résilient — voir `docs/suivi/INSTALLATION-HORS-LIGNE.md`
- [x] Jeu de données de démonstration du sprint 1 (Prompt 15, WBS 5.1.17) — `charger_jeu_demonstration`, voir `docs/suivi/JEU-DEMONSTRATION.md`
- [ ] Jeu de données d'essai fictif, couvrant les douze situations de la règle `tests.md` (sessions, brigades, séances — paquetage P3, sprints 2-3)
- [x] Corrections des écarts de recette du 4 septembre (Prompt 16) — verrouillage et modification concurrente classés absence de défaut (P-31), suppression manquante pour cinq entités (P-30), journalisation des suppressions (patron `ServiceGestion`) — voir `docs/suivi/PROBLEMES.md`
- [x] Pagination et enrichissement des listes (Prompt 17, WBS 5.1.20) — fenêtre de pagination partagée (P-32), cinq compteurs agrégés, filtre objet du journal, modification d'une indisponibilité de lieu — voir `docs/suivi/PROMPT-17-tracabilite.md`
- [x] Clôture du sprint 1 (Prompt 19) — trois corrections documentaires (bloc A), analyse chiffrée du débordement à l'impression sans implantation (bloc B), règle de couverture HTTP inscrite en définition de fini (bloc C), inventaire puis comblement complet des 24 chemins nominaux et 36 refus d'habilitation manquants, avec test de garde mécanique (bloc D), unification des scripts de rôles PostgreSQL (bloc E), P-25 revérifié et état des reports de critères consolidé (bloc F) — voir `docs/suivi/COUVERTURE-HTTP.md`, `docs/suivi/IMPRESSION-ANALYSE.md`, `docs/suivi/DECISIONS.md` (D-62)

## Revue et rétrospective

- [ ] Heures réelles saisies dans le classeur de pilotage
- [ ] Vélocité mesurée, clé de conversion révisée
- [ ] Registre des risques mis à jour
- [ ] `AVANCEMENT.md` mis à jour
