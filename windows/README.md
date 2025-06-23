# LED Tomato - WinUI3 Pomodoro Timer

A modern Windows application for controlling an ESP32-based LED strip that acts as a visual pomodoro timer. Built with WinUI3 for a native Windows experience.

## Features

- 🍅 **Pomodoro Timer**: Customizable work and break sessions
- 💡 **LED Strip Control**: Visual progress indication on ESP32-controlled LED strips
- 🔍 **Auto Discovery**: Automatically finds ESP32 devices on your local network
- 🎨 **Modern UI**: Clean, responsive WinUI3 interface
- 📦 **Portable**: Single EXE deployment, no installation required

## Requirements

- Windows 10 version 1809 (build 17763) or later
- .NET 8.0 Runtime (included in self-contained builds)
- ESP32 device running compatible LED Tomato firmware

## Quick Start

1. **Download** the latest release from the releases page
2. **Run** `LedTomatoWinUI.exe`
3. **Connect** your ESP32 device to the same network
4. **Click Refresh** to discover your device
5. **Start** your pomodoro session!

## Building from Source

### Prerequisites
- Visual Studio 2022 with WinUI3 workload
- .NET 8.0 SDK
- Windows App SDK

### Build Steps
```powershell
# Clone the repository
git clone https://github.com/your-username/led-tomato-windows.git
cd led-tomato-windows

# Restore packages
dotnet restore

# Build the application
dotnet build --configuration Release

# Create portable EXE
dotnet publish --configuration Release --runtime win-x64 --self-contained true --output ./publish
```

## ESP32 Setup

Your ESP32 should expose the following HTTP endpoints:

- `GET /info` - Returns device information (should contain "led-tomato" or "pomodoro")
- `POST /led` - Accepts JSON payload for LED control

### LED Control API

The application sends JSON payloads to control the LED strip:

```json
{
  "mode": "progress",
  "progress": 0.5,
  "color": { "r": 255, "g": 0, "b": 0 },
  "litLeds": 15
}
```

Supported modes:
- `progress` - Show timer progress
- `flash` - Flash completion notification
- `off` - Turn off all LEDs

## Configuration

- **Work Duration**: 1-60 minutes (default: 25 minutes)
- **Break Duration**: 1-30 minutes (default: 5 minutes)
- **LED Count**: Automatically calculated based on strip length

## Architecture

- **PomodoroTimer**: Core timer logic and session management
- **EspDeviceManager**: Network discovery and HTTP communication
- **MainWindow**: UI controller and event handling
- **App**: Application lifecycle management

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Troubleshooting

### Device Not Found
- Ensure ESP32 is connected to the same network
- Check that the ESP32 firmware includes the `/info` endpoint
- Try manually refreshing the device list

### Connection Issues
- Verify ESP32 is responding to HTTP requests
- Check Windows Firewall settings
- Ensure ESP32 and PC are on the same subnet

### Build Issues
- Install Windows App SDK from Microsoft
- Ensure .NET 8.0 SDK is installed
- Check Visual Studio has WinUI3 components installed
