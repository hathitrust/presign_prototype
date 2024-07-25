import re
from pathlib import Path

import os
import boto3
import yaml
from flask import Flask, request
from jose import jwt

bucket_name = os.getenv("BUCKET_NAME")
folder = os.getenv("FOLDER")
profile = os.getenv("PROFILE")
region = os.getenv("REGION")

URL_EXPIRATION = int(os.getenv("URL_EXPIRATION", 3600))
TOKEN_EXPIRATION = int(os.getenv("TOKEN_EXPIRATION", 3600))
MAX_FILE_NAME_LENGTH = int(os.getenv("MAX_FILE_NAME_LENGTH", 60))

from key_helper import PublicKeyManager

app = Flask(__name__)

# Create a Boto3 session with the specified profile
session = boto3.Session()

# Create an S3 client from the session
s3_client = session.client("s3")

# Directory containing public keys
key_dir = Path("keys")

# Initialize the public key manager
key_manager = PublicKeyManager(key_dir)

def is_valid_filename(filename):
    pattern = re.compile(r'^[a-zA-Z0-9\-_\.]+$')
    return bool(pattern.match(filename))


def generate_presigned_url(bucket_name, object_name, expiration):
    """
    Generate a pre-signed URL to upload a file to an S3 bucket.
    """
    try:
        response = s3_client.generate_presigned_url(
            "put_object",
            Params={"Bucket": bucket_name, "Key": object_name},
            ExpiresIn=expiration
        )
        return response
    except Exception as e:
        print(f"Error generating pre-signed URL: {e}")
        return None

@app.route("/api/endpoint", methods=["POST"])
def handle_request():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return {"error": "Missing authorization header"}, 401

    token_parts = auth_header.split(" ")
    if len(token_parts) != 2 or token_parts[0] != "Bearer":
        return {"error": "Invalid authorization header format"}, 401
    token = token_parts[1]

    user = request.json.get("user")
    if not user:
        return {"error": "Missing 'user' in request body"}, 400

    public_key = key_manager.get_key(user)
    if not public_key:
        return {"error": "Public key not found for user"}, 404

    try:
        jwt_payload = jwt.decode(token, public_key, algorithms=["RS256"])
    except jwt.JWTError:
        return {"error": "Invalid or expired token"}, 401
    
    if (jwt_payload["exp"] - jwt_payload["iat"]) > TOKEN_EXPIRATION:
        return {"error": "Token has expired for server time limit"}, 401
    
    file_name = request.json.get("file")
    if not file_name:
        return {"error": "File name not provided"}, 400
    
    if len(file_name) > MAX_FILE_NAME_LENGTH:
        return {"error": "File name is too long"}, 400

    if not is_valid_filename(file_name):
        return {"error": "File name contains invalid characters"}, 400

    object_name = f"{folder}/{user}/{file_name}"
    presigned_url = generate_presigned_url(bucket_name, object_name, URL_EXPIRATION)
    if not presigned_url:
        return {"error": "Error generating pre-signed URL"}, 500

    return {"presigned_url": presigned_url}, 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)

