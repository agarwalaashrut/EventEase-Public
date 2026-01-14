"""
Test voting functionality with calendar integration
Run with: pytest tests/test_voting.py -v
"""
import pytest
from unittest.mock import patch, MagicMock
from app import create_app
from bson.objectid import ObjectId
from datetime import datetime


@pytest.fixture
def client():
    """Create test client."""
    app = create_app('TestingConfig')
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_event():
    """Sample event for voting tests"""
    return {
        "title": "Team Meeting",
        "description": "Weekly sync",
        "organizer": "Alice",
        "organizer_email": "alice@example.com",
        "location": "Zoom",
        "proposed_times": ["2025-12-15T10:00:00", "2025-12-15T14:00:00", "2025-12-16T10:00:00"],
        "attendees": ["bob@example.com", "charlie@example.com"]
    }


class TestSubmitVote:
    """Test voting endpoint"""
    
    @patch('app.routes.voting.get_db')
    def test_submit_vote_success(self, mock_get_db, client, sample_event):
        """Test submitting a vote successfully"""
        # Create event first
        event_id = str(ObjectId())
        
        mock_db = MagicMock()
        mock_events_collection = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.__getitem__.return_value = {'Events': mock_events_collection}
        
        # Mock event document
        sample_event['_id'] = ObjectId(event_id)
        sample_event['votes'] = {}
        mock_events_collection.find_one.return_value = sample_event
        
        vote_data = {
            'user_email': 'bob@example.com',
            'time_slot_index': 0
        }
        
        response = client.post(f'/api/events/{event_id}/vote', json=vote_data)
        
        assert response.status_code == 200
        data = response.json
        assert data['success'] is True
        assert 'votes' in data
        assert 'tallies' in data
    
    @patch('app.routes.voting.get_db')
    def test_submit_vote_missing_email(self, mock_get_db, client, sample_event):
        """Test submitting vote without user email"""
        event_id = str(ObjectId())
        
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        vote_data = {
            'time_slot_index': 0
            # Missing user_email
        }
        
        response = client.post(f'/api/events/{event_id}/vote', json=vote_data)
        
        assert response.status_code == 400
        data = response.json
        assert data['success'] is False
        assert 'user_email' in data['error'].lower()
    
    @patch('app.routes.voting.get_db')
    def test_submit_vote_invalid_slot_index(self, mock_get_db, client, sample_event):
        """Test submitting vote with invalid time slot index"""
        event_id = str(ObjectId())
        
        mock_db = MagicMock()
        mock_events_collection = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.__getitem__.return_value = {'Events': mock_events_collection}
        
        sample_event['_id'] = ObjectId(event_id)
        mock_events_collection.find_one.return_value = sample_event
        
        vote_data = {
            'user_email': 'bob@example.com',
            'time_slot_index': 10  # Invalid index
        }
        
        response = client.post(f'/api/events/{event_id}/vote', json=vote_data)
        
        assert response.status_code == 400
        data = response.json
        assert data['success'] is False
        assert 'invalid' in data['error'].lower()
    
    @patch('app.routes.voting.get_db')
    def test_submit_vote_event_not_found(self, mock_get_db, client):
        """Test submitting vote for non-existent event"""
        event_id = str(ObjectId())
        
        mock_db = MagicMock()
        mock_events_collection = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.__getitem__.return_value = {'Events': mock_events_collection}
        mock_events_collection.find_one.return_value = None
        
        vote_data = {
            'user_email': 'bob@example.com',
            'time_slot_index': 0
        }
        
        response = client.post(f'/api/events/{event_id}/vote', json=vote_data)
        
        assert response.status_code == 404
        data = response.json
        assert data['success'] is False
        assert 'not found' in data['error'].lower()


