"""
Test Google Calendar Service
Run with: pytest tests/test_calendar_service.py -v
"""
import pytest
from unittest.mock import patch, MagicMock
from app.services.calendar_service import CalendarService, get_calendar_service
from datetime import datetime, timedelta
import os


@pytest.fixture
def calendar_service():
    """Create calendar service instance for testing"""
    with patch.dict(os.environ, {
        'GOOGLE_CLIENT_ID': 'test_client_id',
        'GOOGLE_CLIENT_SECRET': 'test_client_secret',
        'GOOGLE_REDIRECT_URI': 'http://localhost:5000/oauth2callback'
    }):
        return CalendarService()


class TestCalendarServiceInit:
    """Test CalendarService initialization"""
    
    def test_calendar_service_init_success(self, calendar_service):
        """Test CalendarService initializes with credentials from environment"""
        assert calendar_service.client_id == 'test_client_id'
        assert calendar_service.client_secret == 'test_client_secret'
        assert calendar_service.redirect_uri == 'http://localhost:5000/oauth2callback'
    
    def test_calendar_service_missing_credentials(self):
        """Test CalendarService raises error when credentials are missing"""
        with patch.dict(os.environ, {'GOOGLE_CLIENT_ID': ''}, clear=False):
            with pytest.raises(ValueError):
                CalendarService()


class TestGetAuthUrl:
    """Test auth URL generation"""
    
    @patch('app.services.calendar_service.Flow')
    def test_get_auth_url_success(self, mock_flow, calendar_service):
        """Test get_auth_url returns valid authorization URL"""
        mock_flow_instance = MagicMock()
        mock_flow.from_client_config.return_value = mock_flow_instance
        mock_flow_instance.authorization_url.return_value = (
            'https://accounts.google.com/o/oauth2/auth?code=...&state=...',
            'test_state'
        )
        
        auth_url = calendar_service.get_auth_url('test_state')
        
        assert auth_url.startswith('https://accounts.google.com')
        assert 'oauth2' in auth_url
        mock_flow_instance.authorization_url.assert_called_once()


class TestGetCredentialsFromCode:
    """Test credential exchange"""
    
    @patch('app.services.calendar_service.Flow')
    def test_get_credentials_from_code_success(self, mock_flow, calendar_service):
        """Test exchanging authorization code for credentials"""
        mock_flow_instance = MagicMock()
        mock_flow.from_client_config.return_value = mock_flow_instance
        
        # Mock credentials
        mock_credentials = MagicMock()
        mock_credentials.token = 'access_token_123'
        mock_credentials.refresh_token = 'refresh_token_xyz'
        mock_credentials.token_uri = 'https://oauth2.googleapis.com/token'
        mock_credentials.client_id = 'test_client_id'
        mock_credentials.client_secret = 'test_client_secret'
        mock_credentials.scopes = ['https://www.googleapis.com/auth/calendar']
        
        mock_flow_instance.credentials = mock_credentials
        
        creds_dict, access_token = calendar_service.get_credentials_from_code('auth_code_123')
        
        assert access_token == 'access_token_123'
        assert creds_dict['refresh_token'] == 'refresh_token_xyz'
        assert creds_dict['token'] == 'access_token_123'
        assert 'token_uri' in creds_dict


class TestRefreshAccessToken:
    """Test access token refresh"""
    
    @patch('app.services.calendar_service.Credentials')
    @patch('app.services.calendar_service.Request')
    def test_refresh_access_token_success(self, mock_request_class, mock_credentials_class, calendar_service):
        """Test refreshing an expired access token"""
        mock_credentials = MagicMock()
        mock_credentials.token = 'new_access_token_456'
        mock_credentials_class.return_value = mock_credentials
        
        new_token = calendar_service.refresh_access_token('refresh_token_xyz')
        
        assert new_token == 'new_access_token_456'
        mock_credentials.refresh.assert_called_once()


