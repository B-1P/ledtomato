# LED Tomato CLI wrapper script for Windows PowerShell
# Uses the full path to Python 3.11

$PythonPath = "C:/Users/bhpanesa/AppData/Local/Microsoft/WindowsApps/python3.11.exe"

# Check if we're in the right directory
if (!(Test-Path "ledtomato_cli")) {
    Write-Host "❌ Please run this script from the python-cli directory" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Run the CLI with all passed arguments
& $PythonPath -m ledtomato_cli.main @args
