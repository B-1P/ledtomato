@echo off
REM Quick run script for LED Tomato CLI

REM Check if virtual environment exists
if not exist "venv" (
    echo ❌ Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the CLI with all passed arguments
ledtomato %*
