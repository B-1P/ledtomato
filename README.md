# 🍅 LED Tomato - Smart Pomodoro Lighting System

A complete IoT Pomodoro timer system featuring an ESP32-based LED controller with multiple client applications.

![LED Tomato Demo](docs/demo.gif)

## Overview

LED Tomato combines the productivity benefits of the Pomodoro Technique with ambient lighting to create an immersive focus environment. The system consists of:

- **ESP32 Firmware**: Controls WS2812 LED strips with WiFi connectivity and REST API
- **Python CLI Client**: Command-line interface for controlling the Pomodoro timer with cycle mode
- **Windows WinUI App**: Modern Windows desktop application with full device integration
- **Web Interface**: Browser-based setup and control interface

## Client Applications

### Python CLI Client
- ✅ **Command Line Interface**: Full-featured terminal-based Pomodoro client
- ✅ **Device Discovery**: Automatic mDNS discovery of LED Tomato devices
- ✅ **Cycle Mode**: Continuous Pomodoro cycles with automatic session transitions
- ✅ **Interactive Mode**: Real-time monitoring and control
- ✅ **Custom Durations**: Set custom work and break session lengths
- ✅ **Session Logging**: Track completed sessions and statistics
- ✅ **Cross-Platform**: Windows, macOS, and Linux support
- ✅ **Rich UI**: Beautiful terminal interface with progress indicators

### Windows WinUI App  
- ✅ **Modern Windows Design**: Native Windows 11 styling and theming
- ✅ **Device Management**: ESP32 device discovery and connection
- ✅ **Visual Timer**: Circular progress ring with time display
- ✅ **Session Controls**: Start work, short break, and long break sessions
- ✅ **Cycle Mode**: Automatic Pomodoro cycle with session progression
- ✅ **Configuration**: Adjust timers, LED colors, brightness, and animations
- ✅ **Real-time Sync**: Synchronized with ESP32 device state
- ✅ **Session Notifications**: System notifications for session completion

## Features

### ESP32 Firmware
- ✅ **WiFi Setup**: Automatic AP mode for initial WiFi configuration
- ✅ **mDNS Support**: Access via `ledtomato.local` hostname
- ✅ **REST API**: Complete API for timer control and configuration
- ✅ **LED Control**: Support for WS2812 LED strips with animations
- ✅ **Breathing Animation**: Smooth breathing effect for break modes
- ✅ **Persistent Settings**: Configuration saved to EEPROM
- ✅ **Timer Management**: Full Pomodoro timer with work/break cycles

## Platform Support

### Command Line Interface
- ✅ **Python CLI** - Cross-platform terminal client with full Pomodoro functionality
- ✅ **Windows** - Native PowerShell and Command Prompt support
- ✅ **macOS/Linux** - Unix shell support with color output
- ✅ **Cycle Mode** - Continuous Pomodoro sessions with auto-advance

### Desktop Applications
- ✅ **Windows WinUI** - Native Windows 10/11 desktop application
- 🔄 **macOS** - Planned native macOS application
- 🔄 **Linux** - Planned GTK application

### Client-Specific Features

#### Python CLI Features
- **Rich Terminal UI**: Colorful progress bars and status displays
- **Session Statistics**: Track daily and weekly Pomodoro completion
- **Sound Notifications**: Audio cues for session transitions (optional)
- **Configuration Files**: Persistent settings and preferences
- **Keyboard Controls**: Press 'q' to stop sessions, interactive prompts

#### Windows WinUI Features
- **Native Windows 11 Styling**: Follows Windows design guidelines
- **System Integration**: Taskbar progress and system notifications
- **Device Management**: Live device discovery and connection status
- **Configurable Settings**: Adjust all timer and LED parameters
- **Session History**: View completed sessions and productivity stats

## Hardware Requirements

### ESP32 Setup
- **Microcontroller**: ESP32 DevKit (WROOM module)
- **LED Strip**: WS2812/WS2812B LED strip (30+ LEDs recommended)
- **Power Supply**: 5V power supply (capacity depends on LED count)
- **Connections**:
  - LED Data Pin → GPIO 5
  - LED VCC → 5V
  - LED GND → GND
  - ESP32 GND → Power Supply GND

