import boto3
import os
import json
from config import LOCAL_DATA_DIR, LOCAL_MODEL_DIR, LOCAL_PROFILE_DIR
from dotenv import load_dotenv

load_dotenv()

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
    """Upload the profile or posts data to S3 and return the URL."""
    ensure_data_dir()

    # Determine file path and S3 key based on file type
    if file_type == 'profile':
        file_path = LOCAL_PROFILE_DIR / username / "profile.json"
        s3_key = f"profiles/{username}/profile.json"
    elif file_type == 'posts':
        file_path = LOCAL_PROFILE_DIR / username / "posts.json"
        s3_key = f"profiles/{username}/posts.json"
        
    elif file_type == 'cache':
        file_path = LOCAL_DATA_DIR / "fetch_cache.json"
        s3_key = "fetch_cache.json"
    else:
        print(f"Error: Unsupported file type '{file_type}'.")
        return None

    # print(f"Uploading {file_path} to {s3_key} in S3... of { username} of {file_type}")
    # Ensure the local directory for the username exists
    # (LOCAL_PROFILE_DIR / username).mkdir(parents=True, exist_ok=True)

    # Check if the file exists and is not empty
    if not file_path.exists() or file_path.stat().st_size == 0:
        print(f"Error: File {file_path} does not exist or is empty.")
        return None

    try:
        # Upload the file to S3
        s3.upload_file(str(file_path), bucket_name, s3_key)
        print(f"Uploaded {file_path} to S3 at {s3_key}.")
        return f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"
    except Exception as e:
        print(f"S3 Upload Error: {e}")
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

def download_file_from_s3(s3_key, local_path):
    """Download a file from S3 to a local path."""
    try:
        s3.download_file(bucket_name, s3_key, local_path)
        print(f"Downloaded {s3_key} to {local_path}.")
    except Exception as e:
        print(f"Error downloading {s3_key} from S3: {e}")