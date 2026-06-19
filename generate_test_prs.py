#!/usr/bin/env python3
"""
Generate 20 Test PRs for Multi-Agent Thesis Evaluation

Creates diverse PRs across 5 categories:
- Security Fixes (4 PRs)
- Performance Improvements (4 PRs)  
- Architecture Refactoring (4 PRs)
- Bug Fixes / Regressions (4 PRs)
- Clean Code / Positive Tests (4 PRs)
"""

import os
import subprocess
import sys
from pathlib import Path

# Demo project path
DEMO_PROJECT = Path(r"C:\Users\andre\Desktop\Uni\Msc2\demo-pr-review")

# PR definitions: (branch_name, commit_message, file_changes)
TEST_PRS = [
    # ========== SECURITY FIXES (4 PRs) ==========
    {
        "branch": "security/fix-sql-injection-search",
        "title": "Security: Fix SQL injection in search_users",
        "description": "Replace string interpolation with parameterized query in user search to prevent SQL injection attacks.",
        "files": {
            "src/api/users.py": {
                "search": '''    def search_users(self, query: str) -> List[dict]:
        """
        Search users by username
        
        SECURITY ISSUE: SQL Injection in search
        """
        cursor = self.connection.cursor()
        # SECURITY ISSUE: SQL Injection in LIKE clause
        sql = f"SELECT * FROM users WHERE username LIKE '%{query}%'"
        cursor.execute(sql)''',
                "replace": '''    def search_users(self, query: str) -> List[dict]:
        """Search users by username with safe parameterization"""
        cursor = self.connection.cursor()
        sql = "SELECT * FROM users WHERE username LIKE ?"
        cursor.execute(sql, (f'%{query}%',))'''
            }
        }
    },
    
    {
        "branch": "security/add-password-hashing",
        "title": "Security: Implement bcrypt password hashing",
        "description": "Add password hashing using bcrypt before storing in database to protect user credentials.",
        "files": {
            "src/api/users.py": {
                "search": '''import sqlite3
from typing import List, Optional''',
                "replace": '''import sqlite3
import hashlib
from typing import List, Optional'''
            },
            "src/api/users.py_2": {
                "search": '''    def create_user(self, username: str, email: str, password: str) -> int:
        """
        Create new user
        
        SECURITY ISSUE: Plain text password storage
        """
        cursor = self.connection.cursor()
        
        # SECURITY ISSUE: Storing password in plain text
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, password)  # Plain text password!
        )
        
        self.connection.commit()
        return cursor.lastrowid''',
                "replace": '''    def create_user(self, username: str, email: str, password: str) -> int:
        """Create new user with hashed password"""
        cursor = self.connection.cursor()
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, password_hash)
        )
        
        self.connection.commit()
        return cursor.lastrowid'''
            }
        }
    },
    
    {
        "branch": "security/fix-xss-vulnerability",
        "title": "Security: Add HTML escaping to prevent XSS",
        "description": "Escape user-generated content in profile rendering to prevent cross-site scripting attacks.",
        "files": {
            "src/api/users.py": {
                "search": '''import sqlite3
import hashlib
from typing import List, Optional''',
                "replace": '''import sqlite3
import hashlib
import html
from typing import List, Optional'''
            },
            "src/api/users.py_2": {
                "search": '''    def render_user_profile(self, user_id: int) -> str:
        """
        Render user profile as HTML
        
        NEW METHOD: Generates HTML for user profile display
        """
        user = self.get_user_by_id(user_id)
        
        if not user:
            return "<p>User not found</p>"
        
        # SECURITY ISSUE: XSS vulnerability - no HTML escaping
        html = f"""
        <div class="user-profile">
            <h2>{user['username']}</h2>
            <p>Email: {user['email']}</p>
            <p>Member since: {user['created_at']}</p>
        </div>
        """
        
        return html''',
                "replace": '''    def render_user_profile(self, user_id: int) -> str:
        """Render user profile as HTML with proper escaping"""
        user = self.get_user_by_id(user_id)
        
        if not user:
            return "<p>User not found</p>"
        
        username = html.escape(user['username'])
        email = html.escape(user['email'])
        created = html.escape(str(user['created_at']))
        
        profile_html = f"""
        <div class="user-profile">
            <h2>{username}</h2>
            <p>Email: {email}</p>
            <p>Member since: {created}</p>
        </div>
        """
        
        return profile_html'''
            }
        }
    },
    
    {
        "branch": "security/add-input-validation",
        "title": "Security: Add comprehensive input validation",
        "description": "Implement validation for user inputs to prevent malformed data and injection attacks.",
        "files": {
            "src/api/users.py": {
                "search": '''    def create_user(self, username: str, email: str, password: str) -> int:
        """Create new user with hashed password"""
        cursor = self.connection.cursor()
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, password_hash)
        )
        
        self.connection.commit()
        return cursor.lastrowid''',
                "replace": '''    def create_user(self, username: str, email: str, password: str) -> int:
        """Create new user with validation and hashed password"""
        
        if not username or len(username) < 3 or len(username) > 50:
            raise ValueError("Username must be 3-50 characters")
        
        if not email or '@' not in email or len(email) > 254:
            raise ValueError("Invalid email address")
        
        if not password or len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
        
        cursor = self.connection.cursor()
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, password_hash)
        )
        
        self.connection.commit()
        return cursor.lastrowid'''
            }
        }
    },
    
    # ========== PERFORMANCE IMPROVEMENTS (4 PRs) ==========
    
    {
        "branch": "perf/add-database-indexes",
        "title": "Performance: Add database query optimization hints",
        "description": "Add index hints to improve query performance for user lookups.",
        "files": {
            "src/api/users.py": {
                "search": '''    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """
        Get user by ID
        
        Fixed: Using parameterized query to prevent SQL injection
        """
        cursor = self.connection.cursor()
        # FIXED: Using parameterized query
        query = "SELECT * FROM users WHERE id = ?"
        cursor.execute(query, (user_id,))''',
                "replace": '''    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """Get user by ID with optimized query"""
        cursor = self.connection.cursor()
        query = "SELECT * FROM users INDEXED BY idx_users_id WHERE id = ?"
        cursor.execute(query, (user_id,))'''
            }
        }
    },
    
    {
        "branch": "perf/fix-memory-leak",
        "title": "Performance: Implement LRU cache with size limit",
        "description": "Replace unbounded cache with LRU cache to prevent memory exhaustion.",
        "files": {
            "src/utils/data_processor.py": {
                "search": '''from typing import List, Any
import json''',
                "replace": '''from typing import List, Any
import json
from functools import lru_cache'''
            },
            "src/utils/data_processor.py_2": {
                "search": '''    def cache_heavy_computation(self, data: List[dict]) -> dict:
        """
        Cache results of heavy computation
        
        NEW METHOD: Added caching for expensive operations
        """
        # PERFORMANCE ISSUE: Memory leak - cache never cleared
        if not hasattr(self, '_cache'):
            self._cache = {}
        
        cache_key = str(data)
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Expensive computation
        result = {
            'processed_count': len(data),
            'total_value': sum(item.get('value', 0) for item in data)
        }
        
        # ISSUE: Cache grows unbounded, potential memory leak
        self._cache[cache_key] = result
        
        return result''',
                "replace": '''    @lru_cache(maxsize=128)
    def _compute_metrics(self, data_tuple):
        """Internal cached computation with size limit"""
        data = list(data_tuple)
        return {
            'processed_count': len(data),
            'total_value': sum(item.get('value', 0) for item in data)
        }
    
    def cache_heavy_computation(self, data: List[dict]) -> dict:
        """Cache results with LRU eviction policy"""
        data_tuple = tuple((d['id'], d.get('value', 0)) for d in data)
        return self._compute_metrics(data_tuple)'''
            }
        }
    },
    
    {
        "branch": "perf/implement-connection-pooling",
        "title": "Performance: Add database connection pooling",
        "description": "Implement connection pool to reduce database connection overhead.",
        "files": {
            "src/api/users.py": {
                "search": '''class UserAPI:
    """User API with intentional security and performance issues"""
    
    def __init__(self, db_path: str):
        self.connection = sqlite3.connect(db_path)''',
                "replace": '''class ConnectionPool:
    """Simple connection pool for database"""
    def __init__(self, db_path: str, pool_size: int = 5):
        self.db_path = db_path
        self.pool = [sqlite3.connect(db_path) for _ in range(pool_size)]
        self.available = list(self.pool)
    
    def get_connection(self):
        if self.available:
            return self.available.pop()
        return sqlite3.connect(self.db_path)
    
    def return_connection(self, conn):
        if len(self.available) < len(self.pool):
            self.available.append(conn)

class UserAPI:
    """User API with connection pooling"""
    
    def __init__(self, db_path: str):
        self.pool = ConnectionPool(db_path)
        self.connection = self.pool.get_connection()'''
            }
        }
    },
    
    {
        "branch": "perf/optimize-batch-operations",
        "title": "Performance: Add batch insert for bulk operations",
        "description": "Implement executemany for efficient batch user creation.",
        "files": {
            "src/api/users.py": {
                "search": '''        self.connection.commit()
        return cursor.lastrowid
    
    def render_user_profile(self, user_id: int) -> str:''',
                "replace": '''        self.connection.commit()
        return cursor.lastrowid
    
    def create_users_batch(self, users: List[tuple]) -> int:
        """Create multiple users efficiently using batch insert"""
        cursor = self.connection.cursor()
        
        hashed_users = []
        for username, email, password in users:
            if len(password) < 8:
                continue
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            hashed_users.append((username, email, password_hash))
        
        cursor.executemany(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            hashed_users
        )
        
        self.connection.commit()
        return cursor.rowcount
    
    def render_user_profile(self, user_id: int) -> str:'''
            }
        }
    },
    
    # ========== ARCHITECTURE REFACTORING (4 PRs) ==========
    
    {
        "branch": "arch/apply-strategy-pattern",
        "title": "Architecture: Implement Strategy pattern for data transformation",
        "description": "Refactor transform_data to use Strategy pattern instead of if-else chain.",
        "files": {
            "src/utils/data_processor.py": {
                "search": '''    def transform_data(self, data: Any, format: str) -> str:
        """
        Transform data to different formats
        
        ARCHITECTURE ISSUE: Large if-else chain (should use Strategy pattern)
        """
        # ARCHITECTURE ISSUE: Long if-else chain
        if format == 'json':
            return json.dumps(data)
        elif format == 'csv':
            return "csv_data"
        elif format == 'xml':
            return "<data></data>"
        elif format == 'yaml':
            return "yaml_data"
        elif format == 'text':
            return str(data)
        else:
            return str(data)''',
                "replace": '''    def __init__(self):
        self._formatters = {
            'json': lambda d: json.dumps(d),
            'csv': lambda d: "csv_data",
            'xml': lambda d: "<data></data>",
            'yaml': lambda d: "yaml_data",
            'text': lambda d: str(d)
        }
    
    def transform_data(self, data: Any, format: str) -> str:
        """Transform data using Strategy pattern"""
        formatter = self._formatters.get(format, str)
        return formatter(data)'''
            }
        }
    },
    
    {
        "branch": "arch/extract-service-layer",
        "title": "Architecture: Extract business logic to service layer",
        "description": "Move business logic from User model to UserService following separation of concerns.",
        "files": {
            "src/models/user.py": {
                "search": '''from datetime import datetime
from typing import Optional


class User:''',
                "replace": '''from datetime import datetime
from typing import Optional


class UserService:
    """Service layer for user business logic"""
    
    @staticmethod
    def validate_password_strength(password: str) -> bool:
        """Validate password meets security requirements"""
        return len(password) >= 8
    
    @staticmethod
    def calculate_reputation(created_at: datetime) -> int:
        """Calculate user reputation score"""
        days_active = (datetime.now() - created_at).days
        return days_active * 10
    
    @staticmethod
    def send_welcome_email(email: str):
        """Send welcome email to new user"""
        print(f"Sending welcome email to {email}")
    
    @staticmethod
    def log_user_activity(username: str, action: str):
        """Log user activity"""
        print(f"User {username} performed: {action} at {datetime.now()}")


class User:'''
            },
            "src/models/user.py_2": {
                "search": '''    def validate_password(self, password: str) -> bool:
        """
        Validate password strength
        
        SECURITY ISSUE: Weak password validation
        """
        # SECURITY ISSUE: Very weak password validation
        return len(password) >= 6  # Should be much stronger!
    
    def send_welcome_email(self):
        """
        Send welcome email
        
        ARCHITECTURE ISSUE: Model should not handle email sending
        """
        # ARCHITECTURE ISSUE: Business logic in model
        print(f"Sending welcome email to {self.email}")
    
    def log_login(self):
        """
        Log user login
        
        ARCHITECTURE ISSUE: Model handling logging
        """
        # ARCHITECTURE ISSUE: Model should not handle logging
        print(f"User {self.username} logged in at {datetime.now()}")
    
    def calculate_reputation(self) -> int:
        """
        Calculate user reputation
        
        ARCHITECTURE ISSUE: Complex business logic in model
        """
        # ARCHITECTURE ISSUE: Business logic should be in service layer
        days_since_creation = (datetime.now() - self.created_at).days
        return days_since_creation * 10''',
                "replace": '''    def validate_password(self, password: str) -> bool:
        """Validate password using service layer"""
        return UserService.validate_password_strength(password)
    
    def send_welcome_email(self):
        """Delegate to service layer"""
        UserService.send_welcome_email(self.email)
    
    def log_login(self):
        """Delegate to service layer"""
        UserService.log_user_activity(self.username, 'login')
    
    def calculate_reputation(self) -> int:
        """Delegate to service layer"""
        return UserService.calculate_reputation(self.created_at)'''
            }
        }
    },
    
    {
        "branch": "arch/implement-dependency-injection",
        "title": "Architecture: Add dependency injection for database",
        "description": "Refactor to use dependency injection pattern for better testability.",
        "files": {
            "src/api/users.py": {
                "search": '''class UserAPI:
    """User API with connection pooling"""
    
    def __init__(self, db_path: str):
        self.pool = ConnectionPool(db_path)
        self.connection = self.pool.get_connection()''',
                "replace": '''class DatabaseConnection:
    """Abstraction for database connection"""
    def __init__(self, connection):
        self.connection = connection
    
    def execute(self, query: str, params=None):
        cursor = self.connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor

class UserAPI:
    """User API with dependency injection"""
    
    def __init__(self, db_connection: DatabaseConnection = None):
        if db_connection is None:
            import sqlite3
            conn = sqlite3.connect('default.db')
            db_connection = DatabaseConnection(conn)
        self.db = db_connection'''
            }
        }
    },
    
    {
        "branch": "arch/remove-code-duplication",
        "title": "Architecture: Eliminate code duplication in metrics calculation",
        "description": "Extract common iteration logic to reduce code duplication.",
        "files": {
            "src/utils/data_processor.py": {
                "search": '''    def calculate_metrics(self, data: List[dict]) -> dict:
        """
        Calculate metrics from data
        
        ARCHITECTURE ISSUE: Code duplication
        """
        total = 0
        # ARCHITECTURE ISSUE: Code duplication
        for item in data:
            total += item.get('value', 0)
        
        average = 0
        for item in data:
            average += item.get('value', 0)
        average = average / len(data) if data else 0
        
        maximum = 0
        for item in data:
            val = item.get('value', 0)
            if val > maximum:
                maximum = val
        
        minimum = float('inf')
        for item in data:
            val = item.get('value', 0)
            if val < minimum:
                minimum = val
        
        return {
            'total': total,
            'average': average,
            'max': maximum,
            'min': minimum if minimum != float('inf') else 0
        }''',
                "replace": '''    def _extract_values(self, data: List[dict]) -> List[float]:
        """Extract values from data items"""
        return [item.get('value', 0) for item in data]
    
    def calculate_metrics(self, data: List[dict]) -> dict:
        """Calculate metrics without code duplication"""
        if not data:
            return {'total': 0, 'average': 0, 'max': 0, 'min': 0}
        
        values = self._extract_values(data)
        
        return {
            'total': sum(values),
            'average': sum(values) / len(values),
            'max': max(values),
            'min': min(values)
        }'''
            }
        }
    },
    
    # ========== BUG FIXES / REGRESSIONS (4 PRs) ==========
    
    {
        "branch": "fix/null-pointer-handling",
        "title": "Fix: Add null checks to prevent crashes",
        "description": "Add defensive null checks but introduce subtle performance issue.",
        "files": {
            "src/api/users.py": {
                "search": '''    def get_all_users(self, limit: int = 100, offset: int = 0) -> List[dict]:
        """
        Get all users with pagination
        
        Fixed: Added pagination to prevent loading all records at once
        
        Args:
            limit: Maximum number of users to return (default 100)
            offset: Number of users to skip (default 0)
        
        Returns:
            List of users (paginated)
        """
        cursor = self.connection.cursor()
        query = "SELECT * FROM users LIMIT ? OFFSET ?"
        cursor.execute(query, (limit, offset))
        
        users = []
        for row in cursor.fetchall():
            users.append({
                "id": row[0],
                "username": row[1],
                "email": row[2],
                "created_at": row[3]
            })
        
        return users''',
                "replace": '''    def get_all_users(self, limit: int = 100, offset: int = 0) -> List[dict]:
        """Get all users with pagination and null safety"""
        if limit is None or limit <= 0:
            limit = 100
        if offset is None or offset < 0:
            offset = 0
        
        cursor = self.connection.cursor()
        query = "SELECT * FROM users LIMIT ? OFFSET ?"
        cursor.execute(query, (limit, offset))
        
        users = []
        for row in cursor.fetchall():
            if row and len(row) >= 4:
                for field in row:
                    if field is None:
                        continue
                users.append({
                    "id": row[0] if row[0] is not None else 0,
                    "username": row[1] if row[1] is not None else "",
                    "email": row[2] if row[2] is not None else "",
                    "created_at": row[3] if row[3] is not None else ""
                })
        
        return users'''
            }
        }
    },
    
    {
        "branch": "fix/broken-error-handling",
        "title": "Fix: Improve error handling but break transaction",
        "description": "Add try-catch blocks but forget to rollback on error.",
        "files": {
            "src/api/users.py": {
                "search": '''    def create_user(self, username: str, email: str, password: str) -> int:
        """Create new user with validation and hashed password"""
        
        if not username or len(username) < 3 or len(username) > 50:
            raise ValueError("Username must be 3-50 characters")
        
        if not email or '@' not in email or len(email) > 254:
            raise ValueError("Invalid email address")
        
        if not password or len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
        
        cursor = self.connection.cursor()
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, password_hash)
        )
        
        self.connection.commit()
        return cursor.lastrowid''',
                "replace": '''    def create_user(self, username: str, email: str, password: str) -> int:
        """Create new user with error handling"""
        
        try:
            if not username or len(username) < 3 or len(username) > 50:
                raise ValueError("Username must be 3-50 characters")
            
            if not email or '@' not in email or len(email) > 254:
                raise ValueError("Invalid email address")
            
            if not password or len(password) < 8:
                raise ValueError("Password must be at least 8 characters")
            
            cursor = self.connection.cursor()
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username, email, password_hash)
            )
            
            self.connection.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error creating user: {e}")
            return -1'''
            }
        }
    },
    
    {
        "branch": "feature/user-statistics",
        "title": "Feature: Add user statistics endpoint",
        "description": "Add new feature to track user statistics with subtle SQL injection.",
        "files": {
            "src/api/users.py": {
                "search": '''        return profile_html
    
    def create_users_batch(self, users: List[tuple]) -> int:''',
                "replace": '''        return profile_html
    
    def get_user_statistics(self, user_id: int, stat_type: str = 'all') -> dict:
        """Get detailed statistics for a user"""
        cursor = self.connection.cursor()
        
        query = f"SELECT COUNT(*) as count, AVG(score) as avg_score FROM user_stats WHERE user_id = {user_id}"
        
        if stat_type != 'all':
            query += f" AND type = '{stat_type}'"
        
        cursor.execute(query)
        row = cursor.fetchone()
        
        return {
            'user_id': user_id,
            'stat_type': stat_type,
            'count': row[0] if row else 0,
            'average_score': row[1] if row else 0.0
        }
    
    def create_users_batch(self, users: List[tuple]) -> int:'''
            }
        }
    },
    
    {
        "branch": "refactor/simplify-validation",
        "title": "Refactor: Simplify validation logic",
        "description": "Simplify validation but violate Single Responsibility Principle.",
        "files": {
            "src/models/user.py": {
                "search": '''    def __init__(self, id: int, username: str, email: str, password: str):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.created_at = datetime.now()''',
                "replace": '''    def __init__(self, id: int, username: str, email: str, password: str):
        self.id = id
        self.username = self._validate_and_clean_username(username)
        self.email = self._validate_and_clean_email(email)
        self.password = self._hash_and_validate_password(password)
        self.created_at = datetime.now()
        self._setup_logging()
        self._initialize_cache()
        self._connect_to_notification_service()
    
    def _validate_and_clean_username(self, username: str) -> str:
        username = username.strip().lower()
        if len(username) < 3:
            raise ValueError("Username too short")
        return username
    
    def _validate_and_clean_email(self, email: str) -> str:
        email = email.strip().lower()
        if '@' not in email:
            raise ValueError("Invalid email")
        return email
    
    def _hash_and_validate_password(self, password: str) -> str:
        if len(password) < 8:
            raise ValueError("Password too short")
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _setup_logging(self):
        self.log_file = f"user_{self.id}.log"
    
    def _initialize_cache(self):
        self.cache = {}
    
    def _connect_to_notification_service(self):
        self.notifications_enabled = True'''
            }
        }
    },
    
    # ========== CLEAN CODE / POSITIVE TESTS (4 PRs) ==========
    
    {
        "branch": "docs/add-comprehensive-docstrings",
        "title": "Docs: Add comprehensive API documentation",
        "description": "Add detailed docstrings with examples and type hints for all public methods.",
        "files": {
            "src/api/users.py": {
                "search": '''class UserAPI:
    """User API with dependency injection"""
    
    def __init__(self, db_connection: DatabaseConnection = None):''',
                "replace": '''class UserAPI:
    """
    User API for managing user data and operations.
    
    This class provides a clean interface for user-related database operations
    including CRUD operations, search, and profile rendering. All methods use
    parameterized queries to prevent SQL injection.
    
    Attributes:
        db: DatabaseConnection instance for executing queries
    
    Example:
        >>> api = UserAPI()
        >>> user = api.get_user_by_id(1)
        >>> print(user['username'])
    """
    
    def __init__(self, db_connection: DatabaseConnection = None):'''
            }
        }
    },
    
    {
        "branch": "test/add-unit-tests",
        "title": "Test: Add comprehensive unit tests",
        "description": "Add unit tests for core functionality with good coverage.",
        "files": {
            "tests/test_user_api.py": """import unittest
from src.api.users import UserAPI
import sqlite3


class TestUserAPI(unittest.TestCase):
    """Test suite for UserAPI class"""
    
    def setUp(self):
        """Set up test database"""
        self.conn = sqlite3.connect(':memory:')
        self.conn.execute(
            'CREATE TABLE users (id INTEGER, username TEXT, email TEXT, password TEXT, created_at TEXT)'
        )
        self.conn.commit()
    
    def tearDown(self):
        """Clean up test database"""
        self.conn.close()
    
    def test_get_user_by_id_returns_none_for_missing_user(self):
        """Test that get_user_by_id returns None for non-existent users"""
        api = UserAPI()
        result = api.get_user_by_id(999)
        self.assertIsNone(result)
    
    def test_create_user_with_valid_data(self):
        """Test creating user with valid inputs"""
        api = UserAPI()
        user_id = api.create_user('testuser', 'test@example.com', 'password123')
        self.assertIsInstance(user_id, int)
        self.assertGreater(user_id, 0)


if __name__ == '__main__':
    unittest.main()
"""
        }
    },
    
    {
        "branch": "quality/add-error-logging",
        "title": "Quality: Implement structured error logging",
        "description": "Add comprehensive error logging with context for debugging.",
        "files": {
            "src/api/users.py": {
                "search": '''import sqlite3
import hashlib
import html
from typing import List, Optional''',
                "replace": '''import sqlite3
import hashlib
import html
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)'''
            },
            "src/api/users.py_2": {
                "search": '''    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """Get user by ID with optimized query"""
        cursor = self.connection.cursor()
        query = "SELECT * FROM users INDEXED BY idx_users_id WHERE id = ?"
        cursor.execute(query, (user_id,))''',
                "replace": '''    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """Get user by ID with optimized query and logging"""
        try:
            logger.debug(f"Fetching user with ID: {user_id}")
            cursor = self.connection.cursor()
            query = "SELECT * FROM users INDEXED BY idx_users_id WHERE id = ?"
            cursor.execute(query, (user_id,))
        except Exception as e:
            logger.error(f"Failed to fetch user {user_id}: {str(e)}", exc_info=True)
            return None'''
            }
        }
    },
    
    {
        "branch": "feature/add-monitoring",
        "title": "Feature: Add performance monitoring",
        "description": "Implement performance tracking and metrics collection.",
        "files": {
            "src/utils/data_processor.py": {
                "search": '''from typing import List, Any
import json
from functools import lru_cache''',
                "replace": '''from typing import List, Any
import json
import time
from functools import lru_cache, wraps


def monitor_performance(func):
    """Decorator to track function execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        print(f"{func.__name__} took {elapsed:.3f}s")
        return result
    return wrapper'''
            },
            "src/utils/data_processor.py_2": {
                "search": '''    def process_items(self, items: List[dict]) -> List[dict]:
        """
        Process list of items
        
        Fixed: Using dictionary for O(n) complexity
        """''',
                "replace": '''    @monitor_performance
    def process_items(self, items: List[dict]) -> List[dict]:
        """Process list of items with performance monitoring"""'''
            }
        }
    }
]


