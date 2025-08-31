"""
Anti-detection utilities for v0rtex scraper.
"""

import random
import time
from typing import Dict, List, Optional, Any
from fake_useragent import UserAgent
from loguru import logger


class AntiDetectionManager:
    """Manages anti-detection techniques and browser fingerprinting."""
    
    def __init__(self, level: str = "medium"):
        self.level = level
        self.ua = UserAgent()
        self.fingerprint_cache: Dict[str, Any] = {}
        
        # Common browser fingerprints
        self.browser_profiles = {
            "chrome": {
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "platform": "Win32",
                "language": "en-US,en;q=0.9",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "accept_encoding": "gzip, deflate, br",
                "accept_language": "en-US,en;q=0.9",
                "sec_ch_ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                "sec_ch_ua_mobile": "?0",
                "sec_ch_ua_platform": '"Windows"',
                "sec_fetch_dest": "document",
                "sec_fetch_mode": "navigate",
                "sec_fetch_site": "none",
                "sec_fetch_user": "?1",
                "upgrade_insecure_requests": "1"
            },
            "firefox": {
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
                "platform": "Win32",
                "language": "en-US,en;q=0.5",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "accept_encoding": "gzip, deflate",
                "accept_language": "en-US,en;q=0.5",
                "sec_fetch_dest": "document",
                "sec_fetch_mode": "navigate",
                "sec_fetch_site": "none",
                "sec_fetch_user": "?1",
                "upgrade_insecure_requests": "1"
            },
            "safari": {
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
                "platform": "MacIntel",
                "language": "en-US,en;q=0.9",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "accept_encoding": "gzip, deflate, br",
                "accept_language": "en-US,en;q=0.9"
            }
        }
    
    def get_random_user_agent(self, browser: str = None) -> str:
        """Get a random user agent for specified browser or random."""
        try:
            if browser:
                return getattr(self.ua, browser)
            else:
                return self.ua.random
        except Exception as e:
            logger.warning(f"Failed to get random user agent: {e}")
            # Fallback to common user agents
            fallback_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
            ]
            return random.choice(fallback_agents)
    
    def get_browser_fingerprint(self, browser: str = "chrome") -> Dict[str, str]:
        """Get browser fingerprint headers."""
        if browser not in self.browser_profiles:
            browser = "chrome"
        
        profile = self.browser_profiles[browser].copy()
        
        # Add randomization based on level
        if self.level in ["high", "extreme"]:
            profile = self._randomize_fingerprint(profile)
        
        return profile
    
    def _randomize_fingerprint(self, profile: Dict[str, str]) -> Dict[str, str]:
        """Randomize fingerprint to avoid detection."""
        randomized = profile.copy()
        
        # Randomize viewport size
        viewport_sizes = [
            (1920, 1080), (1366, 768), (1440, 900), 
            (1536, 864), (1280, 720), (1600, 900)
        ]
        width, height = random.choice(viewport_sizes)
        
        # Randomize language preferences
        languages = [
            "en-US,en;q=0.9",
            "en-US,en;q=0.8,es;q=0.7",
            "en-US,en;q=0.9,fr;q=0.8",
            "en-US,en;q=0.9,de;q=0.8"
        ]
        randomized["accept_language"] = random.choice(languages)
        
        # Randomize encoding preferences
        encodings = [
            "gzip, deflate, br",
            "gzip, deflate",
            "br, gzip, deflate"
        ]
        randomized["accept_encoding"] = random.choice(encodings)
        
        return randomized
    
    def get_stealth_headers(self, base_headers: Dict[str, str] = None) -> Dict[str, str]:
        """Get stealth headers for requests."""
        stealth_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "X-Requested-With": "XMLHttpRequest"
        }
        
        if base_headers:
            stealth_headers.update(base_headers)
        
        return stealth_headers
    
    def add_random_delay(self, base_delay: float = 1.0, variance: float = 0.5) -> float:
        """Add random delay to avoid rate limiting."""
        if self.level in ["high", "extreme"]:
            # Add more randomization for higher levels
            variance = variance * 2
        
        delay = base_delay + random.uniform(-variance, variance)
        delay = max(0.1, delay)  # Minimum delay
        
        time.sleep(delay)
        return delay
    
    def rotate_fingerprint(self) -> Dict[str, str]:
        """Rotate browser fingerprint."""
        browsers = list(self.browser_profiles.keys())
        selected_browser = random.choice(browsers)
        
        fingerprint = self.get_browser_fingerprint(selected_browser)
        self.fingerprint_cache["current"] = fingerprint
        
        logger.info(f"Rotated fingerprint to {selected_browser}")
        return fingerprint
    
    def get_anti_bot_headers(self) -> Dict[str, str]:
        """Get headers that help avoid bot detection."""
        return {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Cache-Control": "max-age=0"
        }
    
    def get_mobile_fingerprint(self) -> Dict[str, str]:
        """Get mobile device fingerprint."""
        mobile_agents = [
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1"
        ]
        
        return {
            "User-Agent": random.choice(mobile_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "X-Requested-With": "XMLHttpRequest"
        }
    
    def get_custom_fingerprint(self, custom_profile: Dict[str, str]) -> Dict[str, str]:
        """Get custom fingerprint based on provided profile."""
        base_fingerprint = self.get_browser_fingerprint("chrome")
        base_fingerprint.update(custom_profile)
        return base_fingerprint
    
    def validate_fingerprint(self, fingerprint: Dict[str, str]) -> bool:
        """Validate if fingerprint looks realistic."""
        required_fields = ["User-Agent", "Accept", "Accept-Language"]
        
        for field in required_fields:
            if field not in fingerprint:
                return False
        
        # Check if User-Agent looks realistic
        ua = fingerprint.get("User-Agent", "")
        if not any(browser in ua.lower() for browser in ["chrome", "firefox", "safari", "edge"]):
            return False
        
        return True
    
    def get_fingerprint_stats(self) -> Dict[str, Any]:
        """Get statistics about fingerprint usage."""
        return {
            "current_level": self.level,
            "cached_fingerprints": len(self.fingerprint_cache),
            "available_profiles": list(self.browser_profiles.keys()),
            "last_rotation": self.fingerprint_cache.get("last_rotation"),
            "total_rotations": self.fingerprint_cache.get("total_rotations", 0)
        }
