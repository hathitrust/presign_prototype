import os
import time

import jose.jwt as jwt
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa


class PublicKeyManager:
    def __init__(self, key_directory):
        self.keys = {}
        self.load_keys(key_directory)

    def load_keys(self, key_directory):
        for key_path in key_directory.glob("*_public.pem"):
            user = key_path.stem.split("_")[0]
            with open(key_path, "rb") as key_file:
                public_key = serialization.load_pem_public_key(key_file.read())
                self.keys[user] = public_key

    def get_key(self, user):
        return self.keys.get(user)
    

def generate_jwt_token(sub, email, private_key, exp=3600):
    payload = {
        "sub": sub,
        "email": email,
        "iat": int(time.time()),
        "exp": int(time.time()) + exp
    }

    # Create the JWT token using RS256 algorithm
    token = jwt.encode(payload, private_key, algorithm="RS256")

    return token

# Helper function to generate private and public keys
def generate_rsa_pem_key_pair():

    # Generate a private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    # Get the public key
    public_key = private_key.public_key()

    # Serialize the private key
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Serialize the public key
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_pem, public_pem


def save_private_key(pem, filename):

    with open(filename, 'wb') as f:
        f.write(pem)
    # Set file permissions to read/write for the owner only.
    os.chmod(filename, 0o600)

def save_public_key(pem, filename):
    with open(filename, 'wb') as f:
        f.write(pem)
    # Set file permissions to read/write for the owner and read for others.
    os.chmod(filename, 0o644)


def encrypt_with_public_key(public_key, message):
    ciphertext = public_key.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext

def decrypt_with_private_key(private_key, ciphertext):
    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return plaintext
