"""
v0rtex - Dynamic JSON-based web scraper with anti-detection capabilities

A powerful web scraping framework that can handle various anti-scraping measures
including CAPTCHAs, browser fingerprinting, and IP blocking through VPN/proxy support.
"""

__version__ = "0.1.0"
__author__ = "v0rtex Team"
__email__ = "team@v0rtex.dev"

from .core.scraper import V0rtexScraper
from .core.config import ScrapingConfig
from .core.session import ScrapingSession
from .utils.anti_detection import AntiDetectionManager
from .utils.captcha_solver import CaptchaSolver
from .utils.vpn_manager import VPNManager

__all__ = [
    "V0rtexScraper",
    "ScrapingConfig", 
    "ScrapingSession",
    "AntiDetectionManager",
    "CaptchaSolver",
    "VPNManager",
]
