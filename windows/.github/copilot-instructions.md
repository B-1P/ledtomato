<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# LED Tomato WinUI3 Project

This is a WinUI3 application for controlling an ESP32-based LED strip that acts as a visual pomodoro timer.

## Project Structure
- **App.xaml/App.xaml.cs**: Application entry point and configuration
- **MainWindow.xaml/MainWindow.xaml.cs**: Main UI window with timer controls and device management
- **PomodoroTimer.cs**: Core timer logic with work/break sessions
- **EspDeviceManager.cs**: Network discovery and HTTP communication with ESP32 devices

## Key Features
- Automatic ESP32 device discovery on local network
- Visual pomodoro timer with customizable work/break durations
- LED strip progress indication and completion notifications
- Modern WinUI3 interface with cards and responsive design
- Portable EXE compilation for easy distribution

## Development Guidelines
- Use async/await patterns for all network operations
- Follow MVVM patterns where applicable
- Ensure proper error handling for network communications
- Use DispatcherQueue for UI thread marshaling
- Implement proper dispose patterns for HTTP clients

## ESP32 Communication
The app communicates with ESP32 devices via HTTP REST API:
- `/info` - Device identification endpoint
- `/led` - LED control endpoint accepting JSON payloads for progress, flash, and off modes
