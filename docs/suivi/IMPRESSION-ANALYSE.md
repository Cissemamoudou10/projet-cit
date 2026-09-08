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

Formations est réglé par le seul masquage. Instructeurs et Lieux débordent
encore : l'arbitrage se poursuit avec le paysage pour ces deux écrans
seulement, avec une mention imprimée indiquant l'orientation attendue —
voir la suite de ce document une fois implantée.
