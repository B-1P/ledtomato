@echo off
REM LED Tomato CLI wrapper script for Windows
REM Uses the full path to Python 3.11

set PYTHON_PATH="C:/Users/bhpanesa/AppData/Local/Microsoft/WindowsApps/python3.11.exe"

REM Check if we're in the right directory
if not exist "ledtomato_cli" (
    echo ❌ Please run this script from the python-cli directory
    pause
    exit /b 1
)

REM Run the CLI with all passed arguments
%PYTHON_PATH% -m ledtomato_cli.main %*
