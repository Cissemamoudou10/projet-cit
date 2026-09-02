# Charte — gabarits Django + Tailwind

Référence en texte brut. Aucun style en ligne, aucun nom de classe personnalisé,
aucun `@apply`, aucune balise `script`, aucune ressource distante.

Tailwind CSS v3, compilé localement. Les classes sont écrites en toutes lettres
dans les gabarits : Tailwind analyse le texte source et ne génère que ce qu'il y
trouve littéralement. Aucune classe ne doit être composée par concaténation dans
une vue, un filtre ou une balise de gabarit.

## Trois décisions signalées

**1 — La palette passe par la configuration.** Les douze couleurs de la charte
n'existent pas dans la palette Tailwind de base. Elles sont déclarées dans
`tailwind.config.js` (§ 1.8) et deviennent des utilitaires standards :
`bg-marine-900`, `text-etat-ecart`, `border-gris-trait`. Ce ne sont ni des
classes personnalisées ni du `@apply` — c'est le mécanisme prévu par Tailwind.
Sans cela, il faudrait écrire `bg-[#1F3864]` à chaque occurrence.

**2 — Les valeurs arbitraires entre crochets sont limitées à quatre cas**,
chacun signalé sur place par un commentaire `<!-- arbitraire -->` :

| Valeur | Où | Pourquoi |
|---|---|---|
| `shadow-[0_2px_6px_rgba(26,29,35,.14)]` | menu, dialogue, notification | Déclarée en jeton `shadow-superpose` (§ 1.8) — la forme brute n'apparaît nulle part |
| `shadow-[inset_0_-3px_0_currentColor]` | onglet actif, badge affiché à l'impression | Soulignement intérieur, sans équivalent utilitaire |
| `w-[94px]` | colonne de groupe de la grille de programme | Largeur fixe imposée par la tenue en largeur |
| `min-h-[26px]` | sélecteur en ligne de tableau | Hauteur de contrôle inférieure au pas de l'échelle |

**3 — Les largeurs variables évitent le style en ligne.** Une barre
d'avancement demanderait `style="width: 54%"`. À la place, la vue arrondit le
pourcentage au douzième le plus proche et le gabarit choisit parmi les fractions
de Tailwind (`w-1/12` … `w-full`). Précision de 8,3 points, suffisante pour une
barre de 200 px de large ; la valeur exacte reste affichée en chiffres à côté.

---

# 1 — Jetons de conception

## 1.1 Couleurs

| Rôle | Hexadécimal | Jeton | Utilitaires |
|---|---|---|---|
| Fond de page | `#F7F8FA` | `fond.page` | `bg-fond-page` |
| Surface de bloc | `#FFFFFF` | `fond.bloc` | `bg-fond-bloc` |
| Surface alternée | `#F2F5F9` | `fond.bande` | `bg-fond-bande` |
| Surface de survol | `#EDF2FA` | `fond.survol` | `hover:bg-fond-survol` |
| Surface de sélection | `#E7ECF4` | `fond.selection` | `bg-fond-selection` |
| Texte principal | `#1A1D23` | `encre` | `text-encre` |
| Texte secondaire | `#4A4F58` | `gris.lecture` | `text-gris-lecture` |
| Texte désactivé | `#A6ACB6` | `gris.eteint` | `text-gris-eteint` |
| Bordure | `#C9CFD8` | `gris.trait` | `border-gris-trait` |
| Bordure désactivée | `#E2E7EE` | `gris.inerte` | `border-gris-inerte` |
| Accent principal | `#1F3864` | `marine.900` | `bg-marine-900` `text-marine-900` |
| Accent clair | `#2E4F8F` | `marine.700` | `hover:bg-marine-700` `text-marine-700` |
| Accent sombre | `#18305A` | `marine.950` | `bg-marine-950` |
| Succès | `#0F6E56` | `etat.conforme` | `text-etat-conforme` `bg-etat-conforme` |
| Succès — fond | `#EEF7F3` | `etat.conforme-fond` | `bg-etat-conforme-fond` |
| Alerte | `#B07000` | `etat.attention` | `text-etat-attention` |
| Alerte — fond | `#FDF6E7` | `etat.attention-fond` | `bg-etat-attention-fond` |
| Erreur | `#B03030` | `etat.ecart` | `text-etat-ecart` |
| Erreur — fond | `#FCF0F0` | `etat.ecart-fond` | `bg-etat-ecart-fond` |
| Erreur — survol | `#9A2A2A` | `etat.ecart-fonce` | `hover:bg-etat-ecart-fonce` |
| Document | `#FBF8F1` | `sable` | `bg-sable` |
| Anneau de focus | `#C7D5EC` | `focus` | `focus:ring-focus` |
| Anneau de focus, erreur | `#EBC0C0` | `focus.ecart` | `focus:ring-focus-ecart` |

Aucune autre couleur n'est admise. Le noir pur `#000000` est réservé aux
documents imprimés (§ 4).

## 1.2 Emploi des couleurs d'état

| Couleur | Sens | Vocabulaire |
|---|---|---|
| `etat.conforme` | Fait constaté et atteint | conforme, validé, achevée, réalisé |
| `etat.attention` | Seuil franchi sans blocage, décision en attente | soumis, en attente, seuil 10 % dépassé |
| `etat.ecart` | Régularisation due | rejeté, non exécuté, erreur de saisie |
| `marine.700` | État neutre en cours, sans jugement | en cours, programmé, lien actif |

Toute information portée par une couleur est doublée d'un mot, d'un symbole ou
d'une trame — les documents s'impriment en monochrome.

## 1.3 Typographie

| Rôle | Famille | Pile de repli | Utilitaire |
|---|---|---|---|
| Titres, en-têtes de tableau | Barlow | `ui-sans-serif, system-ui, "Segoe UI", Roboto, sans-serif` | `font-titre` |
| Texte courant, données | IBM Plex Sans | `ui-sans-serif, system-ui, "Segoe UI", Roboto, sans-serif` | `font-corps` |
| Références, codes, matricules | IBM Plex Mono | `ui-monospace, "Cascadia Mono", Consolas, monospace` | `font-mono` |

Graisses employées : 400, 500, 600, 700 pour Barlow ; 400, 500, 600 pour IBM
Plex Sans ; 400, 500 pour IBM Plex Mono.

## 1.4 Échelle de tailles

| Utilitaire | Taille | Interligne | Rôle |
|---|---|---|---|
| `text-xl` | 24 px | 1.2 | Titre de page |
| `text-lg` | 18 px | 1.3 | Titre de section |
| `text-md` | 15 px | 1.35 | Sous-titre |
| `text-base` | 14 px | 1.5 | Corps de base |
| `text-sm` | 13 px | 1.45 | Donnée de tableau |
| `text-xs` | 12 px | 1.4 | Libellé, mention |
| `text-2xs` | 11 px | 1.3 | En-tête de colonne en capitales |

Aucun titre au-delà de 24 px. Toute colonne de volume, de fraction ou de
pourcentage porte `tabular-nums`.

## 1.5 Échelle d'espacement

| Utilitaire | Valeur |
|---|---|
| `p-1` `gap-1` `m-1` | 4 px |
| `p-2` `gap-2` `m-2` | 8 px |
| `p-3` `gap-3` `m-3` | 12 px |
| `p-4` `gap-4` `m-4` | 16 px |
| `p-6` `gap-6` `m-6` | 24 px |
| `p-8` `gap-8` `m-8` | 32 px |
| `p-12` `gap-12` `m-12` | 48 px |
| `h-ligne` | 32 px — hauteur de ligne compacte |
| `h-ligne-large` | 36 px — hauteur de ligne confortable |
| `h-controle` | 32 px — hauteur de champ et de bouton |

Les groupes de frères — boutons, jetons, icônes, éléments de navigation — se
disposent en `flex` ou `grid` avec `gap-*`, jamais par marges individuelles.

## 1.6 Rayons et bordures

| Utilitaire | Valeur | Emploi |
|---|---|---|
| `rounded-none` | 0 | Tableaux, cellules |
| `rounded` | 2 px | Blocs, champs, boutons — valeur par défaut |
| `rounded-pilule` | 9999 px | Badges d'état uniquement |
| `border` | 1 px | Toute délimitation |
| `border-2` | 2 px | Badge rejeté, soulignement d'onglet actif |
| `border-dashed` | — | Badge brouillon, case non affectée, zone de dépôt |

## 1.7 Ombres

| Utilitaire | Valeur | Emploi |
|---|---|---|
| `shadow-none` | — | Par défaut sur tout élément |
| `shadow-superpose` | `0 2px 6px rgba(26,29,35,.14)` | Menu déroulant, boîte de dialogue, notification — rien d'autre |

Une ombre signale une superposition réelle. Un bloc posé dans le flux n'en porte
jamais.

## 1.8 Configuration

`tailwind.config.js`

