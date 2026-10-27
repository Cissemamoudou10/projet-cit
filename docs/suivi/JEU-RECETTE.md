# Jeu de données de recette — Sprint 2

Prompt 34. Chargé par `python manage.py charger_jeu_recette`. Les treize
fichiers d'import de `docs/recette/fichiers-import/` sont **figés** : ni le
chargement, ni les tests ne les réécrivent (P-40). Seule l'option explicite
`python manage.py charger_jeu_recette --regenerer-fichiers-import` les régénère
— avec un avertissement, et un diff à relire avant tout commit. Un test de
cohérence compare le générateur à ces fichiers suivis : s'il change, il échoue,
et l'on décide alors de régénérer. Code : `app/evaluations/jeu_recette/` et
`app/evaluations/management/commands/charger_jeu_recette.py` — déplacé de
`planification` lors du prompt 51, voir docs/suivi/DECISIONS.md, D-297.
L'état `complet` (Prompt 51, Temps 2) ajoute une option `--etat complet`
à cette même commande ; voir `docs/recette/JEUX-DE-DONNEES-PHASE-6.md`.

## Étiquette de recette du sprint 2

La recette manuelle du sprint 2 se joue sur l'étiquette `recette-sprint-2`, posée sur le commit de clôture du sprint 2 (`e05a1c3`, « Cloture le sprint 2 »). Le développement continue sur `master` sans la perturber (prompt 41, § 0.2) : pour rejouer la recette, `git checkout recette-sprint-2`.

## Base de données dédiée à la recette

Ce jeu ne doit jamais coexister avec le jeu de démonstration (garde-fou, voir
plus bas) : il lui faut sa **propre base**, distincte de `pfe_cit` (base de
développement habituelle). Créée une fois pour la recette du sprint 2 :

```sql
-- Dans le conteneur pfe_cit_base, avec le rôle pfe_cit_migration
CREATE DATABASE pfe_cit_recette OWNER pfe_cit_migration;
GRANT USAGE ON SCHEMA public TO pfe_cit_app;
ALTER DEFAULT PRIVILEGES FOR ROLE pfe_cit_migration IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO pfe_cit_app;
ALTER DEFAULT PRIVILEGES FOR ROLE pfe_cit_migration IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO pfe_cit_app;
```

Puis `migrate` avec le rôle `pfe_cit_migration` (la révocation RG-27 est déjà
portée par la migration `administration.0007`, rejouée automatiquement).

**Pour que l'application (et donc la connexion par l'interface, comme l'exige
le § 2.1 du cahier) pointe sur cette base**, utilisez le module de réglages
dédié `config.settings.recette` (`app/config/settings/recette.py`) — il fixe
la base en dur (`pfe_cit_recette`), pas de variable d'environnement à
retenir ni à oublier :

```powershell
python app\manage.py runserver --settings=config.settings.recette
```

Un essai par variable d'environnement (`BASE_NOM`) a été tenté d'abord et
écarté : elle ne persiste pas d'un terminal à l'autre, et la rendre
permanente aurait fait pointer `pytest` (qui lit la même variable,
`config/settings/test.py`) sur une base de test différente sans que rien ne
le signale. `--settings=config.settings.recette` est explicite à chaque
invocation et n'affecte aucun autre outil. Sans lui, Django retombe sur
`pfe_cit` (la base de développement habituelle, où vit le jeu de
démonstration — `adm.demo` s'y connecte alors avec succès, `u_adm` échoue,
puisqu'il n'existe que dans `pfe_cit_recette`). Utilisez le même drapeau pour
toute commande de recette (`shell`, `charger_jeu_recette --verifier`…).

**Distinct du jeu de démonstration** (`ressources.jeu_demonstration`, sprint 1,
D-163) : celui-ci montre le système, celui-ci le recette. Son contenu
reprend **exactement** le § 4.2 du `docs/suivi/CAHIER-RECETTE-SPRINT-2.md` —
un objet de plus ou de moins y fausserait un contrôle. Toutes les données
sont fictives.

**Mot de passe commun des cinq comptes** : `Transmissions#2026` — aucun
changement exigé à la première connexion (à la différence du jeu de
démonstration, qui le démontre exprès).

## Garde-fous — pourquoi la commande peut refuser de s'exécuter

Deux gardes s'exécutent avant toute écriture (`garde.py`) :

1. **Réglages de production** — refus si `DJANGO_SETTINGS_MODULE` contient
   « production ». Ce jeu crée des comptes à mot de passe COMMUN et CONNU :
   inexécutable ailleurs qu'en développement.
