$ErrorActionPreference = "Stop"

$BackupDirectory = Join-Path $PSScriptRoot "..\backups"

if (-not (Test-Path $BackupDirectory)) {
    New-Item `
        -ItemType Directory `
        -Path $BackupDirectory `
        | Out-Null
}

$Timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"

$BackupName = "campusops_$Timestamp.dump"

$ContainerBackup = "/tmp/$BackupName"

$LocalBackup = Join-Path `
    $BackupDirectory `
    $BackupName


Write-Host ""
Write-Host "Creating PostgreSQL backup..."
Write-Host ""


docker compose exec -T db `
    pg_dump `
    -U campusops `
    -d campusops `
    -Fc `
    -f $ContainerBackup


if ($LASTEXITCODE -ne 0) {
    throw "pg_dump failed"
}


docker cp `
    "campusops-db:$ContainerBackup" `
    $LocalBackup


if ($LASTEXITCODE -ne 0) {
    throw "docker cp failed"
}


docker compose exec -T db `
    rm `
    $ContainerBackup


Write-Host ""
Write-Host "Backup created:"
Write-Host $LocalBackup

Write-Host ""

$File = Get-Item $LocalBackup

Write-Host "Backup size:"
Write-Host "$($File.Length) bytes"

Write-Host ""
Write-Host "Backup complete."