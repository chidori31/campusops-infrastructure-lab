#Requires -RunAsAdministrator

param(
    [Parameter(Mandatory = $true)]
    [string]$IsoPath
)

$ErrorActionPreference = "Stop"

$VMName = "CAMPUSOPS-DC01"
$SwitchName = "CampusOps-Lab"

$VMRoot = "C:\Hyper-V\CampusOps"
$VMPath = Join-Path $VMRoot $VMName
$VHDPath = Join-Path $VMPath "$VMName.vhdx"

$StartupMemory = 4GB
$MinimumMemory = 2GB
$MaximumMemory = 5GB

$VHDSize = 60GB


if (-not (Test-Path $IsoPath)) {
    throw "ISO not found: $IsoPath"
}


if (-not (
    Get-VMSwitch `
        -Name $SwitchName `
        -ErrorAction SilentlyContinue
)) {
    throw "Hyper-V switch '$SwitchName' does not exist."
}


if (
    Get-VM `
        -Name $VMName `
        -ErrorAction SilentlyContinue
) {
    throw "VM '$VMName' already exists."
}


New-Item `
    -ItemType Directory `
    -Path $VMPath `
    -Force |
    Out-Null


Write-Host ""
Write-Host "Creating $VMName..."
Write-Host ""


New-VM `
    -Name $VMName `
    -Generation 2 `
    -MemoryStartupBytes $StartupMemory `
    -NewVHDPath $VHDPath `
    -NewVHDSizeBytes $VHDSize `
    -Path $VMRoot `
    -SwitchName $SwitchName


Set-VMProcessor `
    -VMName $VMName `
    -Count 2


Set-VMMemory `
    -VMName $VMName `
    -DynamicMemoryEnabled $true `
    -MinimumBytes $MinimumMemory `
    -StartupBytes $StartupMemory `
    -MaximumBytes $MaximumMemory


Set-VM `
    -Name $VMName `
    -AutomaticCheckpointsEnabled $true


Add-VMDvdDrive `
    -VMName $VMName `
    -Path $IsoPath


$DVD = Get-VMDvdDrive `
    -VMName $VMName


Set-VMFirmware `
    -VMName $VMName `
    -FirstBootDevice $DVD


Write-Host ""
Write-Host "======================================"
Write-Host " CAMPUSOPS-DC01 created"
Write-Host "======================================"
Write-Host ""
Write-Host "CPU:    2 vCPU"
Write-Host "RAM:    2-5 GB Dynamic"
Write-Host "Disk:   60 GB"
Write-Host "Switch: CampusOps-Lab"
Write-Host "ISO:    $IsoPath"
Write-Host ""