# 🪟 LED Tomato - Windows Setup Guide

This guide covers setting up the LED Tomato React Native app for Windows using react-native-windows.

## Prerequisites

### Required Software

1. **Visual Studio 2019/2022** with the following workloads:
   - Desktop development with C++
   - Game development with C++ (for DirectX support)
   - Universal Windows Platform development

2. **Windows 10/11 SDK** (latest version)
   - Available through Visual Studio Installer
   - Or download from Microsoft Developer site

3. **Node.js** (version 16 or higher)
   - Download from [nodejs.org](https://nodejs.org/)
   - Use LTS version for stability

4. **Git** for version control
   - Download from [git-scm.com](https://git-scm.com/)

### Optional but Recommended

- **Windows Terminal** for better command-line experience
- **Visual Studio Code** for development

## Setup Instructions

### 1. Initialize React Native Windows

Run the Windows setup script:
```cmd
setup-windows.bat
```

Or manually:
```cmd
cd react-native-client
npx react-native-windows-init --overwrite --logging
```

### 2. Install Dependencies

```cmd
cd react-native-client
npm install
```

### 3. Build and Run

Use the build script:
```cmd
build-app.bat
# Select option 3 or 4 for Windows Debug/Release
```

Or manually:
```cmd
npx react-native run-windows --arch x64 --logging
```

## Windows-Specific Features

### Native Integrations

- **Toast Notifications**: System notifications when Pomodoro sessions start/end
- **System Tray**: Minimize to system tray (planned feature)
- **Windows Styling**: Native Windows 11 design elements
- **Keyboard Shortcuts**: Windows-standard shortcuts

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | Start new Pomodoro session |
| `Ctrl+S` | Stop current session |
| `Ctrl+,` | Open settings |
| `F11` | Toggle fullscreen |
| `Esc` | Close dialogs |
| `Space` | Start/stop timer |

### Windows Theme Integration

The app automatically adapts to:
- Windows light/dark theme
- System accent colors
- Native fonts (Segoe UI)
- Windows corner radius and elevation

## Troubleshooting

### Common Build Issues

**Error: "MSBuild not found"**
```cmd
# Solution: Install Visual Studio with C++ tools
# Or set MSBuild path manually:
set MSBUILD_PATH="C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\MSBuild\Current\Bin\MSBuild.exe"
```

**Error: "Windows SDK not found"**
```cmd
# Solution: Install Windows 10/11 SDK via Visual Studio Installer
# Or set SDK path:
set WindowsSDKDir="C:\Program Files (x86)\Windows Kits\10\"
```

**Error: "React Native Windows init failed"**
```cmd
# Clear cache and retry:
npx react-native-clean-project
npm cache clean --force
npx react-native-windows-init --overwrite
```

**Build hangs or fails**
```cmd
# Try these solutions:
# 1. Run as Administrator
# 2. Disable antivirus temporarily
# 3. Clear Visual Studio cache:
devenv /resetuserdata
```

### Performance Issues

**App starts slowly:**
- Use Release build for better performance
- Enable Windows performance mode
- Close unnecessary background apps

**High memory usage:**
- This is normal for development builds
- Release builds are more memory efficient
- Monitor with Task Manager

### Debugging

**Enable verbose logging:**
```cmd
npx react-native run-windows --arch x64 --logging --verbose
```

**View app logs:**
```cmd
npx react-native log-windows
```

**Debug in Visual Studio:**
1. Open `windows/YourApp.sln` in Visual Studio
2. Set breakpoints in C++ code
3. Press F5 to debug

## Windows App Features

### System Integration

- **File Associations**: Associate .pomodoro files with the app
- **Jump Lists**: Quick access to recent timers
- **Live Tiles**: Show current session status (Windows 10)
- **Cortana Integration**: Voice commands for timer control

### Packaging

Create a Windows app package:
```cmd
npx react-native run-windows --release --bundle
```

For Microsoft Store:
```cmd
npx react-native bundle --platform windows --dev false --entry-file index.js --bundle-output windows/Bundle/index.windows.bundle
```

### Distribution

**Development Distribution:**
- Share the built `.exe` file
- Include all runtime dependencies

**Microsoft Store:**
- Create App Package (.appx)
- Submit through Partner Center
- Follow store certification requirements

## Configuration

### Windows-Specific Settings

The app includes Windows-specific configuration in `windows/App.manifest`:

```xml
<application>
  <windowsSettings>
    <dpiAware>true</dpiAware>
    <dpiAwareness>PerMonitorV2</dpiAwareness>
  </windowsSettings>
</application>
```

### Registry Settings

The app may create registry entries for:
- User preferences
- File associations
- System integration

Location: `HKEY_CURRENT_USER\Software\LEDTomato`

## Advanced Usage

### Custom Native Modules

To add Windows-specific functionality:

1. Create native module in `windows/` directory
2. Implement C++ bridge code
3. Register module in `MainReactNativeHost.cpp`

Example structure:
```
windows/
├── LEDTomatoClient/
├── LEDTomatoClient.Package/
├── LEDTomatoClient.sln
└── ReactNativeModules/
    └── CustomWindowsModule/
```

### Background Tasks

For system tray and background operation:
```cpp
// In App.xaml.cpp
void App::OnSuspending(Platform::Object^ sender, Windows::ApplicationModel::SuspendingEventArgs^ e)
{
    // Continue timer in background
}
```

## Support

For Windows-specific issues:
1. Check [React Native Windows GitHub](https://github.com/microsoft/react-native-windows)
2. Review Windows development documentation
3. Join the React Native Windows Discord

## Next Steps

- **System Tray Integration**: Minimize to tray functionality
- **Live Tiles**: Real-time session status
- **Cortana Commands**: Voice control integration
- **Multiple Monitor Support**: Position on different screens
- **Windows Hello**: Secure settings access

---

**Windows development made easy! 🪟🍅**
