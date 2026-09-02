# Décisions de développement

Toute décision qui **s'écarte de la conception arrêtée en phase 4**, ou qui la
complète sur un point qu'elle ne traitait pas.

**Pourquoi ce fichier existe.** Le mémoire décrit la conception ; le code décrira
la réalité. Sans trace des écarts, les deux divergent et la traçabilité —
`OSn → BF → US → CU → RG → SEQ → CLS` — se rompt. Un jury vérifie cette chaîne.

**Ce qui n'entre pas ici** : les choix d'implantation sans effet sur le modèle ni
sur une règle métier. Le nom d'une variable n'est pas une décision.

**Ce qui entre ici** : toute modification d'une règle métier, d'une cardinalité,
d'un attribut, d'un état, d'une responsabilité de service. Et toute règle
nouvelle découverte en développant.

## Format

Une entrée par décision, la plus récente en tête.

```
## D-nn — Titre court
**Date** · **Story** · **Auteur**
**Contexte** — la situation qui a imposé de trancher.
**Décision** — ce qui a été retenu, sans ambiguïté.
**Alternative écartée** — et pourquoi.
**Impact sur les livrables** — quelle règle, quelle classe, quel diagramme est à
reprendre. **Cette ligne n'est jamais vide.**
**Reporté au livrable** — oui / non, avec la date.
```

---

## D-08 — L'intergiciel de changement de mot de passe vit dans `administration`, pas `noyau`
**Date** 2026-09-02 · **Story** US-ADM-02 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — Le prompt place l'intergiciel dans `app/noyau/middleware.py` et veut qu'il consulte « une méthode du service » (§ 2.2 : « il redirige, il ne décide pas »). Mais la règle (`ServiceCompte.doit_changer_mot_de_passe`) vit dans `administration`, et `noyau` ne doit dépendre d'aucune application — invariant testé par `tests/architecture/test_couches.py::test_ordre_des_dependances_entre_applications`.
**Décision** — L'intergiciel vit dans `app/administration/middleware.py`, pas `noyau`. Il appelle réellement `ServiceCompte.doit_changer_mot_de_passe`, respectant la lettre du § 2.2 sur ce point.
**Alternative écartée** — Garder l'intergiciel dans `noyau` et lire `request.user.doit_changer_mot_de_passe` (l'attribut brut) plutôt que la méthode du service : respecte le chemin de fichier du prompt, mais contourne exactement ce que le § 2.2 demande d'éviter — que la règle soit autre chose qu'« une méthode du service ». Écartée sur arbitrage explicite.
**Impact sur les livrables** — aucun sur la conception ; `MIDDLEWARE` dans `config/settings/base.py` référence `administration.middleware...` et non `noyau.middleware...`.
**Reporté au livrable** — non, à faire au prochain relevé du mémoire.

## D-07 — Deux règles de garde-fou, absentes de tout livrable — à porter au cahier des charges
**Date** 2026-09-02 · **Story** US-ADM-02 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — Rien dans les livrables n'empêche un administrateur de désactiver son propre compte, ou de désactiver (ou changer de profil) le dernier compte administrateur actif du système. Le résultat serait un système dont plus personne ne peut créer ni gérer de compte — irrécupérable sans intervention directe en base.
**Décision** — Deux contrôles posés dans `ServiceCompte` (`_interdire_autodesactivation`, `_interdire_perte_du_dernier_administrateur`) :
1. Un administrateur ne peut pas désactiver son propre compte.
2. Le dernier compte administrateur actif ne peut être ni désactivé, ni voir son profil changé vers autre chose qu'administrateur.

**À porter au cahier des charges comme règles métier nouvelles, avec leur code RG**, à l'initiative du binôme — ce n'est pas à moi de leur attribuer un numéro RG.
**Alternative écartée** — Ne rien contrôler et compter sur la vigilance humaine : le prompt de la story juge le risque trop élevé (« irrécupérable sans intervention en base »).
**Impact sur les livrables** — deux règles métier à ajouter au référentiel `RG-*`, avec renvoi vers `docs/conception/13-diagramme-classes.md` si elles affectent le diagramme d'états du compte.
**Reporté au livrable** — **non**, action attendue du binôme, pas automatique.

