# Brief — bibliothèque de composants et charte graphique

*À remettre à Claude Design, avec les cinq wireframes rendus en PNG.*

---

## Contexte

Application web de gestion des activités de formation d'un centre d'instruction
militaire au Maroc. Utilisateurs : quatre cellules administratives et une
direction. Usage quotidien, postes fixes, réseau interne sans accès Internet.

L'interface remplace des feuilles imprimées denses : quinze lignes de groupes sur
quatre colonnes horaires, chaque case portant six informations. La densité n'est
pas un défaut à corriger, c'est le besoin.

**Registre attendu :** administration militaire. Sobre, précis, hiérarchisé,
imprimable. Une interface qui inspire confiance à un colonel et qui se lit en
diagonale par un chef de cellule pressé.

---

## Ce qu'il faut éviter — lire avant de commencer

L'esthétique par défaut des interfaces générées est reconnaissable et ne convient
pas ici. Écartez explicitement :

- les dégradés violets, indigo ou multicolores, sur les fonds comme sur les textes
- le verre dépoli, le flou d'arrière-plan, les cartes flottantes translucides
- les angles très arrondis appliqués partout, qui donnent un aspect jouet
- les ombres portées douces et généralisées
- les grandes zones vides centrées, les titres démesurés, les accroches marketing
- les émojis en guise d'icônes
- les cartes uniformes à padding constant qui transforment tout en tuiles
- Inter comme unique famille typographique, choix par défaut immédiatement lisible

**Références de registre**, à titre d'intention : un bulletin officiel bien
composé, un tableau de bord d'infrastructure ferroviaire, une application de
gestion bancaire professionnelle. Pas une page d'accueil de startup.

---

## Direction artistique

### Palette

Sobre, tirée des documents existants du centre.

| Rôle | Valeur | Usage |
|---|---|---|
| Marine profond | `#1F3864` | En-têtes de tableau, barre de navigation, titres |
| Marine clair | `#2E4F8F` | Survol, liens, accents |
| Encre | `#1A1D23` | Texte principal |
| Gris de lecture | `#4A4F58` | Texte secondaire, libellés |
| Gris de trait | `#C9CFD8` | Bordures, filets, séparateurs |
| Fond de page | `#F7F8FA` | Arrière-plan général |
| Fond de bloc | `#FFFFFF` | Tableaux, formulaires |
| Bande alternée | `#F2F5F9` | Une ligne sur deux |
| Vert conforme | `#0F6E56` | Conformité, validation, réalisé |
| Ambre attention | `#B07000` | Avertissement, seuil dépassé, en attente |
| Rouge écart | `#B03030` | Erreur, rejet, non exécuté |
| Sable document | `#FBF8F1` | Encadrés d'information, zones imprimables |

Les couleurs d'état ne servent **jamais** de décoration. Un aplat vert signifie
qu'une chose est conforme, pas qu'elle est jolie.

### Typographie

Deux familles, toutes deux à héberger localement — aucune police distante.

**Titres et en-têtes de tableau** : une grotesque à caractère, avec une vraie
présence — Barlow, Archivo ou Public Sans. Pas Inter.

**Texte courant et données** : la même famille en graisse normale, ou une
compagne à forte lisibilité en petit corps.

**Chiffres tabulaires obligatoires** dans les tableaux : les colonnes de volumes
horaires et de fractions de progression doivent s'aligner verticalement.

Échelle resserrée. Le corps de base est petit — 13 à 14 pixels — parce que la
densité prime. Les titres ne dépassent pas 24 pixels.

### Formes et espacement

Rayon d'angle **2 pixels**, jamais davantage, sauf sur les badges pleinement
arrondis.

Les blocs sont délimités par des **filets d'un pixel**, pas par des ombres. Une
seule ombre est admise, discrète, sur les éléments qui se superposent réellement :
menus déroulants, boîtes de dialogue, notifications.

Échelle d'espacement en multiples de 4 pixels. Dans les tableaux, la hauteur de
ligne est compacte : 32 à 36 pixels.

Grille de page à 12 colonnes, contenu aligné à gauche. Aucun centrage de bloc de
contenu.

---

## Iconographie

