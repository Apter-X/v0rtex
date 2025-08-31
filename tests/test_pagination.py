"""
Tests for the pagination system.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
import json
import tempfile

from v0rtex.core.pagination.state import PaginationState
from v0rtex.core.pagination.strategy import (
    PaginationStrategy, 
    URLPaginationStrategy, 
    JavaScriptPaginationStrategy, 
    InfiniteScrollStrategy,
    AutoPaginationStrategy
)
from v0rtex.core.pagination.detector import PaginationDetector
from v0rtex.core.pagination.navigator import PaginationNavigator


class TestPaginationState(unittest.TestCase):
    """Test PaginationState class."""
    
    def setUp(self):
        self.state = PaginationState()
    
    def test_initial_state(self):
        """Test initial state values."""
        self.assertEqual(self.state.current_page, 1)
        self.assertEqual(self.state.total_items, 0)
        self.assertIsNone(self.state.total_pages)
        self.assertEqual(len(self.state.failed_pages), 0)
    
    def test_next_page(self):
        """Test moving to next page."""
        initial_page = self.state.current_page
        next_page = self.state.next_page()
        
        self.assertEqual(next_page, initial_page + 1)
        self.assertEqual(self.state.current_page, initial_page + 1)
    
    def test_set_page(self):
        """Test setting specific page."""
        self.state.set_page(5)
        self.assertEqual(self.state.current_page, 5)
    
    def test_set_page_invalid(self):
        """Test setting invalid page number."""
        with self.assertRaises(ValueError):
            self.state.set_page(0)
    
    def test_mark_page_success(self):
        """Test marking page as successful."""
        self.state.mark_page_success(1, 10)
        self.assertEqual(self.state.total_items, 10)
        self.assertEqual(self.state.last_successful_page, 1)
        self.assertNotIn(1, self.state.failed_pages)
    
    def test_mark_page_failed(self):
        """Test marking page as failed."""
        self.state.mark_page_failed(2, "Test error")
        self.assertIn(2, self.state.failed_pages)
    
    def test_can_continue_page_limit(self):
        """Test page limit checking."""
        self.state.current_page = 100
        self.assertFalse(self.state.can_continue(max_pages=100))
    
    def test_can_continue_item_limit(self):
        """Test item limit checking."""
        self.state.total_items = 1000
        self.assertFalse(self.state.can_continue(max_items=1000))
    
    def test_get_progress(self):
        """Test progress calculation."""
        self.state.total_items = 50
        self.state.items_per_page = 10
        self.state.current_page = 5
        
        progress = self.state.get_progress()
        
        self.assertEqual(progress['current_page'], 5)
        self.assertEqual(progress['total_items'], 50)
        self.assertEqual(progress['items_per_page'], 10)
        self.assertIn('success_rate', progress)
        self.assertIn('elapsed_time', progress)
    
    def test_save_and_load_state(self):
        """Test state persistence."""
        self.state.total_items = 100
        self.state.current_page = 5
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = Path(f.name)
        
        try:
            # Save state
            self.state.save_state(temp_file)
            
            # Load state
            loaded_state = PaginationState.load_state(temp_file)
            
            self.assertEqual(loaded_state.total_items, 100)
            self.assertEqual(loaded_state.current_page, 5)
            
        finally:
            temp_file.unlink()
    
    def test_reset(self):
        """Test state reset."""
        self.state.total_items = 100
        self.state.current_page = 5
        self.state.failed_pages = [2, 3]
        
        self.state.reset()
        
        self.assertEqual(self.state.current_page, 1)
        self.assertEqual(self.state.total_items, 0)
        self.assertEqual(len(self.state.failed_pages), 0)


class TestPaginationStrategies(unittest.TestCase):
    """Test pagination strategy classes."""
    
    def setUp(self):
        self.config = {
            'selectors': {
                'next_button': '.next',
                'prev_button': '.prev',
                'page_numbers': '.page',
                'current_page': '.current'
            },
            'navigation': {
                'wait_time': 2,
                'retry_attempts': 3
            }
        }
        self.mock_driver = Mock()
    
    def test_url_strategy_initialization(self):
        """Test URL strategy initialization."""
        strategy = URLPaginationStrategy(self.config)
        self.assertEqual(strategy.page_param, 'page')
        self.assertIsInstance(strategy.url_patterns, list)
    
    def test_javascript_strategy_initialization(self):
        """Test JavaScript strategy initialization."""
        strategy = JavaScriptPaginationStrategy(self.config)
        self.assertEqual(strategy.next_button_selector, '.next')
        self.assertEqual(strategy.prev_button_selector, '.prev')
    
    def test_infinite_scroll_strategy_initialization(self):
        """Test infinite scroll strategy initialization."""
        strategy = InfiniteScrollStrategy(self.config)
        self.assertEqual(strategy.scroll_pause, 1)
        self.assertEqual(strategy.max_scrolls, 50)
    
    def test_auto_strategy_initialization(self):
        """Test auto strategy initialization."""
        strategy = AutoPaginationStrategy(self.config)
        self.assertEqual(len(strategy.strategies), 3)
        self.assertIsNone(strategy.current_strategy)


class TestPaginationDetector(unittest.TestCase):
    """Test PaginationDetector class."""
    
    def setUp(self):
        self.config = {
            'pagination': {
                'enabled': False,
                'strategy': 'auto',
                'selectors': {}
            }
        }
        self.detector = PaginationDetector(self.config)
        self.mock_driver = Mock()
    
    def test_detector_initialization(self):
        """Test detector initialization."""
        self.assertIsInstance(self.detector.common_selectors, dict)
        self.assertIn('pagination_container', self.detector.common_selectors)
        self.assertIn('next_button', self.detector.common_selectors)
    
    def test_create_strategy(self):
        """Test strategy creation."""
        url_strategy = self.detector.create_strategy('url')
        self.assertIsInstance(url_strategy, URLPaginationStrategy)
        
        js_strategy = self.detector.create_strategy('javascript')
        self.assertIsInstance(js_strategy, JavaScriptPaginationStrategy)
        
        auto_strategy = self.detector.create_strategy('auto')
        self.assertIsInstance(auto_strategy, AutoPaginationStrategy)


class TestPaginationNavigator(unittest.TestCase):
    """Test PaginationNavigator class."""
    
    def setUp(self):
        self.config = {
            'pagination': {
                'enabled': True,
                'strategy': 'auto',
                'selectors': {},
                'limits': {
                    'max_pages': 100,
                    'max_items': 1000
                },
                'navigation': {
                    'retry_attempts': 3,
                    'wait_time': 2
                }
            }
        }
        self.mock_driver = Mock()
        self.navigator = PaginationNavigator(self.config, self.mock_driver)
    
    def test_navigator_initialization(self):
        """Test navigator initialization."""
        self.assertFalse(self.navigator.is_initialized)
        self.assertIsNone(self.navigator.strategy)
        self.assertEqual(self.navigator.max_pages, 100)
        self.assertEqual(self.navigator.max_items, 1000)
    
    def test_can_continue_not_initialized(self):
        """Test can_continue when not initialized."""
        self.assertFalse(self.navigator.can_continue())
    
    def test_get_progress_not_initialized(self):
        """Test get_progress when not initialized."""
        progress = self.navigator.get_progress()
        self.assertEqual(progress['status'], 'not_initialized')
    
    def test_get_pagination_info_not_initialized(self):
        """Test get_pagination_info when not initialized."""
        info = self.navigator.get_pagination_info()
        self.assertEqual(info['status'], 'not_initialized')
    
    def test_get_navigation_summary_not_initialized(self):
        """Test get_navigation_summary when not initialized."""
        summary = self.navigator.get_navigation_summary()
        self.assertEqual(summary, "Pagination not initialized")


if __name__ == '__main__':
    unittest.main()
