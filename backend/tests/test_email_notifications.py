"""
Test email notification functionality
Run with: pytest tests/test_email_notifications.py -v

This test uses test_email as both the organizer and invitee,
so you'll receive both invitation emails and response notification emails.
"""
import pytest
from app import create_app


@pytest.fixture
def client():
    """Create test client (fake browser for making API requests)."""
    app = create_app('TestingConfig')
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client


@pytest.fixture
def test_email():
    """Your email for testing - you'll receive actual emails!"""
    return "eventease.cs222@gmail.com"


@pytest.fixture
def sample_event_data(test_email):
    """Sample event data - you are the organizer."""
    return {
        "title": "Test Event - Email Notification",
        "description": "Testing email notifications",
        "organizer": "Test Organizer",
        "organizer_email": test_email,  # You'll get response notifications
        "location": "Siebel Center",
        "proposed_times": ["2025-11-15T14:00:00"],
        "attendees": []
    }


def test_invitation_email_flow(client, sample_event_data, test_email):
    """
    Test the complete invitation flow with real email sending.
    
    What this test does:
    1. Creates an event (you as organizer)
    2. Registers you as a user (or uses existing account)
    3. Sends invitation to you → YOU GET EMAIL #1
    4. Retrieves your invitations
    5. Accepts the invitation → YOU GET EMAIL #2 (notification to organizer)
    
    Expected emails:
    - Invitation email to: test_email
    - Response notification to: test_email (as organizer)
    """
    # Step 1: Create event
    response = client.post('/api/events', json=sample_event_data)
    assert response.status_code == 201, f"Failed to create event: {response.json}"
    event = response.json['event']
    event_id = event['_id']
    print(f"\n- Created event: {event['title']} (ID: {event_id})")
    
    # Step 2: Register user (or 409 if already exists)
    user_data = {
        "email": test_email,
        "password": "password123",
        "name": "Test User"
    }
    response = client.post('/api/users/register', json=user_data)
    assert response.status_code in [201, 409], f"Unexpected status: {response.status_code}"
    if response.status_code == 201:
        print(f"- Registered new user: {test_email}")
    else:
        print(f"-  User already exists: {test_email}")
    
    # Step 3: Send invitation (THIS TRIGGERS EMAIL #1)
    response = client.post(
        f'/api/events/{event_id}/invite',
        json={"emails": [test_email]}
    )
    assert response.status_code == 200, f"Failed to send invitation: {response.json}"
    result = response.json
    assert result['success'] is True
    assert test_email in result['invited']
    print(f"- Invitation sent! Check your inbox: {test_email}")
    print(f"- EMAIL #1: Invitation to '{event['title']}'")
    
    # Step 4: Get your invitations
    response = client.get(f'/api/invitations?email={test_email}')
    assert response.status_code == 200
    result = response.json
    assert result['success'] is True
    assert len(result['invitations']) > 0
    invitation = result['invitations'][0]
    print(f"- Retrieved invitation: {invitation['event']['title']}")
    
    # Step 5: Accept the invitation (THIS TRIGGERS EMAIL #2)
    response = client.post(
        f'/api/invitations/{invitation["event_id"]}/respond',
        json={
            "email": test_email,
            "response": "accepted"
        }
    )
    assert response.status_code == 200, f"Failed to respond: {response.json}"
    result = response.json
    assert result['success'] is True
    assert result['response'] == 'accepted'
    print("- Accepted invitation!")
    print(f"- EMAIL #2: Response notification to organizer ({test_email})")
    
    print(f"\n{'='*60}")
    print(f"- TEST COMPLETE - Check your inbox at: {test_email}")
    print("   You should have received 2 emails:")
    print("   1. Invitation to the event")
    print("   2. Notification that you (as organizer) accepted")
    print(f"{'='*60}\n")


def test_invite_nonexistent_user(client, sample_event_data):
    """Test that inviting a non-existent user doesn't crash."""
    # Create event
    response = client.post('/api/events', json=sample_event_data)
    event_id = response.json['event']['_id']
    
    # Try to invite non-existent user
    response = client.post(
        f'/api/events/{event_id}/invite',
        json={"emails": ["nonexistent@example.com"]}
    )
    assert response.status_code == 200
    result = response.json
    assert "nonexistent@example.com" in result['not_found']
    print("- Correctly handled non-existent user")


def test_invalid_invitation_response(client, sample_event_data, test_email):
    """Test that invalid responses are rejected."""
    # Create event
    response = client.post('/api/events', json=sample_event_data)
    event_id = response.json['event']['_id']
    
    # Register user
    user_data = {"email": test_email, "password": "test123", "name": "Test"}
    client.post('/api/users/register', json=user_data)
    
    # Send invitation
    client.post(f'/api/events/{event_id}/invite', json={"emails": [test_email]})
    
    # Try invalid response
    response = client.post(
        f'/api/invitations/{event_id}/respond',
        json={"email": test_email, "response": "maybe"}  # Invalid!
    )
    assert response.status_code == 400
    assert 'must be "accepted" or "declined"' in response.json['error']
    print("- Correctly rejected invalid response")
