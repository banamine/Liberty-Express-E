"""
Database layer for ScheduleFlow - SQLite backend for user management and persistence

Addresses audit gap: "Data Persistence: F (JSON files)"
"""

import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class User:
    """User data model"""
    id: str
    username: str
    email: str
    hashed_password: str
    role: str  # 'admin', 'editor', 'viewer'
    is_active: bool = True
    created_at: str = None
    updated_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow().isoformat()


class DatabaseManager:
    """SQLite database manager for ScheduleFlow"""
    
    def __init__(self, db_path: str = "scheduleflow.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'viewer',
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                token TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)
        
        # Schedules table (replaces JSON)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schedules (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                data TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)
        
        # Audit logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                action TEXT NOT NULL,
                resource TEXT,
                details TEXT,
                ip_address TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    # User operations
    def create_user(self, user_id: str, username: str, email: str, hashed_password: str, role: str = "viewer") -> bool:
        """Create new user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (id, username, email, hashed_password, role) VALUES (?, ?, ?, ?, ?)",
                (user_id, username, email, hashed_password, role)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def list_users(self) -> List[Dict[str, Any]]:
        """List all users"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, role, is_active, created_at FROM users")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def delete_user(self, user_id: str) -> bool:
        """Delete user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            conn.close()
            return cursor.rowcount > 0
        except Exception:
            return False
    
    def update_user_role(self, user_id: str, role: str) -> bool:
        """Update user role"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET role = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (role, user_id)
            )
            conn.commit()
            conn.close()
            return cursor.rowcount > 0
        except Exception:
            return False
    
    # Session operations
    def create_session(self, session_id: str, user_id: str, token: str, expires_at: str) -> bool:
        """Create session"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO sessions (id, user_id, token, expires_at) VALUES (?, ?, ?, ?)",
                (session_id, user_id, token, expires_at)
            )
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            conn.commit()
            conn.close()
            return cursor.rowcount > 0
        except Exception:
            return False
    
    # Audit logging
    def log_action(self, log_id: str, user_id: Optional[str], action: str, resource: str, details: Optional[str] = None, ip_address: Optional[str] = None) -> bool:
        """Log an action for audit trail"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO audit_logs (id, user_id, action, resource, details, ip_address) VALUES (?, ?, ?, ?, ?, ?)",
                (log_id, user_id, action, resource, details, ip_address)
            )
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def get_audit_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent audit logs"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
