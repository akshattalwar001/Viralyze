import requests
import json
import os
import time
from datetime import datetime
from random import choice, uniform
from dotenv import load_dotenv
from pathlib import Path
from aws_s3_storage import upload_model_to_s3, upload_to_s3, download_file_from_s3
# Load environment variables from .env file
load_dotenv()


# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

USER_AGENTS = [
    "Instagram 123.0.0.0 Android",
    # "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36",
    # "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
]

CACHE_FILE = "data/fetch_cache.json"

def load_cache():
    """Load the cache from the cache file."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as file:
            return json.load(file)
    return {}

def save_cache(cache):
    """Save the cache to the cache file."""
    with open(CACHE_FILE, "w") as file:
        json.dump(cache, file, indent=4)

def scrape_user_data(username, max_posts=12):
    """Fetch all posts for a given username using Instagram's API with pagination, delays, retries, and caching."""
    base_url = "https://i.instagram.com/api/v1/users/web_profile_info/"
    all_posts = []
    batch_count = 0
    batch_size = 1  # Number of posts to save in each batch
    folder_path = os.path.join('data','profiles',username)

    # Create folder for the username if it doesn't exist
    os.makedirs(folder_path, exist_ok=True)
    print(f"{Colors.HEADER}🚀 Fetching posts for {username}...{Colors.ENDC}")

    # Load cache
    cache = load_cache()
    end_cursor = cache.get(username, {}).get("end_cursor")
    has_next_page = cache.get(username, {}).get("has_next_page", True)

    retry_attempts = 0
    max_retries = 3

    while has_next_page:
        headers = {"User-Agent": choice(USER_AGENTS)}
        params = {"username": username}
        if end_cursor:
            params["after"] = end_cursor

        try:
            response = requests.get(base_url, headers=headers, params=params)

            if response.status_code == 200:
                print(f"{Colors.OKGREEN}✅ Successfully fetched data for {username}.{Colors.ENDC}")
                data = response.json()
                # TODO: Check if the response contains the expected data structure
                user_data = data["data"]["user"]
                media = user_data["edge_owner_to_timeline_media"]

                all_posts.extend(media["edges"])
                has_next_page = media["page_info"]["has_next_page"]
                end_cursor = media["page_info"]["end_cursor"]

                # Save posts in batches of 60
                if len(all_posts) >= batch_size:
                    batch_count += 1
                    save_to_file(user_data, os.path.join(folder_path, "profile.json"))
                    all_posts = all_posts[batch_size:]

                # Update cache
                cache[username] = {
                    "end_cursor": end_cursor,
                    "has_next_page": has_next_page,
                    "last_scraped": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                save_cache(cache)

                # Check if max_posts limit is reached
                if max_posts and len(all_posts) >= max_posts:
                    print(f"{Colors.OKBLUE}📌 Reached the specified limit of {max_posts} posts. Stopping...{Colors.ENDC}")
                    has_next_page = False

                # Reset retry attempts and add a random delay to avoid IP blocking
                retry_attempts = 0
                time.sleep(uniform(2, 5))

            elif response.status_code == 401:
                print(f"{Colors.FAIL}❌ Error 401: Unauthorized. Response: {response.json()}{Colors.ENDC}")
                retry_attempts += 1
                if retry_attempts > max_retries:
                    print(f"{Colors.FAIL}❌ Max retries reached. Exiting...{Colors.ENDC}")
                    break
                backoff_time = 2 ** retry_attempts
                print(f"{Colors.WARNING}⚠️ Retrying in {backoff_time} seconds...{Colors.ENDC}")
                time.sleep(backoff_time)

            else:
                print(f"{Colors.FAIL}❌ Failed to fetch data. Status code: {response.status_code}{Colors.ENDC}")
                print(f"{Colors.FAIL}Response: {response.text}{Colors.ENDC}")
                break

        except Exception as e:
            print(f"{Colors.FAIL}❌ An error occurred: {e}{Colors.ENDC}")
            break

    # Save any remaining posts
    # if all_posts:
    #     batch_count += 1
    #     save_to_file(all_posts, os.path.join(folder_path, f"posts_{batch_count}.json"))

    print(f"{Colors.OKBLUE}📁 All {len(all_posts)} posts saved in folder: {folder_path}{Colors.ENDC}")
    return all_posts

def store_posts_into_json(posts, username):
    """Process posts to extract relevant fields."""
    formatted_posts = []
    print(f"{Colors.OKCYAN}📦 Processing posts...{Colors.ENDC}")
    
    for post in posts:
        node = post["node"]
        pid = node["id"]
        shortcode = node["shortcode"]
        taken_at = datetime.fromtimestamp(node["taken_at_timestamp"]).strftime('%Y-%m-%dT%H:%M:%SZ')
        caption = node["edge_media_to_caption"]["edges"][0]["node"]["text"] if node["edge_media_to_caption"]["edges"] else ""
        comments = node["edge_media_to_comment"]["count"]
        likes = node["edge_liked_by"]["count"]
        views = node["video_view_count"] if "video_view_count" in node else 0
        hashtags = [word for word in caption.split() if word.startswith("#")]

        formatted_post = {
            "id": pid,
            "shortcode": shortcode,
            "likes_count": likes,
            "comments_count": comments,
            "timestamp": taken_at,
            "caption": caption,
            "hashtags": hashtags
        }
        formatted_posts.append(formatted_post)
    
    # Save the entire list of formatted posts
    save_to_file(formatted_posts, os.path.join('data', 'profiles', username, 'posts.json'))

    return True if formatted_posts else False


def store_posts_into_json(item, username):
    """Process posts to extract relevant fields."""
    formatted_posts = []
    print(f"{Colors.OKCYAN}📦 Processing posts...{Colors.ENDC}")
    
    for post in item:
        pid = post["id"]
        shortcode = post["shortcode"]
        taken_at = datetime.fromtimestamp(post["taken_at_timestamp"]).strftime('%Y-%m-%dT%H:%M:%SZ')
        caption = post["caption"] if "caption" in post else ""
        comments = post["comments_count"] if "comments_count" in post else 0
        likes = post["likes_count"] if "likes_count" in post else 0
        views = post["views_count"] if "views_count" in post else 0
        hashtags = [word for word in caption.split() if word.startswith("#")]

        formatted_post = {
            "id": pid,
            "shortcode": shortcode,
            "likes_count": likes,
            "comments_count": comments,
            "timestamp": taken_at,
            "caption": caption,
            "hashtags": hashtags
        }
        formatted_posts.append(formatted_post)
    
    # Save the entire list of formatted posts
    save_to_file(formatted_posts, os.path.join('data', 'profiles', username, 'posts.json'))

    return True if formatted_posts else False


def main():
    username = "rvcjinsta"
    
    scrape_user_data(username)


##### NEW SCRAPE FUNCTION ⭐⭐⭐
def save_to_file(data, filename):
    """Save data to a JSON file."""
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)
    print(f"{Colors.OKCYAN}💾 Data saved to {filename}{Colors.ENDC}")


