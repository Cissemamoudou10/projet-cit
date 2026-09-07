# Prompt Claude Code — 16 · Correction des écarts de recette

> Sprint 1. Suite de la recette manuelle du 4 septembre : 115 contrôles,
> **7 écarts majeurs, 8 mineurs**, ramenés à **trois causes racines**.
> À coller dans une session neuve, après `/clear`.

---

Une recette manuelle a été conduite en binôme sur le jeu de démonstration, écran par
écran, hors de tout test automatisé. Elle a trouvé sept défauts majeurs que **la suite
de tests n'avait pas signalés**.

C'est le point le plus important de ce prompt, et il commande la façon de travailler :
**si les tests passaient pendant que le logiciel échouait, les tests testent autre chose
que ce qui s'exécute.** Corriger le code sans comprendre ce silence garantit que le même
type de défaut reviendra.

Tu suis donc une discipline stricte : **diagnostic d'abord, test qui échoue ensuite,
correction en dernier.**

---

# 1 · Étape 1 — Diagnostiquer. Ne corrige rien.

Pour **chacune des trois causes racines** des § 3 à § 5, réponds à trois questions,
dans cet ordre :

1. **Quel est le défaut exact ?** Pas le symptôme observé à l'écran — la ligne de code
   ou l'absence de ligne qui le produit.
2. **Pourquoi la suite de tests ne l'a-t-elle pas vu ?** Test absent, test présent mais
   portant sur une couche que l'écran n'emprunte pas, ou test présent et faux.
3. **Quel test manquant l'aurait attrapé ?** Décris-le, ne l'écris pas encore.

Rends-moi ces neuf réponses et **attends ma validation**. Je veux comprendre le silence
des tests avant que tu le fasses cesser.

Une hypothèse à vérifier en priorité, et à confirmer ou infirmer explicitement : **les
vues appellent-elles bien les services ?** Un test de service qui passe pendant qu'une
vue échoue signifie presque toujours que la vue court-circuite le service. Si c'est le
cas, le défaut est architectural et dépasse les trois causes.

---

# 2 · La règle de correction — un test qui échoue avant chaque correctif

Pour chaque défaut, dans cet ordre :

1. écris le test qui **reproduit** le défaut ;
2. **exécute-le et montre-moi qu'il échoue** — un test de non-régression qui n'a jamais
   échoué ne prouve rien ;
3. corrige ;
4. montre-moi qu'il passe.

Ne groupe pas. Un défaut, un test, une correction, dans cet ordre.

---

# 3 · Cause racine n° 1 — le verrouillage après échecs répétés

**Écarts majeurs A9 et A10. Priorité absolue : c'est une règle de sécurité en défaut.**

## Ce qui a été observé

- Cinq échecs consécutifs sur un compte **ne le verrouillent pas**.
- Un compte qui devrait être verrouillé **accepte le bon mot de passe**.

## Ce qui est attendu — RG-03 et CU-P1-01

Après cinq échecs consécutifs, le compte est verrouillé quinze minutes. Les deux valeurs
sont **paramétrables** au titre de BNF-13 et ne doivent jamais être écrites en dur.

L'ordre des contrôles compte : compte inexistant, compte désactivé et **compte
verrouillé** se vérifient **avant** la comparaison du mot de passe. Un compte verrouillé
auquel on fournit le bon mot de passe **reste refusé** — c'est A10.

Le message de verrouillage est **distinct** du message générique d'identifiants
invalides, et il **ne donne pas l'heure de déverrouillage**.

## Trois hypothèses, à départager

1. le compteur d'échecs n'est jamais incrémenté ;
2. il l'est, mais n'est jamais comparé au seuil ;
3. le verrouillage est posé mais vérifié **après** la comparaison du mot de passe.

A9 et A10 en défaut ensemble oriente vers la première ou la deuxième.

## Tests à ajouter

Au niveau du **service** — ils existent peut-être déjà : dis-moi lesquels, et pourquoi
ils passent.

Et surtout **au niveau de la vue**, ce qui manque sûrement :

| Test | Vérifie |
|---|---|
| Cinq requêtes de connexion en échec → la sixième est refusée pour verrouillage | A9 |
| Compte verrouillé, requête avec le **bon** mot de passe → refus | A10 |
| Le message de verrouillage diffère du message générique | CU-P1-01, E3 |
| Il ne contient aucune heure ni durée | Décision du prompt 01 |
| Un succès après quatre échecs remet le compteur à zéro | RG-03 |
| Le seuil est lu dans les paramètres : le test le modifie et observe | BNF-13 |
| Le verrouillage est journalisé | RG-26 |

