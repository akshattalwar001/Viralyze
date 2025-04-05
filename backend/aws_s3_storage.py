import boto3
import os
from pathlib import Path

# Initialize AWS S3 client
aws_access_key = os.getenv('AWS_ACCESS_KEY')
aws_secret_key = os.getenv('AWS_SECRET_KEY')
bucket_name = os.getenv('BUCKET_NAME')

s3 = boto3.client(
    's3',
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key
)

LOCAL_DATA_DIR = Path("data/profiles")

def ensure_data_dir():
    LOCAL_DATA_DIR.mkdir(parents=True, exist_ok=True)

def save_json_locally(username, data):
    ensure_data_dir()
    file_path = LOCAL_DATA_DIR / f"{username}.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    return str(file_path)

def upload_to_s3(username, file_type='profile'):
    """Upload the profile data to S3 and return the URL."""
    ensure_data_dir()

       # Update file paths to include the username folder
    if file_type == 'profile':
        file_path = LOCAL_DATA_DIR / username / f"profile.json"
        s3_key = f"data/{username}/profile.json"
    elif file_type == 'posts':
        file_path = LOCAL_DATA_DIR / username / f"posts.json"
        s3_key = f"data/{username}/posts.json"

    # Ensure the local directory for the username exists
    (LOCAL_DATA_DIR / username).mkdir(parents=True, exist_ok=True)

    try:
        s3.upload_file(str(file_path), bucket_name, s3_key)
        print(f"Uploaded {username} to S3.")
        return f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"
    except Exception as e:
        print("S3 Upload Error:", e)
        return None

def load_profile_data(username):
    file_path = LOCAL_DATA_DIR / f"{username}.json"

    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    # Try fetching from S3 if not found locally
    try:
        s3_key = f"profiles/{username}.json"
        ensure_data_dir()
        s3.download_file(bucket_name, s3_key, str(file_path))
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print("Error fetching from S3:", e)
        return None
