"""
Test User model with Google Calendar integration
Run with: pytest tests/test_user_model.py -v
"""
import pytest
from app.models.user import User
from bson.objectid import ObjectId
from datetime import datetime


class TestUserInit:
    """Test User model initialization"""
    
    def test_user_init_basic(self):
        """Test User initialization with basic data"""
        user_data = {
            'email': 'user@example.com',
            'name': 'Test User',
            'password_hash': 'hashed_password',
            'created_at': datetime.utcnow()
        }
        
        user = User(user_data)
        
        assert user.email == 'user@example.com'
        assert user.name == 'Test User'
        assert user.password_hash == 'hashed_password'
    
    def test_user_init_with_google_calendar(self):
        """Test User initialization with Google Calendar fields"""
        user_data = {
            'email': 'user@example.com',
            'name': 'Test User',
            'google_refresh_token': 'refresh_token_xyz',
            'google_calendar_id': 'user@example.com',
            'oauth_provider': 'google',
            'oauth_id': 'google_user_id_123'
        }
        
        user = User(user_data)
        
        assert user.google_refresh_token == 'refresh_token_xyz'
        assert user.google_calendar_id == 'user@example.com'
        assert user.oauth_provider == 'google'
        assert user.oauth_id == 'google_user_id_123'
    
    def test_user_init_default_values(self):
        """Test User initializes with default values"""
        user_data = {'email': 'user@example.com'}
        
        user = User(user_data)
        
        assert user.email == 'user@example.com'
        assert user.name == ''
        assert user.password_hash is None
        assert user.oauth_provider is None
        assert user.google_refresh_token is None
        assert user.google_calendar_id is None
        assert user.invitations == []


class TestUserToDict:
    """Test User.to_dict() serialization"""
    
    def test_to_dict_excludes_sensitive_data(self):
        """Test to_dict excludes password_hash and refresh_token"""
        user_data = {
            'email': 'user@example.com',
            'name': 'Test User',
            'password_hash': 'secret_hash',
            'google_refresh_token': 'refresh_token_xyz'
        }
        
        user = User(user_data)
        user_dict = user.to_dict()
        
        assert 'password_hash' not in user_dict
        assert 'google_refresh_token' not in user_dict
    
    def test_to_dict_includes_calendar_status(self):
        """Test to_dict includes google_calendar_connected flag"""
        # User with calendar connected
        user_with_calendar = User({
            'email': 'user@example.com',
            'google_refresh_token': 'token_xyz'
        })
        
        user_dict = user_with_calendar.to_dict()
        assert user_dict['google_calendar_connected'] is True
        
        # User without calendar
        user_without_calendar = User({
            'email': 'user@example.com',
            'google_refresh_token': None
        })
        
        user_dict = user_without_calendar.to_dict()
        assert user_dict['google_calendar_connected'] is False
    
    def test_to_dict_datetime_serialization(self):
        """Test to_dict serializes datetime fields to ISO format"""
        now = datetime.utcnow()
        user_data = {
            'email': 'user@example.com',
            'created_at': now,
            'last_login': now
        }
        
        user = User(user_data)
        user_dict = user.to_dict()
        
        assert isinstance(user_dict['created_at'], str)
        assert isinstance(user_dict['last_login'], str)
        assert user_dict['created_at'].endswith('Z') or '+' in user_dict['created_at']
    
    def test_to_dict_id_conversion(self):
        """Test to_dict converts ObjectId to string"""
        user_id = ObjectId()
        user_data = {
            '_id': user_id,
            'email': 'user@example.com'
        }
        
        user = User(user_data)
        user_dict = user.to_dict()
        
        assert isinstance(user_dict['_id'], str)
        assert user_dict['_id'] == str(user_id)


class TestUserToMongo:
    """Test User.to_mongo() for database storage"""
    
    def test_to_mongo_includes_all_fields(self):
        """Test to_mongo includes all fields for database"""
        user_data = {
            'email': 'user@example.com',
            'name': 'Test User',
            'password_hash': 'hashed_pass',
            'oauth_provider': 'google',
            'oauth_id': 'google_id_123',
            'google_refresh_token': 'refresh_token_xyz',
            'google_calendar_id': 'user@example.com',
            'invitations': ['event1', 'event2']
        }
        
        user = User(user_data)
        mongo_doc = user.to_mongo()
        
        assert mongo_doc['email'] == 'user@example.com'
        assert mongo_doc['password_hash'] == 'hashed_pass'
        assert mongo_doc['google_refresh_token'] == 'refresh_token_xyz'
        assert mongo_doc['google_calendar_id'] == 'user@example.com'
        assert mongo_doc['invitations'] == ['event1', 'event2']
    
    def test_to_mongo_excludes_id_for_new_user(self):
        """Test to_mongo excludes _id for new users"""
        user_data = {'email': 'user@example.com'}
        user = User(user_data)
        
        mongo_doc = user.to_mongo()
        
        assert '_id' not in mongo_doc
    
    def test_to_mongo_includes_id_for_existing_user(self):
        """Test to_mongo includes _id for existing users"""
        user_id = ObjectId()
        user_data = {
            '_id': user_id,
            'email': 'user@example.com'
        }
        
        user = User(user_data)
        mongo_doc = user.to_mongo()
        
        assert mongo_doc['_id'] == user_id


