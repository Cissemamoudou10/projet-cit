# Prompt Claude Code — 17 · Pagination et enrichissement des listes

> Sprint 1, ligne WBS **5.1.20 — nouvelle ligne**, 4 h estimées.
> Fait suite à la recette du 4 septembre : une correction incomplète et cinq
> évolutions arbitrées par le chef de projet.
> À coller dans une session neuve, après `/clear`.

---

Deux sujets. Le premier est une **correction inachevée** : la pagination a été reprise
au mauvais endroit. Le second regroupe **cinq évolutions** demandées à la recette, que
j'avais écartées du prompt de correction et que je réintègre après arbitrage.

Ce sont des évolutions, pas des défauts : **aucun critère d'acceptation ne les exige**.
Elles s'inscrivent donc au carnet de produit comme ajouts, et non comme corrections.
§ 6.

---

# 1 · Bloc A — La pagination, reprise pour de bon

## 1.1 · Ce qui s'est passé

Le correctif demandé a été appliqué **au gabarit générique** issu du patron
`ServiceGestion`, écrit à US-REF-00.

Or le journal des actions sensibles a été construit à **US-ADM-04**, avant que ce patron
existe. Il porte son propre gabarit de liste. Le correctif ne l'a jamais atteint, et
l'écran affiche toujours vingt-trois numéros de page sur une seule ligne.

Les écrans du paquetage administration — comptes, journal, habilitations — sont dans le
même cas. **Vérifie-les tous.**

## 1.2 · La correction, cette fois au bon endroit

**Un seul fragment de gabarit de pagination pour tout le système.** Un fichier, inclus
partout, y compris par les écrans d'administration antérieurs au patron.

S'il faut modifier des gabarits écrits avant le patron pour qu'ils l'incluent, fais-le.
C'est le seul moyen que la prochaine correction de pagination — il y en aura une —
atteigne tout le monde.

## 1.3 · Le comportement attendu, sans ambiguïté

Au plus **cinq numéros de page** : la page courante, deux avant, deux après. Aux
extrémités, la fenêtre se décale pour en montrer cinq quand même.

**Précédent** et **suivant** toujours présents, dans l'état désactivé prévu par la charte
§ 3.10 lorsqu'ils ne mènent nulle part.

**Première et dernière page toujours atteignables**, en un clic, avec un repère
d'omission entre elles et la fenêtre. C'est un ajout à votre demande : sur vingt-trois
pages, sans cela, atteindre la dernière prend cinq clics.

Trois rendus attendus, à reproduire exactement :

```
page 1 sur 23     Précédent(désactivé)  1  2  3  4  5  …  23  Suivant
page 12 sur 23    Précédent  1  …  10  11  12  13  14  …  23  Suivant
page 23 sur 23    Précédent  1  …  19  20  21  22  23  Suivant(désactivé)
```

Sur cinq pages ou moins, aucun repère d'omission, tous les numéros affichés.

Le compte d'éléments — *éléments 21 à 40 sur 458* — est conservé tel quel : il vient de
la charte et il est utile.

La taille de page reste lue dans les paramètres, jamais écrite en dur : BNF-13.

## 1.4 · Accessibilité

La charte l'exige au § 5 et la recette l'a vérifié au contrôle K5 : navigation complète
au clavier, focus visible, `aria-current` sur la page courante, et un libellé
compréhensible pour chaque lien — *page 12* plutôt que *12* seul, pour un lecteur
d'écran.

Le repère d'omission n'est pas un lien et ne doit pas recevoir le focus.

## 1.5 · Tests

| Test | Vérifie |
|---|---|
| 23 pages, page 1 → cinq numéros, pas vingt-trois | § 1.3 |
| 23 pages, page 12 → fenêtre centrée, premier et dernier atteignables | § 1.3 |
| 23 pages, page 23 → *suivant* désactivé | § 1.3 |
| 3 pages → tous les numéros, aucun repère d'omission | § 1.3 |
| 1 page → *précédent* et *suivant* désactivés | Cas limite |
| **Le journal, la liste des comptes et une liste du référentiel rendent le même balisage** | § 1.2 |
| La taille de page est lue dans les paramètres | BNF-13 |

