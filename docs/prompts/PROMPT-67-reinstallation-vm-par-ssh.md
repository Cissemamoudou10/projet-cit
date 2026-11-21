# Prompt 67 — Réinstallation à la lettre sur la VM et test de sauvegarde/restauration, par SSH

Contexte : phase 7. Tu exécutes toi-même `docs/recette/REINSTALLATION-VM.md`
(lis-la en premier, puis `docs/exploitation/INSTALLATION.md` et
`EXPLOITATION.md`) sur la VM Debian 12, par SSH, **uniquement via les alias `vm-cit` (utilisateur cisse) et `vm-cit-root`
(root)**, qui utilisent une clé dédiée. `sudo` n'est pas installé sur la VM :
les commandes d'administration (dont `installer.sh`) passent par
`ssh vm-cit-root`, sans le préfixe `sudo` que cite la doc — ce n'est pas un
écart, `INSTALLATION.md` § 1 prévoit « accès root (ou sudo) ». **Ne lis, ne crée, ne modifie
aucune autre clé ni aucune autre entrée de `~/.ssh`** : l'étudiant y garde des
clés d'accès à d'autres serveurs. N'écris aucun mot de passe dans le dépôt.
Données fictives uniquement.

## 0. Avant de toucher à la VM — arrête-toi et rends compte si un point échoue

1. `ssh vm-cit` et `ssh vm-cit-root` sans aucune question (`whoami` = root).
2. **VM nue** : ni `docker`, ni paquet `docker-ce`, ni dossier
   `paquet-deploiement`. Si Docker est déjà là, ce n'est pas une VM neuve :
   arrête-toi, l'étudiant restaurera un instantané.
3. **Pas d'Internet sur la VM** : `timeout 5 bash -c '</dev/tcp/deb.debian.org/443'`
   et `timeout 5 bash -c '</dev/tcp/1.1.1.1/443'` doivent échouer tous les deux
   (`curl` n'est pas installé sur la VM). Le réseau host-only 192.168.56.x sert seulement au transfert.
   Si Internet répond, arrête-toi : l'étudiant désactivera la carte NAT.

## 0 bis. Si l'étudiant a choisi le nettoyage (la VM n'est pas nue)

La VM porte l'installation du 7 septembre. Sur décision de l'étudiant, tu la
ramènes à l'état « serveur nu » au lieu d'une réinstallation de Debian :

1. Relevé de l'existant **avant** nettoyage (versions Docker, `docker ps -a`,
   `docker volume ls`, `docker images`), consigné dans le relevé.
2. `docker compose down -v` de l'ancienne pile si elle existe, arrêt de
   `docker` et `containerd`.
3. `apt-get purge -y docker-ce docker-ce-cli containerd.io
   docker-buildx-plugin docker-compose-plugin` puis
   `apt-get autoremove --purge -y` (sans réseau : aucune installation).
4. Suppression de `/var/lib/docker`, `/var/lib/containerd`, `/etc/docker`,
   `~/paquet-deploiement` et `~/verification-sortie` de cisse.
5. Vérification : `dpkg -l | grep -Ei 'docker|containerd'` vide,
   `command -v docker` vide. Les paquets retirés par `autoremove` sont
   listés dans le relevé.

Note-le comme **écart E-00, assumé** : « VM nettoyée, non réinstallée depuis
l'image Debian ». Puis reprends au § 0, point 3 (Internet), et continue.

## 1. Transfert (§ 2.1 du relevé)

`scp -r paquet-deploiement` vers `~/` de la VM. Le transfert passe par le
réseau host-only (sans Internet) au lieu d'un support physique : note-le
comme **écart E-0, assumé**. Puis `sha256sum images/*.tar` sur la VM, à
comparer avec `MANIFESTE.txt`.

## 2. Installation (§ 2.2 à 2.11)

Rejoue `INSTALLATION.md` **à la lettre**, dans l'ordre, en chronométrant
chaque étape (heure de début et de fin). Toute commande que tu dois
corriger, ajouter ou deviner est un **écart** : note-le dans le relevé
(constat, contournement, correction à faire), ne le corrige pas en silence.
- Mots de passe et `SECRET_KEY` générés sur la VM comme le dit le § 4,
  jamais réutilisés depuis le poste de développement.
- § 10, rendu PDF : au lieu de l'œil, `pdffonts` sur le PDF produit (toutes
  les polices `emb yes`) et `pdftotext` (accents corrects) ; rapatrie le PDF
  dans `docs/recette/reinstallation-vm/`.
- § 10, redémarrage : `reboot` (en root), attends, reconnecte-toi, vérifie que la
  pile est repartie seule.
- Contrôle fonctionnel : `curl` de la page de connexion (HTTP 200), puis
  connexion du compte administrateur (session et jeton CSRF) et accès au
  tableau de bord.

## 3. Sauvegarde et restauration (§ 3)

- § 3.1 : `charger_jeu_demonstration`, puis crée l'élément témoin
  (un lieu `TEMOIN-SAUVEGARDE`) par `manage.py shell`, en passant par le
  service comme le ferait l'écran.
- § 3.2 à 3.4 (scénario A) : relevé, sauvegarde, suppression du témoin par
  le service, restauration, relevé, `diff`. Code de sortie de `pg_restore`
  et lignes « errors ignored » relevés tels quels.
- § 3.5 (scénario B) : **autorisation exceptionnelle de `down -v`, sur cette
  VM uniquement** ; puis restauration du même `.dump`, relevé, `diff`,
  connexion administrateur, témoin retrouvé, PDF produit, redémarrage.

## 4. Relevé

Remplis `docs/recette/REINSTALLATION-VM.md` (tableaux des § 2, 4 et 5) et
range dans `docs/recette/reinstallation-vm/` : les trois `releve_*.txt`, les
deux `diff`, le PDF, la sortie de `pdffonts`, la taille du `.dump` (pas le
`.dump` lui-même). Verdict honnête : « réussie avec écarts » si la doc a dû
être complétée.

## 5. Clôture

- Retire la clé `vm-cit` de `/root/.ssh/authorized_keys` sur la VM (en
  dernier, par `ssh vm-cit-root`), puis vérifie que `ssh vm-cit-root` est refusé.
- Pour chaque écart réel : entrée `PROBLEMES.md` (numéro suivant P-85),
  correction de `INSTALLATION.md` ou `EXPLOITATION.md`, puis **rejoue
  l'étape corrigée** pour prouver la correction.
- Un commit « Phase 7 : réinstallation à la lettre sur VM et test de
  sauvegarde/restauration (prompt 67) ».

Règles permanentes : sur le poste de développement, ne tue aucun processus,
ne réinitialise ni ne supprime aucune base, un seul processus
pytest/PostgreSQL à la fois, ne modifie pas tes propres permissions. Sur la
VM, tout est permis dans le cadre de ce prompt, rien au-delà.

Compte rendu attendu : verdict, durée totale d'installation, écarts (numéro
P, correction, rejeu), résultat des scénarios A et B (code de sortie, diff),
polices du PDF, redémarrage.
