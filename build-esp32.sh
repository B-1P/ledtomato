#!/bin/bash

# LED Tomato - Build Script for ESP32 Firmware
# This script builds and uploads the firmware to ESP32

echo "🍅 LED Tomato - ESP32 Build Script"
echo "=================================="

# Check if PlatformIO is installed
if ! command -v pio &> /dev/null; then
    echo "❌ PlatformIO not found. Installing..."
    pip install platformio
fi

# Navigate to firmware directory
cd "$(dirname "$0")/esp32-firmware"

echo "📦 Building firmware..."
pio run

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    
    read -p "🔌 Upload to ESP32? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📤 Uploading firmware..."
        pio run --target upload
        
        if [ $? -eq 0 ]; then
            echo "✅ Upload successful!"
            echo "🔍 Starting serial monitor..."
            pio device monitor
        else
            echo "❌ Upload failed!"
            exit 1
        fi
    fi
else
    echo "❌ Build failed!"
    exit 1
fi
