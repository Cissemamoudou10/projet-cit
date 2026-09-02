# Configuration Claude Code — comment ce dépôt est organisé

## Ce qui est chargé, et quand

| Élément | Chargement | Rôle |
|---|---|---|
| `CLAUDE.md` | **Chaque session** | Commandes, cinq règles non négociables, méthode |
| `.claude/rules/*.md` | **Quand un fichier correspond** | Règles propres aux modèles, services, vues, migrations, gabarits, tests |
| `.claude/skills/*/SKILL.md` | **À la demande** | Glossaire, modèle, règles métier, workflow d'une story |
| `docs/conception/*.md` | **Sur demande explicite** | Les sept livrables complets |
| `docs/charte/` | **Quand on écrit un gabarit** | Composants, palette, règles d'interface |
| `docs/suivi/*.md` | **Quand on les met à jour** | Avancement, problèmes, décisions |

**Le principe.** La fenêtre de contexte est la ressource rare : les performances
se dégradent à mesure qu'elle se remplit. D'où cette gradation — le permanent
tient en quatre-vingts lignes, le spécialisé arrive quand il sert, le volumineux
ne vient que si on le demande.

**À ne pas faire :** importer les fichiers de suivi ou les livrables dans le
CLAUDE.md avec `@`. Les imports n'économisent pas de contexte, ils chargent au
lancement comme le reste.

## Les règles par chemin

Chaque fichier de `.claude/rules/` porte un champ `paths` : il ne se charge que
lorsque Claude travaille sur un fichier correspondant. Les règles sur les modèles
n'encombrent pas une session consacrée aux gabarits.

## Organisation du dépôt

```
developpement/
├── CLAUDE.md              instructions permanentes
├── .claude/               règles, skills, sous-agent, permissions et hooks
├── app/                   le projet Django — sept applications
├── tests/architecture/    contrôles d'architecture, hors de app/
└── docs/
    ├── conception/        les 7 livrables de la phase 4
    ├── diagrammes/        les 23 sources PlantUML
    ├── charte/            brief de design, puis composants et palette
    └── suivi/             avancement, sprints, problèmes, décisions
```

## Ce qui est déterministe

Une consigne écrite dans le CLAUDE.md est suivie la plupart du temps ; un hook
l'est toujours. Trois protections sont donc mécaniques :

- `pip install` et `npm install` sont **refusés** par les permissions
- les tests d'architecture s'exécutent **après chaque édition**
- `git status` s'affiche **à la fin de chaque tour**

**Treize tests d'architecture** couvrent ce qu'une consigne ne garantit pas.

*Architecture* : import de modèle dans une vue, objet HTTP dans un service,
attribut dérivé stocké, `FloatField` sur une note, dépendance inverse entre
applications.

*Dépendances* : paquet non validé dans `requirements.txt`, ressource distante
dans un gabarit.

*Qualité* : fichier au-delà de 400 lignes, fonction au-delà de 40, classe au-delà
de 200, plus de cinq paramètres, appel de service depuis un signal, import
générique ou `print` oublié.

Ces limites ne sont pas des recommandations : un fichier de mille lignes n'est
pas modulaire, quelle que soit l'intention de son auteur.

## Le workflow d'une story

```
/story US-REF-03
```

Huit étapes : comprendre, explorer, planifier, **attendre validation**, implanter,
vérifier, faire relire par le sous-agent, consigner, livrer.

Le sous-agent `relecteur-conception` examine le diff dans un contexte neuf : il
ne voit pas le raisonnement qui l'a produit, seulement le résultat.

## Conduite de session

`/clear` entre deux stories sans rapport. Après deux corrections infructueuses sur
le même point, `/clear` et reprendre avec un prompt plus précis : une session
propre l'emporte presque toujours sur une session encombrée d'approches ratées.

`/context` pour vérifier ce qui est chargé. `/doctor` propose des coupes dans le
CLAUDE.md quand il grossit.

## Entretien de cette configuration

Quand Claude se trompe de façon répétée sur un point, ne corrige pas seulement le
code : ajoute la correction à la règle concernée. Le fichier devient un registre
des pièges du projet.

Si une instruction est ignorée malgré tout, le fichier est probablement trop long
et la règle s'y perd. Élaguer vaut mieux qu'insister.