```js
module.exports = {
  content: [
    './gabarits/**/*.html',
    './**/templates/**/*.html',
  ],
  theme: {
    colors: {
      marine: { 950: '#18305A', 900: '#1F3864', 700: '#2E4F8F' },
      encre: '#1A1D23',
      gris: { lecture: '#4A4F58', trait: '#C9CFD8', eteint: '#A6ACB6', inerte: '#E2E7EE' },
      fond: {
        page: '#F7F8FA', bloc: '#FFFFFF', bande: '#F2F5F9',
        survol: '#EDF2FA', selection: '#E7ECF4',
      },
      etat: {
        conforme: '#0F6E56', 'conforme-fond': '#EEF7F3',
        attention: '#B07000', 'attention-fond': '#FDF6E7',
        ecart: '#B03030', 'ecart-fond': '#FCF0F0', 'ecart-fonce': '#9A2A2A',
      },
      sable: '#FBF8F1',
      focus: { DEFAULT: '#C7D5EC', ecart: '#EBC0C0' },
      blanc: '#FFFFFF',
      noir: '#000000',
      transparent: 'transparent',
      current: 'currentColor',
    },
    fontFamily: {
      titre: ['Barlow', 'ui-sans-serif', 'system-ui', 'Segoe UI', 'Roboto', 'sans-serif'],
      corps: ['IBM Plex Sans', 'ui-sans-serif', 'system-ui', 'Segoe UI', 'Roboto', 'sans-serif'],
      mono: ['IBM Plex Mono', 'ui-monospace', 'Cascadia Mono', 'Consolas', 'monospace'],
    },
    fontSize: {
      '2xs': ['11px', '1.3'],
      xs: ['12px', '1.4'],
      sm: ['13px', '1.45'],
      base: ['14px', '1.5'],
      md: ['15px', '1.35'],
      lg: ['18px', '1.3'],
      xl: ['24px', '1.2'],
    },
    borderRadius: { none: '0', DEFAULT: '2px', pilule: '9999px' },
    boxShadow: {
      none: 'none',
      superpose: '0 2px 6px rgba(26,29,35,.14)',
    },
    extend: {
      spacing: {
        1: '4px', 2: '8px', 3: '12px', 4: '16px', 6: '24px', 8: '32px', 12: '48px',
        ligne: '32px', 'ligne-large': '36px', controle: '32px',
      },
      maxWidth: { utile: '1180px', large: '1240px' },
      transitionDuration: {
        survol: '120ms', menu: '150ms', badge: '180ms',
        notif: '200ms', secousse: '300ms', barre: '400ms',
      },
      keyframes: {
        secousse: {
          '0%,100%': { transform: 'translateX(0)' },
          '25%': { transform: 'translateX(-3px)' },
          '75%': { transform: 'translateX(3px)' },
        },
        squelette: { '0%,100%': { opacity: '.5' }, '50%': { opacity: '1' } },
        glisser: {
          from: { transform: 'translateY(-12px)', opacity: '0' },
          to: { transform: 'translateY(0)', opacity: '1' },
        },
        ouvrir: {
          from: { transform: 'scale(.98)', opacity: '0' },
          to: { transform: 'scale(1)', opacity: '1' },
        },
      },
      animation: {
        secousse: 'secousse 300ms ease-in-out',
        squelette: 'squelette 1.2s ease-in-out infinite',
        glisser: 'glisser 200ms ease-out',
        ouvrir: 'ouvrir 150ms ease-out',
      },
    },
  },
  plugins: [],
}
```

## 1.9 Polices locales

Fichiers `woff2` dans `static/polices/`. Aucun appel distant.

`static/css/polices.css`

```css
@font-face {
  font-family: 'Barlow';
  src: url('../polices/barlow-400.woff2') format('woff2');
  font-weight: 400; font-style: normal; font-display: swap;
}
@font-face {
  font-family: 'Barlow';
  src: url('../polices/barlow-500.woff2') format('woff2');
  font-weight: 500; font-style: normal; font-display: swap;
}
@font-face {
  font-family: 'Barlow';
  src: url('../polices/barlow-600.woff2') format('woff2');
  font-weight: 600; font-style: normal; font-display: swap;
}
@font-face {
  font-family: 'Barlow';
  src: url('../polices/barlow-700.woff2') format('woff2');
  font-weight: 700; font-style: normal; font-display: swap;
}
@font-face {
  font-family: 'IBM Plex Sans';
  src: url('../polices/plex-sans-400.woff2') format('woff2');
  font-weight: 400; font-style: normal; font-display: swap;
}
@font-face {
  font-family: 'IBM Plex Sans';
  src: url('../polices/plex-sans-500.woff2') format('woff2');
  font-weight: 500; font-style: normal; font-display: swap;
}
@font-face {
  font-family: 'IBM Plex Sans';
  src: url('../polices/plex-sans-600.woff2') format('woff2');
  font-weight: 600; font-style: normal; font-display: swap;
}
@font-face {
  font-family: 'IBM Plex Mono';
  src: url('../polices/plex-mono-400.woff2') format('woff2');
  font-weight: 400; font-style: normal; font-display: swap;
}
@font-face {
  font-family: 'IBM Plex Mono';
  src: url('../polices/plex-mono-500.woff2') format('woff2');
  font-weight: 500; font-style: normal; font-display: swap;
}
```

## 1.10 Animations

| Effet | Durée | Utilitaire |
|---|---|---|
| Survol de ligne | 120 ms | `transition-colors duration-survol` |
| Ouverture de menu ou de dialogue | 150 ms | `animate-ouvrir` |
| Transition de badge d'état | 180 ms | `transition-colors duration-badge` |
| Notification, glissement | 200 ms | `animate-glisser` |
| Champ invalide, secousse | 300 ms | `animate-secousse` |
| Barre d'avancement | 400 ms | `transition-[width] duration-barre` |
| Squelette de chargement | 1,2 s en boucle | `animate-squelette` |

Sous `prefers-reduced-motion: reduce`, toutes les durées passent à zéro (§ 4.1).
Aucun état ne dépend d'une animation pour être lisible.

## 1.11 Iconographie

Icônes Lucide, trait de 1,5 px, grille de 20 px, servies localement en planche
SVG unique `static/icones/planche.svg` et appelées par `<use>`. Aucun script,
aucun CDN. La teinte vient de `currentColor` — l'icône n'a pas d'attribut de
couleur.

```html
<svg class="h-4 w-4 stroke-marine-900" aria-hidden="true">
  <use href="{% static 'icones/planche.svg' %}#validation"></use>
</svg>
```

Correspondance des 34 identifiants — nom français employé dans le gabarit, nom
Lucide de la source. Les lignes marquées `?` portent un nom proposé, à trancher.

| Identifiant | Lucide | Contexte |
|---|---|---|
| `calendrier` | `calendar-days` | Date, plage, en-tête de semaine |
| `horloge` | `clock` | Créneau, heure, durée |
| `grille-horaire` `?` | `grid-3x3` | Grille horaire active |
| `salle` `?` | `door-closed` | Code de salle, lieu |
| `groupe` | `users` | Brigade, effectif |
| `instructeur` `?` | `presentation` | Instructeur affecté |
| `stagiaire` | `graduation-cap` | Stagiaire, fiche individuelle |
| `matiere` | `book-open` | Matière, catalogue |
| `seance` `?` | `calendar-clock` | Séance unitaire |
| `document` | `file-text` | Programme édité, pièce jointe |
| `proces-verbal` | `file-signature` | Procès-verbal d'évaluation |
| `signature` | `signature` | Circuit de signature |
| `validation` | `check` | Valider, conformité |
| `rejet` | `x` | Rejeter, fermer, retirer |
| `avertissement` | `triangle-alert` | Seuil dépassé, créneau non pourvu |
| `information` | `info` | Encadré, règle rappelée |
| `recherche` | `search` | Champ de recherche |
| `filtre` | `filter` | Barre de filtres |
| `tri` | `arrow-up-down` | En-tête triable |
| `tri-croissant` | `arrow-up` | Colonne triée en ordre croissant |
| `tri-decroissant` | `arrow-down` | Colonne triée en ordre décroissant |
| `export` `?` | `download` | Export CSV |
| `impression` | `printer` | Édition du document |
| `ajout` | `plus` | Créer, rattacher |
| `modification` | `pencil` | Éditer une ligne |
| `suppression` | `trash-2` | Retirer, supprimer |
| `verrou` | `lock` | Programme ou séance verrouillé |
| `historique` | `history` | Historique, avenants |
| `alerte` | `bell` | Notification |
| `statistique` `?` | `bar-chart-3` | Bloc de statistique — `chart-column` en version récente |
| `fleche-suite` | `arrow-right` | Enchaînement, lien vers le détail |
| `chevron-bas` | `chevron-down` | Liste déroulante, dépliement |
| `chevron-droite` | `chevron-right` | Fil d'Ariane |
| `actions` `?` | `ellipsis-vertical` | Menu d'actions — `more-vertical` en ancienne version |
| `document-valide` | `file-check` | Programme affiché |
| `avenant` `?` | `file-clock` | Avenant daté |

---

# 2 — Ossature

## 2.1 Conteneur de page

`gabarits/base.html`

```html
{% load static %}
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block titre %}Gestion des activités de formation{% endblock %}</title>
  <link rel="stylesheet" href="{% static 'css/polices.css' %}">
  <link rel="stylesheet" href="{% static 'css/application.css' %}">
  <link rel="stylesheet" href="{% static 'css/impression.css' %}" media="print">
</head>
<body class="min-w-[1280px] bg-fond-page font-corps text-base text-encre antialiased">
  <!-- arbitraire : min-w-[1280px], largeur minimale imposée par la grille de programme -->
  {% include "ossature/entete.html" %}
  {% include "ossature/fil_ariane.html" %}
  {% block entete_page %}{% endblock %}
  <main class="px-6 pb-12 pt-4">
    {% include "ossature/messages.html" %}
    {% block contenu %}{% endblock %}
  </main>
  {% include "ossature/pied.html" %}
</body>
</html>
```

## 2.2 En-tête

`gabarits/ossature/entete.html`

```html
{% load static %}
<header class="bg-marine-900 text-blanc">
  <div class="flex h-12 items-center justify-between px-6">
    <div class="flex items-center gap-6">
      <span class="font-titre text-md font-bold tracking-wide">
        CENTRE D'INSTRUCTION — GESTION DES ACTIVITÉS
      </span>
      {% include "ossature/navigation.html" %}
    </div>
    <div class="flex items-center gap-4 text-xs">
      <span class="flex items-center gap-2 border border-marine-700 bg-marine-950 px-3 py-1">
        <svg class="h-4 w-4 stroke-gris-trait" aria-hidden="true">
          <use href="{% static 'icones/planche.svg' %}#grille-horaire"></use>
        </svg>
        <span class="text-gris-trait">Grille active</span>
        <span class="font-semibold">{{ grille_active.libelle }}</span>
      </span>
      <span class="flex items-center gap-2">
        <svg class="h-4 w-4 stroke-gris-trait" aria-hidden="true">
          <use href="{% static 'icones/planche.svg' %}#groupe"></use>
        </svg>
        <span>{{ user.grade }} {{ user.last_name|upper }}</span>
        <span class="text-gris-trait">— {{ user.cellule }}</span>
      </span>
    </div>
  </div>
</header>
<div class="h-[3px] bg-marine-700"></div>
<!-- arbitraire : h-[3px], filet d'accent inférieur au pas de l'échelle -->
```

