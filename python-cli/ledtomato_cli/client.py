"""LED Tomato API Client"""

import asyncio
from typing import Dict, Optional, Any
import aiohttp
import json


class LEDTomatoClient:
    """Client for communicating with LED Tomato device"""
    
    def __init__(self, host: str, port: int = 80, timeout: int = 10):
        """Initialize client
        
        Args:
            host: Device IP address or hostname
            port: Device port (default: 80)
            timeout: Request timeout in seconds
        """
        self.host = host.replace('http://', '').replace('https://', '')
        self.port = port
        self.timeout = timeout
        self.base_url = f"http://{self.host}:{self.port}"
        
    async def ping(self) -> bool:
        """Test connection to device"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(f"{self.base_url}/api/status") as response:
                    return response.status == 200
        except Exception:
            return False
    
    async def get_status(self) -> Optional[Dict[str, Any]]:
        """Get current device status"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.get(f"{self.base_url}/api/status") as response:
                    if response.status == 200:
                        return await response.json()
        except Exception as e:
            print(f"Error getting status: {e}")
        return None
    
    async def get_config(self) -> Optional[Dict[str, Any]]:
        """Get current device configuration"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.get(f"{self.base_url}/api/pomodoro/config") as response:
                    if response.status == 200:
                        return await response.json()
        except Exception as e:
            print(f"Error getting config: {e}")
        return None
    
    async def update_config(self, config: Dict[str, Any]) -> bool:
        """Update device configuration"""
        try:
            # Convert to form data
            form_data = aiohttp.FormData()
            form_data.add_field('workTime', str(config.get('workTime', 1500)))
            form_data.add_field('shortBreakTime', str(config.get('shortBreakTime', 300)))
            form_data.add_field('longBreakTime', str(config.get('longBreakTime', 900)))
            form_data.add_field('workColor', str(config.get('workColor', 'FF0000')).replace('#', ''))
            form_data.add_field('breakColor', str(config.get('breakColor', '00FF00')).replace('#', ''))
            form_data.add_field('workAnimation', str(config.get('workAnimation', False)).lower())
            form_data.add_field('breakAnimation', str(config.get('breakAnimation', True)).lower())
            form_data.add_field('brightness', str(config.get('brightness', 128)))
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.post(f"{self.base_url}/api/pomodoro/config", data=form_data) as response:
                    return response.status == 200
        except Exception as e:
            print(f"Error updating config: {e}")
        return False
    
    async def start_timer(self, timer_type: str) -> bool:
        """Start a timer session
        
        Args:
            timer_type: 'work', 'short_break', or 'long_break'
        """
        try:
            form_data = aiohttp.FormData()
            form_data.add_field('type', timer_type)
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.post(f"{self.base_url}/api/pomodoro/start", data=form_data) as response:
                    return response.status == 200
        except Exception as e:
            print(f"Error starting timer: {e}")
        return False
    
    async def stop_timer(self) -> bool:
        """Stop the current timer session"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.post(f"{self.base_url}/api/pomodoro/stop") as response:
                    return response.status == 200
        except Exception as e:
            print(f"Error stopping timer: {e}")
        return False
    
    async def get_device_info(self) -> Optional[Dict[str, Any]]:
        """Get device information"""
        status = await self.get_status()
        if status:
            return {
                'ip': status.get('ipAddress', self.host),
                'hostname': status.get('hostname', 'unknown'),
                'wifi_connected': status.get('wifiConnected', False),
            }
        return None
