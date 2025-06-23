"""Configuration management for LED Tomato CLI"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import appdirs


@dataclass
class PomodoroConfig:
    """Pomodoro timer configuration"""
    work_time: int = 25  # minutes
    short_break: int = 5  # minutes
    long_break: int = 15  # minutes
    work_color: str = "#FF0000"  # red
    break_color: str = "#00FF00"  # green
    brightness: int = 128  # 0-255
    work_animation: bool = False
    break_animation: bool = True


@dataclass
class SoundConfig:
    """Sound configuration"""
    enabled: bool = True
    work_start_sound: Optional[str] = None
    break_start_sound: Optional[str] = None
    session_end_sound: Optional[str] = None
    volume: float = 0.8  # 0.0-1.0


@dataclass
class DisplayConfig:
    """Display configuration"""
    show_progress: bool = True
    show_ascii_tomato: bool = True
    color_output: bool = True
    compact_mode: bool = False
    refresh_interval: float = 1.0  # seconds


@dataclass
class NetworkConfig:
    """Network configuration"""
    discovery_timeout: int = 10  # seconds
    request_timeout: int = 5  # seconds
    default_device: Optional[str] = None
    preferred_devices: list = None
    
    def __post_init__(self):
        if self.preferred_devices is None:
            self.preferred_devices = []


class Config:
    """Main configuration class"""
    
    def __init__(self):
        self.pomodoro = PomodoroConfig()
        self.sound = SoundConfig()
        self.display = DisplayConfig()
        self.network = NetworkConfig()
        
        # App directories
        self.app_name = "ledtomato-cli"
        self.config_dir = Path(appdirs.user_config_dir(self.app_name))
        self.data_dir = Path(appdirs.user_data_dir(self.app_name))
        self.cache_dir = Path(appdirs.user_cache_dir(self.app_name))
        
        # Ensure directories exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.config_file = self.config_dir / "config.json"
    
    @classmethod
    def load(cls, config_path: Optional[str] = None) -> 'Config':
        """Load configuration from file"""
        config = cls()
        
        if config_path:
            config_file = Path(config_path)
        else:
            config_file = config.config_file
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    data = json.load(f)
                
                # Load each section
                if 'pomodoro' in data:
                    config.pomodoro = PomodoroConfig(**data['pomodoro'])
                if 'sound' in data:
                    config.sound = SoundConfig(**data['sound'])
                if 'display' in data:
                    config.display = DisplayConfig(**data['display'])
                if 'network' in data:
                    config.network = NetworkConfig(**data['network'])
                    
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
        
        return config
    
    def save(self, config_path: Optional[str] = None) -> bool:
        """Save configuration to file"""
        if config_path:
            config_file = Path(config_path)
        else:
            config_file = self.config_file
        
        try:
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'pomodoro': asdict(self.pomodoro),
                'sound': asdict(self.sound),
                'display': asdict(self.display),
                'network': asdict(self.network)
            }
            
            with open(config_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get_device_cache_file(self) -> Path:
        """Get path to device cache file"""
        return self.cache_dir / "devices.json"
    
    def get_session_log_file(self) -> Path:
        """Get path to session log file"""
        return self.data_dir / "sessions.log"
    
    def load_device_cache(self) -> Dict[str, Any]:
        """Load cached device information"""
        cache_file = self.get_device_cache_file()
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}
    
    def save_device_cache(self, devices: Dict[str, Any]) -> bool:
        """Save device information to cache"""
        cache_file = self.get_device_cache_file()
        try:
            with open(cache_file, 'w') as f:
                json.dump(devices, f, indent=2)
            return True
        except Exception:
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            'pomodoro': asdict(self.pomodoro),
            'sound': asdict(self.sound),
            'display': asdict(self.display),
            'network': asdict(self.network)
        }
    
    def reset_to_defaults(self) -> None:
        """Reset all configuration to defaults"""
        self.pomodoro = PomodoroConfig()
        self.sound = SoundConfig()
        self.display = DisplayConfig()
        self.network = NetworkConfig()
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        # Validate pomodoro settings
        if self.pomodoro.work_time <= 0:
            errors.append("Work time must be positive")
        if self.pomodoro.short_break <= 0:
            errors.append("Short break time must be positive")
        if self.pomodoro.long_break <= 0:
            errors.append("Long break time must be positive")
        if not (0 <= self.pomodoro.brightness <= 255):
            errors.append("Brightness must be between 0 and 255")
        
        # Validate sound settings
        if not (0.0 <= self.sound.volume <= 1.0):
            errors.append("Volume must be between 0.0 and 1.0")
        
        # Validate display settings
        if self.display.refresh_interval <= 0:
            errors.append("Refresh interval must be positive")
        
        # Validate network settings
        if self.network.discovery_timeout <= 0:
            errors.append("Discovery timeout must be positive")
        if self.network.request_timeout <= 0:
            errors.append("Request timeout must be positive")
        
        return errors
