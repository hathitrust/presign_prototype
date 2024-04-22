import os
import sys

from cryptography.hazmat.primitives.serialization import (load_pem_private_key,
                                                          load_pem_public_key)

import lib.key_helper as kh


def main():
  # Get the current working directory
  current_dir = os.getcwd()

  print("Generating RSA keys...", file=sys.stderr)

  # Generate a new RSA private key and corresponding public key
  private_key, public_key = kh.generate_rsa_pem_key_pair()

  # Paths where the keys will be saved
  public_key_path = os.path.join(current_dir, 'public.pem')
  private_key_path = os.path.join(current_dir, 'private.pem')

  # Save the public key in PEM format to the specified file
  kh.save_public_key(public_key, public_key_path)
  print(f"Public key saved to {public_key_path}")

  # Save the private key in PEM format to the specified file
  kh.save_private_key(private_key, private_key_path)
  print(f"Private key saved to {private_key_path}")

  # Std.err that the keys have been saved, round trip to be performed.
  print("Starting round trip of a message...", file=sys.stderr)

  print("Loading the keys from the files...", file=sys.stderr)

  # Load the keys from the files
  with open(public_key_path, 'rb') as f:
    public_key = load_pem_public_key(f.read())
    
  with open(private_key_path, 'rb') as f:
    private_key = load_pem_private_key(f.read(), password=None)
  # Encrypt a message with the public key
  message = 'Roundtrip of the message is complete'

  ciphertext = kh.encrypt_with_public_key(public_key, message.encode())
  print(f"Encrypted message: {ciphertext.hex()}", file=sys.stderr)

  # Decrypt the message with the private key, decode from bytes to string
  plaintext = kh.decrypt_with_private_key(private_key, ciphertext)
  print(f"Decrypted message: {plaintext.decode()}", file=sys.stderr) 

if __name__ == "__main__":
    main()