class TestGetVotingResults:
    """Test voting results endpoint"""
    
    @patch('app.routes.voting.get_db')
    def test_get_voting_results_success(self, mock_get_db, client, sample_event):
        """Test getting voting results"""
        event_id = str(ObjectId())
        
        mock_db = MagicMock()
        mock_events_collection = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.__getitem__.return_value = {'Events': mock_events_collection}
        
        sample_event['_id'] = ObjectId(event_id)
        sample_event['votes'] = {
            'alice@example.com': 0,
            'bob@example.com': 0,
            'charlie@example.com': 1
        }
        
        mock_events_collection.find_one.return_value = sample_event
        
        response = client.get(f'/api/events/{event_id}/votes')
        
        assert response.status_code == 200
        data = response.json
        assert data['success'] is True
        assert 'votes_by_user' in data
        assert 'votes_by_time_slot' in data
        assert 'popular_time_slots' in data
        assert 'winner' in data
        assert data['total_participants'] == 3
        assert data['total_votes'] == 3
    
    @patch('app.routes.voting.get_db')
    def test_get_voting_results_no_votes(self, mock_get_db, client, sample_event):
        """Test getting results when no votes exist"""
        event_id = str(ObjectId())
        
        mock_db = MagicMock()
        mock_events_collection = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.__getitem__.return_value = {'Events': mock_events_collection}
        
        sample_event['_id'] = ObjectId(event_id)
        sample_event['votes'] = {}
        mock_events_collection.find_one.return_value = sample_event
        
        response = client.get(f'/api/events/{event_id}/votes')
        
        assert response.status_code == 200
        data = response.json
        assert data['success'] is True
        assert data['total_votes'] == 0
        assert data['total_participants'] == 0


