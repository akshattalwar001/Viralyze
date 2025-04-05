import requests
import json
import os
import time
from datetime import datetime
from random import choice, uniform

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
    "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
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

def fetch_all_posts(username):
    """Fetch all posts for a given username using Instagram's API with pagination, delays, retries, and caching."""
    base_url = "https://i.instagram.com/api/v1/users/web_profile_info/"
    all_posts = []
    batch_count = 0
    batch_size = 500
    folder_path = os.path.join('data',username)

    # Create folder for the username if it doesn't exist
    os.makedirs(folder_path, exist_ok=True)

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
                user_data = data["data"]["user"]
                media = user_data["edge_owner_to_timeline_media"]

                all_posts.extend(media["edges"])
                has_next_page = media["page_info"]["has_next_page"]
                end_cursor = media["page_info"]["end_cursor"]

                # Save posts in batches of 500
                if len(all_posts) >= batch_size:
                    batch_count += 1
                    save_to_file(all_posts[:batch_size], os.path.join(folder_path, f"batch_{batch_count}.json"))
                    all_posts = all_posts[batch_size:]

                # Update cache
                cache[username] = {"end_cursor": end_cursor, "has_next_page": has_next_page}
                save_cache(cache)

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
    if all_posts:
        batch_count += 1
        save_to_file(all_posts, os.path.join(folder_path, f"batch_{batch_count}.json"))

    print(f"{Colors.OKBLUE}📁 All posts saved in folder: {folder_path}{Colors.ENDC}")

def process_posts(posts):
    """Process posts to extract relevant fields."""
    formatted_posts = []

    for post in posts:
        node = post["node"]
        pid = node["id"]
        shortcode = node["shortcode"]
        taken_at = datetime.fromtimestamp(node["taken_at_timestamp"]).strftime('%Y-%m-%dT%H:%M:%SZ')
        caption = node["edge_media_to_caption"]["edges"][0]["node"]["text"] if node["edge_media_to_caption"]["edges"] else ""
        comments = node["edge_media_to_comment"]["count"]
        likes = node["edge_liked_by"]["count"]
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

    return formatted_posts

def save_to_file(data, filename):
    """Save data to a JSON file."""
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)
    print(f"{Colors.OKCYAN}💾 Data saved to {filename}{Colors.ENDC}")

def main():
    username = "rvcjinsta"
    print(f"{Colors.HEADER}🚀 Fetching posts for {username}...{Colors.ENDC}")
    fetch_all_posts(username)

if __name__ == "__main__":
    main()
