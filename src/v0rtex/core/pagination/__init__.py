"""
Pagination module for v0rtex web scraper.

This module provides comprehensive pagination handling for web scraping,
supporting multiple pagination strategies and automatic detection.
"""

from .detector import PaginationDetector
from .navigator import PaginationNavigator
from .state import PaginationState
from .strategy import PaginationStrategy, URLPaginationStrategy, JavaScriptPaginationStrategy, InfiniteScrollStrategy

__all__ = [
    'PaginationDetector',
    'PaginationNavigator', 
    'PaginationState',
    'PaginationStrategy',
    'URLPaginationStrategy',
    'JavaScriptPaginationStrategy',
    'InfiniteScrollStrategy'
]
