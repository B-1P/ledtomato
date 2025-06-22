@echo off
REM LED Tomato - Build Script for ESP32 Firmware (Windows)
REM This script builds and uploads the firmware to ESP32

echo 🍅 LED Tomato - ESP32 Build Script
echo ==================================

REM Check if PlatformIO is installed
pio --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ PlatformIO not found. Installing...
    pip install platformio
)

REM Navigate to firmware directory
cd /d "%~dp0esp32-firmware"

echo 📦 Building firmware...
pio run

if %errorlevel% == 0 (
    echo ✅ Build successful!
    
    set /p upload="🔌 Upload to ESP32? (y/n): "
    if /i "%upload%"=="y" (
        echo 📤 Uploading firmware...
        pio run --target upload
        
        if %errorlevel% == 0 (
            echo ✅ Upload successful!
            echo 🔍 Starting serial monitor...
            pio device monitor
        ) else (
            echo ❌ Upload failed!
            pause
            exit /b 1
        )
    )
) else (
    echo ❌ Build failed!
    pause
    exit /b 1
)

pause
