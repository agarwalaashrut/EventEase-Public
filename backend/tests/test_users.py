"""
Test user authentication operations
Run with: pytest tests/test_users.py -v
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
def sample_user_data():
    """Sample user data for testing - uses unique email per test run."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    return {
        "email": f"testuser-{unique_id}@example.com",
        "password": "securepassword123",
        "name": "Test User"
    }


def test_register_new_user(client, sample_user_data):
    """Test registering a new user returns 201 and user data."""
    response = client.post('/api/users/register', json=sample_user_data)
    
    assert response.status_code == 201
    data = response.json
    assert data['success'] is True
    assert 'user' in data
    assert data['user']['email'] == sample_user_data['email']
    assert data['user']['name'] == sample_user_data['name']
    assert 'password_hash' not in data['user']  # Password should not be returned
    assert '_id' in data['user']


def test_register_duplicate_email(client, sample_user_data):
    """Test registering a user with existing email returns 409."""
    # Register user first time
    response1 = client.post('/api/users/register', json=sample_user_data)
    assert response1.status_code == 201
    
    # Try to register with same email
    response2 = client.post('/api/users/register', json=sample_user_data)
    
    assert response2.status_code == 409
    data = response2.json
    assert data['success'] is False
    assert 'error' in data
    assert 'already exists' in data['error'].lower()


def test_register_missing_password(client):
    """Test registering without password returns 400."""
    invalid_data = {
        "email": "nopassword@example.com",
        "name": "No Password User"
        # Missing password field
    }
    
    response = client.post('/api/users/register', json=invalid_data)
    
    assert response.status_code == 400
    data = response.json
    assert data['success'] is False
    assert 'error' in data


def test_register_missing_email(client):
    """Test registering without email returns 400."""
    invalid_data = {
        "password": "somepassword",
        "name": "No Email User"
        # Missing email field
    }
    
    response = client.post('/api/users/register', json=invalid_data)
    
    assert response.status_code == 400
    data = response.json
    assert data['success'] is False
    assert 'error' in data


def test_login_success(client, sample_user_data):
    """Test logging in with valid credentials returns 200 and user data."""
    # Register user first
    register_response = client.post('/api/users/register', json=sample_user_data)
    assert register_response.status_code == 201
    
    # Login with valid credentials
    login_data = {
        "email": sample_user_data['email'],
        "password": sample_user_data['password']
    }
    response = client.post('/api/users/login', json=login_data)
    
    assert response.status_code == 200
    data = response.json
    assert data['success'] is True
    assert 'user' in data
    assert data['user']['email'] == sample_user_data['email']
    assert 'password_hash' not in data['user']


def test_login_invalid_password(client, sample_user_data):
    """Test logging in with wrong password returns 401."""
    # Register user first
    register_response = client.post('/api/users/register', json=sample_user_data)
    assert register_response.status_code == 201
    
    # Try to login with wrong password
    login_data = {
        "email": sample_user_data['email'],
        "password": "wrongpassword"
    }
    response = client.post('/api/users/login', json=login_data)
    
    assert response.status_code == 401
    data = response.json
    assert data['success'] is False
    assert 'error' in data


def test_login_nonexistent_user(client):
    """Test logging in with nonexistent user returns 401."""
    login_data = {
        "email": "doesnotexist@example.com",
        "password": "somepassword"
    }
    
    response = client.post('/api/users/login', json=login_data)
    
    assert response.status_code == 401
    data = response.json
    assert data['success'] is False
    assert 'error' in data


def test_login_missing_credentials(client):
    """Test logging in without email or password returns 400."""
    # Missing email
    response1 = client.post('/api/users/login', json={"password": "test"})
    assert response1.status_code == 400
    
    # Missing password
    response2 = client.post('/api/users/login', json={"email": "test@example.com"})
    assert response2.status_code == 400
