import json
from pathlib import Path

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

