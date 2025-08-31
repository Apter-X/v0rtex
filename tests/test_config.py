"""
Tests for configuration module.
"""

import pytest
import tempfile
import os
from src.core.config import ScrapingConfig, BrowserType, ProxyType, CaptchaType, AntiDetectionLevel


class TestScrapingConfig:
    """Test ScrapingConfig class."""
    
    def test_basic_config_creation(self):
        """Test basic configuration creation."""
        config = ScrapingConfig(
            name="Test Scraper",
            target_url="https://example.com"
        )
        
        assert config.name == "Test Scraper"
        assert config.target_url == "https://example.com"
        assert config.method == "GET"
        assert config.anti_detection_level == AntiDetectionLevel.MEDIUM
    
    def test_config_with_all_options(self):
        """Test configuration with all options set."""
        config = ScrapingConfig(
            name="Full Config",
            target_url="https://example.com",
            method="POST",
            login_required=True,
            login_url="https://example.com/login",
            login_credentials={"username": "test", "password": "pass"},
            anti_detection_level=AntiDetectionLevel.HIGH,
            browser_type=BrowserType.UNDETECTED,
            headless=True
        )
        
        assert config.login_required is True
        assert config.login_url == "https://example.com/login"
        assert config.anti_detection_level == AntiDetectionLevel.HIGH
    
    def test_url_validation(self):
        """Test URL validation."""
        # Valid URLs
        valid_urls = [
            "https://example.com",
            "http://localhost:8000",
            "https://sub.domain.com/path"
        ]
        
        for url in valid_urls:
            config = ScrapingConfig(name="Test", target_url=url)
            assert config.target_url == url
        
        # Invalid URLs
        invalid_urls = [
            "not-a-url",
            "ftp://example.com",
            "example.com"
        ]
        
        for url in invalid_urls:
            with pytest.raises(ValueError):
                ScrapingConfig(name="Test", target_url=url)
    
    def test_config_serialization(self):
        """Test configuration serialization to JSON and YAML."""
        config = ScrapingConfig(
            name="Serialization Test",
            target_url="https://example.com",
            selectors={"title": "h1", "content": "p"},
            data_mapping={"title": "css:h1"}
        )
        
        # Test JSON serialization
        json_str = config.to_json()
        assert "Serialization Test" in json_str
        assert "https://example.com" in json_str
        
        # Test YAML serialization
        yaml_str = config.to_yaml()
        assert "Serialization Test" in yaml_str
        assert "https://example.com" in yaml_str
    
    def test_config_from_json(self):
        """Test configuration creation from JSON."""
        json_data = {
            "name": "JSON Config",
            "target_url": "https://example.com",
            "selectors": {"title": "h1"},
            "browser": {
                "type": "chrome",
                "headless": True
            }
        }
        
        config = ScrapingConfig.from_json(json_data)
        assert config.name == "JSON Config"
        assert config.target_url == "https://example.com"
        assert config.selectors["title"] == "h1"
        assert config.browser.type == BrowserType.CHROME
        assert config.browser.headless is True
    
    def test_config_from_json_string(self):
        """Test configuration creation from JSON string."""
        json_str = '''
        {
            "name": "JSON String Config",
            "target_url": "https://example.com",
            "selectors": {"title": "h1"}
        }
        '''
        
        config = ScrapingConfig.from_json(json_str)
        assert config.name == "JSON String Config"
        assert config.target_url == "https://example.com"
    
    def test_config_save_and_load(self):
        """Test configuration save and load from file."""
        config = ScrapingConfig(
            name="File Test",
            target_url="https://example.com",
            selectors={"title": "h1"}
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            # Save config
            config.save_to_file(temp_file)
            assert os.path.exists(temp_file)
            
            # Load config
            loaded_config = ScrapingConfig.load_from_file(temp_file)
            assert loaded_config.name == config.name
            assert loaded_config.target_url == config.target_url
            assert loaded_config.selectors == config.selectors
            
        finally:
            # Cleanup
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_config_save_and_load_yaml(self):
        """Test configuration save and load from YAML file."""
        config = ScrapingConfig(
            name="YAML Test",
            target_url="https://example.com",
            selectors={"title": "h1"}
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_file = f.name
        
        try:
            # Save config
            config.save_to_file(temp_file)
            assert os.path.exists(temp_file)
            
            # Load config
            loaded_config = ScrapingConfig.load_from_file(temp_file)
            assert loaded_config.name == config.name
            assert loaded_config.target_url == config.target_url
            assert loaded_config.selectors == config.selectors
            
        finally:
            # Cleanup
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_invalid_file_extension(self):
        """Test error handling for invalid file extensions."""
        config = ScrapingConfig(
            name="Test",
            target_url="https://example.com"
        )
        
        with pytest.raises(ValueError):
            config.save_to_file("config.txt")
        
        with pytest.raises(ValueError):
            ScrapingConfig.load_from_file("config.txt")


class TestEnums:
    """Test enum classes."""
    
    def test_browser_type_enum(self):
        """Test BrowserType enum."""
        assert BrowserType.CHROME == "chrome"
        assert BrowserType.FIREFOX == "firefox"
        assert BrowserType.SAFARI == "safari"
        assert BrowserType.EDGE == "edge"
        assert BrowserType.UNDETECTED == "undetected"
    
    def test_proxy_type_enum(self):
        """Test ProxyType enum."""
        assert ProxyType.HTTP == "http"
        assert ProxyType.HTTPS == "https"
        assert ProxyType.SOCKS4 == "socks4"
        assert ProxyType.SOCKS5 == "socks5"
    
    def test_captcha_type_enum(self):
        """Test CaptchaType enum."""
        assert CaptchaType.RECAPTCHA == "recaptcha"
        assert CaptchaType.HCAPTCHA == "hcaptcha"
        assert CaptchaType.IMAGE == "image"
        assert CaptchaType.TEXT == "text"
        assert CaptchaType.AUDIO == "audio"
    
    def test_anti_detection_level_enum(self):
        """Test AntiDetectionLevel enum."""
        assert AntiDetectionLevel.LOW == "low"
        assert AntiDetectionLevel.MEDIUM == "medium"
        assert AntiDetectionLevel.HIGH == "high"
        assert AntiDetectionLevel.EXTREME == "extreme"


class TestProxyConfig:
    """Test ProxyConfig class."""
    
    def test_proxy_config_creation(self):
        """Test proxy configuration creation."""
        proxy = ProxyConfig(
            type=ProxyType.HTTP,
            host="proxy.example.com",
            port=8080
        )
        
        assert proxy.type == ProxyType.HTTP
        assert proxy.host == "proxy.example.com"
        assert proxy.port == 8080
        assert proxy.url == "http://proxy.example.com:8080"
    
    def test_proxy_config_with_auth(self):
        """Test proxy configuration with authentication."""
        proxy = ProxyConfig(
            type=ProxyType.SOCKS5,
            host="proxy.example.com",
            port=1080,
            username="user",
            password="pass"
        )
        
        assert proxy.username == "user"
        assert proxy.password == "pass"
        assert proxy.url == "socks5://user:pass@proxy.example.com:1080"


class TestBrowserConfig:
    """Test BrowserConfig class."""
    
    def test_browser_config_defaults(self):
        """Test browser configuration defaults."""
        config = BrowserConfig()
        
        assert config.type == BrowserType.UNDETECTED
        assert config.headless is False
        assert config.window_size == (1920, 1080)
        assert config.stealth_mode is True
        assert config.fingerprint_spoofing is True
    
    def test_browser_config_custom(self):
        """Test browser configuration with custom values."""
        config = BrowserConfig(
            type=BrowserType.CHROME,
            headless=True,
            window_size=(1366, 768),
            stealth_mode=False
        )
        
        assert config.type == BrowserType.CHROME
        assert config.headless is True
        assert config.window_size == (1366, 768)
        assert config.stealth_mode is False


class TestCaptchaConfig:
    """Test CaptchaConfig class."""
    
    def test_captcha_config_defaults(self):
        """Test CAPTCHA configuration defaults."""
        config = CaptchaConfig()
        
        assert config.enabled is True
        assert config.auto_solve is True
        assert "2captcha" in config.services
        assert "anticaptcha" in config.services
        assert config.timeout == 120
        assert config.retry_attempts == 3
    
    def test_captcha_config_custom(self):
        """Test CAPTCHA configuration with custom values."""
        config = CaptchaConfig(
            enabled=False,
            auto_solve=False,
            services=["custom_service"],
            timeout=300,
            retry_attempts=5
        )
        
        assert config.enabled is False
        assert config.auto_solve is False
        assert config.services == ["custom_service"]
        assert config.timeout == 300
        assert config.retry_attempts == 5


class TestRateLimitConfig:
    """Test RateLimitConfig class."""
    
    def test_rate_limit_config_defaults(self):
        """Test rate limit configuration defaults."""
        config = RateLimitConfig()
        
        assert config.enabled is True
        assert config.requests_per_minute == 60
        assert config.delay_between_requests == 1.0
        assert config.random_delay is True
        assert config.delay_variance == 0.5
    
    def test_rate_limit_config_custom(self):
        """Test rate limit configuration with custom values."""
        config = RateLimitConfig(
            enabled=False,
            requests_per_minute=30,
            delay_between_requests=2.0,
            random_delay=False,
            delay_variance=1.0
        )
        
        assert config.enabled is False
        assert config.requests_per_minute == 30
        assert config.delay_between_requests == 2.0
        assert config.random_delay is False
        assert config.delay_variance == 1.0
