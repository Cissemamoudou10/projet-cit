# Réinstallation à la lettre et test de sauvegarde/restauration — procédure et relevé

**Objet.** Prouver que la procédure écrite suffit (leçon L7 : une procédure
n'est prouvée qu'une fois rejouée à la lettre) et que la sauvegarde restaure
réellement les données (risques R9 et R20). Le résultat alimente le
mémoire, chapitre 5, § 5.7.

**Règles.**
- Suivre `docs/exploitation/INSTALLATION.md` puis `EXPLOITATION.md` **à la
  lettre**. Toute commande à corriger, ajouter ou deviner est un **écart** :
  on le note dans le relevé (§ 4), on ne le corrige pas en silence.
- VM Debian 12 **neuve** (netinst, sans Docker), **carte réseau déconnectée**
  après le transfert du paquet.
- Données **fictives** uniquement (jeu de démonstration).
- Chronométrer chaque étape (heure de début et de fin).

Durée prévue : 3 h à 4 h.

## 1. Avant de commencer (poste de développement)

Fait par Claude Code (prompt 66) :
- [ ] `INSTALLATION.md` complété (étape des gabarits de documents, voir P-85).
- [ ] Paquet reconstruit depuis le code gelé, avec `MANIFESTE.txt` (empreintes).
- [ ] Script `verification-restauration/releve.sql` présent dans le paquet.

Fait par toi :
- [ ] Copier `paquet-deploiement/` sur le support de transfert (dossier
      partagé de la VM ou clé USB virtuelle).

## 2. Installation (VM)

**Note sur le chronométrage** : le poste de développement (pas la VM) s'est mis
en veille pendant l'exécution des § 2.1 à 2.4, entre deux commandes SSH — sans
rapport avec la VM elle-même, qui n'a jamais perdu son état. Les heures de
début/fin de ces quatre étapes ne sont donc pas fiables et ne sont pas
reportées ; la connexion SSH a aussi montré une instabilité intermittente
(coupures ponctuelles, toujours sans perte de travail déjà effectué — vérifié
chaque fois avant de rejouer une commande). Les étapes 2.5 à 2.11, après la
reprise, sont chronométrées normalement.

| # | Étape (`INSTALLATION.md`) | Début | Fin | Résultat (OK / écart n°) |
|---|---|---|---|---|
| 2.1 | § 2 Transfert, puis **déconnecter le réseau** | — | — | OK (SHA-256 des deux images vérifiées identiques au `MANIFESTE.txt`) |
| 2.2 | § 3 Premier passage de `installer.sh` | — | — | OK — arrêt volontaire attendu (`.env` absent) |
| 2.3 | § 4 Préparer `compose/.env` | — | — | OK, puis **P-86** (CRLF, voir § 4) |
| 2.4 | § 5 Second passage | — | — | OK — pile démarrée |
| 2.5 | § 6 Pile démarrée | 10:12:30 | 10:12:35 | OK (`base` healthy, `application` Up) |
| 2.6 | § 7 Migrations | 10:12:40 | 10:13:00 | **P-86** à la première tentative (authentification refusée via `.env` CRLF) ; OK après correction, rejoué avec succès |
| 2.7 | § 8 et 8 bis Habilitations, natures | 10:12:43 | 10:12:56 | OK (13 s) |
| 2.8 | § 8 ter Gabarits de documents | 10:12:56 | 10:12:56 | OK (inclus dans la même passe) |
| 2.9 | § 9 Compte administrateur | 10:13:04 | 10:13:08 | OK (4 s) |
| 2.10 | § 9 bis Grilles horaires | 10:13:13 | 10:13:17 | OK (4 s) |
| 2.11 | § 10 Tri accentué, rendu PDF, redémarrage | 10:13:20 | 10:20:53 | OK — tri conforme, PDF 9 polices `emb yes` + 1 police de repli, texte accentué net (`pdffonts`/`pdftotext`, `curl` absent de la VM — écart mineur, non bloquant), redémarrage 10:20:07→10:20:53 (46 s), pile repartie seule |

**Contrôle fonctionnel minimal** : connexion du compte administrateur réalisée
par requête HTTP directe (script Python, `curl` absent de la VM nue) —
changement de mot de passe forcé au premier login franchi, tableau de bord
atteint (`GET /accueil/` → 200, en-tête et menu de navigation présents), PDF
produit par l'application. Résultat : **OK**.

## 3. Sauvegarde et restauration (VM)

### 3.1 Charger des données fictives

```
docker compose -f compose/docker-compose.production.yml exec application \
    python manage.py charger_jeu_demonstration
```

Puis, depuis l'écran : créer **un élément témoin** facile à retrouver (par
exemple un lieu nommé `TEMOIN-SAUVEGARDE`). Le noter : lieu « TEMOIN-SAUVEGARDE »
(catégorie salle attitrable, capacité 30), créé par `ServiceLieu.creer`, pk 12.

### 3.2 Relevé de référence

```
set -a; . compose/.env; set +a
docker compose -f compose/docker-compose.production.yml exec -T base \
    psql -U "$BASE_UTILISATEUR_MIGRATION" -d "$BASE_NOM" -At \
    -v app_role="$BASE_UTILISATEUR" \
    < verification-restauration/releve.sql > releve_avant.txt
```

### 3.3 Sauvegarde