## 2.3 Navigation principale

`gabarits/ossature/navigation.html`

L'état actif se choisit par un `{% if %}` sur deux jeux de classes complets —
jamais par concaténation, que Tailwind ne saurait pas analyser.

```html
<nav class="flex gap-px font-titre text-sm font-medium" aria-label="Navigation principale">
  {% for rubrique in rubriques %}
    {% if rubrique.slug == rubrique_active %}
      <a href="{{ rubrique.url }}" aria-current="page"
         class="bg-blanc px-3 py-1.5 font-semibold text-marine-900">{{ rubrique.libelle }}</a>
    {% else %}
      <a href="{{ rubrique.url }}"
         class="px-3 py-1.5 text-gris-trait transition-colors duration-survol
                hover:bg-marine-700 hover:text-blanc
                focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2
                focus-visible:outline-blanc">{{ rubrique.libelle }}</a>
    {% endif %}
  {% endfor %}
</nav>
```

## 2.4 Pied de page

`gabarits/ossature/pied.html`

```html
<footer class="border-t border-gris-trait bg-fond-bloc">
  <div class="flex items-center justify-between px-6 py-3 font-mono text-xs text-gris-lecture">
    <span>{{ application.nom }} — version {{ application.version }}</span>
    <span class="tabular-nums">Réseau interne — poste isolé — {{ maintenant|date:"d/m/Y H:i" }}</span>
  </div>
</footer>
```

## 2.5 Bloc de messages

`gabarits/ossature/messages.html`

Le cadre de messages de Django expose `message.tags` : `success`, `warning`,
`error`, `info`. Chaque branche porte son jeu de classes en toutes lettres.

```html
{% load static %}
{% if messages %}
  <div class="mb-4 grid gap-3" role="status" aria-live="polite">
    {% for message in messages %}
      {% if message.tags == "success" %}
        <div class="flex items-start gap-3 border border-l-[3px] border-gris-trait
                    border-l-etat-conforme bg-etat-conforme-fond px-4 py-3">
          <!-- arbitraire : border-l-[3px], filet d'accent latéral -->
          <svg class="mt-px h-4 w-4 shrink-0 stroke-etat-conforme" aria-hidden="true">
            <use href="{% static 'icones/planche.svg' %}#validation"></use>
          </svg>
          <div>
            <p class="font-titre text-base font-semibold text-etat-conforme">Succès</p>
            <p class="text-xs text-gris-lecture">{{ message }}</p>
          </div>
        </div>
      {% elif message.tags == "warning" %}
        <div class="flex items-start gap-3 border border-l-[3px] border-gris-trait
                    border-l-etat-attention bg-etat-attention-fond px-4 py-3">
          <svg class="mt-px h-4 w-4 shrink-0 stroke-etat-attention" aria-hidden="true">
            <use href="{% static 'icones/planche.svg' %}#avertissement"></use>
          </svg>
          <div>
            <p class="font-titre text-base font-semibold text-etat-attention">Avertissement</p>
            <p class="text-xs text-gris-lecture">{{ message }}</p>
          </div>
        </div>
      {% elif message.tags == "error" %}
        <div class="flex items-start gap-3 border border-l-[3px] border-gris-trait
                    border-l-etat-ecart bg-etat-ecart-fond px-4 py-3">
          <svg class="mt-px h-4 w-4 shrink-0 stroke-etat-ecart" aria-hidden="true">
            <use href="{% static 'icones/planche.svg' %}#rejet"></use>
          </svg>
          <div>
            <p class="font-titre text-base font-semibold text-etat-ecart">Erreur</p>
            <p class="text-xs text-gris-lecture">{{ message }}</p>
          </div>
        </div>
      {% else %}
        <div class="flex items-start gap-3 border border-l-[3px] border-gris-trait
                    border-l-marine-900 bg-sable px-4 py-3">
          <svg class="mt-px h-4 w-4 shrink-0 stroke-marine-900" aria-hidden="true">
            <use href="{% static 'icones/planche.svg' %}#information"></use>
          </svg>
          <div>
            <p class="font-titre text-base font-semibold text-marine-900">Information</p>
            <p class="text-xs text-gris-lecture">{{ message }}</p>
          </div>
        </div>
      {% endif %}
    {% endfor %}
  </div>
{% endif %}
```

---

# 3 — Les 46 composants

## Famille A — Navigation et structure (01 → 07)

| N° | Composant | Section |
|---|---|---|
| 01 | Conteneur de page | § 2.1 |
| 02 | En-tête | § 2.2 |
| 03 | Navigation principale | § 2.3 |
| 04 | Fil d'Ariane | § 3.04 |
| 05 | En-tête de page | § 3.05 |
| 06 | Pied de page | § 2.4 |
| 07 | Bloc de messages | § 2.5 |

### 3.04 — Fil d'Ariane

```html
<nav class="border-b border-gris-trait bg-fond-bloc px-6" aria-label="Fil d'Ariane">
  <ol class="flex h-8 items-center gap-2 text-xs text-gris-lecture">
    {% for maillon in fil_ariane %}
      <li class="flex items-center gap-2">
        {% if not forloop.first %}
          <svg class="h-3 w-3 stroke-gris-trait" aria-hidden="true">
            <use href="{% static 'icones/planche.svg' %}#chevron-droite"></use>
          </svg>
        {% endif %}
        {% if forloop.last %}
          <span class="font-medium text-encre" aria-current="page">{{ maillon.libelle }}</span>
        {% else %}
          <a href="{{ maillon.url }}" class="hover:text-marine-700">{{ maillon.libelle }}</a>
        {% endif %}
      </li>
    {% endfor %}
  </ol>
</nav>
```

### 3.05 — En-tête de page

```html
<div class="border-b border-gris-trait bg-fond-bloc px-6 pb-3 pt-4">
  <div class="flex items-end justify-between gap-6">
    <div>
      <h1 class="mb-0.5 font-titre text-xl font-semibold leading-tight">{% block titre_page %}{% endblock %}</h1>
      <p class="text-sm text-gris-lecture">{% block sous_titre_page %}{% endblock %}</p>
    </div>
    <div class="flex items-center gap-2">{% block actions_page %}{% endblock %}</div>
  </div>
</div>
```

## Famille B — Tableaux et données (08 → 16)

### 3.08 — Tableau dense

```html
<div class="border border-gris-trait bg-fond-bloc">
  <div class="max-h-80 overflow-auto">
    <table class="w-full border-collapse text-sm">
      <thead>
        <tr>
          <th scope="col" class="sticky top-0 z-10 bg-marine-900 px-3 py-2 text-left
                                 font-titre text-2xs font-semibold uppercase tracking-wider text-blanc">
            Matière
          </th>
          <th scope="col" class="sticky top-0 z-10 w-24 bg-marine-900 px-3 py-2 text-right
                                 font-titre text-2xs font-semibold uppercase tracking-wider text-blanc">
            Volume
          </th>
        </tr>
      </thead>
      <tbody>
        {% for ligne in lignes %}
          {% cycle 'bg-fond-bloc' 'bg-fond-bande' as bande silent %}
          <tr class="{% cycle bande %} h-ligne border-t border-gris-trait
                     transition-colors duration-survol hover:bg-fond-survol">
            <th scope="row" class="px-3 text-left font-medium">{{ ligne.matiere }}</th>
            <td class="px-3 text-right tabular-nums">{{ ligne.volume }} h</td>
          </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</div>
```

### 3.09 — En-tête figé et tri par colonne

```html
<th scope="col" aria-sort="{{ tri.matiere_aria }}"
    class="sticky top-0 z-10 bg-marine-900 px-3 py-2 text-left font-titre text-2xs
           font-semibold uppercase tracking-wider text-blanc">
  <a href="?tri={{ tri.matiere_suivant }}"
     class="inline-flex items-center gap-1.5 text-blanc no-underline
            hover:text-gris-trait
            focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2
            focus-visible:outline-blanc">
    Volume prescrit
    {% if tri.colonne == "volume" and tri.sens == "asc" %}
      <svg class="h-3 w-3 stroke-blanc" aria-hidden="true">
        <use href="{% static 'icones/planche.svg' %}#tri-croissant"></use>
      </svg>
    {% elif tri.colonne == "volume" %}
      <svg class="h-3 w-3 stroke-blanc" aria-hidden="true">
        <use href="{% static 'icones/planche.svg' %}#tri-decroissant"></use>
      </svg>
    {% else %}
      <svg class="h-3 w-3 stroke-blanc" aria-hidden="true">
        <use href="{% static 'icones/planche.svg' %}#tri"></use>
      </svg>
    {% endif %}
  </a>
</th>
```

### 3.10 — Pagination

