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
- [ ] `INSTALLATION.md` complété (étape des gabarits de documents, voir P-xx).
- [ ] Paquet reconstruit depuis le code gelé, avec `MANIFESTE.txt` (empreintes).
- [ ] Script `verification-restauration/releve.sql` présent dans le paquet.

Fait par toi :
- [ ] Copier `paquet-deploiement/` sur le support de transfert (dossier
      partagé de la VM ou clé USB virtuelle).

## 2. Installation (VM)

| # | Étape (`INSTALLATION.md`) | Début | Fin | Résultat (OK / écart n°) |
|---|---|---|---|---|
| 2.1 | § 2 Transfert, puis **déconnecter le réseau** | | | |
| 2.2 | § 3 Premier passage de `installer.sh` | | | |
| 2.3 | § 4 Préparer `compose/.env` | | | |
| 2.4 | § 5 Second passage | | | |
| 2.5 | § 6 Pile démarrée | | | |
| 2.6 | § 7 Migrations | | | |
| 2.7 | § 8 et 8 bis Habilitations, natures | | | |
| 2.8 | § 8 ter Gabarits de documents | | | |
| 2.9 | § 9 Compte administrateur | | | |
| 2.10 | § 9 bis Grilles horaires | | | |
| 2.11 | § 10 Tri accentué, rendu PDF, redémarrage | | | |

**Contrôle fonctionnel minimal** : se connecter avec le compte administrateur
depuis le navigateur de la VM, ouvrir le tableau de bord, produire un PDF
depuis l'application.

## 3. Sauvegarde et restauration (VM)

### 3.1 Charger des données fictives

```
docker compose -f compose/docker-compose.production.yml exec application \
    python manage.py charger_jeu_demonstration
```

Puis, depuis l'écran : créer **un élément témoin** facile à retrouver (par
exemple un lieu nommé `TEMOIN-SAUVEGARDE`). Le noter : ________________

### 3.2 Relevé de référence

```
set -a; . compose/.env; set +a
docker compose -f compose/docker-compose.production.yml exec -T base \
    psql -U "$BASE_UTILISATEUR_MIGRATION" -d "$BASE_NOM" -At \
    < verification-restauration/releve.sql > releve_avant.txt
```

### 3.3 Sauvegarde

Commande de `EXPLOITATION.md` § « Sauvegarde ». Copier le `.dump` **hors de
la VM** (dossier partagé). Taille du fichier : ________

### 3.4 Scénario A — erreur de manipulation

1. Depuis l'écran, **supprimer ou modifier** l'élément témoin.
2. Restaurer (`EXPLOITATION.md` § « Restauration »). **Noter le code de sortie
   de `pg_restore` (`echo $?`) et toute ligne « errors ignored on restore ».**
   Une erreur n'est jamais ignorée : c'est un écart.
3. Refaire le relevé dans `releve_apres_A.txt`, puis :
   `diff releve_avant.txt releve_apres_A.txt` → **aucune différence attendue**.
4. Vérifier à l'écran que l'élément témoin est revenu.

### 3.5 Scénario B — perte totale du volume (sinistre)

**Uniquement sur cette VM de test.** `EXPLOITATION.md` interdit `down -v` en
exploitation : ici, on simule justement la perte du disque.

1. `docker compose -f compose/docker-compose.production.yml down -v`
2. `docker compose -f compose/docker-compose.production.yml up -d` puis
   attendre `base` « healthy ».
3. Restaurer le même `.dump` (même commande). Noter le code de sortie et les
   erreurs.
4. Relevé `releve_apres_B.txt`, `diff` avec `releve_avant.txt` → aucune
   différence attendue (y compris la ligne des droits du journal).
5. Se connecter avec le compte administrateur, retrouver l'élément témoin,
   produire un PDF.
6. Redémarrer la VM ; vérifier que la pile repart seule.

## 4. Relevé des écarts

| N° | Étape | Constat | Contournement appliqué | Correction à faire dans la doc |
|---|---|---|---|---|
| | | | | |

## 5. Verdict

- Installation à la lettre : réussie / réussie avec écarts / échec
- Durée totale d'installation : ________
- Scénario A : réussi / échec. Scénario B : réussi / échec.
- Date, opérateur : ________

Rapporter ce relevé complété (et les trois fichiers `releve_*.txt`) au chef
de projet et à Claude Code (prompt 67 : corrections de la documentation,
P-xx, registre des risques).
