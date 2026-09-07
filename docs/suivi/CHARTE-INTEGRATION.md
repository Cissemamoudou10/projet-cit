# Intégration de la charte — socle technique

Suivi de l'intégration de la charte réexprimée
(`docs/charte/# Charte — gabarits Django + Tailwind.md`) : ce qui a été fait,
ce qui reste un défaut connu assumé, et un amendement daté à la charte
elle-même.

## Variables de gabarit sans source, et ce qui a été fait pour chacune

Annoncées comme « six » dans la consigne ; le détail de la même consigne en
énumère en réalité huit — décompte fait ligne à ligne, comme pour les icônes
plus bas. Aucune n'a de vue pour l'alimenter encore ; toutes les huit sont
donc gérées maintenant, pas seulement les six comptées.

| Variable | Où | Traitement | Fichier |
|---|---|---|---|
| `user.cellule` | § 2.2 | N'existe pas sur `Utilisateur` (seul `profil` existe) — remplacée par `user.get_profil_display` | `app/noyau/templates/noyau/ossature/entete.html:25` |
| `grille_active` | § 2.2 | Entité du sprint 2 — cartouche entouré de `{% if grille_active %}…{% endif %}` | `app/noyau/templates/noyau/ossature/entete.html:11-19` |
| `application.nom` | § 2.4 | Fourni par le processeur de contexte, lit `settings.APPLICATION_NOM` | `app/noyau/context_processors.py`, `app/config/settings/base.py` |
| `application.version` | § 2.4 | Idem, `settings.APPLICATION_VERSION` | idem |
| `maintenant` | § 2.4 | Idem, `timezone.now()` | idem |
| `rubriques` | § 2.3 | Liste vide par défaut, surchargeable par toute vue | `app/noyau/context_processors.py` |
| `rubrique_active` | § 2.3 | `None` par défaut | idem |
| `fil_ariane` | § 3.04 | Liste vide par défaut | idem |

Les deux premières (`user.cellule`, `grille_active`) sont des changements de
contenu dans le gabarit lui-même, pas de simples valeurs de contexte : elles
ne figuraient dans aucun document de suivi avant cette entrée — signalé par
le relecteur, corrigé ici.

`fil_ariane.html` (§ 3.04) porte en plus un `{% load static %}` absent du
texte de la charte : sans lui, le fragment utiliserait `{% static %}` sans
l'avoir chargé et lèverait une `TemplateSyntaxError` à l'exécution — un
`{% include %}` ne hérite pas des tags chargés par le gabarit qui inclut.
Ajout mécanique, pas une décision de contenu.

## Amendement daté — icônes : `stroke-*` remplacé par `text-*`

**2026-09-02.** La couleur d'une icône référencée par `<use href="...">` depuis
un fichier SVG externe (notre cas : `planche.svg`) doit passer par la
propriété CSS `color` (héritée normalement à travers la frontière du
document référencé), pas par `stroke` posé directement sur l'élément hôte —
`stroke` ne traverse pas toujours cette frontière selon le moteur de rendu.
Comme chaque `<symbol>` de `planche.svg` porte `stroke="currentColor"`,
c'est `color` qui doit porter la teinte voulue.

**Correction : `stroke-marine-900`, `stroke-gris-trait`, `stroke-blanc`,
`stroke-etat-*` deviennent `text-marine-900`, `text-gris-trait`,
`text-blanc`, `text-etat-*` sur tout `<svg>` d'icône.** Appliqué aux sept
occurrences de l'ossature (`entete.html` ×2, `fil_ariane.html` ×1,
`messages.html` ×4). Les composants du § 3 (46 composants, pas encore
transposés) devront recevoir la même correction au moment de leur
transposition — ils utilisent encore `stroke-*` dans le texte de la charte.

**Vérifié réellement**, pas supposé : page statique
(`app/noyau/static/icones/verification.html`, générée pour ce contrôle),
ouverte dans Chrome, 36 icônes × 3 teintes. Les trois colonnes changent
bien de couleur — `currentColor` traverse la référence externe dans ce
navigateur. Pas besoin du repli (planche incluse en ligne dans `base.html`).

## Amendement daté — bloc de messages (§ 2.5) : fermeture manuelle et disparition automatique

**2026-09-02.** Signalé par l'utilisateur : les messages (succès, erreur,
avertissement, information) ne se fermaient jamais — ni tout seuls après un
délai, ni au clic, faute de croix de fermeture.

**Cause.** Le texte de la charte (§ 2.5) ne montre aucune croix de
fermeture et aucun script : le composant tel que décrit est purement
statique. La feuille Tailwind porte pourtant une durée `notif` (200 ms,
`tailwind.config.js`) manifestement prévue pour ce genre d'interaction,
jamais câblée. Premier gabarit du projet à avoir besoin de JavaScript —
aucun fichier `.js` n'existait encore.