Icônes de trait, épaisseur 1,5 pixel, jeu unique et cohérent — style Lucide ou
Phosphor en variante *regular*. **Fichiers SVG locaux**, jamais une bibliothèque
chargée depuis un réseau.

Une icône accompagne toujours un mot ; elle ne le remplace pas, sauf dans les
boutons d'action de ligne où l'infobulle prend le relais.

**Icônes attendues**, à nommer explicitement dans la livraison : calendrier,
horloge, grille horaire, salle, groupe de personnes, instructeur, matière,
document, procès-verbal, signature, validation, rejet, avertissement,
information, recherche, filtre, tri, export, impression, ajout, modification,
suppression, verrou, historique, alerte, statistique.

---

## Animations

Fonctionnelles uniquement. Chacune répond à la question « qu'est-ce qui vient de
changer ». Aucune n'est décorative.

| Effet | Durée | Où |
|---|---|---|
| Surbrillance de ligne au survol | 120 ms | Tableaux |
| Transition de badge d'état | 180 ms | Passage brouillon → soumis → validé |
| Apparition d'une notification | 200 ms, glissement depuis le haut | Confirmation d'action |
| Ouverture d'un menu ou d'une boîte de dialogue | 150 ms | Superpositions |
| Squelette de chargement, pulsation lente | 1,2 s en boucle | Tableaux en attente de données |
| Remplissage d'une barre de progression | 400 ms | Volume prescrit / réalisé |
| Secousse brève sur champ invalide | 300 ms | Formulaires |
| Dépliement d'une ligne de détail | 200 ms | Tableau de suivi |

**Interdits :** apparition au défilement, parallaxe, compteurs animés,
transitions de page, effets d'écriture.

Respecter `prefers-reduced-motion` : toutes les animations se désactivent.

---

## Composants à produire

Chacun avec ses états — normal, survol, focus clavier, désactivé, chargement,
erreur — et avec une variante compacte lorsque la densité l'exige.

### Structure

1. Ossature d'application : barre supérieure, navigation principale, zone de
   contenu, pied
2. Barre supérieure : nom de l'application, profil et cellule de l'utilisateur,
   **indicateur de grille horaire active**, déconnexion
3. Navigation principale à six entrées : Référentiel, Sessions, Ressources,
   Planification, Évaluations, Suivi
4. Fil d'Ariane
5. En-tête de page : titre, sous-titre, groupe d'actions à droite
6. Bandeau d'état contextuel — l'état du programme, l'auteur et la date de
   soumission
7. Pied de page discret : version, environnement

### Tableaux et données

8. **Tableau dense** — le composant central. En-tête marine sur texte blanc,
   lignes alternées, filets fins, tri par colonne, colonne d'actions à droite,
   en-tête figé au défilement
9. **Grille de programme hebdomadaire** — tableau croisé, lignes par groupe
   regroupées en blocs de type de formation, colonnes par créneau horaire
10. **Cellule de séance** — six informations dans une case étroite : matière,
    instructeur avec grade, fraction de progression, code de salle. Variante
    séance regroupée, variante verrouillée, variante vide portant la mention
    **AD/GROUPEMENT** en gris
11. Barre de filtres : sélecteurs, plage de dates, recherche, réinitialisation
12. Pagination avec compteur d'éléments
13. État vide, avec explication et action suggérée
14. Squelette de chargement pour tableau
15. Ligne de détail dépliable
16. **Matrice croisée** — instructeurs en lignes, matières en colonnes, cases à
    cocher. Sert aussi aux cibles de période

### Formulaires

17. Champ texte, avec libellé, aide et message d'erreur
18. Champ numérique avec unité accolée — « 40 h », « 3 pts »
19. Sélecteur de date, sélecteur d'heure, sélecteur de plage horaire
20. Liste déroulante simple, avec recherche intégrée
21. **Liste déroulante à sélection multiple** avec jetons — cibles d'une période :
    plusieurs sessions et plusieurs brigades
22. Zone de texte pour les motifs — rejet, non-exécution, avenant
23. Cases à cocher, boutons radio, interrupteur
24. Groupe de champs avec légende
25. Formulaire à deux colonnes, actions alignées à droite en pied
26. Zone de dépôt de fichier, avec compte rendu d'analyse avant validation :
    lignes valides, lignes en anomalie avec leur numéro

