import time
from pathlib import Path

import pytest
from jose import jwt

from server.app import app  # Import the Flask app


# Helper function to generate tokens for testing
def generate_token():
    key_dir = Path(__file__).resolve().parent.parent
    private_key_path = key_dir / "private.pem"

    with open(private_key_path, "rb") as key_file:
        private_key = key_file.read()

    # User information
    contrib_id = "UNV"
    contrib_email = "user@uni.com"

    # Create a sample payload
    payload = {
        "sub": contrib_id,
        "email": contrib_email,
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600
    }

    # Generate a token
    token = jwt.encode(payload, private_key, algorithm='RS256')
    return token

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_missing_token(client):
    # Test the endpoint without Authorization header
    response = client.post('/api/endpoint')
    assert response.status_code == 401
    assert 'Missing token' in response.data.decode()

def test_invalid_token(client):
    # Test the endpoint with an invalid token
    response = client.post(
        '/api/endpoint',
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    assert 'Invalid token' in response.data.decode()

def test_valid_request(client):
    # Test the endpoint with a valid token
    valid_token = generate_token()
    response = client.post(
        '/api/endpoint',
        headers={"Authorization": f"Bearer {valid_token}"},
        json={"data": "This is a test."}
    )

    assert response.status_code == 200
    assert 'Success' in response.data.decode()