class TestUserFromMongo:
    """Test User.from_mongo() for database retrieval"""
    
    def test_from_mongo_creates_user(self):
        """Test from_mongo creates User from MongoDB document"""
        doc = {
            '_id': ObjectId(),
            'email': 'user@example.com',
            'name': 'Test User',
            'password_hash': 'hashed_pass',
            'google_refresh_token': 'token_xyz',
            'google_calendar_id': 'user@example.com',
            'invitations': ['event1']
        }
        
        user = User.from_mongo(doc)
        
        assert user is not None
        assert user.email == 'user@example.com'
        assert user.google_refresh_token == 'token_xyz'
    
    def test_from_mongo_handles_none(self):
        """Test from_mongo returns None for None input"""
        user = User.from_mongo(None)
        
        assert user is None
    
    def test_from_mongo_with_oauth(self):
        """Test from_mongo with OAuth fields"""
        doc = {
            '_id': ObjectId(),
            'email': 'user@example.com',
            'oauth_provider': 'google',
            'oauth_id': 'google_id_123',
            'google_refresh_token': 'refresh_token_xyz',
            'google_calendar_id': 'user@example.com'
        }
        
        user = User.from_mongo(doc)
        
        assert user.oauth_provider == 'google'
        assert user.oauth_id == 'google_id_123'
        assert user.google_refresh_token == 'refresh_token_xyz'


class TestUserValidation:
    """Test User.validate() validation"""
    
    def test_validate_valid_user(self):
        """Test validation passes for valid user data"""
        user_data = {'email': 'user@example.com'}
        
        is_valid, error = User.validate(user_data)
        
        assert is_valid is True
        assert error is None
    
    def test_validate_missing_email(self):
        """Test validation fails for missing email"""
        user_data = {'name': 'Test User'}
        
        is_valid, error = User.validate(user_data)
        
        assert is_valid is False
        assert 'email' in error.lower()
    
    def test_validate_invalid_email(self):
        """Test validation fails for invalid email format"""
        user_data = {'email': 'not_an_email'}
        
        is_valid, error = User.validate(user_data)
        
        assert is_valid is False
        assert 'email' in error.lower()
    
    def test_validate_empty_email(self):
        """Test validation fails for empty email"""
        user_data = {'email': ''}
        
        is_valid, error = User.validate(user_data)
        
        assert is_valid is False


class TestUserWithGoogleOAuth:
    """Test User model with Google OAuth workflow"""
    
    def test_user_oauth_to_mongo_to_user(self):
        """Test full OAuth user lifecycle: create -> mongo -> create"""
        # Create OAuth user
        oauth_user_data = {
            'email': 'user@example.com',
            'name': 'Google User',
            'oauth_provider': 'google',
            'oauth_id': 'google_id_xyz',
            'google_refresh_token': 'refresh_token_abc',
            'google_calendar_id': 'user@example.com',
            'invitations': []
        }
        
        user = User(oauth_user_data)
        
        # Convert to MongoDB
        mongo_doc = user.to_mongo()
        
        # Create new user from MongoDB document
        restored_user = User.from_mongo(mongo_doc)
        
        assert restored_user.email == user.email
        assert restored_user.oauth_provider == user.oauth_provider
        assert restored_user.google_refresh_token == user.google_refresh_token
    
    def test_user_calendar_disconnect(self):
        """Test user can disconnect calendar"""
        user_data = {
            'email': 'user@example.com',
            'google_refresh_token': 'token_xyz',
            'google_calendar_id': 'user@example.com'
        }
        
        user = User(user_data)
        
        # User has calendar
        assert user.to_dict()['google_calendar_connected'] is True
        
        # Disconnect calendar
        user.google_refresh_token = None
        user.google_calendar_id = None
        
        # User no longer has calendar
        assert user.to_dict()['google_calendar_connected'] is False
