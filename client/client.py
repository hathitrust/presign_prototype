from jose import jwt
import time
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import requests
from pathlib import Path
import sys

import argparse
import yaml


def create_headers(contrib_id, contrib_email, exp, private_key):
    payload = {
        "sub": contrib_id,
        "email": contrib_email,
        "iat": int(time.time()),
        "exp": int(time.time()) + exp
    }

    # Create the JWT token using RS256 algorithm
    token = jwt.encode(payload, private_key, algorithm="RS256")

    headers = {
        "Authorization": f"Bearer {token}"
    }

    return headers

# Function to decrypt a message
def decrypt_message(encrypted_message, private_key):
    return private_key.decrypt(
        bytes.fromhex(encrypted_message),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

def upload_file(file_path, url):
    # Upload the file to the presigned URL
    with open(file_path, "rb") as file:
        response = requests.put(url, data=file)
    
    if response.status_code != 200:
        print(response.status_code, file=sys.stderr)
        print(response.text, file=sys.stderr)
        return

    print("File uploaded successfully")

    
def request_presigned(filename, config):
    # Get private key
    private_key_path = Path(config["key_dir"]) / "private.pem"
    
    with open(private_key_path, "rb") as key_file:
        private_key = key_file.read()

    # Create the headers
    headers = create_headers(
        config["contrib_id"],
        config["contrib_email"],
        config["exp"],
        private_key,
    )
        
    # Make the HTTP POST request with the JWT in the Authorization header
    data = {"file": filename, "stream": "uni1"}
    response = requests.post("http://127.0.0.1:5000/api/endpoint", headers=headers, json=data)
 
    if response.status_code != 200:
        print(response.status_code, file=sys.stderr)
        print(response.text, file=sys.stderr)
        return

    # Decrypt the URL
    # encrypted_url = response.text
    # url = decrypt_message(encrypted_url, private_key).decode("utf-8")

    return response.text
    

def main():
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)

    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="File to be uploaded", required=True)
    args = parser.parse_args()

    url = request_presigned(args.file, config)

    upload_file(args.file, url)


if __name__ == "__main__":
    main()
