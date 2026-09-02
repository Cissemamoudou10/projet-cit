# Charte graphique — Gestion des activités de formation

Référence unique pour le développement. Toute valeur absente ici doit être
arbitrée avant d'être employée.

Registre : administration militaire. Sobre, dense, hiérarchisé, imprimable.
L'interface remplace des feuilles imprimées denses — la densité est le besoin,
pas un défaut à corriger.

---

## 1. Palette

| Rôle | Valeur | Jeton Tailwind | Usage |
|---|---|---|---|
| Marine profond | `#1F3864` | `marine.900` | En-têtes de tableau, barre de navigation, titres |
| Marine clair | `#2E4F8F` | `marine.700` | Survol, liens, accents |
| Encre | `#1A1D23` | `encre` | Texte principal |
| Gris de lecture | `#4A4F58` | `gris.lecture` | Texte secondaire, libellés |
| Gris de trait | `#C9CFD8` | `gris.trait` | Bordures, filets, séparateurs |
| Fond de page | `#F7F8FA` | `fond.page` | Arrière-plan général |
| Fond de bloc | `#FFFFFF` | `fond.bloc` | Tableaux, formulaires |
| Bande alternée | `#F2F5F9` | `fond.bande` | Une ligne sur deux |
| Vert conforme | `#0F6E56` | `etat.conforme` | Conformité, validation, réalisé |
| Ambre attention | `#B07000` | `etat.attention` | Avertissement, seuil dépassé, en attente |
| Rouge écart | `#B03030` | `etat.ecart` | Erreur, rejet, non exécuté |
| Sable document | `#FBF8F1` | `sable` | Encadrés d'information, zones imprimables |

Deux teintes de service, employées uniquement en fond de survol ou de sélection :
`#EDF2FA` (survol de ligne, jeton, encadré marine) et `#E7ECF4` (en-tête de bloc
de type de formation, ligne sélectionnée).

---

## 2. Quand employer chaque couleur d'état

Une couleur d'état affirme un fait vérifiable. Elle ne décore jamais.

**Vert conforme** — le volume réalisé atteint le prescrit, la validation est
acquise, la séance est tenue. Un fait constaté, jamais une intention.
Vocabulaire : conforme, validé, achevée, réalisé.

**Ambre attention** — un seuil est dépassé sans blocage, une pièce attend une
décision. L'action reste possible, elle demande un regard.
Vocabulaire : soumis, en attente, seuil 10 % dépassé, écart non bloquant.

**Rouge écart** — le programme est rejeté, la séance n'a pas été exécutée, la
saisie est invalide. Une régularisation est due.
Vocabulaire : rejeté, non exécuté, erreur de saisie.

**Marine** — état neutre en cours, sans jugement : *en cours*, *programmé*,
liens, éléments actifs. Ce n'est pas une couleur d'état, c'est la couleur de
l'application.

**Lisibilité en noir et blanc.** Les documents s'impriment sur des imprimantes
monochromes. Toute information portée par une couleur est doublée d'un mot,
d'un symbole ou d'une trame : un badge vert porte le mot « validé », un écart
rouge porte son pourcentage signé, une barre d'avancement s'imprime en trame
grise et noire.

Les cinq badges d'état du programme se distinguent sans la couleur :

| État | Filet | Aplat | Symbole |
|---|---|---|---|
| Brouillon | pointillé | aucun | aucun |
| Soumis | plein | fond très clair | pastille pleine |
| Validé | plein | aplat plein | coche |
| Rejeté | double épaisseur | aucun | croix |
| Affiché | plein | aplat plein, souligné à l'impression | document |

---

## 3. Typographie

Deux familles, hébergées localement en `woff2`, déclarées en `@font-face`.
Aucune police distante — le poste de déploiement est isolé.

**Barlow** — titres, en-têtes de tableau, libellés de navigation, nombres mis en
avant. Graisses 400 / 500 / 600 / 700. Grotesque étroite, économe en largeur.

**IBM Plex Sans** — texte courant et données. Graisses 400 / 500 / 600. Forte
lisibilité en petit corps, chiffres tabulaires natifs.

**IBM Plex Mono** — références, codes de salle, matricules, extraits de code.
Jamais pour du texte courant.

Échelle resserrée, base à 14 px, aucun titre au-delà de 24 px.

| Corps | Interligne | Rôle |
|---|---|---|
| 24 px | 1.2 | Titre de page |
| 18 px | 1.3 | Titre de section |
| 15 px | 1.35 | Sous-titre |
| 14 px | 1.5 | Corps de base |
| 13 px | 1.45 | Donnée de tableau |
| 12 px | 1.4 | Libellé, mention |
| 11 px | 1.3 | En-tête de colonne, capitales espacées |

**Chiffres tabulaires obligatoires.** Toute colonne de volume horaire, de
fraction de progression ou de pourcentage porte
`font-variant-numeric: tabular-nums`. Unité séparée par une espace insécable.

---

## 4. Formes et espacement

**Rayon d'angle : 2 px partout.** Seule exception, les badges pleinement
arrondis. Aucune autre valeur n'est admise.

**Délimitation par filets d'un pixel**, jamais par une ombre. Une seule ombre
existe — `0 2px 6px rgba(26,29,35,.14)` — réservée à ce qui se superpose
réellement : menu déroulant, boîte de dialogue, notification.

