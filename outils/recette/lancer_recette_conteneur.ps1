<#
.SYNOPSIS
    Lance l'application dans le conteneur python:3.14-slim-bookworm, pour
    les contrôles marqués [PDF] des cahiers de recette (Prompt 52).

.DESCRIPTION
    WeasyPrint ne s'exécute pas sous Windows (P-44) : `runserver` sous
    Windows ne peut jamais produire les procès-verbaux ni le PDF de la
    progression réalisée. Ce script lance `runserver` dans la même image
    que `pytest -m pdf`, sur le réseau Docker `developpement_default`
    (hôte `base`), SANS RIEN RECHARGER — il pointe sur la base déjà
    chargée par `charger_jeu_recette` / `charger_jeu_volume`.

    Port publié : 8001 (jamais 8000, pour ne jamais être confondu avec un
    `runserver` Windows). Les fichiers statiques (CSS Tailwind précompilé,
    `noyau/static/css/application.css`) sont servis automatiquement :
    `config.settings.recette`/`volume` héritent de `local.py`, DEBUG=True,
    et `django.contrib.staticfiles` sert les fichiers sans `collectstatic`.

    Premier lancement plus lent (installation des dépendances système de
    WeasyPrint et des paquets Python dans le conteneur) — les suivants ne
    recréent rien d'autre que le conteneur lui-même, mais réinstallent
    quand même (image jetable, `--rm`) : c'est le prix de rester sur
    l'image déjà validée par `pytest -m pdf`, sans en construire une
    nouvelle.

    Script bloquant : Ctrl+C arrête le conteneur (`--rm` le supprime).

.PARAMETER Base
    recette | volume

.EXAMPLE
    .\outils\recette\lancer_recette_conteneur.ps1 -Base recette
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("recette", "volume")]
    [string]$Base
)

$ErrorActionPreference = "Stop"

$Racine = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$Conteneur = "pfe_cit_recette_conteneur"
$PortPublie = 8001
$PortInterne = 8000

$BasesParCible = @{
    "recette" = @{ Base = "pfe_cit_recette"; Parametres = "config.settings.recette" }
    "volume"  = @{ Base = "pfe_cit_volume"; Parametres = "config.settings.volume" }
}
$CibleChoisie = $BasesParCible[$Base]

Write-Host "=============================================================="
Write-Host " Lancement de la recette dans le conteneur — base « $($CibleChoisie.Base) »"
Write-Host " Aucun rechargement : la base doit déjà être en l'état voulu"
Write-Host " (charger_jeu_recette --etat complet, ou charger_jeu_volume)."
Write-Host "=============================================================="

# Point 2 — deux serveurs sur la même base pendant une recette, c'est deux
# sources de vérité : avertit plutôt que de refuser (le port 8000 peut être
# occupé par autre chose qu'un runserver Windows sur CETTE base, impossible
# à vérifier depuis l'extérieur), mais ne laisse jamais passer sans l'avoir dit.
$OccupePar8000 = Get-NetTCPConnection -LocalPort $PortInterne -State Listen -ErrorAction SilentlyContinue
if ($OccupePar8000) {
    Write-Warning (
        "Le port $PortInterne est déjà occupé (probablement un `"runserver`" Windows). " +
        "S'il pointe sur la même base « $($CibleChoisie.Base) », deux serveurs vont " +
        "coexister sur la même base pendant cette recette — deux sources de vérité. " +
        "Vérifiez avant de continuer, ou arrêtez ce runserver Windows."
    )
    Start-Sleep -Seconds 5
}

if (docker ps -a --format "{{.Names}}" | Select-String -Pattern "^$Conteneur$" -Quiet) {
    Write-Host "Un conteneur « $Conteneur » existe déjà — suppression avant relancement."
    docker rm -f $Conteneur | Out-Null
}

Write-Host "== Démarrage (installation des dépendances WeasyPrint puis runserver) =="
Write-Host "Adresse : http://localhost:$PortPublie/"
Write-Host "Arrêt : Ctrl+C (le conteneur est supprimé automatiquement, --rm)."
Write-Host ""

# Tableau d'arguments plutôt que la continuation par backtick (`) : un
# espace de trop après un backtick casse silencieusement la commande sans
# erreur claire — un défaut déjà rencontré ailleurs dans ce dépôt.
$CommandeConteneur = (
    "apt-get update -qq && " +
    "apt-get install --no-install-recommends -y -qq libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0 >/dev/null 2>&1 && " +
    "rm -rf /var/lib/apt/lists/* && " +
    "pip install --no-cache-dir -q -r requirements.txt && " +
    "cd app && " +
    "python manage.py runserver 0.0.0.0:$PortInterne --settings=$($CibleChoisie.Parametres)"
)

$ArgumentsDocker = @(
    "run", "--rm", "--name", $Conteneur,
    "--network", "developpement_default",
    "-p", "${PortPublie}:${PortInterne}",
    "-v", "${Racine}:/workspace",
    "-w", "/workspace",
    "-e", "BASE_HOTE=base",
    "python:3.14-slim-bookworm",
    "bash", "-c", $CommandeConteneur
)

& docker @ArgumentsDocker
