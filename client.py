import argparse
import os
import sys
from pathlib import Path

import requests
import lib.key_helper as kh

TIMEOUT = 3600

def upload_file(file_path, url):
    # Check if file has any content
    if os.path.exists(file_path) and os.path.getsize(file_path) == 0:
        response = requests.put(url, timeout=TIMEOUT)
    else:
        # Upload the file to the presigned URL
        with open(file_path, "rb") as file:
            response = requests.put(url, data=file, timeout=TIMEOUT)

    if response.status_code != 200:
        print(response.status_code, file=sys.stderr)
        print(response.text, file=sys.stderr)
        return False

    print("File uploaded successfully", file=sys.stderr)
    return True


def request_presigned_url(data, token, server_url):
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.post(server_url, headers=headers, json=data, timeout=TIMEOUT)

    if response.status_code != 200:
        print(response.status_code, file=sys.stderr)
        print(response.text, file=sys.stderr)
        return

    presigned_url = response.json()["presigned_url"]

    return presigned_url


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="File to be uploaded", required=True)
    parser.add_argument("--private_key_path", help="Path to private key", default=os.getenv("PRIVATE_KEYS_PATH"))
    parser.add_argument("--user", help="User", default=os.getenv("USER"))
    parser.add_argument("--email", help="Email", default=os.getenv("EMAIL"))
    parser.add_argument("--jwt_expiration", help="JWT expiration", default=os.getenv("JWT_EXPIRATION"), type=int)
    parser.add_argument("--server_url", help="Server URL", default=os.getenv("SERVER_URL"))
    args = parser.parse_args()

    # Get private key
    private_key_path = Path(args.private_key_path)

    with open(private_key_path, "rb") as key_file:
        private_key = key_file.read()

    # Create the headers
    token = kh.generate_jwt_token(
        args.user,
        args.email,
        private_key,
        args.jwt_expiration,
    )

    # Create body with file and user (server links user to public key)
    data = {"file": args.file, "user": args.user}

    url = request_presigned_url(data, token, args.server_url)

    if not url:
        sys.exit(1)

    result = upload_file(args.file, url)

    if not result:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
