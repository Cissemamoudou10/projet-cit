# Prompt Claude Code — 02 · US-ADM-02 · Gérer les comptes utilisateurs

> Sprint 1, ligne WBS 5.1.3. Must, 5 points, 6,5 h estimées. Story en **binômage**.
> Prérequis : US-ADM-01 est finie — `ServiceJournal`, `base_public.html` et les
> gabarits d'ossature existent.
> À coller dans une session neuve, après `/clear`.

---

Nous développons **US-ADM-02 — Gérer les comptes utilisateurs**. Tu suis les huit
étapes du workflow `/story`, avec arrêt obligatoire sur ma validation avant
l'implantation.

## Traçabilité — à recopier dans le message de commit

`BF-ADM-02 → US-ADM-02 → CU-P1-02 → RG-01, RG-04, RG-26 → CLS-01`

---

# 1 · Le besoin

*En tant qu'administrateur, je veux créer, modifier et désactiver des comptes
utilisateurs, afin de contrôler qui accède au système.*

## Critères d'acceptation — backlog v7

1. L'administrateur crée un compte en renseignant identité, identifiant et profil.
2. Un compte peut être désactivé sans être supprimé, afin de préserver l'historique
   des actions.
3. Un compte désactivé ne peut plus s'authentifier.
4. L'identifiant est unique ; toute tentative de doublon est refusée avec un message
   explicite.
5. Seul un administrateur accède à cette fonctionnalité.

## Le cas d'utilisation

CU-P1-02 renvoie à la **fiche générique des cas d'utilisation de gestion**, plus
quatre écarts. La fiche générique donne le déroulement :

**Consultation.** L'acteur accède à la liste ; le système la présente **paginée et
dotée d'une recherche** sur les champs identifiants dès que le nombre d'éléments peut
dépasser vingt (BNF-15) ; l'acteur filtre, puis ouvre le détail.

**Création et modification.** L'acteur saisit, le système valide, enregistre,
horodate et rattache l'opération à son auteur.

**Les quatre écarts propres à CU-P1-02 :**

1. L'identifiant est unique.
2. **La désactivation remplace la suppression.** Un compte ayant produit des entrées
   de journal ne peut être supprimé (RG-04).
3. **Le mot de passe initial est défini par l'administrateur, et son changement est
   exigé à la première connexion.**
4. Le profil est modifiable, mais **tout changement est journalisé**.

## Règles métier et exigences

| Code | Énoncé |
|---|---|
| **RG-01** | Un compte est rattaché à un et un seul profil parmi les cinq définis |
| **RG-02** | Le profil de l'acteur l'habilite au cas d'utilisation — contrainte transversale |
| **RG-04** | Un compte ayant produit des entrées de journal ne peut être supprimé |
| **RG-26** | Sont journalisées, avec auteur et horodatage : **la création et la modification d'un compte**, entre autres |
| **BNF-03** | Condensats — le mot de passe initial n'échappe pas à la règle |
| **BNF-10** | Messages indiquant l'action attendue |
| **BNF-14** | Horodatage et auteur, par la classe de base |
| **BNF-15** | Pagination et recherche au-delà de vingt éléments |

---

# 2 · Quatre décisions déjà tranchées

## 2.1 · Aucune suppression, nulle part

RG-04 interdit la suppression d'un compte ayant produit des entrées de journal.
Plutôt que d'implanter une suppression conditionnelle — qui échouerait pour tout
compte ayant servi, c'est-à-dire tous — **l'interface n'expose aucune suppression**.
Seule la désactivation existe. Le critère 2 le dit d'ailleurs directement.

Aucun bouton, aucune vue, aucune méthode de service de suppression. Si un jour un
compte créé par erreur doit disparaître, cela relèvera d'une intervention
d'administration hors application.

## 2.2 · Le changement à la première connexion se pose en intergiciel

Un contrôle placé dans la vue d'accueil se contourne en tapant une autre adresse.
Il faut donc un **intergiciel** qui, pour toute requête d'un utilisateur authentifié
dont le drapeau est levé, redirige vers l'écran de changement de mot de passe — en
laissant passer cet écran lui-même, la déconnexion et les fichiers statiques, faute
de quoi la redirection boucle.

L'intergiciel appartient à la couche présentation : il redirige, il ne décide pas.
La règle — *ce compte doit-il changer son mot de passe* — est une méthode du service.

## 2.3 · Le drapeau est un champ du modèle, donc une migration

Le modèle `Utilisateur` posé au socle ne porte pas ce champ. Ajoute
`doit_changer_mot_de_passe`, booléen, défaut `True` à la création par
l'administrateur, abaissé au premier changement réussi.

C'est la seule modification du modèle dans cette story. Elle vient avec sa migration.

## 2.4 · Un garde-fou que les livrables n'ont pas prévu

