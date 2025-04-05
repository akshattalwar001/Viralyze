from firebase_database import  UserData
# from aws_s3_storage import upload_to_s3
from aws_s3_storage import upload_model_to_s3
# import json

user_data = UserData(
    username="elonmusk",
    full_name="Elon Musk",
    user_id="123456789",
    biography="CEO of SpaceX and Tesla, Inc.",
    fbid="1234567890",
    fb_account_url="https://www.facebook.com/elonmusk",
    json_url="https://s3.amazonaws.com/your-bucket/profiles/elonmusk.json",
    post_json_url="https://s3.amazonaws.com/your-bucket/posts/elonmusk.json",
    profile_pic_url="https://s3.amazonaws.com/your-bucket/profiles/elonmusk.jpg",
    profile_pic_url_hd="https://s3.amazonaws.com/your-bucket/profiles/elonmusk_hd.jpg",
    is_verified=True,
    last_scraped="2025-04-04T15:00:00Z",
    followers=231000000,
    following=1,
    posts_scraped=1342,
    posts_count=3192,
    avg_likes=1.3e6,
    avg_comments=12_300
)

# # create_user(user_data)
# upload_to_s3("swiggyindia",file_type='profile')
# upload_to_s3("swiggyindia",file_type='posts')

upload_model_to_s3("likes_predictor")