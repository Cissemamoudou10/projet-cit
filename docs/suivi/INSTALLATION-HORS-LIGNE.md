# Installation hors ligne — préparation du test du 12 septembre

Non exécuté. Le socle produit les fichiers de dépendances ; la constitution du
cache et l'installation elle-même restent à faire au moment du test, sur un
poste représentatif du réseau isolé (BNF-06).

## Dépendances Python

```
pip download -d vendor/wheels -r requirements-dev.txt
```

`requirements-dev.txt` inclut `requirements.txt` (`-r requirements.txt`), donc
cette seule commande couvre aussi bien le runtime (Django, psycopg) que
l'outillage de développement (pytest, pytest-django, pytest-cov, ruff).

**Les versions figées ont été installées pour de vrai** (`pip install -r
requirements-dev.txt` dans un `.venv` local, Python 3.14.4 Windows) : Django,
psycopg, pytest, pytest-django, pytest-cov, ruff s'installent tous sans
erreur. Une correction a été nécessaire : `psycopg[binary]==3.2.3` n'existe
pas pour cette plateforme (aucune roue disponible) — corrigé en `3.2.10`,
version disponible la plus proche de la même série 3.2.x. Les autres pins
étaient corrects du premier coup. Nuance : l'installation a eu lieu sur ce
poste de développement (accès réseau disponible), pas sur un poste réellement
isolé — le test du 12 septembre reste la vérification qui compte pour BNF-06.

## Outillage Tailwind (npm)

**Hors périmètre de ce test.** `package.json` / `node_modules` ne servent qu'à
compiler `app/noyau/static/css/application.css` sur le poste de développement
— ce fichier compilé est ensuite versionné et déployé comme n'importe quel
fichier statique. Node n'est jamais installé ni exécuté sur le poste cible
(`.claude/rules/gabarits.md`), donc aucun cache npm n'est nécessaire pour le
test du 12 septembre.
