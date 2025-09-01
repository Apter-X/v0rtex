# v0rtex API Reference

This document provides comprehensive API documentation for the v0rtex web scraping framework.

## 📚 Table of Contents

- [Core Classes](#core-classes)
- [Configuration](#configuration)
- [Pagination](#pagination)
- [Utilities](#utilities)
- [CLI Interface](#cli-interface)
- [Exceptions](#exceptions)

## 🔧 Core Classes

### V0rtexScraper

The main scraper class that orchestrates all scraping operations.

**Location**: `src/v0rtex/core/scraper.py`

#### Constructor
```python
def __init__(self, config: ScrapingConfig):
    """
    Initialize the scraper with configuration.
    
    Args:
        config: Scraping configuration object
    """
```

#### Methods

##### `scrape() -> List[Dict[str, Any]]`
Scrape data from the configured target URL.

**Returns**: List of scraped data dictionaries

**Example**:
```python
scraper = V0rtexScraper(config)
results = scraper.scrape()
```

##### `scrape_with_pagination(config: PaginationConfig) -> List[Dict[str, Any]]`
Scrape data with automatic pagination handling.

**Args**:
- `config`: Pagination configuration

**Returns**: List of scraped data from all pages

**Example**:
```python
pagination_config = PaginationConfig(enabled=True, max_pages=10)
results = scraper.scrape_with_pagination(pagination_config)
```

##### `setup_browser() -> WebDriver`
Initialize and configure the browser instance.

**Returns**: Configured WebDriver instance

##### `cleanup() -> None`
Clean up resources and close browser instances.

### ScrapingConfig

Configuration management class using Pydantic for validation.

**Location**: `src/v0rtex/core/config.py`

#### Class Methods

##### `load_from_file(file_path: str) -> ScrapingConfig`
Load configuration from a JSON or YAML file.

**Args**:
- `file_path`: Path to configuration file

**Returns**: Loaded configuration object

**Example**:
```python
config = ScrapingConfig.load_from_file('config.json')
```

##### `load_from_dict(data: Dict[str, Any]) -> ScrapingConfig`
Load configuration from a dictionary.

**Args**:
- `data`: Configuration dictionary

**Returns**: Configuration object

#### Properties

- `name: str` - Scraper name
- `target_url: str` - Target URL to scrape
- `selectors: Dict[str, str]` - CSS selectors for data extraction
- `browser: BrowserConfig` - Browser configuration
- `anti_detection: AntiDetectionConfig` - Anti-detection settings
- `pagination: PaginationConfig` - Pagination configuration

### ScrapingSession

Manages scraping session state and persistence.

**Location**: `src/v0rtex/core/session.py`

#### Methods

##### `save_state() -> None`
Save current session state to disk.

##### `load_state() -> None`
Load session state from disk.

##### `update_progress(page: int, items: int) -> None`
Update scraping progress.

**Args**:
- `page`: Current page number
- `items`: Number of items found

##### `get_progress() -> Dict[str, Any]`
Get current progress information.

**Returns**: Progress dictionary with page, items, and status

## 📄 Pagination System

### PaginationConfig

Configuration for pagination behavior.

**Location**: `src/v0rtex/core/pagination/`

#### Properties

- `enabled: bool` - Enable pagination
- `strategy: str` - Pagination strategy ('auto', 'url', 'javascript', 'infinite')
- `selectors: PaginationSelectors` - CSS selectors for pagination elements
- `limits: PaginationLimits` - Page and item limits
- `navigation: NavigationConfig` - Navigation settings

#### Example Configuration
```python
pagination_config = PaginationConfig(
    enabled=True,
    strategy="auto",
    selectors=PaginationSelectors(
        next_button=".pagination .next",
        page_numbers=".pagination .page"
    ),
    limits=PaginationLimits(
        max_pages=50,
        max_items=1000
    ),
    navigation=NavigationConfig(
        wait_time=3.0,
        retry_attempts=3
    )
)
```

### PaginationStrategy

Abstract base class for pagination strategies.

**Location**: `src/v0rtex/core/pagination/strategy.py`

#### Abstract Methods

##### `can_handle(page: WebElement) -> bool`
Check if this strategy can handle the page.

**Args**:
- `page`: WebElement representing the page

**Returns**: True if strategy can handle the page

##### `navigate_next(driver: WebDriver) -> bool`
Navigate to the next page.

**Args**:
- `driver`: WebDriver instance

**Returns**: True if navigation successful

##### `get_confidence() -> float`
Get confidence score for this strategy.

**Returns**: Confidence score between 0.0 and 1.0

### PaginationDetector

Automatically detects pagination strategies.

**Location**: `src/v0rtex/core/pagination/detector.py`

#### Methods

##### `detect_strategy(driver: WebDriver) -> PaginationStrategy`
Detect the best pagination strategy for the page.

**Args**:
- `driver`: WebDriver instance

**Returns**: Best pagination strategy

##### `get_confidence_scores() -> Dict[str, float]`
Get confidence scores for all strategies.

**Returns**: Dictionary mapping strategy names to confidence scores

### PaginationNavigator

Manages pagination workflow and navigation.

**Location**: `src/v0rtex/core/pagination/navigator.py`

#### Methods

##### `navigate_pages(config: PaginationConfig) -> Iterator[WebElement]`
Navigate through pages and yield page elements.

**Args**:
- `config`: Pagination configuration

**Yields**: WebElement for each page

##### `get_page_info() -> PaginationInfo`
Get current pagination information.

**Returns**: PaginationInfo object with current state

## 🛡️ Anti-Detection System

### AntiDetectionManager

Manages browser fingerprinting and stealth techniques.

**Location**: `src/v0rtex/utils/anti_detection.py`

#### Methods

##### `apply_stealth_mode(driver: WebDriver) -> None`
Apply stealth mode to the WebDriver.

**Args**:
- `driver`: WebDriver instance

##### `rotate_user_agent() -> str`
Get a random user agent string.

**Returns**: Random user agent string

##### `randomize_viewport(driver: WebDriver) -> None`
Randomize viewport dimensions.

**Args**:
- `driver`: WebDriver instance

### AntiDetectionConfig

Configuration for anti-detection features.

**Location**: `src/v0rtex/core/config.py`

#### Properties

- `enabled: bool` - Enable anti-detection
- `stealth_mode: bool` - Enable stealth mode
- `user_agent_rotation: bool` - Rotate user agents
- `viewport_randomization: bool` - Randomize viewport
- `header_rotation: bool` - Rotate headers

## 🔐 CAPTCHA Solving

### CaptchaSolver

Handles automatic CAPTCHA resolution.

**Location**: `src/v0rtex/utils/captcha_solver.py`

#### Methods

##### `solve_recaptcha(site_key: str, page_url: str) -> str`
Solve reCAPTCHA v2.

**Args**:
- `site_key`: reCAPTCHA site key
- `page_url`: Page URL containing the CAPTCHA

**Returns**: CAPTCHA solution token

##### `solve_hcaptcha(site_key: str, page_url: str) -> str`
Solve hCaptcha.

**Args**:
- `site_key`: hCaptcha site key
- `page_url`: Page URL containing the CAPTCHA

**Returns**: CAPTCHA solution token

##### `solve_image_captcha(image_path: str) -> str`
Solve image-based CAPTCHA.

**Args**:
- `image_path`: Path to CAPTCHA image

**Returns**: CAPTCHA solution text

### CaptchaConfig

Configuration for CAPTCHA solving services.

**Location**: `src/v0rtex/core/config.py`

#### Properties

- `enabled: bool` - Enable CAPTCHA solving
- `service: str` - CAPTCHA solving service ('2captcha', 'anticaptcha')
- `api_key: str` - API key for the service
- `timeout: int` - Timeout in seconds

## 🌐 VPN/Proxy Management

### VPNManager

Manages VPN connections and proxy rotation.

**Location**: `src/v0rtex/utils/vpn_manager.py`

#### Methods

##### `connect_vpn(config: VPNConfig) -> bool`
Connect to VPN service.

**Args**:
- `config`: VPN configuration

**Returns**: True if connection successful

##### `disconnect_vpn() -> None`
Disconnect from VPN service.

##### `rotate_proxy() -> str`
Get next proxy from rotation.

**Returns**: Proxy URL string

##### `test_connection() -> bool`
Test current connection.

**Returns**: True if connection working

### VPNConfig

Configuration for VPN and proxy services.

**Location**: `src/v0rtex/core/config.py`

#### Properties

- `enabled: bool` - Enable VPN/proxy
- `type: str` - VPN type ('openvpn', 'wireguard', 'proxy')
- `config_path: str` - Path to VPN configuration file
- `proxy_list: List[str]` - List of proxy URLs
- `rotation_interval: int` - Proxy rotation interval in seconds

## 🖥️ CLI Interface

### Command Line Interface

The v0rtex CLI provides command-line access to all features.

#### Commands

##### `v0rtex init`
Initialize a new configuration file.

**Options**:
- `-o, --output`: Output file path
- `-t, --template`: Template type

**Example**:
```bash
v0rtex init -o my_config.json
```

##### `v0rtex run`
Run the scraper with configuration.

**Options**:
- `-c, --config`: Configuration file path
- `-u, --url`: Override target URL
- `-o, --output`: Output file path
- `-v, --verbose`: Verbose logging

**Example**:
```bash
v0rtex run -c config.json -v
```

##### `v0rtex validate`
Validate configuration file.

**Options**:
- `-c, --config`: Configuration file path

**Example**:
```bash
v0rtex validate -c config.json
```

## 🚨 Exceptions

### Exception Hierarchy

```python
class V0rtexError(Exception):
    """Base exception for v0rtex framework."""
    pass

class ConfigurationError(V0rtexError):
    """Configuration-related errors."""
    pass

class ScrapingError(V0rtexError):
    """Scraping operation errors."""
    pass

class PaginationError(V0rtexError):
    """Pagination-related errors."""
    pass

class CaptchaError(V0rtexError):
    """CAPTCHA solving errors."""
    pass

class VPNError(V0rtexError):
    """VPN/proxy connection errors."""
    pass
```

### Common Exceptions

#### ConfigurationError
Raised when configuration is invalid or missing.

**Common Causes**:
- Missing required fields
- Invalid field values
- File not found
- JSON/YAML parsing errors

#### ScrapingError
Raised when scraping operations fail.

**Common Causes**:
- Network errors
- Page not found
- Selector not found
- Browser errors

#### PaginationError
Raised when pagination operations fail.

**Common Causes**:
- Pagination elements not found
- Navigation failures
- Strategy detection failures

## 📖 Usage Examples

### Basic Scraping
```python
from v0rtex.core.scraper import V0rtexScraper
from v0rtex.core.config import ScrapingConfig

# Load configuration
config = ScrapingConfig.load_from_file('config.json')

# Create scraper
scraper = V0rtexScraper(config)

# Scrape data
try:
    results = scraper.scrape()
    print(f"Scraped {len(results)} items")
except ScrapingError as e:
    print(f"Scraping failed: {e}")
finally:
    scraper.cleanup()
```

### Pagination Scraping
```python
from v0rtex.core.pagination import PaginationConfig

# Configure pagination
pagination_config = PaginationConfig(
    enabled=True,
    strategy="auto",
    limits={"max_pages": 10}
)

# Scrape with pagination
results = scraper.scrape_with_pagination(pagination_config)
print(f"Scraped {len(results)} items across multiple pages")
```

### Anti-Detection Setup
```python
from v0rtex.utils.anti_detection import AntiDetectionManager

# Create anti-detection manager
anti_detection = AntiDetectionManager()

# Apply stealth mode
anti_detection.apply_stealth_mode(driver)
anti_detection.randomize_viewport(driver)
```

## 🔗 Related Documentation

- [Configuration Guide](configuration.md) - Detailed configuration options
- [Architecture Documentation](../architecture.md) - System architecture
- [Contributing Guide](../contributing-guide.md) - Development guidelines
- [Examples](../examples/) - Configuration examples
