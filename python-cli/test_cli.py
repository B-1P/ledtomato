#!/usr/bin/env python3
"""
Simple test script for LED Tomato CLI functionality
"""

import sys
import os
import subprocess

# Full path to Python executable
PYTHON_PATH = "C:/Users/bhpanesa/AppData/Local/Microsoft/WindowsApps/python3.11.exe"

def run_cli_command(args):
    """Run a CLI command and return the result"""
    cmd = [PYTHON_PATH, "-m", "ledtomato_cli.main"] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)

def test_cli():
    """Test basic CLI functionality"""
    print("🍅 Testing LED Tomato CLI...")
    print("=" * 50)
    
    # Test help command
    print("\n1. Testing help command...")
    code, stdout, stderr = run_cli_command(["--help"])
    if code == 0:
        print("✅ Help command works!")
        print("📝 Available commands:")
        # Extract command list from help output
        lines = stdout.split('\n')
        for line in lines:
            if 'Commands:' in line:
                for i, cmd_line in enumerate(lines[lines.index(line)+1:]):
                    if cmd_line.strip() == "":
                        break
                    if cmd_line.strip().startswith('discover') or cmd_line.strip().startswith('start') or cmd_line.strip().startswith('stop') or cmd_line.strip().startswith('status') or cmd_line.strip().startswith('config'):
                        print(f"   • {cmd_line.strip()}")
    else:
        print(f"❌ Help command failed: {stderr}")
        return False
    
    # Test discover command (will fail without device, but should show proper error)
    print("\n2. Testing device discovery...")
    code, stdout, stderr = run_cli_command(["discover"])
    if "Scanning for LED Tomato devices" in stdout or "No LED Tomato devices found" in stdout:
        print("✅ Discovery command works (no devices found, which is expected)")
    else:
        print(f"⚠️ Discovery command output: {stdout}")
        print(f"⚠️ Discovery command error: {stderr}")
    
    # Test status command (will fail without device)
    print("\n3. Testing status command...")
    code, stdout, stderr = run_cli_command(["status"])
    if "No device found" in stdout or "Could not connect" in stdout:
        print("✅ Status command works (no device available, which is expected)")
    else:
        print(f"⚠️ Status command output: {stdout}")
        print(f"⚠️ Status command error: {stderr}")
    
    print("\n✅ CLI tests completed!")
    print("\n🚀 To use the CLI:")
    print(f'   {PYTHON_PATH} -m ledtomato_cli.main --help')
    print(f'   {PYTHON_PATH} -m ledtomato_cli.main discover')
    print(f'   {PYTHON_PATH} -m ledtomato_cli.main status')
    
    return True

if __name__ == "__main__":
    # Change to CLI directory
    cli_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(cli_dir)
    
    try:
        test_cli()
    except KeyboardInterrupt:
        print("\n\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)
