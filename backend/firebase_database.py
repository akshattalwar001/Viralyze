# firebase_config.py
import os
import json
import base64
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from dataclasses import dataclass

# Load environment variables
load_dotenv()

# Decode the base64-encoded service account key
service_account_key_base64 = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY")
service_account_key = json.loads(base64.b64decode(service_account_key_base64).decode("utf-8"))
print("Decoded key")

# Initialize Firebase
cred = credentials.Certificate(service_account_key)
firebase_admin.initialize_app(cred)
db = firestore.client()
print("Firebase initialized.")

@dataclass
class UserData:
    username: str
    full_name: str
    user_id: str
    biography: str
    fbid: str
    fb_account_url: str
    json_url: str
    post_json_url: str
    profile_pic_url: str
    profile_pic_url_hd: str
    is_verified: bool
    last_scraped: str
    followers: int
    following: int
    posts_scraped: int
    posts_count: int
    avg_likes: float
    avg_comments: float

def has_profile_been_scraped(username):
    doc = db.collection("profiles").document(username).get()
    return doc.exists

def get_scraped_post_ids(username):
    doc = db.collection("scrap_cache").document(username).get()
    if doc.exists:
        return set(doc.to_dict().get("scraped_post_ids", []))
    return set()

def update_scraped_post_ids(username, new_ids):
    doc_ref = db.collection("scrap_cache").document(username)
    doc = doc_ref.get()

    if doc.exists:
        existing_ids = set(doc.to_dict().get("scraped_post_ids", []))
        all_ids = list(existing_ids.union(new_ids))
    else:
        all_ids = list(new_ids)

    doc_ref.set({
        "username": username,
        "scraped_post_ids": all_ids,
        "last_updated": datetime.utcnow().isoformat()
    })

def create_user(user_data):
    """
    Creates a user document in the Firestore database.
    Args:
        user_data (UserData): An instance of the UserData dataclass containing user data.
    """
    doc_ref = db.collection("profiles").document(user_data.username)
    doc_ref.set({
        "username": user_data.username,
        "full_name": user_data.full_name,
        "user_id": user_data.user_id,
        "biography": user_data.biography,
        "fbid": user_data.fbid,
        "fb_account_url": user_data.fb_account_url,
        "json_url": user_data.json_url,
        "post_json_url": user_data.post_json_url,
        "profile_pic_url": user_data.profile_pic_url,
        "profile_pic_url_hd": user_data.profile_pic_url_hd,
        "is_verified": user_data.is_verified,
        "last_scraped": user_data.last_scraped,
        "followers": user_data.followers,
        "following": user_data.following,
        "posts_scraped": user_data.posts_scraped,
        "posts_count": user_data.posts_count,
        "avg_likes": user_data.avg_likes,
        "avg_comments": user_data.avg_comments
    })