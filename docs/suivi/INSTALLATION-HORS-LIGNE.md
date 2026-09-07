# Installation hors ligne — préparation du test du 12 septembre

**Cible révisée par le Prompt 18 v4 : conteneurs, orchestrés par `docker
compose`, images construites avec réseau puis exportées/rechargées sans
réseau.** Les sections « Dépendances Python » et « Outillage Tailwind »
ci-dessous documentaient le plan précédent (vendoring direct sur un poste
isolé) — dépassé par cette cible, conservé pour mémoire. Dans la pile en
conteneurs, `pip install` s'exécute **à la construction de l'image**, sur le
poste de développement (réseau disponible) ; seule l'image déjà construite
voyage vers la machine isolée. Voir `docker-compose.production.yml` et
`Dockerfile`, racine du dépôt.

## Dépendances Python de la pile de production (Prompt 18 v4, § 4.2 et § 5)

**Vérifié avant construction**, comme demandé : Python 3.14.4 est très récent
(sorti après la plupart des cycles de publication de roues précompilées), le
risque étant qu'une dépendance de `gunicorn`, `whitenoise` ou `weasyprint
exige une compilation locale — un jeu d'outils de développement à embarquer
dans l'image, contraire à la sobriété du § 4.2.

Test réel : `pip install --no-cache-dir gunicorn==26.2.0 whitenoise==6.12.0
weasyprint==69.0` dans un conteneur `python:3.14.4-slim-bookworm` **sans
compilateur installé**. Les quinze paquets (les trois demandés, plus leurs
dépendances transitives — `cffi`, `Pillow`, `fonttools`, `brotli`, `zopfli`,
`pydyf`, `tinyhtml5`, `tinycss2`, `cssselect2`, `Pyphen`, `pycparser`,
`webencodings`) s'installent tous depuis une roue précompilée
(`cp314-manylinux*` ou `py3-none-any`) — aucune compilation. **Rien à
replier : l'image de base reste Python 3.14.4-slim-bookworm.**

## Dette identifiée

**Deux scripts de rôles PostgreSQL redondants** — `infra/postgres/init/01_roles.sql`
(développement, mots de passe fixes) et `infra/postgres/init-production/01_roles.sh`
(production, mots de passe lus dans l'environnement) posent les deux mêmes
rôles (`pfe_cit_migration`, `pfe_cit_app`) par la même suite d'instructions
SQL, recopiée une seconde fois plutôt que partagée. Non corrigé maintenant —
hors périmètre du test d'installation hors ligne. **Cible à terme : un script
unique, lisant les mots de passe dans l'environnement des deux côtés** (le
développement fixerait simplement des valeurs par défaut dans son `.env`,
comme il le fait déjà pour `BASE_MOT_DE_PASSE`/`BASE_MOT_DE_PASSE_MIGRATION`).
Sans cette unification, un correctif appliqué à l'un des deux scripts (une
nouvelle table par défaut, une permission supplémentaire) sera oublié dans
l'autre — la même classe de défaut que P-32 (`docs/suivi/PROBLEMES.md`),
où un correctif de pagination n'avait touché qu'une seule des copies d'un
balisage dupliqué.

## Paquet constitué (`scripts/constituer-paquet.sh`)

Exécuté avec succès le 2026-09-07 (un incident réseau transitoire sur le
conteneur Debian jetable de l'étape 4 — panne momentanée pendant le tirage
concurrent de la lourde image PostgreSQL, sans rapport avec le script —
corrigé par une seconde exécution de cette seule étape, réseau rétabli).

| Contenu | Poids |
|---|---|
| `images/` (application + `postgres:16.15-bookworm`) | 244 Mo |
| `moteur-docker/debian-12/` (19 `.deb` — 5 paquets demandés, 14 dépendances transitives résolues par `apt`) | 87 Mo |
| `compose/` (composition, `.env.exemple`, script de rôles) | 12 Ko |
| **Total** | **330 Mo** |

## Test réel sur VM Debian 12 (`192.168.56.101`) — 2026-09-07

**Verdict : réussi.** Les quatre phases du protocole (§ 2) ont été exécutées
pour de vrai, sur une machine isolée (aucune passerelle réseau — vérifié par
`ip route` et `getent hosts` avant d'incriminer quoi que ce soit d'autre) :
installation du moteur Docker depuis les `.deb` locaux, chargement des deux
images, démarrage de la pile, migrations, tri accentué réel, rendu PDF,
création du premier compte, redémarrage complet de la machine avec retour
autonome de la pile — sans aucune commande manuelle après le redémarrage.

Trois défauts réels ont été trouvés et corrigés en cours de test — exactement
ce que ce test est censé révéler, jamais visible sur un poste encore
connecté :

1. **`installer.sh` réclamait des paquets jamais embarqués** (`git`, `pigz`,
   `liberror-perl`...) — l'installation utilisait `apt-get install ./*.deb`
   sans `--no-install-recommends`, alors que le téléchargement
   (`constituer-paquet.sh`) l'avait utilisé. Voir `docs/suivi/PROBLEMES.md`,
   P-33.
2. **`docker-compose.production.yml` ne transmettait jamais `BASE_NOM`** au
   conteneur `base` — seulement `POSTGRES_DB` (pour l'image officielle) ;
   `01_roles.sh`, qui lit `$BASE_NOM`, échouait donc systématiquement à
   créer les rôles. Corrigé par l'ajout de la variable manquante.
3. **Un `SECRET_KEY` généré contenant un `$` littéral** (charset de
   `get_random_secret_key()`) a été mal réinterprété par l'interpolation de
   variables de `docker compose` (`.env`) — `docs/exploitation/INSTALLATION.md`
   recommande désormais `secrets.token_urlsafe(50)` pour `SECRET_KEY` aussi,
   pas seulement pour les mots de passe.

Deux imprécisions de `docs/exploitation/INSTALLATION.md` ont aussi été
corrigées en cours de route : la fixture de vérification PDF a besoin d'un
dossier de sortie accessible en écriture à l'utilisateur non-root du
conteneur (`chmod 777`) ; `manage.py createsuperuser` ne convient pas au
modèle `Utilisateur` du projet (champs `profil`/`grade` obligatoires, non
connus de la commande générique) — remplacé par la création via le shell
Django, `Utilisateur.objects.create_superuser(...)`.

Un `WORKER TIMEOUT` Gunicorn observé juste après le démarrage s'est révélé
être un artefact de charge CPU transitoire de la VM de test (2 vCPU,
saturée par nos propres opérations d'installation), sans récidive une fois
la charge retombée — voir P-34, à surveiller si la machine réelle du CIT a
des ressources plus limitées.

Le paquet transféré (330 Mo, intégrité vérifiée par somme SHA-256 des deux
images entre le poste de développement et la VM) inclut désormais
`verification-pdf/`, absent de la première construction — corrigé dans
`scripts/constituer-paquet.sh` avant le transfert.

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
