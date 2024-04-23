from lib.key_helper import generate_jwt_token
import time
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import jose.jwt as jwt

def test_generate_jwt_token():

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
    token = generate_jwt_token('123', 'user@example.com', pem,  3600)

    # Decode the token without verification just to check payload correctness
    decoded = jwt.decode(token, pem, algorithms=['RS256'], options={"verify_signature": False})

    # Check that the decoded information matches what we expect
    assert decoded['sub'] == '123'
    assert decoded['email'] == 'user@example.com'
    assert decoded['iat'] == current_time
    assert decoded['exp'] == current_time + 3600