```html
<nav class="flex items-center justify-between border-t border-gris-trait bg-fond-bande px-3 py-2 text-xs"
     aria-label="Pagination">
  <p class="tabular-nums text-gris-lecture">
    Éléments <strong class="text-encre">{{ page.start_index }} à {{ page.end_index }}</strong>
    sur <strong class="text-encre">{{ page.paginator.count }}</strong>
  </p>
  <div class="flex items-center gap-1">
    {% if page.has_previous %}
      <a href="?page={{ page.previous_page_number }}"
         class="border border-gris-trait bg-fond-bloc px-2.5 py-1 no-underline text-encre
                transition-colors duration-survol hover:bg-fond-bande">Précédent</a>
    {% else %}
      <span class="cursor-not-allowed border border-gris-trait bg-fond-bloc px-2.5 py-1
                   text-gris-eteint">Précédent</span>
    {% endif %}
    {% for numero in page.paginator.page_range %}
      {% if numero == page.number %}
        <span aria-current="page"
              class="border border-marine-900 bg-marine-900 px-2.5 py-1 font-semibold
                     tabular-nums text-blanc">{{ numero }}</span>
      {% else %}
        <a href="?page={{ numero }}"
           class="border border-gris-trait bg-fond-bloc px-2.5 py-1 tabular-nums no-underline
                  text-encre transition-colors duration-survol hover:bg-fond-bande">{{ numero }}</a>
      {% endif %}
    {% endfor %}
  </div>
</nav>
```

### 3.11 — Barre de filtres

```html
<form method="get"
      class="flex flex-wrap items-end gap-3 border border-gris-trait bg-fond-bloc px-3 py-2.5">
  <div>
    <label for="filtre-session"
           class="mb-1 block text-2xs font-medium uppercase tracking-wide text-gris-lecture">Session</label>
    <select id="filtre-session" name="session"
            class="h-controle w-64 rounded border border-gris-trait bg-fond-bloc px-2.5 text-sm
                   outline-none hover:border-marine-700
                   focus:border-marine-700 focus:ring-2 focus:ring-focus">
      {% for session in sessions %}<option value="{{ session.pk }}">{{ session.libelle }}</option>{% endfor %}
    </select>
  </div>
  <div>
    <label for="filtre-debut"
           class="mb-1 block text-2xs font-medium uppercase tracking-wide text-gris-lecture">Période</label>
    <input type="date" id="filtre-debut" name="debut" value="{{ filtres.debut|date:'Y-m-d' }}"
           class="h-controle rounded border border-gris-trait bg-fond-bloc px-2.5 text-sm
                  tabular-nums outline-none hover:border-marine-700
                  focus:border-marine-700 focus:ring-2 focus:ring-focus">
  </div>
  <button type="submit"
          class="inline-flex h-controle items-center gap-2 border border-marine-900 bg-marine-900
                 px-3.5 text-sm font-semibold text-blanc transition-colors duration-survol
                 hover:bg-marine-700
                 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2
                 focus-visible:outline-marine-700">
    Appliquer
  </button>
  <a href="{{ request.path }}" class="px-3 text-sm text-marine-700">Réinitialiser</a>
</form>
```

### 3.12 — Jeton de filtre actif

```html
<div class="mt-2 flex flex-wrap items-center gap-1.5">
  <span class="text-xs text-gris-lecture">Filtres actifs :</span>
  {% for filtre in filtres_actifs %}
    <span class="inline-flex items-center gap-1.5 border border-gris-trait bg-fond-bloc
                 py-0.5 pl-2.5 pr-1 text-xs">
      {{ filtre.libelle }}
      <a href="{{ filtre.url_retrait }}" aria-label="Retirer le filtre {{ filtre.libelle }}">
        <svg class="h-3 w-3 stroke-gris-lecture" aria-hidden="true">
          <use href="{% static 'icones/planche.svg' %}#rejet"></use>
        </svg>
      </a>
    </span>
  {% endfor %}
</div>
```

### 3.13 — État vide

```html
<div class="border-t border-gris-trait px-6 py-8">
  <svg class="mb-2.5 h-6 w-6 stroke-gris-trait" aria-hidden="true">
    <use href="{% static 'icones/planche.svg' %}#matiere"></use>
  </svg>
  <p class="mb-1 font-titre text-lg font-semibold">Aucune matière rattachée</p>
  <p class="mb-3.5 max-w-lg text-sm text-gris-lecture">
    Le référentiel déclare {{ referentiel.modules_declares }} modules, aucun n'est rattaché.
    Le volume total prescrit ne peut être calculé.
  </p>
  <a href="{% url 'referentiel:ajouter_matiere' referentiel.pk %}"
     class="inline-flex items-center gap-2 border border-marine-900 bg-marine-900 px-3.5 py-1.5
            text-sm font-semibold text-blanc no-underline transition-colors duration-survol
            hover:bg-marine-700">
    Ajouter une matière du catalogue
  </a>
</div>
```

### 3.14 — Squelette de chargement

```html
<tr class="h-ligne border-t border-gris-trait">
  <td class="px-3"><span class="block h-2 w-2/3 animate-squelette bg-gris-trait"></span></td>
  <td class="px-3"><span class="ml-auto block h-2 w-12 animate-squelette bg-gris-trait"></span></td>
</tr>
```

### 3.15 — Ligne de détail dépliable

Le dépliement se fait par `<details>` natif, sans script.

```html
<tr class="h-ligne border-t border-gris-trait bg-fond-bloc">
  <th scope="row" colspan="8" class="px-3 text-left font-medium">
    <details class="group">
      <summary class="flex cursor-pointer list-none items-center gap-2">
        <svg class="h-3 w-3 -rotate-90 stroke-gris-lecture transition-transform duration-notif
                    group-open:rotate-0" aria-hidden="true">
          <use href="{% static 'icones/planche.svg' %}#chevron-bas"></use>
        </svg>
        {{ matiere.libelle }}
      </summary>
      <div class="mt-3 grid grid-cols-3 gap-6 bg-sable px-4 py-3.5 font-normal">
        <div>
          <p class="mb-1.5 font-titre text-xs font-semibold uppercase tracking-wide text-marine-900">
            Prérequis</p>
          <p class="text-xs text-gris-lecture">{{ matiere.prerequis_libelles|default:"—" }}</p>
        </div>
        <div>
          <p class="mb-1.5 font-titre text-xs font-semibold uppercase tracking-wide text-marine-900">
            Instructeurs qualifiés</p>
          <p class="text-xs text-gris-lecture">{{ matiere.instructeurs_qualifies }}</p>
        </div>
        <div>
          <p class="mb-1.5 font-titre text-xs font-semibold uppercase tracking-wide text-marine-900">
            Dernière modification</p>
          <p class="text-xs text-gris-lecture">
            {{ matiere.modifie_par }} — {{ matiere.modifie_le|date:"d/m/Y H:i" }}</p>
        </div>
      </div>
    </details>
  </th>
</tr>
```

### 3.16 — Tableau éditable en ligne

```html
<tr class="border-b border-gris-trait bg-fond-bloc transition-colors duration-survol hover:bg-fond-survol">
  <th scope="row" class="px-3 py-1.5 text-left font-medium">{{ form.instance.libelle }}</th>
  <td class="px-3 py-1.5">
    <span class="flex w-24 items-stretch border border-gris-trait bg-fond-bloc">
      <input type="text" name="{{ form.volume.html_name }}" value="{{ form.volume.value }}"
             aria-label="Volume prescrit — {{ form.instance.libelle }}"
             class="h-ligne w-full border-0 bg-transparent px-2 text-right text-xs
                    tabular-nums outline-none">
      <span class="flex items-center border-l border-gris-trait bg-fond-bande px-2
                   text-2xs text-gris-lecture">h</span>
    </span>
  </td>
  <td class="px-3 py-1.5 text-right">
    <button type="submit" name="supprimer" value="{{ form.instance.pk }}"
            title="Retirer la matière du référentiel"
            aria-label="Retirer {{ form.instance.libelle }} du référentiel"
            class="inline-flex border border-transparent p-1 transition-colors duration-survol
                   hover:border-etat-ecart hover:bg-etat-ecart-fond">
      <svg class="h-4 w-4 stroke-etat-ecart" aria-hidden="true">
        <use href="{% static 'icones/planche.svg' %}#suppression"></use>
      </svg>
    </button>
  </td>
</tr>
```

## Famille C — Formulaires (17 → 26)

### 3.17 — Champ texte, six états

```html
<label for="{{ form.intitule.id_for_label }}"
       class="mb-1 block text-xs font-medium tracking-wide text-gris-lecture">
  Intitulé de la session
  {% if form.intitule.field.required %}<span class="text-etat-ecart">— obligatoire</span>{% endif %}
</label>

{% if form.intitule.errors %}
  <input type="text" id="{{ form.intitule.id_for_label }}" name="{{ form.intitule.html_name }}"
         value="{{ form.intitule.value|default_if_none:'' }}"
         aria-invalid="true" aria-describedby="{{ form.intitule.id_for_label }}-erreur"
         class="h-controle w-full animate-secousse rounded border border-etat-ecart
                bg-etat-ecart-fond px-2.5 text-sm outline-none
                focus:ring-2 focus:ring-focus-ecart">
  <p id="{{ form.intitule.id_for_label }}-erreur"
     class="mt-1 flex items-start gap-1.5 text-2xs text-etat-ecart">
    <svg class="mt-px h-3 w-3 shrink-0 stroke-etat-ecart" aria-hidden="true">
      <use href="{% static 'icones/planche.svg' %}#avertissement"></use>
    </svg>
    {{ form.intitule.errors|first }}
  </p>
{% elif form.intitule.field.disabled %}
  <input type="text" id="{{ form.intitule.id_for_label }}" name="{{ form.intitule.html_name }}"
         value="{{ form.intitule.value|default_if_none:'' }}" disabled
         class="h-controle w-full cursor-not-allowed rounded border border-gris-trait
                bg-fond-bande px-2.5 text-sm text-gris-lecture">
  <p class="mt-1 text-2xs text-gris-lecture">Session clôturée — modification interdite.</p>
{% else %}
  <input type="text" id="{{ form.intitule.id_for_label }}" name="{{ form.intitule.html_name }}"
         value="{{ form.intitule.value|default_if_none:'' }}"
         class="h-controle w-full rounded border border-gris-trait bg-fond-bloc px-2.5 text-sm
                text-encre outline-none hover:border-marine-700
                focus:border-marine-700 focus:ring-2 focus:ring-focus">
  <p class="mt-1 text-2xs text-gris-lecture">{{ form.intitule.help_text }}</p>
{% endif %}
```

