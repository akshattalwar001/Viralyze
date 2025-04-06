import json
from pathlib import Path
from aws_s3_storage import download_file_from_s3, fetch_folder_names_from_s3
from config import LOCAL_DATA_DIR, LOCAL_MODEL_DIR, LOCAL_PROFILE_DIR
import os

# Load the JSON dataset with error handling
def load_data(filename='swiggyindia_posts.json'):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found. Please ensure it is in the same directory as this script.")
        print(f"Current directory: {Path.cwd()}")
        return []

def download_data_from_server():
    """
    Download all JSON files (e.g., posts.json, profiles.json) from the S3 bucket
    and save them in the corresponding local directories under the data folder.
    """
    data_dir = LOCAL_DATA_DIR / "profiles"
    if not data_dir.exists():
        data_dir.mkdir(parents=True)

    profile_folders = fetch_folder_names_from_s3(prefix="profiles/")
    if not profile_folders:
        print("No profile folders found in S3.")
        return

    for profile in profile_folders:
        profile_dir = data_dir / profile
        if not profile_dir.exists():
            profile_dir.mkdir(parents=True)

        # Define the files to download
        files_to_download = ["posts.json", "profile.json"]
        for file_name in files_to_download:
            s3_key = f"profiles/{profile}/{file_name}"
            local_path = profile_dir / file_name
            try:
                download_file_from_s3(s3_key, str(local_path))
                print(f"Downloaded {s3_key} to {local_path}.")
            except Exception as e:
                print(f"Failed to download {s3_key}: {e}")