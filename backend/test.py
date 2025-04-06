import json, os
from utils import download_data_from_server
from pathlib import Path
from aws_s3_storage import upload_model_to_s3, upload_to_s3, download_file_from_s3
from firebase_database import create_user, calc_avg_likes,avg_comments, UserData
from scraper import scrape_using_apify

# user = data["data"]["user"]
def upload_bulk_profiles(data):
    user_data = UserData(
        user_id=data["id"],
        username=data["username"],
        full_name=data["full_name"],
        biography=data["biography"],
        fbid=data["fbid"],
        json_url="https://s3.amazonaws.com/viralyze/data/profiles/wth_ishu/profile.json",
        post_json_url="https://s3.amazonaws.com/viralyze/data/profiles/wth_ishu/posts.json",
        profile_pic_url=data["profile_pic_url"],
        profile_pic_url_hd=data["profile_pic_url_hd"],
        is_verified=data["is_verified"],
        is_private=data["is_private"],
        last_scraped='2023-10-01T12:00:00Z',
        followers=data["edge_followed_by"]["count"],
        following=data["edge_follow"]["count"],
        posts_scraped=data["edge_owner_to_timeline_media"]["count"],
        posts_count=data["edge_owner_to_timeline_media"]["count"],
        avg_likes=calc_avg_likes(data["edge_owner_to_timeline_media"]["edges"]),
        avg_comments=avg_comments(data["edge_owner_to_timeline_media"]["edges"]),
    )

    create_user(user_data)
    
def bulk_upload_profiles_posts_to_s3():
    for profile in os.listdir("data/profiles/"):
        # profile = "swiggyindia"
        file_path = f"data/profiles/{profile}/posts.json"

        # with open(file_path, "r") as file:
        #     data = json.load(file)
        
        # Assuming the JSON structure is as follows:
        # upload_bulk_profiles(data)
        print(f"Uploading {profile} to S3...")
        upload_to_s3(profile, file_type='profile')
        upload_to_s3(profile, file_type='posts')

# upload_model_to_s3("likes_predictor")

def upload_cache_file_to_s3():
    cache_file_path = "data/fetch_cache.json"
    if os.path.exists(cache_file_path):
        upload_to_s3("cache", file_type='cache')
    else:
        print(f"Cache file {cache_file_path} does not exist.")

# upload_cache_file_to_s3()
# download_file_from_s3("fetch_cache.json", "fetch_cache.json")
bulk_upload_profiles_posts_to_s3()
# download_data_from_server()

# scrape_using_apify("wth_ishu")