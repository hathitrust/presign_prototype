import pytest
from unittest.mock import patch, mock_open, MagicMock
from client.app import upload_file, request_presigned_url, main
import lib.key_helper as kh
import sys


def test_upload_file():
    with patch('builtins.open', mock_open(read_data="data")) as mock_file:
        with patch('client.app.requests.put') as mock_put:
            mock_put.return_value.status_code = 200
            result = upload_file("fake_path", "http://fakeurl.com")
            assert result is True
            mock_file.assert_called_once_with("fake_path", "rb")

def test_upload_file_failure():
    with patch('builtins.open', mock_open(read_data="data")) as mock_file:
        with patch('client.app.requests.put') as mock_put:
            mock_put.return_value = MagicMock(status_code=404, text='Not Found')
            result = upload_file("fake_path", "http://fakeurl.com")
            assert result is False
            mock_file.assert_called_once_with("fake_path", "rb")

def test_request_presigned_url():
    # Prepare the mock response object to return from requests.post
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'presigned_url': 'http://fakeurl.com'}

    with patch('client.app.requests.post', return_value=mock_response) as mock_post:
        # Call the function under test
        url = request_presigned_url({'file': 'myfile'}, 'mock_token', 'http://server_url.com')

        # Assert that the function returns the correct URL
        assert url == 'http://fakeurl.com', "The URL returned from request_presigned_url did not match the expected URL."
        mock_post.assert_called_once()

def test_request_presigned_url_failure():
    with patch('client.app.requests.post') as mock_post:
        mock_post.return_value = MagicMock(status_code=500, text='Server Error')
        url = request_presigned_url({'file': 'myfile'}, 'mock_token', 'http://server_url.com')
        assert url is None
        mock_post.assert_called_once()

# todo: refactor to use a fixture instead of extreme mocking
def test_client_main_function(tmpdir, capsys):
    test_file_path = str(tmpdir.join("dummy_file.txt"))
    private_key_path = str(tmpdir.join("private.pem"))
    # create a dummy file in tmpdir
    with open(test_file_path, "w") as f:
        f.write("\{file: 'dummy_file.txt', user: 'test'\}")
    with open(private_key_path, "wb") as f:
        f.write(kh.generate_rsa_pem_key_pair()[0])
    sys.argv = ["client.py", "--file", test_file_path]

    with patch('client.app.yaml.safe_load', return_value={
             'private_key_path': private_key_path,
             'user': 'test',
             'email': 'email@example.com',
             'jwt_expiration': 3600,
             'server_url': 'http://example.com'
         }), \
         patch('client.app.requests.post') as mock_post, \
         patch('client.app.requests.put') as mock_put:

        mock_post.return_value = MagicMock(status_code=200, text='http://fakeurl.com')
        mock_put.return_value = MagicMock(status_code=200)  # Simulate successful upload

        with pytest.raises(SystemExit) as pytest_e:
            main()

        # Capture the output and check behavior
        out, err = capsys.readouterr()

        # Check for success message in the stderr
        assert "File uploaded successfully" in err, "Upload should be successful and confirm via stderr"

if __name__ == "__main__":
    pytest.main()