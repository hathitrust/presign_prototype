import pytest

from server import app as flask_app


@pytest.fixture
def server():
    app_instance = flask_app()  # Create an instance of the app
    yield app_instance

@pytest.fixture
def client(server):  # Use the server fixture, which provides the app instance
    server.config['TESTING'] = True
    with server.test_client() as client:
        yield client