### 3.18 — Champ numérique à unité accolée

```html
<div class="flex w-36 items-stretch rounded border border-gris-trait bg-fond-bloc
            hover:border-marine-700
            focus-within:border-marine-700 focus-within:ring-2 focus-within:ring-focus">
  <input type="text" inputmode="numeric" id="{{ form.volume.id_for_label }}"
         name="{{ form.volume.html_name }}" value="{{ form.volume.value|default_if_none:'' }}"
         class="h-[30px] w-full border-0 bg-transparent px-2.5 text-right text-sm
                tabular-nums outline-none">
  <!-- arbitraire : h-[30px], hauteur intérieure du contrôle bordé de 1 px -->
  <span class="flex items-center border-l border-gris-trait bg-fond-bande px-2.5
               text-xs font-medium text-gris-lecture">h</span>
</div>
<p class="mt-1 text-2xs text-gris-lecture">Entier, entre 1 et 400.</p>
```

### 3.19 — Sélecteur de date et de plage horaire

```html
<div class="flex items-center gap-2">
  <input type="time" name="debut" value="{{ seance.debut|time:'H:i' }}" aria-label="Heure de début"
         class="h-controle w-28 rounded border border-gris-trait bg-fond-bloc px-2.5 text-sm
                tabular-nums outline-none hover:border-marine-700
                focus:border-marine-700 focus:ring-2 focus:ring-focus">
  <span class="text-sm text-gris-lecture" aria-hidden="true">→</span>
  <input type="time" name="fin" value="{{ seance.fin|time:'H:i' }}" aria-label="Heure de fin"
         class="h-controle w-28 rounded border border-gris-trait bg-fond-bloc px-2.5 text-sm
                tabular-nums outline-none hover:border-marine-700
                focus:border-marine-700 focus:ring-2 focus:ring-focus">
  <span class="text-2xs text-gris-lecture">durée {{ seance.duree_lisible }} — {{ grille_active.libelle }}</span>
</div>
```

### 3.20 — Liste déroulante

```html
<select id="{{ form.lieu.id_for_label }}" name="{{ form.lieu.html_name }}"
        class="h-controle w-full rounded border border-gris-trait bg-fond-bloc px-2.5 text-sm
               outline-none hover:border-marine-700
               focus:border-marine-700 focus:ring-2 focus:ring-focus">
  {% for valeur, libelle in form.lieu.field.choices %}
    <option value="{{ valeur }}" {% if valeur == form.lieu.value %}selected{% endif %}>{{ libelle }}</option>
  {% endfor %}
</select>
```

### 3.21 — Sélection multiple à jetons

Sans script, la sélection multiple repose sur `<select multiple>`. Les jetons
affichent l'état courant, chacun retirable par un bouton de soumission nommé.

```html
<div class="flex min-h-controle flex-wrap items-center gap-1.5 rounded border border-gris-trait px-2 py-1">
  {% for cible in cibles_selectionnees %}
    <span class="inline-flex items-center gap-1.5 border border-focus bg-fond-survol
                 py-0.5 pl-2 pr-1 text-xs font-medium text-marine-900">
      {{ cible.libelle }}
      <button type="submit" name="retirer_cible" value="{{ cible.pk }}"
              aria-label="Retirer {{ cible.libelle }}">
        <svg class="h-3 w-3 stroke-marine-700" aria-hidden="true">
          <use href="{% static 'icones/planche.svg' %}#rejet"></use>
        </svg>
      </button>
    </span>
  {% empty %}
    <span class="text-xs text-gris-lecture">Aucune cible — la période s'applique à tout le centre</span>
  {% endfor %}
</div>
<p class="mt-1 text-2xs text-gris-lecture">
  {{ cibles_selectionnees|length }} cible{{ cibles_selectionnees|pluralize }} sélectionnée{{ cibles_selectionnees|pluralize }}.
</p>
```

### 3.22 — Zone de texte

```html
<label for="{{ form.motif.id_for_label }}"
       class="mb-1 block text-xs font-medium tracking-wide text-gris-lecture">
  Motif du rejet <span class="text-etat-ecart">— obligatoire en cas de rejet</span>
</label>
<textarea id="{{ form.motif.id_for_label }}" name="{{ form.motif.html_name }}" rows="4"
          maxlength="500"
          class="w-full resize-y rounded border border-gris-trait bg-fond-bloc px-2.5 py-2
                 text-sm leading-normal outline-none
                 focus:border-marine-700 focus:ring-2 focus:ring-focus">{{ form.motif.value|default_if_none:'' }}</textarea>
<div class="mt-1 flex justify-between text-2xs text-gris-lecture">
  <span>Le motif est reporté au procès-verbal et notifié à la cellule planification.</span>
  <span class="tabular-nums">500 caractères au plus</span>
</div>
```

### 3.23 — Cases à cocher, boutons radio, interrupteur

L'interrupteur est une case à cocher stylée par `peer`, sans script.

```html
<fieldset class="grid gap-2">
  <legend class="mb-1.5 text-xs font-medium tracking-wide text-gris-lecture">Notifications</legend>
  {% for case in form.notifications %}
    <label class="flex cursor-pointer items-center gap-2 text-sm">
      {{ case.tag }}
      <span>{{ case.choice_label }}</span>
    </label>
  {% endfor %}
</fieldset>

<label class="flex cursor-pointer items-center gap-2.5 text-sm">
  <input type="checkbox" name="comptee" class="peer sr-only"
         {% if seance.comptee %}checked{% endif %}>
  <span class="relative h-5 w-9 shrink-0 rounded-pilule border border-gris-trait bg-gris-inerte
               transition-colors duration-badge
               peer-checked:border-etat-conforme peer-checked:bg-etat-conforme
               peer-focus-visible:outline peer-focus-visible:outline-2
               peer-focus-visible:outline-offset-2 peer-focus-visible:outline-marine-700">
    <span class="absolute left-0.5 top-0.5 h-3.5 w-3.5 rounded-pilule bg-blanc
                 transition-[left] duration-badge peer-checked:left-[18px]"></span>
    <!-- arbitraire : left-[18px], course du curseur dans une piste de 36 px -->
  </span>
  Séance comptée dans le volume réalisé
</label>
```

Dans `forms.py`, les classes des cases et radios se posent sur le widget :

```python
notifications = forms.MultipleChoiceField(
    widget=forms.CheckboxSelectMultiple(
        attrs={"class": "h-3.5 w-3.5 accent-marine-900"}
    ),
)
```

### 3.24 — Formulaire à deux colonnes

```html
<form method="post" class="border border-gris-trait bg-fond-bloc">
  {% csrf_token %}
  <div class="grid grid-cols-2 gap-6 px-5 py-4">
    <fieldset class="rounded border border-gris-trait px-4 pb-4 pt-3.5">
      <legend class="px-1.5 font-titre text-xs font-semibold uppercase tracking-wide text-marine-900">
        Identification de la séance
      </legend>
      <div class="grid gap-3">{% include "formulaires/champs_identification.html" %}</div>
    </fieldset>
    <fieldset class="rounded border border-gris-trait px-4 pb-4 pt-3.5">
      <legend class="px-1.5 font-titre text-xs font-semibold uppercase tracking-wide text-marine-900">
        Affectation
      </legend>
      <div class="grid gap-3">{% include "formulaires/champs_affectation.html" %}</div>
    </fieldset>
  </div>
  {% include "composants/pied_formulaire.html" %}
</form>
```

### 3.25 — Pied de formulaire

```html
<div class="flex items-center justify-between border-t border-gris-trait bg-fond-bande px-5 py-2.5">
  <p class="text-xs text-gris-lecture">Les champs sans mention sont facultatifs.</p>
  <div class="flex gap-2">
    <a href="{{ url_retour }}" class="inline-flex items-center px-3.5 py-1.5 text-sm text-marine-700">
      Annuler
    </a>
    <button type="submit" name="action" value="brouillon"
            class="inline-flex items-center border border-gris-trait bg-fond-bloc px-3.5 py-1.5
                   text-sm font-medium transition-colors duration-survol
                   hover:border-marine-700 hover:bg-fond-survol">
      Enregistrer en brouillon
    </button>
    <button type="submit" name="action" value="confirmer"
            class="inline-flex items-center gap-2 border border-marine-900 bg-marine-900 px-3.5 py-1.5
                   text-sm font-semibold text-blanc transition-colors duration-survol
                   hover:bg-marine-700">
      Confirmer l'affectation
    </button>
  </div>
</div>
```

### 3.26 — Dépôt de fichier et compte rendu d'analyse

```html
<form method="post" enctype="multipart/form-data"
      class="border border-dashed border-gris-trait bg-fond-bloc px-4 py-6">
  {% csrf_token %}
  <p class="mb-1 font-titre text-base font-semibold">Déposer le fichier des stagiaires</p>
  <p class="mb-2.5 text-xs text-gris-lecture">
    CSV ou XLSX, 2 Mo au plus. Le fichier est analysé avant tout enregistrement.
  </p>
  <input type="file" name="fichier" accept=".csv,.xlsx"
         class="text-sm file:mr-3 file:border file:border-gris-trait file:bg-fond-bloc
                file:px-3 file:py-1 file:text-xs file:font-medium file:text-encre">
</form>

<table class="w-full border-collapse text-xs">
  <thead>
    <tr>
      <th scope="col" class="border-b border-gris-trait bg-fond-bande px-3 py-1.5 text-left
                             font-titre text-2xs font-semibold uppercase tracking-wide
                             text-gris-lecture">Ligne</th>
      <th scope="col" class="border-b border-gris-trait bg-fond-bande px-3 py-1.5 text-left
                             font-titre text-2xs font-semibold uppercase tracking-wide
                             text-gris-lecture">Anomalie</th>
    </tr>
  </thead>
  <tbody>
    {% for anomalie in analyse.anomalies %}
      <tr class="border-b border-gris-trait">
        <td class="px-3 py-1.5 font-mono font-medium text-etat-ecart">{{ anomalie.ligne }}</td>
        <td class="px-3 py-1.5 text-gris-lecture">{{ anomalie.motif }}</td>
      </tr>
    {% endfor %}
  </tbody>
</table>
```

