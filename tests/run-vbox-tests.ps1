# MicroOS v1.0 Automated Oracle VirtualBox Test Suite Runner
# Strictly uses Oracle VirtualBox (VBoxManage). QEMU is never used.
param(
    [string]$ProjectRoot = "C:\Users\tirup\.gemini\antigravity\scratch\MicroOS",
    [switch]$SkipNetPersist
)

$ErrorActionPreference = "Stop"
$VBox = "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
$Iso = Join-Path $ProjectRoot "release\microos.iso"
$DiskDir = Join-Path $ProjectRoot "build\vm-disks"
$LogFile = Join-Path $ProjectRoot "logs\test.log"
$Driver = Join-Path $ProjectRoot "tests\vbox-serial-driver.py"

if (-not (Test-Path $Iso)) {
    throw "ISO not found at $Iso. Build MicroOS ISO first."
}
New-Item -ItemType Directory -Force -Path $DiskDir | Out-Null

function Setup-TestVM {
    param(
        [string]$Name,
        [string]$Firmware,   # bios or efi
        [int]$SerialPort,
        [string]$DiskPath,
        [bool]$EnableNet
    )
    $null = cmd /c "`"$VBox`" controlvm `"$Name`" poweroff >nul 2>&1"
    Start-Sleep -Milliseconds 500
    $null = cmd /c "`"$VBox`" unregistervm `"$Name`" --delete >nul 2>&1"
    $userProfile = [Environment]::GetFolderPath("UserProfile")
    $vmDir = Join-Path $userProfile "VirtualBox VMs\$Name"
    if (Test-Path $vmDir) {
        Remove-Item -Recurse -Force $vmDir -ErrorAction SilentlyContinue
    }

    $null = cmd /c "`"$VBox`" closemedium disk `"$DiskPath`" --delete >nul 2>&1"
    if (Test-Path $DiskPath) { Remove-Item -Force $DiskPath -ErrorAction SilentlyContinue }
    $null = cmd /c "`"$VBox`" createmedium disk --filename `"$DiskPath`" --size 512 --format VDI >nul 2>&1"

    $null = cmd /c "`"$VBox`" createvm --name `"$Name`" --ostype Linux_64 --register"
    $nicStr = if ($EnableNet) { "--nic1 nat --nictype1 82540EM" } else { "--nic1 none" }
    $null = cmd /c "`"$VBox`" modifyvm `"$Name`" --memory 1024 --cpus 1 --firmware $Firmware --ioapic on --acpi on --boot1 dvd --boot2 disk --boot3 none --boot4 none --uart1 0x3F8 4 --uartmode1 tcpserver $SerialPort --audio-enabled off --graphicscontroller vmsvga --vram 16 $nicStr"

    $null = cmd /c "`"$VBox`" storagectl `"$Name`" --name SATA --add sata --controller IntelAhci --portcount 2"
    $null = cmd /c "`"$VBox`" storageattach `"$Name`" --storagectl SATA --port 0 --device 0 --type hdd --medium `"$DiskPath`""
    $null = cmd /c "`"$VBox`" storageattach `"$Name`" --storagectl SATA --port 1 --device 0 --type dvddrive --medium `"$Iso`""
}

# Virtual hard disks for BIOS and UEFI offline tests
$BiosDisk = Join-Path $DiskDir "microos-bios-test.vdi"
$UefiDisk = Join-Path $DiskDir "microos-uefi-test.vdi"

$allPass = $true

Write-Output "=== Running Suite A: VirtualBox BIOS Offline Test (1024MB RAM, 1 CPU, No NIC) ==="
Setup-TestVM -Name "MicroOS-BIOS-Test" -Firmware "bios" -SerialPort 2301 -DiskPath $BiosDisk -EnableNet $false
python $Driver --vm "MicroOS-BIOS-Test" --port 2301 --mode "bios-offline" --screenshot (Join-Path $DiskDir "bios-boot.png") --log $LogFile
if ($LASTEXITCODE -ne 0) { $allPass = $false }

Write-Output "=== Running Suite B: VirtualBox UEFI Offline Test (1024MB RAM, 1 CPU, No NIC) ==="
Setup-TestVM -Name "MicroOS-UEFI-Test" -Firmware "efi" -SerialPort 2302 -DiskPath $UefiDisk -EnableNet $false
python $Driver --vm "MicroOS-UEFI-Test" --port 2302 --mode "uefi-offline" --screenshot (Join-Path $DiskDir "uefi-boot.png") --log $LogFile
if ($LASTEXITCODE -ne 0) { $allPass = $false }

$PersistVdi = Join-Path $DiskDir "microos-persist.vdi"
if ((-not $SkipNetPersist) -and (Test-Path $PersistVdi)) {
    Write-Output "=== Running Suite C: VirtualBox Persistent Debian APT + Emulated Ethernet Test ==="
    Setup-TestVM -Name "MicroOS-NetPersist-Test" -Firmware "bios" -SerialPort 2303 -DiskPath $PersistVdi -EnableNet $true
    python $Driver --vm "MicroOS-NetPersist-Test" --port 2303 --mode "net-persist" --screenshot (Join-Path $DiskDir "netpersist-boot.png") --log $LogFile
    if ($LASTEXITCODE -ne 0) { $allPass = $false }
}

if (-not $allPass) {
    Write-Error "One or more VirtualBox test suites failed. See $LogFile"
    exit 1
}
Write-Output "ALL VIRTUALBOX TEST SUITES PASSED!"
