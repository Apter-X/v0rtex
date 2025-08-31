"""
Pagination navigation for v0rtex web scraper.

This module handles the actual navigation between pages and manages
the pagination workflow including retry logic and error handling.
"""

import logging
import time
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import WebDriverException, TimeoutException

from .state import PaginationState
from .strategy import PaginationStrategy
from .detector import PaginationDetector

logger = logging.getLogger(__name__)


class PaginationNavigator:
    """Handles navigation between pages during pagination."""
    
    def __init__(self, config: Dict[str, Any], driver: WebDriver):
        self.config = config
        self.driver = driver
        self.pagination_config = config.get('pagination', {})
        
        # Initialize components
        self.detector = PaginationDetector(config)
        self.state = PaginationState()
        self.strategy: Optional[PaginationStrategy] = None
        
        # Configuration
        self.max_pages = self.pagination_config.get('limits', {}).get('max_pages', 100)
        self.max_items = self.pagination_config.get('limits', {}).get('max_items', 1000)
        self.retry_attempts = self.pagination_config.get('navigation', {}).get('retry_attempts', 3)
        self.wait_time = self.pagination_config.get('navigation', {}).get('wait_time', 2)
        
        # State tracking
        self.is_initialized = False
        self.current_strategy_name = None
    
    def initialize(self) -> bool:
        """Initialize pagination detection and strategy selection."""
        try:
            logger.info("Initializing pagination navigation...")
            
            # Detect pagination
            has_pagination, strategy_name, pagination_info = self.detector.detect_pagination(self.driver)
            
            if not has_pagination:
                logger.info("No pagination detected on current page")
                return False
            
            # Create strategy
            self.strategy = self.detector.create_strategy(strategy_name)
            self.current_strategy_name = strategy_name
            
            # Update state with detected information
            if pagination_info.get('total_pages'):
                self.state.total_pages = pagination_info['total_pages']
            
            if pagination_info.get('current_page'):
                self.state.set_page(pagination_info['current_page'])
            
            # Set strategy in state
            self.state.strategy = strategy_name
            
            self.is_initialized = True
            logger.info(f"Pagination initialized with strategy: {strategy_name}")
            
            # Log pagination summary
            summary = self.detector.get_pagination_summary(self.driver)
            logger.info(f"Pagination Summary:\n{summary}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize pagination: {e}")
            return False
    
    def can_continue(self) -> bool:
        """Check if pagination can continue based on limits and state."""
        if not self.is_initialized:
            return False
        
        return self.state.can_continue(self.max_pages, self.max_items)
    
    def navigate_to_next(self, data_extractor: Optional[Callable] = None) -> bool:
        """
        Navigate to the next page and optionally extract data.
        
        Args:
            data_extractor: Optional function to extract data from the current page
            
        Returns:
            True if navigation was successful, False otherwise
        """
        if not self.is_initialized:
            logger.error("Pagination not initialized")
            return False
        
        if not self.can_continue():
            logger.info("Pagination limits reached")
            return False
        
        try:
            # Extract data from current page if extractor provided
            items_found = 0
            if data_extractor:
                try:
                    items_found = data_extractor(self.driver)
                    logger.info(f"Extracted {items_found} items from page {self.state.current_page}")
                except Exception as e:
                    logger.warning(f"Data extraction failed on page {self.state.current_page}: {e}")
            
            # Mark current page as successful
            self.state.mark_page_success(self.state.current_page, items_found)
            
            # Try to navigate to next page
            success = self._navigate_with_retry()
            
            if success:
                # Update state for next page
                self.state.next_page()
                logger.info(f"Successfully navigated to page {self.state.current_page}")
                return True
            else:
                # Mark navigation as failed
                self.state.mark_page_failed(self.state.current_page, "Navigation failed")
                logger.warning(f"Failed to navigate from page {self.state.current_page}")
                return False
                
        except Exception as e:
            logger.error(f"Error during pagination navigation: {e}")
            self.state.mark_page_failed(self.state.current_page, str(e))
            return False
    
    def _navigate_with_retry(self) -> bool:
        """Navigate to next page with retry logic."""
        for attempt in range(self.retry_attempts):
            try:
                logger.debug(f"Navigation attempt {attempt + 1}/{self.retry_attempts}")
                
                # Try to navigate using the current strategy
                if self.strategy:
                    success = self.strategy.navigate_to_next(self.driver)
                    if success:
                        return True
                
                # If strategy navigation failed, try alternative methods
                if self._try_alternative_navigation():
                    return True
                
                # Wait before retry
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.wait_time * (attempt + 1))  # Exponential backoff
                
            except Exception as e:
                logger.warning(f"Navigation attempt {attempt + 1} failed: {e}")
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.wait_time * (attempt + 1))
        
        return False
    
    def _try_alternative_navigation(self) -> bool:
        """Try alternative navigation methods if the primary strategy fails."""
        try:
            # Try URL-based navigation as fallback
            if self.current_strategy_name != 'url':
                url_strategy = self.detector.create_strategy('url')
                if url_strategy.can_handle(self.driver):
                    logger.debug("Trying URL-based navigation as fallback")
                    return url_strategy.navigate_to_next(self.driver)
            
            # Try JavaScript-based navigation as fallback
            if self.current_strategy_name != 'javascript':
                js_strategy = self.detector.create_strategy('javascript')
                if js_strategy.can_handle(self.driver):
                    logger.debug("Trying JavaScript-based navigation as fallback")
                    return js_strategy.navigate_to_next(self.driver)
                    
        except Exception as e:
            logger.debug(f"Alternative navigation failed: {e}")
        
        return False
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current pagination progress."""
        if not self.is_initialized:
            return {"status": "not_initialized"}
        
        progress = self.state.get_progress()
        progress.update({
            "status": "active" if self.can_continue() else "completed",
            "strategy": self.current_strategy_name,
            "initialized": self.is_initialized
        })
        
        return progress
    
    def save_state(self, file_path: Path) -> None:
        """Save current pagination state to file."""
        if self.is_initialized:
            self.state.save_state(file_path)
    
    def load_state(self, file_path: Path) -> bool:
        """Load pagination state from file."""
        try:
            self.state = PaginationState.load_state(file_path)
            logger.info(f"Loaded pagination state from {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load pagination state: {e}")
            return False
    
    def reset(self) -> None:
        """Reset pagination state and reinitialize."""
        self.state.reset()
        self.is_initialized = False
        self.strategy = None
        self.current_strategy_name = None
        logger.info("Pagination navigation reset")
    
    def get_pagination_info(self) -> Dict[str, Any]:
        """Get comprehensive pagination information."""
        if not self.is_initialized:
            return {"status": "not_initialized"}
        
        # Get current page info
        has_pagination, strategy_name, pagination_info = self.detector.detect_pagination(self.driver)
        
        info = {
            "status": "active" if self.can_continue() else "completed",
            "strategy": self.current_strategy_name,
            "detected_strategy": strategy_name,
            "pagination_info": pagination_info,
            "state": self.state.get_progress(),
            "limits": {
                "max_pages": self.max_pages,
                "max_items": self.max_items
            },
            "navigation": {
                "retry_attempts": self.retry_attempts,
                "wait_time": self.wait_time
            }
        }
        
        return info
    
    def handle_pagination_error(self, error: Exception, context: str = "") -> bool:
        """Handle pagination errors and decide on recovery strategy."""
        logger.error(f"Pagination error in {context}: {error}")
        
        # Mark current page as failed
        self.state.mark_page_failed(self.state.current_page, str(error))
        
        # Check if we should continue or stop
        if len(self.state.failed_pages) >= 3:  # Stop after 3 consecutive failures
            logger.error("Too many consecutive failures, stopping pagination")
            return False
        
        # Try to recover by waiting longer
        logger.info("Waiting before retry...")
        time.sleep(self.wait_time * 2)
        
        return True
    
    def validate_page_content(self) -> bool:
        """Validate that the current page has expected content."""
        try:
            # Basic validation - check if page has content
            body = self.driver.find_element("tag name", "body")
            if not body.text.strip():
                logger.warning("Page appears to be empty")
                return False
            
            # Check for common error indicators
            error_indicators = [
                "error",
                "not found",
                "404",
                "access denied",
                "forbidden"
            ]
            
            page_text = body.text.lower()
            for indicator in error_indicators:
                if indicator in page_text:
                    logger.warning(f"Page contains error indicator: {indicator}")
                    return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Could not validate page content: {e}")
            return True  # Assume valid if we can't check
    
    def get_navigation_summary(self) -> str:
        """Get a human-readable summary of the navigation status."""
        if not self.is_initialized:
            return "Pagination not initialized"
        
        progress = self.get_progress()
        summary = f"Pagination Navigation Summary\n"
        summary += f"Status: {progress['status']}\n"
        summary += f"Strategy: {progress['strategy']}\n"
        summary += f"Current Page: {progress['current_page']}\n"
        
        if progress.get('total_pages'):
            summary += f"Total Pages: {progress['total_pages']}\n"
        
        summary += f"Items Found: {progress['total_items']}\n"
        summary += f"Success Rate: {progress['success_rate']:.1f}%\n"
        summary += f"Elapsed Time: {progress['elapsed_time']}\n"
        
        if progress.get('estimated_completion'):
            summary += f"Estimated Completion: {progress['estimated_completion']}\n"
        
        if self.state.failed_pages:
            summary += f"Failed Pages: {', '.join(map(str, self.state.failed_pages))}\n"
        
        return summary