## Famille D — États, badges et encadrés (27 → 34)

### 3.27 — Badges d'état du programme

Cinq traitements séparables sans la couleur : filet pointillé, filet plein et
pastille, aplat et coche, filet double et croix, aplat et icône de document.

```html
{% if programme.etat == "brouillon" %}
  <span class="inline-flex items-center gap-1.5 rounded-pilule border border-dashed
               border-gris-lecture bg-fond-bloc px-2.5 py-0.5 text-2xs font-semibold
               tracking-wide text-gris-lecture">BROUILLON</span>
{% elif programme.etat == "soumis" %}
  <span class="inline-flex items-center gap-1.5 rounded-pilule border border-etat-attention
               bg-etat-attention-fond px-2.5 py-0.5 text-2xs font-semibold tracking-wide
               text-etat-attention">
    <span class="h-1.5 w-1.5 rounded-pilule bg-etat-attention"></span>SOUMIS
  </span>
{% elif programme.etat == "valide" %}
  <span class="inline-flex items-center gap-1.5 rounded-pilule bg-etat-conforme px-2.5 py-0.5
               text-2xs font-semibold tracking-wide text-blanc">
    <svg class="h-3 w-3 stroke-blanc" aria-hidden="true">
      <use href="{% static 'icones/planche.svg' %}#validation"></use>
    </svg>VALIDÉ
  </span>
{% elif programme.etat == "rejete" %}
  <span class="inline-flex items-center gap-1.5 rounded-pilule border-2 border-etat-ecart
               bg-fond-bloc px-2.5 py-0.5 text-2xs font-semibold tracking-wide text-etat-ecart">
    <svg class="h-3 w-3 stroke-etat-ecart" aria-hidden="true">
      <use href="{% static 'icones/planche.svg' %}#rejet"></use>
    </svg>REJETÉ
  </span>
{% elif programme.etat == "affiche" %}
  <span class="inline-flex items-center gap-1.5 rounded-pilule bg-marine-900 px-2.5 py-0.5
               text-2xs font-semibold tracking-wide text-blanc">
    <svg class="h-3 w-3 stroke-blanc" aria-hidden="true">
      <use href="{% static 'icones/planche.svg' %}#document-valide"></use>
    </svg>AFFICHÉ
  </span>
{% endif %}
```

### 3.28 — Badge de priorité

```html
{% if seance.priorite == "must" %}
  <span class="inline-flex h-5 w-6 items-center justify-center bg-marine-900 font-titre
               text-xs font-bold text-blanc" title="Must — non négociable">M</span>
{% elif seance.priorite == "should" %}
  <span class="inline-flex h-5 w-6 items-center justify-center border border-marine-900
               font-titre text-xs font-bold text-marine-900"
        title="Should — placée si le créneau le permet">S</span>
{% else %}
  <span class="inline-flex h-5 w-6 items-center justify-center border border-dashed
               border-gris-lecture font-titre text-xs font-bold text-gris-lecture"
        title="Could — reportable sans écart">C</span>
{% endif %}
```

### 3.29 — Badge de type d'évaluation

```html
{% if evaluation.certificative %}
  <span class="bg-marine-900 px-2 py-px text-2xs font-semibold tracking-wide text-blanc">
    CERTIFICATIVE</span>
{% else %}
  <span class="border border-marine-700 px-2 py-px text-2xs font-semibold tracking-wide
               text-marine-700">FORMATIVE</span>
{% endif %}
```

### 3.30 — Encadrés

Quatre variantes, mêmes classes que le bloc de messages (§ 2.5), employées hors
du cadre de messages de Django.

```html
<div class="flex items-start gap-3 border border-l-[3px] border-gris-trait
            border-l-etat-attention bg-etat-attention-fond px-4 py-3">
  <svg class="mt-px h-4 w-4 shrink-0 stroke-etat-attention" aria-hidden="true">
    <use href="{% static 'icones/planche.svg' %}#avertissement"></use>
  </svg>
  <div>
    <p class="font-titre text-base font-semibold text-etat-attention">Avertissement</p>
    <p class="text-xs text-gris-lecture">
      Le référentiel déclare {{ referentiel.modules_declares }} modules,
      {{ referentiel.modules_rattaches }} sont rattachés. Écart signalé au directeur (RG-65).
    </p>
  </div>
</div>
```

### 3.31 — Notification

Rendue par le cadre de messages, positionnée en superposition. Ombre admise.

```html
<div role="status" aria-live="polite"
     class="fixed right-6 top-4 z-40 min-w-[340px] animate-glisser border border-l-[3px]
            border-gris-trait border-l-etat-conforme bg-fond-bloc px-3.5 py-3
            shadow-superpose">
  <!-- arbitraire : min-w-[340px], largeur plancher de la notification -->
  <p class="font-titre text-sm font-semibold">Remplacement confirmé</p>
  <p class="text-xs text-gris-lecture">{{ message }}</p>
</div>
```

### 3.32 — Boîte de dialogue

`<dialog>` natif, ouvert par le serveur avec l'attribut `open`. Ombre admise.

```html
<dialog open aria-labelledby="titre-dialogue"
        class="w-[520px] animate-ouvrir border border-marine-900 bg-fond-bloc p-0
               shadow-superpose backdrop:bg-encre/45">
  <!-- arbitraire : w-[520px], largeur fixe de dialogue -->
  <form method="post">
    {% csrf_token %}
    <p id="titre-dialogue"
       class="flex items-center gap-2 bg-marine-900 px-4 py-2 font-titre text-base
              font-semibold text-blanc">
      Soumettre le programme à validation
    </p>
    <div class="px-4 py-4 text-sm">
      <p>Le programme passera à l'état SOUMIS et sera verrouillé en modification
         jusqu'à la décision de la cellule pédagogique.</p>
      <p class="mt-3 border border-gris-trait bg-sable px-3 py-2.5 text-xs text-gris-lecture">
        Circuit : soumission, validation pédagogique, signature du directeur, affichage.
      </p>
    </div>
    <div class="flex justify-end gap-2 border-t border-gris-trait bg-fond-bande px-4 py-2.5">
      <a href="{{ url_retour }}" class="inline-flex items-center px-3.5 py-1.5 text-sm text-marine-700">
        Annuler</a>
      <button type="submit"
              class="inline-flex items-center gap-2 border border-marine-900 bg-marine-900
                     px-3.5 py-1.5 text-sm font-semibold text-blanc
                     transition-colors duration-survol hover:bg-marine-700">Soumettre</button>
    </div>
  </form>
</dialog>
```

Variante destructive : `border-etat-ecart`, bandeau `bg-etat-ecart`, bouton
`border-etat-ecart bg-etat-ecart hover:bg-etat-ecart-fonce`.

### 3.33 — Indicateur d'écart

```html
{% if suivi.statut == "conforme" %}
  <span class="text-xs font-medium tabular-nums text-etat-conforme">conforme</span>
{% elif suivi.statut == "achevee" %}
  <span class="text-xs font-medium tabular-nums text-etat-conforme">achevée</span>
{% elif suivi.statut == "en_cours" %}
  <span class="text-xs font-medium tabular-nums text-marine-700">en cours</span>
{% elif suivi.statut == "retard" %}
  <span class="text-xs font-medium tabular-nums text-etat-ecart">retard {{ suivi.ecart_pourcent }} %</span>
{% elif suivi.statut == "depassement" %}
  <span class="text-xs font-medium tabular-nums text-etat-attention">dépassement</span>
{% else %}
  <span class="text-xs font-medium tabular-nums text-gris-lecture">non commencée</span>
{% endif %}
```

### 3.34 — Barre prescrit / programmé / réalisé

La vue fournit `douzieme_programme` et `douzieme_realise`, entiers de 0 à 12.
Le gabarit choisit une fraction parmi les utilitaires de Tailwind — aucune
largeur en ligne. La valeur exacte reste lisible en chiffres.

```html
<div class="relative h-4 border border-gris-trait bg-gris-inerte">
  <div class="absolute inset-y-0 left-0 bg-marine-700 transition-[width] duration-barre
              {% if suivi.douzieme_programme == 0 %}w-0
              {% elif suivi.douzieme_programme == 1 %}w-1/12
              {% elif suivi.douzieme_programme == 2 %}w-2/12
              {% elif suivi.douzieme_programme == 3 %}w-3/12
              {% elif suivi.douzieme_programme == 4 %}w-4/12
              {% elif suivi.douzieme_programme == 5 %}w-5/12
              {% elif suivi.douzieme_programme == 6 %}w-6/12
              {% elif suivi.douzieme_programme == 7 %}w-7/12
              {% elif suivi.douzieme_programme == 8 %}w-8/12
              {% elif suivi.douzieme_programme == 9 %}w-9/12
              {% elif suivi.douzieme_programme == 10 %}w-10/12
              {% elif suivi.douzieme_programme == 11 %}w-11/12
              {% else %}w-full{% endif %}"></div>
  <div class="absolute inset-y-1 left-0 bg-etat-conforme transition-[width] duration-barre
              {% if suivi.douzieme_realise == 0 %}w-0
              {% elif suivi.douzieme_realise == 1 %}w-1/12
              {% elif suivi.douzieme_realise == 2 %}w-2/12
              {% elif suivi.douzieme_realise == 3 %}w-3/12
              {% elif suivi.douzieme_realise == 4 %}w-4/12
              {% elif suivi.douzieme_realise == 5 %}w-5/12
              {% elif suivi.douzieme_realise == 6 %}w-6/12
              {% elif suivi.douzieme_realise == 7 %}w-7/12
              {% elif suivi.douzieme_realise == 8 %}w-8/12
              {% elif suivi.douzieme_realise == 9 %}w-9/12
              {% elif suivi.douzieme_realise == 10 %}w-10/12
              {% elif suivi.douzieme_realise == 11 %}w-11/12
              {% else %}w-full{% endif %}"></div>
</div>
<p class="mt-1 flex justify-end gap-2.5 text-xs tabular-nums text-gris-lecture">
  <span>{{ suivi.prescrit }} / {{ suivi.programme }} / {{ suivi.realise }} h</span>
  <span class="min-w-16 text-right font-semibold text-etat-ecart">{{ suivi.ecart_signe }}</span>
</p>
```

