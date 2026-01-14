"""
Test OAuth and Calendar integration
Run with: pytest tests/test_oauth.py -v
"""
import pytest
from unittest.mock import patch, MagicMock
from app import create_app
import uuid


@pytest.fixture
def client():
    """Create test client."""
    app = create_app('TestingConfig')
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        yield client


@pytest.fixture
def app():
    """Create Flask app for testing."""
    app = create_app('TestingConfig')
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    return app


class TestGoogleLogin:
    """Test Google OAuth login endpoint"""
    
    @patch('app.routes.auth.get_calendar_service')
    def test_google_login_success(self, mock_calendar_service, client, app):
        """Test /api/auth/google/login returns auth URL and state"""
        mock_service = MagicMock()
        mock_calendar_service.return_value = mock_service
        mock_service.get_auth_url.return_value = 'https://accounts.google.com/o/oauth2/auth?...'
        
        with client:
            response = client.get('/api/auth/google/login')
            
            assert response.status_code == 200
            data = response.json
            assert data['success'] is True
            assert 'auth_url' in data
            assert 'state' in data
            assert data['auth_url'].startswith('https://accounts.google.com')
    
    @patch('app.routes.auth.get_calendar_service')
    def test_google_login_with_custom_redirect_url(self, mock_calendar_service, client, app):
        """Test /api/auth/google/login with custom redirect URL"""
        mock_service = MagicMock()
        mock_calendar_service.return_value = mock_service
        mock_service.get_auth_url.return_value = 'https://accounts.google.com/o/oauth2/auth?...'
        
        custom_url = 'http://localhost:3000/dashboard'
        
        with client:
            response = client.get(f'/api/auth/google/login?redirect_url={custom_url}')
            
            assert response.status_code == 200
            data = response.json
            assert data['success'] is True
    
    @patch('app.routes.auth.get_calendar_service')
    def test_google_login_exception_handling(self, mock_calendar_service, client):
        """Test /api/auth/google/login handles exceptions gracefully"""
        mock_calendar_service.side_effect = Exception('Calendar service error')
        
        response = client.get('/api/auth/google/login')
        
        assert response.status_code == 500
        data = response.json
        assert data['success'] is False
        assert 'error' in data


class TestGoogleCallback:
    """Test Google OAuth callback endpoint"""
    
    @patch('app.routes.auth.get_calendar_service')
    @patch('app.routes.auth.get_db')
    def test_google_callback_success(self, mock_get_db, mock_calendar_service, client, app):
        """Test /oauth2callback with valid code and state creates user and redirects"""
        # Mock calendar service
        mock_service = MagicMock()
        mock_calendar_service.return_value = mock_service
        mock_service.get_credentials_from_code.return_value = (
            {
                'token': 'access_token',
                'refresh_token': 'refresh_token_xyz',
                'token_uri': 'https://oauth2.googleapis.com/token',
                'client_id': 'client_id',
                'client_secret': 'secret',
                'scopes': ['calendar']
            },
            'access_token'
        )
        
        # Mock database
        mock_db = MagicMock()
        mock_users_collection = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.__getitem__.return_value = {'Users': mock_users_collection}
        
        # Mock Google user info
        mock_users_collection.find_one.return_value = None  # New user
        mock_users_collection.insert_one.return_value = MagicMock(inserted_id='user_id_123')
        
        with client:
            # First initiate login to get state
            login_response = client.get('/api/auth/google/login')
            state = login_response.json['state']
            
            # Mock the build function for Google API
            with patch('app.routes.auth.build') as mock_build:
                mock_oauth_service = MagicMock()
                mock_build.return_value = mock_oauth_service
                mock_oauth_service.userinfo().get().execute.return_value = {
                    'email': 'user@example.com',
                    'name': 'Test User',
                    'id': 'google_id_123'
                }
                
                # Callback with code and state
                response = client.get(f'/oauth2callback?code=auth_code_123&state={state}')
                
                assert response.status_code == 302  # Redirect
                assert 'auth=success' in response.location
                assert 'user_id=' in response.location
                assert 'email=' in response.location
    
    @patch('app.routes.auth.get_calendar_service')
    def test_google_callback_missing_code(self, mock_calendar_service, client):
        """Test /oauth2callback without code parameter redirects with error"""
        response = client.get('/oauth2callback?state=invalid_state')
        
        assert response.status_code == 302
        assert 'auth=failed' in response.location
        assert 'missing_code_or_state' in response.location
    
    def test_google_callback_missing_state(self, client):
        """Test /oauth2callback without state parameter redirects with error"""
        response = client.get('/oauth2callback?code=auth_code_123')
        
        assert response.status_code == 302
        assert 'auth=failed' in response.location
    
    def test_google_callback_user_denied(self, client):
        """Test /oauth2callback when user denies authorization"""
        response = client.get('/oauth2callback?error=access_denied')
        
        assert response.status_code == 302
        assert 'auth=cancelled' in response.location
    
    @patch('app.routes.auth.get_calendar_service')
    @patch('app.routes.auth.get_db')
    def test_google_callback_invalid_state(self, mock_get_db, mock_calendar_service, client):
        """Test /oauth2callback with invalid state token"""
        response = client.get('/oauth2callback?code=auth_code_123&state=invalid_state_123')
        
        assert response.status_code == 302
        assert 'auth=failed' in response.location
        assert 'invalid_state' in response.location


