# Livrables de conception — phase 4

Les sept livrables arrêtés au 30 août 2026, à la revue de conception.

**Ne les lis pas systématiquement.** Le livrable des cas d'utilisation dépasse à
lui seul quatre-vingts pages : le charger sans nécessité sature le contexte et
dégrade les réponses. Les skills `glossaire-cit`, `modele-domaine` et
`regles-metier` portent l'essentiel distillé. Ces fichiers servent à vérifier un
point précis, par recherche ciblée.

| Fichier | Contenu | Quand le consulter |
|---|---|---|
| `11-cas-utilisation.md` | 57 cas d'utilisation, 65 règles métier, 6 diagrammes | Une fiche précise, un enchaînement d'exception |
| `12-diagrammes-sequence.md` | Génération, validation, examen, indisponibilité | Un ordre d'appels entre services |
| `13-diagramme-classes.md` | **Fait foi.** 30 classes, 12 énumérations | Une cardinalité, un attribut, une association |
| `14-note-implementation.md` | Schéma PostgreSQL, contraintes, index | Écrire une migration |
| `15-dossier-architecture.md` | Couches, déploiement, choix documentaire | Placer un composant |
| `16-maquettes.md` | 5 wireframes des écrans structurants | Construire un écran |
| `17-dossier-consolide.md` | Synthèse de la phase | Retrouver une décision et son origine |

Les figures sont dans `docs/diagrammes/`, en sources PlantUML versionnables.

```
cd docs/diagrammes
rendre.bat C:\outils\plantuml\plantuml.jar
```