Le sixième est celui qui compte : il prouve que le fragment est partagé et non recopié.

---

# 2 · Bloc B — Compteurs dans les listes

Cinq emplacements, tous relevés à la recette. Le principe est le même partout : **une
liste doit dire ce qu'un objet coûterait à supprimer, avant qu'on essaie.**

C'est l'origine de la demande, au contrôle F3 : l'agent découvrait le refus de
suppression après coup, sans avoir jamais vu que la matière servait ailleurs.

## 2.1 · Catalogue des matières — trois compteurs

Origines : contrôles F3, G1, I8.

| Colonne | Contenu |
|---|---|
| **Formations** | Nombre de référentiels employant la matière |
| **Instructeurs** | Nombre d'instructeurs qualifiés, **non archivés** |
| **Objectifs** | Nombre d'objectifs pédagogiques |

Le compteur d'instructeurs à zéro reprend le signalement visuel déjà posé à US-INS-02,
critère 4 — **couleur doublée d'un mot**, charte § 1.2.

## 2.2 · Vue consolidée du référentiel

Origine : contrôle I11.

Le nombre d'instructeurs qualifiés apparaît **par matière**, dans la section des matières
et volumes. Le signalement à zéro y figure aussi.

Vérifie d'abord si l'écran de couverture demandé à US-INS-02 existe. S'il existe, la
question est celle du chemin d'accès, pas de la donnée. **Dis-le-moi avant d'écrire.**

## 2.3 · Liste des formations

Nombre de matières au référentiel, et **somme des volumes prescrits**. La colonne du
nombre de formations par type existe déjà à US-REF-00 : c'est la symétrie.

## 2.4 · Liste des instructeurs

Nombre de qualifications. Un instructeur qualifié pour rien est aussi signalant qu'une
matière que personne ne peut enseigner.

## 2.5 · Liste des lieux

Nombre d'indisponibilités **à venir**, les passées n'intéressant personne à la
consultation.

## 2.6 · La contrainte technique qui commande ce bloc

**Aucun compteur ne se calcule ligne par ligne.**

Compter dans une boucle de gabarit produit une requête par ligne : vingt lignes, trois
compteurs, soixante requêtes pour une page. Sur le poste du CIT, personne ne
diagnostiquera une page lente.

Emploie une **agrégation en une seule requête** pour toute la page.

**Test obligatoire** : le nombre de requêtes de la liste des matières **ne dépend pas du
nombre de lignes affichées**. Compte les requêtes sur cinq lignes, puis sur vingt : le
nombre doit être identique. C'est le seul test qui empêche la régression, et il vaut pour
les cinq emplacements.

## 2.7 · Présentation

Colonnes numériques : `tabular-nums`, alignées à droite, en-têtes selon la charte
§ 3.08. Libellés courts — *Formations*, *Instructeurs*, *Objectifs* — la place est
comptée.

Ces colonnes s'impriment : vérifie qu'elles n'aggravent pas le débordement relevé au
contrôle K3, encore en attente d'arbitrage. **Si elles l'aggravent, dis-le-moi** —
peut-être devront-elles être masquées à l'impression.

---

# 3 · Bloc C — Deux corrections sur l'écran du journal

Origine : contrôle D4.

## 3.1 · Le champ de filtre « objet »

Il est incompris parce que son intitulé induit en erreur. L'agent y a saisi
*modification*, qui est une **nature d'action** et non un objet, et n'a rien obtenu.

Remplace le champ libre par une **liste déroulante des types d'objet** — formation,
matière, compte, instructeur, lieu, qualification —, accompagnée d'un champ
d'identifiant facultatif.

Un champ libre portant sur un identifiant technique ne sera jamais rempli correctement,
et il n'a aucune raison de l'être : ce n'est pas une donnée que l'agent connaît par cœur.

## 3.2 · Les colonnes « valeur avant » et « valeur après » vides

Elles ne se remplissent que pour les **modifications**. Une création n'a pas de valeur
antérieure ; un refus d'habilitation ne modifie rien. Le comportement est juste, mais
l'écran laisse deux colonnes vides sans explication.

