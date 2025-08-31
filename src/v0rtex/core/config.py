"""
Configuration management for v0rtex scraper.
"""

from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, validator
from enum import Enum
import json
import yaml


class BrowserType(str, Enum):
    """Supported browser types."""
    CHROME = "chrome"
    FIREFOX = "firefox"
    SAFARI = "safari"
    EDGE = "edge"
    UNDETECTED = "undetected"


class ProxyType(str, Enum):
    """Supported proxy types."""
    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"


class CaptchaType(str, Enum):
    """Supported CAPTCHA types."""
    RECAPTCHA = "recaptcha"
    HCAPTCHA = "hcaptcha"
    IMAGE = "image"
    TEXT = "text"
    AUDIO = "audio"


class AntiDetectionLevel(str, Enum):
    """Anti-detection levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"


class PaginationStrategy(str, Enum):
    """Supported pagination strategies."""
    AUTO = "auto"
    URL = "url"
    JAVASCRIPT = "javascript"
    INFINITE_SCROLL = "infinite_scroll"


class ProxyConfig(BaseModel):
    """Proxy configuration."""
    type: ProxyType
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    country: Optional[str] = None
    
    @property
    def url(self) -> str:
        """Get proxy URL."""
        if self.username and self.password:
            return f"{self.type}://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"{self.type}://{self.host}:{self.port}"


class VPNConfig(BaseModel):
    """VPN configuration."""
    enabled: bool = False
    provider: Optional[str] = None
    country: Optional[str] = None
    auto_rotate: bool = False
    rotation_interval: int = 300  # seconds


class BrowserConfig(BaseModel):
    """Browser configuration."""
    type: BrowserType = BrowserType.UNDETECTED
    headless: bool = False
    user_agent: Optional[str] = None
    window_size: tuple = (1920, 1080)
    disable_images: bool = False
    disable_javascript: bool = False
    disable_css: bool = False
    stealth_mode: bool = True
    fingerprint_spoofing: bool = True


class CaptchaConfig(BaseModel):
    """CAPTCHA solving configuration."""
    enabled: bool = True
    auto_solve: bool = True
    services: List[str] = Field(default_factory=lambda: ["2captcha", "anticaptcha"])
    api_keys: Dict[str, str] = Field(default_factory=dict)
    timeout: int = 120
    retry_attempts: int = 3


class RateLimitConfig(BaseModel):
    """Rate limiting configuration."""
    enabled: bool = True
    requests_per_minute: int = 60
    delay_between_requests: float = 1.0
    random_delay: bool = True
    delay_variance: float = 0.5


class PaginationSelectorsConfig(BaseModel):
    """Pagination element selectors configuration."""
    next_button: str = ".pagination .next, .pagination .next-page"
    prev_button: str = ".pagination .prev, .pagination .prev-page"
    page_numbers: str = ".pagination .page, .pagination a"
    current_page: str = ".pagination .current, .pagination .active"
    pagination_container: str = ".pagination, .pager, .page-navigation"


class PaginationLimitsConfig(BaseModel):
    """Pagination limits configuration."""
    max_pages: int = 100
    max_items: int = 1000
    max_scrolls: int = 50  # For infinite scroll


class PaginationNavigationConfig(BaseModel):
    """Pagination navigation configuration."""
    wait_time: float = 2.0
    retry_attempts: int = 3
    scroll_pause: float = 1.0
    scroll_threshold: int = 100  # pixels from bottom


class PaginationConfig(BaseModel):
    """Pagination configuration."""
    enabled: bool = False
    strategy: PaginationStrategy = PaginationStrategy.AUTO
    selectors: PaginationSelectorsConfig = Field(default_factory=PaginationSelectorsConfig)
    limits: PaginationLimitsConfig = Field(default_factory=PaginationLimitsConfig)
    navigation: PaginationNavigationConfig = Field(default_factory=PaginationNavigationConfig)
    
    # URL-based pagination specific
    url_patterns: List[str] = Field(default_factory=lambda: [
        r'[?&]page=(\d+)',
        r'[?&]p=(\d+)',
        r'[?&]pg=(\d+)',
        r'[?&]pageno=(\d+)',
        r'/page/(\d+)',
        r'/p/(\d+)'
    ])
    page_param: str = "page"


class ScrapingConfig(BaseModel):
    """Main scraping configuration."""
    
    # Basic settings
    name: str
    description: Optional[str] = None
    target_url: str
    method: str = "GET"
    headers: Dict[str, str] = Field(default_factory=dict)
    cookies: Dict[str, str] = Field(default_factory=dict)
    
    # Authentication
    login_required: bool = False
    login_url: Optional[str] = None
    login_credentials: Optional[Dict[str, str]] = None
    session_persistence: bool = True
    
    # Anti-detection
    anti_detection_level: AntiDetectionLevel = AntiDetectionLevel.MEDIUM
    browser: BrowserConfig = Field(default_factory=BrowserConfig)
    proxy: Optional[ProxyConfig] = None
    vpn: VPNConfig = Field(default_factory=VPNConfig)
    captcha: CaptchaConfig = Field(default_factory=CaptchaConfig)
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)
    
    # Scraping behavior
    selectors: Dict[str, str] = Field(default_factory=dict)
    wait_time: float = 2.0
    max_retries: int = 3
    timeout: int = 30
    follow_redirects: bool = True
    verify_ssl: bool = True
    
    # Data extraction
    data_mapping: Dict[str, str] = Field(default_factory=dict)
    output_format: str = "json"
    save_to_file: bool = True
    output_file: Optional[str] = None
    
    # Advanced options
    custom_scripts: List[str] = Field(default_factory=list)
    wait_for_elements: List[str] = Field(default_factory=list)
    scroll_behavior: Optional[str] = None
    screenshot_on_error: bool = False
    
    # Pagination support
    pagination: PaginationConfig = Field(default_factory=PaginationConfig)
    
    @validator('target_url')
    def validate_url(cls, v):
        """Validate target URL."""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('target_url must start with http:// or https://')
        return v
    
    @classmethod
    def from_json(cls, json_data: Union[str, Dict[str, Any]]) -> 'ScrapingConfig':
        """Create config from JSON data."""
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data
        return cls(**data)
    
    @classmethod
    def from_yaml(cls, yaml_data: str) -> 'ScrapingConfig':
        """Create config from YAML data."""
        data = yaml.safe_load(yaml_data)
        return cls(**data)
    
    def to_json(self) -> str:
        """Convert config to JSON string."""
        return self.model_dump_json(indent=2)
    
    def to_yaml(self) -> str:
        """Convert config to YAML string."""
        return yaml.dump(self.model_dump(), default_flow_style=False, indent=2)
    
    def save_to_file(self, filepath: str) -> None:
        """Save config to file."""
        if filepath.endswith('.json'):
            with open(filepath, 'w') as f:
                f.write(self.to_json())
        elif filepath.endswith('.yml', '.yaml'):
            with open(filepath, 'w') as f:
                f.write(self.to_yaml())
        else:
            raise ValueError("File must have .json, .yml, or .yaml extension")
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'ScrapingConfig':
        """Load config from file."""
        with open(filepath, 'r') as f:
            content = f.read()
        
        if filepath.endswith('.json'):
            return cls.from_json(content)
        elif filepath.endswith('.yml', '.yaml'):
            return cls.from_yaml(content)
        else:
            raise ValueError("File must have .json, .yml, or .yaml extension")
