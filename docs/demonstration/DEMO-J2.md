# Guide de la démonstration J2 — Prompt 43

Jalon J2, samedi 10 octobre. Le fil unique du § A1 du prompt, joué de bout en
bout par cinq comptes. Chaque étape nomme le compte, l'écran, le geste, ce
que le jury doit voir, et la règle qu'elle illustre. Vérifié de bout en bout
par le cycle HTTP réel (`tests/scenarios/test_demonstration_j2.py`) — s'il
casse un jour sur une règle métier, c'est ce test qui le montrera avant la
salle.

## Avant la démonstration

**Base dédiée**, jamais celle du développement ni celle de la recette du
sprint 2 (`pfe_cit_recette` — § A3, ne pas la toucher). Créée une fois :

```sql
-- Dans le conteneur pfe_cit_base, avec le rôle pfe_cit_migration
CREATE DATABASE pfe_cit_demo_j2 OWNER pfe_cit_migration;
GRANT USAGE ON SCHEMA public TO pfe_cit_app;
ALTER DEFAULT PRIVILEGES FOR ROLE pfe_cit_migration IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO pfe_cit_app;
ALTER DEFAULT PRIVILEGES FOR ROLE pfe_cit_migration IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO pfe_cit_app;
```

Puis, une fois pour migrer (rôle `pfe_cit_migration` — la révocation RG-27
est rejouée automatiquement par `administration.0007`) :

```powershell
$env:BASE_UTILISATEUR="pfe_cit_migration"; $env:BASE_MOT_DE_PASSE="developpement_local_migration"
python app\manage.py migrate --settings=config.settings.demonstration
```

**À chaque répétition** (rejouable, remet la base à zéro — § A3) :

```powershell
python app\manage.py preparer_demonstration --settings=config.settings.demonstration
```

**Lancer le serveur** sur cette base, pendant la démonstration :

```powershell
python app\manage.py runserver --settings=config.settings.demonstration
```

**Les cinq comptes**, un par profil, mot de passe commun
`Transmissions-J2#2026` : `plan.j2` (Planification), `ped.j2`
(Pédagogique), `exa.j2` (Examens), `df.j2` (Direction de Formation),
`adm.j2` (Administrateur — non utilisé par le fil A1).

La semaine générée est **celle qui suit la date du jour**, calculée à
chaque préparation : aucune date en dur à vérifier avant de jouer.

## Le fil, étape par étape

