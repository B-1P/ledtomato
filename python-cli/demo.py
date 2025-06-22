#!/usr/bin/env python3
"""
LED Tomato CLI Demo Script
Demonstrates the CLI functionality without requiring a physical device
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the CLI module to path
sys.path.insert(0, str(Path(__file__).parent / "ledtomato_cli"))

from ledtomato_cli.display import Display
from ledtomato_cli.config import Config

def demo_display():
    """Demo the display functionality"""
    display = Display(verbose=True)
    
    print("🍅 LED Tomato CLI Display Demo")
    print("=" * 50)
    
    # Show banner
    display.show_banner()
    
    # Demo messages
    display.show_info("This is an info message")
    display.show_success("This is a success message")
    display.show_warning("This is a warning message")
    display.show_error("This is an error message")
    
    # Demo status (mock data)
    mock_status = {
        'hostname': 'ledtomato',
        'wifiConnected': True,
        'pomodoro': {
            'state': 1,  # Working
            'running': True,
            'remaining': 900,  # 15 minutes
            'elapsed': 600,    # 10 minutes
            'duration': 1500   # 25 minutes total
        }
    }
    
    print("\n📊 Status Display Demo:")
    display.show_status(mock_status, "192.168.1.100")
    
    # Demo configuration display
    mock_config = {
        'workTime': 1500,      # 25 minutes
        'shortBreakTime': 300, # 5 minutes
        'longBreakTime': 900,  # 15 minutes
        'workColor': 'FF0000',
        'breakColor': '00FF00',
        'brightness': 128,
        'workAnimation': False,
        'breakAnimation': True
    }
    
    print("\n⚙️ Configuration Display Demo:")
    display.show_config(mock_config)
    
    # Demo device list
    mock_devices = [
        {'ip': '192.168.1.100', 'hostname': 'ledtomato-01', 'wifi_connected': True},
        {'ip': '192.168.4.1', 'hostname': 'ledtomato-02', 'wifi_connected': False}
    ]
    
    print("\n🔍 Device Discovery Demo:")
    display.show_device_list(mock_devices)
    
    print("\n✅ Display demo complete!")

def demo_config():
    """Demo the configuration functionality"""
    print("\n🔧 Configuration Demo")
    print("=" * 30)
    
    # Create a temporary config
    config = Config()
    
    print("📁 Configuration directories:")
    print(f"  Config: {config.config_dir}")
    print(f"  Data: {config.data_dir}")
    print(f"  Cache: {config.cache_dir}")
    
    print("\n⚙️ Default configuration:")
    config_dict = config.to_dict()
    for section, settings in config_dict.items():
        print(f"  [{section}]")
        for key, value in settings.items():
            print(f"    {key}: {value}")
    
    # Validate config
    errors = config.validate()
    if errors:
        print(f"\n❌ Configuration errors: {errors}")
    else:
        print("\n✅ Configuration is valid")

async def demo_commands():
    """Demo the CLI commands (without actual device)"""
    print("\n🖥️ CLI Commands Demo")
    print("=" * 30)
    
    commands = [
        ("discover", "Find LED Tomato devices on network"),
        ("status", "Show device status and timer information"),
        ("start --type work", "Start a 25-minute work session"),
        ("start --type short", "Start a 5-minute short break"),
        ("start --type long", "Start a 15-minute long break"),
        ("start --type work --duration 30", "Start a custom 30-minute work session"),
        ("stop", "Stop the current timer session"),
        ("config --work-time 30", "Set work time to 30 minutes"),
        ("config --brightness 200", "Set LED brightness to 200"),
        ("config --work-color FF0000", "Set work color to red"),
        ("--device 192.168.1.100 status", "Connect to specific device"),
        ("--verbose status", "Show detailed output"),
    ]
    
    print("Available commands:")
    for cmd, desc in commands:
        print(f"  ledtomato {cmd:<30} # {desc}")
    
    print("\n🔄 Interactive mode:")
    print("  ledtomato                          # Start interactive shell")
    print("  Available in interactive mode:")
    print("    start, stop, status, config, monitor, help, quit")

def main():
    """Run the demo"""
    try:
        print("🍅 LED Tomato Python CLI Demo")
        print("=" * 60)
        print("This demo shows the CLI functionality without requiring a device.")
        print("=" * 60)
        
        # Demo display
        demo_display()
        
        # Demo config
        demo_config()
        
        # Demo commands
        asyncio.run(demo_commands())
        
        print("\n" + "=" * 60)
        print("🚀 To use the actual CLI:")
        if os.name == 'nt':  # Windows
            print("  ledtomato.bat --help")
            print("  ledtomato.bat discover")
            print("  ledtomato.bat start --type work")
        else:  # Linux/Mac
            print("  ledtomato --help")
            print("  ledtomato discover")
            print("  ledtomato start --type work")
        
        print("\n🔗 Make sure your LED Tomato device is connected to the network!")
        print("   Default AP mode: http://192.168.4.1")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