---

# 4 · Cause racine n° 2 — la modification concurrente n'est pas détectée

**Écart majeur E11, confirmé par un second essai.**

## Ce qui a été observé

Deux agents ouvrent la même formation. Le premier enregistre. Le second enregistre
ensuite : **son enregistrement réussit et écrase le premier**, sans aucun avertissement.

## Pourquoi c'est grave

Le travail d'un agent disparaît sans que personne le sache. Sur un centre où trois
cellules travaillent sur les mêmes données, c'est une perte silencieuse.

Et le défaut vit dans **`ServiceGestion`** : il touche donc **tous les écrans de gestion
du système** — types, formations, matières, objectifs, instructeurs, lieux, comptes. Un
seul correctif, à l'endroit juste.

## Ce qui est attendu — E5 de la fiche générique

Le mécanisme est celui que j'ai spécifié à US-REF-00 et qui n'a pas été implanté :

- le formulaire transporte, dans un champ caché, la valeur de `modifie_le` **lue à
  l'ouverture** ;
- le service **compare** cette valeur à celle en base **avant** d'écrire ;
- si elle diffère, il lève `ErreurModificationConcurrente` ;
- le message dit que la donnée a changé **et par qui** — l'auteur est dans
  `modifie_par`.

Aucun champ de version supplémentaire n'est nécessaire : `ModeleHorodate` fournit déjà
le jeton.

**La comparaison est faite dans le service, jamais dans le formulaire.** Le formulaire
ignore ce qui est en base au moment de l'écriture.

## Trois hypothèses

1. le champ caché n'est pas dans le formulaire ;
2. il y est mais le service ne compare pas ;
3. la comparaison existe mais échoue toujours à égalité — par exemple parce que la
   valeur transite en texte et perd sa précision.

La troisième est perfide : elle donnerait un test qui passe sur des objets fabriqués en
mémoire et un écran qui échoue. Vérifie-la.

## Tests à ajouter

| Test | Vérifie |
|---|---|
| Enregistrement avec un `modifie_le` obsolète → `ErreurModificationConcurrente` | E5 |
| Le message nomme l'auteur de la modification intercalée | E5 |
| **Par la vue** : deux requêtes successives, la seconde partant d'un état antérieur → refus | E11 |
| La première modification est **intacte** après le refus de la seconde | E11 |
| Un enregistrement normal, sans modification intercalée, réussit | Non-régression |
| Le mécanisme opère sur **au moins trois entités différentes** | Le correctif est dans le patron |

Le dernier est le plus important : il prouve que la correction est au bon endroit et non
recopiée écran par écran.

---

# 5 · Cause racine n° 3 — la suppression n'existe nulle part

**Écarts majeurs E9, F3, F4, I13. Quatre symptômes, un défaut.**

## Ce qui a été observé

Aucun bouton de suppression n'existe sur les types de formation, les formations, les
matières, ni ailleurs. La recette n'a donc pu vérifier ni qu'une suppression légitime
réussit, ni qu'une suppression illégitime est refusée.

## Ce qui s'est probablement passé

À US-ADM-02, j'avais tranché : *aucune suppression de compte, nulle part*, parce que
RG-04 la rendait impossible pour tout compte ayant servi. **Cette décision ne valait que
pour les comptes** et semble avoir été généralisée.

Le prompt d'US-REF-00 disait l'inverse, et je le cite : *archiver — toujours possible ;
supprimer — seulement si jamais référencé.*

## Pourquoi ce n'est pas sans conséquence

Trois critères d'acceptation du backlog présupposent que la suppression existe :

- *un type utilisé par au moins une formation ne peut être supprimé* — US-REF-00 ;
- *une matière utilisée dans au moins un référentiel ne peut être supprimée* —
  US-REF-02 ;
- *un lieu affecté à une brigade ou à une séance ne peut être supprimé* — US-PLAN-02.

Un critère qui interdit une opération inexistante n'est pas satisfait : il est sans
objet.

## Ce que tu implantes

La suppression conditionnelle, **dans `ServiceGestion`**, pas entité par entité.

| Action | Condition | Effet |
|---|---|---|
| **Archiver** | Toujours possible | Disparaît des listes de sélection, reste consultable et référencé |
| **Supprimer** | **Seulement si jamais référencé** | Disparaît définitivement |