**Correction.**
- `app/noyau/templates/noyau/ossature/bouton_fermeture_message.html`
  (nouveau) : croix de fermeture (icône `rejet`, § 1.11 — « rejeter, fermer,
  retirer »), incluse dans les quatre variantes de
  `noyau/ossature/messages.html`, chacune reçoit aussi `data-message` pour
  le ciblage JS.
- `app/noyau/static/js/messages.js` (nouveau, chargé en `defer` depuis
  `base.html` et `base_public.html`) : ferme un message au clic sur sa
  croix, et automatiquement après **6 secondes** — valeur choisie faute de
  délai déjà fixé par la charte, à ajuster si le terrain la juge trop
  courte ou trop longue. Fondu de 200 ms (durée `notif`) posé en style
  JS inline, pas en classes Tailwind : ce fichier n'étant pas dans la liste
  `content` de `tailwind.config.js`, une classe qui n'existerait que dans
  une chaîne JS ne serait jamais générée par la compilation.
- Respecte `prefers-reduced-motion` sans code supplémentaire : la règle
  globale de `application.css` (`transition-duration: .001ms !important`)
  s'applique aussi aux transitions posées en style inline par JS.

**Vérifié réellement** au navigateur : déclenchement d'un message d'erreur
réel (garde-fou administrateur, écran des habilitations), clic sur la
croix — le message disparaît immédiatement ; rejoué sans clic — le message
disparaît seul après le délai, sans intervention.

## Amendement daté — squelette de base (§ 2.1) : pied de page fixé en bas d'écran

**2026-09-02.** Signalé visuellement par l'utilisateur sur toutes les pages :
le pied de page (§ 2.4) ne restait pas plaqué en bas de l'écran sur une page
dont le contenu est plus court que la fenêtre — il suivait directement le
contenu, changeant de hauteur selon l'écran affiché, au lieu de rester une
ligne d'ancrage stable.

**Cause.** Le squelette `<body>` du § 2.1 de la charte porte
`min-w-[1280px] bg-fond-page …` sans `min-h-screen`/`flex`/`flex-col`, et
`<main>` sans `flex-1` — la charte elle-même ne contient pas la disposition
« pied de page collant » (*sticky footer*) : le défaut vient du texte de
référence, pas d'un écart pris en développant.

**Correction.** `<body>` reçoit `flex min-h-screen flex-col` (en plus des
classes existantes) ; `<main>` reçoit `flex-1` (en plus des siennes). Le
pied de page occupe alors sa hauteur naturelle mais reste ancré au bas de
la fenêtre quand le contenu est court, et suit normalement le contenu
quand il dépasse la hauteur d'écran. Appliqué aux deux squelettes de base :
`app/noyau/templates/noyau/base.html` et `base_public.html` (celui-ci sans
`min-w-[1280px]`, déjà omis pour une autre raison, voir plus haut).

