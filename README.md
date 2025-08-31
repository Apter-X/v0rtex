# v0rtex 🕷️

**Dynamic JSON-based web scraper with anti-detection capabilities**

v0rtex is a powerful and flexible web scraping framework that can handle various anti-scraping measures including CAPTCHAs, browser fingerprinting, and IP blocking through VPN/proxy support.

## ✨ Features

- **🔄 Dynamic Configuration**: JSON/YAML-based configuration for easy setup and modification
- **🛡️ Anti-Detection**: Advanced browser fingerprinting and stealth techniques
- **🔐 Authentication Support**: Handle login forms and session management
- **🤖 CAPTCHA Solving**: Automatic CAPTCHA solving with multiple services (2captcha, AntiCaptcha)
- **🌐 VPN/Proxy Support**: Built-in VPN and proxy rotation capabilities
- **📱 Multi-Browser**: Support for Chrome, Firefox, Safari, Edge, and undetected Chrome
- **⚡ Rate Limiting**: Configurable rate limiting with random delays
- **📊 Data Extraction**: Flexible CSS/XPath selectors and data mapping
- **💾 Session Persistence**: Save and restore scraping sessions
- **📝 Comprehensive Logging**: Detailed logging for debugging and monitoring

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/v0rtex.git
cd v0rtex

# Install dependencies
pip install -r requirements.txt

# Or install with optional dependencies
pip install -e ".[vpn,proxy,dev]"
```

### Basic Usage

1. **Create a configuration file** (`config.json`):

```json
{
  "name": "My Scraper",
  "target_url": "https://example.com",
  "selectors": {
    "title": "h1",
    "content": "p",
    "links": "a[href]"
  },
  "browser": {
    "type": "undetected",
    "headless": false
  }
}
```

2. **Run the scraper**:

```bash
# Using CLI
v0rtex run -c config.json

# Using Python
from src.core.scraper import V0rtexScraper
from src.core.config import ScrapingConfig

config = ScrapingConfig.load_from_file('config.json')
scraper = V0rtexScraper(config)
results = scraper.scrape()
```

### CLI Commands

```bash
# Initialize sample configuration
v0rtex init -o my_config.json

# Run scraper with configuration
v0rtex run -c config.json

# Run with multiple URLs
v0rtex run -c config.json -u "https://example1.com" -u "https://example2.com"

# Run with verbose logging
v0rtex run -c config.json -v

# Save results to specific file
v0rtex run -c config.json -o results.json
```

## 📋 Configuration

### Basic Configuration

```json
{
  "name": "Basic Scraper",
  "target_url": "https://example.com",
  "selectors": {
    "title": "h1",
    "content": "p"
  }
}
```

### Advanced Configuration

```json
{
  "name": "Advanced Scraper",
  "target_url": "https://target-site.com",
  "login_required": true,
  "login_url": "https://target-site.com/login",
  "login_credentials": {
    "username": "your_username",
    "password": "your_password"
  },
  "anti_detection_level": "high",
  "browser": {
    "type": "undetected",
    "headless": false,
    "stealth_mode": true
  },
  "proxy": {
    "type": "socks5",
    "host": "proxy.example.com",
    "port": 1080
  },
  "captcha": {
    "enabled": true,
    "services": ["2captcha"],
    "api_keys": {
      "2captcha": "YOUR_API_KEY"
    }
  },
  "rate_limit": {
    "enabled": true,
    "requests_per_minute": 30,
    "delay_between_requests": 2.0
  }
}
```

## 🔧 Anti-Detection Features

### Browser Fingerprinting

- **User Agent Rotation**: Automatic user agent rotation
- **Stealth Mode**: Disable automation indicators
- **Fingerprint Spoofing**: Randomize browser characteristics
- **Viewport Randomization**: Random window sizes

### CAPTCHA Handling

- **reCAPTCHA**: Automatic solving with 2captcha/AntiCaptcha
- **hCaptcha**: Support for hCaptcha challenges
- **Image CAPTCHA**: OCR-based image CAPTCHA solving
- **Service Fallback**: Multiple CAPTCHA solving services

### VPN/Proxy Support

- **OpenVPN**: Native OpenVPN integration
- **WireGuard**: WireGuard VPN support
- **Proxy Rotation**: Automatic proxy rotation
- **IP Rotation**: VPN-based IP rotation

## 📚 Examples

Check the `examples/` directory for complete configuration examples:

- `basic_scraping.json` - Simple scraping configuration
- `advanced_scraping.json` - Advanced configuration with login and anti-detection

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_config.py

# Run with verbose output
pytest -v
```

## 📖 Documentation

- [Architecture Guide](docs/architecture.md)
- [Contributing Guide](docs/contributing-guide.md)
- [API Reference](docs/api.md)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/contributing-guide.md) for details.

### Development Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Setup pre-commit hooks
pre-commit install

# Run code formatting
black src/ tests/
isort src/ tests/

# Run linting
flake8 src/ tests/
mypy src/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational and legitimate web scraping purposes only. Please respect websites' terms of service and robots.txt files. The authors are not responsible for any misuse of this software.

## 🔗 Links

- [GitHub Repository](https://github.com/your-org/v0rtex)
- [Issue Tracker](https://github.com/your-org/v0rtex/issues)
- [Documentation](https://v0rtex.readthedocs.io)

## 📊 Project Status

- **Version**: 0.1.0
- **Status**: Alpha
- **Python**: 3.8+
- **License**: MIT

---

**Made with ❤️ by the v0rtex team**
