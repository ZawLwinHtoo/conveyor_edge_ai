@echo off
title Conveyor Edge AI All-In-One Dashboard
cd /d "%~dp0"

echo ========================================================
echo   Starting Conveyor Edge AI All-In-One Dashboard...
echo ========================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [1/2] Creating virtual environment...
    python -m venv .venv
    echo [2/2] Installing required Python packages...
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    echo.
)

.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 exit /b 1

echo Launching Streamlit Dashboard...
.\.venv\Scripts\python.exe -m streamlit run dashboard.py

pause
