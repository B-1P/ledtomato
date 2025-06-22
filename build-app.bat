@echo off
REM LED Tomato - React Native Build Script (Windows)
REM This script sets up and builds the React Native app

echo 🍅 LED Tomato - React Native Build Script
echo =========================================

REM Navigate to React Native directory
cd /d "%~dp0react-native-client"

REM Check if node_modules exists
if not exist "node_modules" (
    echo 📦 Installing dependencies...
    npm install
    
    if %errorlevel% neq 0 (
        echo ❌ Failed to install dependencies!
        pause
        exit /b 1
    )
)

echo 🔧 Available build options:
echo 1) Android Debug
echo 2) Android Release
echo 3) Windows Debug
echo 4) Windows Release
echo 5) Start Metro bundler only

set /p choice="Select option (1-5): "

if "%choice%"=="1" (
    echo 🤖 Building Android Debug...
    npx react-native run-android --variant=debug
) else if "%choice%"=="2" (
    echo 🤖 Building Android Release...
    npx react-native run-android --variant=release
) else if "%choice%"=="3" (
    echo 🪟 Building Windows Debug...
    npx react-native run-windows --arch x64 --logging
) else if "%choice%"=="4" (
    echo 🪟 Building Windows Release...
    npx react-native run-windows --arch x64 --release
) else if "%choice%"=="5" (
    echo 🚀 Starting Metro bundler...
    npx react-native start
) else (
    echo ❌ Invalid option!
    pause
    exit /b 1
)

pause