2. **Données étrangères** — refus si la base contient un compte que ce jeu
   n'a pas créé lui-même (les cinq comptes du § 4.1, plus son propre compte
   bootstrap, jamais celui du jeu de démonstration). **Interprétation
   retenue, au sens strict** : aucune coexistence avec le jeu de
   démonstration n'est tolérée, même si celui-ci n'a rien à voir avec la
   recette — un jeu qui pose des mots de passe connus doit tourner sur un
   environnement dédié. *Point à confirmer avec le binôme si la lecture
   souhaitée était plus permissive.*

Concrètement : sur une base où `charger_jeu_demonstration` a déjà tourné,
`charger_jeu_recette` refuse avec un message nommant les comptes étrangers
trouvés. Repartir d'une base vierge (ou d'un conteneur PostgreSQL dédié à la
recette) avant de charger ce jeu.

## Ce qui est chargé (§ 2 / § 4.2 du cahier)

| Objet | Contenu | État particulier |
|---|---|---|
| Comptes | `u_ped`, `u_plan`, `u_exa`, `u_df`, `u_adm` | — |
| Types de formation | `TF1` Formation initiale · `TF2` Formation de spécialité | — |
| Formations | `F1` Exploitant radio · `F2` Chef de poste · `F3` Formation archivée · `F4` Formation sans référentiel | `F3` archivée, `F4` référentiel vide |
| Matières | `M1` (salle attitrée) · `M2` (lieu partagé) · `M3` (sans lieu) · `M4` (salle attitrée) · `M5` (salle attitrée) | — |
| Référentiel `F1` | M1 = 20 h, M2 = 10 h, M3 = 10 h | — |
| Référentiel `F2` | M4 = 10 h, M5 = 10 h | M4 prérequis de M5 |
| Référentiel `F3` | M1 = 10 h | — |
| Instructeurs | `I1` (M1, M2, M3) · `I2` (M1) · `I3` (M2) · `I4` (M1) · `I5` (M4, M5) | `I4` archivé |
| Lieux | `L1` (attitrée, cap. 20) · `L2` (attitrée, cap. 15) · `L4` (partagé **simultané**, cap. 30) · `L5` (partagé **séquentiel**, cap. 30) · `L6` (attitrée, archivé) | `L6` archivé |

## Ce qui n'est PAS chargé, et pourquoi

- **`L3`** (§ 4.2 : « salle attitrée, capacité non renseignée ») —
  **impossible à produire**. `ressources.models.Lieu.capacite` est un
  `PositiveIntegerField` obligatoire, contrainte de base
  `ck_lieu_capacite_positive` en renfort. Ni le modèle ni `ServiceLieu` ne
  permettent une capacité vide. `--verifier` rapporte `L3` comme absent avec
  ce motif — jamais un défaut silencieux, jamais une valeur approchante qui
  masquerait l'écart (0 ou 1, par exemple).
- **Les deux grilles horaires** (Ordinaire active, Ramadan inactive) — livrées
  par `initialiser_grilles_horaires` (US-PLAN-12), pas par ce jeu. `--verifier`
  en confirme seulement la présence et les créneaux exacts (R2-P12-02/03).
  Chargez-les séparément avant le § 7 du cahier si ce n'est pas déjà fait.
- **Tout objet du périmètre sprint 2** — sessions, brigades, stagiaires,
  périodes de calendrier, programmes hebdomadaires. Le cahier (§ 4.3) est
  explicite : ces objets sont créés **par les contrôles eux-mêmes** ; les
  précharger fausserait ce qui est recetté.

## Options

| Option | Effet |
|---|---|
| *(aucune)* | Charge le jeu si absent ; ne fait rien si déjà présent (idempotent, sentinelle : le compte `u_adm`) |
| `--reinitialiser` | Vide les données propres à ce jeu (référentiel, instructeurs, lieux, formation de pagination) et recharge tout, dans une seule transaction. **Ne touche jamais aux comptes ni au journal** (RG-27) : les cinq comptes ont journalisé leur propre création, un privilège `UPDATE`/`DELETE` que le rôle applicatif n'a plus sur `administration_entree_journal` — les supprimer ferait échouer la mise à `NULL` que Django tenterait sur ces entrées. |
| `--verifier` | Ne crée rien : rapport de lecture seule (§ 5, voir ci-dessous) |
| `--pagination` | Ajoute 25 sessions sur une formation dédiée `F5`, pour R2-SES01-17 **seule** — ne figure dans aucun autre contrôle. Combinable avec un chargement ou `--reinitialiser`. |

### Limite connue de `--reinitialiser`

