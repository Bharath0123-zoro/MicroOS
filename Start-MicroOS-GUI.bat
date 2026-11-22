@echo off
set VBOX="C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
set VMNAME=MicroOS-Desktop

echo ===================================================
echo   MICROOS GUI EDITION - Graphical Desktop System
echo ===================================================
echo Starting MicroOS Graphical Desktop in Oracle VirtualBox...
start "" %VBOX% startvm "%VMNAME%" --type gui
echo.
echo VirtualBox GUI display window opened!
