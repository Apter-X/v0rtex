"""
Main scraper class for v0rtex.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any, Union
from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import requests
import json
import os

from v0rtex.core.config import ScrapingConfig
from v0rtex.core.session import ScrapingSession
from v0rtex.utils.anti_detection import AntiDetectionManager
from v0rtex.utils.captcha_solver import CaptchaSolver
from v0rtex.utils.vpn_manager import VPNManager
from v0rtex.core.pagination import PaginationNavigator


class V0rtexScraper:
    """Main scraper class that orchestrates all components."""
    
    def __init__(self, config: ScrapingConfig):
        self.config = config
        self.session = ScrapingSession()
        self.anti_detection = AntiDetectionManager(config.anti_detection_level.value)
        self.captcha_solver = CaptchaSolver(config.captcha.api_keys)
        self.vpn_manager = VPNManager({
            "vpn_providers": {},
            "proxy_providers": {},
            "auto_rotation": config.vpn.auto_rotate,
            "rotation_interval": config.vpn.rotation_interval
        })
        
        self.driver = None
        self.current_page = None
        self.scraped_data = []
        
        # Pagination support
        self.pagination_navigator: Optional[PaginationNavigator] = None
        
        # Initialize components
        self._setup_session()
        self._setup_vpn_proxy()
    
    def _setup_session(self):
        """Setup scraping session."""
        try:
            # Create new session with anti-detection headers
            fingerprint = self.anti_detection.get_browser_fingerprint(
                self.config.browser.type.value
            )
            
            self.session.create_session(
                headers=fingerprint,
                user_agent=fingerprint.get("User-Agent"),
                cookies=self.config.cookies
            )
            
            logger.info("Session setup completed")
            
        except Exception as e:
            logger.error(f"Session setup failed: {e}")
    
    def _setup_vpn_proxy(self):
        """Setup VPN and proxy if configured."""
        try:
            # Setup proxy if configured
            if self.config.proxy:
                proxy_config = {
                    "name": "config_proxy",
                    "proxies": [{
                        "type": self.config.proxy.type.value,
                        "host": self.config.proxy.host,
                        "port": self.config.proxy.port,
                        "username": self.config.proxy.username,
                        "password": self.config.proxy.password
                    }]
                }
                
                self.vpn_manager.proxy_providers["config_proxy"] = self.vpn_manager.proxy_providers.get("config_proxy", None)
                if not self.vpn_manager.proxy_providers.get("config_proxy"):
                    from v0rtex.utils.vpn_manager import ProxyProvider
                    self.vpn_manager.proxy_providers["config_proxy"] = ProxyProvider("config_proxy", proxy_config)
                
                self.vpn_manager.set_proxy("config_proxy")
                logger.info("Proxy setup completed")
            
            # Setup VPN if enabled
            if self.config.vpn.enabled:
                # This would require VPN configuration files
                logger.info("VPN setup requires configuration files")
                
        except Exception as e:
            logger.error(f"VPN/Proxy setup failed: {e}")
    
    def _setup_driver(self):
        """Setup web driver based on configuration."""
        try:
            if self.config.browser.type.value == "undetected":
                # Note: undetected_chromedriver v3.5.5 has compatibility issues with newer Chrome versions
                # Falling back to standard Chrome with enhanced stealth options
                logger.warning("undetected mode has compatibility issues, using standard Chrome with stealth")
                
                options = ChromeOptions()
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-blink-features=AutomationControlled")
                
                if self.config.browser.headless:
                    options.add_argument("--headless")
                
                if self.config.browser.disable_images:
                    options.add_argument("--disable-images")
                
                if self.config.browser.disable_javascript:
                    options.add_argument("--disable-javascript")
                
                if self.config.browser.disable_css:
                    options.add_argument("--disable-css")
                
                # Set window size
                width, height = self.config.browser.window_size
                options.add_argument(f"--window-size={width},{height}")
                
                # Add stealth options
                if self.config.browser.stealth_mode:
                    options.add_experimental_option("excludeSwitches", ["enable-automation"])
                    options.add_experimental_option('useAutomationExtension', False)
                
                self.driver = webdriver.Chrome(options=options)
                
                # Execute stealth script
                if self.config.browser.stealth_mode:
                    self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                
            else:
                # Standard Selenium setup
                if self.config.browser.type.value == "chrome":
                    options = ChromeOptions()
                    options.add_argument("--no-sandbox")
                    options.add_argument("--disable-dev-shm-usage")
                    
                    if self.config.browser.headless:
                        options.add_argument("--headless")
                    
                    self.driver = webdriver.Chrome(options=options)
                    
                elif self.config.browser.type.value == "firefox":
                    options = FirefoxOptions()
                    
                    if self.config.browser.headless:
                        options.add_argument("--headless")
                    
                    self.driver = webdriver.Firefox(options=options)
                
                else:
                    raise ValueError(f"Unsupported browser type: {self.config.browser.type.value}")
            
            # Set window size
            width, height = self.config.browser.window_size
            self.driver.set_window_size(width, height)
            
            # Set user agent if specified
            if self.config.browser.user_agent:
                self.driver.execute_script(f"Object.defineProperty(navigator, 'userAgent', {{get: function () {{return '{self.config.browser.user_agent}';}}}});")
            
            logger.info(f"Web driver setup completed: {self.config.browser.type.value}")
            
        except Exception as e:
            logger.error(f"Driver setup failed: {e}")
            raise
    
    def _handle_login(self):
        """Handle login if required."""
        if not self.config.login_required or not self.config.login_url:
            return True
        
        try:
            logger.info("Handling login...")
            
            # Navigate to login page
            self.driver.get(self.config.login_url)
            
            # Wait for page to load
            time.sleep(self.config.wait_time)
            
            # Find and fill login form
            if self.config.login_credentials:
                # This is a simplified login - in practice, you'd need specific selectors
                username_field = self.driver.find_element(By.NAME, "username")
                password_field = self.driver.find_element(By.NAME, "password")
                
                username_field.send_keys(self.config.login_credentials.get("username", ""))
                password_field.send_keys(self.config.login_credentials.get("password", ""))
                
                # Submit form
                submit_button = self.driver.find_element(By.TYPE, "submit")
                submit_button.click()
                
                # Wait for login to complete
                time.sleep(self.config.wait_time)
                
                # Check if login was successful
                if "login" not in self.driver.current_url.lower():
                    logger.info("Login successful")
                    return True
                else:
                    logger.error("Login failed")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Login handling failed: {e}")
            return False
    
    def _handle_captcha(self):
        """Handle CAPTCHA if detected."""
        try:
            # Check for reCAPTCHA
            recaptcha_elements = self.driver.find_elements(By.CLASS_NAME, "g-recaptcha")
            if recaptcha_elements:
                logger.info("reCAPTCHA detected, attempting to solve...")
                
                # Get site key
                site_key = recaptcha_elements[0].get_attribute("data-sitekey")
                if site_key:
                    solution = self.captcha_solver.solve_recaptcha(
                        site_key, 
                        self.driver.current_url
                    )
                    
                    if solution:
                        # Execute solution
                        self.driver.execute_script(
                            f"document.getElementById('g-recaptcha-response').innerHTML = '{solution}';"
                        )
                        logger.info("reCAPTCHA solved")
                        return True
            
            # Check for hCaptcha
            hcaptcha_elements = self.driver.find_elements(By.CLASS_NAME, "h-captcha")
            if hcaptcha_elements:
                logger.info("hCaptcha detected, attempting to solve...")
                
                site_key = hcaptcha_elements[0].get_attribute("data-sitekey")
                if site_key:
                    solution = self.captcha_solver.solve_hcaptcha(
                        site_key,
                        self.driver.current_url
                    )
                    
                    if solution:
                        # Execute solution
                        self.driver.execute_script(
                            f"document.querySelector('[name=h-captcha-response]').value = '{solution}';"
                        )
                        logger.info("hCaptcha solved")
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"CAPTCHA handling failed: {e}")
            return False
    
    def _extract_data(self) -> Dict[str, Any]:
        """Extract data from current page based on configuration."""
        try:
            data = {}
            
            # Get page source
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract data using selectors
            for field_name, selector in self.config.selectors.items():
                try:
                    elements = soup.select(selector)
                    if elements:
                        if len(elements) == 1:
                            data[field_name] = elements[0].get_text(strip=True)
                        else:
                            data[field_name] = [elem.get_text(strip=True) for elem in elements]
                    else:
                        data[field_name] = None
                except Exception as e:
                    logger.warning(f"Failed to extract field {field_name}: {e}")
                    data[field_name] = None
            
            # Extract data using data mapping
            for field_name, mapping in self.config.data_mapping.items():
                try:
                    if mapping.startswith("css:"):
                        selector = mapping[4:]
                        elements = soup.select(selector)
                        if elements:
                            data[field_name] = elements[0].get_text(strip=True)
                    elif mapping.startswith("xpath:"):
                        # XPath extraction would need lxml
                        pass
                    else:
                        # Direct attribute mapping
                        data[field_name] = mapping
                except Exception as e:
                    logger.warning(f"Failed to extract mapped field {field_name}: {e}")
                    data[field_name] = None
            
            # Add metadata
            data["_metadata"] = {
                "url": self.driver.current_url,
                "timestamp": time.time(),
                "user_agent": self.driver.execute_script("return navigator.userAgent;"),
                "ip": self.vpn_manager.get_current_ip()
            }
            
            return data
            
        except Exception as e:
            logger.error(f"Data extraction failed: {e}")
            return {}
    
    def _save_data(self, data: Dict[str, Any]):
        """Save extracted data."""
        try:
            self.scraped_data.append(data)
            
            if self.config.save_to_file:
                output_file = self.config.output_file or f"scraped_data_{int(time.time())}.json"
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(self.scraped_data, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Data saved to {output_file}")
            
        except Exception as e:
            logger.error(f"Data saving failed: {e}")
    
    def scrape(self) -> List[Dict[str, Any]]:
        """Main scraping method."""
        try:
            logger.info(f"Starting scraping: {self.config.name}")
            
            # Setup web driver
            self._setup_driver()
            
            # Handle login if required
            if not self._handle_login():
                raise Exception("Login failed")
            
            # Navigate to target URL
            self.driver.get(self.config.target_url)
            self.current_page = self.config.target_url
            
            # Wait for page to load
            time.sleep(self.config.wait_time)
            
            # Wait for specific elements if configured
            if self.config.wait_for_elements:
                for selector in self.config.wait_for_elements:
                    try:
                        WebDriverWait(self.driver, self.config.timeout).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                    except TimeoutException:
                        logger.warning(f"Element not found: {selector}")
            
            # Handle CAPTCHA if detected
            if self.config.captcha.enabled:
                self._handle_captcha()
            
            # Execute custom scripts if configured
            if self.config.custom_scripts:
                for script in self.config.custom_scripts:
                    try:
                        self.driver.execute_script(script)
                    except Exception as e:
                        logger.warning(f"Custom script failed: {e}")
            
            # Extract data
            data = self._extract_data()
            
            # Save data
            self._save_data(data)
            
            logger.info("Scraping completed successfully")
            return self.scraped_data
            
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            
            # Take screenshot on error if configured
            if self.config.screenshot_on_error:
                try:
                    screenshot_file = f"error_screenshot_{int(time.time())}.png"
                    self.driver.save_screenshot(screenshot_file)
                    logger.info(f"Error screenshot saved: {screenshot_file}")
                except Exception as se:
                    logger.error(f"Failed to save error screenshot: {se}")
            
            raise
        
        finally:
            # Cleanup
            if self.driver:
                self.driver.quit()
    
    def scrape_multiple(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Scrape multiple URLs."""
        results = []
        
        for i, url in enumerate(urls):
            try:
                logger.info(f"Scraping URL {i+1}/{len(urls)}: {url}")
                
                # Update target URL
                self.config.target_url = url
                
                # Scrape single URL
                data = self.scrape()
                results.extend(data)
                
                # Rate limiting
                if self.config.rate_limit.enabled and i < len(urls) - 1:
                    delay = self.config.rate_limit.delay_between_requests
                    if self.config.rate_limit.random_delay:
                        delay += self.anti_detection.add_random_delay(
                            delay, 
                            self.config.rate_limit.delay_variance
                        )
                    else:
                        time.sleep(delay)
                
            except Exception as e:
                logger.error(f"Failed to scrape {url}: {e}")
                continue
        
        return results
    
    def get_status(self) -> Dict[str, Any]:
        """Get scraper status."""
        status = {
            "config": self.config.model_dump(),
            "session": self.session.get_session_stats(),
            "anti_detection": self.anti_detection.get_fingerprint_stats(),
            "vpn_proxy": self.vpn_manager.get_status(),
            "captcha_services": self.captcha_solver.get_available_services(),
            "scraped_count": len(self.scraped_data),
            "current_page": self.current_page,
            "driver_active": self.driver is not None
        }
        
        # Add pagination status if available
        if self.pagination_navigator:
            status["pagination"] = self.pagination_navigator.get_pagination_info()
        
        return status
    
    def _initialize_pagination(self) -> bool:
        """Initialize pagination if enabled."""
        if not self.config.pagination.enabled:
            logger.info("Pagination is disabled in configuration")
            return False
        
        if not self.driver:
            logger.error("Cannot initialize pagination without driver")
            return False
        
        try:
            self.pagination_navigator = PaginationNavigator(self.config.model_dump(), self.driver)
            success = self.pagination_navigator.initialize()
            
            if success:
                logger.info("Pagination initialized successfully")
                return True
            else:
                logger.info("Pagination initialization failed - no pagination detected")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize pagination: {e}")
            return False
    
    def scrape_with_pagination(self, data_extractor: Optional[callable] = None) -> List[Dict[str, Any]]:
        """
        Scrape data with pagination support.
        
        Args:
            data_extractor: Optional function to extract data from each page.
                          Should return the number of items found on the page.
        
        Returns:
            List of scraped data from all pages
        """
        if not self.config.pagination.enabled:
            logger.warning("Pagination is disabled, falling back to single page scraping")
            return self.scrape()
        
        try:
            logger.info("Starting pagination-aware scraping...")
            
            # Setup driver if not already done
            if not self.driver:
                self._setup_driver()
            
            # Navigate to target URL
            self.driver.get(self.config.target_url)
            time.sleep(self.config.wait_time)
            
            # Handle login if required
            if self.config.login_required:
                self._handle_login()
            
            # Initialize pagination
            if not self._initialize_pagination():
                logger.info("No pagination detected, scraping single page")
                return self.scrape()
            
            # Start pagination loop
            all_data = []
            page_count = 0
            
            while self.pagination_navigator.can_continue():
                page_count += 1
                logger.info(f"Processing page {page_count}")
                
                try:
                    # Extract data from current page
                    if data_extractor:
                        items_found = data_extractor(self.driver)
                        logger.info(f"Extracted {items_found} items from page {page_count}")
                    else:
                        # Use default data extraction
                        page_data = self._extract_data()
                        items_found = len(page_data) if isinstance(page_data, list) else 1
                        all_data.extend(page_data if isinstance(page_data, list) else [page_data])
                        logger.info(f"Extracted {items_found} items from page {page_count}")
                    
                    # Check if we've reached item limit
                    if self.config.pagination.limits.max_items and len(all_data) >= self.config.pagination.limits.max_items:
                        logger.info(f"Reached maximum item limit: {self.config.pagination.limits.max_items}")
                        break
                    
                    # Navigate to next page
                    if not self.pagination_navigator.navigate_to_next(data_extractor):
                        logger.info("Failed to navigate to next page, stopping pagination")
                        break
                    
                    # Rate limiting between pages
                    if self.config.rate_limit.enabled:
                        delay = self.config.rate_limit.delay_between_requests
                        if self.config.rate_limit.random_delay:
                            delay += self.anti_detection.add_random_delay(
                                delay, 
                                self.config.rate_limit.delay_variance
                            )
                        time.sleep(delay)
                    
                except Exception as e:
                    logger.error(f"Error processing page {page_count}: {e}")
                    
                    # Handle pagination error
                    if self.pagination_navigator:
                        if not self.pagination_navigator.handle_pagination_error(e, f"page_{page_count}"):
                            logger.error("Too many pagination errors, stopping")
                            break
                    else:
                        break
            
            logger.info(f"Pagination scraping completed. Processed {page_count} pages, extracted {len(all_data)} total items")
            return all_data
            
        except Exception as e:
            logger.error(f"Pagination scraping failed: {e}")
            raise
        
        finally:
            # Cleanup
            if self.driver:
                self.driver.quit()
    
    def get_pagination_status(self) -> Dict[str, Any]:
        """Get detailed pagination status."""
        if not self.pagination_navigator:
            return {"status": "not_initialized", "message": "Pagination not initialized"}
        
        return self.pagination_navigator.get_pagination_info()
    
    def get_pagination_progress(self) -> Dict[str, Any]:
        """Get pagination progress information."""
        if not self.pagination_navigator:
            return {"status": "not_initialized"}
        
        return self.pagination_navigator.get_progress()
    
    def save_pagination_state(self, file_path: str) -> bool:
        """Save current pagination state to file."""
        if not self.pagination_navigator:
            logger.warning("Cannot save pagination state - pagination not initialized")
            return False
        
        try:
            from pathlib import Path
            self.pagination_navigator.save_state(Path(file_path))
            return True
        except Exception as e:
            logger.error(f"Failed to save pagination state: {e}")
            return False
    
    def load_pagination_state(self, file_path: str) -> bool:
        """Load pagination state from file."""
        if not self.pagination_navigator:
            logger.warning("Cannot load pagination state - pagination not initialized")
            return False
        
        try:
            from pathlib import Path
            return self.pagination_navigator.load_state(Path(file_path))
        except Exception as e:
            logger.error(f"Failed to load pagination state: {e}")
            return False
    
    def reset_pagination(self) -> None:
        """Reset pagination state."""
        if self.pagination_navigator:
            self.pagination_navigator.reset()
            logger.info("Pagination state reset")
    
    def get_pagination_summary(self) -> str:
        """Get human-readable pagination summary."""
        if not self.pagination_navigator:
            return "Pagination not initialized"
        
        return self.pagination_navigator.get_navigation_summary()
    
    def cleanup(self):
        """Cleanup resources."""
        try:
            if self.driver:
                self.driver.quit()
            
            # Save pagination state if available
            if self.pagination_navigator and self.config.pagination.enabled:
                try:
                    state_file = f"pagination_state_{int(time.time())}.json"
                    self.save_pagination_state(state_file)
                    logger.info(f"Pagination state saved to {state_file}")
                except Exception as e:
                    logger.warning(f"Failed to save pagination state: {e}")
            
            self.vpn_manager.stop_auto_rotation()
            
            logger.info("Cleanup completed")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
