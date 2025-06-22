"""Device discovery for LED Tomato devices"""

import asyncio
import socket
import aiohttp
from typing import List, Dict, Optional, Any
from zeroconf import ServiceBrowser, ServiceListener, Zeroconf
import threading
import time


class LEDTomatoServiceListener(ServiceListener):
    """mDNS service listener for LED Tomato devices"""
    
    def __init__(self):
        self.devices = []
        self.found_event = threading.Event()
    
    def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        """Called when a service is discovered"""
        info = zc.get_service_info(type_, name)
        if info and info.addresses:
            ip = socket.inet_ntoa(info.addresses[0])
            hostname = info.server.rstrip('.')
            
            # Check if this is actually a LED Tomato device
            if 'ledtomato' in hostname.lower() or 'tomato' in name.lower():
                device = {
                    'ip': ip,
                    'hostname': hostname,
                    'name': name,
                    'port': info.port
                }
                self.devices.append(device)
                self.found_event.set()
    
    def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        """Called when a service is removed"""
        pass
    
    def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        """Called when a service is updated"""
        pass


class DeviceDiscovery:
    """LED Tomato device discovery"""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
    
    async def find_device(self) -> Optional[str]:
        """Find a single LED Tomato device"""
        devices = await self.scan_network()
        if devices:
            return devices[0]['ip']
        return None
    
    async def scan_network(self) -> List[Dict[str, Any]]:
        """Scan network for LED Tomato devices"""
        devices = []
        
        # Try mDNS discovery first
        mdns_devices = await self._mdns_discovery()
        devices.extend(mdns_devices)
        
        # If no devices found via mDNS, try network scan
        if not devices:
            scan_devices = await self._network_scan()
            devices.extend(scan_devices)
        
        return devices
    
    async def _mdns_discovery(self) -> List[Dict[str, Any]]:
        """Discover devices using mDNS/Bonjour"""
        try:
            zeroconf = Zeroconf()
            listener = LEDTomatoServiceListener()
            
            # Browse for HTTP services
            browser = ServiceBrowser(zeroconf, "_http._tcp.local.", listener)
            
            # Wait for discovery
            await asyncio.sleep(self.timeout)
            
            zeroconf.close()
            return listener.devices
            
        except Exception as e:
            print(f"mDNS discovery failed: {e}")
            return []
    
    async def _network_scan(self) -> List[Dict[str, Any]]:
        """Scan local network for LED Tomato devices"""
        devices = []
        
        try:
            # Get local network range
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            network_base = '.'.join(local_ip.split('.')[:-1]) + '.'
            
            # Create tasks for scanning IP range
            tasks = []
            for i in range(1, 255):
                ip = f"{network_base}{i}"
                if ip != local_ip:  # Skip our own IP
                    tasks.append(self._check_device(ip))
            
            # Run scans concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Collect successful results
            for result in results:
                if isinstance(result, dict):
                    devices.append(result)
            
        except Exception as e:
            print(f"Network scan failed: {e}")
        
        return devices
    
    async def _check_device(self, ip: str) -> Optional[Dict[str, Any]]:
        """Check if IP address hosts a LED Tomato device"""
        try:
            timeout = aiohttp.ClientTimeout(total=2)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(f"http://{ip}/api/status") as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('hostname') == 'ledtomato':
                            return {
                                'ip': ip,
                                'hostname': data.get('hostname', 'ledtomato'),
                                'wifi_connected': data.get('wifiConnected', False)
                            }
        except Exception:
            pass
        
        return None
    
    async def discover_with_progress(self, callback=None) -> List[Dict[str, Any]]:
        """Discover devices with progress callback"""
        if callback:
            callback("Starting device discovery...")
        
        # Try mDNS first
        if callback:
            callback("Scanning for mDNS services...")
        
        devices = await self._mdns_discovery()
        
        if not devices:
            if callback:
                callback("No mDNS devices found, scanning network...")
            devices = await self._network_scan()
            
        if callback:
            callback(f"Discovery complete. Found {len(devices)} device(s).")
        
        return devices
