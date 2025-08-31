"""
Session management for v0rtex scraper.
"""

from typing import Dict, Optional, Any, Union
from pydantic import BaseModel, Field
import json
import pickle
import os
from datetime import datetime, timedelta
from loguru import logger
from typing import List


class SessionData(BaseModel):
    """Session data model."""
    cookies: Dict[str, str] = {}
    headers: Dict[str, str] = {}
    user_agent: Optional[str] = None
    last_used: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = {}


class ScrapingSession:
    """Manages scraping sessions with persistence and rotation."""
    
    def __init__(self, session_dir: str = "sessions"):
        self.session_dir = session_dir
        self.current_session: Optional[SessionData] = None
        self.session_history: List[SessionData] = []
        
        # Ensure session directory exists
        os.makedirs(session_dir, exist_ok=True)
        
        # Load existing sessions
        self._load_sessions()
    
    def create_session(self, 
                      cookies: Optional[Dict[str, str]] = None,
                      headers: Optional[Dict[str, str]] = None,
                      user_agent: Optional[str] = None,
                      expires_in: Optional[int] = None) -> SessionData:
        """Create a new session."""
        session = SessionData(
            cookies=cookies or {},
            headers=headers or {},
            user_agent=user_agent,
            expires_at=datetime.now() + timedelta(seconds=expires_in) if expires_in else None
        )
        
        self.current_session = session
        self.session_history.append(session)
        
        # Save session
        self._save_session(session)
        logger.info(f"Created new session: {session.created_at}")
        
        return session
    
    def load_session(self, session_id: str) -> Optional[SessionData]:
        """Load a specific session by ID."""
        session_file = os.path.join(self.session_dir, f"{session_id}.json")
        
        if os.path.exists(session_file):
            try:
                with open(session_file, 'r') as f:
                    data = json.load(f)
                    session = SessionData(**data)
                    self.current_session = session
                    logger.info(f"Loaded session: {session_id}")
                    return session
            except Exception as e:
                logger.error(f"Failed to load session {session_id}: {e}")
        
        return None
    
    def save_current_session(self) -> None:
        """Save the current session."""
        if self.current_session:
            self._save_session(self.current_session)
    
    def update_cookies(self, cookies: Dict[str, str]) -> None:
        """Update cookies in current session."""
        if self.current_session:
            self.current_session.cookies.update(cookies)
            self.current_session.last_used = datetime.now()
            self.save_current_session()
    
    def update_headers(self, headers: Dict[str, str]) -> None:
        """Update headers in current session."""
        if self.current_session:
            self.current_session.headers.update(headers)
            self.current_session.last_used = datetime.now()
            self.save_current_session()
    
    def get_session_cookies(self) -> Dict[str, str]:
        """Get cookies from current session."""
        return self.current_session.cookies if self.current_session else {}
    
    def get_session_headers(self) -> Dict[str, str]:
        """Get headers from current session."""
        return self.current_session.headers if self.current_session else {}
    
    def get_user_agent(self) -> Optional[str]:
        """Get user agent from current session."""
        return self.current_session.user_agent if self.current_session else None
    
    def rotate_session(self) -> SessionData:
        """Create a new session and rotate the current one."""
        if self.current_session:
            # Archive current session
            self._archive_session(self.current_session)
        
        # Create new session
        return self.create_session()
    
    def clear_expired_sessions(self) -> int:
        """Clear expired sessions and return count of cleared sessions."""
        cleared = 0
        current_time = datetime.now()
        
        for session in self.session_history[:]:
            if session.expires_at and session.expires_at < current_time:
                self._remove_session(session)
                self.session_history.remove(session)
                cleared += 1
        
        logger.info(f"Cleared {cleared} expired sessions")
        return cleared
    
    def export_session(self, session_id: str, format: str = "json") -> str:
        """Export session data in specified format."""
        session = self._find_session_by_id(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        if format == "json":
            return session.model_dump_json(indent=2)
        elif format == "pickle":
            return pickle.dumps(session)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def import_session(self, session_data: Union[str, bytes], format: str = "json") -> SessionData:
        """Import session data from specified format."""
        if format == "json":
            data = json.loads(session_data)
            session = SessionData(**data)
        elif format == "pickle":
            session = pickle.loads(session_data)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        self.session_history.append(session)
        self._save_session(session)
        return session
    
    def _save_session(self, session: SessionData) -> None:
        """Save session to file."""
        session_id = session.created_at.strftime("%Y%m%d_%H%M%S")
        session_file = os.path.join(self.session_dir, f"{session_id}.json")
        
        try:
            with open(session_file, 'w') as f:
                f.write(session.model_dump_json(indent=2))
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
    
    def _load_sessions(self) -> None:
        """Load existing sessions from directory."""
        for filename in os.listdir(self.session_dir):
            if filename.endswith('.json'):
                try:
                    session_file = os.path.join(self.session_dir, filename)
                    with open(session_file, 'r') as f:
                        data = json.load(f)
                        session = SessionData(**data)
                        self.session_history.append(session)
                except Exception as e:
                    logger.error(f"Failed to load session from {filename}: {e}")
    
    def _archive_session(self, session: SessionData) -> None:
        """Archive a session."""
        archive_dir = os.path.join(self.session_dir, "archived")
        os.makedirs(archive_dir, exist_ok=True)
        
        session_id = session.created_at.strftime("%Y%m%d_%H%M%S")
        archive_file = os.path.join(archive_dir, f"{session_id}.json")
        
        try:
            with open(archive_file, 'w') as f:
                f.write(session.model_dump_json(indent=2))
        except Exception as e:
            logger.error(f"Failed to archive session: {e}")
    
    def _remove_session(self, session: SessionData) -> None:
        """Remove a session file."""
        session_id = session.created_at.strftime("%Y%m%d_%H%M%S")
        session_file = os.path.join(self.session_dir, f"{session_id}.json")
        
        try:
            if os.path.exists(session_file):
                os.remove(session_file)
        except Exception as e:
            logger.error(f"Failed to remove session file: {e}")
    
    def _find_session_by_id(self, session_id: str) -> Optional[SessionData]:
        """Find session by ID."""
        for session in self.session_history:
            if session.created_at.strftime("%Y%m%d_%H%M%S") == session_id:
                return session
        return None
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        total_sessions = len(self.session_history)
        active_sessions = len([s for s in self.session_history if not s.expires_at or s.expires_at > datetime.now()])
        expired_sessions = total_sessions - active_sessions
        
        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "expired_sessions": expired_sessions,
            "current_session": self.current_session.created_at.isoformat() if self.current_session else None,
            "session_directory": self.session_dir
        }
