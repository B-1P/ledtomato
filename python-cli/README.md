# LED Tomato Python CLI Client

A comprehensive command-line interface for controlling your LED Tomato Pomodoro Timer device.

## Features

- 🔍 **Auto-discovery**: Automatically find LED Tomato devices on your network
- ⏰ **Timer Control**: Start, stop, and monitor Pomodoro sessions
- 🎨 **Rich Interface**: Beautiful terminal UI with progress bars and colors
- 🔧 **Configuration**: Manage device settings from the command line
- 📊 **Session Monitoring**: Real-time monitoring with live updates
- 🎵 **Audio Cues**: Play sounds when sessions start/end (optional)
- 💾 **Session Logging**: Track your productivity sessions
- 🔄 **Interactive Mode**: Full-featured interactive shell

## Installation

### Windows Installation (Recommended)

If Python is not in your PATH, you can use our Windows setup scripts:

```batch
# Run the setup script
setup.bat

# Or use PowerShell
setup.ps1
```

The setup script will:
- Find your Python installation (even if not in PATH)
- Create a virtual environment
- Install all dependencies
- Install the CLI in development mode

After setup, use the wrapper scripts:
```batch
# Using batch script
ledtomato.bat --help
ledtomato.bat discover
ledtomato.bat start --type work

# Using PowerShell script
.\ledtomato.ps1 --help
.\ledtomato.ps1 discover
```

### Manual Windows Installation

If you know your Python path:
```batch
# Replace with your actual Python path
set PYTHON_PATH="C:/Users/YourName/AppData/Local/Microsoft/WindowsApps/python3.11.exe"

# Install dependencies
%PYTHON_PATH% -m pip install -r requirements.txt

# Install CLI
%PYTHON_PATH% -m pip install -e .

# Run CLI
%PYTHON_PATH% -m ledtomato_cli.main --help
```

### Option 1: Install from source (Linux/Mac)

```bash
# Clone the repository (if not already done)
git clone https://github.com/yourusername/ledtomato.git
cd ledtomato/python-cli

# Install in development mode
pip install -e .
```

### Option 2: Install dependencies manually

```bash
cd python-cli
pip install -r requirements.txt
```

### Option 3: Using pipx (Isolated installation)

```bash
pipx install ./python-cli
```

## Quick Start (Windows)

1. **Setup**: Run `setup.bat` or `setup.ps1` from the `python-cli` directory
2. **Test**: Run `ledtomato.bat --help` to verify installation
3. **Discover devices**: Run `ledtomato.bat discover`
4. **Start timer**: Run `ledtomato.bat start --type work`
5. **Interactive mode**: Run `ledtomato.bat` (no arguments)

### Windows Wrapper Scripts

The project includes convenient wrapper scripts for Windows:
- `ledtomato.bat` - Batch script for Command Prompt
- `ledtomato.ps1` - PowerShell script
- `setup.bat` - Automatic setup for Command Prompt
- `setup.ps1` - Automatic setup for PowerShell
- `test_cli.py` - Test script to verify installation

## Usage

### Command Line Interface

After installation, you can use the CLI with the `ledtomato` or `tomato` command:

```bash
# Auto-discover and connect to device
ledtomato

# Start a work session
ledtomato start --type work

# Start with custom duration
ledtomato start --type work --duration 30

# Stop current session
ledtomato stop

# Show device status
ledtomato status

# Discover devices on network
ledtomato discover

# Configure device settings
ledtomato config --work-time 25 --brightness 200

# Specify device manually
ledtomato --device 192.168.1.100 status
```

### Interactive Mode

Launch interactive mode for full control:

```bash
ledtomato
```

Available commands in interactive mode:
- `start` - Start a timer session
- `stop` - Stop current session
- `status` - Show device status
- `config` - Show device configuration
- `monitor` - Monitor session with live updates
- `help` - Show help information
- `quit` - Exit application

### Configuration

The CLI creates configuration files in your user directory:
- **Config**: `~/.config/ledtomato-cli/config.json`
- **Cache**: `~/.cache/ledtomato-cli/devices.json`
- **Logs**: `~/.local/share/ledtomato-cli/sessions.log`