## D-06 — Le sens de `auteur` dépend du `type_action`
**Date** 2026-09-02 · **Story** US-ADM-02 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — RG-26 exige que la création et la modification d'un compte soient journalisées « avec auteur ». Contrairement à un échec d'authentification (D-03 : un seul compte en jeu, celui visé), une action de gestion de compte met en jeu **deux comptes distincts** — l'administrateur agissant et le compte créé/modifié/désactivé. `EntreeJournal.auteur` ne peut porter que l'un des deux.
**Décision** — Pour `creation_compte`, `modification_compte`, `changement_profil`, `desactivation_compte`, `reactivation_compte` : `auteur` porte **l'administrateur agissant**. Le compte visé va dans `cible` (son identifiant). Pour `echec_authentification` (US-ADM-01) : `auteur` reste **le compte visé** — il n'y a pas d'acteur authentifié, c'est le seul candidat sensé.
**Alternative écartée** — Garder `auteur` uniformément « le compte concerné », comme US-ADM-01 : aurait rendu RG-26 « avec auteur » incapable de désigner qui a agi pour cette story, alors que c'est précisément l'information que la règle demande de tracer.
**Impact sur les livrables** — le sens de `auteur` dépend donc du `type_action` — documenté dans la docstring d'`EntreeJournal`. À garder en tête pour l'écran de consultation (US-ADM-04) : une même colonne ne signifie pas la même chose sur toutes les lignes.
**Reporté au livrable** — non, à faire au prochain relevé du mémoire.

## D-05 — Page d'accueil technique, placeholder du redirecteur post-connexion
**Date** 2026-09-02 · **Story** US-ADM-01 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — Critère 1 de CU-P1-01 : « accède à la page d'accueil correspondant à son profil ». Aucun écran métier n'existe encore (hors périmètre explicite de la story), donc `LOGIN_REDIRECT_URL` n'a nulle part où pointer, et rien ne permet de vérifier que le contenu diffère par profil.
**Décision** — `noyau/accueil.html` + une vue minimale (`noyau/views.py::accueil`), affichant seulement `Bienvenue, {{ user.grade }} {{ user.last_name }}` et `Profil : {{ user.get_profil_display }}`. Aucune rubrique de navigation, aucune logique métier — juste assez pour que la connexion mène quelque part et que le critère 1 soit vérifiable.
**Alternative écartée** — Rediriger vers `/admin/` : aurait évité de créer un gabarit, mais n'aurait rien démontré sur le profil de l'utilisateur, et aurait exposé l'admin Django comme page d'atterrissage par défaut de tous les profils, y compris ceux qui ne devraient pas y accéder.
**Impact sur les livrables** — aucun sur la conception ; à remplacer par le vrai tableau de bord dès qu'une story en construit un.
**Reporté au livrable** — non applicable.