Rien n'empêche aujourd'hui un administrateur de désactiver son propre compte, ou de
désactiver le dernier administrateur actif du système. Le résultat serait un système
dont plus personne ne peut créer de compte — irrécupérable sans intervention en base.

Tu poses donc deux contrôles dans le service :

- un administrateur ne peut pas désactiver son propre compte
- le dernier compte administrateur actif ne peut pas être désactivé, ni voir son
  profil changé

Ces deux règles ne figurent dans aucun livrable. **Signale-le dans `docs/suivi/`** :
je les porterai au cahier des charges comme règles nouvelles, avec leur code. En
attendant, elles vivent dans le service avec un commentaire renvoyant à cette note.

---

# 3 · Étape 0 — Explorer

Lis `app/administration/` en entier — le modèle, `ServiceAuthentification`,
`ServiceJournal`, les gabarits d'US-ADM-01 —, `app/noyau/pagination.py`,
`app/noyau/habilitations.py`, et `.claude/rules/`.

Dans `docs/charte/`, les sections **3.08** (tableau dense), **3.09** (tri),
**3.10** (pagination), **3.11** (barre de filtres), **3.13** (état vide),
**3.17** (champ texte), **3.20** (liste déroulante), **3.24** (formulaire à deux
colonnes), **3.25** (pied de formulaire), **3.29** (badge, pour le motif de
l'aplat contre le contour), **3.32** (boîte de dialogue), **3.39** (boutons),
**3.40** (bouton d'action de ligne).

Rends-moi ce que tu reprends, section par section.

# 4 · Étape 1 — Planifier. Attends ma validation.

Plan complet : fichiers, ordre, tests, et le contenu exact de la migration. Signale
toute décision que le plan te force à prendre et qui n'est pas tranchée en § 2.
**N'écris rien avant mon accord.**

---

# 5 · La couche services

`app/administration/services/comptes.py` — `ServiceCompte`.

Méthodes attendues, chacune prenant **l'utilisateur agissant en paramètre explicite** :

- `creer(agissant, donnees)` → crée, pose `doit_changer_mot_de_passe = True`,
  journalise
- `modifier(agissant, compte, donnees)` → journalise, et **journalise séparément tout
  changement de profil**, avec l'ancienne et la nouvelle valeur (écart 4)
- `desactiver(agissant, compte)` → contrôles du § 2.4, journalise
- `reactiver(agissant, compte)` → journalise
- `definir_mot_de_passe_initial(agissant, compte, mot_de_passe)`
- `changer_mot_de_passe(compte, ancien, nouveau)` → abaisse le drapeau
- `doit_changer_mot_de_passe(compte)` → la règle que l'intergiciel consulte
- `lister(filtres, page)` → s'appuie sur la pagination du noyau

**Aucun objet HTTP** dans ce fichier. **Aucune suppression.**

Le mot de passe passe toujours par `set_password`. Aucune affectation directe, aucun
mot de passe en clair stocké nulle part, y compris à titre temporaire.

Les validateurs de mot de passe de Django s'appliquent au mot de passe initial comme
au changement.

---

# 6 · Les contraintes portées en base

L'unicité de l'identifiant est déjà assurée par `AbstractUser`. **Vérifie-le plutôt
que de l'ajouter en double** : une contrainte redondante produit deux messages
d'erreur différents selon le chemin.

Le message du critère 4 est explicite — *cet identifiant est déjà attribué* — et
remonte de la contrainte, pas d'un contrôle préalable en Python : entre la
vérification et l'écriture, un autre administrateur peut avoir créé le même compte.

---

# 7 · La présentation

Trois écrans, plus l'intergiciel.

## 7.1 · Liste des comptes

Étend `noyau/base.html`. Tableau dense (§ 3.08), en-tête figé et tri (§ 3.09),
pagination (§ 3.10), barre de filtres (§ 3.11), état vide (§ 3.13).

Colonnes : identifiant, grade et nom, profil, état, dernière connexion, actions.

Recherche sur identifiant, nom et grade. Filtres sur le profil et sur l'état.

**Badge d'état.** La charte n'en propose pas pour un compte. Compose-le sur le motif
du § 3.29 — aplat pour l'état actif, contour pour l'état désactivé — et **double la
couleur d'un mot**, conformément au § 1.2. Les classes viennent des jetons existants,
tu n'en inventes aucune.

Bouton d'action de ligne (§ 3.40) pour la modification. La désactivation passe par
une boîte de dialogue de confirmation (§ 3.32), variante destructive.

## 7.2 · Création et modification

Formulaire à deux colonnes (§ 3.24) : *Identité* et *Accès*. Pied de formulaire
(§ 3.25), sans le bouton « Enregistrer en brouillon » — un compte n'a pas d'état
intermédiaire.

À la création, le mot de passe initial est saisi par l'administrateur. Un encadré
d'information (§ 3.30) rappelle que l'utilisateur devra le changer à sa première
connexion.

**Le mot de passe initial n'est jamais réaffiché après l'enregistrement**, ni dans un
message, ni dans le détail du compte, ni dans le journal.

À la modification, le mot de passe n'apparaît pas : sa réinitialisation est une action
distincte.

## 7.3 · Changement de mot de passe à la première connexion

Écran étendant **`base_public.html`** : l'utilisateur est authentifié mais n'a encore
accès à rien, et l'ossature complète l'inviterait à naviguer alors que l'intergiciel
le renverra ici.

Ancien mot de passe, nouveau, confirmation. Les erreurs se rendent par l'état erreur
du § 3.17.

## 7.4 · L'intergiciel

`app/noyau/middleware.py`. Pour toute requête d'un utilisateur authentifié dont le
service dit que le mot de passe doit changer, redirection vers cet écran.

**Laisse passer** : l'écran lui-même, la déconnexion, les fichiers statiques. Sans
cela, la redirection boucle et l'utilisateur ne peut plus rien faire, pas même se
déconnecter.

## 7.5 · Navigation

C'est la première rubrique réelle du système. Ajoute *Administration* à la liste
`rubriques`, servie par le processeur de contexte du noyau, visible seulement pour le
profil administrateur — contrôle par `verifier_habilitation`, celui qui existe déjà.

**La matrice fine des droits reste à US-ADM-03.** Ici, un seul point de contrôle : la
rubrique et ses vues sont réservées à l'administrateur (critère 5), vérifié **dans le
service**, la vue ne faisant que doubler.

## 7.6 · Recompilation du CSS

`npm run css:build` avant les tests d'interface. Rends-moi la variation de taille.

---

# 8 · Tests

## Service

| Test | Vérifie |
|---|---|
| Création → compte actif, drapeau levé, entrée de journal | Critère 1, RG-26 |
| Création avec identifiant existant → refus, message explicite | Critère 4 |
| Le mot de passe initial est stocké en condensat | BNF-03 |
| Le mot de passe initial n'apparaît dans aucune entrée de journal | BNF-03 |
| Désactivation → compte inactif, non supprimé, journalisé | Critère 2 |
| Un compte désactivé ne peut plus s'authentifier | Critère 3 |
| Changement de profil → entrée de journal portant ancienne et nouvelle valeur | Écart 4 |
| Un administrateur ne peut pas se désactiver lui-même | § 2.4 |
| Le dernier administrateur actif ne peut être ni désactivé ni changé de profil | § 2.4 |
| Un non-administrateur appelant le service → `ErreurHabilitation` | Critère 5 |
| Changement de mot de passe réussi → drapeau abaissé | Écart 3 |
| Aucune méthode de suppression n'existe sur le service | § 2.1 |

Le test sur le compte désactivé passe par `ServiceAuthentification`, pas par une
vérification de drapeau : c'est le comportement qui compte, pas l'attribut.

## Intergiciel et vues

| Test | Vérifie |
|---|---|
| Utilisateur au drapeau levé demandant n'importe quelle URL → redirigé | § 2.2 |
| Le même sur l'écran de changement → non redirigé | Boucle |
| Le même demandant la déconnexion → non redirigé | Boucle |
| Après changement réussi → accès normal | Écart 3 |
| Un non-administrateur atteignant la liste → refus | Critère 5 |
| Liste au-delà de vingt comptes → paginée | BNF-15 |
| La recherche filtre sur identifiant, nom et grade | BNF-15 |
| Aucune vue ni URL de suppression n'existe | § 2.1 |
| Le mot de passe initial n'apparaît dans aucune réponse après création | BNF-03 |

---

# 9 · Vérification et livraison

- Les quatorze tests d'architecture passent
- `ruff check` et `ruff format --check` propres
- La migration est unique, réversible, et `makemigrations --check --dry-run` est muet
- `npm run css:build` rejoué
- Relecture par le sous-agent `relecteur-conception`
- `docs/suivi/` : les deux règles nouvelles du § 2.4 signalées pour report au cahier
  des charges, décisions, écarts à la charte, temps réel passé
- Commit portant la ligne de traçabilité

---

# 10 · Hors périmètre

- Matrice fine des droits par profil et par cas d'utilisation → **US-ADM-03**
- Écran de consultation du journal et ses filtres → **US-ADM-04**
- Révocation des privilèges sur la table de journal → **US-ADM-04**
- Réinitialisation d'un mot de passe oublié par l'utilisateur lui-même : **hors
  périmètre du projet**
- Toute suppression de compte

# 11 · Définition de fini

Les cinq critères d'acceptation sont couverts par un test nommé, les quatre écarts de
CU-P1-02 sont implantés et testés, aucune règle métier ne vit dans une vue, aucun mot
de passe n'est écrit en clair où que ce soit, aucune suppression n'existe, les écrans
sont bâtis sur les composants de la charte sans classe inventée, et les deux règles
nouvelles sont consignées pour report au cahier des charges.

Commence par l'étape 0.
