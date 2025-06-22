#!/bin/bash

# LED Tomato - React Native Build Script
# This script sets up and builds the React Native app

echo "🍅 LED Tomato - React Native Build Script"
echo "========================================="

# Navigate to React Native directory
cd "$(dirname "$0")/react-native-client"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies!"
        exit 1
    fi
fi

echo "🔧 Available build options:"
echo "1) Android Debug"
echo "2) Android Release"
echo "3) iOS Debug"
echo "4) iOS Release"
echo "5) Windows Debug"
echo "6) Windows Release"
echo "7) Start Metro bundler only"

read -p "Select option (1-7): " -n 1 -r
echo

case $REPLY in
    1)
        echo "🤖 Building Android Debug..."
        npx react-native run-android --variant=debug
        ;;
    2)
        echo "🤖 Building Android Release..."
        npx react-native run-android --variant=release
        ;;
    3)
        echo "🍎 Building iOS Debug..."
        npx react-native run-ios --configuration Debug
        ;;
    4)
        echo "🍎 Building iOS Release..."
        npx react-native run-ios --configuration Release
        ;;
    5)
        echo "🪟 Building Windows Debug..."
        npx react-native run-windows --arch x64 --logging
        ;;
    6)
        echo "🪟 Building Windows Release..."
        npx react-native run-windows --arch x64 --release
        ;;
    7)
        echo "🚀 Starting Metro bundler..."
        npx react-native start
        ;;
    *)
        echo "❌ Invalid option!"
        exit 1
        ;;
esac