**Vérifié réellement** au navigateur, deux gabarits : `noyau/accueil.html`
(contenu court, deux lignes) et `administration/habilitations.html`
(contenu proche de la hauteur d'écran) — le pied de page reste au bas de
l'écran dans les deux cas. `app/administration/tests/test_gabarit_connexion.py`
(suite existante, contrôle le contenu rendu de `base_public.html`) repasse
sans modification.

## Amendement daté — badge à trois états neutres (US-INS-01, statut d'instructeur)

**2026-09-04.** La charte ne propose qu'un badge à deux états (§ 3.29, type
d'évaluation : rempli marine-900 / contour marine-700) et les seuls badges à
trois teintes ou plus (§ 2.5, bloc de messages) portent les couleurs `etat.*`
— un jugement de conformité (conforme/attention/écart) inadapté à un statut
d'emploi (militaire du centre / vacataire / civil), qui n'est pas une échelle
bon/mauvais.

**Motif retenu**, composé sur le même principe que § 3.29 plutôt qu'ajouté à
la charte comme un nouveau numéro (à faire si un second cas se présente) :

```html
<span class="bg-marine-900 px-2 py-px text-2xs font-semibold tracking-wide text-blanc">
  MILITAIRE DU CENTRE</span>
<span class="border border-marine-700 px-2 py-px text-2xs font-semibold tracking-wide
             text-marine-700">VACATAIRE</span>
<span class="border border-gris-trait px-2 py-px text-2xs font-semibold tracking-wide
             text-gris-lecture">CIVIL</span>
```

Le libellé complet en majuscules double la couleur d'un mot (§ 1.2) : les
trois états restent distinguables à l'impression monochrome. Implanté dans
`app/ressources/views/instructeur.py::_badge_statut`, vérifié par
`test_le_badge_de_statut_distingue_les_trois_valeurs_par_le_mot`.

## Défauts connus de la charte

### 1 — Interrupteur (§ 3.23) : `peer-checked:left-[18px]` ne peut pas s'appliquer

```html
<input type="checkbox" name="comptee" class="peer sr-only" ...>
<span class="relative ... peer-checked:border-etat-conforme ...">
  <span class="absolute left-0.5 top-0.5 ... peer-checked:left-[18px]"></span>
</span>
```

`peer-*` exige que la cible soit un **frère** de l'élément `.peer` dans le DOM.
Le `<span class="absolute ... peer-checked:left-[18px]">` est un enfant du
premier `<span>`, pas un frère de l'`<input>` : le curseur de l'interrupteur ne
se déplacera jamais au changement d'état, quel que soit le navigateur.

**Non corrigé** — hors périmètre du socle. À traiter par la première story qui
emploie un interrupteur (probablement `programme_hebdomadaire`, case « séance
comptée »).

### 2 — `impression.css` (§ 4) : résolu, scindé en deux fichiers

**a. `details > summary { display: none }` corrigé.** Cette règle visait à
masquer le menu d'actions (§ 3.41) à l'impression, mais masquait aussi le
libellé de matière d'une ligne dépliable (§ 3.15), qui doit rester visible.
Retirée du sélecteur générique ; tout ce qui doit disparaître à l'impression
porte désormais explicitement `data-impression="masquer"` (mécanisme déjà
prévu par la feuille). **À faire par la première story qui transpose § 3.41
en gabarit Django** : poser `data-impression="masquer"` sur son conteneur
`<details>` — sans quoi le menu d'actions s'imprimera.

**b. Constructions propres à WeasyPrint isolées dans un second fichier, non
chargé par le navigateur.** `@page paysage`, `position: running()`, les
boîtes de marge `@top-left`/`@bottom-left`/`@bottom-right` : aucun moteur de
rendu de navigateur ne les interprète, seuls des moteurs de mise en page
paginée comme WeasyPrint le font.

| Fichier | Chargé par | Contenu |
|---|---|---|
| `app/noyau/static/css/impression.css` | `base.html`, `<link media="print">` | Sous-ensemble navigateur du § 4 — géométrie de page simple, tableaux, ruptures, badges, barres, animations coupées |
| `app/noyau/static/css/document_pdf.css` | Personne pour l'instant — `ServiceDocument` le chargera au sprint 4 | Les trois constructions WeasyPrint retirées du premier |

## Polices — `app/noyau/static/polices/`

Fait. Neuf fichiers `.woff2` copiés depuis `@fontsource/barlow`,
`@fontsource/ibm-plex-sans`, `@fontsource/ibm-plex-mono` (sous-ensemble
latin, style normal), plus les trois licences (`LICENCE-barlow.txt`,
`LICENCE-ibm-plex-sans.txt`, `LICENCE-ibm-plex-mono.txt`). Copie faite par
`scripts/copier-polices.mjs` (`npm run polices:copier`), rejouable à chaque
mise à jour de version — pas une suite de commandes ponctuelles.

## Icônes — `app/noyau/static/icones/planche.svg`

Fait. 36 `<symbol>` construits par `scripts/construire-planche-icones.mjs`
(`npm run icones:construire`) depuis `lucide-static`, rejouable à chaque mise
à jour de version. Les 36 identifiants — y compris les 8 marqués `?` — se
sont tous résolus dans la version installée (`lucide-static@1.39.0`) :
aucun manquant à signaler.

**Écart avec la charte à signaler avant de trancher les noms.** Le texte de
la charte (§ 1.11) annonce « la correspondance des 34 identifiants » et « les
lignes marquées `?` », en indiquant que 4 sont concernées. Le tableau qui suit
en compte réellement **36**, dont **8** marquées `?` — pas 4. Compte vérifié
ligne à ligne sur le fichier déposé. Les deux chiffres annoncés dans le texte
d'intro ne correspondent pas au tableau qui les suit.

Les 36 identifiants, tels que le tableau les donne, nom Lucide en second :

| Identifiant | Lucide |
|---|---|
| `calendrier` | `calendar-days` |
| `horloge` | `clock` |
| `grille-horaire` **?** | `grid-3x3` |
| `salle` **?** | `door-closed` |
| `groupe` | `users` |
| `instructeur` **?** | `presentation` |
| `stagiaire` | `graduation-cap` |
| `matiere` | `book-open` |
| `seance` **?** | `calendar-clock` |
| `document` | `file-text` |
| `proces-verbal` | `file-signature` |
| `signature` | `signature` |
| `validation` | `check` |
| `rejet` | `x` |
| `avertissement` | `triangle-alert` |
| `information` | `info` |
| `recherche` | `search` |
| `filtre` | `filter` |
| `tri` | `arrow-up-down` |
| `tri-croissant` | `arrow-up` |
| `tri-decroissant` | `arrow-down` |
| `export` **?** | `download` |
| `impression` | `printer` |
| `ajout` | `plus` |
| `modification` | `pencil` |
| `suppression` | `trash-2` |
| `verrou` | `lock` |
| `historique` | `history` |
| `alerte` | `bell` |
| `statistique` **?** | `bar-chart-3` (`chart-column` en version récente de Lucide) |
| `fleche-suite` | `arrow-right` |
| `chevron-bas` | `chevron-down` |
| `chevron-droite` | `chevron-right` |
| `actions` **?** | `ellipsis-vertical` (`more-vertical` en ancienne version de Lucide) |
| `document-valide` | `file-check` |
| `avenant` **?** | `file-clock` |

Les 8 marquées **?** (`grille-horaire`, `salle`, `instructeur`, `seance`,
`export`, `statistique`, `actions`, `avenant`) portent un nom proposé par la
charte, pas encore tranché.

Chaque identifiant est un `id="…"` sur un `<symbol>` de la planche unique
`planche.svg`, appelé par `<use href="{% static 'icones/planche.svg' %}#identifiant">`
(§ 1.11). `stroke-width` réécrit à `1,5` (la charte) au moment de la
construction — `lucide-static` livre du 2 px par défaut.

## Commande de compilation du CSS

**Exécutée.** `npm install` (74 paquets), puis `npm run css:build` :
`app/noyau/static/css/application.css` fait **9 591 octets** (minifié),
**77 sélecteurs de classe distincts**. `package.json` (racine) épingle
`tailwindcss` en `3.4.14` (3.4.x, correction 3). `tailwind.config.js`
(racine) porte la configuration corrigée (`content`, `minWidth`,
`minHeight`).

```
npm install
npm run css:build
```

équivaut à :

```
npx tailwindcss -c tailwind.config.js \
  -i app/noyau/static_src/application.css \
  -o app/noyau/static/css/application.css \
  --minify
```

Source : `app/noyau/static_src/application.css` (directives `@tailwind` +
réduction de mouvement, § 4.1, installée verbatim). Sortie versionnée :
`app/noyau/static/css/application.css` — c'est ce fichier, pas la source, que
`base.html` référence et que le dépôt doit conserver à jour après toute
modification des gabarits ou de `tailwind.config.js`. `npm run css:watch`
recompile en continu pendant le développement.

## Amendement daté — § 3.10, pagination : fenêtre bornée à cinq numéros

**2026-09-07, Prompt 17.** Le texte de la charte (§ 3.10) boucle sur
`page.paginator.page_range` en entier — correct pour une poignée de pages,
inutilisable au-delà (le journal en compte déjà vingt-trois, une barre sur
plusieurs lignes). Un premier correctif avait repris ce défaut au seul
gabarit générique du patron `ServiceGestion`, sans toucher les écrans
d'administration (comptes, journal) écrits avant ce patron et portant leur
propre copie du même balisage — jamais atteints, voir P-32,
`docs/suivi/PROBLEMES.md`.

**Correction : le fragment n'est plus inclus (`{% include %}`), il est
généré par une balise d'inclusion, `{% load pagination %}{% pagination page
%}`** (`app/noyau/templatetags/pagination.py`), seul point du système qui
calcule la fenêtre (page courante, deux avant, deux après, décalée aux
extrémités pour toujours en montrer cinq ; première et dernière page
ajoutées séparément, avec un repère d'omission — `<span aria-hidden="true">`,
jamais un lien — seulement quand un écart réel les sépare de la fenêtre).
Chaque lien de page porte un `aria-label="Page N"` distinct du texte visible,
pour un lecteur d'écran. `app/noyau/templates/noyau/gestion/_pagination.html`
reste le seul gabarit de rendu, mais n'est plus jamais inclus directement.

**Écrans mis à jour** : les cinq déjà sur le patron (types de formation,
formations, matières, instructeurs, lieux) et les qualifications par
instructeur l'utilisaient déjà via `noyau/gestion/liste.html` — migrés vers
la balise sans changement de comportement pour eux. `liste_comptes.html` et
`journal.html` (administration, antérieurs au patron) portaient chacun leur
propre copie du balisage fautif — remplacée par la même balise. Vérifié par
un test qui compare le balisage produit sur les trois familles d'écrans
(`referentiel/tests/test_pagination_ecran.py`).

**Écran non concerné, contrairement à ce qu'annonçait le prompt** :
*habilitations* n'est jamais paginé (`ServiceMatriceHabilitations` n'appelle
pas `paginer()` — matrice fixe de 5 groupes × 18 permissions, voir P-16).
Rien à corriger là.

Le texte de la charte devra être repris pour refléter ce nouveau patron —
non fait ici : cette entrée en tient lieu jusqu'à la prochaine reprise du
document source.
