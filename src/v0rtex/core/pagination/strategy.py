"""
Pagination strategy implementations for v0rtex web scraper.

This module provides different pagination strategies for handling various
website pagination patterns including URL-based, JavaScript-based, and infinite scroll.
"""

import logging
import re
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)


class PaginationStrategy(ABC):
    """Abstract base class for pagination strategies."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.wait_time = config.get('navigation', {}).get('wait_time', 2)
        self.retry_attempts = config.get('navigation', {}).get('retry_attempts', 3)
    
    @abstractmethod
    def can_handle(self, driver: WebDriver) -> bool:
        """Check if this strategy can handle the current page."""
        pass
    
    @abstractmethod
    def get_next_page(self, driver: WebDriver, current_url: str) -> Optional[str]:
        """Get the next page URL or action."""
        pass
    
    @abstractmethod
    def navigate_to_next(self, driver: WebDriver) -> bool:
        """Navigate to the next page using this strategy."""
        pass
    
    @abstractmethod
    def get_total_pages(self, driver: WebDriver) -> Optional[int]:
        """Get the total number of pages if available."""
        pass


class URLPaginationStrategy(PaginationStrategy):
    """Handles URL-based pagination (e.g., ?page=2, &p=3)."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.url_patterns = config.get('url_patterns', [
            r'[?&]page=(\d+)',
            r'[?&]p=(\d+)',
            r'[?&]pg=(\d+)',
            r'[?&]pageno=(\d+)',
            r'/page/(\d+)',
            r'/p/(\d+)'
        ])
        self.page_param = config.get('page_param', 'page')
    
    def can_handle(self, driver: WebDriver) -> bool:
        """Check if current page has URL-based pagination."""
        current_url = driver.current_url
        
        # Check if URL matches any known pagination patterns
        for pattern in self.url_patterns:
            if re.search(pattern, current_url):
                return True
        
        # Check if we can add a page parameter
        parsed = urlparse(current_url)
        return True  # Most URLs can accept page parameters
    
    def get_next_page(self, driver: WebDriver, current_url: str) -> Optional[str]:
        """Get the next page URL by modifying the current URL."""
        parsed = urlparse(current_url)
        query_params = parse_qs(parsed.query)
        
        # Get current page number
        current_page = 1
        path_pattern_matched = False
        
        # First check for path-based patterns (e.g., /page/2/)
        for pattern in self.url_patterns:
            if pattern.startswith('/'):
                match = re.search(pattern, current_url)
                if match:
                    current_page = int(match.group(1))
                    path_pattern_matched = True
                    break
        
        # If no path pattern matched, check query parameters
        if not path_pattern_matched:
            for pattern in self.url_patterns:
                if not pattern.startswith('/'):
                    match = re.search(pattern, current_url)
                    if match:
                        current_page = int(match.group(1))
                        break
        
        # If no pattern matched at all, assume we're on page 1
        # This handles cases where the first page doesn't have /page/1/ in the URL
        if not path_pattern_matched and current_page == 1:
            # For path-based pagination, we need to construct the first page URL
            # to establish the pattern, then we can increment from there
            pass
        
        # Create next page URL
        next_page = current_page + 1
        
        if path_pattern_matched:
            # Handle path-based pagination (e.g., /page/2/ -> /page/3/)
            for pattern in self.url_patterns:
                if pattern.startswith('/'):
                    match = re.search(pattern, current_url)
                    if match:
                        # Replace the page number in the path
                        next_url = re.sub(pattern, f'/page/{next_page}/', current_url)
                        logger.info(f"Generated next page URL (path-based): {next_url}")
                        return next_url
        else:
            # Handle query parameter pagination (e.g., ?page=2 -> ?page=3)
            if current_page == 1 and not path_pattern_matched:
                # We're on the first page with no pattern, need to construct the pattern
                # For eShop Maroc, this would be adding /page/2/ to the base URL
                base_url = current_url.rstrip('/')
                if not base_url.endswith('/page/1'):
                    # Add the page pattern to the base URL
                    next_url = f"{base_url}/page/{next_page}/"
                    logger.info(f"Generated next page URL (first page pattern): {next_url}")
                    return next_url
            
            # Standard query parameter handling
            query_params[self.page_param] = [str(next_page)]
            new_query = urlencode(query_params, doseq=True)
            next_url = urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                new_query,
                parsed.fragment
            ))
            logger.info(f"Generated next page URL (query-based): {next_url}")
            return next_url
        
        return None
    
    def navigate_to_next(self, driver: WebDriver) -> bool:
        """Navigate to the next page by changing the URL."""
        try:
            current_url = driver.current_url
            logger.info(f"Current URL: {current_url}")
            
            next_url = self.get_next_page(driver, current_url)
            logger.info(f"Generated next URL: {next_url}")
            
            if next_url:
                logger.info(f"Navigating to: {next_url}")
                driver.get(next_url)
                time.sleep(self.wait_time)
                
                # Wait for page to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                logger.info(f"Successfully navigated to next page: {next_url}")
                return True
            else:
                logger.warning("No next URL generated")
            
        except Exception as e:
            logger.error(f"Failed to navigate to next page: {e}")
        
        return False
    
    def get_total_pages(self, driver: WebDriver) -> Optional[int]:
        """Try to extract total pages from the current page."""
        try:
            # Look for common total page indicators
            total_page_selectors = [
                ".pagination .total",
                ".pagination .last",
                ".pagination .count",
                "[data-total-pages]",
                "[data-last-page]"
            ]
            
            for selector in total_page_selectors:
                try:
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                    text = element.text.strip()
                    
                    # Extract number from text
                    numbers = re.findall(r'\d+', text)
                    if numbers:
                        return int(numbers[-1])  # Usually the last number is total pages
                        
                except NoSuchElementException:
                    continue
            
            # Try to find pagination links and get the highest page number
            pagination_links = driver.find_elements(By.CSS_SELECTOR, ".pagination a, .pagination .page")
            page_numbers = []
            
            for link in pagination_links:
                try:
                    text = link.text.strip()
                    if text.isdigit():
                        page_numbers.append(int(text))
                except (ValueError, AttributeError):
                    continue
            
            if page_numbers:
                return max(page_numbers)
                
        except Exception as e:
            logger.warning(f"Could not determine total pages: {e}")
        
        return None


