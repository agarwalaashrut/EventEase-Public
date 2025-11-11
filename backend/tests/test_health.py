"""Test health check endpoint."""
import pytest
from app import create_app


@pytest.fixture
def client():
    """Create test client."""
    app = create_app('TestingConfig')
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client


def test_health_check(client):
    """Test GET /health returns status ok."""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json == {'status': 'ok'}
