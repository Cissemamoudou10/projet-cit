---
name: story
description: Dérouler une user story de bout en bout, de l'exploration à la relecture. À invoquer au début de chaque story du backlog.
disable-model-invocation: true
---

Implante la user story : $ARGUMENTS

Déroule ces étapes dans l'ordre et ne passe à la suivante qu'une fois la
précédente achevée.

**1. Comprendre.** Relis le besoin et les critères d'acceptation que je t'ai
donnés. Consulte les skills `glossaire-cit` et `regles-metier` si un terme ou une
contrainte t'échappe. Si une information manque, **demande-la** plutôt que de
supposer : neuf points du modèle ont été corrigés par le terrain, l'invention est
coûteuse ici.

**2. Explorer.** Regarde comment les stories déjà livrées traitent des cas
voisins. Suis les motifs existants plutôt que d'en introduire un nouveau.

**3. Planifier.** Propose un plan : fichiers à créer ou modifier, services
appelés, contraintes portées en base, tests prévus. **Attends ma validation.**

**4. Implanter.** Modèles, migration, service, vue, gabarit, tests — dans cet
ordre. Un test au moins par critère d'acceptation.

**5. Vérifier.** Lance `pytest` puis `pytest tests/architecture -q`. Montre la
sortie. Si un test échoue, corrige la cause, ne le contourne pas.

**6. Relire.** Fais examiner le diff par le sous-agent `relecteur-conception`.
Corrige les écarts de conformité ; ignore les préférences de style.

**7. Consigner.** Coche la story dans `docs/suivi/sprint-N.md`. Si tu as rencontré
un blocage, note-le dans `PROBLEMES.md`. Si une décision s'écarte de la
conception, inscris-la dans `DECISIONS.md` avec son impact sur les livrables.

**8. Livrer.** Commit en français, à l'impératif, mentionnant le code de la
story. Définition de fini : implantée, testée, relue par le sous-agent,
**commitée**, **ligne ajoutée au tableau Sprints d'`AVANCEMENT.md`**,
**ligne ajoutée à `heures-sprint-N.md`, datée du jour** — les deux derniers
points sont mécaniques, jamais reconstitués après coup (mesure corrective
de R23, prompt 34, suite à deux reports oubliés du tableau de suivi
pendant tout le sprint 2, D-91 et D-83).