class JavaScriptPaginationStrategy(PaginationStrategy):
    """Handles JavaScript-based pagination (clicking next buttons, etc.)."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.selectors = config.get('selectors', {})
        self.next_button_selector = self.selectors.get('next_button', '.pagination .next, .pagination .next-page')
        self.prev_button_selector = self.selectors.get('prev_button', '.pagination .prev, .pagination .prev-page')
        self.page_number_selector = self.selectors.get('page_numbers', '.pagination .page, .pagination a')
        self.current_page_selector = self.selectors.get('current_page', '.pagination .current, .pagination .active')
    
    def can_handle(self, driver: WebDriver) -> bool:
        """Check if current page has JavaScript-based pagination."""
        try:
            # Look for pagination elements
            pagination_elements = driver.find_elements(By.CSS_SELECTOR, 
                ".pagination, .pager, .page-navigation, [class*='pagination'], [class*='pager']")
            
            if pagination_elements:
                return True
            
            # Check for next/previous buttons
            next_buttons = driver.find_elements(By.CSS_SELECTOR, self.next_button_selector)
            if next_buttons:
                return True
                
        except Exception as e:
            logger.debug(f"Error checking JavaScript pagination: {e}")
        
        return False
    
    def get_next_page(self, driver: WebDriver, current_url: str) -> Optional[str]:
        """For JavaScript pagination, we return the current URL since navigation happens via clicks."""
        return current_url
    
    def navigate_to_next(self, driver: WebDriver) -> bool:
        """Navigate to the next page by clicking the next button."""
        try:
            # Try to find and click the next button
            next_button = driver.find_element(By.CSS_SELECTOR, self.next_button_selector)
            
            if next_button and next_button.is_enabled():
                # Scroll to button if needed
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                time.sleep(0.5)
                
                # Click the next button
                next_button.click()
                time.sleep(self.wait_time)
                
                # Wait for page content to change
                WebDriverWait(driver, 10).until(
                    EC.staleness_of(next_button)
                )
                
                logger.info("Successfully clicked next button")
                return True
            else:
                logger.info("Next button not found or disabled")
                return False
                
        except NoSuchElementException:
            logger.info("Next button not found")
            return False
        except Exception as e:
            logger.error(f"Failed to navigate to next page: {e}")
            return False
    
    def get_total_pages(self, driver: WebDriver) -> Optional[int]:
        """Try to extract total pages from pagination elements."""
        try:
            # Look for current page indicator
            current_element = driver.find_element(By.CSS_SELECTOR, self.current_page_selector)
            if current_element:
                current_text = current_element.text.strip()
                current_page = int(current_text) if current_text.isdigit() else 1
            else:
                current_page = 1
            
            # Look for total pages in pagination
            page_elements = driver.find_elements(By.CSS_SELECTOR, self.page_number_selector)
            page_numbers = []
            
            for element in page_elements:
                try:
                    text = element.text.strip()
                    if text.isdigit():
                        page_numbers.append(int(text))
                except (ValueError, AttributeError):
                    continue
            
            if page_numbers:
                max_page = max(page_numbers)
                # If we're on page 1 and see page 5, assume there are at least 5 pages
                if current_page == 1 and max_page > 1:
                    return max_page
            
            # Look for "of X pages" text
            pagination_text = driver.find_elements(By.CSS_SELECTOR, ".pagination, .pager")
            for element in pagination_text:
                text = element.text.lower()
                if "of" in text and "page" in text:
                    numbers = re.findall(r'\d+', text)
                    if len(numbers) >= 2:
                        return int(numbers[-1])  # Usually the last number is total pages
                        
        except Exception as e:
            logger.warning(f"Could not determine total pages: {e}")
        
        return None


class InfiniteScrollStrategy(PaginationStrategy):
    """Handles infinite scroll pagination."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.scroll_pause = config.get('navigation', {}).get('scroll_pause', 1)
        self.max_scrolls = config.get('max_scrolls', 50)
        self.scroll_threshold = config.get('scroll_threshold', 100)  # pixels from bottom
    
    def can_handle(self, driver: WebDriver) -> bool:
        """Check if current page uses infinite scroll."""
        try:
            # Look for infinite scroll indicators
            scroll_indicators = [
                "[data-infinite-scroll]",
                "[class*='infinite']",
                "[class*='scroll']",
                ".load-more",
                ".infinite-scroll"
            ]
            
            for selector in scroll_indicators:
                if driver.find_elements(By.CSS_SELECTOR, selector):
                    return True
            
            # Check for load more buttons
            load_more = driver.find_elements(By.CSS_SELECTOR, ".load-more, .load-more-btn, .show-more")
            if load_more:
                return True
                
        except Exception as e:
            logger.debug(f"Error checking infinite scroll: {e}")
        
        return False
    
    def get_next_page(self, driver: WebDriver, current_url: str) -> Optional[str]:
        """For infinite scroll, we return the current URL since content loads dynamically."""
        return current_url
    
    def navigate_to_next(self, driver: WebDriver) -> bool:
        """Load more content by scrolling or clicking load more button."""
        try:
            # First try to find and click a load more button
            load_more_selectors = [".load-more", ".load-more-btn", ".show-more", ".infinite-scroll-trigger"]
            
            for selector in load_more_selectors:
                try:
                    load_more_btn = driver.find_element(By.CSS_SELECTOR, selector)
                    if load_more_btn and load_more_btn.is_enabled():
                        # Scroll to button
                        driver.execute_script("arguments[0].scrollIntoView(true);", load_more_btn)
                        time.sleep(0.5)
                        
                        # Click load more
                        load_more_btn.click()
                        time.sleep(self.wait_time)
                        
                        logger.info("Clicked load more button")
                        return True
                        
                except NoSuchElementException:
                    continue
            
            # If no load more button, try scrolling
            initial_height = driver.execute_script("return document.body.scrollHeight")
            
            # Scroll to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(self.scroll_pause)
            
            # Check if content loaded
            new_height = driver.execute_script("return document.body.scrollHeight")
            
            if new_height > initial_height:
                logger.info("Scrolled to load more content")
                return True
            else:
                logger.info("No more content to load")
                return False
                
        except Exception as e:
            logger.error(f"Failed to load more content: {e}")
            return False
    
    def get_total_pages(self, driver: WebDriver) -> Optional[int]:
        """For infinite scroll, we can't determine total pages easily."""
        return None  # Infinite scroll doesn't have traditional page counts


class AutoPaginationStrategy(PaginationStrategy):
    """Automatically detects and uses the best pagination strategy."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.strategies = [
            URLPaginationStrategy(config),
            JavaScriptPaginationStrategy(config),
            InfiniteScrollStrategy(config)
        ]
        self.current_strategy = None
    
    def can_handle(self, driver: WebDriver) -> bool:
        """Check if any strategy can handle the current page."""
        for strategy in self.strategies:
            if strategy.can_handle(driver):
                self.current_strategy = strategy
                logger.info(f"Auto-detected pagination strategy: {strategy.__class__.__name__}")
                return True
        return False
    
    def get_next_page(self, driver: WebDriver, current_url: str) -> Optional[str]:
        """Delegate to the current strategy."""
        if self.current_strategy:
            return self.current_strategy.get_next_page(driver, current_url)
        return None
    
    def navigate_to_next(self, driver: WebDriver) -> bool:
        """Delegate to the current strategy."""
        if self.current_strategy:
            return self.current_strategy.navigate_to_next(driver)
        return False
    
    def get_total_pages(self, driver: WebDriver) -> Optional[int]:
        """Delegate to the current strategy."""
        if self.current_strategy:
            return self.current_strategy.get_total_pages(driver)
        return None
