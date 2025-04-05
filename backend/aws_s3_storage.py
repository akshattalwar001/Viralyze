import boto3
import os
import json
from config import LOCAL_DATA_DIR, LOCAL_MODEL_DIR, LOCAL_PROFILE_DIR


# Initialize AWS S3 client
aws_access_key = os.getenv('AWS_ACCESS_KEY')
aws_secret_key = os.getenv('AWS_SECRET_KEY')
bucket_name = os.getenv('BUCKET_NAME')

s3 = boto3.client(
    's3',
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key
)


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
        file_path = LOCAL_PROFILE_DIR / username / "profile.json"
        s3_key = f"profiles/{username}/profile.json"
    elif file_type == 'posts':
        file_path = LOCAL_PROFILE_DIR / username / "posts.json"
        s3_key = f"profiles/{username}/posts.json"

    # Ensure the local directory for the username exists
    (LOCAL_PROFILE_DIR / username).mkdir(parents=True, exist_ok=True)

    try:
        s3.upload_file(str(file_path), bucket_name, s3_key)
        print(f"Uploaded {username} to S3.")
        return f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"
    except Exception as e:
        print("S3 Upload Error:", e)
        return None

def upload_model_to_s3(model_name):
    """Upload a joblib model to S3 and return the URL."""
    # Ensure the local directory for the model exists
    (LOCAL_MODEL_DIR).mkdir(parents=True, exist_ok=True)
    s3_key = f"models/{model_name}.joblib"
    model_path = LOCAL_MODEL_DIR / s3_key
    if not model_path.exists():
        print(f"Model file {model_path} does not exist.")
        return None
    try:
        s3.upload_file(str(model_path), bucket_name, s3_key)
        print(f"Uploaded model to S3 at {s3_key}.")
        return f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"
    except Exception as e:
        print("S3 Upload Error:", e)
        return None

def load_profile_data(username):
    file_path = LOCAL_PROFILE_DIR / f"{username}/profile.json"

    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    # Try fetching from S3 if not found locally
    try:
        s3_key = f"profiles/{username}/profile.json"
        ensure_data_dir()
        s3.download_file(bucket_name, s3_key, str(file_path))
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print("Error fetching from S3:", e)
        return None
