# Débordement à l'impression (contrôle K3) — analyse, bloc B du Prompt 19

Aucune implantation dans ce document — analyse seule, pour arbitrage. Cadre
rappelé par le Prompt 19, § 2 : l'arbitrage porte sur **l'impression
navigateur seule** (`app/noyau/static/css/impression.css`). La mise en page
paysage au sens de la mise en page CSS paginée (page nommée, boîtes de
marge) n'est interprétée par aucun navigateur ; elle vit dans
`document_pdf.css`, réservée à WeasyPrint au sprint 4 — hors sujet ici.

## 1. État réel mesuré

Mesuré le 2026-09-08 en aperçu émulé (feuille `impression.css` injectée,
largeur de contenu contrainte à 703 px — la largeur imprimable réelle d'une
page A4 portrait avec les marges de `impression.css`, 14/12/12/16 mm),
graphismes d'arrière-plan désactivés, sur les cinq écrans modifiés par le
bloc B du Prompt 17 :

| Écran | Largeur du tableau | Dépassement | Cause principale observée |
|---|---|---|---|
| Matières (liste) | 653 px | — (tient, 2 px de marge) | — |
| Formations (liste) | 715 px | **60 px (~9 %)** | colonne Actions (icônes crayon/cadenas/corbeille) |
| Instructeurs (liste) | 768 px | **113 px (~17 %)** | colonne Actions + badge « Militaire du centre » |
| Lieux (liste) | 801 px | **146 px (~22 %)** | colonne Actions + sept colonnes de données, dont deux à intitulé long |
| Vue consolidée du référentiel (consultation) | 653 px | — (tient, 2 px de marge) | — (pas de colonne Actions, écran lecture seule) |

