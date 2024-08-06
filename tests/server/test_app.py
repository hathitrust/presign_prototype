from lib.key_helper import generate_jwt_token
from lib.key_helper import generate_rsa_pem_key_pair
from unittest.mock import patch

def test_missing_auth_header(client):
    # Test the endpoint without Authorization header
    response = client.post('/api/endpoint')
    assert response.status_code == 401
    assert 'Missing authorization header' in response.data.decode()

@patch('server.PublicKeyManager.get_key')
def test_invalid_token(mock_get_key, client):
    # Setup mock to return a fake user key
    mock_get_key.return_value = "fake user exists"
    # Test the endpoint with an invalid token
    response = client.post(
        '/api/endpoint',
        headers={"Authorization": "Bearer invalid_token"},
        json={"user": "test_user", "file": "test.txt"}
    )
    assert response.status_code == 401
    assert 'Invalid or expired token' in response.data.decode()

@patch('server.PublicKeyManager.get_key')
@patch('server.s3_client')
def test_valid_request(mock_s3_client, mock_get_key, client):

    # Load private key to generate token
    private_key, public_key = generate_rsa_pem_key_pair()

    # Generate a valid JWT token
    sub= "UNV"
    email = "user@uni.com"
    valid_token = generate_jwt_token(sub, email, private_key) 
    
    # Setup mock to validate the token by public key
    mock_get_key.return_value = public_key

    # Setup mock for the presigned URL generation
    payload = 'http://google.com'
    mock_s3_client.generate_presigned_url.return_value = payload

    # Test the endpoint with a valid token and user identifier
    response = client.post(
        '/api/endpoint',
        headers={"Authorization": f"Bearer {valid_token}"},
        json={"user": "test_user", "file": "test.txt"} 
    )

    assert response.status_code == 200
    assert payload in response.data.decode()
