---
paths:
  - "**/templates/**"
  - "**.html"
  - "**/static/**"
  - "**/tailwind.config.js"
---

# Gabarits et interface

## Le livre de composants fait référence

`docs/charte/# Charte — gabarits Django + Tailwind.md` présente les 46
composants avec leur balisage exact. **Ne réinvente jamais un composant qui
s'y trouve** : reprends ses classes Tailwind à l'identique. Un tableau dense
écrit deux fois de deux façons différentes est un défaut, pas une variation.

Si un composant manque, dis-le avant d'improviser : il vaut mieux l'ajouter à la
charte que le laisser diverger.

Les défauts connus de la charte et les amendements datés (icônes, impression)
sont consignés dans `docs/suivi/CHARTE-INTEGRATION.md` — à lire avant de
reprendre un composant qui y est mentionné.

## Contraintes non négociables

**Classes utilitaires Tailwind uniquement.** Le CSS est précompilé sur le poste
de développement, Node étant absent du poste cible. Toute règle CSS écrite hors
de `tailwind.config.js` ne sera pas générée et disparaîtra au déploiement.

**Aucune ressource distante.** Ni police, ni icône, ni script, ni feuille de style
appelée par une adresse réseau (BNF-06). Les polices sont des fichiers locaux,
les icônes des SVG intégrés. Un test d'architecture le vérifie.

**Terminologie du CIT** (BNF-08) : brigade, séance, référentiel, progression,
créneau, matière, salle attitrée, AD/GROUPEMENT. Jamais de traduction, jamais
d'anglicisme.

## Densité

L'interface remplace des feuilles imprimées denses — quinze groupes sur quatre
créneaux, six informations par case. Ne cherche pas à aérer : les lignes de
tableau sont compactes, le corps de texte est petit, l'information prime sur le
confort visuel.

## Écriture des gabarits

Héritage par blocs depuis un gabarit de base. Les composants réutilisables sont
des inclusions ou des balises personnalisées, jamais du balisage recopié.

Aucune logique métier dans un gabarit : pas de calcul, pas de règle. Le contexte
arrive prêt à afficher depuis la vue, qui l'a obtenu d'un service.

## Recompilation obligatoire

**Tout ajout ou toute modification de gabarit impose de relancer
`npm run css:build`.** Tailwind analyse le texte source : une classe qui
n'apparaît dans aucun fichier scanné au moment de la compilation n'est jamais
générée. Une classe absente du CSS compilé ne rend rien — **sans erreur, sans
message** — et c'est indiscernable d'une faute de frappe à l'œil nu. Recompile
avant toute relecture ou tout test d'interface, jamais après.

## Impression

La progression d'instruction est **imprimée en paysage** et signée à la main. Les
gabarits imprimables portent l'en-tête officiel et le pied de signature définis
dans la charte, et masquent navigation et actions.

## Messages

Un message d'erreur indique l'action corrective attendue, pas seulement le refus.
Les couleurs d'état ne sont jamais décoratives : le vert dit conforme, l'ambre
dit attention, le rouge dit écart.

## Animations

Fonctionnelles uniquement, durées définies par la charte. Aucune apparition au
défilement, aucune transition de page. `prefers-reduced-motion` désactive tout.