`organisation.models.Session.formation` est en `on_delete=PROTECT` (règle par
défaut du projet). Si un contrôle du cahier a déjà ouvert une session sur
`F1`/`F2`/`F4` — précisément ce que le § 5 fait faire — `--reinitialiser`
échoue à supprimer ces formations : Django lève `ProtectedError`, retraduite
en `CommandError` nommant les sessions en cause. **Ce n'est pas contourné** :
supprimez d'abord ces sessions (et leurs brigades/stagiaires) depuis les
écrans de l'application, puis relancez `--reinitialiser`. Les sessions du
sprint 2 elles-mêmes ne sont jamais supprimées par cette commande — seule la
formation qui les porte peut bloquer sa propre suppression.

### Revenir à un état propre en cours de journée de recette

1. Si aucune session n'a encore été ouverte sur `F1`/`F2`/`F4` :
   `python manage.py charger_jeu_recette --reinitialiser`.
2. Sinon : supprimer les sessions concernées depuis l'écran Sessions (avec
   `u_ped`), puis relancer `--reinitialiser`.
3. `--verifier` à tout moment pour connaître l'état réel de la base avant de
   trancher — il liste, sans jamais les supprimer, les objets du sprint 2
   déjà présents (sessions hors pagination, brigades, stagiaires, périodes,
   programmes).

## `--verifier` — rapport de lecture seule (§ 5)

Contrôle, sans rien créer ni modifier :

- chaque objet du § 2 est présent et dans l'état attendu (`F3` archivée,
  `F4` sans référentiel, `L3` absent avec son motif, `I4` archivé, `L6`
  archivé, `M4` prérequis de `M5`, `L4`/`L5` avec leur mode de partage) ;
- les deux grilles horaires sont présentes, l'Ordinaire active, avec les
  créneaux exacts de R2-P12-02/03 ;
- les cinq comptes existent avec leur groupe de profil ;
- les treize fichiers d'import et `00-LISEZ-MOI.md` sont présents ;
- les objets du **sprint 2** déjà en base (sessions hors pagination,
  brigades, stagiaires, périodes, programmes) — listés, jamais supprimés.

Rapport observé sur une base fraîche, jeu chargé puis grilles horaires
initialisées : **73/73 contrôles conformes**.

## Fichiers d'import de test (§ 3, US-SES-05)

Figés dans `docs/recette/fichiers-import/` ; régénérés seulement par
`charger_jeu_recette --regenerer-fichiers-import` (P-40). Table complète et
scénario de chaque fichier dans `docs/recette/fichiers-import/00-LISEZ-MOI.md`.
Résumé :

| Fichier | Sert |
|---|---|
| `01-valide-10.csv` | R2-SES05-08/09 — 10 lignes valides |
| `02-valide-5.xlsx` | R2-SES05-10 — XLSX, 5 lignes valides |
| `03-valide-45-colonnes-permutees.csv` | R2-SES05-13/14 — séparateur virgule, colonnes permutées, volume |
| `04-encodage-utf8-bom.csv` | R2-SES05-11 |
| `05-encodage-cp1252.csv` | R2-SES05-12 — mêmes identités que `04` |
| `06-valide-colonnes-permutees.csv` | R2-SES05-14 — permutation distincte de `03` |
| `07-valide-entetes-majuscules.csv` | R2-SES05-14 — reconnaissance d'en-tête insensible à la casse |
| `08-colonne-matricule-absente.csv` | R2-SES05-15 — refus global |
| `09-matricule-manquant-ligne-12.csv` | R2-SES05-16 — anomalie exactement à la ligne 12 |
| `10-doublon-dans-le-fichier.csv` | R2-SES05-17 |
| `11-doublon-en-base.csv` | R2-SES05-18 — **en deux temps**, voir le LISEZ-MOI |
| `12-un-champ-vide-par-ligne.csv` | R2-SES05-19 — chaque ligne en anomalie |
| `13-faux-fichier.csv` | R2-SES05-20 — PDF renommé en `.csv` |

Chaque générateur réutilise `organisation.import_stagiaires.constantes.
ENTETES_MODELE` — aucune divergence possible entre le fichier généré et ce
que le parseur réel attend. Vérifié aussi par le test qui télécharge le
modèle vide et le réimporte (`generer_modele_xlsx`, R2-SES05-07 côté
application) : aucun écart trouvé entre le modèle téléchargeable et
`ENTETES_MODELE`.

## Ce qui reste à faire tourner manuellement

Ce jeu couvre le § 4 du cahier. Tout ce qui suit reste à la charge du
recetteur, par l'interface, comme le § 2.1 du cahier l'exige (« jamais par un
appel de service ») : §§ 5 à 10 du cahier de recette.
