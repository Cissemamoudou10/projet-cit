<#
.SYNOPSIS
    Remet à zéro la base de recette ou la base volumineuse (Prompt 51, Temps 1).

.DESCRIPTION
    Supprime puis recrée la base cible, migre, charge les catalogues de
    référence (habilitations, gabarits de documents, grilles horaires), puis
    le chargeur de l'état demandé et son `--verifier`.

    Deux bases seulement, jamais une autre : `pfe_cit_recette` (états
    `socle` et `complet`, module de réglages `config.settings.recette`) et
    `pfe_cit_volume` (état `volume`, `config.settings.volume`). Refuse toute
    autre cible — voir `docs/suivi/JEU-RECETTE.md` pour la raison de cette
    séparation (jamais de coexistence avec le jeu de démonstration).

    ORDRE DES CATALOGUES DE RÉFÉRENCE — écart volontaire avec l'ordre
    littéral du prompt 51 : `initialiser_grilles_horaires` exige qu'un compte
    administrateur existe déjà (son propre `CommandError`, voir
    `ressources/management/commands/initialiser_grilles_horaires.py`), alors
    que c'est le CHARGEUR (Temps 2/3) qui crée ce compte. Les grilles sont
    donc chargées APRÈS le chargeur, jamais avant — `initialiser_habilitations`,
    `initialiser_gabarits_documents` et `initialiser_natures_evenement`, eux,
    ne dépendent d'aucun compte et restent avant. `initialiser_natures_evenement`
    n'est pas nommée par le prompt 51 lui-même (seulement les trois autres) :
    ajoutée ici parce que l'état `complet` charge des périodes de calendrier
    (§ 2.2) qui référencent une `NatureEvenement` du catalogue — sans elle,
    `ServicePeriodeCalendrier.creer` échouerait avec `NatureEvenement.
    DoesNotExist`.

.PARAMETER Etat
    socle | complet | volume

.EXAMPLE
    .\outils\recette\reinitialiser_base_recette.ps1 -Etat socle
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("socle", "complet", "volume")]
    [string]$Etat
)

$ErrorActionPreference = "Stop"

$Racine = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$DossierApplication = Join-Path $Racine "app"

$Conteneur = "pfe_cit_base"
$RoleMigration = "pfe_cit_migration"
$RoleApplication = "pfe_cit_app"
$MotDePasseMigration = if ($env:BASE_MOT_DE_PASSE_MIGRATION) { $env:BASE_MOT_DE_PASSE_MIGRATION } else { "developpement_local_migration" }
$MotDePasseApplication = if ($env:BASE_MOT_DE_PASSE) { $env:BASE_MOT_DE_PASSE } else { "developpement_local_app" }

# Les deux seules bases autorisées (§ garde-fou commun, docs/suivi/JEU-RECETTE.md).
# Dérivées de -Etat, jamais saisies : ce dictionnaire est la SEULE source de vérité.
$BasesParEtat = @{
    "socle"   = @{ Base = "pfe_cit_recette"; Parametres = "config.settings.recette" }
    "complet" = @{ Base = "pfe_cit_recette"; Parametres = "config.settings.recette" }
    "volume"  = @{ Base = "pfe_cit_volume"; Parametres = "config.settings.volume" }
}
$BasesAutorisees = @("pfe_cit_recette", "pfe_cit_volume")

$Base = $BasesParEtat[$Etat].Base
$Parametres = $BasesParEtat[$Etat].Parametres

if ($BasesAutorisees -notcontains $Base) {
    throw "Base « $Base » non autorisée — seules $($BasesAutorisees -join ', ') le sont. Rien n'a été touché."
}

Write-Host "=============================================================="
Write-Host " Remise à zéro — état « $Etat », base « $Base »"
Write-Host " Cette opération SUPPRIME DÉFINITIVEMENT le contenu actuel."
Write-Host "=============================================================="
$Confirmation = Read-Host "Tapez exactement le nom de la base à supprimer ($Base) pour confirmer"
if ($Confirmation -ne $Base) {
    throw "Confirmation refusée ou nom incorrect (« $Confirmation » ≠ « $Base ») — rien n'a été supprimé."
}

