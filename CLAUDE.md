# Système de gestion des activités de formation — CIT

Projet de fin d'études. Application web Django pour la Direction de Formation du
Centre d'Instruction des Transmissions. Binôme : Lt Cissé, Lt Niangaly.

## Commandes

Le projet Django est dans `app/`. Les tests d'architecture sont à la racine.

```bash
docker compose up -d                       # base PostgreSQL de développement
.venv\Scripts\activate                    # Windows
python app\manage.py runserver
python app\manage.py makemigrations && python app\manage.py migrate
pytest                                     # suite complète
pytest tests/architecture -q               # après chaque série d'éditions
pytest chemin/test_x.py::test_y            # un seul test — à privilégier
python -m pytest app/referentiel -q        # les tests d'une application
```

## Cinq règles non négociables

**IMPORTANT — aucune dépendance nouvelle sans mon accord explicite.** Le poste de
déploiement est un réseau militaire isolé, sans accès Internet à l'exécution
(BNF-06). Toute bibliothèque doit être téléchargée et validée avant la coupure.
Ne lance jamais `pip install` de ta propre initiative : propose, j'arbitre.

**Aucune règle métier dans les vues, les formulaires ou les gabarits.** Toute la
logique passe par la couche services. Une règle qui ne vit que dans un formulaire
est contournée dès qu'une donnée entre par un import ou par l'API.

**Aucun attribut dérivé n'est stocké.** Neuf grandeurs se calculent et ne doivent
jamais devenir des colonnes — volume restant, écart prescrit/programmé, charge
d'un instructeur notamment. Voir la règle `modeles.md`.

**Aucune donnée réelle du CIT dans le dépôt.** Pas de liste nominative, pas de
sujet d'examen, pas de nom d'instructeur. Les jeux d'essai sont fictifs. Un
fichier poussé une fois demeure dans l'historique même après suppression.

**Le code est en français.** Modèles, champs, méthodes, tables, colonnes,
commentaires, messages. La terminologie est celle du CIT (BNF-08) : brigade,
séance, référentiel, progression, créneau. Voir le skill `glossaire-cit`.

## Méthode de travail

Une story à la fois. Avant d'implémenter : lire le besoin et les critères
d'acceptation que je te donne, poser tes questions, proposer un plan. Je valide,
tu implantes.

Écris les tests au fil du développement, pas à la fin. Chaque critère
d'acceptation donne au moins un test.

Avant de considérer une story terminée : lance `pytest`, montre la sortie, et
fais relire le diff par le sous-agent `relecteur-conception`.

`/clear` entre deux stories sans rapport.

## Suivi

Ne charge ces fichiers que lorsque tu en as besoin — ils grossissent.

- `docs/suivi/sprint-N.md` — coche la story terminée, à chaque fin de story
- `docs/suivi/AVANCEMENT.md` — mets à jour le récapitulatif en fin de sprint
- `docs/suivi/PROBLEMES.md` — consigne tout blocage et sa résolution
- `docs/suivi/DECISIONS.md` — **toute** décision qui s'écarte de la conception,
  avec son impact sur les livrables. Sans cette trace, le mémoire ne
  correspondra plus au code

## Qualité du code

Fichiers sous 400 lignes, fonctions sous 40. Transactions atomiques sur toute
écriture multi-tables. Aucune requête dans une boucle. Aucune valeur littérale
sans nom. Exceptions métier typées. La règle `python.md` détaille chaque point,
et deux tests d'architecture en vérifient les limites.

## Charte graphique

Les composants d'interface sont définis dans `docs/charte/`. **Ne réinvente pas
un composant qui existe** : reprends les classes Tailwind du livre de composants.
Voir la règle `gabarits.md`.

## Conception de référence

Les livrables sont dans `docs/conception/`. Ne les lis **pas** systématiquement :
le livrable des cas d'utilisation fait à lui seul plus de quatre-vingts pages.
Je te donnerai la fiche utile dans le prompt de chaque story. Consulte-les de
ta propre initiative seulement si une règle métier te manque, et par recherche
ciblée plutôt que par lecture intégrale.

Le diagramme de classes fait foi : `docs/conception/13-diagramme-classes.md`.

## Dépôt

Branche par story, nommée `us-xxx-nn`. Message de commit en français, à
l'impératif, mentionnant le code de la story. Pas de fusion sans relecture.

## Compactage

Lors d'un compactage, conserve la story en cours, les fichiers modifiés et les
commandes de test.
