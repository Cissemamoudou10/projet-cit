# Corrige un bug connu de Docker Desktop / WSL2 : au demarrage de Windows, le
# conteneur pfe_cit_base redemarre automatiquement (restart: unless-stopped)
# avant que le proxy reseau WSL2 <-> Windows soit pret. Le conteneur tourne et
# passe "healthy", mais le port 5432 n'est jamais transfere vers Windows --
# un "docker restart" du conteneur suffit a reinitialiser le transfert.
#
# Lancee automatiquement a l'ouverture de session (tache planifiee
# "CIT - Reparer port Postgres"). Journal : infra/docker/reparer-port.log
#
# Pas d'accents dans ce fichier : Windows PowerShell 5.1 lit les .ps1 en ANSI
# par defaut et les caracteres accentues cassent le parseur de chaines.

$ErrorActionPreference = "SilentlyContinue"
$conteneur = "pfe_cit_base"
$port = 5432
$journal = Join-Path $PSScriptRoot "reparer-port.log"

function Ecrire-Journal($message) {
    $horodatage = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$horodatage $message" | Out-File -FilePath $journal -Append -Encoding utf8
}

# Docker Desktop met du temps a demarrer apres l'ouverture de session : on
# attend qu'il reponde, jusqu'a cinq minutes.
$limite = (Get-Date).AddMinutes(5)
$dockerPret = $false
while ((Get-Date) -lt $limite) {
    docker info *> $null
    if ($LASTEXITCODE -eq 0) {
        $dockerPret = $true
        break
    }
    Start-Sleep -Seconds 5
}

if (-not $dockerPret) {
    Ecrire-Journal "Docker n'a pas repondu apres cinq minutes -- abandon."
    exit 1
}

# Le conteneur peut mettre quelques secondes de plus a apparaitre.
Start-Sleep -Seconds 5

$conteneurExiste = docker ps -a --filter "name=^${conteneur}$" --format "{{.Names}}"
if (-not $conteneurExiste) {
    Ecrire-Journal "Conteneur $conteneur introuvable -- rien a faire."
    exit 0
}

$portOk = (Test-NetConnection -ComputerName localhost -Port $port -WarningAction SilentlyContinue).TcpTestSucceeded

if ($portOk) {
    Ecrire-Journal "Port $port deja joignable -- rien a faire."
} else {
    Ecrire-Journal "Port $port injoignable -- redemarrage de $conteneur."
    docker restart $conteneur *> $null
    Start-Sleep -Seconds 5
    $portOk = (Test-NetConnection -ComputerName localhost -Port $port -WarningAction SilentlyContinue).TcpTestSucceeded
    if ($portOk) {
        Ecrire-Journal "Port $port joignable apres redemarrage."
    } else {
        Ecrire-Journal "Port $port toujours injoignable apres redemarrage -- intervention manuelle necessaire."
    }
}
