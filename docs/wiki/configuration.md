# v0rtex Configuration Guide

This guide covers all configuration options for the v0rtex web scraping framework, from basic setup to advanced features.

## 📚 Table of Contents

- [Basic Configuration](#basic-configuration)
- [Browser Configuration](#browser-configuration)
- [Anti-Detection Configuration](#anti-detection-configuration)
- [CAPTCHA Configuration](#captcha-configuration)
- [VPN/Proxy Configuration](#vpnproxy-configuration)
- [Pagination Configuration](#pagination-configuration)
- [Advanced Configuration](#advanced-configuration)
- [Configuration Examples](#configuration-examples)
- [Best Practices](#best-practices)

## 🚀 Basic Configuration

### Minimal Configuration
```json
{
  "name": "My Scraper",
  "target_url": "https://example.com",
  "selectors": {
    "title": "h1",
    "content": "p"
  }
}
```

### Complete Basic Configuration
```json
{
  "name": "My Scraper",
  "description": "Scrape example website for titles and content",
  "target_url": "https://example.com",
  "selectors": {
    "title": "h1",
    "content": "p",
    "links": "a[href]",
    "images": "img[src]"
  },
  "output_format": "json",
  "output_file": "results.json",
  "log_level": "INFO"
}
```

## 🌐 Browser Configuration

### Browser Types
v0rtex supports multiple browser types with different capabilities:

```json
{
  "browser": {
    "type": "undetected",
    "headless": false,
    "window_size": {
      "width": 1920,
      "height": 1080
    },
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "timeout": 30,
    "implicit_wait": 10
  }
}
```

### Browser Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `type` | string | `"chrome"` | Browser type: `"chrome"`, `"firefox"`, `"safari"`, `"edge"`, `"undetected"` |
| `headless` | boolean | `false` | Run browser in headless mode |
| `window_size.width` | integer | `1920` | Browser window width |
| `window_size.height` | integer | `1080` | Browser window height |
| `user_agent` | string | `null` | Custom user agent string |
| `timeout` | integer | `30` | Page load timeout in seconds |
| `implicit_wait` | integer | `10` | Implicit wait for elements in seconds |

### Browser Profiles
```json
{
  "browser": {
    "type": "chrome",
    "profile_path": "/path/to/chrome/profile",
    "extensions": [
      "/path/to/extension1.crx",
      "/path/to/extension2.crx"
    ],
    "arguments": [
      "--no-sandbox",
      "--disable-dev-shm-usage",
      "--disable-blink-features=AutomationControlled"
    ]
  }
}
```

## 🛡️ Anti-Detection Configuration

### Basic Anti-Detection
```json
{
  "anti_detection": {
    "enabled": true,
    "stealth_mode": true,
    "user_agent_rotation": true,
    "viewport_randomization": true,
    "header_rotation": true
  }
}
```

### Advanced Anti-Detection
```json
{
  "anti_detection": {
    "enabled": true,
    "stealth_mode": true,
    "user_agent_rotation": true,
    "viewport_randomization": true,
    "header_rotation": true,
    "language_randomization": true,
    "timezone_randomization": true,
    "webgl_randomization": true,
    "canvas_randomization": true,
    "audio_randomization": true,
    "custom_headers": {
      "Accept-Language": "en-US,en;q=0.9",
      "Accept-Encoding": "gzip, deflate, br",
      "DNT": "1"
    },
    "exclude_plugins": ["Chrome PDF Plugin", "Chrome PDF Viewer"],
    "exclude_languages": ["en-US", "en-GB"]
  }
}
```

### Anti-Detection Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `false` | Enable anti-detection features |
| `stealth_mode` | boolean | `false` | Enable stealth mode |
| `user_agent_rotation` | boolean | `false` | Rotate user agents |
| `viewport_randomization` | boolean | `false` | Randomize viewport size |
| `header_rotation` | boolean | `false` | Rotate HTTP headers |
| `language_randomization` | boolean | `false` | Randomize language preferences |
| `timezone_randomization` | boolean | `false` | Randomize timezone |
| `webgl_randomization` | boolean | `false` | Randomize WebGL fingerprint |
| `canvas_randomization` | boolean | `false` | Randomize canvas fingerprint |
| `audio_randomization` | boolean | `false` | Randomize audio fingerprint |

## 🔐 CAPTCHA Configuration

### Basic CAPTCHA Setup
```json
{
  "captcha": {
    "enabled": true,
    "service": "2captcha",
    "api_key": "your_api_key_here",
    "timeout": 120,
    "auto_solve": true
  }
}
```

### Advanced CAPTCHA Configuration
```json
{
  "captcha": {
    "enabled": true,
    "service": "2captcha",
    "api_key": "your_api_key_here",
    "timeout": 120,
    "auto_solve": true,
    "retry_attempts": 3,
    "services": {
      "2captcha": {
        "api_key": "your_2captcha_key",
        "timeout": 120,
        "priority": 1
      },
      "anticaptcha": {
        "api_key": "your_anticaptcha_key",
        "timeout": 180,
        "priority": 2
      }
    },
    "supported_types": [
      "recaptcha_v2",
      "recaptcha_v3",
      "hcaptcha",
      "image_captcha"
    ],
    "fallback_service": "anticaptcha"
  }
}
```

### CAPTCHA Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `false` | Enable CAPTCHA solving |
| `service` | string | `"2captcha"` | Primary CAPTCHA solving service |
| `api_key` | string | `null` | API key for the service |
| `timeout` | integer | `120` | Timeout in seconds |
| `auto_solve` | boolean | `true` | Automatically solve CAPTCHAs |
| `retry_attempts` | integer | `3` | Number of retry attempts |
| `fallback_service` | string | `null` | Fallback service if primary fails |

### Supported CAPTCHA Types
- **reCAPTCHA v2**: Google's reCAPTCHA v2
- **reCAPTCHA v3**: Google's reCAPTCHA v3
- **hCaptcha**: hCaptcha service
- **Image CAPTCHA**: Image-based CAPTCHAs
- **Text CAPTCHA**: Text-based CAPTCHAs

## 🌐 VPN/Proxy Configuration

### Basic VPN Setup
```json
{
  "vpn": {
    "enabled": true,
    "type": "openvpn",
    "config_path": "/path/to/vpn.ovpn",
    "credentials": {
      "username": "vpn_user",
      "password": "vpn_pass"
    }
  }
}
```

### Advanced VPN Configuration
```json
{
  "vpn": {
    "enabled": true,
    "type": "openvpn",
    "config_path": "/path/to/vpn.ovpn",
    "credentials": {
      "username": "vpn_user",
      "password": "vpn_pass"
    },
    "auto_connect": true,
    "connection_timeout": 60,
    "health_check_interval": 300,
    "rotation_interval": 3600,
    "fallback_configs": [
      "/path/to/backup1.ovpn",
      "/path/to/backup2.ovpn"
    ]
  }
}
```

### Proxy Configuration
```json
{
  "proxy": {
    "enabled": true,
    "type": "http",
    "servers": [
      "http://proxy1:8080",
      "http://proxy2:8080",
      "socks5://proxy3:1080"
    ],
    "rotation_interval": 300,
    "health_check": true,
    "exclude_domains": ["localhost", "127.0.0.1"],
    "authentication": {
      "username": "proxy_user",
      "password": "proxy_pass"
    }
  }
}
```

### VPN/Proxy Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `false` | Enable VPN/proxy |
| `type` | string | `"openvpn"` | Type: `"openvpn"`, `"wireguard"`, `"http"`, `"socks4"`, `"socks5"` |
| `config_path` | string | `null` | Path to VPN configuration file |
| `servers` | array | `[]` | List of proxy servers |
| `rotation_interval` | integer | `3600` | Rotation interval in seconds |
| `health_check` | boolean | `true` | Enable health checking |
| `auto_connect` | boolean | `false` | Auto-connect on startup |

## 📄 Pagination Configuration

### Basic Pagination
```json
{
  "pagination": {
    "enabled": true,
    "strategy": "auto",
    "max_pages": 10,
    "max_items": 100
  }
}
```

### Advanced Pagination Configuration
```json
{
  "pagination": {
    "enabled": true,
    "strategy": "auto",
    "selectors": {
      "next_button": ".pagination .next",
      "previous_button": ".pagination .prev",
      "page_numbers": ".pagination .page",
      "load_more": ".load-more",
      "infinite_scroll": ".infinite-scroll"
    },
    "limits": {
      "max_pages": 50,
      "max_items": 1000,
      "items_per_page": 20
    },
    "navigation": {
      "wait_time": 3.0,
      "retry_attempts": 3,
      "scroll_pause": 2.0,
      "page_load_timeout": 30
    },
    "detection": {
      "confidence_threshold": 0.7,
      "auto_detect": true,
      "fallback_strategy": "javascript"
    }
  }
}
```

### Pagination Strategies

| Strategy | Description | Use Case |
|----------|-------------|----------|
| `"auto"` | Automatically detect best strategy | General purpose |
| `"url"` | URL-based pagination (`?page=2`) | Simple pagination |
| `"javascript"` | Click-based navigation | Dynamic pages |
| `"infinite"` | Infinite scroll/load more | Modern web apps |

### Pagination Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `false` | Enable pagination |
| `strategy` | string | `"auto"` | Pagination strategy |
| `max_pages` | integer | `100` | Maximum pages to scrape |
| `max_items` | integer | `1000` | Maximum items to scrape |
| `wait_time` | float | `3.0` | Wait time between pages |
| `retry_attempts` | integer | `3` | Navigation retry attempts |

## ⚙️ Advanced Configuration

### Rate Limiting
```json
{
  "rate_limiting": {
    "enabled": true,
    "requests_per_minute": 60,
    "delay_between_requests": 1.0,
    "random_delay": true,
    "delay_range": {
      "min": 0.5,
      "max": 2.0
    }
  }
}
```

### Session Management
```json
{
  "session": {
    "persist": true,
    "save_interval": 300,
    "max_session_size": "100MB",
    "encrypt_sensitive": true,
    "cleanup_old_sessions": true,
    "session_ttl": 86400
  }
}
```

### Error Handling
```json
{
  "error_handling": {
    "max_retries": 3,
    "retry_delay": 5.0,
    "continue_on_error": true,
    "save_screenshots": true,
    "log_errors": true,
    "fatal_errors": [
      "AuthenticationError",
      "ConfigurationError"
    ]
  }
}
```

### Logging Configuration
```json
{
  "logging": {
    "level": "INFO",
    "file": "v0rtex.log",
    "max_file_size": "10MB",
    "backup_count": 5,
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "console_output": true,
    "file_output": true
  }
}
```

## 📖 Configuration Examples

### E-commerce Scraper
```json
{
  "name": "E-commerce Product Scraper",
  "target_url": "https://example-store.com/products",
  "selectors": {
    "product_name": ".product-title",
    "price": ".product-price",
    "description": ".product-description",
    "image": ".product-image img",
    "rating": ".product-rating",
    "reviews": ".product-reviews"
  },
  "browser": {
    "type": "undetected",
    "headless": true
  },
  "anti_detection": {
    "enabled": true,
    "stealth_mode": true
  },
  "pagination": {
    "enabled": true,
    "strategy": "auto",
    "max_pages": 20
  },
  "rate_limiting": {
    "enabled": true,
    "requests_per_minute": 30
  }
}
```

### News Scraper
```json
{
  "name": "News Article Scraper",
  "target_url": "https://example-news.com",
  "selectors": {
    "headline": "h1.article-headline",
    "content": ".article-content p",
    "author": ".article-author",
    "date": ".article-date",
    "category": ".article-category"
  },
  "browser": {
    "type": "chrome",
    "headless": false
  },
  "pagination": {
    "enabled": true,
    "strategy": "javascript",
    "max_pages": 50
  },
  "captcha": {
    "enabled": true,
    "service": "2captcha",
    "api_key": "your_key_here"
  }
}
```

### Social Media Scraper
```json
{
  "name": "Social Media Profile Scraper",
  "target_url": "https://example-social.com/profile",
  "selectors": {
    "username": ".profile-username",
    "bio": ".profile-bio",
    "followers": ".profile-followers",
    "posts": ".profile-post",
    "avatar": ".profile-avatar img"
  },
  "browser": {
    "type": "undetected",
    "headless": true
  },
  "anti_detection": {
    "enabled": true,
    "stealth_mode": true,
    "user_agent_rotation": true
  },
  "vpn": {
    "enabled": true,
    "type": "openvpn",
    "config_path": "/path/to/vpn.ovpn"
  },
  "pagination": {
    "enabled": true,
    "strategy": "infinite",
    "max_items": 500
  }
}
```

## 🎯 Best Practices

### 1. Configuration Organization
- Use descriptive names for scrapers
- Group related settings logically
- Comment complex configurations
- Use environment variables for sensitive data

### 2. Performance Optimization
- Enable headless mode for production
- Use appropriate timeouts
- Implement rate limiting
- Monitor resource usage

### 3. Anti-Detection
- Rotate user agents regularly
- Use stealth mode for sensitive sites
- Implement random delays
- Monitor detection rates

### 4. Error Handling
- Set appropriate retry limits
- Log errors for debugging
- Implement graceful degradation
- Use fallback strategies

### 5. Security
- Never commit API keys
- Use environment variables
- Encrypt sensitive data
- Validate all inputs

### 6. Testing
- Test configurations in development
- Validate selectors before production
- Monitor scraping success rates
- Keep configurations version controlled

## 🔧 Configuration Validation

### Validate Configuration File
```bash
v0rtex validate -c config.json
```

### Common Validation Errors
- Missing required fields
- Invalid field types
- Invalid URLs
- Missing API keys
- Invalid selectors

### Configuration Schema
The configuration follows a strict schema defined in `src/v0rtex/core/config.py`. All configurations are validated against this schema before use.

## 📚 Related Documentation

- [API Reference](api-reference.md) - Complete API documentation
- [Architecture Documentation](../architecture.md) - System architecture
- [Examples](../examples/) - More configuration examples
- [Troubleshooting](troubleshooting.md) - Common issues and solutions
