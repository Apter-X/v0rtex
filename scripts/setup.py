#!/usr/bin/env python3
"""
Setup script for v0rtex project.
"""

import os
import sys
import subprocess
import json
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True


def create_directories():
    """Create necessary directories."""
    directories = [
        "logs",
        "sessions",
        "examples",
        "docs",
        "tests"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")


def create_env_file():
    """Create .env file with template."""
    env_content = """# v0rtex Environment Configuration

# CAPTCHA Service API Keys
2CAPTCHA_API_KEY=your_2captcha_api_key_here
ANTICAPTCHA_API_KEY=your_anticaptcha_api_key_here

# VPN Configuration (optional)
VPN_PROVIDER=openvpn
VPN_CONFIG_PATH=/path/to/vpn/config.ovpn

# Proxy Configuration (optional)
PROXY_HOST=proxy.example.com
PROXY_PORT=8080
PROXY_USERNAME=username
PROXY_PASSWORD=password

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/v0rtex.log

# Anti-Detection Settings
ANTI_DETECTION_LEVEL=medium
STEALTH_MODE=true
"""
    
    env_file = Path(".env")
    if not env_file.exists():
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ Created .env file")
    else:
        print("ℹ️  .env file already exists")


def create_sample_configs():
    """Create sample configuration files."""
    basic_config = {
        "name": "Basic Web Scraping Example",
        "description": "Simple example for scraping a website",
        "target_url": "https://example.com",
        "method": "GET",
        "headers": {},
        "cookies": {},
        "login_required": False,
        "anti_detection_level": "medium",
        "browser": {
            "type": "undetected",
            "headless": False,
            "window_size": [1920, 1080],
            "stealth_mode": True,
            "fingerprint_spoofing": True
        },
        "proxy": None,
        "vpn": {
            "enabled": False,
            "auto_rotate": False,
            "rotation_interval": 300
        },
        "captcha": {
            "enabled": True,
            "auto_solve": True,
            "services": ["2captcha", "anticaptcha"],
            "api_keys": {},
            "timeout": 120,
            "retry_attempts": 3
        },
        "rate_limit": {
            "enabled": True,
            "requests_per_minute": 60,
            "delay_between_requests": 1.0,
            "random_delay": True,
            "delay_variance": 0.5
        },
        "selectors": {
            "title": "h1",
            "description": "p",
            "links": "a[href]"
        },
        "wait_time": 2.0,
        "max_retries": 3,
        "timeout": 30,
        "follow_redirects": True,
        "verify_ssl": True,
        "data_mapping": {},
        "output_format": "json",
        "save_to_file": True,
        "output_file": "scraped_data.json",
        "custom_scripts": [],
        "wait_for_elements": [],
        "scroll_behavior": None,
        "screenshot_on_error": False
    }
    
    config_file = Path("examples/basic_scraping.json")
    with open(config_file, 'w') as f:
        json.dump(basic_config, f, indent=2)
    print("✅ Created basic configuration example")


def install_dependencies():
    """Install project dependencies."""
    print("🔄 Installing dependencies...")
    
    # Install base requirements
    if not run_command("pip install -r requirements.txt", "Installing base requirements"):
        return False
    
    # Install development dependencies
    if not run_command("pip install -e .[dev]", "Installing development dependencies"):
        return False
    
    return True


def setup_pre_commit():
    """Setup pre-commit hooks."""
    try:
        import pre_commit
        if run_command("pre-commit install", "Installing pre-commit hooks"):
            print("✅ Pre-commit hooks installed")
        else:
            print("⚠️  Pre-commit hooks installation failed")
    except ImportError:
        print("ℹ️  Pre-commit not available, skipping hooks installation")


def main():
    """Main setup function."""
    print("🚀 Setting up v0rtex project...")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Create environment file
    create_env_file()
    
    # Create sample configurations
    create_sample_configs()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Dependency installation failed")
        sys.exit(1)
    
    # Setup pre-commit
    setup_pre_commit()
    
    print("=" * 50)
    print("🎉 v0rtex project setup completed successfully!")
    print("\nNext steps:")
    print("1. Update .env file with your API keys")
    print("2. Modify examples/basic_scraping.json for your target website")
    print("3. Run: v0rtex run -c examples/basic_scraping.json")
    print("\nFor more information, see README.md")


if __name__ == "__main__":
    main()
