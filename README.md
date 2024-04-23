# Presign URL Service Prototype

## Overview
This is a prototype for a AWS S3 presign url service. It is a a simple client-server that allows a client to request a AWS S3 presign url for a file that is uploaded to the server. The user is authenticated using a JWT token and RSA public/private key pair.

Note: The prototype assumes AWS sessions are tied directly to a user's AWS credentials stored on the development machine. This approach requires the server operator to periodically authenticate with AWS credentials. This is not a practical or secure approach for a production system. In a production system, the server operator would authenticate with AWS using a service account which the server application code is not currently configured to do.

## Installation and Setup

### Requirements
- Python 3.12
- Pipenv

### Installation
To run the client-server, you need to install the dependencies. You can do this by running the following command in the root directory of the project:
```bash
pipenv install
```

### Test Installation
You can test the installation by running the following command:
```bash
pipenv run pytest
```

## Setting up AWS credentials
The prototype is configured to use the default AWS session credentials. This will allow you to authenticate on the command line for a session. You can set up the default credentials by running the following command:

```bash
aws configure
```

This will result in a default profile being created in the `~/.aws/credentials` file. The default profile is used by the prototype to authenticate with AWS.

If you are using SSO, you can set up a profile in the `~/.aws/config` file. The profile should look like this:
```bash

[profile {profile_name}]
sso_start_url = https://{ssosubdomain}.awsapps.com/start
sso_region = {region}
sso_registration_scopes = sso:account:access
sso_role_name = {role_name}
sso_account_id = {account_id}
``` 

## Setup Keys
The client requires a RSA private key to sign the JWT token. The key is stored in the `/keys` directory. The key is generated using the following command:

```bash
pipenv run python -m scripts.generate_rsa_keys
```
Move the files to the `/keys` directory with the pattern {user_name}_private.pem and {user_name}_public.pem.

## Server Configuration and Operation

### Yaml Configuration
The server configuration is stored in the `server/config.yaml` file. There is an example configuration file in the `server/config.yaml.example` file. You can copy this file to `server/config.yaml` and modify the values.

### Running the Server
```bash
pipenv run python -m server.app
```

# Client Configuration and Operation

### Yaml Configuration
The client configuration is stored in the `client/config.yaml` file. There is an example configuration file in the `client/config.yaml.example` file. You can copy this file to `client/config.yaml` and modify the values.

### Running the Client
```bash
pipenv run python -m client.app
```





