from jose import jwt
import time
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
import requests


# Load the private key from the PEM file
with open("private.pem", "rb") as key_file:
    private_key = key_file.read()

# User information
contrib_id = "UNV"
contrib_email = "user@uni.com"

# Generate the JWT
payload = {
    "sub": contrib_id,
    "email": contrib_email,
    "iat": int(time.time()),
    "exp": int(time.time()) + 3600
}

# Create the JWT token using RS256 algorithm
token = jwt.encode(payload, private_key, algorithm="RS256")

# Make the HTTP POST request with the JWT in the Authorization header
headers = {
    "Authorization": f"Bearer {token}"
}
data = {"file": "new_records.xml", "stream": "uni1"}

response = requests.post("http://127.0.0.1:5000/api/endpoint", headers=headers, json=data)

print(response.status_code)
print(response.text)