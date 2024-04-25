import argparse
import os
import sys
from pathlib import Path

import requests
import yaml

import lib.key_helper as kh


def upload_file(file_path, url):
    

    # Check if file has any content
    if os.path.getsize(file_path) == 0:
        response = requests.put(url)
    else:
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
    

    presigned_url = response.json()['presigned_url']


    return presigned_url
    

def main():
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)

    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="File to be uploaded", required=True)
    args = parser.parse_args()

    # Get private key
    private_key_path = Path(config["private_key_path"])

    with open(private_key_path, "rb") as key_file:
        private_key = key_file.read()

    # Create the headers
    token = kh.generate_jwt_token(
        config["user"],
        config["email"],
        private_key,
        config["jwt_expiration"],
    )

    # Create body with file and user (server links user to public key)
    data = {"file": args.file, "user": config["user"]}

    url = request_presigned_url(data, 
                                token, 
                                config['server_url'])

    if not url:
        sys.exit(1)

    result = upload_file(args.file, url)

    if not result:
        sys.exit(1)
    else:
        sys.exit(0)



if __name__ == "__main__":
    main()