function Invoke-Psql {
    param(
        [Parameter(Mandatory = $true)][string]$BaseCible,
        [Parameter(Mandatory = $true)][string]$Commande
    )
    & docker exec -e "PGPASSWORD=$MotDePasseMigration" $Conteneur `
        psql -v ON_ERROR_STOP=1 -U $RoleMigration -d $BaseCible -c $Commande
    if ($LASTEXITCODE -ne 0) {
        throw "psql a échoué sur « $BaseCible » : $Commande"
    }
}

function Invoke-Manage {
    param([Parameter(Mandatory = $true)][string[]]$Arguments)
    Push-Location $DossierApplication
    try {
        & python manage.py @Arguments --settings=$Parametres
        if ($LASTEXITCODE -ne 0) {
            throw "manage.py $($Arguments -join ' ') a échoué (settings=$Parametres)."
        }
    }
    finally {
        Pop-Location
    }
}

Write-Host "== 1. Suppression puis recréation de « $Base » =="
Invoke-Psql -BaseCible "postgres" -Commande "DROP DATABASE IF EXISTS $Base;"
Invoke-Psql -BaseCible "postgres" -Commande "CREATE DATABASE $Base OWNER $RoleMigration;"
Invoke-Psql -BaseCible $Base -Commande "GRANT USAGE ON SCHEMA public TO $RoleApplication;"
Invoke-Psql -BaseCible $Base -Commande (
    "ALTER DEFAULT PRIVILEGES FOR ROLE $RoleMigration IN SCHEMA public " +
    "GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO $RoleApplication;"
)
Invoke-Psql -BaseCible $Base -Commande (
    "ALTER DEFAULT PRIVILEGES FOR ROLE $RoleMigration IN SCHEMA public " +
    "GRANT USAGE, SELECT ON SEQUENCES TO $RoleApplication;"
)

Write-Host "== 2. Migrations (rôle $RoleMigration) =="
$env:BASE_UTILISATEUR = $RoleMigration
$env:BASE_MOT_DE_PASSE = $MotDePasseMigration
try {
    Invoke-Manage -Arguments @("migrate")
}
finally {
    # Retour immédiat au rôle applicatif : tout ce qui suit (chargeurs,
    # initialiseurs, verifier) tourne comme l'application en fonctionnement
    # normal, jamais avec les privilèges de migration.
    $env:BASE_UTILISATEUR = $RoleApplication
    $env:BASE_MOT_DE_PASSE = $MotDePasseApplication
}

Write-Host "== 3. Catalogues de référence sans dépendance de compte =="
Invoke-Manage -Arguments @("initialiser_habilitations")
Invoke-Manage -Arguments @("initialiser_gabarits_documents")
Invoke-Manage -Arguments @("initialiser_natures_evenement")

Write-Host "== 4. Chargeur de l'état « $Etat » =="
switch ($Etat) {
    "socle"   { Invoke-Manage -Arguments @("charger_jeu_recette") }
    "complet" { Invoke-Manage -Arguments @("charger_jeu_recette", "--etat", "complet") }
    "volume"  { Invoke-Manage -Arguments @("charger_jeu_volume") }
}

Write-Host "== 5. Grilles horaires (après le chargeur : exige un compte administrateur) =="
Invoke-Manage -Arguments @("initialiser_grilles_horaires")

Write-Host "== 6. Vérification =="
switch ($Etat) {
    "socle"   { Invoke-Manage -Arguments @("charger_jeu_recette", "--verifier") }
    "complet" { Invoke-Manage -Arguments @("charger_jeu_recette", "--etat", "complet", "--verifier") }
    "volume"  { Invoke-Manage -Arguments @("charger_jeu_volume", "--verifier") }
}

Write-Host "=============================================================="
Write-Host " Terminé — base « $Base », état « $Etat »."
Write-Host "=============================================================="
