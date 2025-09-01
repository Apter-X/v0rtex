# v0rtex Troubleshooting Guide

This guide helps you resolve common issues and errors when using the v0rtex web scraping framework.

## 📚 Table of Contents

- [Common Issues](#common-issues)
- [Error Messages](#error-messages)
- [Browser Issues](#browser-issues)
- [Configuration Problems](#configuration-problems)
- [Performance Issues](#performance-issues)
- [Network Problems](#network-problems)
- [Debugging Techniques](#debugging-techniques)
- [Getting Help](#getting-help)

## 🚨 Common Issues

### 1. Installation Problems

#### Issue: ModuleNotFoundError: No module named 'v0rtex'
**Symptoms**: Python can't find the v0rtex module after installation.

**Solutions**:
```bash
# Check if v0rtex is installed
pip list | grep v0rtex

# Reinstall the package
pip uninstall v0rtex
pip install v0rtex

# Install in development mode
pip install -e .

# Check Python path
python -c "import sys; print(sys.path)"
```

#### Issue: ImportError: cannot import name 'V0rtexScraper'
**Symptoms**: Specific classes can't be imported.

**Solutions**:
```bash
# Check the installed version
pip show v0rtex

# Verify the source installation
cd src
python -c "from v0rtex.core.scraper import V0rtexScraper; print('Import successful')"

# Reinstall from source
pip install -e .
```

### 2. Dependency Issues

#### Issue: Missing WebDriver
**Symptoms**: `WebDriverException: Message: unknown error: cannot find Chrome binary`

**Solutions**:
```bash
# Install Chrome on Ubuntu/Debian
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install google-chrome-stable

# Install Chrome on CentOS/RHEL
sudo yum install -y google-chrome-stable

# Verify installation
google-chrome --version
```

#### Issue: ChromeDriver Version Mismatch
**Symptoms**: `SessionNotCreatedException: Message: session not created: This version of ChromeDriver only supports Chrome version XX`

**Solutions**:
```bash
# Check Chrome version
google-chrome --version

# Download matching ChromeDriver
CHROME_VERSION=$(google-chrome --version | cut -d' ' -f3 | cut -d'.' -f1)
wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION
wget https://chromedriver.storage.googleapis.com/$(cat LATEST_RELEASE_$CHROME_VERSION)/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver

# Or use webdriver-manager
pip install webdriver-manager
```

### 3. Permission Issues

#### Issue: Permission Denied Errors
**Symptoms**: `PermissionError: [Errno 13] Permission denied`

**Solutions**:
```bash
# Check file permissions
ls -la /path/to/file

# Fix ownership
sudo chown -R $USER:$USER /path/to/directory

# Fix permissions
sudo chmod 755 /path/to/directory
sudo chmod 644 /path/to/file

# For system directories
sudo chown -R v0rtex:v0rtex /etc/v0rtex /var/lib/v0rtex /var/log/v0rtex
```

## ❌ Error Messages

### Configuration Errors

#### `ConfigurationError: Invalid configuration`
**Cause**: Configuration file has invalid syntax or missing required fields.

**Solutions**:
```bash
# Validate configuration
v0rtex validate -c config.json

# Check JSON syntax
python -m json.tool config.json

# Verify required fields
cat config.json | jq '.name, .target_url, .selectors'
```

#### `ConfigurationError: Invalid selector`
**Cause**: CSS selector is malformed or doesn't exist on the page.

**Solutions**:
```python
# Test selector manually
from selenium import webdriver
driver = webdriver.Chrome()
driver.get("https://example.com")
elements = driver.find_elements_by_css_selector("your-selector")
print(f"Found {len(elements)} elements")
driver.quit()
```

### Scraping Errors

#### `ScrapingError: Page not found`
**Cause**: Target URL is inaccessible or returns 404.

**Solutions**:
```bash
# Check URL manually
curl -I https://example.com

# Verify URL in browser
# Check if site requires authentication
# Verify the URL hasn't changed
```

#### `ScrapingError: Selector not found`
**Cause**: CSS selector doesn't match any elements on the page.

**Solutions**:
```python
# Debug page structure
from selenium import webdriver
driver = webdriver.Chrome()
driver.get("https://example.com")

# Check page source
print(driver.page_source[:1000])

# Find elements with different selectors
elements = driver.find_elements_by_css_selector("*")
for elem in elements[:10]:
    print(f"Tag: {elem.tag_name}, Class: {elem.get_attribute('class')}")

driver.quit()
```

#### `ScrapingError: Timeout waiting for element`
**Cause**: Page takes too long to load or element is not present.

**Solutions**:
```json
{
  "browser": {
    "timeout": 60,
    "implicit_wait": 20
  }
}
```

### Pagination Errors

#### `PaginationError: No pagination strategy detected`
**Cause**: Automatic pagination detection failed.

**Solutions**:
```json
{
  "pagination": {
    "enabled": true,
    "strategy": "javascript",
    "selectors": {
      "next_button": ".pagination .next",
      "page_numbers": ".pagination .page"
    }
  }
}
```

#### `PaginationError: Navigation failed`
**Cause**: Pagination navigation didn't work as expected.

**Solutions**:
```json
{
  "pagination": {
    "navigation": {
      "wait_time": 5.0,
      "retry_attempts": 5,
      "scroll_pause": 3.0
    }
  }
}
```

### CAPTCHA Errors

#### `CaptchaError: Service unavailable`
**Cause**: CAPTCHA solving service is down or API key is invalid.

**Solutions**:
```bash
# Check API key
echo $V0RTEX_CAPTCHA_API_KEY

# Test service manually
curl "http://2captcha.com/res.php?key=YOUR_KEY&action=getbalance"

# Use fallback service
```

#### `CaptchaError: CAPTCHA solving failed`
**Cause**: CAPTCHA solving service couldn't solve the CAPTCHA.

**Solutions**:
```json
{
  "captcha": {
    "timeout": 300,
    "retry_attempts": 5,
    "fallback_service": "anticaptcha"
  }
}
```

## 🌐 Browser Issues

### Chrome/Chromium Issues

#### Issue: Chrome crashes on startup
**Symptoms**: Chrome exits immediately or shows crash dialog.

**Solutions**:
```bash
# Run with debugging
google-chrome --disable-gpu --disable-software-rasterizer --disable-dev-shm-usage

# Check system resources
free -h
df -h

# Update Chrome
sudo apt update && sudo apt upgrade google-chrome-stable
```

#### Issue: Chrome runs in headless mode unexpectedly
**Symptoms**: Chrome runs without GUI even when headless=false.

**Solutions**:
```bash
# Check DISPLAY variable
echo $DISPLAY

# Set display for X11 forwarding
export DISPLAY=:0

# Install xvfb for headless systems
sudo apt install xvfb
xvfb-run python -m v0rtex run -c config.json
```

### Firefox Issues

#### Issue: Firefox profile not loading
**Symptoms**: Firefox starts with default profile instead of custom one.

**Solutions**:
```json
{
  "browser": {
    "type": "firefox",
    "profile_path": "/path/to/firefox/profile",
    "profile_name": "default"
  }
}
```

#### Issue: Firefox geckodriver not found
**Symptoms**: `WebDriverException: Message: 'geckodriver' executable needs to be in PATH`

**Solutions**:
```bash
# Install geckodriver
wget https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux64.tar.gz
tar -xzf geckodriver-v0.33.0-linux64.tar.gz
sudo mv geckodriver /usr/local/bin/
sudo chmod +x /usr/local/bin/geckodriver

# Verify installation
geckodriver --version
```

### Undetected Chrome Issues

#### Issue: Undetected Chrome not working
**Symptoms**: Undetected Chrome behaves like regular Chrome.

**Solutions**:
```python
# Ensure proper import
import undetected_chromedriver as uc

# Use specific version
driver = uc.Chrome(version_main=119)  # Match your Chrome version

# Check if undetected features are working
print(driver.execute_script("return navigator.webdriver"))
```

## ⚙️ Configuration Problems

### JSON/YAML Parsing Issues

#### Issue: Invalid JSON syntax
**Symptoms**: `json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes`

**Solutions**:
```bash
# Validate JSON syntax
python -m json.tool config.json

# Use online JSON validator
# Check for trailing commas
# Ensure all strings are quoted
```

#### Issue: YAML parsing errors
**Symptoms**: `yaml.parser.ParserError: while parsing a block mapping`

**Solutions**:
```bash
# Install PyYAML
pip install PyYAML

# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('config.yaml'))"
```

### Environment Variable Issues

#### Issue: Environment variables not loaded
**Symptoms**: Configuration values are None or default values.

**Solutions**:
```bash
# Check environment variables
env | grep V0RTEX

# Load from .env file
source .env

# Set variables manually
export V0RTEX_LOG_LEVEL=DEBUG
export V0RTEX_CONFIG_PATH=/path/to/config.json
```

### File Path Issues

#### Issue: Configuration file not found
**Symptoms**: `FileNotFoundError: [Errno 2] No such file or directory`

**Solutions**:
```bash
# Check file exists
ls -la config.json

# Use absolute path
v0rtex run -c /absolute/path/to/config.json

# Check working directory
pwd
ls -la
```

## 🚀 Performance Issues

### Memory Problems

#### Issue: High memory usage
**Symptoms**: Process uses excessive RAM, system becomes slow.

**Solutions**:
```python
# Enable garbage collection
import gc
gc.collect()

# Use generators for large datasets
def process_items(items):
    for item in items:
        yield process_item(item)

# Monitor memory usage
import psutil
process = psutil.Process()
print(f"Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB")
```

#### Issue: Memory leaks
**Symptoms**: Memory usage grows over time without releasing.

**Solutions**:
```python
# Close WebDriver properly
try:
    driver = webdriver.Chrome()
    # ... scraping code ...
finally:
    driver.quit()

# Clear page cache
driver.delete_all_cookies()
driver.execute_script("window.localStorage.clear();")
driver.execute_script("window.sessionStorage.clear();")
```

### Speed Issues

#### Issue: Scraping is too slow
**Symptoms**: Takes too long to scrape pages.

**Solutions**:
```json
{
  "browser": {
    "headless": true,
    "disable_images": true,
    "disable_javascript": false
  },
  "rate_limiting": {
    "enabled": false
  }
}
```

#### Issue: Page load times are slow
**Symptoms**: Pages take too long to load.

**Solutions**:
```json
{
  "browser": {
    "timeout": 30,
    "implicit_wait": 5
  },
  "anti_detection": {
    "enabled": false
  }
}
```

## 🌐 Network Problems

### Connection Issues

#### Issue: Connection timeout
**Symptoms**: `requests.exceptions.ConnectTimeout` or similar errors.

**Solutions**:
```json
{
  "browser": {
    "timeout": 60,
    "page_load_strategy": "eager"
  },
  "network": {
    "retry_attempts": 3,
    "retry_delay": 5.0
  }
}
```

#### Issue: SSL certificate errors
**Symptoms**: `ssl.SSLCertVerificationError` or certificate warnings.

**Solutions**:
```python
# Disable SSL verification (not recommended for production)
from selenium.webdriver.chrome.options import Options
options = Options()
options.add_argument('--ignore-ssl-errors')
options.add_argument('--ignore-certificate-errors')
```

### Proxy/VPN Issues

#### Issue: Proxy connection failed
**Symptoms**: Can't connect through configured proxy.

**Solutions**:
```bash
# Test proxy manually
curl --proxy http://proxy:port http://httpbin.org/ip

# Check proxy authentication
curl --proxy http://user:pass@proxy:port http://httpbin.org/ip

# Verify proxy is working
nslookup google.com proxy
```

#### Issue: VPN connection failed
**Symptoms**: VPN connection can't be established.

**Solutions**:
```bash
# Check VPN service status
sudo systemctl status openvpn

# Test VPN connection
ping 8.8.8.8

# Check VPN logs
sudo journalctl -u openvpn -f
```

## 🔍 Debugging Techniques

### Enable Debug Logging

#### Set Log Level
```bash
# Environment variable
export V0RTEX_LOG_LEVEL=DEBUG

# Configuration file
{
  "logging": {
    "level": "DEBUG",
    "console_output": true,
    "file_output": true
  }
}
```

#### Verbose CLI Output
```bash
# Run with verbose flag
v0rtex run -c config.json -v

# Check specific log files
tail -f /var/log/v0rtex/v0rtex.log
tail -f /var/log/v0rtex/debug.log
```

### Interactive Debugging

#### Python Debugger
```python
import pdb

def scrape_function():
    # ... code ...
    pdb.set_trace()  # Breakpoint here
    # ... more code ...
```

#### IPython Debugger
```python
from IPython import embed

def scrape_function():
    # ... code ...
    embed()  # Interactive shell
    # ... more code ...
```

### Browser Debugging

#### Chrome DevTools
```python
# Enable DevTools
options = webdriver.ChromeOptions()
options.add_argument('--auto-open-devtools-for-tabs')
options.add_argument('--remote-debugging-port=9222')

# Connect to existing Chrome instance
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
```

#### Screenshot Debugging
```python
# Take screenshots on errors
try:
    # ... scraping code ...
except Exception as e:
    driver.save_screenshot(f"error_{int(time.time())}.png")
    raise
```

### Network Debugging

#### Enable Network Logging
```python
# Enable Chrome performance logging
options = webdriver.ChromeOptions()
options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

# Get network logs
logs = driver.get_log('performance')
for log in logs:
    print(log['message'])
```

#### Proxy Debugging
```python
# Use mitmproxy for debugging
# Install: pip install mitmproxy
# Run: mitmproxy -p 8080

# Configure browser to use proxy
options = webdriver.ChromeOptions()
options.add_argument('--proxy-server=http://127.0.0.1:8080')
```

## 🆘 Getting Help

### Self-Help Resources

#### Check Documentation
- [API Reference](api-reference.md)
- [Configuration Guide](configuration.md)
- [Architecture Documentation](../architecture.md)

#### Search Issues
- Check existing GitHub issues
- Search error messages
- Look for similar problems

### Reporting Issues

#### Issue Template
```markdown
**Description**
Brief description of the problem

**Steps to Reproduce**
1. Step 1
2. Step 2
3. Step 3

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: [e.g., Ubuntu 22.04]
- Python: [e.g., 3.11.0]
- v0rtex: [e.g., 0.1.0]
- Browser: [e.g., Chrome 119]

**Configuration**
```json
{
  "name": "example",
  "target_url": "https://example.com"
}
```

**Logs**
```
Paste relevant log output here
```

**Additional Information**
Any other context about the problem
```

#### Debug Information
```bash
# Collect system information
python -c "import platform; print(platform.platform())"
python -c "import sys; print(sys.version)"
pip list | grep v0rtex

# Collect browser information
google-chrome --version
chromedriver --version

# Collect configuration
cat config.json | jq '.'

# Collect logs
tail -100 /var/log/v0rtex/v0rtex.log
```

### Community Support

#### GitHub Discussions
- Ask questions in GitHub Discussions
- Share solutions and workarounds
- Get help from the community

#### Discord/Slack
- Join community chat channels
- Real-time help and support
- Share experiences and tips

### Professional Support

#### Commercial Support
- Enterprise support plans
- Priority issue resolution
- Custom development services

#### Consulting Services
- Architecture review
- Performance optimization
- Custom feature development

## 📚 Related Documentation

- [Configuration Guide](configuration.md) - Configuration options
- [API Reference](api-reference.md) - API documentation
- [Deployment Guide](deployment.md) - Deployment instructions
- [Architecture Documentation](../architecture.md) - System architecture
