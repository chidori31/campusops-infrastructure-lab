param(
    [Parameter(Mandatory = $true)]
    [string]$File
)

$ErrorActionPreference = "Stop"


if (-not (Test-Path $File)) {
    throw "Backup file not found: $File"
}


$ResolvedFile = Resolve-Path $File

$BackupName = Split-Path `
    $ResolvedFile `
    -Leaf

$ContainerBackup = "/tmp/$BackupName"

$RestoreDatabase = "campusops_restore"


Write-Host ""
Write-Host "CampusOps PostgreSQL recovery test"
Write-Host "Backup: $ResolvedFile"
Write-Host ""


Write-Host "Copying backup into PostgreSQL container..."

docker cp `
    $ResolvedFile `
    "campusops-db:$ContainerBackup"


if ($LASTEXITCODE -ne 0) {
    throw "Unable to copy backup"
}


Write-Host ""
Write-Host "Dropping previous restore database if it exists..."


docker compose exec -T db `
    psql `
    -U campusops `
    -d postgres `
    -c "DROP DATABASE IF EXISTS $RestoreDatabase WITH (FORCE);"


if ($LASTEXITCODE -ne 0) {
    throw "Unable to drop restore database"
}


Write-Host ""
Write-Host "Creating clean restore database..."


docker compose exec -T db `
    psql `
    -U campusops `
    -d postgres `
    -c "CREATE DATABASE $RestoreDatabase OWNER campusops;"


if ($LASTEXITCODE -ne 0) {
    throw "Unable to create restore database"
}


Write-Host ""
Write-Host "Restoring backup..."


docker compose exec -T db `
    pg_restore `
    -U campusops `
    -d $RestoreDatabase `
    --no-owner `
    $ContainerBackup


if ($LASTEXITCODE -ne 0) {
    throw "pg_restore failed"
}


Write-Host ""
Write-Host "Checking restored tables..."


docker compose exec -T db `
    psql `
    -U campusops `
    -d $RestoreDatabase `
    -c "\dt"


Write-Host ""
Write-Host "Checking Alembic version..."


docker compose exec -T db `
    psql `
    -U campusops `
    -d $RestoreDatabase `
    -c "SELECT * FROM alembic_version;"


Write-Host ""
Write-Host "Checking restored records..."


docker compose exec -T db `
    psql `
    -U campusops `
    -d $RestoreDatabase `
    -c "SELECT COUNT(*) AS employees FROM employees;"


docker compose exec -T db `
    psql `
    -U campusops `
    -d $RestoreDatabase `
    -c "SELECT COUNT(*) AS devices FROM devices;"


docker compose exec -T db `
    psql `
    -U campusops `
    -d $RestoreDatabase `
    -c "SELECT COUNT(*) AS tickets FROM tickets;"


Write-Host ""
Write-Host "Removing temporary backup from container..."


docker compose exec -T db `
    rm `
    $ContainerBackup


Write-Host ""
Write-Host "====================================="
Write-Host " PostgreSQL restore completed"
Write-Host " Database: $RestoreDatabase"
Write-Host "====================================="
Write-Host ""