Le mécanisme de contrôle **existe déjà** : la méthode d'énumération des éléments
bloquants, écrite à US-REF-01 et enrichie à chaque story. Il ne manque que le chemin
d'exécution, le bouton et la confirmation.

Le refus produit le message d'**E3** : l'énumération des éléments qui s'y opposent, pas
un refus sec.

**Entités concernées** : types de formation, formations, matières, objectifs
pédagogiques — déjà supprimables, à vérifier —, instructeurs, qualifications — déjà
supprimables —, lieux, **et les indisponibilités de lieu**, dont l'absence de
suppression a aussi été relevée en recette.

**Les comptes utilisateurs restent hors de ce mécanisme.** La décision d'US-ADM-02 tient
et n'est pas revenue dessus : aucun bouton, aucune vue, aucune méthode de suppression de
compte.

Confirmation par dialogue (§ 3.32) au titre de BNF-09, avec un texte **distinct de celui
de l'archivage** : l'un est réversible, l'autre non.

## Tests à ajouter

| Test | Vérifie |
|---|---|
| Suppression d'un élément jamais référencé → réussit | US-REF-00, F3 |
| Suppression d'un élément référencé → refus **énumérant les opposants** | E3, F4, E9, I13 |
| Un type portant des formations → refus les énumérant | US-REF-00, critère 3 |
| Une matière dans un référentiel → refus | US-REF-02, critère 5 |
| Une matière qualifiée → refus | US-INS-02 |
| **Aucune suppression de compte n'existe** | US-ADM-02, non-régression |
| Le mécanisme opère sur au moins trois entités | Le correctif est dans le patron |
| Chaque suppression est journalisée | Extension de RG-26 |

---

# 6 · Cinq corrections légères

À traiter en une passe, après validation des trois causes racines.

## 6.1 · A7 — les pages authentifiées restent en cache

Après déconnexion, le retour arrière du navigateur affiche l'accueil ; seul un
rechargement révèle la déconnexion.

Sur un poste partagé — et les postes du CIT le seront — le suivant voit l'écran du
précédent.

Pose des en-têtes de cache interdisant la conservation sur **toutes les réponses
authentifiées**, par un intergiciel plutôt qu'écran par écran. Vérifie que les fichiers
statiques restent, eux, cachables : les décacher rendrait chaque page plus lente sans
rien protéger.

**Test** : la réponse d'un écran authentifié porte l'en-tête ; celle d'un fichier
statique ne le porte pas.

## 6.2 · C2 et H2 — un bouton non masqué

Le bouton *Composer le référentiel* reste visible pour la cellule planification, alors
qu'elle n'a que la lecture. **Le serveur refuse bien** — le contrôle C3 est conforme —,
donc la sécurité tient ; c'est le critère 2 d'US-REF-07 qui est en défaut.

Filtre-le par l'appel **silencieux** d'habilitation, celui qui ne journalise pas.

**Et cherche les autres.** Ce bouton a échappé au test paramétré d'US-REF-07 : soit le
test ne couvre pas cet écran, soit il ne cherche pas cette commande. **Élargis-le**
plutôt que de corriger ce seul bouton — sinon le prochain passera aussi.

## 6.3 · F5 — la catégorie de lieu n'est pas affichée

La donnée existe, la colonne manque sur l'écran de composition du référentiel. Le prompt
d'US-REF-03 la demandait. Ajoute-la, avec le type de lieu partagé le cas échéant.

## 6.4 · F8 — le message d'intervalle ne s'affiche jamais

Un volume horaire nul est refusé **par le champ du navigateur**, avant tout envoi. Le
message d'E2 — *refus avec indication de l'intervalle attendu* — ne s'affiche donc
jamais, et personne ne peut vérifier que le serveur contrôle.

**La cause est un écart à la charte.** Le composant § 3.18, champ numérique à unité
accolée, emploie `type="text"` avec `inputmode="numeric"` : la saisie reste confortable
sur mobile, mais le navigateur ne bloque rien et le contrôle serveur s'exprime.
L'implantation a employé un champ numérique borné.

Aligne-toi sur la charte. **Vérifie si le même écart existe ailleurs** — capacité d'un
lieu, durée d'une formation.

**Test** : un volume nul envoyé au serveur produit le message d'intervalle attendu.

## 6.5 · La pagination affiche tous les numéros de page