#### Config File Example

```json
{
  "pomodoro": {
    "work_time": 25,
    "short_break": 5,
    "long_break": 15,
    "work_color": "#FF0000",
    "break_color": "#00FF00",
    "brightness": 128,
    "work_animation": false,
    "break_animation": true
  },
  "sound": {
    "enabled": true,
    "volume": 0.8,
    "work_start_sound": null,
    "break_start_sound": null,
    "session_end_sound": null
  },
  "display": {
    "show_progress": true,
    "show_ascii_tomato": true,
    "color_output": true,
    "compact_mode": false,
    "refresh_interval": 1.0
  },
  "network": {
    "discovery_timeout": 10,
    "request_timeout": 5,
    "default_device": null,
    "preferred_devices": []
  }
}
```

## Command Reference

### Global Options
- `--device, -d` - Specify device IP address
- `--discover` - Auto-discover devices
- `--config, -c` - Path to config file
- `--verbose, -v` - Verbose output

### Commands

#### `start` - Start Timer Session
```bash
ledtomato start [OPTIONS]
```
Options:
- `--type, -t` - Timer type: work, short, long (default: work)
- `--duration` - Custom duration in minutes

#### `stop` - Stop Current Session
```bash
ledtomato stop [OPTIONS]
```

#### `status` - Show Device Status
```bash
ledtomato status [OPTIONS]
```

#### `discover` - Find Devices
```bash
ledtomato discover
```

#### `config` - Configure Device
```bash
ledtomato config [OPTIONS]
```
Options:
- `--work-time` - Work session duration (minutes)
- `--short-break` - Short break duration (minutes)
- `--long-break` - Long break duration (minutes)
- `--work-color` - Work session color (hex)
- `--break-color` - Break session color (hex)
- `--brightness` - LED brightness (0-255)

## Examples

### Basic Usage
```bash
# Start a 25-minute work session
ledtomato start

# Start a 30-minute work session
ledtomato start --duration 30

# Start a short break
ledtomato start --type short

# Monitor current session
ledtomato status
```

### Device Discovery
```bash
# Find all LED Tomato devices
ledtomato discover

# Connect to specific device
ledtomato --device 192.168.1.100 status
```

### Configuration
```bash
# Set work time to 30 minutes
ledtomato config --work-time 30

# Change colors and brightness
ledtomato config --work-color FF0000 --break-color 00FF00 --brightness 200

# Configure multiple settings
ledtomato config --work-time 25 --short-break 5 --long-break 15 --brightness 150
```

### Interactive Session
```bash
# Start interactive mode
ledtomato

# In interactive mode:
🍅 > start
Select timer type [work/short/long] (default: work): work
Use custom duration? [y/N]: n
✅ Started Work session
Monitor this session? [Y/n]: y
📊 Monitoring session... (Press Ctrl+C to stop monitoring)
```

## Troubleshooting

### Device Not Found
```bash
# Check network connectivity
ping 192.168.4.1  # Default AP mode IP

# Manually specify device
ledtomato --device 192.168.4.1 status

# Scan for devices
ledtomato discover
```

### Connection Issues
```bash
# Test with verbose output
ledtomato --verbose status

# Check device is running
curl http://192.168.4.1/api/status
```

### Sound Issues
- Install audio dependencies: `pip install playsound`
- Check audio files exist in config
- Verify system audio is working

## Dependencies

Core dependencies:
- `click` - Command-line interface framework
- `requests` - HTTP requests
- `rich` - Terminal formatting and progress bars
- `zeroconf` - mDNS device discovery
- `colorama` - Cross-platform colored terminal text
- `pydantic` - Data validation
- `python-dateutil` - Date/time utilities
- `appdirs` - Platform-specific directories

Optional dependencies:
- `playsound` - Audio notification support

## Development

### Running from Source
```bash
cd python-cli
python -m ledtomato_cli.main --help
```

### Installing in Development Mode
```bash
pip install -e .
```

### Code Style
The project uses:
- `black` for code formatting
- `isort` for import sorting
- `flake8` for linting
- `mypy` for type checking

## License

MIT License - see LICENSE file for details.
