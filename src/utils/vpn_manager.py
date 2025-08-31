"""
VPN and proxy management utilities for v0rtex scraper.
"""

import subprocess
import time
import requests
import json
import os
from typing import Dict, List, Optional, Union, Any
from loguru import logger
import threading
import random


class VPNProvider:
    """Base class for VPN providers."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.is_connected = False
        self.current_ip = None
        self.current_country = None
    
    def connect(self) -> bool:
        """Connect to VPN."""
        raise NotImplementedError
    
    def disconnect(self) -> bool:
        """Disconnect from VPN."""
        raise NotImplementedError
    
    def get_status(self) -> Dict[str, Any]:
        """Get VPN status."""
        return {
            "name": self.name,
            "connected": self.is_connected,
            "current_ip": self.current_ip,
            "current_country": self.current_country
        }
    
    def get_ip_info(self) -> Dict[str, Any]:
        """Get current IP information."""
        try:
            response = requests.get("https://ipapi.co/json/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.current_ip = data.get("ip")
                self.current_country = data.get("country_name")
                return data
        except Exception as e:
            logger.error(f"Failed to get IP info: {e}")
        
        return {}


class OpenVPNProvider(VPNProvider):
    """OpenVPN provider implementation."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.config_file = config.get("config_file")
        self.auth_file = config.get("auth_file")
        self.process = None
    
    def connect(self) -> bool:
        """Connect using OpenVPN."""
        try:
            if not self.config_file or not os.path.exists(self.config_file):
                logger.error(f"OpenVPN config file not found: {self.config_file}")
                return False
            
            cmd = ["openvpn", "--config", self.config_file]
            if self.auth_file:
                cmd.extend(["--auth-user-pass", self.auth_file])
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for connection
            time.sleep(5)
            
            if self.process.poll() is None:
                self.is_connected = True
                self.get_ip_info()
                logger.info(f"Connected to OpenVPN: {self.name}")
                return True
            else:
                logger.error("OpenVPN connection failed")
                return False
                
        except Exception as e:
            logger.error(f"OpenVPN connection error: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from OpenVPN."""
        try:
            if self.process:
                self.process.terminate()
                self.process.wait(timeout=10)
                self.process = None
            
            self.is_connected = False
            self.current_ip = None
            self.current_country = None
            
            logger.info(f"Disconnected from OpenVPN: {self.name}")
            return True
            
        except Exception as e:
            logger.error(f"OpenVPN disconnection error: {e}")
            return False


class WireGuardProvider(VPNProvider):
    """WireGuard provider implementation."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.interface = config.get("interface", "wg0")
        self.config_file = config.get("config_file")
    
    def connect(self) -> bool:
        """Connect using WireGuard."""
        try:
            if not self.config_file or not os.path.exists(self.config_file):
                logger.error(f"WireGuard config file not found: {self.config_file}")
                return False
            
            # Bring up interface
            subprocess.run(["wg-quick", "up", self.interface], check=True)
            
            self.is_connected = True
            self.get_ip_info()
            logger.info(f"Connected to WireGuard: {self.name}")
            return True
            
        except Exception as e:
            logger.error(f"WireGuard connection error: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from WireGuard."""
        try:
            subprocess.run(["wg-quick", "down", self.interface], check=True)
            
            self.is_connected = False
            self.current_ip = None
            self.current_country = None
            
            logger.info(f"Disconnected from WireGuard: {self.name}")
            return True
            
        except Exception as e:
            logger.error(f"WireGuard disconnection error: {e}")
            return False


class ProxyProvider:
    """Proxy provider implementation."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.proxies = config.get("proxies", [])
        self.current_proxy = None
        self.rotation_index = 0
    
    def get_proxy(self) -> Optional[Dict[str, str]]:
        """Get current proxy configuration."""
        if not self.proxies:
            return None
        
        if self.current_proxy is None:
            self.current_proxy = self.proxies[0]
        
        return self.current_proxy
    
    def rotate_proxy(self) -> Optional[Dict[str, str]]:
        """Rotate to next proxy."""
        if not self.proxies:
            return None
        
        self.rotation_index = (self.rotation_index + 1) % len(self.proxies)
        self.current_proxy = self.proxies[self.rotation_index]
        
        logger.info(f"Rotated to proxy: {self.current_proxy.get('host', 'unknown')}")
        return self.current_proxy
    
    def get_random_proxy(self) -> Optional[Dict[str, str]]:
        """Get random proxy from list."""
        if not self.proxies:
            return None
        
        self.current_proxy = random.choice(self.proxies)
        return self.current_proxy
    
    def test_proxy(self, proxy: Dict[str, str]) -> bool:
        """Test if proxy is working."""
        try:
            proxy_url = f"{proxy['type']}://{proxy['host']}:{proxy['port']}"
            if proxy.get('username') and proxy.get('password'):
                proxy_url = f"{proxy['type']}://{proxy['username']}:{proxy['password']}@{proxy['host']}:{proxy['port']}"
            
            proxies = {
                "http": proxy_url,
                "https": proxy_url
            }
            
            response = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Proxy test failed: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get proxy status."""
        return {
            "name": self.name,
            "total_proxies": len(self.proxies),
            "current_proxy": self.current_proxy,
            "rotation_index": self.rotation_index
        }


class VPNManager:
    """Main VPN and proxy manager."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.vpn_providers: Dict[str, VPNProvider] = {}
        self.proxy_providers: Dict[str, ProxyProvider] = {}
        self.current_vpn: Optional[VPNProvider] = None
        self.current_proxy: Optional[ProxyProvider] = None
        self.auto_rotation = config.get("auto_rotation", False)
        self.rotation_interval = config.get("rotation_interval", 300)
        self.rotation_thread = None
        self.stop_rotation = False
        
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize VPN and proxy providers from config."""
        # Initialize VPN providers
        vpn_configs = self.config.get("vpn_providers", {})
        for name, vpn_config in vpn_configs.items():
            vpn_type = vpn_config.get("type")
            if vpn_type == "openvpn":
                self.vpn_providers[name] = OpenVPNProvider(name, vpn_config)
            elif vpn_type == "wireguard":
                self.vpn_providers[name] = WireGuardProvider(name, vpn_config)
        
        # Initialize proxy providers
        proxy_configs = self.config.get("proxy_providers", {})
        for name, proxy_config in proxy_configs.items():
            self.proxy_providers[name] = ProxyProvider(name, proxy_config)
    
    def connect_vpn(self, provider_name: str) -> bool:
        """Connect to specified VPN provider."""
        if provider_name not in self.vpn_providers:
            logger.error(f"VPN provider not found: {provider_name}")
            return False
        
        # Disconnect current VPN if any
        if self.current_vpn:
            self.disconnect_vpn()
        
        provider = self.vpn_providers[provider_name]
        if provider.connect():
            self.current_vpn = provider
            return True
        
        return False
    
    def disconnect_vpn(self) -> bool:
        """Disconnect from current VPN."""
        if self.current_vpn:
            success = self.current_vpn.disconnect()
            if success:
                self.current_vpn = None
            return success
        return True
    
    def set_proxy(self, provider_name: str) -> bool:
        """Set proxy provider."""
        if provider_name not in self.proxy_providers:
            logger.error(f"Proxy provider not found: {provider_name}")
            return False
        
        self.current_proxy = self.proxy_providers[provider_name]
        logger.info(f"Set proxy provider: {provider_name}")
        return True
    
    def rotate_vpn(self) -> bool:
        """Rotate to next available VPN."""
        if not self.vpn_providers:
            logger.warning("No VPN providers available")
            return False
        
        available_providers = [name for name, provider in self.vpn_providers.items() 
                             if not provider.is_connected]
        
        if not available_providers:
            logger.warning("No available VPN providers for rotation")
            return False
        
        # Disconnect current VPN
        if self.current_vpn:
            self.disconnect_vpn()
        
        # Connect to random available provider
        selected_provider = random.choice(available_providers)
        return self.connect_vpn(selected_provider)
    
    def rotate_proxy(self) -> Optional[Dict[str, str]]:
        """Rotate proxy."""
        if self.current_proxy:
            return self.current_proxy.rotate_proxy()
        return None
    
    def get_current_ip(self) -> Optional[str]:
        """Get current IP address."""
        if self.current_vpn:
            return self.current_vpn.current_ip
        
        # Get IP without VPN
        try:
            response = requests.get("https://ipapi.co/json/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get("ip")
        except Exception as e:
            logger.error(f"Failed to get current IP: {e}")
        
        return None
    
    def get_ip_info(self) -> Dict[str, Any]:
        """Get detailed IP information."""
        if self.current_vpn:
            return self.current_vpn.get_ip_info()
        
        # Get IP info without VPN
        try:
            response = requests.get("https://ipapi.co/json/", timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Failed to get IP info: {e}")
        
        return {}
    
    def start_auto_rotation(self):
        """Start automatic VPN/proxy rotation."""
        if self.auto_rotation and not self.rotation_thread:
            self.stop_rotation = False
            self.rotation_thread = threading.Thread(target=self._rotation_worker)
            self.rotation_thread.daemon = True
            self.rotation_thread.start()
            logger.info("Started auto-rotation")
    
    def stop_auto_rotation(self):
        """Stop automatic rotation."""
        self.stop_rotation = True
        if self.rotation_thread:
            self.rotation_thread.join(timeout=5)
            self.rotation_thread = None
            logger.info("Stopped auto-rotation")
    
    def _rotation_worker(self):
        """Worker thread for automatic rotation."""
        while not self.stop_rotation:
            try:
                time.sleep(self.rotation_interval)
                
                if self.stop_rotation:
                    break
                
                # Rotate VPN
                if self.vpn_providers:
                    self.rotate_vpn()
                
                # Rotate proxy
                if self.current_proxy:
                    self.rotate_proxy()
                
            except Exception as e:
                logger.error(f"Rotation worker error: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get overall VPN/proxy status."""
        return {
            "vpn": {
                "current": self.current_vpn.name if self.current_vpn else None,
                "connected": self.current_vpn.is_connected if self.current_vpn else False,
                "providers": {name: provider.get_status() for name, provider in self.vpn_providers.items()}
            },
            "proxy": {
                "current": self.current_proxy.name if self.current_proxy else None,
                "providers": {name: provider.get_status() for name, provider in self.proxy_providers.items()}
            },
            "auto_rotation": {
                "enabled": self.auto_rotation,
                "interval": self.rotation_interval,
                "active": self.rotation_thread is not None
            },
            "current_ip": self.get_current_ip()
        }
    
    def test_connection(self) -> Dict[str, bool]:
        """Test VPN and proxy connections."""
        results = {}
        
        # Test VPN
        if self.current_vpn:
            results["vpn"] = self.current_vpn.is_connected
        
        # Test proxy
        if self.current_proxy:
            current_proxy = self.current_proxy.get_proxy()
            if current_proxy:
                results["proxy"] = self.current_proxy.test_proxy(current_proxy)
        
        return results
