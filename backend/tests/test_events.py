"""
Test event CRUD operations
Run with: pytest tests/test_events.py -v
"""
import pytest
from app import create_app
from bson.objectid import ObjectId


@pytest.fixture
def client():
    """Create test client (fake browser for making API requests)."""
    app = create_app('TestingConfig')
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_event_data():
    """Sample event data for testing."""
    return {
        "title": "Team Standup Meeting",
        "description": "Weekly team sync",
        "organizer": "Alice Johnson",
        "organizer_email": "alice@example.com",
        "location": "Siebel Center Room 1404",
        "proposed_times": ["2025-12-10T10:00:00", "2025-12-10T14:00:00"],
        "attendees": []
    }


def test_create_event_success(client, sample_event_data):
    """Test creating a valid event returns 201 and event data."""
    response = client.post('/api/events', json=sample_event_data)
    
    assert response.status_code == 201
    data = response.json
    assert data['success'] is True
    assert 'event' in data
    assert data['event']['title'] == sample_event_data['title']
    assert data['event']['organizer_email'] == sample_event_data['organizer_email']
    assert '_id' in data['event']


def test_create_event_missing_fields(client):
    """Test creating event without required fields returns 400."""
    invalid_data = {
        "title": "Incomplete Event"
        # Missing organizer_email and location
    }
    
    response = client.post('/api/events', json=invalid_data)
    
    assert response.status_code == 400
    data = response.json
    assert data['success'] is False
    assert 'error' in data


def test_get_all_events(client, sample_event_data):
    """Test retrieving all events returns 200 and events list."""
    # Create an event first
    create_response = client.post('/api/events', json=sample_event_data)
    assert create_response.status_code == 201
    
    # Get all events
    response = client.get('/api/events')
    
    assert response.status_code == 200
    data = response.json
    assert data['success'] is True
    assert 'events' in data
    assert 'count' in data
    assert data['count'] >= 1
    assert isinstance(data['events'], list)


def test_get_event_by_id(client, sample_event_data):
    """Test retrieving a single event by ID returns 200 and event data."""
    # Create an event first
    create_response = client.post('/api/events', json=sample_event_data)
    event_id = create_response.json['event']['_id']
    
    # Get the event by ID
    response = client.get(f'/api/events/{event_id}')
    
    assert response.status_code == 200
    data = response.json
    assert data['success'] is True
    assert 'event' in data
    assert data['event']['_id'] == event_id
    assert data['event']['title'] == sample_event_data['title']


def test_get_nonexistent_event(client):
    """Test retrieving a nonexistent event returns 404."""
    fake_id = str(ObjectId())
    
    response = client.get(f'/api/events/{fake_id}')
    
    assert response.status_code == 404
    data = response.json
    assert data['success'] is False
    assert 'error' in data


def test_update_event(client, sample_event_data):
    """Test updating an event returns 200 and updated data."""
    # Create an event first
    create_response = client.post('/api/events', json=sample_event_data)
    event_id = create_response.json['event']['_id']
    
    # Update the event
    update_data = {
        "title": "Updated Team Standup",
        "location": "Online - Zoom"
    }
    response = client.put(f'/api/events/{event_id}', json=update_data)
    
    assert response.status_code == 200
    data = response.json
    assert data['success'] is True
    assert data['event']['title'] == update_data['title']
    assert data['event']['location'] == update_data['location']


def test_delete_event(client, sample_event_data):
    """Test deleting an event returns 200."""
    # Create an event first
    create_response = client.post('/api/events', json=sample_event_data)
    event_id = create_response.json['event']['_id']
    
    # Delete the event
    response = client.delete(f'/api/events/{event_id}')
    
    assert response.status_code == 200
    data = response.json
    assert data['success'] is True
    
    # Verify it's deleted by trying to get it
    get_response = client.get(f'/api/events/{event_id}')
    assert get_response.status_code == 404