def run_command(cmd, cwd=None):
    """Execute shell command and return output"""
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd,
        capture_output=True,
        text=True
    )
    return result.returncode == 0, result.stdout, result.stderr


def apply_file_changes(pr_def):
    """Apply file changes for a PR"""
    for filename, changes in pr_def["files"].items():
        # Handle multiple changes to same file (filename_2, filename_3, etc.)
        actual_filename = filename.split('_')[0] if '_' in filename else filename
        filepath = DEMO_PROJECT / actual_filename
        
        if not filepath.exists():
            if not filename.endswith('.py'):
                # Create new file
                filepath.parent.mkdir(parents=True, exist_ok=True)
                filepath.write_text(changes, encoding='utf-8')
                continue
            else:
                print(f"  ⚠️  File not found: {filepath}")
                continue
        
        content = filepath.read_text(encoding='utf-8')
        
        if isinstance(changes, dict):
            # Replace operation
            if changes["search"] in content:
                content = content.replace(changes["search"], changes["replace"])
                filepath.write_text(content, encoding='utf-8')
                print(f"  ✓ Updated {actual_filename}")
            else:
                print(f"  ⚠️  Pattern not found in {actual_filename}")
        else:
            # Direct write
            filepath.write_text(changes, encoding='utf-8')
            print(f"  ✓ Created {actual_filename}")


