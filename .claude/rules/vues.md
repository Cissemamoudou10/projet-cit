---
paths:
  - "**/views.py"
  - "**/views/**.py"
  - "**/forms.py"
  - "**/urls.py"
  - "**/serializers.py"
---

# Couche présentation

**Aucune règle métier ici.** Une vue orchestre : elle lit la requête, appelle un
service, met en forme la réponse. Rien d'autre.

Un contrôle en formulaire est autorisé — il donne un retour immédiat — mais il
**double** un contrôle porté en service, il ne le remplace jamais. Une règle qui
ne vit que dans un formulaire est contournée dès qu'une donnée entre par un
import, par l'API ou par une commande d'administration.

## Habilitations

Le contrôle d'accès est appliqué en couche services, non vue par vue. Les droits
reposent sur les groupes et permissions Django : l'administrateur les ajuste sans
modification du code. Cinq profils préconfigurés — pédagogique, planification,
examens, Direction de Formation, administrateur.

## Messages

En français, terminologie du CIT. Un message d'erreur indique **l'action
corrective attendue**, pas seulement le refus.

Mauvais : « Aucun instructeur qualifié disponible. »
Bon : « Aucun instructeur qualifié disponible pour Matériel radio le lundi
08:00–09:45 : Lt Ziani en mission du 24/04 au 09/05, Cne Kibour affecté à BCM1
sur le même créneau. »

## Interface

Tailwind CSS **précompilé** — Node est absent du poste cible. Le CSS est généré
sur le poste de développement et versionné comme fichier statique. Ne référence
jamais un CDN.

Pagination et recherche dès qu'une liste peut dépasser vingt éléments.
Confirmation explicite avant toute action irréversible.

## API

Consultation seule, périmètre limité au référentiel, aux sessions et au programme
affiché. Notes et sujets exclus. Priorité Should — c'est le premier candidat à
l'abandon en cas de dérive.
