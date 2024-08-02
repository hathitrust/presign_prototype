# Presign URL Service Prototype

## Overview
This is a prototype for a AWS S3 presign url service. It is a a simple client-server that allows a client to request a AWS S3 presign url for a file that is uploaded to the server. The user is authenticated using a JWT token and RSA public/private key pair.

Note: The prototype assumes AWS sessions are tied directly to a user's AWS credentials stored on the development machine. This approach requires the server operator to periodically authenticate with AWS credentials. This is not a practical or secure approach for a production system. In a production system, the server operator would authenticate with AWS using a service account which the server application code is not currently configured to do.

## Installation and Setup

### Requirements
- Docker
- Python
- An S3 bucket
- An IAM User with permissions to put objects in the S3 bucket above
- RSA public/private key pair for the a user (see below)

### Configurations
- Take a look at the docker-compose.yml file to see the configurations.
- The fields that read from environment variables:
    - The `AWS_REGION` is the region of the S3 bucket.
    - The `S3_BUCKET` is the name of the S3 bucket.
    - The `S3_FOLDER` is the folder in the S3 bucket where the files will be uploaded.
    - The `AWS_ACCESS_KEY_ID` is the access key for the IAM User.
    - The `AWS_SECRET_ACCESS_KEY` is the secret access key for the IAM User.
    - The `AWS_SESSION_TOKEN` is only relevant for temporary credentials, comment it out if not.
- The rest can be left untouched for the sake of the demo.

### Keys
- The directory containing the RSA keys by default is named "keys", and is present at the root of the project. It will be mounted to the Docker container. If you change this, make sure to update the `docker-compose.yml` file.
- For each user (default name is "example", and this is different from the IAM User), two key files are expected in that directory:
    - Public key file: `<user>_public.pem`
    - Private key file: `<user>_private.pem`
- Run `generate_keys.py --location <keys_dir_name> --user <user>` to set up the key files.
    - Location defaults to "keys".
    - User defaults to "example".

## Running the demo
- To run only the server: `docker-compose up --build`
    - You can make custom requests to the server by following the logic in the `client.py` file.
- To run the server and the client: `docker-compose --profile client up --build`
    - Look at the comment in the `docker-compose.yml` for more information.