Dans la vue :

```python
def douzieme(partie, total):
    if not total:
        return 0
    return min(12, round(12 * partie / total))
```

## Famille E — Restitution métier (35 → 38)

### 3.35 — Bloc de statistique

```html
<div class="border border-gris-trait bg-fond-bloc px-4 py-3.5">
  <p class="mb-1.5 text-2xs font-medium uppercase tracking-wide text-gris-lecture">
    {{ indicateur.libelle }}</p>
  <p class="flex items-baseline gap-1.5">
    <span class="font-titre text-xl font-bold leading-none tabular-nums">{{ indicateur.valeur }}</span>
    <span class="text-xs text-gris-lecture">{{ indicateur.unite }}</span>
  </p>
  <p class="mt-2 border-t border-dotted border-gris-trait pt-1.5 text-xs tabular-nums">
    {% if indicateur.sens == "favorable" %}
      <span class="font-medium text-etat-conforme">{{ indicateur.variation }}</span>
    {% elif indicateur.sens == "defavorable" %}
      <span class="font-medium text-etat-ecart">{{ indicateur.variation }}</span>
    {% else %}
      <span class="font-medium text-etat-attention">{{ indicateur.variation }}</span>
    {% endif %}
    <span class="text-gris-lecture">{{ indicateur.reference }}</span>
  </p>
</div>
```

### 3.36 — Créneau non pourvu

```html
<section class="border border-etat-attention bg-fond-bloc">
  <div class="flex items-center gap-2 border-b border-gris-trait bg-etat-attention-fond px-3.5 py-2">
    <svg class="h-4 w-4 stroke-etat-attention" aria-hidden="true">
      <use href="{% static 'icones/planche.svg' %}#avertissement"></use>
    </svg>
    <h2 class="font-titre text-sm font-semibold text-etat-attention">Créneau non pourvu</h2>
    <p class="ml-auto font-mono text-2xs tabular-nums text-gris-lecture">
      {{ creneau.brigade }} · {{ creneau.date|date:"D d/m" }} · {{ creneau.plage }}</p>
  </div>
  <div class="px-3.5 py-3">
    <p class="mb-1.5 text-2xs font-medium uppercase tracking-wide text-gris-lecture">
      Instructeurs qualifiés — cause d'indisponibilité</p>
    <ul class="border border-gris-trait">
      {% for cas in creneau.indisponibilites %}
        <li class="flex items-start gap-2.5 border-b border-gris-trait px-3 py-2">
          <span class="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-pilule bg-etat-ecart"></span>
          <span class="flex-1">
            <span class="block text-sm font-medium">{{ cas.instructeur }}</span>
            <span class="block text-2xs text-gris-lecture">{{ cas.cause }}</span>
          </span>
          <span class="shrink-0 border border-etat-ecart px-1.5 font-mono text-2xs text-etat-ecart">
            {{ cas.code }}</span>
        </li>
      {% endfor %}
    </ul>
  </div>
</section>
```

### 3.37 — Remplaçants classés

Le critère de classement est affiché : la proposition ne s'impose pas.

```html
<tbody>
  {% for candidat in remplacants %}
    <tr class="border-b border-gris-trait transition-colors duration-survol hover:bg-fond-survol">
      <td class="px-3 py-2 font-titre text-base font-bold tabular-nums text-marine-900">
        {{ forloop.counter }}</td>
      <td class="px-3 py-2 font-medium">{{ candidat.nom }}</td>
      <td class="px-3 py-2 text-right tabular-nums">{{ candidat.charge_semaine }}</td>
      <td class="px-3 py-2 text-xs text-gris-lecture">{{ candidat.anteriorite }}</td>
      <td class="px-3 py-2 text-xs text-gris-lecture">{{ candidat.statut }}</td>
      <td class="px-3 py-2 text-right">
        <button type="submit" name="designer" value="{{ candidat.pk }}"
                class="inline-flex items-center border border-gris-trait bg-fond-bloc px-2.5 py-1
                       text-xs font-semibold text-marine-900 transition-colors duration-survol
                       hover:border-marine-700 hover:bg-fond-survol">Désigner</button>
      </td>
    </tr>
  {% endfor %}
</tbody>
<tfoot>
  <tr>
    <td colspan="6" class="border-t border-gris-trait bg-sable px-3 py-2.5 text-xs text-gris-lecture">
      <strong class="text-encre">Critère de classement :</strong> qualification et disponibilité
      éliminatoires, puis charge hebdomadaire croissante, antériorité sur la brigade, statut (RG-43).
      Vous restez libre de désigner un autre instructeur qualifié.
    </td>
  </tr>
</tfoot>
```

### 3.38 — Chronologie des avenants

```html
<ol class="grid">
  {% for avenant in seance.avenants %}
    <li class="grid grid-cols-[130px_22px_1fr] items-start gap-3">
      <!-- arbitraire : grid-cols-[130px_22px_1fr], gouttière de chronologie à largeur fixe -->
      <span class="pt-px text-right text-xs tabular-nums text-gris-lecture">
        {{ avenant.horodatage|date:"d/m/Y H:i" }}</span>
      <span class="flex h-full flex-col items-center">
        {% if avenant.nature == "non_execution" %}
          <span class="mt-1 h-2.5 w-2.5 shrink-0 rounded-pilule bg-etat-ecart"></span>
        {% elif avenant.nature == "report" %}
          <span class="mt-1 h-2.5 w-2.5 shrink-0 rounded-pilule bg-etat-attention"></span>
        {% elif avenant.nature == "affichage" %}
          <span class="mt-1 h-2.5 w-2.5 shrink-0 rounded-pilule bg-etat-conforme"></span>
        {% else %}
          <span class="mt-1 h-2.5 w-2.5 shrink-0 rounded-pilule bg-marine-700"></span>
        {% endif %}
        {% if not forloop.last %}<span class="w-px flex-1 bg-gris-trait"></span>{% endif %}
      </span>
      <span class="pb-4">
        <span class="block text-sm font-semibold">{{ avenant.titre }}</span>
        <span class="block text-xs text-gris-lecture">{{ avenant.motif }}</span>
        <span class="mt-0.5 block font-mono text-2xs text-gris-lecture">{{ avenant.auteur }}</span>
      </span>
    </li>
  {% endfor %}
</ol>
```

## Famille F — Actions et contrôles (39 → 43)

### 3.39 — Boutons, quatre variantes

```html
<button type="submit"
        class="inline-flex items-center gap-2 border border-marine-900 bg-marine-900 px-3.5 py-1.5
               text-sm font-semibold text-blanc transition-colors duration-survol
               hover:bg-marine-700
               focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2
               focus-visible:outline-marine-700
               disabled:cursor-not-allowed disabled:border-gris-trait disabled:bg-gris-trait">
  Soumettre
</button>

<button type="submit"
        class="inline-flex items-center gap-2 border border-gris-trait bg-fond-bloc px-3.5 py-1.5
               text-sm font-medium transition-colors duration-survol
               hover:border-marine-700 hover:bg-fond-survol
               focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2
               focus-visible:outline-marine-700
               disabled:cursor-not-allowed disabled:border-gris-inerte disabled:bg-fond-page
               disabled:text-gris-eteint">
  Enregistrer
</button>

<a href="{{ url_retour }}"
   class="inline-flex items-center px-3 py-1.5 text-sm text-marine-700 no-underline
          transition-colors duration-survol hover:bg-fond-survol">Annuler</a>

<button type="submit" name="supprimer" value="{{ objet.pk }}"
        class="inline-flex items-center gap-2 border border-etat-ecart bg-fond-bloc px-3.5 py-1.5
               text-sm font-semibold text-etat-ecart transition-colors duration-survol
               hover:bg-etat-ecart-fond
               focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2
               focus-visible:outline-etat-ecart">
  Supprimer
</button>
```

### 3.40 — Bouton d'action de ligne

Seul cas où l'icône remplace le mot. Cible de 28 px au moins.

```html
<button type="submit" name="modifier" value="{{ seance.pk }}"
        title="Modifier l'affectation" aria-label="Modifier l'affectation de {{ seance }}"
        class="inline-flex border border-transparent p-1 transition-colors duration-survol
               hover:border-marine-700 hover:bg-fond-survol
               focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2
               focus-visible:outline-marine-700">
  <svg class="h-4 w-4 stroke-marine-900" aria-hidden="true">
    <use href="{% static 'icones/planche.svg' %}#modification"></use>
  </svg>
</button>
```

### 3.41 — Menu déroulant d'actions

`<details>` natif, sans script. Ombre admise sur le panneau.