Commande de `EXPLOITATION.md` § « Sauvegarde ». Copier le `.dump` **hors de
la VM** (dossier partagé). Taille du fichier : **299 178 octets**
(`sauvegarde_2026-11-21_0525.dump`, rapatrié sur le poste de développement,
non versionné).

### 3.4 Scénario A — erreur de manipulation

1. Depuis l'écran, **supprimer ou modifier** l'élément témoin. **Fait** —
   supprimé par `ServiceLieu.supprimer`, comme l'écran.
2. Restaurer (`EXPLOITATION.md` § « Restauration »). **Noter le code de sortie
   de `pg_restore` (`echo $?`) et toute ligne « errors ignored on restore ».**
   Une erreur n'est jamais ignorée : c'est un écart. — **Code de sortie : 0**,
   aucune ligne « errors ignored ».
3. Refaire le relevé dans `releve_apres_A.txt`, puis :
   `diff releve_avant.txt releve_apres_A.txt` → **aucune différence attendue**.
   — **Première exécution : différence sur deux lignes** (droits UPDATE/DELETE
   du rôle applicatif sur `administration_entree_journal`, passés à `true` —
   voir **P-87**, § 4). Après correction (révocation rejouée), `diff` vide.
4. Vérifier à l'écran que l'élément témoin est revenu. — **OK**, confirmé par
   requête à l'application (`Lieu.objects.filter(intitule="TEMOIN-SAUVEGARDE").exists()` → `True`).

### 3.5 Scénario B — perte totale du volume (sinistre)

**Uniquement sur cette VM de test.** `EXPLOITATION.md` interdit `down -v` en
exploitation : ici, on simule justement la perte du disque.

1. `docker compose -f compose/docker-compose.production.yml down -v` — **Fait**.
2. `docker compose -f compose/docker-compose.production.yml up -d` puis
   attendre `base` « healthy ». — **OK**.
3. Restaurer le même `.dump` (même commande). Noter le code de sortie et les
   erreurs. — **Code de sortie : 0**, aucune erreur.
4. Relevé `releve_apres_B.txt`, `diff` avec `releve_avant.txt` → aucune
   différence attendue (y compris la ligne des droits du journal). —
   **Vide**, en suivant la procédure déjà corrigée (révocation RG-27 rejouée
   après restauration, voir P-87).
5. Se connecter avec le compte administrateur, retrouver l'élément témoin,
   produire un PDF. — **OK** (connexion 200 directe sur `/accueil/`, témoin
   retrouvé, PDF produit avec succès).
6. Redémarrer la VM ; vérifier que la pile repart seule. — **OK** (arrêt et
   reprise de la pile confirmés par `docker compose ps` après reboot).

## 4. Relevé des écarts

| N° | Étape | Constat | Contournement appliqué | Correction à faire dans la doc |
|---|---|---|---|---|
| E-00 | § 0 bis (avant transfert) | VM non nue (installation du 7 septembre encore présente) | Nettoyage choisi par l'étudiant plutôt qu'une réinstallation Debian complète (purge Docker/containerd, suppression des dossiers restants) | Aucune — assumé, voir § 0 bis |
| E-0 | § 1 Transfert | Transfert par réseau host-only (192.168.56.x) plutôt que par support physique | Assumé — réseau isolé du reste, sans Internet (vérifié § 0.3) | Aucune — assumé |
| P-86 | § 2.3/2.6 `compose/.env` | `set -a; . compose/.env; set +a` puis `migrate` échoue (`password authentication failed`) alors que les mêmes identifiants en dur réussissent | Valeurs passées en dur pour débloquer, puis `.env`/`.env.exemple` corrigés (CRLF → LF) et procédure rejouée avec succès | `.gitattributes` ajouté (`eol=lf`) — fait, voir `docs/suivi/PROBLEMES.md` P-86 |
| P-87 | § 3.4 Scénario A, restauration | Après `pg_restore --clean --if-exists` (code 0, sans erreur), le rôle applicatif retrouve UPDATE/DELETE sur `administration_entree_journal` — RG-27 violée | `REVOKE UPDATE, DELETE ...` rejoué manuellement, puis ajouté à la procédure documentée et rejoué sans écart au scénario B | `EXPLOITATION.md` § « Restauration » complété (étape de révocation systématique) — fait, voir `docs/suivi/PROBLEMES.md` P-87 |

## 5. Verdict

- Installation à la lettre : **réussie avec écarts** (P-86, bloquant à la
  première tentative, corrigé et rejoué avec succès ; E-00 et E-0 assumés,
  sans impact sur le résultat)
- Durée totale d'installation : **non mesurable de façon fiable** — le poste
  de développement s'est mis en veille pendant les § 2.1 à 2.4 (voir note du
  § 2) ; les étapes mesurées après reprise (§ 2.5 à 2.11) ont pris environ
  8 minutes au total, redémarrage inclus (46 s de coupure)
- Scénario A : **réussi** (après correction de P-87 pendant le rejeu — la
  première tentative avait révélé l'écart). Scénario B : **réussi**, dès le
  premier passage, avec la procédure déjà corrigée.
- Date, opérateur : 2026-11-21, Claude Code (prompt 67, par SSH `vm-cit`/`vm-cit-root`)

Rapporté : ce relevé complété, les trois fichiers `releve_*.txt`, les deux
`diff` (vides après correction), le PDF et la sortie de `pdffonts`, dans
`docs/recette/reinstallation-vm/`. P-86 et P-87 consignés dans
`docs/suivi/PROBLEMES.md`.
