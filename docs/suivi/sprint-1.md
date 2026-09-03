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
- [ ] **US-REF-02** — Gérer le catalogue des matières · 3 pts · Must
- [ ] **US-REF-03** — Composer le référentiel d'une formation · 8 pts · Must
- [ ] **US-REF-04** — Déclarer la catégorie de lieu requise par matière · 3 pts · Must
- [ ] **US-REF-05** — Associer des objectifs pédagogiques aux matières · 3 pts · Must
- [ ] **US-REF-06** — Déclarer les prérequis d'un référentiel · 5 pts · Must
- [ ] **US-REF-07** — Consulter le référentiel depuis les autres cellules · 2 pts · Must
- [ ] **US-INS-01** — Gérer les instructeurs · 5 pts · Must
- [ ] **US-INS-02** — Établir la matrice de qualification · 5 pts · Must
- [ ] **US-PLAN-02** — Gérer les lieux d'enseignement · 3 pts · Must

## Tâches transverses

- [x] Squelette Django : sept applications, réglages, base PostgreSQL
- [x] Extension `btree_gist` installée et migration initiale
- [x] Tailwind précompilé, CSS versionné (`app/noyau/static/css/application.css`, 17 257 octets après US-REF-01)
- [x] Tests d'architecture en place et passants (confirmé par un vrai `pytest`, 28/28 — voir docs/suivi/PROBLEMES.md)
- [ ] **Test d'installation hors ligne** — dépendances natives de WeasyPrint
- [ ] Jeu de données d'essai fictif, couvrant les douze situations de la règle `tests.md`

## Revue et rétrospective

- [ ] Heures réelles saisies dans le classeur de pilotage
- [ ] Vélocité mesurée, clé de conversion révisée
- [ ] Registre des risques mis à jour
- [ ] `AVANCEMENT.md` mis à jour
