# Setup and install LED Tomato Python CLI for Windows (PowerShell)

Write-Host "🍅 Setting up LED Tomato Python CLI..." -ForegroundColor Green

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8 or higher from https://python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Create virtual environment if it doesn't exist
if (!(Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Blue
    python -m venv venv
}

# Activate virtual environment
Write-Host "🔄 Activating virtual environment..." -ForegroundColor Blue
& "venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "⬆️ Upgrading pip..." -ForegroundColor Blue
python -m pip install --upgrade pip

# Install dependencies
Write-Host "📥 Installing dependencies..." -ForegroundColor Blue
pip install -r requirements.txt

# Install in development mode
Write-Host "🔧 Installing LED Tomato CLI..." -ForegroundColor Blue
pip install -e .

Write-Host ""
Write-Host "✅ Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Usage:" -ForegroundColor Yellow
Write-Host "  # Activate virtual environment:" -ForegroundColor White
Write-Host "  venv\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "  # Run CLI:" -ForegroundColor White
Write-Host "  ledtomato" -ForegroundColor Cyan
Write-Host "  # or" -ForegroundColor White
Write-Host "  tomato" -ForegroundColor Cyan
Write-Host ""
Write-Host "  # Deactivate virtual environment when done:" -ForegroundColor White
Write-Host "  deactivate" -ForegroundColor Cyan
Write-Host ""
Write-Host "🍅 Happy Pomodoro timing!" -ForegroundColor Green
Read-Host "Press Enter to continue"
