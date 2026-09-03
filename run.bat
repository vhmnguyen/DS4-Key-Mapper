@echo off
setlocal
cd /d "%~dp0"

set "PYTHON_CMD="
where py >nul 2>nul && set "PYTHON_CMD=py -3"
if not defined PYTHON_CMD (
    where python >nul 2>nul && set "PYTHON_CMD=python"
)

if not defined PYTHON_CMD (
    echo Python was not found.
    echo.
    echo Install Python 3.11 or newer from https://www.python.org/downloads/windows/
    echo IMPORTANT: enable "Add python.exe to PATH" in the installer.
    echo Then close this window and run run.bat again.
    echo.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating Python environment...
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 goto :setup_failed

    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    if errorlevel 1 goto :setup_failed

    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 goto :setup_failed
)

".venv\Scripts\python.exe" main.py
if errorlevel 1 (
    echo.
    echo DS4 Key Mapper exited with an error.
    pause
)
exit /b

:setup_failed
echo.
echo Setup failed. Check the error above, then delete the .venv folder and try again.
pause
exit /b 1
