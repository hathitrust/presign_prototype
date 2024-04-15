from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

# Generate a new RSA private key
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

# Derive the public key from the private key
public_key = private_key.public_key()

# Save the public key in PEM format
public_key_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

with open('public.pem', 'wb') as f:
    f.write(public_key_pem)
    print("Public key saved to public.pem")

# Save the private key in PEM format
private_key_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption()
)

with open('private.pem', 'wb') as f:
    f.write(private_key_pem)
    print("Private key saved to private.pem")

# Encrypt a message with the public key
message = b'Hello, World!'
ciphertext = public_key.encrypt(
    message,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)
print(f"Encrypted message: {ciphertext}")

# Decrypt the message with the private key
plaintext = private_key.decrypt(
    ciphertext,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)
print(f"Decrypted message: {plaintext}")