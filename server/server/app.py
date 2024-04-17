from pathlib import Path

import boto3
import yaml
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from flask import Flask, request
from jose import jwt

app = Flask(__name__)

# create path for the config file
config_path = Path(__file__).parent / "config.yaml"

with open(config_path, "r") as config_file:
    config = yaml.safe_load(config_file)

# Specify the file name that will appear in the bucket once uploaded
object_name = "test.txt"

# URL expiration time in seconds
url_expiration = 3600  # 1 hour

# Create a Boto3 session with the specified profile
session = boto3.Session(profile_name=config["profile"], region_name="us-west-2")

# Create an S3 client from the session
s3_client = session.client("s3")

key_dir = Path(config["key_dir"])

public_key_path = key_dir / "public.pem"

with open(public_key_path, "rb") as key_file:
    app.config["public_key"] = serialization.load_pem_public_key(key_file.read())

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

# Function to encrypt a message
def encrypt_message(message, public_key):
    return public_key.encrypt(
        message.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )


@app.route("/api/endpoint", methods=["POST"])
def handle_request():
    auth_header = request.headers.get("Authorization")
    if auth_header:
        try:
            token = auth_header.split(" ")[1]
            jwt_payload = jwt.decode(
                token, app.config["public_key"], algorithms=["RS256"]
            )
            # Proceed with the request, payload contains the decoded JWT
            #print(auth_header)
            print(jwt_payload)
            # print the post request data
            print(request.json)

            # Return a presigned url
            presigned_url = generate_presigned_url(
                config["bucket_name"], object_name, url_expiration
            )

            # encrypted_url = encrypt_message(presigned_url, app.config["public_key"])
            # return encrypted_url.hex(), 200

            return presigned_url, 200
        except jwt.JWTError:
            return "Invalid token", 401
    else:
        return "Missing token", 401



if __name__ == "__main__":
    app.run()