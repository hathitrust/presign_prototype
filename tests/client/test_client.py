import pytest
from unittest.mock import patch, mock_open, MagicMock
from client.client import generate_jwt_token, upload_file, request_presigned_url, main
import sys
import time

def test_generate_jwt_token():
    # Setup: Generate or use a fixed private key. Here, we use an RSA key for RS256.
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization
    import jose.jwt as jwt

    # Generate a new private RSA key.
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # Convert private key to PEM format for use with jwt.encode.
    pem = private_key.private_bytes(
      encoding=serialization.Encoding.PEM,
      format=serialization.PrivateFormat.TraditionalOpenSSL,
      encryption_algorithm=serialization.NoEncryption()
    )

    # Current time for setting issued at and expiration times
    current_time = int(time.time())

    # Use the function to generate a JWT
    token = generate_jwt_token('123', 'user@example.com', 3600, pem)

    # Decode the token without verification just to check payload correctness
    decoded = jwt.decode(token, pem, algorithms=['RS256'], options={"verify_signature": False})

    # Check that the decoded information matches what we expect
    assert decoded['sub'] == '123'
    assert decoded['email'] == 'user@example.com'
    assert decoded['iat'] == current_time
    assert decoded['exp'] == current_time + 3600

def test_upload_file():
    with patch('builtins.open', mock_open(read_data="data")) as mock_file:
        with patch('client.client.requests.put') as mock_put:
            mock_put.return_value.status_code = 200
            result = upload_file("fake_path", "http://fakeurl.com")
            assert result is True
            mock_file.assert_called_once_with("fake_path", "rb")

def test_upload_file_failure():
    with patch('builtins.open', mock_open(read_data="data")) as mock_file:
        with patch('client.client.requests.put') as mock_put:
            mock_put.return_value = MagicMock(status_code=404, text='Not Found')
            result = upload_file("fake_path", "http://fakeurl.com")
            assert result is False

def test_request_presigned_url():
    with patch('client.client.requests.post') as mock_post:
        mock_post.return_value = MagicMock(status_code=200, text='http://fakeurl.com')
        url = request_presigned_url({'file': 'myfile'}, 'mock_token', 'http://server_url.com')
        assert url == 'http://fakeurl.com'
        mock_post.assert_called_once()

def test_request_presigned_url_failure():
    with patch('client.client.requests.post') as mock_post:
        mock_post.return_value = MagicMock(status_code=500, text='Server Error')
        url = request_presigned_url({'file': 'myfile'}, 'mock_token', 'http://server_url.com')
        assert url is None

# todo: overmocking, refactor to use a fixture
def test_client_main_function(tmpdir, capsys, jwt_encode_mock):
    test_file_path = str(tmpdir.join("dummy_file.txt"))
    sys.argv = ["client.py", "--file", test_file_path]

    with patch('builtins.open', mock_open(read_data='private_key_data')), \
         patch('client.client.yaml.safe_load', return_value={
             'key_dir': 'keys',
             'contrib_id': '123',
             'contrib_email': 'email@example.com',
             'exp': 3600,
             'server_url': 'http://example.com'
         }), \
         patch('client.client.requests.post') as mock_post, \
         patch('client.client.requests.put') as mock_put, \
         patch('sys.exit') as mock_exit:

        mock_post.return_value = MagicMock(status_code=200, text='http://fakeurl.com')
        mock_put.return_value = MagicMock(status_code=200)  # Simulate successful upload
        mock_exit.side_effect = SystemExit(0)  

        with pytest.raises(SystemExit) as pytest_e:
          main()

        # Capture the output and check behavior
        out, err = capsys.readouterr()

        # Check for success message in the stderr
        assert "File uploaded successfully" in err, "Upload should be successful and confirm via stderr"

@pytest.fixture
def jwt_encode_mock():
    with patch('client.client.jwt.encode', return_value='mocked_token') as mock:
        yield mock

if __name__ == "__main__":
    pytest.main()