# 🍅 LED Tomato - Smart Pomodoro Lighting System

A complete IoT Pomodoro timer system featuring an ESP32-based LED controller and React Native mobile app.

![LED Tomato Demo](docs/demo.gif)

## Overview

LED Tomato combines the productivity benefits of the Pomodoro Technique with ambient lighting to create an immersive focus environment. The system consists of:

- **ESP32 Firmware**: Controls WS2812 LED strips with WiFi connectivity and REST API
- **React Native App**: Mobile interface for controlling the Pomodoro timer and LED settings
- **Web Interface**: Browser-based setup and control interface

## Features

### ESP32 Firmware
- ✅ **WiFi Setup**: Automatic AP mode for initial WiFi configuration
- ✅ **mDNS Support**: Access via `ledtomato.local` hostname
- ✅ **REST API**: Complete API for timer control and configuration
- ✅ **LED Control**: Support for WS2812 LED strips with animations
- ✅ **Breathing Animation**: Smooth breathing effect for break modes
- ✅ **Persistent Settings**: Configuration saved to EEPROM
- ✅ **Timer Management**: Full Pomodoro timer with work/break cycles

### React Native App
- ✅ **Device Discovery**: Automatic detection of LED Tomato devices
- ✅ **Visual Timer**: Circular progress indicator with time remaining
- ✅ **Color Customization**: Pick colors for work and break modes
- ✅ **Animation Control**: Enable/disable breathing animations
- ✅ **Audio Cues**: Sound notifications for mode changes
- ✅ **Settings Persistence**: Save preferences locally
- ✅ **Network Status**: Connection status and device information
- ✅ **Cross-Platform**: Android, iOS, and Windows support
- ✅ **Windows Integration**: Native Windows 11 styling and toast notifications

## Platform Support

### Mobile Platforms
- ✅ **Android** (API 21+) - Full support with native Android features
- ✅ **iOS** (iOS 11+) - Full support with native iOS features

### Desktop Platforms  
- ✅ **Windows** (Windows 10/11) - Native Windows app with system integration
- 🔄 **macOS** - Planned support via React Native macOS
- 🔄 **Linux** - Under consideration

### Windows-Specific Features
- **Native Windows 11 Styling**: Follows Windows design guidelines
- **Toast Notifications**: System notifications for session changes
- **Keyboard Shortcuts**: Standard Windows shortcuts (Ctrl+N, Ctrl+S, etc.)
- **System Tray**: Minimize to tray (planned)
- **File Associations**: Open .pomodoro files directly
- **Microsoft Store**: Ready for store distribution

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

### React Native App

1. **Install Dependencies**
   ```bash
   cd react-native-client
   npm install
   ```

2. **Android Setup**
   ```bash
   # Make sure Android SDK is installed
   npx react-native run-android
   ```

3. **iOS Setup**
   ```bash
   cd ios && pod install && cd ..
   npx react-native run-ios
   ```

4. **Windows Setup**
   ```cmd
   # Initialize Windows support
   setup-windows.bat
   
   # Or manually
   npx react-native-windows-init --overwrite
   npx react-native run-windows --arch x64
   ```
   
   See [WINDOWS-SETUP.md](WINDOWS-SETUP.md) for detailed Windows setup instructions.

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

### First Time Setup

1. **Power on ESP32** - Device will create WiFi access point
2. **Connect to AP** - Join `LEDTomato-Setup` network
3. **Configure WiFi** - Visit setup page and enter your WiFi credentials
4. **Install Mobile App** - Build and install the React Native app
5. **Connect App** - App will automatically discover the device

### Daily Use

1. **Start Session** - Use mobile app to start work/break sessions
2. **Visual Feedback** - LEDs will display current mode with appropriate colors
3. **Audio Cues** - App provides sound notifications for mode changes
4. **Customize Settings** - Adjust timers, colors, and animations via app

## Troubleshooting

### Common Issues

**Device not found by app:**
- Ensure device and phone are on same WiFi network
- Try accessing `http://ledtomato.local` directly in browser
- Check device logs via PlatformIO monitor

**LEDs not working:**
- Verify wiring connections
- Check power supply capacity (60mA per LED at full brightness)
- Confirm LED_PIN and LED_COUNT in config.h

**WiFi connection issues:**
- Reset device to re-enter AP mode
- Check WiFi credentials in setup page
- Verify network supports 2.4GHz (ESP32 requirement)

### Debug Mode

Enable debug output by setting `DEBUG_SERIAL 1` in `config.h`:
```bash
pio device monitor
```

## Customization

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

### Mobile App Themes

Modify styles in React Native components to match your preferences:
```javascript
const styles = StyleSheet.create({
  // Your custom styles
});
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

---

**Happy focusing! 🍅**
