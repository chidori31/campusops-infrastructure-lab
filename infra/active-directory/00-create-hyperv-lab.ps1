#Requires -RunAsAdministrator

$ErrorActionPreference = "Stop"

$SwitchName = "CampusOps-Lab"
$Subnet = "192.168.56.0/24"
$HostIP = "192.168.56.1"
$PrefixLength = 24
$NatName = "CampusOps-Lab-NAT"

Write-Host ""
Write-Host "=== CampusOps Hyper-V Lab ==="
Write-Host ""

# ---------------------------------------------------------
# Check Hyper-V
# ---------------------------------------------------------

$HyperV = Get-WindowsOptionalFeature `
    -Online `
    -FeatureName Microsoft-Hyper-V-All

if ($HyperV.State -ne "Enabled") {
    throw "Hyper-V is not enabled."
}

Write-Host "[OK] Hyper-V enabled"


# ---------------------------------------------------------
# Check subnet collision
# ---------------------------------------------------------

$ExistingIP = Get-NetIPAddress `
    -AddressFamily IPv4 `
    -ErrorAction SilentlyContinue |
    Where-Object {
        $_.IPAddress -eq $HostIP
    }

if ($ExistingIP) {
    Write-Host "[INFO] $HostIP already configured"
}


# ---------------------------------------------------------
# Create internal virtual switch
# ---------------------------------------------------------

$Switch = Get-VMSwitch `
    -Name $SwitchName `
    -ErrorAction SilentlyContinue

if (-not $Switch) {
    Write-Host "[CREATE] Hyper-V switch: $SwitchName"

    New-VMSwitch `
        -Name $SwitchName `
        -SwitchType Internal
}
else {
    Write-Host "[OK] Hyper-V switch already exists"
}


# ---------------------------------------------------------
# Locate host-side virtual adapter
# ---------------------------------------------------------

$Adapter = Get-NetAdapter |
    Where-Object {
        $_.Name -eq "vEthernet ($SwitchName)"
    }

if (-not $Adapter) {
    throw "Unable to find Hyper-V virtual adapter."
}

Write-Host "[OK] Adapter: $($Adapter.Name)"


# ---------------------------------------------------------
# Configure host IP
# ---------------------------------------------------------

$ConfiguredIP = Get-NetIPAddress `
    -InterfaceIndex $Adapter.ifIndex `
    -AddressFamily IPv4 `
    -ErrorAction SilentlyContinue |
    Where-Object {
        $_.IPAddress -eq $HostIP
    }

if (-not $ConfiguredIP) {
    Write-Host "[CREATE] Host lab IP: $HostIP"

    New-NetIPAddress `
        -InterfaceIndex $Adapter.ifIndex `
        -IPAddress $HostIP `
        -PrefixLength $PrefixLength
}
else {
    Write-Host "[OK] Host lab IP already configured"
}


# ---------------------------------------------------------
# Create NAT
# ---------------------------------------------------------

$ExistingNat = Get-NetNat `
    -Name $NatName `
    -ErrorAction SilentlyContinue

if (-not $ExistingNat) {
    Write-Host "[CREATE] NAT: $Subnet"

    New-NetNat `
        -Name $NatName `
        -InternalIPInterfaceAddressPrefix $Subnet
}
else {
    Write-Host "[OK] NAT already exists"
}


Write-Host ""
Write-Host "=================================="
Write-Host " CampusOps Hyper-V network ready"
Write-Host "=================================="
Write-Host ""
Write-Host "Switch : $SwitchName"
Write-Host "Subnet : $Subnet"
Write-Host "Host   : $HostIP"
Write-Host ""