class TestFinalizeEvent:
    """Test event finalization with calendar integration"""
    
    @patch('app.routes.voting.get_db')
    @patch('app.routes.voting.get_calendar_service')
    def test_finalize_event_auto_select(self, mock_calendar_service, mock_get_db, client, sample_event):
        """Test finalizing event with auto-selected winner"""
        event_id = str(ObjectId())
        
        mock_db = MagicMock()
        mock_events_collection = MagicMock()
        mock_users_collection = MagicMock()
        
        mock_get_db.return_value = mock_db
        
        def mock_getitem(key):
            if key == 'Events':
                return mock_events_collection
            elif key == 'Users':
                return mock_users_collection
            return MagicMock()
        
        mock_db.__getitem__.side_effect = mock_getitem
        
        sample_event['_id'] = ObjectId(event_id)
        sample_event['votes'] = {
            'alice@example.com': 0,
            'bob@example.com': 0,
            'charlie@example.com': 0
        }
        
        mock_events_collection.find_one.return_value = sample_event
        mock_users_collection.find_one.return_value = None  # Organizer has no calendar
        
        response = client.post(f'/api/events/{event_id}/finalize', json={})
        
        assert response.status_code == 200
        data = response.json
        assert data['success'] is True
        assert 'finalized_time_slot_index' in data
        assert 'finalized_time_slot' in data
        assert data['finalized_time_slot_index'] >= 0
    
    @patch('app.routes.voting.get_db')
    @patch('app.routes.voting.get_calendar_service')
    def test_finalize_event_manual_override(self, mock_calendar_service, mock_get_db, client, sample_event):
        """Test finalizing event with manual time slot override"""
        event_id = str(ObjectId())
        
        mock_db = MagicMock()
        mock_events_collection = MagicMock()
        mock_users_collection = MagicMock()
        
        mock_get_db.return_value = mock_db
        
        def mock_getitem(key):
            if key == 'Events':
                return mock_events_collection
            elif key == 'Users':
                return mock_users_collection
            return MagicMock()
        
        mock_db.__getitem__.side_effect = mock_getitem
        
        sample_event['_id'] = ObjectId(event_id)
        mock_events_collection.find_one.return_value = sample_event
        mock_users_collection.find_one.return_value = None
        
        response = client.post(f'/api/events/{event_id}/finalize', json={'time_slot_index': 1})
        
        assert response.status_code == 200
        data = response.json
        assert data['success'] is True
        assert data['finalized_time_slot_index'] == 1
    
    @patch('app.routes.voting.get_db')
    @patch('app.routes.voting.get_calendar_service')
    def test_finalize_event_with_calendar_sync(self, mock_calendar_service, mock_get_db, client, sample_event):
        """Test event finalization with calendar event creation"""
        event_id = str(ObjectId())
        
        mock_db = MagicMock()
        mock_events_collection = MagicMock()
        mock_users_collection = MagicMock()
        
        mock_get_db.return_value = mock_db
        
        def mock_getitem(key):
            if key == 'Events':
                return mock_events_collection
            elif key == 'Users':
                return mock_users_collection
            return MagicMock()
        
        mock_db.__getitem__.side_effect = mock_getitem
        
        sample_event['_id'] = ObjectId(event_id)
        sample_event['votes'] = {'alice@example.com': 0}
        
        mock_events_collection.find_one.return_value = sample_event
        
        # Organizer has Google Calendar connected
        mock_users_collection.find_one.return_value = {
            '_id': 'organizer_id',
            'email': 'alice@example.com',
            'google_refresh_token': 'refresh_token_xyz'
        }
        
        # Mock calendar service
        mock_service = MagicMock()
        mock_calendar_service.return_value = mock_service
        mock_service.create_calendar_event.return_value = (True, 'google_event_id_123', None)
        
        response = client.post(f'/api/events/{event_id}/finalize', json={})
        
        assert response.status_code == 200
        data = response.json
        assert data['success'] is True
        assert data['calendar']['calendar_event_created'] is True
        assert data['calendar']['calendar_event_id'] == 'google_event_id_123'
        assert data['calendar']['calendar_error'] is None
        
        # Verify calendar service was called
        mock_service.create_calendar_event.assert_called_once()
    
    @patch('app.routes.voting.get_db')
    @patch('app.routes.voting.get_calendar_service')
    def test_finalize_event_calendar_sync_failure(self, mock_calendar_service, mock_get_db, client, sample_event):
        """Test event finalization succeeds even if calendar sync fails"""
        event_id = str(ObjectId())
        
        mock_db = MagicMock()
        mock_events_collection = MagicMock()
        mock_users_collection = MagicMock()
        
        mock_get_db.return_value = mock_db
        
        def mock_getitem(key):
            if key == 'Events':
                return mock_events_collection
            elif key == 'Users':
                return mock_users_collection
            return MagicMock()
        
        mock_db.__getitem__.side_effect = mock_getitem
        
        sample_event['_id'] = ObjectId(event_id)
        sample_event['votes'] = {'alice@example.com': 0}
        
        mock_events_collection.find_one.return_value = sample_event
        mock_users_collection.find_one.return_value = {
            'google_refresh_token': 'refresh_token_xyz'
        }
        
        # Mock calendar service failure
        mock_service = MagicMock()
        mock_calendar_service.return_value = mock_service
        mock_service.create_calendar_event.return_value = (
            False,
            None,
            'Calendar API error: Permission denied'
        )
        
        response = client.post(f'/api/events/{event_id}/finalize', json={})
        
        # Event finalization should still succeed
        assert response.status_code == 200
        data = response.json
        assert data['success'] is True
        assert data['calendar']['calendar_event_created'] is False
        assert data['calendar']['calendar_error'] is not None
    
    @patch('app.routes.voting.get_db')
    def test_finalize_event_no_votes(self, mock_get_db, client, sample_event):
        """Test finalizing event with no votes fails appropriately"""
        event_id = str(ObjectId())
        
        mock_db = MagicMock()
        mock_events_collection = MagicMock()
        
        mock_get_db.return_value = mock_db
        mock_db.__getitem__.return_value = {'Events': mock_events_collection}
        
        sample_event['_id'] = ObjectId(event_id)
        sample_event['votes'] = {}  # No votes
        
        mock_events_collection.find_one.return_value = sample_event
        
        response = client.post(f'/api/events/{event_id}/finalize', json={})
        
        assert response.status_code == 400
        data = response.json
        assert data['success'] is False
        assert 'no clear winning' in data['error'].lower() or 'no votes' in str(data).lower()
    
    @patch('app.routes.voting.get_db')
    def test_finalize_event_invalid_slot_index(self, mock_get_db, client, sample_event):
        """Test finalizing with invalid time slot index"""
        event_id = str(ObjectId())
        
        mock_db = MagicMock()
        mock_events_collection = MagicMock()
        
        mock_get_db.return_value = mock_db
        mock_db.__getitem__.return_value = {'Events': mock_events_collection}
        
        sample_event['_id'] = ObjectId(event_id)
        mock_events_collection.find_one.return_value = sample_event
        
        response = client.post(f'/api/events/{event_id}/finalize', json={'time_slot_index': 99})
        
        assert response.status_code == 400
        data = response.json
        assert data['success'] is False
        assert 'invalid' in data['error'].lower()
