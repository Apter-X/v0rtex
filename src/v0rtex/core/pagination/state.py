"""
Pagination state management for v0rtex web scraper.

This module handles tracking pagination progress, current page position,
and state persistence for resuming interrupted scraping sessions.
"""

import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


@dataclass
class PaginationState:
    """Manages pagination state and progress tracking."""
    
    current_page: int = 1
    total_pages: Optional[int] = None
    total_items: int = 0
    items_per_page: int = 0
    strategy: str = "auto"
    last_successful_page: int = 1
    failed_pages: List[int] = None
    start_time: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    session_id: Optional[str] = None
    
    def __post_init__(self):
        if self.failed_pages is None:
            self.failed_pages = []
        if self.start_time is None:
            self.start_time = datetime.now()
        self.last_activity = datetime.now()
    
    def next_page(self) -> int:
        """Move to the next page and update state."""
        self.current_page += 1
        self.last_activity = datetime.now()
        logger.info(f"Moving to page {self.current_page}")
        return self.current_page
    
    def set_page(self, page: int) -> None:
        """Set current page to specific number."""
        if page < 1:
            raise ValueError("Page number must be >= 1")
        self.current_page = page
        self.last_activity = datetime.now()
        logger.info(f"Set current page to {self.current_page}")
    
    def mark_page_success(self, page: int, items_found: int) -> None:
        """Mark a page as successfully scraped."""
        self.last_successful_page = page
        self.total_items += items_found
        self.last_activity = datetime.now()
        
        # Remove from failed pages if it was there
        if page in self.failed_pages:
            self.failed_pages.remove(page)
        
        logger.info(f"Page {page} marked as successful, {items_found} items found")
    
    def mark_page_failed(self, page: int, error: str = None) -> None:
        """Mark a page as failed."""
        if page not in self.failed_pages:
            self.failed_pages.append(page)
        self.last_activity = datetime.now()
        logger.warning(f"Page {page} marked as failed: {error}")
    
    def can_continue(self, max_pages: Optional[int] = None, max_items: Optional[int] = None) -> bool:
        """Check if pagination can continue based on limits."""
        # Check page limit
        if max_pages and self.current_page >= max_pages:
            logger.info(f"Reached maximum page limit: {max_pages}")
            return False
        
        # Check item limit
        if max_items and self.total_items >= max_items:
            logger.info(f"Reached maximum item limit: {max_items}")
            return False
        
        # Check if we've reached the last known page
        if self.total_pages and self.current_page > self.total_pages:
            logger.info(f"Reached last known page: {self.total_pages}")
            return False
        
        return True
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current pagination progress."""
        progress = {
            "current_page": self.current_page,
            "total_pages": self.total_pages,
            "total_items": self.total_items,
            "items_per_page": self.items_per_page,
            "success_rate": self._calculate_success_rate(),
            "elapsed_time": self._get_elapsed_time(),
            "estimated_completion": self._estimate_completion()
        }
        return progress
    
    def _calculate_success_rate(self) -> float:
        """Calculate success rate based on failed pages."""
        if self.current_page <= 1:
            return 100.0
        
        total_attempted = self.current_page - 1
        failed_count = len([p for p in self.failed_pages if p <= self.current_page])
        success_count = total_attempted - failed_count
        
        return (success_count / total_attempted) * 100 if total_attempted > 0 else 100.0
    
    def _get_elapsed_time(self) -> str:
        """Get elapsed time since pagination started."""
        if not self.start_time:
            return "Unknown"
        
        elapsed = datetime.now() - self.start_time
        hours, remainder = divmod(elapsed.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def _estimate_completion(self) -> Optional[str]:
        """Estimate time to completion based on current progress."""
        if self.current_page <= 1 or not self.start_time:
            return None
        
        elapsed = datetime.now() - self.start_time
        pages_per_second = (self.current_page - 1) / elapsed.total_seconds()
        
        if pages_per_second <= 0:
            return None
        
        if self.total_pages:
            remaining_pages = self.total_pages - self.current_page
            estimated_seconds = remaining_pages / pages_per_second
        else:
            # Estimate based on items found so far
            if self.items_per_page > 0:
                estimated_seconds = (1000 - self.total_items) / (self.items_per_page * pages_per_second)
            else:
                return None
        
        if estimated_seconds > 0:
            hours, remainder = divmod(int(estimated_seconds), 3600)
            minutes, seconds = divmod(remainder, 60)
            
            if hours > 0:
                return f"{hours}h {minutes}m"
            elif minutes > 0:
                return f"{minutes}m {seconds}s"
            else:
                return f"{seconds}s"
        
        return None
    
    def save_state(self, file_path: Path) -> None:
        """Save pagination state to file for persistence."""
        try:
            state_data = asdict(self)
            # Convert datetime objects to ISO format for JSON serialization
            for key, value in state_data.items():
                if isinstance(value, datetime):
                    state_data[key] = value.isoformat()
            
            with open(file_path, 'w') as f:
                json.dump(state_data, f, indent=2)
            
            logger.info(f"Pagination state saved to {file_path}")
        except Exception as e:
            logger.error(f"Failed to save pagination state: {e}")
    
    @classmethod
    def load_state(cls, file_path: Path) -> 'PaginationState':
        """Load pagination state from file."""
        try:
            with open(file_path, 'r') as f:
                state_data = json.load(f)
            
            # Convert ISO format strings back to datetime objects
            for key, value in state_data.items():
                if key in ['start_time', 'last_activity'] and isinstance(value, str):
                    state_data[key] = datetime.fromisoformat(value)
            
            return cls(**state_data)
        except Exception as e:
            logger.error(f"Failed to load pagination state: {e}")
            return cls()
    
    def reset(self) -> None:
        """Reset pagination state to initial values."""
        self.current_page = 1
        self.total_pages = None
        self.total_items = 0
        self.items_per_page = 0
        self.last_successful_page = 1
        self.failed_pages = []
        self.start_time = datetime.now()
        self.last_activity = datetime.now()
        logger.info("Pagination state reset")
