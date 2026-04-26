"""
collaboration.py — User and session management for ActionForge AI collaboration.
Handles user authentication, workspace sharing, and collaborative features.
"""

import json
import uuid
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field

# ─────────────────────────────────────────────────────────────
# Data Models
# ─────────────────────────────────────────────────────────────

class User(BaseModel):
    """User account model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    username: str
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class SharedSession(BaseModel):
    """Shared workspace/session for collaboration."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    owner_id: str
    name: str
    description: str = ""
    meeting_data: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    shared_with: List[str] = Field(default_factory=list)  # List of user IDs
    public: bool = False
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class Permission(BaseModel):
    """Collaboration permission for a user on a session."""
    user_id: str
    session_id: str
    permission: str  # 'view' | 'edit' | 'admin'
    granted_at: datetime = Field(default_factory=datetime.now)
    granted_by: str = ""
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


# ─────────────────────────────────────────────────────────────
# Authentication & User Management
# ─────────────────────────────────────────────────────────────

class UserManager:
    """In-memory user management (could be replaced with DB)."""
    
    def __init__(self, storage_dir: str = "data"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.users_file = self.storage_dir / "users.json"
        self.users: Dict[str, User] = self._load_users()
    
    def _load_users(self) -> Dict[str, User]:
        """Load users from JSON file."""
        if self.users_file.exists():
            try:
                with open(self.users_file, "r") as f:
                    data = json.load(f)
                    return {uid: User(**u) for uid, u in data.items()}
            except:
                return {}
        return {}
    
    def _save_users(self):
        """Save users to JSON file."""
        data = {uid: u.model_dump() for uid, u in self.users.items()}
        with open(self.users_file, "w") as f:
            json.dump(data, f, indent=2, default=str)
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, email: str, username: str, password: str) -> User:
        """Create a new user."""
        # Check if user already exists
        if any(u.email == email or u.username == username for u in self.users.values()):
            raise ValueError("User with this email or username already exists")
        
        user = User(
            email=email,
            username=username,
            password_hash=self.hash_password(password)
        )
        self.users[user.id] = user
        self._save_users()
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.users.get(user_id)
    
    def authenticate(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        for user in self.users.values():
            if user.email == email and user.password_hash == self.hash_password(password):
                return user
        return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        for user in self.users.values():
            if user.email == email:
                return user
        return None
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        if user_id in self.users:
            del self.users[user_id]
            self._save_users()
            return True
        return False


# ─────────────────────────────────────────────────────────────
# Session & Workspace Management
# ─────────────────────────────────────────────────────────────

class SessionManager:
    """Manage shared sessions and collaboration."""
    
    def __init__(self, storage_dir: str = "data"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.sessions_file = self.storage_dir / "sessions.json"
        self.permissions_file = self.storage_dir / "permissions.json"
        self.sessions: Dict[str, SharedSession] = self._load_sessions()
        self.permissions: List[Permission] = self._load_permissions()
    
    def _load_sessions(self) -> Dict[str, SharedSession]:
        """Load sessions from JSON file."""
        if self.sessions_file.exists():
            try:
                with open(self.sessions_file, "r") as f:
                    data = json.load(f)
                    return {sid: SharedSession(**s) for sid, s in data.items()}
            except:
                return {}
        return {}
    
    def _save_sessions(self):
        """Save sessions to JSON file."""
        data = {sid: s.model_dump() for sid, s in self.sessions.items()}
        with open(self.sessions_file, "w") as f:
            json.dump(data, f, indent=2, default=str)
    
    def _load_permissions(self) -> List[Permission]:
        """Load permissions from JSON file."""
        if self.permissions_file.exists():
            try:
                with open(self.permissions_file, "r") as f:
                    data = json.load(f)
                    return [Permission(**p) for p in data]
            except:
                return []
        return []
    
    def _save_permissions(self):
        """Save permissions to JSON file."""
        data = [p.model_dump() for p in self.permissions]
        with open(self.permissions_file, "w") as f:
            json.dump(data, f, indent=2, default=str)
    
    def create_session(self, owner_id: str, name: str, description: str = "", meeting_data: Dict = None) -> SharedSession:
        """Create a new shared session."""
        session = SharedSession(
            owner_id=owner_id,
            name=name,
            description=description,
            meeting_data=meeting_data or {}
        )
        self.sessions[session.id] = session
        self._save_sessions()
        return session
    
    def get_session(self, session_id: str) -> Optional[SharedSession]:
        """Get session by ID."""
        return self.sessions.get(session_id)
    
    def update_session(self, session_id: str, **kwargs) -> Optional[SharedSession]:
        """Update session data."""
        session = self.sessions.get(session_id)
        if session:
            for key, value in kwargs.items():
                if hasattr(session, key):
                    setattr(session, key, value)
            session.updated_at = datetime.now()
            self._save_sessions()
            return session
        return None
    
    def share_session(self, session_id: str, target_user_id: str, permission: str = "view", granted_by: str = "") -> Permission:
        """Share a session with another user."""
        # Remove existing permission if any
        self.permissions = [p for p in self.permissions if not (p.session_id == session_id and p.user_id == target_user_id)]
        
        # Create new permission
        perm = Permission(
            user_id=target_user_id,
            session_id=session_id,
            permission=permission,
            granted_by=granted_by
        )
        self.permissions.append(perm)
        self._save_permissions()
        
        # Add to session's shared_with list
        session = self.sessions.get(session_id)
        if session and target_user_id not in session.shared_with:
            session.shared_with.append(target_user_id)
            self._save_sessions()
        
        return perm
    
    def get_user_sessions(self, user_id: str) -> List[SharedSession]:
        """Get all sessions accessible by a user."""
        user_sessions = []
        
        # Own sessions
        user_sessions.extend([s for s in self.sessions.values() if s.owner_id == user_id])
        
        # Shared sessions
        shared_ids = {p.session_id for p in self.permissions if p.user_id == user_id}
        user_sessions.extend([s for sid, s in self.sessions.items() if sid in shared_ids])
        
        # Public sessions
        user_sessions.extend([s for s in self.sessions.values() if s.public and s.owner_id != user_id])
        
        # Remove duplicates
        seen = set()
        unique_sessions = []
        for s in user_sessions:
            if s.id not in seen:
                seen.add(s.id)
                unique_sessions.append(s)
        
        return unique_sessions
    
    def get_permission(self, user_id: str, session_id: str) -> Optional[Permission]:
        """Get permission for a user on a session."""
        for perm in self.permissions:
            if perm.user_id == user_id and perm.session_id == session_id:
                return perm
        return None
    
    def can_access(self, user_id: str, session_id: str, required_permission: str = "view") -> bool:
        """Check if user can access session with required permission."""
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        # Owner has all permissions
        if session.owner_id == user_id:
            return True
        
        # Public sessions allow view
        if session.public and required_permission == "view":
            return True
        
        # Check explicit permission
        perm = self.get_permission(user_id, session_id)
        if perm:
            permission_hierarchy = {"view": 0, "edit": 1, "admin": 2}
            return permission_hierarchy.get(perm.permission, -1) >= permission_hierarchy.get(required_permission, 0)
        
        return False
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            # Remove all permissions for this session
            self.permissions = [p for p in self.permissions if p.session_id != session_id]
            self._save_sessions()
            self._save_permissions()
            return True
        return False


# ─────────────────────────────────────────────────────────────
# Global Instances
# ─────────────────────────────────────────────────────────────

user_manager = UserManager()
session_manager = SessionManager()
