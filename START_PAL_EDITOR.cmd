@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo The local Pal Editor environment is missing.
  echo Recreate .venv and install this project before launching.
  pause
  exit /b 1
)

".venv\Scripts\python.exe" -m palworld_pal_editor --mode gui --nocli
if errorlevel 1 pause
