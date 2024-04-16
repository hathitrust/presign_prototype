from cryptography.hazmat.primitives import serialization
import time
from pathlib import Path

import pytest
from jose import jwt

from server.app import app  # Import the Flask app

# Helper function to generate private and public keys for testing
def generate_keys(path):
    print(path)
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    # Generate a private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    # Get the public key
    public_key = private_key.public_key()

    # Serialize the private key
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Write the private key to a file
    key_dir = Path(path).resolve().parent.parent
    private_key_path = key_dir / "private.pem"
    with open(private_key_path, "wb") as key_file:
        key_file.write(pem)

    # Serialize the public key
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # Write the public key to a file
    public_key_path = key_dir / "public.pem"
    with open(public_key_path, "wb") as key_file:
        key_file.write(pem)

    return private_key_path, public_key_path

# Helper function to generate tokens for testing
def generate_token(private_key_path):

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

# Create the keys before running the tests
@pytest.fixture(scope='session')
def keys(tmp_path_factory):
    path = tmp_path_factory.mktemp("keys")
    private_key_path, public_key_path = generate_keys(path)
    return private_key_path, public_key_path

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

def test_valid_request(client, keys):

    # Load the public key into the app
    with open(keys[1], "rb") as key_file:
        app.config['public_key'] = serialization.load_pem_public_key(
            key_file.read()
        )

    # Test the endpoint with a valid token
    valid_token = generate_token(keys[0])
    response = client.post(
        '/api/endpoint',
        headers={"Authorization": f"Bearer {valid_token}"},
        json={"data": "This is a test."}
    )

    assert response.status_code == 200
    assert 'Success' in response.data.decode()
