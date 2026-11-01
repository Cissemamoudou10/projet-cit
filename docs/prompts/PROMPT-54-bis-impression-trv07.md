# Prompt 54 bis — Impression : TRV-07 toujours non conforme au rejeu

**Contexte.** Rejeu du 01/11 sur `recette-phase-6-c2`. Sept contrôles corrigés par le prompt 54 sont conformes. **R00B-TRV-07 reste non conforme**, constaté dans **Chrome et Edge**, après un rechargement complet (Ctrl+Maj+R), avec `runserver --settings=config.settings.recette` :
- des **boutons** (Modifier, etc.) apparaissent encore sur l'aperçu d'impression ;
- la **liste des instructeurs** s'imprime toujours en **portrait**.

Les tests du prompt 54 vérifiaient les gabarits **sans navigateur** : ils ne pouvaient pas voir ce défaut. Ce prompt ne traite que TRV-07.

---

## Temps 0 — Relevé d'heure

Une ligne dans `docs/suivi/heures-phase-6.md`.

## Temps 1 — Reproduire dans un vrai navigateur, avant toute correction

Chromium et Playwright sont installés. Sur une base de test chargée à l'état `socle-planif`, avec les réglages **`recette`** (ceux du recetteur, pas ceux des tests), rends les deux pages en média impression :
- la fiche de composition de S0 ;
- la liste des instructeurs.

Pour chacune : `page.emulate_media(media="print")` + capture d'écran, puis `page.pdf(prefer_css_page_size=True)`. Relève dans le PDF : orientation (largeur > hauteur ?) et texte des boutons présents.

**Pas de correction avant d'avoir reproduit le défaut.** Si tu ne le reproduis pas, arrête-toi et dis-le.

## Temps 2 — Chercher la cause, dans cet ordre

1. **Feuille de style servie.** Vérifie ce que le navigateur reçoit réellement sous `config.settings.recette` : `DEBUG`, `STATIC_ROOT`, `collectstatic`, WhiteNoise ou manifeste éventuel. Une ancienne copie collectée expliquerait tout.
2. **Tailwind précompilé.** Si la correction utilise une classe Tailwind (`print:hidden` ou autre) absente du CSS précompilé, elle n'a aucun effet. Vérifie que chaque classe ou règle ajoutée par 1fd65f6 existe dans le fichier CSS effectivement servi.
3. **Règle `data-impression="masquer"`.** Vérifie qu'elle est bien chargée dans les deux pages et qu'elle n'est pas écrasée par une règle plus spécifique (par exemple `display:flex` sur le conteneur des boutons).
4. **Orientation.** Vérifie que la règle `@page { size: A4 landscape; }` de la liste des instructeurs est bien présente dans la page servie, et qu'elle ne s'applique qu'à cette page.

## Temps 3 — Corriger et figer

- Corrige la cause trouvée, sans modifier d'autre écran.
- Si la cause est la régénération du CSS précompilé, régénère-le et explique pourquoi le prompt 54 ne l'a pas fait.
- **Ajoute un test qui ouvre un vrai navigateur**, avec un marqueur dédié (par exemple `-m navigateur`), sur les deux pages : aucun texte de bouton dans le PDF ; liste des instructeurs en paysage. Dis comment le lancer sous Windows et en conteneur.
- Consigne la cause et la correction dans `PROBLEMES.md`, et la leçon sur les tests d'impression sans navigateur.

## Temps 4 — Contrôle, étiquette

1. Suite complète, **seule sur la machine** (P-51), plus `-m pdf` et le nouveau marqueur.
2. Commit, puis étiquette **`recette-phase-6-c3`**. Les étiquettes précédentes ne bougent pas.
3. Clôture la ligne d'heures.

## Temps 5 — Question sur le script de remise à zéro (lecture seule)

Le 01/11, `reinitialiser_base_recette.ps1` a refusé de continuer : « Connexions coupées : 0 ». Il restait une connexion du compte **`pfe_cit`**, ouverte par un explorateur de base de VS Code (adresse 172.23.0.1, état idle). Le recetteur l'a ensuite coupée **à la main** avec `select pg_terminate_backend(<pid>);` sous le compte `pfe_cit`.

Lis le script et explique pourquoi il n'a pas coupé cette connexion lui-même. **Ne le modifie pas** : propose la correction, on l'arbitrera.

## Rendu attendu

- Les captures ou relevés du Temps 1 (avant), puis après correction.
- La cause exacte.
- Le commit, l'étiquette, le nombre de tests.
- L'explication du Temps 5 et ta proposition.
