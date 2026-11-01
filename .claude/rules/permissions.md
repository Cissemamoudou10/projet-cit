# Permissions de l'outil

**Jamais de modification, même temporaire, des règles de permission de
`.claude/`** (`settings.json`, `settings.local.json` — `allow`, `ask`,
`deny`) par l'agent lui-même, quelle que soit la règle visée et même avec
un accord explicite sur le fond donné en conversation. Un accord sur une
action (par exemple installer une dépendance) n'est pas un accord pour
modifier la permission qui l'encadre.

**À la place : s'arrêter et donner la commande exacte à lancer**, pour que
le chef de projet l'exécute lui-même (ou modifie la règle lui-même, puis
confirme). Reprendre seulement une fois confirmé.

**Pourquoi** — un agent qui peut lever puis reposer sa propre barrière de
permission peut tout aussi bien ne jamais la reposer, ou l'assouplir plus
largement que prévu « pendant qu'il y est ». La règle `deny` sur
`pip install` existe précisément parce que le poste cible est isolé
(BNF-06, CLAUDE.md) et qu'aucune dépendance ne doit être ajoutée sans
arbitrage — la faire respecter par l'outil, pas seulement par la
discipline de l'agent, est le but même de son existence dans `.claude/`.
Contourné une fois (prompt 54 bis, installation de `playwright`), corrigé
sur instruction du chef de projet.
