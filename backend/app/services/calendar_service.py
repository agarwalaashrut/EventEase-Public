"""
Google Calendar Service
Handles OAuth2 authentication and calendar event management
"""
import os
from datetime import datetime, timedelta
from typing import Optional, Tuple
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class CalendarService:
    """Service for managing Google Calendar integration"""
    
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self):
        """Initialize calendar service with Google OAuth configuration"""
        self.client_id = os.getenv('GOOGLE_CLIENT_ID')
        self.client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        self.redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:5001/api/auth/callback')
        
        if not self.client_id or not self.client_secret:
            raise ValueError("Google OAuth credentials not configured in environment")
    
    def get_auth_url(self, state: str) -> str:
        print("ENTERED get_auth_url()")
        """
        Generate Google OAuth authorization URL
        
        Args:
            state: CSRF token for security
            
        Returns:
            OAuth authorization URL
        """
        redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [redirect_uri],
                }
            },
            scopes=self.SCOPES,
            redirect_uri=redirect_uri,
            state=state
        )
        print("GOOGLE_REDIRECT_URI =", repr(redirect_uri))
        auth_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent"
        )

        return auth_url

    
    def get_credentials_from_code(self, authorization_code: str) -> Tuple[dict, str]:
        """
        Exchange authorization code for OAuth credentials
        
        Args:
            authorization_code: Code from OAuth callback
            
        Returns:
            Tuple of (credentials dict with refresh_token, access_token)
        """
        flow = Flow.from_client_config(
            {
                'installed': {
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
                    'token_uri': 'https://oauth2.googleapis.com/token',
                    'redirect_uris': [self.redirect_uri]
                }
            },
            scopes=self.SCOPES,
            redirect_uri=self.redirect_uri
        )
        
        flow.fetch_token(code=authorization_code)
        credentials = flow.credentials
        
        # Return credentials in serializable format
        creds_dict = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        
        return creds_dict, credentials.token
    
    def refresh_access_token(self, refresh_token: str) -> str:
        """
        Refresh expired access token using refresh token
        
        Args:
            refresh_token: OAuth refresh token stored in database
            
        Returns:
            New access token
        """
        credentials = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri='https://oauth2.googleapis.com/token',
            client_id=self.client_id,
            client_secret=self.client_secret
        )
        
        request = Request()
        credentials.refresh(request)
        
        return credentials.token
    
    def create_calendar_event(
        self,
        refresh_token: str,
        event_title: str,
        event_time: str,
        event_description: str = '',
        organizer_email: str = '',
        attendee_emails: list = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Create an event on user's Google Calendar
        
        Args:
            refresh_token: OAuth refresh token for the user
            event_title: Title of the event
            event_time: ISO format datetime string (e.g., "2025-11-14T10:00:00")
            event_description: Event description
            organizer_email: Organizer email (optional)
            attendee_emails: List of attendee emails to invite
            
        Returns:
            Tuple of (success: bool, calendar_event_id: Optional[str], error_message: Optional[str])
        """
        try:
            # Refresh access token
            access_token = self.refresh_access_token(refresh_token)
            
            # Build calendar service
            credentials = Credentials(token=access_token)
            service = build('calendar', 'v3', credentials=credentials)
            
            # Parse event time
            start_time = datetime.fromisoformat(event_time)
            end_time = start_time + timedelta(hours=1)  # Default 1-hour duration
            
            # Build event body
            event_body = {
                'summary': event_title,
                'description': event_description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                }
            }
            
            # Add attendees
            if attendee_emails:
                event_body['attendees'] = [
                    {'email': email} for email in attendee_emails
                ]
            
            # Create event on primary calendar
            event = service.events().insert(
                calendarId='primary',
                body=event_body,
                sendUpdates='eventCreated'  # Send notifications to attendees
            ).execute()
            
            return True, event.get('id'), None
            
        except HttpError as error:
            error_msg = f"Google Calendar API error: {error.resp.status} - {error.content}"
            return False, None, error_msg
        except Exception as error:
            error_msg = f"Error creating calendar event: {str(error)}"
            return False, None, error_msg
    
    def check_calendar_conflicts(
        self,
        refresh_token: str,
        start_time: str,
        end_time: str
    ) -> Tuple[bool, list, Optional[str]]:
        """
        Check for conflicts on user's calendar within a time range
        
        Args:
            refresh_token: OAuth refresh token for the user
            start_time: ISO format datetime string
            end_time: ISO format datetime string
            
        Returns:
            Tuple of (has_conflicts: bool, conflicting_events: list, error_message: Optional[str])
        """
        try:
            # Refresh access token
            access_token = self.refresh_access_token(refresh_token)
            
            # Build calendar service
            credentials = Credentials(token=access_token)
            service = build('calendar', 'v3', credentials=credentials)
            
            # Query for events in time range
            events_result = service.events().list(
                calendarId='primary',
                timeMin=start_time,
                timeMax=end_time,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Filter out all-day events and extract relevant info
            conflicting_events = [
                {
                    'title': event.get('summary', 'Unnamed Event'),
                    'start': event.get('start', {}).get('dateTime'),
                    'end': event.get('end', {}).get('dateTime'),
                    'event_id': event.get('id')
                }
                for event in events
                if 'dateTime' in event.get('start', {})  # Exclude all-day events
            ]
            
            has_conflicts = len(conflicting_events) > 0
            
            return has_conflicts, conflicting_events, None
            
        except HttpError as error:
            error_msg = f"Google Calendar API error: {error.resp.status} - {error.content}"
            return False, [], error_msg
        except Exception as error:
            error_msg = f"Error checking calendar conflicts: {str(error)}"
            return False, [], error_msg


# Singleton instance
_calendar_service = None


def get_calendar_service() -> CalendarService:
    """Get or create calendar service instance"""
    global _calendar_service
    if _calendar_service is None:
        _calendar_service = CalendarService()
    return _calendar_service