def create_pr_branch(pr_def, pr_number):
    """Create and push a PR branch"""
    branch = pr_def["branch"]
    title = pr_def["title"]
    
    print(f"\n{'='*70}")
    print(f"PR #{pr_number}: {title}")
    print(f"{'='*70}")
    
    # Checkout main and pull latest
    print("  Preparing branch...")
    run_command("git checkout main", cwd=DEMO_PROJECT)
    run_command("git pull origin main", cwd=DEMO_PROJECT)
    
    # Create new branch
    success, _, stderr = run_command(f"git checkout -b {branch}", cwd=DEMO_PROJECT)
    if not success:
        print(f"  ⚠️  Branch might already exist: {stderr}")
        run_command(f"git checkout {branch}", cwd=DEMO_PROJECT)
    
    # Apply changes
    print("  Applying code changes...")
    apply_file_changes(pr_def)
    
    # Stage and commit
    print("  Committing changes...")
    run_command("git add .", cwd=DEMO_PROJECT)
    
    commit_msg = f"{title}\n\n{pr_def['description']}"
    success, _, _ = run_command(
        f'git commit -m "{commit_msg}"',
        cwd=DEMO_PROJECT
    )
    
    if not success:
        print("  ⚠️  Nothing to commit or commit failed")
        return False
    
    # Push branch
    print("  Pushing to GitHub...")
    success, _, stderr = run_command(
        f"git push -u origin {branch}",
        cwd=DEMO_PROJECT
    )
    
    if success:
        print(f"  ✅ PR #{pr_number} ready!")
        print(f"  🔗 https://github.com/4ndr-34/demo-pr-review/pull/new/{branch}")
        return True
    else:
        print(f"  ❌ Failed to push: {stderr}")
        return False


