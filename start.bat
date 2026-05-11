@echo off
REM Double-click launcher for Star Citizen Companion.
REM Activates the venv and starts the app from this directory.
cd /d "%~dp0"
start "" "%~dp0.venv\Scripts\pythonw.exe" -m sc_companion