## D-04 — `EntreeJournal.cible` et index différés à US-ADM-04
**Date** 2026-09-02 · **Story** US-ADM-01 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — Le prompt US-ADM-01 liste `cible` parmi les champs minimaux d'`EntreeJournal` sans la définir ; ni RG-26 ni CU-P1-01 ne la mentionnent. Par ailleurs, `.claude/rules/migrations.md` anticipait des index (`idx_journal_horodatage`, `idx_journal_objet`) sur des colonnes (`horodatage`, `objet_type`, `objet_identifiant`) qui ne correspondent pas aux champs réellement posés (`cree_le`, `type_action`, `cible`).
**Décision** — `cible` peuplée avec la valeur littérale `"authentification"` pour cette story (la ressource visée, distincte de `auteur`, l'acteur) — générique pour que de futures actions sensibles s'y insèrent sans changer le sens du champ. Les deux index ne sont pas posés ici : rien dans US-ADM-01 n'interroge le journal, et les vrais motifs de filtre ne seront connus qu'à la construction de l'écran de consultation.
**Alternative écartée** — Poser les index tout de suite sur des noms de colonnes devinés : aurait figé un choix sans le vérifier contre l'usage réel.
**Impact sur les livrables** — `.claude/rules/migrations.md` reste à jour avec des noms de colonnes qui ne correspondent plus au modèle réel ; à corriger au moment d'US-ADM-04.
**Reporté au livrable** — non, à faire au prochain relevé du mémoire.

## D-03 — `EntreeJournal.auteur` distinct de `cree_par`/`modifie_par`
**Date** 2026-09-02 · **Story** US-ADM-01 · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — `ModeleHorodate` (socle) porte `cree_par`/`modifie_par` pour toute entité — qui a créé/modifié la ligne. RG-26 exige que le journal porte son propre « auteur » : le compte concerné par l'action journalisée, nullable si l'identifiant saisi ne correspond à aucun compte.
**Décision** — Les deux mécanismes cohabitent avec des rôles distincts. `cree_par`/`modifie_par` restent `None` sur toute entrée de journal : aucun utilisateur authentifié ne « crée » techniquement une entrée générée par le système lors d'une tentative de connexion. `auteur` porte le sens métier — le compte visé, pas l'auteur technique de l'écriture.
**Alternative écartée** — Réutiliser `cree_par` comme porteur du compte concerné : aurait fait porter deux sens différents (auteur technique de la ligne / sujet métier de l'action) au même champ, source de confusion dès qu'un vrai utilisateur authentifié écrira un jour dans le journal pour une autre action sensible.
**Impact sur les livrables** — aucun sur la conception ; précise l'usage de `ModeleHorodate` pour toute future entité de type journal.
**Reporté au livrable** — non, à faire au prochain relevé du mémoire.

## D-02 — Révocation RG-27 différée à US-ADM-04
**Date** 2026-09-02 · **Story** Socle technique (PROMPT_00) · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — RG-27 (immuabilité du journal) porte sur `administration_entree_journal`, qui n'existe pas encore : elle est hors périmètre du socle, `entree_journal` vient avec US-ADM-04.
**Décision** — Aucune révocation de privilège n'est posée dans `infra/postgres/init/01_roles.sql`. La révocation UPDATE/DELETE sur `administration_entree_journal` sera portée par une migration SQL explicite et réversible dans US-ADM-04, accompagnée d'un test ouvrant une connexion dédiée avec le rôle `pfe_cit_app` pour vérifier le refus.
**Alternative écartée** — Poser la révocation par anticipation : impossible techniquement (`REVOKE` sur une table absente échoue), et aurait dispersé une règle de sécurité loin de la migration qui crée la table qu'elle protège.
**Impact sur les livrables** — aucun sur la conception ; c'est la seule ligne du schéma où la sécurité repose sur les privilèges et non sur une contrainte déclarative — dette identifiée et datée, à traiter dès US-ADM-04, pas un oubli.
**Reporté au livrable** — non applicable, dette de développement, pas un écart de conception.

## D-01 — Deux rôles de connexion PostgreSQL (migration / application)
**Date** 2026-09-02 · **Story** Socle technique (PROMPT_00) · **Auteur** Lt Cissé (avec Claude Code)
**Contexte** — RG-27 exige la révocation d'UPDATE/DELETE sur `administration_entree_journal` pour le rôle applicatif ; poser l'extension `btree_gist` (RG-24) exige un rôle capable de `CREATE EXTENSION`. Un rôle de connexion unique aurait fini par cumuler ces deux besoins contradictoires.
**Décision** — Deux rôles PostgreSQL distincts dès le développement : `pfe_cit_migration` (propriétaire de la base, exécute les migrations, `CREATEDB` pour que pytest-django puisse créer/détruire la base de test) et `pfe_cit_app` (rôle applicatif restreint, aucun privilège de création, lecture/écriture accordée par `ALTER DEFAULT PRIVILEGES`). Vérifié empiriquement sur un conteneur PostgreSQL 16 : `btree_gist` étant une extension « trusted » depuis PostgreSQL 13, être propriétaire de la base suffit à `pfe_cit_migration` pour l'installer — aucun superutilisateur nécessaire, ce qui évite d'avoir à en demander un sur le poste du CIT.
**Alternative écartée** — Un rôle unique superutilisateur : plus simple à démarrer, mais rend la révocation RG-27 sans objet (un superutilisateur contourne toute révocation de privilège) et exigerait une élévation de droits sur le poste cible, potentiellement refusée en environnement militaire.
**Impact sur les livrables** — note d'implémentation §5.4 (immuabilité du journal) à compléter : elle mentionne la révocation mais pas le partage en deux rôles qui la rend possible sans bloquer les migrations. `infra/postgres/init/01_roles.sql` matérialise la décision ; `config/settings/local.py` pointe `pfe_cit_app` par défaut, `config/settings/test.py` pointe `pfe_cit_migration`.
**Reporté au livrable** — non, à faire au prochain relevé du mémoire.
