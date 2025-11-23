"""
User management module - handles user CRUD and authentication state

Addresses audit gap: "Security: F (No auth)"
"""

import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from core.database import DatabaseManager, User
from core.auth import AuthManager


class UserManager:
    """Manages user operations and authentication"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.auth = AuthManager()
    
    def register_user(self, username: str, email: str, password: str, role: str = "viewer") -> tuple[bool, str]:
        """Register a new user
        
        Returns: (success, message)
        """
        # Validate input
        if not username or len(username) < 3:
            return False, "Username must be at least 3 characters"
        if not email or "@" not in email:
            return False, "Invalid email format"
        if not password or len(password) < 8:
            return False, "Password must be at least 8 characters"
        
        # Check if user exists
        if self.db.get_user_by_username(username):
            return False, "Username already exists"
        
        # Hash password
        hashed = self.auth.hash_password(password)
        user_id = str(uuid.uuid4())
        
        # Create user
        if self.db.create_user(user_id, username, email, hashed, role):
            return True, f"User {username} created successfully"
        else:
            return False, "Failed to create user"
    
    def authenticate_user(self, username: str, password: str) -> tuple[bool, Optional[str], str]:
        """Authenticate user and create session
        
        Returns: (success, user_id, message)
        """
        user = self.db.get_user_by_username(username)
        
        if not user:
            return False, None, "Invalid username or password"
        
        if not self.auth.verify_password(password, user["hashed_password"]):
            return False, None, "Invalid username or password"
        
        if not user["is_active"]:
            return False, None, "User account is inactive"
        
        return True, user["id"], "Authentication successful"
    
    def create_access_token(self, user_id: str) -> str:
        """Create JWT access token for user"""
        return self.auth.create_access_token({"sub": user_id, "user_id": user_id})
    
    def verify_token(self, token: str) -> tuple[bool, Optional[str]]:
        """Verify JWT token
        
        Returns: (valid, user_id)
        """
        payload = self.auth.verify_token(token)
        if payload:
            return True, payload.get("user_id")
        return False, None
    
    def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user information"""
        user = self.db.get_user(user_id)
        if user:
            # Remove sensitive data
            user.pop("hashed_password", None)
            return user
        return None
    
    def list_users(self) -> List[Dict[str, Any]]:
        """List all users (admin only)"""
        return self.db.list_users()
    
    def delete_user(self, user_id: str) -> tuple[bool, str]:
        """Delete user"""
        if self.db.delete_user(user_id):
            return True, "User deleted successfully"
        return False, "Failed to delete user"
    
    def update_user_role(self, user_id: str, role: str) -> tuple[bool, str]:
        """Update user role (admin only)"""
        valid_roles = ["viewer", "editor", "admin"]
        if role not in valid_roles:
            return False, f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        
        if self.db.update_user_role(user_id, role):
            return True, f"User role updated to {role}"
        return False, "Failed to update user role"