def scrape_using_apify(username, max_posts=200):
    """Scrape Instagram posts using Apify Actor."""
    from apify_client import ApifyClient

    # Initialize the ApifyClient with your API token
    client = ApifyClient(os.getenv("APIFY_API_KEY"))

    # Prepare the Actor input
    run_input = {
        "addParentData": False,
        "directUrls": [f"https://www.instagram.com/{username}/"],
        "resultsType": "details",
        "resultsLimit": max_posts,
        "enhanceUserSearchWithFacebookPage": False,
        "isUserReelFeedURL": False,
        "isUserTaggedFeedURL": False,
        "searchLimit": 1,
        "searchType": "hashtag"
    }

    # Run the Actor and wait for it to finish
    run = client.actor("shu8hvrXbJbY3Eb9W").call(run_input=run_input)

    # Fetch and process Actor results
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        # Extract profile data
        profile_data = {
            "inputUrl": item["inputUrl"],
            "id": item["id"],
            "username": item["username"],
            "url": item["url"],
            "fullName": item["fullName"],
            "biography": item["biography"],
            "externalUrls": item["externalUrls"],
            "followersCount": item["followersCount"],
            "followsCount": item["followsCount"],
            "hasChannel": item["hasChannel"],
            "highlightReelCount": item["highlightReelCount"],
            "isBusinessAccount": item["isBusinessAccount"],
            "joinedRecently": item["joinedRecently"],
            "businessCategoryName": item["businessCategoryName"],
            "private": item["private"],
            "verified": item["verified"],
            "profilePicUrl": item["profilePicUrl"],
            "profilePicUrlHD": item["profilePicUrlHD"],
            "igtvVideoCount": item["igtvVideoCount"],
            "relatedProfiles": item["relatedProfiles"],
            "latestIgtvVideos": item["latestIgtvVideos"],
            "postsCount": item["postsCount"]
        }

        # Extract posts data
        posts_data = []
        for post in item.get("latestPosts", []):
            posts_data.append({
                "id": post["id"],
                "shortcode": post["shortCode"],
                "likes_count": post["likesCount"],
                "comments_count": post["commentsCount"],
                "timestamp": post["timestamp"],
                "caption": post["caption"],
                "hashtags": post["hashtags"],
                "displayUrl": post["displayUrl"],
            })

        # Save profile and posts data
        folder_path = os.path.join('data', 'profiles', username)
        os.makedirs(folder_path, exist_ok=True)

        save_to_file(profile_data, os.path.join(folder_path, 'profile.json'))
        save_to_file(posts_data, os.path.join(folder_path, 'posts.json'))

        # upload the files to aws s3
        upload_to_s3(username, "profile")
        upload_to_s3(username, "posts")

    return True, posts_data if item else False


if __name__ == "__main__":
    main()
