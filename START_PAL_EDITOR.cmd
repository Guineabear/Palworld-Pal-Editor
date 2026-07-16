@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo This file is only for developers running the source code.
  echo.
  echo For normal Windows use, download and run:
  echo Palworld-Pal-Editor-1.0.exe
  echo.
  echo Opening the official Community Edition release page...
  start "" "https://github.com/Guineabear/Palworld-Pal-Editor/releases/latest"
  echo.
  echo If you are a developer, create .venv and install the project first.
  pause
  exit /b 1
)

".venv\Scripts\python.exe" -m palworld_pal_editor --mode gui --nocli
if errorlevel 1 pause
