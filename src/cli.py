"""
Command-line interface for v0rtex scraper.
"""

import argparse
import json
import sys
import os
from pathlib import Path
from loguru import logger
from typing import Optional

from .core.scraper import V0rtexScraper
from .core.config import ScrapingConfig


def setup_logging(verbose: bool = False, log_file: Optional[str] = None):
    """Setup logging configuration."""
    # Remove default handler
    logger.remove()
    
    # Add console handler
    log_level = "DEBUG" if verbose else "INFO"
    logger.add(sys.stderr, level=log_level, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
    
    # Add file handler if specified
    if log_file:
        logger.add(log_file, level="DEBUG", format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}")


def load_config(config_path: str) -> ScrapingConfig:
    """Load configuration from file."""
    try:
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        return ScrapingConfig.load_from_file(config_path)
    
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)


def validate_config(config: ScrapingConfig) -> bool:
    """Validate configuration."""
    try:
        # Basic validation
        if not config.target_url:
            logger.error("Target URL is required")
            return False
        
        if config.login_required and not config.login_url:
            logger.error("Login URL is required when login_required is true")
            return False
        
        if config.login_required and not config.login_credentials:
            logger.error("Login credentials are required when login_required is true")
            return False
        
        # Validate CAPTCHA configuration
        if config.captcha.enabled:
            if not config.captcha.api_keys:
                logger.warning("CAPTCHA is enabled but no API keys provided")
        
        # Validate proxy configuration
        if config.proxy:
            if not config.proxy.host or not config.proxy.port:
                logger.error("Proxy host and port are required")
                return False
        
        logger.info("Configuration validation passed")
        return True
    
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        return False


def run_scraper(config: ScrapingConfig, output_file: Optional[str] = None) -> bool:
    """Run the scraper with given configuration."""
    scraper = None
    
    try:
        logger.info(f"Initializing scraper: {config.name}")
        
        # Create scraper instance
        scraper = V0rtexScraper(config)
        
        # Get initial status
        status = scraper.get_status()
        logger.info(f"Scraper status: {json.dumps(status, indent=2)}")
        
        # Run scraping
        logger.info("Starting scraping process...")
        results = scraper.scrape()
        
        # Save results if output file specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Results saved to: {output_file}")
        
        logger.info(f"Scraping completed successfully. Extracted {len(results)} data items.")
        return True
    
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        return False
    
    finally:
        if scraper:
            scraper.cleanup()


def run_multiple_urls(config: ScrapingConfig, urls: list, output_file: Optional[str] = None) -> bool:
    """Run scraper on multiple URLs."""
    scraper = None
    
    try:
        logger.info(f"Initializing scraper for multiple URLs: {config.name}")
        
        # Create scraper instance
        scraper = V0rtexScraper(config)
        
        # Run scraping on multiple URLs
        logger.info(f"Starting scraping process for {len(urls)} URLs...")
        results = scraper.scrape_multiple(urls)
        
        # Save results if output file specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Results saved to: {output_file}")
        
        logger.info(f"Scraping completed successfully. Extracted {len(results)} data items from {len(urls)} URLs.")
        return True
    
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        return False
    
    finally:
        if scraper:
            scraper.cleanup()


def create_sample_config(output_path: str):
    """Create a sample configuration file."""
    try:
        sample_config = {
            "name": "Sample Scraping Configuration",
            "description": "A sample configuration file for v0rtex scraper",
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
                "content": "p"
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
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(sample_config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Sample configuration created: {output_path}")
        
    except Exception as e:
        logger.error(f"Failed to create sample configuration: {e}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="v0rtex - Dynamic JSON-based web scraper with anti-detection capabilities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run scraper with configuration file
  v0rtex run -c config.json
  
  # Run scraper with multiple URLs
  v0rtex run -c config.json -u "https://example1.com" -u "https://example2.com"
  
  # Create sample configuration
  v0rtex init -o sample_config.json
  
  # Run with verbose logging
  v0rtex run -c config.json -v
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run the scraper')
    run_parser.add_argument('-c', '--config', required=True, help='Configuration file path')
    run_parser.add_argument('-u', '--urls', action='append', help='Additional URLs to scrape (optional)')
    run_parser.add_argument('-o', '--output', help='Output file path for results')
    run_parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging')
    run_parser.add_argument('-l', '--log-file', help='Log file path')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize sample configuration')
    init_parser.add_argument('-o', '--output', default='v0rtex_config.json', help='Output file path')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Setup logging
    setup_logging(args.verbose if hasattr(args, 'verbose') else False, 
                  args.log_file if hasattr(args, 'log_file') else None)
    
    try:
        if args.command == 'run':
            # Load and validate configuration
            config = load_config(args.config)
            if not validate_config(config):
                sys.exit(1)
            
            # Run scraper
            if args.urls:
                success = run_multiple_urls(config, args.urls, args.output)
            else:
                success = run_scraper(config, args.output)
            
            if not success:
                sys.exit(1)
        
        elif args.command == 'init':
            create_sample_config(args.output)
        
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
