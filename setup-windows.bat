@echo off
REM LED Tomato - Windows Setup Script
REM This script initializes React Native Windows support

echo 🪟 LED Tomato - Windows Setup Script
echo ====================================

REM Navigate to React Native directory
cd /d "%~dp0react-native-client"

echo 📦 Installing React Native Windows...

REM Check if already initialized
if exist "windows" (
    echo ✅ React Native Windows already initialized
    goto :build
)

REM Initialize React Native Windows
echo 🔧 Initializing React Native Windows...
npx react-native-windows-init --overwrite --logging

if %errorlevel% neq 0 (
    echo ❌ Failed to initialize React Native Windows!
    echo.
    echo Prerequisites check:
    echo - Visual Studio 2019/2022 with C++ tools
    echo - Windows 10/11 SDK
    echo - Node.js 16 or higher
    echo.
    pause
    exit /b 1
)

:build
echo ✅ React Native Windows initialized successfully!
echo.
echo 🔧 Building Windows app...
npx react-native run-windows --arch x64 --logging

if %errorlevel% == 0 (
    echo ✅ Windows build successful!
    echo 🚀 App should be launching...
) else (
    echo ❌ Windows build failed!
    echo.
    echo Common issues:
    echo - Make sure Visual Studio is installed with C++ tools
    echo - Ensure Windows SDK is installed
    echo - Try running as Administrator
    echo - Check that no antivirus is blocking the build
)

pause
