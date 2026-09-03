@echo off
setlocal
cd /d "%~dp0"

set "PYTHON_CMD="
where py >nul 2>nul && set "PYTHON_CMD=py -3"
if not defined PYTHON_CMD (
    where python >nul 2>nul && set "PYTHON_CMD=python"
)
if not defined PYTHON_CMD (
    echo Python was not found. Install it from https://www.python.org/downloads/windows/
    echo Enable "Add python.exe to PATH" during installation.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 goto :build_failed
)
".venv\Scripts\python.exe" -m pip install -r requirements.txt pyinstaller
if errorlevel 1 goto :build_failed
".venv\Scripts\pyinstaller.exe" --noconfirm --clean --windowed --name DS4KeyMapper main.py
if errorlevel 1 goto :build_failed
echo Build complete: dist\DS4KeyMapper\DS4KeyMapper.exe
pause
exit /b

:build_failed
echo Build failed. Check the error above.
pause
exit /b 1
