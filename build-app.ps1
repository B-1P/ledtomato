# LED Tomato - PowerShell Build Script
# This script builds the React Native app for Windows

param(
    [Parameter(Position=0)]
    [ValidateSet("android-debug", "android-release", "windows-debug", "windows-release", "metro")]
    [string]$Target = "windows-debug"
)

Write-Host "🍅 LED Tomato - PowerShell Build Script" -ForegroundColor Red
Write-Host "======================================" -ForegroundColor Red

# Navigate to React Native directory
$reactNativeDir = Join-Path $PSScriptRoot "react-native-client"
Set-Location $reactNativeDir

# Check if node_modules exists
if (!(Test-Path "node_modules")) {
    Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
    npm install
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install dependencies!" -ForegroundColor Red
        exit 1
    }
}

# Build based on target
switch ($Target) {
    "android-debug" {
        Write-Host "🤖 Building Android Debug..." -ForegroundColor Green
        npx react-native run-android --variant=debug
    }
    "android-release" {
        Write-Host "🤖 Building Android Release..." -ForegroundColor Green
        npx react-native run-android --variant=release
    }
    "windows-debug" {
        Write-Host "🪟 Building Windows Debug..." -ForegroundColor Cyan
        
        # Check if Windows is initialized
        if (!(Test-Path "windows")) {
            Write-Host "🔧 Initializing React Native Windows..." -ForegroundColor Yellow
            npx react-native-windows-init --overwrite --verbose
            
            if ($LASTEXITCODE -ne 0) {
                Write-Host "❌ Failed to initialize React Native Windows!" -ForegroundColor Red
                Write-Host "Prerequisites:" -ForegroundColor Yellow
                Write-Host "- Visual Studio 2019/2022 with C++ tools" -ForegroundColor White
                Write-Host "- Windows 10/11 SDK" -ForegroundColor White
                Write-Host "- Node.js 16 or higher" -ForegroundColor White
                exit 1
            }
        }
        
        npx react-native run-windows --arch x64 --verbose
    }
    "windows-release" {
        Write-Host "🪟 Building Windows Release..." -ForegroundColor Cyan
        npx react-native run-windows --arch x64 --release
    }
    "metro" {
        Write-Host "🚀 Starting Metro bundler..." -ForegroundColor Magenta
        npx react-native start
    }
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Build completed successfully!" -ForegroundColor Green
    if ($Target -like "windows-*") {
        Write-Host "🚀 Windows app should be launching..." -ForegroundColor Cyan
    }
} else {
    Write-Host "❌ Build failed!" -ForegroundColor Red
    
    if ($Target -like "windows-*") {
        Write-Host "Common Windows build issues:" -ForegroundColor Yellow
        Write-Host "- Make sure Visual Studio is installed with C++ tools" -ForegroundColor White
        Write-Host "- Ensure Windows SDK is installed" -ForegroundColor White
        Write-Host "- Try running as Administrator" -ForegroundColor White
        Write-Host "- Check that no antivirus is blocking the build" -ForegroundColor White
    }
}

Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
