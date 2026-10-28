# Prompt 52 — Lancer l'application de recette dans le conteneur (contrôles PDF)

**Nature.** Outillage de recette uniquement. **Aucun fichier sous `app/` n'est modifié**, sauf, si c'est indispensable, un module de réglages de recette.

**Contexte.** Les cahiers RECETTE-02, 03 et 05 contiennent des contrôles marqués **[PDF]** : génération des procès-verbaux, PDF de la progression réalisée. Le recetteur les joue **par l'interface**, dans un navigateur. Or WeasyPrint ne s'exécute pas sous Windows (P-44) : `runserver` sous Windows ne peut pas produire ces documents. Jusqu'ici, les PDF n'ont été vérifiés que par `pytest -m pdf` dans le conteneur, jamais par un humain dans un navigateur.

Ajoute les cahiers fournis (`RECETTE-01` à `RECETTE-05`) dans `docs/recette/` avant de commencer.

## À faire

1. Écris `outils/recette/lancer_recette_conteneur.ps1`, avec un paramètre `-Base {recette|volume}`. Il lance l'application **dans l'image `python:3.14-slim-bookworm` déjà utilisée pour `pytest -m pdf`**, sur le réseau Docker `developpement_default`, hôte `base`. Il pointe sur `pfe_cit_recette` (réglages `config.settings.recette`) ou sur `pfe_cit_volume` (`config.settings.volume`), **la base déjà chargée**, sans rien recharger. Il publie le port vers le poste : par exemple `http://localhost:8001`, pour ne jamais être confondu avec le `runserver` Windows sur le 8000.
2. Il refuse de démarrer si un `runserver` Windows est déjà ouvert **sur la même base**, ou il l'annonce clairement : deux serveurs sur la même base pendant une recette, c'est deux sources de vérité.
3. Les fichiers statiques (Tailwind précompilé) doivent être servis : le recetteur doit voir exactement les mêmes écrans que sous Windows.
4. **Vérifie toi-même, de bout en bout, par le client de test ou un navigateur sans interface dans le conteneur**, sur `pfe_cit_recette` remise à zéro en `complet` :
   - générer le procès-verbal de E1 ;
   - éditer la progression réalisée de W-1 et télécharger son PDF.

   Les deux PDF doivent s'ouvrir et contenir les données attendues.
5. Ajoute une section « Lancer la recette dans le conteneur » à `docs/recette/JEUX-DE-DONNEES-PHASE-6.md` : la commande, l'adresse, l'arrêt du conteneur, et le rappel que la base est partagée avec le `runserver` Windows.
6. Ajoute à `JEUX-DE-DONNEES-PHASE-6.md` le **mot de passe des comptes `v_*`** du jeu volumineux : RECETTE-05 en a besoin et le document ne le donne pas.
7. Vérifie une incohérence et rapporte-la sans rien corriger : le document décrit W-2 comme « pleine sur les **six** jours ouvrables ». La grille Ordinaire n'a aucun créneau le samedi (R2-P12-04). Y a-t-il réellement des séances le samedi dans W-2, W-1 ou W0 du jeu `complet` ? Si oui, d'où viennent-elles ? Si non, corrige seulement le libellé du document.
8. Un commit, sans déplacer l'étiquette `recette-phase-6` : ce sont des outils et de la documentation. Une ligne dans `heures-phase-6.md`.

## Rendu attendu

- La commande exacte de lancement et l'adresse.
- Le résultat de la vérification du point 4 (deux PDF produits, oui ou non).
- La réponse au point 7.
- Le mot de passe des comptes `v_*`, s'il figure déjà dans le dépôt.