Le composant § 3.10 de la charte parcourt **toutes** les pages. Sur cinq c'est
acceptable ; le journal en comptera soixante en quelques mois, et la barre deviendra
inutilisable — elle occupera plusieurs lignes.

Ce n'est pas une préférence d'affichage : c'est un défaut du composant, et il touche
**toutes les listes du système**.

Corrige-le dans le **gabarit générique**, pas dans chaque écran : au plus cinq numéros
autour de la page courante, avec *précédent* et *suivant*, et un repère lorsque des
pages sont omises.

**Consigne l'amendement dans `docs/suivi/`** : la charte devra être reprise, § 3.10.

**Test** : une liste de soixante pages n'affiche pas plus de cinq numéros ; la première
et la dernière page restent atteignables.

---

# 7 · Deux vérifications, sans correction

**I11 — l'écran de couverture d'US-INS-02.** Le prompt demandait, pour un référentiel
donné, ses matières et le nombre d'instructeurs qualifiés pour chacune. La recette ne
l'a pas trouvé dans la vue consolidée. **Existe-t-il ? Où ?** Réponds avant de créer
quoi que ce soit : s'il existe ailleurs, c'est un problème de chemin d'accès, pas de
fonction manquante.

**K3 — la mise en page d'impression déborde.** Les tableaux larges sont coupés. La cause
tient en partie à un arbitrage que j'ai rendu : la mise en page paysage a été retirée de
la feuille du navigateur parce que sa forme n'y est pas interprétée. **Deux voies
possibles** — réduire police et colonnes pour tenir en portrait, ou laisser l'agent
choisir le paysage dans la boîte d'impression. Analyse-les, chiffre-les, **ne corrige
pas** : je tranche.

---

# 8 · Ce que tu ne fais pas

Cinq remarques de la recette sont des **demandes d'évolution**, non des défauts. Aucun
critère d'acceptation ne les exige. Elles vont au carnet de produit pour arbitrage à la
revue du 12 septembre.

- afficher au catalogue le nombre d'objectifs, d'instructeurs qualifiés et de formations
  par matière ;
- la même information dans la vue consolidée du référentiel ;
- rendre le champ de filtre *objet* du journal plus compréhensible — une liste déroulante
  des types d'objet plutôt qu'un champ libre ;
- indiquer sur l'écran du journal pourquoi les colonnes *valeur avant* et *valeur après*
  sont vides pour les créations et les refus ;
- modifier une indisponibilité de lieu — **la supprimer relève, elle, du § 5**.

Les implanter maintenant gonflerait le périmètre sans trace, ce qu'un jury relève
immédiatement. **Consigne-les dans `docs/suivi/`** avec leur origine — le numéro du
contrôle de recette — et n'y touche pas.

---

# 9 · Vérification et livraison

- Les quinze tests d'architecture passent
- La suite complète passe, **et compte les tests que tu as ajoutés**
- `ruff check` et `ruff format --check` propres
- Migration seulement si le § 5 en impose une ; sinon aucune
- `npm run css:build` rejoué
- Relecture par le sous-agent `relecteur-conception`
- `docs/suivi/` : les neuf réponses de l'étape 1, l'amendement de la charte sur la
  pagination, les cinq demandes d'évolution avec leur origine, l'analyse du § 7, le
  temps passé
- Commit unique par cause racine, pas un commit fourre-tout

## Contrôles de recette à rejouer

Rends-moi la liste des contrôles que tes tests couvrent désormais, afin que le binôme ne
rejoue que ceux-là : **A7, A9, A10, C2, E9, E11, F3, F4, F5, F8, H2, I13**, plus les
listes paginées.

---

# 10 · La question de fond, à laquelle je veux une réponse

Sept défauts majeurs, aucun signalé par la suite de tests. Les tests d'architecture
passaient, les tests de service passaient, la couverture semblait bonne.

**Dis-moi ce qui manque à la façon dont ce projet teste**, et propose **une** mesure —
une seule, applicable dès le sprint 2. Pas cinq bonnes intentions : une règle qu'on peut
tenir.

Ma propre hypothèse, à confirmer ou à réfuter : les tests portent sur les services, où
vit la logique, et **presque rien ne traverse la vue**. Tout défaut situé entre la vue et
le service — un service non appelé, un champ absent du formulaire, une valeur perdue en
chemin — passe alors inaperçu. C'est exactement le profil des trois causes racines.

Commence par l'étape 1. Ne corrige rien avant ma validation.
