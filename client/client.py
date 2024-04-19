from jose import jwt
import time
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import requests
from pathlib import Path
import sys

import argparse
import yaml


def generate_jwt_token(sub, email, exp, private_key):
    payload = {
        "sub": sub,
        "email": email,
        "iat": int(time.time()),
        "exp": int(time.time()) + exp
    }

    # Create the JWT token using RS256 algorithm
    token = jwt.encode(payload, private_key, algorithm="RS256")

    return token

def upload_file(file_path, url):
    # Upload the file to the presigned URL
    with open(file_path, "rb") as file:
        response = requests.put(url, data=file)
    
    if response.status_code != 200:
        print(response.status_code, file=sys.stderr)
        print(response.text, file=sys.stderr)
        return False

    print("File uploaded successfully", file=sys.stderr)
    return True

    
def request_presigned_url(data, token, server_url):
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.post(server_url, headers=headers, json=data)
 
    if response.status_code != 200:
        print(response.status_code, file=sys.stderr)
        print(response.text, file=sys.stderr)
        return

    return response.text
    

def main():
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)

    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="File to be uploaded", required=True)
    args = parser.parse_args()

    # Get private key
    private_key_path = Path(config["key_dir"]) / "private.pem"
    
    with open(private_key_path, "rb") as key_file:
        private_key = key_file.read()

    # Create the headers
    token = generate_jwt_token(
        config["contrib_id"],
        config["contrib_email"],
        config["exp"],
        private_key,
    )

    data = {"file": args.file}

    url = request_presigned_url(data, 
                                token, 
                                config['server_url'])

    result = upload_file(args.file, url)

    if not result:
        sys.exit(1)
    else:
        sys.exit(0)



if __name__ == "__main__":
    main()
