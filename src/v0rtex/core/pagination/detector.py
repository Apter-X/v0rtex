"""
Pagination detection for v0rtex web scraper.

This module automatically detects pagination elements on web pages
and determines the most appropriate pagination strategy to use.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urlparse, parse_qs

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from .strategy import (
    PaginationStrategy, 
    URLPaginationStrategy, 
    JavaScriptPaginationStrategy, 
    InfiniteScrollStrategy,
    AutoPaginationStrategy
)

logger = logging.getLogger(__name__)


class PaginationDetector:
    """Automatically detects pagination elements and strategies."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.pagination_config = config.get('pagination', {})
        self.selectors = self.pagination_config.get('selectors', {})
        
        # Common pagination selectors
        self.common_selectors = {
            'pagination_container': [
                '.pagination',
                '.pager',
                '.page-navigation',
                '.pagination-wrapper',
                '[class*="pagination"]',
                '[class*="pager"]',
                '[class*="page"]'
            ],
            'next_button': [
                '.pagination .next',
                '.pagination .next-page',
                '.pager .next',
                '.next',
                '.next-page',
                '[aria-label*="next"]',
                '[title*="next"]'
            ],
            'prev_button': [
                '.pagination .prev',
                '.pagination .prev-page',
                '.pager .prev',
                '.prev',
                '.prev-page',
                '[aria-label*="previous"]',
                '[title*="previous"]'
            ],
            'page_numbers': [
                '.pagination .page',
                '.pagination a',
                '.pager .page',
                '.pager a',
                '.page-number',
                '[data-page]'
            ],
            'current_page': [
                '.pagination .current',
                '.pagination .active',
                '.pager .current',
                '.pager .active',
                '.current-page',
                '.active-page'
            ]
        }
    
    def detect_pagination(self, driver: WebDriver) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Detect if the current page has pagination and return details.
        
        Returns:
            Tuple of (has_pagination, strategy_name, pagination_info)
        """
        try:
            # Check for explicit pagination configuration
            if self.pagination_config.get('enabled', False):
                strategy = self.pagination_config.get('strategy', 'auto')
                logger.info(f"Using configured pagination strategy: {strategy}")
                return True, strategy, self._get_pagination_info(driver)
            
            # Auto-detect pagination
            pagination_info = self._get_pagination_info(driver)
            
            if pagination_info['has_pagination']:
                strategy = self._determine_best_strategy(driver, pagination_info)
                logger.info(f"Auto-detected pagination strategy: {strategy}")
                return True, strategy, pagination_info
            
            logger.info("No pagination detected on current page")
            return False, None, pagination_info
            
        except Exception as e:
            logger.error(f"Error detecting pagination: {e}")
            return False, None, {}
    
    def _get_pagination_info(self, driver: WebDriver) -> Dict[str, Any]:
        """Extract detailed pagination information from the current page."""
        info = {
            'has_pagination': False,
            'strategy': None,
            'elements': {},
            'url_patterns': [],
            'total_pages': None,
            'current_page': 1,
            'confidence': 0.0
        }
        
        try:
            # Check for pagination containers
            pagination_containers = self._find_elements(driver, self.common_selectors['pagination_container'])
            if pagination_containers:
                info['has_pagination'] = True
                info['elements']['container'] = len(pagination_containers)
                info['confidence'] += 0.3
            
            # Check for navigation buttons
            next_buttons = self._find_elements(driver, self.common_selectors['next_button'])
            prev_buttons = self._find_elements(driver, self.common_selectors['prev_button'])
            
            if next_buttons:
                info['elements']['next_button'] = len(next_buttons)
                info['confidence'] += 0.2
            
            if prev_buttons:
                info['elements']['prev_button'] = len(prev_buttons)
                info['confidence'] += 0.1
            
            # Check for page numbers
            page_numbers = self._find_elements(driver, self.common_selectors['page_numbers'])
            if page_numbers:
                info['elements']['page_numbers'] = len(page_numbers)
                info['confidence'] += 0.2
            
            # Check for current page indicator
            current_page_elements = self._find_elements(driver, self.common_selectors['current_page'])
            if current_page_elements:
                info['elements']['current_page'] = len(current_page_elements)
                info['confidence'] += 0.1
            
            # Check URL patterns
            url_patterns = self._detect_url_patterns(driver.current_url)
            if url_patterns:
                info['url_patterns'] = url_patterns
                info['confidence'] += 0.2
            
            # Try to determine total pages
            total_pages = self._extract_total_pages(driver)
            if total_pages:
                info['total_pages'] = total_pages
                info['confidence'] += 0.1
            
            # Try to determine current page
            current_page = self._extract_current_page(driver)
            if current_page:
                info['current_page'] = current_page
            
            # Check for infinite scroll indicators
            if self._has_infinite_scroll(driver):
                info['has_pagination'] = True
                info['strategy'] = 'infinite_scroll'
                info['confidence'] += 0.3
            
            # Normalize confidence to 0-1 range
            info['confidence'] = min(1.0, info['confidence'])
            
        except Exception as e:
            logger.error(f"Error getting pagination info: {e}")
        
        return info
    
    def _find_elements(self, driver: WebDriver, selectors: List[str]) -> List:
        """Find elements using multiple selectors."""
        elements = []
        for selector in selectors:
            try:
                found = driver.find_elements(By.CSS_SELECTOR, selector)
                if found:
                    elements.extend(found)
            except Exception:
                continue
        return elements
    
    def _detect_url_patterns(self, url: str) -> List[str]:
        """Detect pagination patterns in the URL."""
        patterns = []
        
        # Common pagination parameters
        pagination_params = ['page', 'p', 'pg', 'pageno', 'pagenumber']
        
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        
        for param in pagination_params:
            if param in query_params:
                patterns.append(f"{param}=<number>")
        
        # Check for path-based pagination
        path_patterns = [
            r'/page/(\d+)',
            r'/p/(\d+)',
            r'/pg/(\d+)'
        ]
        
        for pattern in path_patterns:
            if re.search(pattern, url):
                patterns.append(pattern.replace(r'(\d+)', '<number>'))
        
        return patterns
    
    def _extract_total_pages(self, driver: WebDriver) -> Optional[int]:
        """Try to extract total pages from various sources."""
        try:
            # Look for explicit total page indicators
            total_selectors = [
                '[data-total-pages]',
                '[data-last-page]',
                '.pagination .total',
                '.pagination .last',
                '.pagination .count'
            ]
            
            for selector in total_selectors:
                try:
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                    if element:
                        # Check data attributes first
                        total_pages = element.get_attribute('data-total-pages') or element.get_attribute('data-last-page')
                        if total_pages and total_pages.isdigit():
                            return int(total_pages)
                        
                        # Check text content
                        text = element.text.strip()
                        numbers = re.findall(r'\d+', text)
                        if numbers:
                            return int(numbers[-1])
                            
                except NoSuchElementException:
                    continue
            
            # Look for pagination links and find the highest number
            page_elements = self._find_elements(driver, self.common_selectors['page_numbers'])
            page_numbers = []
            
            for element in page_elements:
                try:
                    text = element.text.strip()
                    if text.isdigit():
                        page_numbers.append(int(text))
                except (ValueError, AttributeError):
                    continue
            
            if page_numbers:
                return max(page_numbers)
                
        except Exception as e:
            logger.debug(f"Error extracting total pages: {e}")
        
        return None
    
    def _extract_current_page(self, driver: WebDriver) -> Optional[int]:
        """Try to extract current page number."""
        try:
            # Look for current page indicators
            current_elements = self._find_elements(driver, self.common_selectors['current_page'])
            
            for element in current_elements:
                try:
                    text = element.text.strip()
                    if text.isdigit():
                        return int(text)
                except (ValueError, AttributeError):
                    continue
            
            # Check URL for page number
            url = driver.current_url
            page_match = re.search(r'[?&]page=(\d+)', url)
            if page_match:
                return int(page_match.group(1))
            
            # Default to page 1 if no indicators found
            return 1
                
        except Exception as e:
            logger.debug(f"Error extracting current page: {e}")
        
        return None
    
    def _has_infinite_scroll(self, driver: WebDriver) -> bool:
        """Check if the page has infinite scroll pagination."""
        try:
            # Look for infinite scroll indicators
            infinite_selectors = [
                '[data-infinite-scroll]',
                '[class*="infinite"]',
                '[class*="scroll"]',
                '.load-more',
                '.infinite-scroll',
                '.lazy-load'
            ]
            
            for selector in infinite_selectors:
                if driver.find_elements(By.CSS_SELECTOR, selector):
                    return True
            
            # Check for load more buttons
            load_more_selectors = [
                '.load-more',
                '.load-more-btn',
                '.show-more',
                '.infinite-scroll-trigger'
            ]
            
            for selector in load_more_selectors:
                if driver.find_elements(By.CSS_SELECTOR, selector):
                    return True
                    
        except Exception as e:
            logger.debug(f"Error checking infinite scroll: {e}")
        
        return False
    
    def _determine_best_strategy(self, driver: WebDriver, pagination_info: Dict[str, Any]) -> str:
        """Determine the best pagination strategy based on detected elements."""
        confidence = pagination_info.get('confidence', 0.0)
        
        # If confidence is too low, default to auto
        if confidence < 0.3:
            return 'auto'
        
        # Check for infinite scroll
        if pagination_info.get('strategy') == 'infinite_scroll':
            return 'infinite_scroll'
        
        # Check for URL patterns
        if pagination_info.get('url_patterns'):
            return 'url'
        
        # Check for JavaScript elements
        if (pagination_info.get('elements', {}).get('next_button') or 
            pagination_info.get('elements', {}).get('page_numbers')):
            return 'javascript'
        
        # Default to auto for best compatibility
        return 'auto'
    
    def create_strategy(self, strategy_name: str) -> PaginationStrategy:
        """Create a pagination strategy instance."""
        strategy_map = {
            'url': URLPaginationStrategy,
            'javascript': JavaScriptPaginationStrategy,
            'infinite_scroll': InfiniteScrollStrategy,
            'auto': AutoPaginationStrategy
        }
        
        strategy_class = strategy_map.get(strategy_name, AutoPaginationStrategy)
        return strategy_class(self.pagination_config)
    
    def get_pagination_summary(self, driver: WebDriver) -> str:
        """Get a human-readable summary of pagination detection."""
        has_pagination, strategy, info = self.detect_pagination(driver)
        
        if not has_pagination:
            return "No pagination detected"
        
        summary = f"Pagination detected (Strategy: {strategy}, Confidence: {info.get('confidence', 0):.1%})\n"
        
        if info.get('total_pages'):
            summary += f"Total pages: {info['total_pages']}\n"
        
        if info.get('current_page'):
            summary += f"Current page: {info['current_page']}\n"
        
        if info.get('url_patterns'):
            summary += f"URL patterns: {', '.join(info['url_patterns'])}\n"
        
        elements = info.get('elements', {})
        if elements:
            summary += "Elements found:\n"
            for element_type, count in elements.items():
                summary += f"  - {element_type}: {count}\n"
        
        return summary.strip()
