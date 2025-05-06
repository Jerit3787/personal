#!/usr/bin/env python
"""
Social Media Follower Counter
Fetches follower counts from Twitter and Instagram APIs and saves to a JSON file.
Designed to run as a GitHub Action workflow.
"""

import os
import json
import requests
from datetime import datetime

# Configuration
OUTPUT_PATH = "social_data.json"
TWITTER_USER_ID = os.environ.get("TWITTER_USER_ID", "")
TWITTER_BEARER_TOKEN = os.environ.get("TWITTER_BEARER_TOKEN", "")
INSTAGRAM_ACCESS_TOKEN = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")
INSTAGRAM_USER_ID = os.environ.get("INSTAGRAM_USER_ID", "")


def get_twitter_followers():
    """Fetch follower count from Twitter API"""
    if not TWITTER_BEARER_TOKEN or not TWITTER_USER_ID:
        print("Error: Twitter API credentials not provided")
        return 0

    url = f"https://api.twitter.com/2/users/{TWITTER_USER_ID}?user.fields=public_metrics"
    headers = {
        "Authorization": f"Bearer {TWITTER_BEARER_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        print("Fetching Twitter follower count via API...")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        data = response.json()
        if data and "data" in data and "public_metrics" in data["data"]:
            follower_count = data["data"]["public_metrics"]["followers_count"]
            print(f"Twitter followers: {follower_count}")
            return follower_count
        else:
            print("Error: Unexpected Twitter API response format")
            print(f"Response: {data}")
            return 0
    except Exception as e:
        print(f"Error fetching Twitter data: {e}")
        return 0


def get_instagram_followers():
    """Fetch follower count from Instagram Graph API"""
    if not INSTAGRAM_ACCESS_TOKEN or not INSTAGRAM_USER_ID:
        print("Error: Instagram API credentials not provided")
        return 0

    try:
        print("Fetching Instagram follower count via API...")
        # Instagram Graph API endpoint for user profile
        url = f"https://graph.instagram.com/v12.0/{INSTAGRAM_USER_ID}?fields=followers_count&access_token={INSTAGRAM_ACCESS_TOKEN}"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if "followers_count" in data:
            follower_count = data["followers_count"]
            print(f"Instagram followers: {follower_count}")
            return follower_count
        else:
            print("Error: Instagram API response missing follower count")
            print(f"Response: {data}")
            return 0
    except Exception as e:
        print(f"Error fetching Instagram data: {e}")
        return 0


def load_existing_data():
    """Load existing data file if it exists"""
    try:
        if os.path.exists(OUTPUT_PATH):
            with open(OUTPUT_PATH, 'r', encoding='utf-8') as file:
                return json.load(file)
    except Exception as e:
        print(f"Error loading existing data: {e}")
    
    # Return default structure if file doesn't exist or is invalid
    return {
        "instagram": {"followers": 0},
        "twitter": {"followers": 0}
    }


def save_data(data):
    """Save data to JSON file"""
    try:
        with open(OUTPUT_PATH, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2)
        print(f"Data successfully saved to {OUTPUT_PATH}")
    except Exception as e:
        print(f"Error saving data: {e}")


def main():
    """Main function to fetch and save social media data"""
    # Get current data
    twitter_followers = get_twitter_followers()
    instagram_followers = get_instagram_followers()
    
    # Load existing data to preserve history if needed
    existing_data = load_existing_data()
    
    # Use existing data as fallback if API failed
    if twitter_followers == 0:
        twitter_followers = existing_data.get("twitter", {}).get("followers", 0)
        print(f"Using existing Twitter follower count: {twitter_followers}")
    
    if instagram_followers == 0:
        instagram_followers = existing_data.get("instagram", {}).get("followers", 0)
        print(f"Using existing Instagram follower count: {instagram_followers}")
    
    # Update with new data
    data = {
        "instagram": {
            "followers": instagram_followers
        },
        "twitter": {
            "followers": twitter_followers
        }
    }
    
    # Save to file
    save_data(data)
    print("Social media data update complete!")


if __name__ == "__main__":
    main()