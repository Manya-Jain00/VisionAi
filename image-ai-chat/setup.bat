@echo off
REM ──────────────────────────────────────────────────────────
REM setup.bat — One-time setup for Image AI Chat (Windows)
REM
REM Double-click this file OR run it from Command Prompt.
REM ──────────────────────────────────────────────────────────

echo.
echo ╔══════════════════════════════════════════════════╗
echo ║        Image AI Chat — Setup Script             ║
echo ╚══════════════════════════════════════════════════╝
echo.

REM 1. Check Python
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo [ERROR] Python not found.
    echo         Please install Python 3.9+ from https://www.python.org/downloads/
    echo         Make sure to tick "Add Python to PATH" during install.
    pause
    exit /b 1
)

FOR /F "tokens=2" %%V IN ('python --version') DO SET PY_VER=%%V
echo [OK] Python found: %PY_VER%

REM 2. Create virtual environment
IF NOT EXIST "venv\" (
    echo.
    echo [--] Creating virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created.
) ELSE (
    echo [OK] Virtual environment already exists.
)

REM 3. Activate venv
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated.

REM 4. Upgrade pip
pip install --upgrade pip --quiet

REM 5. Install dependencies
echo.
echo [--] Installing Python dependencies (may take several minutes)...
pip install -r requirements.txt
echo.
echo [OK] All dependencies installed.

REM 6. Create uploads folder
IF NOT EXIST "uploads\" mkdir uploads
echo [OK] uploads\ folder ready.

echo.
echo ══════════════════════════════════════════════════
echo   Setup complete!
echo.
echo   To run the app, open a Command Prompt and type:
echo.
echo     cd /d "%CD%"
echo     venv\Scripts\activate
echo     python app.py
echo.
echo   Then open:  http://127.0.0.1:5000
echo ══════════════════════════════════════════════════
echo.
pause