```html
<details class="relative inline-block">
  <summary class="inline-flex cursor-pointer list-none items-center gap-2 border border-gris-trait
                  bg-fond-bloc px-3 py-1.5 text-sm font-medium transition-colors duration-survol
                  hover:bg-fond-bande">
    Actions
    <svg class="h-3.5 w-3.5 stroke-gris-lecture" aria-hidden="true">
      <use href="{% static 'icones/planche.svg' %}#chevron-bas"></use>
    </svg>
  </summary>
  <div class="absolute right-0 z-30 mt-1 min-w-60 animate-ouvrir border border-gris-trait
              bg-fond-bloc text-sm shadow-superpose">
    <a href="{% url 'planification:modifier' programme.pk %}"
       class="flex items-center gap-2.5 px-3 py-1.5 no-underline text-encre
              transition-colors duration-survol hover:bg-fond-survol">Modifier une affectation</a>
    <a href="{% url 'planification:regrouper' programme.pk %}"
       class="flex items-center gap-2.5 px-3 py-1.5 no-underline text-encre
              transition-colors duration-survol hover:bg-fond-survol">Regrouper des brigades</a>
    <span class="flex cursor-not-allowed items-center gap-2.5 border-t border-gris-trait px-3 py-1.5
                 text-gris-eteint">Exporter — indisponible en brouillon</span>
    <button type="submit" name="vider" value="{{ programme.pk }}"
            class="flex w-full items-center gap-2.5 border-t border-gris-trait px-3 py-1.5
                   text-left text-etat-ecart transition-colors duration-survol
                   hover:bg-etat-ecart-fond">Vider le programme</button>
  </div>
</details>
```

### 3.42 — Onglets

```html
<nav class="flex border-b border-gris-trait bg-fond-bande" aria-label="Sections">
  {% for onglet in onglets %}
    {% if onglet.slug == onglet_actif %}
      <a href="{{ onglet.url }}" aria-current="page"
         class="border-r border-gris-trait bg-fond-bloc px-4 py-2 font-titre text-sm font-semibold
                text-marine-900 no-underline shadow-[inset_0_-3px_0_currentColor]">
        <!-- arbitraire : soulignement intérieur, sans équivalent utilitaire -->
        {{ onglet.libelle }}</a>
    {% else %}
      <a href="{{ onglet.url }}"
         class="border-r border-gris-trait px-4 py-2 font-titre text-sm font-medium
                text-gris-lecture no-underline transition-colors duration-survol
                hover:bg-fond-bloc hover:text-marine-900">{{ onglet.libelle }}</a>
    {% endif %}
  {% endfor %}
</nav>
```

### 3.43 — Groupe segmenté

Trois choix au plus, exclusifs, libellés courts. Au-delà, employer les onglets.

```html
<div class="inline-flex border border-gris-trait" role="group" aria-label="Granularité">
  {% for segment in segments %}
    {% if segment.slug == segment_actif %}
      <a href="{{ segment.url }}" aria-current="true"
         class="bg-marine-900 px-4 py-1.5 text-xs font-semibold text-blanc no-underline">
        {{ segment.libelle }}</a>
    {% else %}
      <a href="{{ segment.url }}"
         class="border-l border-gris-trait bg-fond-bloc px-4 py-1.5 text-xs text-encre
                no-underline transition-colors duration-survol hover:bg-fond-bande">
        {{ segment.libelle }}</a>
    {% endif %}
  {% endfor %}
</div>
```

Le premier segment ne porte pas `border-l` : `{% if forloop.first %}` sélectionne
la variante sans bordure gauche, écrite en toutes lettres.

## Famille G — Impression (44 → 46)

### 3.44 — En-tête de document officiel

Les classes `print:` génèrent la variante papier ; le CSS de la § 4 porte la
géométrie de page.

```html
<header class="hidden border-b-2 border-noir pb-1.5 print:flex print:justify-between">
  <div>
    <p class="font-titre text-xs font-bold uppercase tracking-widest text-noir">Centre d'instruction</p>
    <p class="font-titre text-2xs uppercase tracking-wider text-noir">
      Direction de la formation — {{ cellule }}</p>
  </div>
  <div class="text-center">
    <p class="font-titre text-sm font-bold uppercase tracking-wide text-noir">{{ document.titre }}</p>
    <p class="text-2xs tabular-nums text-noir">{{ document.sous_titre }}</p>
  </div>
  <div class="text-right text-2xs tabular-nums text-noir">
    <p>{{ document.lieu }}, le {{ document.edite_le|date:"d/m/Y" }}</p>
    <p class="font-mono">{{ document.reference }}</p>
  </div>
</header>
```

### 3.45 — Pied de signature

```html
<div class="mt-6 hidden break-inside-avoid grid-cols-2 gap-16 print:grid">
  <div class="text-2xs text-noir">
    <p>Édité par</p>
    <p class="font-semibold">{{ document.edite_par }}</p>
    <p class="tabular-nums">Le {{ document.edite_le|date:"d/m/Y à H:i" }}</p>
  </div>
  <div class="text-2xs text-noir">
    <p class="mb-1">À {{ document.lieu }}, le ……………………</p>
    <p class="font-semibold">{{ document.signataire }}</p>
    <p class="mb-1.5">{{ document.signataire_fonction }}</p>
    <div class="flex h-20 items-end justify-between border border-noir px-1.5 py-1">
      <span>Signature</span><span>Cachet</span>
    </div>
  </div>
</div>
```

### 3.46 — Feuille de style d'impression

Voir § 4.

---

# 4 — Feuille de style d'impression

`static/css/impression.css`, chargée par `<link media="print">` (§ 2.1). Ce
fichier porte la géométrie de page et les corrections monochromes que les
utilitaires `print:` ne peuvent pas exprimer. Il ne contient aucun `@apply` et
ne définit aucune classe réutilisable : il agit sur les balises et sur quatre
attributs `data-*` de rôle documentaire.

```css
/* --------------------------------------------------------------------------
   Impression — géométrie de page et rendu monochrome
   Les documents s'impriment sur des imprimantes noir et blanc.
   -------------------------------------------------------------------------- */

/* 1. Format. Paysage pour le programme hebdomadaire et le suivi ;
      portrait partout ailleurs. */
@page {
  size: A4 portrait;
  margin: 14mm 12mm 16mm;
}
@page paysage {
  size: A4 landscape;
  margin: 12mm;
}
[data-impression="paysage"] {
  page: paysage;
}

/* 2. Masquer tout ce qui n'est pas le document. */
header nav,
[data-impression="masquer"] {
  display: none !important;
}
body > header,
body > footer,
body > nav,
form[method="get"],
dialog,
details > summary {
  display: none !important;
}

/* 3. Supprimer l'habillage écran. */
body {
  min-width: 0;
  background: #fff;
  color: #000;
  font-size: 10pt;
  line-height: 1.35;
}
main {
  padding: 0;
}
section,
div,
table {
  box-shadow: none !important;
}
a {
  color: #000;
  text-decoration: none;
}
a[href]::after {
  content: "";
}

/* 4. Tableaux : filets noirs, en-tête en trame grise.
      L'aplat marine ne s'imprime pas. */
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 8.5pt;
}
thead th {
  border: 1px solid #000 !important;
  background: #e6e6e6 !important;
  color: #000 !important;
  padding: 3px 6px;
  text-align: left;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}
tbody td,
tbody th {
  border: 1px solid #000 !important;
  padding: 2px 6px;
}
tbody tr:nth-child(even) {
  background: #fff !important;
}
tbody tr[data-impression="total"] > * {
  background: #f0f0f0 !important;
  font-weight: 700;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}

/* 5. En-tête de tableau répété sur chaque page, pied de page numéroté. */
thead {
  display: table-header-group;
}
tfoot {
  display: table-footer-group;
}
[data-impression="entete"] {
  position: running(entete);
}
@page {
  @top-left {
    content: element(entete);
  }
  @bottom-left {
    content: attr(data-reference);
    font-size: 8pt;
  }
  @bottom-right {
    content: "Page " counter(page) " / " counter(pages);
    font-size: 8pt;
  }
}

/* 6. Ruptures de page. */
tr,
li,
fieldset,
[data-impression="bloc"] {
  break-inside: avoid;
}
h1,
h2,
legend {
  break-after: avoid;
}
[data-impression="signature"] {
  break-inside: avoid;
}

/* 7. Badges d'état lisibles sans couleur.
      La forme du filet et le symbole portent l'information ;
      la couleur n'était qu'un renfort. */
[data-etat] {
  border: 1px solid #000 !important;
  background: #fff !important;
  color: #000 !important;
}
[data-etat="brouillon"] {
  border-style: dashed !important;
}
[data-etat="rejete"] {
  border-width: 2px !important;
}
[data-etat="valide"],
[data-etat="affiche"] {
  box-shadow: inset 0 -3px 0 #000 !important;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}

/* 8. Barres d'avancement en trames. */
[data-avancement] {
  border: 1px solid #000 !important;
  background: #fff !important;
}
[data-avancement="programme"] {
  background: #bbb !important;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}
[data-avancement="realise"] {
  background: #000 !important;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}

/* 9. Aucune animation à l'impression. */
*,
*::before,
*::after {
  animation: none !important;
  transition: none !important;
}
```

## 4.1 Réduction de mouvement

À placer en fin de `static/css/application.css`, après les directives Tailwind.

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.001ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.001ms !important;
    scroll-behavior: auto !important;
  }
}
```

---

# 5 — Règles de tenue

**Classes littérales.** Tailwind analyse le texte source. Une classe assemblée
dans une vue, un filtre ou une balise de gabarit n'est jamais générée. Tout état
conditionnel s'écrit en branches `{% if %}` portant chacune son jeu complet.

**Aucune ressource distante.** Ni police, ni icône, ni feuille de style, ni
script chargé depuis un réseau. Le poste de déploiement est isolé.

**Accessibilité.** Contraste minimum 4,5:1 sur le texte. Navigation complète au
clavier. Focus visible par `focus-visible:outline focus-visible:outline-2
focus-visible:outline-offset-2 focus-visible:outline-marine-700`. `scope` sur
chaque en-tête de tableau, `aria-sort` sur les colonnes triables, `aria-label`
sur tout bouton réduit à une icône.

**Vocabulaire.** Libellés en français, terminologie du centre : brigade, séance,
référentiel, progression, créneau, matière, stagiaire, instructeur, salle
attitrée, AD/GROUPEMENT.

**Interdits.** Dégradés, verre dépoli, angles au-delà de 2 px, ombres hors des
trois superpositions admises, blocs centrés à grande respiration, émojis,
tuiles à padding uniforme, Inter.