**Espacement en multiples de 4 px** : 4 · 8 · 12 · 16 · 24 · 32 · 48.

**Hauteur de ligne** : 36 px en densité confortable, 32 px en densité compacte.
La grille de programme fait exception : la cellule porte six informations sur
deux lignes, sa hauteur suit son contenu.

**Grille de page à 12 colonnes**, gouttière 16 px, marges latérales 24 px,
contenu aligné à gauche. Aucun bloc de contenu centré.

---

## 5. Iconographie

Icônes de trait, épaisseur 1,5 px, grille de 20 px, jeu unique. SVG locaux
inline, nommés en français, sans attribut de couleur — la teinte vient de
`currentColor`. Chaque icône porte un attribut `data-lucide` avec le nom Lucide
exact, pour que la substitution par le jeu réel soit mécanique. Le tableau de
correspondance complet — nom français, nom Lucide, contexte d'usage — figure en
fin de `composants.html`.

Une icône accompagne toujours un mot ; elle ne le remplace jamais, sauf dans les
boutons d'action de ligne, où l'infobulle et l'`aria-label` portent le libellé.

---

## 6. Animations

Fonctionnelles uniquement. Chacune répond à « qu'est-ce qui vient de changer ».

| Effet | Durée |
|---|---|
| Surbrillance de ligne au survol | 120 ms |
| Transition de badge d'état | 180 ms |
| Apparition d'une notification, glissement depuis le haut | 200 ms |
| Ouverture d'un menu ou d'une boîte de dialogue | 150 ms |
| Squelette de chargement, pulsation | 1,2 s en boucle |
| Remplissage d'une barre de progression | 400 ms |
| Secousse sur champ invalide | 300 ms |
| Dépliement d'une ligne de détail | 200 ms |

Interdits : apparition au défilement, parallaxe, compteurs animés, transitions
de page, effets d'écriture.

Sous `prefers-reduced-motion: reduce`, toutes les durées passent à zéro. Aucun
état ne dépend d'une animation pour être lisible.

---

## 7. Ce qu'il ne faut pas faire

- **Dégradés** — violet, indigo, multicolore, sur fond comme sur texte. Aplats
  unis seulement.
- **Verre dépoli** — flou d'arrière-plan, cartes translucides flottantes.
- **Angles très arrondis** — au-delà de 2 px, l'interface prend un aspect jouet.
- **Ombres généralisées** — une ombre signale une superposition réelle, rien
  d'autre.
- **Grandes zones vides centrées** — pas de titre démesuré, pas d'accroche
  marketing, pas de bloc centré.
- **Émojis** — jamais en guise d'icône, ni dans les libellés.
- **Tuiles uniformes** — le padding constant partout efface la hiérarchie.
- **Inter** — choix par défaut immédiatement reconnaissable. Écarté.
- **Couleur d'état décorative** — un aplat vert signifie qu'une chose est
  conforme, pas qu'elle est jolie.

---

## 8. Contraintes techniques

**Classes utilitaires Tailwind uniquement**, écrites en toutes lettres dans le
balisage. Tailwind scanne le texte source : une classe composée dynamiquement
n'est jamais générée. Les couleurs et familles personnalisées passent par
`tailwind.config.js`.

**Aucune ressource distante.** Ni police, ni icône, ni script, ni feuille de
style chargée depuis un réseau.

**Libellés en français**, avec la terminologie du centre : brigade, séance,
référentiel, progression, créneau, matière, stagiaire, instructeur, salle
attitrée, AD/GROUPEMENT.

**Accessibilité** : contraste minimum 4,5:1 sur le texte, navigation complète au
clavier, focus visible — contour de 2 px en `marine.700`, décalé de 2 px —,
tableaux avec `scope` sur chaque en-tête, colonne triable portant `aria-sort`.

**Aucune donnée réelle.** Noms, matricules et intitulés des exemples sont
fictifs.

---

## 9. Livrables

| Fichier | Contenu |
|---|---|
| `CHARTE.md` | Ce document |
| `Charte.dc.html` | Charte visuelle : palette, typographie, formes, icônes, animations |
| `Composants.dc.html` | Tableaux, données, badges d'état, correspondance des icônes |
| `Composants-formulaires.dc.html` | Champs, sélecteurs, jetons, dépôt de fichier |
| `Composants-restitution.dc.html` | Encadrés, superpositions, restitution, actions |
| `Composants-impression.dc.html` | Document officiel et `impression.css` |
| `Grille-programme.dc.html` | Écran 1 — génération du programme hebdomadaire |
| `Ecran-2-Referentiel.dc.html` | Écran 2 — composition du référentiel |
| `Ecran-3-Validation.dc.html` | Écran 3 — validation d'un programme |
| `Ecran-4-Indisponibilite.dc.html` | Écran 4 — traitement d'une indisponibilité |
| `Ecran-5-Suivi.dc.html` | Écran 5 — suivi prescrit et réalisé |
| `Impression-Programme.dc.html` | Programme hebdomadaire, paysage |
| `Impression-Suivi.dc.html` | Rapprochement prescrit et réalisé, paysage |