Affiche une mention brève — *sans objet pour cette nature d'action* — plutôt qu'un vide.
Un vide se lit comme une donnée manquante, et quelqu'un finira par ouvrir une anomalie.

---

# 4 · Bloc D — Modifier une indisponibilité de lieu

Origine : remarque du parcours J.

La suppression a été traitée au prompt de correction. **La modification manque encore.**

Elle emprunte le même formulaire que la déclaration, et **repasse par les mêmes
contrôles** : fin postérieure au début, et surtout **absence de chevauchement avec les
autres périodes du même lieu** — la contrainte d'exclusion posée à US-PLAN-02.

Le piège est là. Une modification qui déplace une période sur une autre doit être
refusée, **et la période en cours de modification ne doit pas se compter elle-même comme
un conflit**. C'est l'erreur classique : la contrainte détecte le chevauchement de la
période avec sa propre version enregistrée, et toute modification devient impossible.

**Tests :**

| Test | Vérifie |
|---|---|
| Modifier le motif seul → réussit | Nominal |
| Décaler les bornes sans conflit → réussit | § 4 |
| **Modifier sans déplacer les bornes → réussit** | Le piège ci-dessus |
| Déplacer sur une période existante → refus nommant la période | Contrainte d'exclusion |
| Déplacer jusqu'à être contiguë → **réussit** | Cas limite d'US-PLAN-02 |
| Fin avant début → refus | Contrainte de vérification |
| La modification est journalisée | Extension de RG-26 |

---

# 5 · Ce que tu ne fais pas

Ce prompt ne rouvre **aucune** décision antérieure.

- Pas de suppression de compte : la décision d'US-ADM-02 tient.
- Pas de reprise de la mise en page d'impression : le contrôle K3 attend mon arbitrage,
  fondé sur ton analyse.
- Pas de nouveau compteur au-delà des cinq du § 2.
- Aucun compteur cliquable menant à une liste filtrée. C'est une bonne idée ; ce n'est
  pas demandé.

---

# 6 · Traçabilité — le point à ne pas négliger

Les blocs B, C et D **ne corrigent aucun critère d'acceptation** : ils en ajoutent.

Consigne dans `docs/suivi/` un tableau : pour chaque évolution, le **contrôle de recette
qui l'a fait naître** — F3, G1, I8, I11, D4, remarque J —, ce qui a été fait, et le
temps passé.

Sans cette trace, le système comporte des fonctions que rien ne justifie dans le cahier
des charges. C'est exactement ce qu'un jury relève : *d'où vient cette colonne ? qui l'a
demandée ?* La recette est une source de besoin parfaitement légitime, à condition
qu'elle soit écrite.

Le bloc A, lui, achève une correction : il se rattache au contrôle D4 comme défaut, pas
comme évolution.

---

# 7 · Vérification et livraison

- Les quinze tests d'architecture passent
- La suite complète passe, comptant les tests ajoutés
- **Le test de non-croissance des requêtes du § 2.6 passe sur les cinq listes**
- `ruff check` et `ruff format --check` propres
- Aucune migration : ce prompt n'ajoute aucune donnée persistée
- `npm run css:build` rejoué
- Relecture par le sous-agent `relecteur-conception`
- `docs/suivi/` : le tableau de traçabilité du § 6, l'amendement de la charte sur la
  pagination § 3.10, la réponse sur l'écran de couverture § 2.2, l'effet des nouvelles
  colonnes sur l'impression § 2.7, le temps passé
- Un commit par bloc

## Contrôles à rejouer par le binôme

Rends-moi la liste, pour qu'ils ne reprennent que le nécessaire. A priori : la pagination
sur le journal **et** sur deux autres listes, le catalogue des matières, la vue
consolidée, les listes de formations, d'instructeurs et de lieux, le filtre *objet* du
journal, et la modification d'une indisponibilité.

Commence par me dire, avant tout code, **quels gabarits de liste existent aujourd'hui et
lesquels n'incluent pas le fragment de pagination partagé**. C'est cette réponse qui
mesure l'ampleur réelle du bloc A.