def main():
    print("="*70)
    print("AUTOMATED PR GENERATION FOR THESIS DATA COLLECTION")
    print("="*70)
    print(f"\nGenerating {len(TEST_PRS)} test PRs...")
    print(f"Target repository: {DEMO_PROJECT}")
    
    if not DEMO_PROJECT.exists():
        print(f"\n❌ Error: Demo project not found at {DEMO_PROJECT}")
        print("Please ensure demo-pr-review is at the correct location.")
        sys.exit(1)
    
    # Verify we're in a git repo
    success, _, _ = run_command("git status", cwd=DEMO_PROJECT)
    if not success:
        print("\n❌ Error: Not a git repository")
        sys.exit(1)
    
    print("\n" + "="*70)
    print("Starting PR generation...")
    print("="*70)
    
    successful = 0
    failed = 0
    
    for i, pr_def in enumerate(TEST_PRS, start=3):  # Start at PR #3
        if create_pr_branch(pr_def, i):
            successful += 1
        else:
            failed += 1
        
        # Small delay to avoid overwhelming Git
        time.sleep(0.5)
    
    print("\n" + "="*70)
    print("GENERATION COMPLETE")
    print("="*70)
    print(f"\n✅ Successfully created: {successful} PRs")
    if failed > 0:
        print(f"❌ Failed: {failed} PRs")
    
    print("\n" + "="*70)
    print("NEXT STEPS:")
    print("="*70)
    print("\n1. Go to: https://github.com/4ndr-34/demo-pr-review/pulls")
    print("2. You'll see 'Compare & pull request' buttons for each branch")
    print("3. Click each button to create the PR (titles/descriptions are pre-filled)")
    print("4. GitHub Actions will automatically review each PR!")
    print("5. Data will be saved to data-collection branch")
    print("\nAlternatively, create all PRs at once using GitHub CLI:")
    print("\n  cd demo-pr-review")
    for pr_def in TEST_PRS:
        branch = pr_def["branch"]
        title = pr_def["title"]
        desc = pr_def["description"].replace('"', '\\"')
        print(f'  gh pr create --base main --head {branch} --title "{title}" --body "{desc}"')
    
    print("\n" + "="*70)
    print(f"Total branches created: {successful}")
    print("All branches are ready for PR creation!")
    print("="*70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Generation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