class TestCalendarStatus:
    """Test calendar connection status endpoint"""
    
    @patch('app.routes.auth.get_db')
    def test_get_calendar_status_connected(self, mock_get_db, client):
        """Test /api/auth/calendar/status when calendar is connected"""
        mock_db = MagicMock()
        mock_users_collection = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.__getitem__.return_value = {'Users': mock_users_collection}
        
        mock_users_collection.find_one.return_value = {
            '_id': 'user_id_123',
            'email': 'user@example.com',
            'name': 'Test User',
            'google_refresh_token': 'refresh_token_xyz',
            'google_calendar_id': 'user@example.com'
        }
        
        response = client.get('/api/auth/calendar/status?email=user@example.com')
        
        assert response.status_code == 200
        data = response.json
        assert data['success'] is True
        assert data['calendar_connected'] is True
        assert data['calendar_id'] == 'user@example.com'
    
    @patch('app.routes.auth.get_db')
    def test_get_calendar_status_not_connected(self, mock_get_db, client):
        """Test /api/auth/calendar/status when calendar is not connected"""
        mock_db = MagicMock()
        mock_users_collection = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.__getitem__.return_value = {'Users': mock_users_collection}
        
        mock_users_collection.find_one.return_value = {
            '_id': 'user_id_123',
            'email': 'user@example.com',
            'name': 'Test User',
            'google_refresh_token': None,
            'google_calendar_id': None
        }
        
        response = client.get('/api/auth/calendar/status?email=user@example.com')
        
        assert response.status_code == 200
        data = response.json
        assert data['success'] is True
        assert data['calendar_connected'] is False
    
    def test_get_calendar_status_missing_email(self, client):
        """Test /api/auth/calendar/status without email parameter"""
        response = client.get('/api/auth/calendar/status')
        
        assert response.status_code == 400
        data = response.json
        assert data['success'] is False
        assert 'error' in data
    
    @patch('app.routes.auth.get_db')
    def test_get_calendar_status_user_not_found(self, mock_get_db, client):
        """Test /api/auth/calendar/status for non-existent user"""
        mock_db = MagicMock()
        mock_users_collection = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.__getitem__.return_value = {'Users': mock_users_collection}
        mock_users_collection.find_one.return_value = None
        
        response = client.get('/api/auth/calendar/status?email=nonexistent@example.com')
        
        assert response.status_code == 404
        data = response.json
        assert data['success'] is False
        assert 'error' in data


class TestDisconnectCalendar:
    """Test calendar disconnection endpoint"""
    
    @patch('app.routes.auth.get_db')
    def test_disconnect_calendar_success(self, mock_get_db, client):
        """Test /api/auth/calendar/disconnect successfully revokes access"""
        mock_db = MagicMock()
        mock_users_collection = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.__getitem__.return_value = {'Users': mock_users_collection}
        
        mock_result = MagicMock()
        mock_result.matched_count = 1
        mock_users_collection.update_one.return_value = mock_result
        
        response = client.post('/api/auth/calendar/disconnect', json={'email': 'user@example.com'})
        
        assert response.status_code == 200
        data = response.json
        assert data['success'] is True
        assert 'message' in data
        
        # Verify update was called with None values
        mock_users_collection.update_one.assert_called_once()
        call_args = mock_users_collection.update_one.call_args
        update_values = call_args[0][1]['$set']
        assert update_values['google_refresh_token'] is None
        assert update_values['google_calendar_id'] is None
    
    @patch('app.routes.auth.get_db')
    def test_disconnect_calendar_user_not_found(self, mock_get_db, client):
        """Test /api/auth/calendar/disconnect for non-existent user"""
        mock_db = MagicMock()
        mock_users_collection = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.__getitem__.return_value = {'Users': mock_users_collection}
        
        mock_result = MagicMock()
        mock_result.matched_count = 0
        mock_users_collection.update_one.return_value = mock_result
        
        response = client.post('/api/auth/calendar/disconnect', json={'email': 'nonexistent@example.com'})
        
        assert response.status_code == 404
        data = response.json
        assert data['success'] is False
    
    def test_disconnect_calendar_missing_email(self, client):
        """Test /api/auth/calendar/disconnect without email field"""
        response = client.post('/api/auth/calendar/disconnect', json={})
        
        assert response.status_code == 400
        data = response.json
        assert data['success'] is False
        assert 'error' in data