**Trois écrans sur cinq débordent réellement.** Détail utile à l'arbitrage :
sur les trois écrans en défaut, masquer seule la colonne Actions (icônes
d'action, sans objet sur un document imprimé) suffit à faire rentrer
Formations (60 px → tient), ramène Instructeurs à 33 px de dépassement et
Lieux à 74 px — dans les deux derniers cas, insuffisant seul.

**Constat supplémentaire, indépendant du débordement lui-même.** La colonne
Actions et le bouton d'en-tête (« Créer une … ») s'impriment aujourd'hui sur
les cinq écrans : `impression.css`, § 2, prévoit déjà le mécanisme
(`data-impression="masquer"`) mais aucun gabarit de liste ne le pose sur ces
éléments — la note du fichier l'annonçait comme réservé « à la première
story qui transpose § 3.41 en gabarit Django », jamais fait depuis pour les
écrans de liste eux-mêmes.

**Constat sur l'option paysage.** `impression.css`, § 1, fixe aujourd'hui
`@page { size: A4 portrait; }`. Cette déclaration explicite de l'orientation
est, selon le comportement documenté de Chrome, ce qui verrouille le
sélecteur d'orientation de la boîte d'impression sur « Portrait » — **l'agent
ne peut pas choisir le paysage aujourd'hui**, quelle que soit la voie
retenue par cet arbitrage, tant que cette ligne n'est pas modifiée. Ce point
n'a pas été vérifié en déclenchant réellement la boîte d'impression (les
consignes de cette session l'interdisent) ; il repose sur le comportement
documenté du moteur de rendu, à confirmer par un essai manuel si l'option 2
est retenue.

## 2. Option 1 — réduire police et colonnes pour tenir en portrait

**Ce qui referait rentrer chaque écran :**

- **Formations** — masquer la colonne Actions (`data-impression="masquer"`,
  mécanisme déjà prévu, zéro CSS nouveau). Suffit intégralement (60 px → -2 px).
- **Instructeurs** — masquer Actions (113 px → 33 px), puis un ajustement
  ciblé pour les 33 px restants : réduire le remplissage des cellules
  (`impression.css`, `tbody td` passe de `2px 6px` à `2px 4px`, ~28 px
  récupérés sur sept colonnes) suffit probablement, à vérifier après coup.
- **Lieux** — masquer Actions (146 px → 74 px), insuffisant seul. Les 74 px
  restants exigent un choix de contenu, pas seulement de mise en forme :
  abréger l'intitulé « Indisponibilités à venir » (colonne la plus large
  après Actions) ou la retirer de la vue imprimée. **C'est une perte
  d'information sur le papier, pas un simple ajustement visuel — nécessite
  votre arbitrage, pas seulement le mien.**

**Effort estimé** : environ 1 h — poser l'attribut sur les `<th>`/`<td>`
Actions des quatre gabarits de liste concernés (`matiere_liste.html` par
cohérence même si non nécessaire, `formation_liste.html`,
`instructeur_liste.html`, `lieu_liste.html`), ajuster le remplissage des
cellules dans `impression.css`, puis trancher et implanter le sort de la
colonne « Indisponibilités à venir » pour Lieux.

**Coût en lisibilité** : nul pour le masquage d'Actions (aucune icône
cliquable n'a de sens sur un document imprimé). Faible pour le remplissage
resserré (8,5 pt reste lisible ; encore un peu de marge avant l'illisible).
Réel et à trancher pour Lieux si la colonne des indisponibilités est
retirée ou abrégée — une information qui existe à l'écran disparaîtrait du
papier.

**Bénéfice** : correction une fois pour toutes, aucune action requise de qui
imprime, aucun risque d'oubli.

## 3. Option 2 — laisser l'agent choisir le paysage

**Ce qu'il faudrait changer** : une ligne, `impression.css` § 1 —
`size: A4 portrait;` → `size: A4;` (ou retirer la mention d'orientation),
pour rendre au sélecteur de la boîte d'impression son fonctionnement normal.
En paysage, la largeur imprimable passe à environ 1032 px (297 mm − 24 mm de
marges) : les trois écrans en défaut (801 px au pire, Lieux) y tiendraient
largement, colonne Actions comprise, sans aucun autre changement.

**Effort estimé** : quelques minutes — une ligne de CSS, un essai manuel en
boîte d'impression pour confirmer que le sélecteur d'orientation est bien
disponible (point non vérifié par cette session, voir § 1).

**Coût en lisibilité** : aucun sur le document lui-même — le contenu ne
change pas.

**Coût en fiabilité, à mettre en balance** : cette option ne corrige rien
par elle-même, elle **rend le choix possible**. Sans lui, l'agent qui
imprime un écran de lieux ou d'instructeurs obtient exactement le
débordement mesuré au § 1, à chaque fois qu'il oublie de sélectionner
« Paysage » — aucun mécanisme ne le rappelle ni ne l'impose. Le geste est à
répéter à chaque impression, sur un centre où plusieurs profils impriment
ces écrans sans consigne écrite pour l'orientation.

## 4. Arbitrage du 2026-09-08 (D-63)

**Retenu : le paysage — mais après le masquage de la colonne Actions, pas à
sa place.** Les deux voies ne s'excluaient pas : masquer une commande n'est
pas masquer une donnée (voir D-63), c'est une étape distincte, appliquée en
premier.

**Le masquage d'une colonne de DONNÉE est explicitement refusé**, quel que
soit le débordement résiduel : retirer silencieusement une information d'un
document qui circule dans le centre est pire qu'une mise en page
imparfaite — le lecteur n'a aucun moyen de savoir qu'il lui manque quelque
chose, même principe que la règle de la charte sur les couleurs doublées
d'un mot. La piste envisagée au § 2 pour Lieux (abréger ou retirer
« Indisponibilités à venir ») est donc écartée, pas seulement reportée.

**Étape 1, implantée** — `data-impression="masquer"` posé sur la colonne
Actions du patron de gestion (`noyau/templates/noyau/gestion/liste.html`),
une seule modification pour les cinq écrans. Remesuré le 2026-09-08 :

| Écran | Avant (Actions visible) | Après (Actions masquée) |
|---|---|---|
| Formations | 60 px de dépassement | **Tient** (-2 px de marge) |
| Instructeurs | 113 px | 33 px — déborde encore |
| Lieux | 146 px | 74 px — déborde encore |

Formations est réglé par le seul masquage — suffisant pour clore le
contrôle K3 sur cet écran au sprint 1.

## 5. Clôture du sprint 1, point ouvert reporté au sprint 4

**Instructeurs (33 px) et Lieux (74 px) débordent encore.** Le principe
retenu pour la suite reste le paysage plutôt qu'un masquage de donnée (§ 4),
avec une mention visible uniquement à l'impression indiquant l'orientation
attendue — sans elle, un tableau coupé sans explication serait imprimé
plusieurs fois avant d'être compris. **Rien n'est implanté** : reporté au
sprint 4, avec les gabarits des documents imprimables déjà prévus à ce
sprint (`docs/suivi/sprint-4.md`) plutôt que traité isolément ici — voir ce
fichier pour le point de suivi.

## 6. Sprint 2 — US-SES-04 et US-SES-05, mesuré le 2026-09-12

Même protocole qu'au § 1 (feuille `impression.css` injectée, largeur
contrainte à 703 px, graphismes d'arrière-plan désactivés), sur les deux
écrans de liste ajoutés par ces deux stories. Les deux tiennent — aucun
arbitrage requis :

| Écran | Largeur du tableau | Dépassement |
|---|---|---|
| Fiche session — brigades et occupation (US-SES-04) | 701 px | — (tient, 2 px de marge) |
| Stagiaires d'une session (US-SES-05) | 653 px | — (tient) |
| Écran de répartition — affectations par brigade (US-SES-06, mesuré le 2026-09-12) | 653 px | — (tient) |
| Liste des stagiaires, colonne Brigade ajoutée, sept colonnes (US-SES-07, mesuré le 2026-09-12) | 653 px | — (tient, malgré la mise en garde du § 7 du Prompt 26 sur les écrans à sept colonnes textuelles) |

Ces deux écrans utilisent déjà le patron de gestion (`data-impression="masquer"`
sur la colonne Actions, § 4) — la colonne Actions n'apparaît donc pas dans la
largeur mesurée, conformément à D-63.

**Bogue latent découvert pendant la mesure, non corrigé ici.** La méthode de
mesure par simple injection de `<style>` (utilisée sans problème au § 1) ne
fonctionne plus telle quelle : `noyau/base.html` pose désormais la classe
Tailwind `min-w-[1280px]` sur `<body>`, dont la spécificité de sélecteur de
classe l'emporte sur le sélecteur de balise `body { min-width: 0 }` de
`impression.css`, `!important` ou pas. Contournement utilisé pour cette seule
mesure (sonde JavaScript éphémère, pas de changement de dépôt) :
`document.body.style.setProperty('min-width', '0', 'important')` (idem pour
`width`/`max-width`) — seule une déclaration en ligne passe outre un
sélecteur de classe. **Conséquence potentielle non vérifiée davantage** :
si un navigateur réel applique la même cascade que cette émulation, la
largeur du corps de page pourrait ne pas être réellement contrainte à
l'impression aujourd'hui, quel que soit le contenu du tableau — à vérifier
par un essai de boîte d'impression réelle avant le sprint 4, où le sujet est
de toute façon repris (§ 5).

## 7. Sprint 2 — US-INS-03, mesuré le 2026-09-12

Même protocole (feuille `impression.css` injectée, `<body>` contraint à
703 px par déclaration en ligne — § 6 — colonne Actions déjà masquée par
`data-impression="masquer"`), sur les deux écrans touchés par cette story.

| Écran | Largeur du tableau | Dépassement |
|---|---|---|
| Instructeurs (liste), deux colonnes ajoutées (Disponibilité, Indispo. à venir) | 871 px | **168 px (~24 %)** |
| Indisponibilités des instructeurs (nouvel écran autonome, DECISIONS.md D-120) | 653 px | — (tient) |

**Confirme exactement la mise en garde du § 7 du Prompt 27** : « L'écran
Instructeurs débordait déjà de 33 px au 2026-09-08 : une colonne de plus
l'aggravera. » Deux colonnes ajoutées ici (pas une), dépassement porté de
33 px à 168 px. Conformément à la même consigne (« Ne corrige pas ici »),
AUCUN correctif n'est appliqué — la mesure est seulement mise à jour pour
l'arbitrage déjà ouvert au § 5 (reporté au sprint 4, avec Lieux).

Le nouvel écran autonome des indisponibilités tient sans arbitrage : cinq
colonnes de données (Instructeur, Début, Fin, Motif, État), aucune ne porte
d'intitulé aussi long que « Indisponibilités à venir » sur Lieux — même
ordre de grandeur que les écrans de liste à cinq-sept colonnes déjà mesurés
au § 6 (653 px, tient systématiquement).

## 8. Sprint 2 — US-PLAN-01, mesuré le 2026-09-13, portrait ET paysage

§ 6, Prompt 28 demande les deux orientations pour le calendrier annuel,
premier écran du projet où le paysage était pressenti comme le format
naturel. Budget portrait 703 px (§ 1) ; budget paysage recalculé sur le
même principe — A4 paysage, mêmes marges (`impression.css`, 14/12/12/16 mm),
soit 297 mm − 24 mm = 273 mm × 3,7795 px/mm ≈ **1 032 px**.

| Écran | Largeur du tableau (portrait, 703 px) | Dépassement | Paysage nécessaire ? |
|---|---|---|---|
| Calendrier — vue annuelle (douze lignes-mois, pastilles) | 653 px | — (tient) | Non |
| Calendrier — vue mensuelle (détail horaire, une ligne par jour) | 653 px | — (tient) | Non |

**Contrairement à l'attente du § 6, le paysage n'est PAS nécessaire ici** —
et c'est un choix de conception délibéré, pas une mesure de chance. Le
piège que le prompt signale explicitement (« une grille annuelle horaire...
illisible et impossible à imprimer ») a été évité en amont : la vue annuelle
n'est pas une grille de jours (sept colonnes de semaine × un nombre de
semaines), c'est un TABLEAU DE DEUX COLONNES (mois, pastilles), fluide comme
tout autre écran de liste du patron de gestion — sa largeur ne dépend que du
texte des pastilles, pas d'une géométrie de calendrier. La vue mensuelle
suit le même principe (jour, texte). Le paysage aurait été nécessaire avec
une grille à cases fixes (semaines en lignes, jours en colonnes) : ce
découpage a été écarté au § 6 précisément pour cette raison, parmi
d'autres — voir le choix de vues motivé dans le compte rendu de la story.

**Conséquence pour le lot d'impression du sprint 4** : cet écran ne
rejoint PAS la liste des écrans nécessitant l'arbitrage paysage/masquage
ouvert au § 5 — aucune action requise ici.
