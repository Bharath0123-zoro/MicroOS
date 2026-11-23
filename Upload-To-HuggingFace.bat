@echo off
setlocal
cd /d "C:\Users\tirup\.gemini\antigravity\scratch\MicroOS"

echo ============================================================
echo       MicroOS - Automated Hugging Face Publisher
echo ============================================================
echo.

python "%~dp0Upload-To-HuggingFace.py"

echo.
pause
