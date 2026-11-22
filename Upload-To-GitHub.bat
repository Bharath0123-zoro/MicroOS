@echo off
setlocal
cd /d "C:\Users\tirup\.gemini\antigravity\scratch\MicroOS"

echo ============================================================
echo           MicroOS - Automated GitHub Publisher
echo ============================================================
echo Username : Bharath0123-zoro
echo Repo Name: MicroOS
echo Target   : https://github.com/Bharath0123-zoro/MicroOS
echo Location : %CD%
echo ============================================================
echo.

git branch -M main
git remote remove origin 2>nul
git remote add origin https://github.com/Bharath0123-zoro/MicroOS.git

echo [*] Staging all project files...
git add .
git status --short

echo [*] Committing latest changes...
git commit -m "release(v1.0): Complete MicroOS ultra-lightweight Linux OS and GUI Desktop Edition" 2>nul

echo [*] Pushing to GitHub...
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo   MICROOS SUCCESSFULLY PUBLISHED TO GITHUB!
    echo ============================================================
    echo   GitHub URL: https://github.com/Bharath0123-zoro/MicroOS
    echo ============================================================
) else (
    echo.
    echo [!] Push failed. Please verify:
    echo     1. Have you created the repository on GitHub?
    echo        Go to: https://github.com/new and create 'MicroOS' (Public).
    echo     2. Then run this script again!
)

echo.
pause
