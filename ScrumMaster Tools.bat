@echo off
REM Windows Launcher

REM Navigate to script directory
cd /d "%~dp0"

REM Clear screen
cls

REM Display startup information
echo =========================================
echo    ScrumMaster Tools 2.11.1 (SMT)
echo =========================================
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check activation status
if errorlevel 1 (
    echo.
    echo ERROR: Failed to activate virtual environment!
    echo Please make sure virtual environment is properly installed.
    echo Run: python -m venv venv
    echo.
    pause
    exit /b 1
)

REM Run main script
echo Starting ScrumMaster Tools...
echo.
python smt.py

echo.
echo Program finished. Press any key to close...
pause > nul