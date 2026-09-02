# Environnement de développement local

## La base de données

PostgreSQL 16 en conteneur, décrit par `docker-compose.yml` à la racine.

```
docker compose up -d
```

**Le fichier est versionné**, donc identique pour les deux membres du binôme :
même version, même encodage, même tri. Deux installations PostgreSQL sur deux
postes Windows finissent toujours par diverger.

### Ce qu'il faut vérifier au premier lancement

**L'extension `btree_gist`.** Elle est fournie par l'image officielle mais doit
être créée dans la base — c'est la première migration du projet. La contrainte
d'exclusion sur les indisponibilités en dépend.

```sql
SELECT * FROM pg_extension WHERE extname = 'btree_gist';
```

**Le tri des noms accentués.** La configuration demande le fournisseur ICU en
locale française, pour que *Émile* se classe avec les E et non après Z. Le
classement des stagiaires en dépend.

```sql
SELECT nom FROM organisation_stagiaire ORDER BY nom;
```

Si le tri place les accents en fin de liste, l'option d'initialisation n'a pas
pris. Recréez la base — `docker compose down -v` puis `up -d` — ou appliquez la
collation par requête.

**Le port 5432.** S'il est déjà pris par une autre base sur votre poste,
changez-le à gauche des deux-points : `"5433:5432"`, et adaptez le réglage Django.

### Persistance et remise à zéro

Les données vivent dans un volume nommé : `docker compose down` les conserve,
`down -v` les efface. Pendant le sprint 1, où les migrations changent souvent,
repartir de zéro est parfois plus rapide que de démêler un historique.

### Le mot de passe

`developpement_local`, en clair et volontairement : c'est une base de
développement contenant des données fictives, jamais exposée. **Le poste du CIT
aura un mot de passe distinct**, hors du dépôt.

## Ce que Docker ne préjuge pas

Le poste de déploiement du CIT reste sur une **installation classique**. Trois
inconnues interdisent d'y transposer ce choix : le système d'exploitation du
poste est inconnu, la présence de Docker aussi, et l'autorisation de l'installer
sur un réseau militaire reste à obtenir.

Le motif décisif est ailleurs : après la soutenance, le système sera maintenu par
le CIT. Une installation classique se dépanne avec les compétences d'un
administrateur ordinaire. La décision est reportée au **jalon C1**, selon le
résultat du test d'installation hors ligne.

## Le reste de l'environnement

| Élément | Où |
|---|---|
| Environnement virtuel Python | `.venv` à la racine, hors dépôt |
| Projet Django | `app/` |
| Tests d'architecture | `tests/architecture/`, hors de `app/` |
| Dépendances | `requirements.txt`, contrôlé par un test |
| Tailwind | précompilé sur ce poste, CSS versionné |
| PlantUML | `C:\outils\plantuml\plantuml.jar`, avec Java et Graphviz |