| # | Compte | Écran | Geste | Ce que le jury doit voir | Règle illustrée |
|---|---|---|---|---|---|
| 1 | Planification | Lancement de la génération (`/planification/generer/`) | Choisir la semaine proposée, cocher la brigade « DEMO-J2 », lancer | La grille de la semaine se remplit de séances « Procédures radio J2 » | RG-31 (génération = brouillon), RG-35/36 (instructeur qualifié et libre) |
| 2 | Examens | Créer une évaluation (`/evaluations/creer/`) | Type « Formative », matière « Transmission sécurisée J2 », brigade « DEMO-J2-TEMOIN », un jour/créneau libre, instructeur « Beta » | La séance apparaît au programme de la même semaine, verrouillée, étiquetée « Contrôle » | US-EVAL-01 (`inserer_seance_de_controle`, seconde entrée de la porte unique) |
| 3 | Planification | Consultation du programme | « Soumettre à validation » | Bandeau « Soumis », programme verrouillé en écriture directe | T2 (ETA-01) |
| 4 | Pédagogique | Page d'attente (`/planification/programmes/en-attente/`) | Ouvrir le programme, « Rejeter », saisir un motif | Bandeau « Rejeté », motif affiché | T5, RG-45 (motif obligatoire) |
| 5 | Planification | Consultation, puis modification d'une séance | Modifier l'heure ou le lieu d'une séance « Procédures radio J2 », enregistrer, puis « Soumettre » à nouveau | Le programme repasse par « Brouillon » (reprise implicite) avant de redevenir « Soumis » | T6 implicite (écriture sur un programme rejeté) |
| 6 | Pédagogique | Page d'attente | « Valider » | Bandeau « Validé » | T4 |
| 7 | Planification | Consultation du programme validé | Enregistrer la signature (date, nom du signataire), puis « Afficher » | Bandeau « Affiché » | T7, T8, RG-46 (affichage exige la signature) |
| 8a | Planification | Déclarer une indisponibilité (`/indisponibilites-instructeurs/declarer/`) | Instructeur « Alpha », une période couvrant une de ses séances de la semaine | Redirection immédiate vers les séances impactées : la séance « Procédures radio J2 » d'Alpha y figure | C1/I2, US-PLAN-09 |
| 8b | Planification | Traitement de l'indisponibilité, écran « Remplacer » | Choisir « Gamma » (seul proposé : qualifié, libre), motif et nature d'avenant « Remplacement d'instructeur » | La séance change d'instructeur ; le programme reste « Affiché » ; l'avenant apparaît sur la consultation | I3, I4 (liste des remplaçants bornée), avenant jamais un retour à brouillon |
| 9a | Examens | Créer une évaluation | Type « Certificative », session « Session J2 », date dans quelques semaines | Évaluation créée ; le jour choisi se ferme au calendrier (consultable depuis les écrans de `ressources`) | A2/A4 US-EVAL-02, `ResolveurJoursExamen` |
| 9b | Examens | Fiche de l'évaluation, bloc créneau puis sujets (`/evaluations/<id>/sujets/`) | Fixer un créneau horaire ; déposer deux sujets ; retenir l'un des deux | La fiche affiche « 2 sujets enregistrés », « sujet retenu : oui » — jamais la référence ni le rang en dehors de cet écran | C3-C5 US-EVAL-03 (confidentialité par construction) |
| 9c | Examens | Organisation de l'épreuve (`/evaluations/<id>/organisation/`) | Ajouter la brigade « DEMO-J2 », le lieu « Salle J2 », un surveillant | Organisation « Prête » (sujet retenu) | US-EVAL-04 |
| 9d | Examens | Convocation (`/evaluations/<id>/convocation/`) | Ouvrir, imprimer | Convocation complète, aucune référence de sujet | A11 (convocation sans sujet) |
| 10 | Direction de Formation | Consultation du programme, puis convocation | Ouvrir les deux écrans ; tenter d'ouvrir les sujets de l'évaluation | Programme affiché lisible, convocation lisible, sujets refusés (403) | RG-02 (habilitation par domaine), confidentialité des sujets |

## Trois questions probables du jury

**Pourquoi un avenant plutôt qu'un retour à brouillon, pour remplacer un
instructeur sur un programme déjà affiché ?** Un programme affiché a déjà
été distribué : le faire revenir en brouillon effacerait silencieusement
une publication déjà faite, sans laisser de trace de ce qui a changé ni
pourquoi. L'avenant motivé et daté modifie la séance sans jamais changer
l'état du programme — la trace de la décision survit à la séance elle-même
(`Avenant.seance` en `PROTECT`).

**Pourquoi les sujets d'examen ne sont-ils stockés que par référence ?**
Le système ne numérise jamais le contenu réel d'une épreuve : `Sujet` ne
porte qu'un libellé (« Pli confidentiel… ») et une date de dépôt, jamais le
texte de l'épreuve. La confidentialité tient à ce que le contenu n'entre
jamais dans la base, pas à un contrôle d'accès qui pourrait être contourné
— la référence elle-même n'apparaît d'ailleurs jamais dans le journal
(C3, US-EVAL-03).

**Pourquoi une projection plutôt qu'une copie, pour fermer un jour au
calendrier à la date d'un examen ?** Le jour fermé n'est jamais stocké :
`ResolveurJoursExamen` le recalcule à chaque appel depuis la date de
l'évaluation. Une copie recopiée au moment de la saisie deviendrait fausse
dès que la date change (US-EVAL-02) ou qu'une brigade rejoint la session
après coup — la projection, elle, est toujours à jour par construction
(« aucun attribut dérivé n'est stocké »).
