from pathlib import Path

from cryptography.hazmat.primitives import serialization
from flask import Flask, request
from jose import jwt

app = Flask(__name__)

key_dir = Path(__file__).resolve().parent.parent
public_key_path = key_dir / "public.pem"

with open(public_key_path, "rb") as key_file:
    public_key = serialization.load_pem_public_key(
        key_file.read()
    )

@app.route("/api/endpoint", methods=["POST"])
def handle_request():
    auth_header = request.headers.get("Authorization")
    if auth_header:
        try:
            token = auth_header.split(" ")[1]
            jwt_payload = jwt.decode(token, public_key, algorithms=["RS256"])
            # Proceed with the request, payload contains the decoded JWT
            print(auth_header)
            print(jwt_payload)
            # print the post request data
            print(request.json)
            return "Success", 200
        except jwt.JWTError:
            return "Invalid token", 401
    else:
        return "Missing token", 401

if __name__ == "__main__":
    app.run()