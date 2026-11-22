@echo off
set VBOX="C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
set VMNAME=MicroOS-v1.0

echo ===================================================
echo   MICROOS v1.0 - Minimal Linux. Maximum Control.
echo ===================================================
echo Starting MicroOS in Oracle VirtualBox (Interactive GUI Window)...
start "" %VBOX% startvm "%VMNAME%" --type gui
echo.
echo VirtualBox display window launched!
