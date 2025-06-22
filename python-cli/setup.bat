@echo off
REM Setup and install LED Tomato Python CLI for Windows

echo 🍅 Setting up LED Tomato Python CLI...

REM Check if Python is available (try multiple variants)
set PYTHON_CMD=
python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python
) else (
    py --version >nul 2>&1
    if not errorlevel 1 (
        set PYTHON_CMD=py
    ) else (
        python3 --version >nul 2>&1
        if not errorlevel 1 (
            set PYTHON_CMD=python3
        ) else (
            REM Try common Windows App Store Python location
            "C:/Users/bhpanesa/AppData/Local/Microsoft/WindowsApps/python3.11.exe" --version >nul 2>&1
            if not errorlevel 1 (
                set PYTHON_CMD="C:/Users/bhpanesa/AppData/Local/Microsoft/WindowsApps/python3.11.exe"
            ) else (
                echo ❌ Python is not installed or not in PATH
                echo Please install Python 3.8 or higher from https://python.org
                echo Make sure to check "Add Python to PATH" during installation
                echo Or use the full path to your Python installation
                pause
                exit /b 1
            )
        )
    )
)

echo ✅ Python found: %PYTHON_CMD%

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    %PYTHON_CMD% -m venv venv
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️ Upgrading pip...
%PYTHON_CMD% -m pip install --upgrade pip

REM Install dependencies
echo 📥 Installing dependencies...
%PYTHON_CMD% -m pip install -r requirements.txt

REM Install in development mode
echo 🔧 Installing LED Tomato CLI...
%PYTHON_CMD% -m pip install -e .

echo.
echo ✅ Installation complete!
echo.
echo Usage:
echo   # Activate virtual environment:
echo   venv\Scripts\activate.bat
echo.
echo   # Run CLI:
echo   ledtomato
echo   # or
echo   tomato
echo.
echo   # Deactivate virtual environment when done:
echo   deactivate
echo.
echo 🍅 Happy Pomodoro timing!
pause