### Wiring Diagram
```
ESP32 DevKit    WS2812 LED Strip    Power Supply
    5V     ←→       VCC        ←→      5V+
   GND     ←→       GND        ←→      5V-
  GPIO5    →        DATA
```

## Software Setup

### ESP32 Firmware

1. **Install PlatformIO**
   ```bash
   # Install PlatformIO CLI
   pip install platformio
   ```

2. **Build and Upload**
   ```bash
   cd esp32-firmware
   pio run --target upload
   pio device monitor
   ```

3. **Initial Setup**
   - On first boot, device creates AP: `LEDTomato-Setup`
   - Connect to AP with password: `pomodoro123`
   - Navigate to `192.168.4.1` in browser
   - Enter your WiFi credentials
   - Device will restart and connect to your network

### Python CLI Client

1. **Install Dependencies**
   ```bash
   cd python-cli
   pip install -r requirements.txt
   ```

2. **Install CLI Tool**
   ```bash
   # Install as editable package
   pip install -e .
   
   # Or use setup scripts
   # Windows
   setup.bat
   
   # macOS/Linux
   ./setup.sh
   ```

3. **Run CLI**
   ```bash
   # Interactive mode
   ledtomato
   
   # Direct commands
   ledtomato start work
   ledtomato cycle
   ledtomato status
   
   # With device discovery
   ledtomato --discover start work
   ```

### Windows WinUI App

1. **Prerequisites**
   - Windows 10 SDK version 19041 or later
   - .NET 8.0 SDK
   - Windows App SDK

2. **Build and Run**
   ```cmd
   cd windows
   dotnet build
   dotnet run
   ```

3. **Build for Distribution**
   ```cmd
   # Build self-contained
   build-app.bat
   
   # Or using PowerShell
   .\build-app.ps1
   ```
   
   See [windows/README.md](windows/README.md) for detailed Windows setup instructions.

## Configuration

### Hardware Configuration (`config.h`)
```cpp
#define LED_PIN 5           // GPIO pin for LED data
#define LED_COUNT 30        // Number of LEDs in strip
#define LED_BRIGHTNESS 128  // Default brightness (0-255)
#define AP_SSID "LEDTomato-Setup"
#define AP_PASSWORD "pomodoro123"
```

### Default Pomodoro Settings
- **Work Session**: 25 minutes (red color)
- **Short Break**: 5 minutes (green color)
- **Long Break**: 15 minutes (green color)
- **Work Mode**: Solid color (no animation)
- **Break Mode**: Breathing animation enabled

## API Reference

### Device Status
```http
GET /api/status
```
Returns device status including WiFi connection, timer state, and remaining time.

### Timer Control
```http
POST /api/pomodoro/start
Content-Type: application/x-www-form-urlencoded

type=work|short_break|long_break
```

```http
POST /api/pomodoro/stop
```

### Configuration
```http
GET /api/pomodoro/config
```

```http
POST /api/pomodoro/config
Content-Type: application/x-www-form-urlencoded

workTime=1500&shortBreakTime=300&longBreakTime=900&workColor=FF0000&breakColor=00FF00&workAnimation=false&breakAnimation=true&brightness=128
```

## Usage

### Python CLI Client

#### Interactive Mode
```bash
# Start interactive CLI
ledtomato

# Available commands in interactive mode:
🍅 > start      # Start individual sessions
🍅 > cycle      # Start continuous Pomodoro cycle
🍅 > stop       # Stop current session
🍅 > status     # Show device status
🍅 > config     # Show configuration
🍅 > monitor    # Monitor current session
🍅 > quit       # Exit application
```

#### Direct Commands
```bash
# Start specific sessions
ledtomato start work
ledtomato start short
ledtomato start long

# Start continuous cycle
ledtomato cycle

# Stop current session
ledtomato stop

# Get device status
ledtomato status

# Configure device
ledtomato config --work-time 30 --short-break 10 --brightness 200
```

#### Device Discovery
```bash
# Auto-discover devices
ledtomato --discover start work

# Specify device manually
ledtomato --device 192.168.1.100 cycle
```

### Windows WinUI App

1. **Connect to Device**
   - Launch the application
   - Use the device dropdown to select your ESP32
   - Connection status will show "Connected" when ready

2. **Basic Timer Control**
   - Use "Start/Pause" for manual timer control
   - Use "Reset" to reset current session
   - Individual session buttons for quick starts

