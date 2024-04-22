import requests


def upload_file(url, file_path):
    """
    Upload a file to an S3 bucket using a pre-signed URL.
    """
    with open(file_path, 'rb') as file:
        response = requests.put(url, data=file)
        if response.status_code == 200:
            print("File uploaded successfully.")
        else:
            print(f"Failed to upload file. HTTP Status Code: {response.status_code}")
            print(response.text)

# Read the pre-signed URL from the file
with open('presigned_url.txt', 'r') as file:
    url = file.read().strip()

# Specify the path to your file
file_path = 'test.txt'

# Upload the file
upload_file(url, file_path)
