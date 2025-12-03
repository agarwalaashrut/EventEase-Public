"""
User model for managing user authentication data
Defines the structure and validation for User documents in MongoDB
"""
from datetime import datetime
from typing import Optional
from bson import ObjectId


class User:
    """User model representing a user with authentication capabilities"""
    
    def __init__(self, data: dict):
        """Initialize User from dictionary data"""
        self._id = data.get('_id')
        self.email = data.get('email', '')
        self.name = data.get('name', '')
        self.password_hash = data.get('password_hash')  # None for OAuth users
        self.oauth_provider = data.get('oauth_provider')  # e.g., 'google', None for email/password
        self.oauth_id = data.get('oauth_id')  # Provider-specific user ID
        self.created_at = data.get('created_at', datetime.utcnow())
        self.last_login = data.get('last_login')
        self.invitations = data.get('invitations', [])  # List of event IDs the user is invited to
        # Google Calendar OAuth
        self.google_refresh_token = data.get('google_refresh_token')  # Refresh token for calendar API
        self.google_calendar_id = data.get('google_calendar_id')  # User's primary calendar ID (usually email)

    
    def to_dict(self) -> dict:
        """Convert User to dictionary for JSON serialization (excludes password_hash and refresh_token)"""
        return {
            '_id': str(self._id) if self._id else None,
            'email': self.email,
            'name': self.name,
            'oauth_provider': self.oauth_provider,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'last_login': self.last_login.isoformat() if isinstance(self.last_login, datetime) else self.last_login,
            'invitations': self.invitations,
            'google_calendar_connected': bool(self.google_refresh_token)
        }
    
    def to_mongo(self) -> dict:
        """Convert User to MongoDB document format"""
        doc = {
            'email': self.email,
            'name': self.name,
            'password_hash': self.password_hash,
            'oauth_provider': self.oauth_provider,
            'oauth_id': self.oauth_id,
            'created_at': self.created_at,
            'last_login': self.last_login,
            'invitations': self.invitations,
            'google_refresh_token': self.google_refresh_token,
            'google_calendar_id': self.google_calendar_id
        }
        if self._id:
            doc['_id'] = self._id
        return doc
    
    @staticmethod
    def from_mongo(doc: dict) -> 'User':
        """Create User instance from MongoDB document"""
        if doc is None:
            return None
        return User(doc)
    
    @staticmethod
    def validate(data: dict) -> tuple[bool, Optional[str]]:
        """
        Validate user data
        Returns: (is_valid, error_message)
        """
        required_fields = ['email']
        
        for field in required_fields:
            if field not in data or not data[field]:
                return False, f"Missing required field: {field}"
        
        # Basic email validation
        if '@' not in data['email']:
            return False, "Invalid email format"
        
        return True, None