3. **Cycle Mode**
   - Click "Start Cycle" to begin continuous Pomodoro sessions
   - Enable "Auto-advance through breaks" to skip break confirmations
   - Monitor cycle progress in the status display

4. **Configuration**
   - Adjust work and break durations with sliders
   - Set LED brightness and enable/disable animations
   - Settings are automatically synced to the ESP32 device

### First Time Setup

1. **Power on ESP32** - Device will create WiFi access point
2. **Connect to AP** - Join `LEDTomato-Setup` network
3. **Configure WiFi** - Visit setup page and enter your WiFi credentials
4. **Install Client** - Set up Python CLI or Windows app
5. **Connect Client** - Clients will automatically discover the device

## Troubleshooting

### Common Issues

**Device not found by clients:**
- Ensure device and computer are on same WiFi network
- Try accessing `http://ledtomato.local` directly in browser
- Check device logs via PlatformIO monitor
- For Python CLI, use `ledtomato --discover` to scan network

**LEDs not working:**
- Verify wiring connections
- Check power supply capacity (60mA per LED at full brightness)
- Confirm LED_PIN and LED_COUNT in config.h

**WiFi connection issues:**
- Reset device to re-enter AP mode
- Check WiFi credentials in setup page
- Verify network supports 2.4GHz (ESP32 requirement)

**Python CLI issues:**
- Ensure Python 3.7+ is installed
- Install dependencies: `pip install -r requirements.txt`
- Check firewall settings for mDNS discovery

**Windows app issues:**
- Ensure Windows 10 version 19041 or later
- Install Windows App SDK if missing
- Run as administrator if device discovery fails

### Debug Mode

Enable debug output by setting `DEBUG_SERIAL 1` in `config.h`:
```bash
pio device monitor
```

## Customization

### Python CLI Configuration

Create a config file at `~/.ledtomato/config.yaml`:
```yaml
sound:
  enabled: true
  work_start_sound: /path/to/work_start.wav
  break_start_sound: /path/to/break_start.wav
  session_end_sound: /path/to/session_end.wav

display:
  refresh_interval: 1.0
  show_progress_bar: true
  
logging:
  session_log_enabled: true
  log_file: ~/.ledtomato/sessions.log
```

### Adding New LED Animations

1. Create animation function in `main.cpp`:
```cpp
void myCustomAnimation(uint32_t color) {
  // Your animation code here
}
```

2. Add animation option to config and call in `updateLEDs()`

### Extending the API

Add new endpoints in `setupRoutes()` function:
```cpp
server.on("/api/custom", HTTP_GET, handleCustomFunction);
```

### Extending Client Applications

#### Python CLI
Add new commands by extending the CLI in `python-cli/ledtomato_cli/main.py`:
```python
@cli.command()
@click.option('--device', '-d', help='Device IP address')
def my_custom_command(device):
    """Custom command description"""
    # Your implementation here
```

#### Windows WinUI
Extend the Windows app by adding new controls in `windows/MainWindow.xaml` and corresponding logic in `windows/MainWindow.xaml.cs`.

### Mobile App Themes

Modify styles in React Native components to match your preferences:
```javascript
const styles = StyleSheet.create({
  // Your custom styles
});
```

## Project Structure

```
ledtomato/
├── esp32-firmware/          # ESP32 firmware source code
│   ├── src/main.cpp        # Main firmware implementation
│   ├── include/config.h    # Hardware configuration
│   └── platformio.ini      # PlatformIO project config
├── python-cli/             # Python command-line client
│   ├── ledtomato_cli/      # Main CLI package
│   ├── requirements.txt    # Python dependencies
│   └── pyproject.toml      # Python project configuration
├── windows/                # Windows WinUI desktop application
│   ├── MainWindow.xaml     # UI layout
│   ├── MainWindow.xaml.cs  # UI logic
│   ├── PomodoroTimer.cs    # Timer implementation
│   ├── EspDeviceManager.cs # ESP32 communication
│   └── LedTomatoWinUI.csproj # .NET project file
└── README.md               # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Pomodoro Technique® by Francesco Cirillo
- Adafruit NeoPixel library
- React Native community
- PlatformIO platform

## Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the API documentation
- Check client-specific README files:
  - [Python CLI README](python-cli/README.md)
  - [Windows App README](windows/README.md)

---

**Happy focusing! 🍅**