class TestCreateCalendarEvent:
    """Test calendar event creation"""
    
    @patch('app.services.calendar_service.CalendarService.refresh_access_token')
    @patch('app.services.calendar_service.build')
    def test_create_calendar_event_success(self, mock_build, mock_refresh, calendar_service):
        """Test creating a calendar event successfully"""
        mock_refresh.return_value = 'new_access_token'
        
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        mock_event = MagicMock()
        mock_event.get.return_value = 'google_event_id_789'
        mock_service.events().insert().execute.return_value = mock_event
        
        success, event_id, error = calendar_service.create_calendar_event(
            refresh_token='refresh_token_xyz',
            event_title='Team Meeting',
            event_time='2025-12-15T10:00:00',
            event_description='Weekly standup',
            organizer_email='org@example.com',
            attendee_emails=['user1@example.com', 'user2@example.com']
        )
        
        assert success is True
        assert event_id == 'google_event_id_789'
        assert error is None
        
        # Verify service was called with correct parameters
        mock_service.events().insert.assert_called_once()
        call_args = mock_service.events().insert.call_args
        assert call_args[1]['calendarId'] == 'primary'
        event_body = call_args[1]['body']
        assert event_body['summary'] == 'Team Meeting'
        assert event_body['description'] == 'Weekly standup'
    
    @patch('app.services.calendar_service.CalendarService.refresh_access_token')
    @patch('app.services.calendar_service.build')
    def test_create_calendar_event_with_attendees(self, mock_build, mock_refresh, calendar_service):
        """Test creating calendar event with attendees"""
        mock_refresh.return_value = 'access_token'
        
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        mock_event = MagicMock()
        mock_event.get.return_value = 'event_id'
        mock_service.events().insert().execute.return_value = mock_event
        
        attendees = ['alice@example.com', 'bob@example.com']
        success, event_id, error = calendar_service.create_calendar_event(
            refresh_token='refresh_token_xyz',
            event_title='All Hands',
            event_time='2025-12-15T14:00:00',
            attendee_emails=attendees
        )
        
        assert success is True
        
        # Verify attendees were included
        call_args = mock_service.events().insert.call_args
        event_body = call_args[1]['body']
        assert 'attendees' in event_body
        assert len(event_body['attendees']) == 2
    
    @patch('app.services.calendar_service.CalendarService.refresh_access_token')
    @patch('app.services.calendar_service.build')
    def test_create_calendar_event_api_error(self, mock_build, mock_refresh, calendar_service):
        """Test handling of Google Calendar API errors"""
        mock_refresh.return_value = 'access_token'
        
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        # Mock API error
        from googleapiclient.errors import HttpError
        mock_http_resp = MagicMock()
        mock_http_resp.status = 403
        mock_service.events().insert().execute.side_effect = HttpError(
            mock_http_resp,
            b'Permission denied'
        )
        
        success, event_id, error = calendar_service.create_calendar_event(
            refresh_token='refresh_token_xyz',
            event_title='Meeting',
            event_time='2025-12-15T10:00:00'
        )
        
        assert success is False
        assert event_id is None
        assert error is not None
        assert '403' in error
    
    @patch('app.services.calendar_service.CalendarService.refresh_access_token')
    def test_create_calendar_event_refresh_error(self, mock_refresh, calendar_service):
        """Test handling of token refresh errors"""
        mock_refresh.side_effect = Exception('Token refresh failed')
        
        success, event_id, error = calendar_service.create_calendar_event(
            refresh_token='invalid_token',
            event_title='Meeting',
            event_time='2025-12-15T10:00:00'
        )
        
        assert success is False
        assert error is not None


class TestCheckCalendarConflicts:
    """Test calendar conflict detection"""
    
    @patch('app.services.calendar_service.CalendarService.refresh_access_token')
    @patch('app.services.calendar_service.build')
    def test_check_calendar_conflicts_no_conflicts(self, mock_build, mock_refresh, calendar_service):
        """Test checking calendar when no conflicts exist"""
        mock_refresh.return_value = 'access_token'
        
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.events().list().execute.return_value = {'items': []}
        
        has_conflicts, events, error = calendar_service.check_calendar_conflicts(
            refresh_token='refresh_token_xyz',
            start_time='2025-12-15T10:00:00Z',
            end_time='2025-12-15T11:00:00Z'
        )
        
        assert has_conflicts is False
        assert events == []
        assert error is None
    
    @patch('app.services.calendar_service.CalendarService.refresh_access_token')
    @patch('app.services.calendar_service.build')
    def test_check_calendar_conflicts_found(self, mock_build, mock_refresh, calendar_service):
        """Test checking calendar when conflicts exist"""
        mock_refresh.return_value = 'access_token'
        
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.events().list().execute.return_value = {
            'items': [
                {
                    'summary': 'Existing Meeting',
                    'start': {'dateTime': '2025-12-15T10:30:00'},
                    'end': {'dateTime': '2025-12-15T11:30:00'},
                    'id': 'event_123'
                }
            ]
        }
        
        has_conflicts, events, error = calendar_service.check_calendar_conflicts(
            refresh_token='refresh_token_xyz',
            start_time='2025-12-15T10:00:00Z',
            end_time='2025-12-15T11:00:00Z'
        )
        
        assert has_conflicts is True
        assert len(events) == 1
        assert events[0]['title'] == 'Existing Meeting'
        assert error is None
    
    @patch('app.services.calendar_service.CalendarService.refresh_access_token')
    @patch('app.services.calendar_service.build')
    def test_check_calendar_conflicts_api_error(self, mock_build, mock_refresh, calendar_service):
        """Test handling of API errors during conflict check"""
        mock_refresh.return_value = 'access_token'
        
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        from googleapiclient.errors import HttpError
        mock_http_resp = MagicMock()
        mock_http_resp.status = 500
        mock_service.events().list().execute.side_effect = HttpError(
            mock_http_resp,
            b'Server error'
        )
        
        has_conflicts, events, error = calendar_service.check_calendar_conflicts(
            refresh_token='refresh_token_xyz',
            start_time='2025-12-15T10:00:00Z',
            end_time='2025-12-15T11:00:00Z'
        )
        
        assert has_conflicts is False
        assert events == []
        assert error is not None


class TestGetCalendarServiceSingleton:
    """Test calendar service singleton"""
    
    @patch.dict(os.environ, {
        'GOOGLE_CLIENT_ID': 'test_id',
        'GOOGLE_CLIENT_SECRET': 'test_secret'
    })
    def test_get_calendar_service_singleton(self):
        """Test that get_calendar_service returns same instance"""
        # Import fresh to reset module state
        import importlib
        from app.services import calendar_service as cs_module
        
        # Reset the singleton
        cs_module._calendar_service = None
        
        service1 = cs_module.get_calendar_service()
        service2 = cs_module.get_calendar_service()
        
        assert service1 is service2