### Restitution et états

27. **Badges d'état du programme** : brouillon, soumis, validé, rejeté, affiché.
    Cinq traitements visuels distincts, lisibles en noir et blanc à l'impression
28. Badges de priorité : Must, Should, Could
29. Badge de type d'évaluation : formative, certificative
30. Encadrés : information, avertissement, erreur, succès. Filet à gauche, fond
    très clair, icône, titre, corps
31. Notification transitoire
32. Boîte de dialogue de confirmation, avec variante destructive
33. **Indicateur d'écart** — conforme, en cours, retard avec pourcentage,
    dépassement, achevée, non commencée
34. Barre de progression prescrit / programmé / réalisé, en trois segments
    superposés
35. Bloc de statistique : valeur, libellé, variation
36. **Carte de créneau non pourvu** — matière recherchée et motif détaillé :
    instructeurs qualifiés et cause d'indisponibilité de chacun
37. **Liste de remplaçants classés** — rang, nom, charge de la semaine,
    antériorité, statut, et mention visible du critère de classement
38. **Chronologie des avenants** — modifications successives d'une séance après
    affichage, avec date, motif et auteur

### Actions

39. Boutons : principal, secondaire, discret, destructeur. Avec et sans icône
40. Bouton d'action de ligne, icône seule avec infobulle
41. Menu déroulant d'actions
42. Onglets
43. Groupe de boutons segmenté

### Impression

44. **En-tête de document officiel** : intitulé, date, lieu, nature du document
45. **Pied de document** : « À Kénitra le … », grade, nom, fonction, zone de
    signature manuscrite et de cachet
46. **Feuille de style d'impression** — orientation paysage pour la progression
    d'instruction, en-tête répété sur chaque page, numérotation, masquage de la
    navigation et des actions

---

## Écrans de démonstration

Cinq, assemblés à partir des composants, d'après les wireframes fournis.

1. **Génération du programme hebdomadaire** — grille croisée du centre entier,
   panneau des créneaux non pourvus, barre d'actions
2. **Composition du référentiel** — tableau éditable à cinq attributs, bandeau
   d'écart entre déclaré et calculé
3. **Validation d'un programme** — écart au référentiel, décision, rappel du
   circuit de signature
4. **Traitement d'une indisponibilité** — séances impactées, remplaçants classés,
   confirmation d'avenant
5. **Suivi prescrit et réalisé** — tableau des trois volumes, onglet de
   progression réalisée hebdomadaire

Chaque écran en **deux versions** : à l'écran, et à l'impression pour ceux qui
sont imprimés.

---

## Contraintes techniques impératives

**Classes utilitaires Tailwind uniquement.** Le CSS est précompilé sur le poste
de développement : toute règle écrite à la main hors du fichier de configuration
ne sera pas générée et disparaîtra. Les couleurs et polices personnalisées
passent par un `tailwind.config.js` que vous fournirez.

**Aucune ressource distante.** Ni police, ni icône, ni script, ni feuille de
style chargée depuis un réseau. Le poste de déploiement est isolé. Les polices
sont fournies en fichiers, les icônes en SVG inline.

**Libellés en français**, avec la terminologie du centre : brigade, séance,
référentiel, progression, créneau, matière, stagiaire, instructeur, salle
attitrée, AD/GROUPEMENT.

**Accessibilité** : contraste minimum 4,5:1 sur le texte, navigation complète au
clavier, focus visible et net, tableaux avec en-têtes correctement associés.

**Aucune donnée réelle.** Les noms, matricules et intitulés des exemples sont
fictifs.

---

## Livrables attendus

1. `tailwind.config.js` — palette, familles typographiques, échelle d'espacement,
   rayons
2. `composants.html` — page unique présentant les quarante-six composants avec
   leurs états, chacun accompagné de son extrait de balisage
3. `ecrans/` — les cinq écrans de démonstration
4. `impression.css` — la feuille de style d'impression
5. `icones/` — les SVG, nommés en français
6. `CHARTE.md` — une page : palette, typographie, règles d'espacement, quand
   employer chaque couleur d'état, ce qu'il ne faut pas faire

Le tout se déposera dans `docs/charte/` du dépôt, et servira de référence unique
au développement.
