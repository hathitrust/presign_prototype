import boto3

# Specify the profile name you configured with AWS SSO
profile_name = 'profile-name'

# Specify your bucket name here
bucket_name = 'bucket-name'

# Specify the file name that will appear in the bucket once uploaded
object_name = 'test_file.txt'

# URL expiration time in seconds
url_expiration = 3600  # 1 hour

# Create a Boto3 session with the specified profile
session = boto3.Session(profile_name=profile_name,region_name='us-west-2')

# Create an S3 client from the session
s3_client = session.client('s3')

def generate_presigned_url(bucket_name, object_name, expiration):
    """
    Generate a pre-signed URL to upload a file to an S3 bucket.
    """
    try:
        response = s3_client.generate_presigned_url('put_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
        return response
    except Exception as e:
        print(f"Error generating pre-signed URL: {e}")
        return None

# Generate the pre-signed URL
url = generate_presigned_url(bucket_name, object_name, url_expiration)

if url:
    print(f"Pre-signed URL for upload: {url}")
else:
    print("Failed to generate pre-signed URL.")
