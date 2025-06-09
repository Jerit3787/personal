#!/usr/bin/env python
"""
Enhanced Social Media Data Fetcher
Fetches comprehensive profile data from Twitter and Instagram APIs and saves to a JSON file.
Designed to run as a GitHub Action workflow.
"""

import os
import json
import requests
import base64
from datetime import datetime
from urllib.parse import urlparse
from pathlib import Path

# Configuration
OUTPUT_PATH = "social_data.json"
TWITTER_USER_ID = os.environ.get("TWITTER_USER_ID", "")
TWITTER_BEARER_TOKEN = os.environ.get("TWITTER_BEARER_TOKEN", "")
TWITTER_USERNAME = os.environ.get("TWITTER_USERNAME", "")  # Added missing variable
INSTAGRAM_ACCESS_TOKEN = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")
INSTAGRAM_USER_ID = os.environ.get("INSTAGRAM_USER_ID", "")
SAVE_PROFILE_IMAGES = True  # Whether to download profile images


def fetch_twitter_profile(api_url, api_name="API", data_accessor=None):
    """Generic function to fetch Twitter profile data from various APIs
    
    Args:
        api_url: The Twitter API URL to fetch data from
        api_name: Name of the API for logging purposes
        data_accessor: Function to access user data from the response (default: lambda d: d["data"])
    
    Returns:
        Twitter profile data dictionary or None if fetching failed
    """
    if not TWITTER_BEARER_TOKEN:
        print("Error: Twitter API credentials not provided")
        return None

    if data_accessor is None:
        # Default accessor for single user response
        data_accessor = lambda d: d["data"]
        
    headers = {
        "Authorization": f"Bearer {TWITTER_BEARER_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        print(f"Fetching Twitter profile data via {api_name}...")
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if data and "data" in data:
            user_data = data_accessor(data)
            profile_data = {
                "username": user_data.get("username", ""),
                "name": user_data.get("name", ""),
                "description": user_data.get("description", ""),
                "followers": user_data.get("public_metrics", {}).get("followers_count", 0),
                "following": user_data.get("public_metrics", {}).get("following_count", 0),
                "tweets": user_data.get("public_metrics", {}).get("tweet_count", 0),
                "profile_image_url": user_data.get("profile_image_url", "")
            }
            
            # Apply high-res profile image replacement for all APIs
            if profile_data["profile_image_url"]:
                profile_data["profile_image_url"] = profile_data["profile_image_url"].replace("_normal", "_400x400")
            
            # Save profile image if available and configured to do so
            if SAVE_PROFILE_IMAGES and profile_data["profile_image_url"]:
                profile_data["profile_image_path"] = download_image(
                    profile_data["profile_image_url"], 
                    "twitter_profile.jpg"
                )
            
            print(f"Twitter data fetched: @{profile_data['username']} - {profile_data['followers']} followers")
            return profile_data
        else:
            print("Error: Unexpected Twitter API response format")
            print(f"Response: {data}")
            return None
    except Exception as e:
        print(f"Error fetching Twitter data from {api_name}: {e}")
        return None


def get_twitter_profile():
    """Fetch comprehensive Twitter profile data via primary API"""
    if not TWITTER_USER_ID:
        print("Error: Twitter user ID not provided")
        return None
        
    url = f"https://api.x.com/2/users/{TWITTER_USER_ID}?user.fields=name,username,description,profile_image_url,public_metrics"
    # The primary API returns a single user directly in the "data" field
    return fetch_twitter_profile(url, "primary API")


def get_twitter_profile_alternative():
    """Fetch comprehensive Twitter profile data via alternative API"""
    if not TWITTER_USER_ID:
        print("Error: Twitter user ID not provided")
        return None
        
    url = f"https://api.x.com/2/users?ids={TWITTER_USER_ID}&user.fields=name,username,description,profile_image_url,public_metrics"
    # This API returns an array of users in the "data" field
    return fetch_twitter_profile(url, "alternative API", lambda d: d["data"][0])


def get_twitter_profile_username():
    """Fetch comprehensive Twitter profile data via username API"""
    if not TWITTER_USERNAME:
        print("Error: Twitter username not provided")
        return None
        
    url = f"https://api.x.com/2/users/by/username/{TWITTER_USERNAME}?user.fields=name,username,description,profile_image_url,public_metrics"
    print("NOTE - This API depends on the username not being changed by the user.")
    print("If the username has changed, please update the username or attempt to use the user ID API instead.")
    
    # This API returns an array of users in the "data" field
    return fetch_twitter_profile(url, "username API")


def get_instagram_profile():
    """Fetch comprehensive Instagram profile data"""
    if not INSTAGRAM_ACCESS_TOKEN:
        print("Error: Instagram API credentials not provided")
        return None

    try:
        print("Fetching Instagram profile data via API...")
        # Get basic profile information including full name
        url = f"https://graph.instagram.com/me?fields=id,username,name,media_count,account_type&access_token={INSTAGRAM_ACCESS_TOKEN}"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        basic_data = response.json()
        if "username" not in basic_data:
            print(f"Error: Instagram API missing username field: {basic_data}")
            return None
            
        # Now get additional fields like follower count
        url = f"https://graph.instagram.com/me?fields=followers_count,follows_count,biography&access_token={INSTAGRAM_ACCESS_TOKEN}"
        
        followers_response = requests.get(url, timeout=10)
        followers_data = {}
        
        if followers_response.status_code == 200:
            followers_data = followers_response.json()
        else:
            print(f"Warning: Couldn't fetch Instagram follower data: {followers_response.text}")
            
        # Get user profile info if available
        profile_data = {
            "id": basic_data.get("id", ""),
            "username": basic_data.get("username", ""),
            "name": basic_data.get("name", ""),
            "media_count": basic_data.get("media_count", 0),
            "account_type": basic_data.get("account_type", ""),
            "biography": followers_data.get("biography", ""),
            "followers": followers_data.get("followers_count", 0),
            "following": followers_data.get("follows_count", 0)
        }
        
        # Try to fetch profile picture if possible
        try:
            profile_pic_url = f"https://graph.instagram.com/me?fields=profile_picture_url&access_token={INSTAGRAM_ACCESS_TOKEN}"
            pic_response = requests.get(profile_pic_url, timeout=10)
            if pic_response.status_code == 200:
                pic_data = pic_response.json()
                if "profile_picture_url" in pic_data:
                    profile_data["profile_image_url"] = pic_data["profile_picture_url"]
                    if SAVE_PROFILE_IMAGES:
                        profile_data["profile_image_path"] = download_image(
                            profile_data["profile_image_url"],
                            "insta_profile.jpg"
                        )
        except Exception as pic_error:
            print(f"Warning: Couldn't fetch Instagram profile picture: {pic_error}")
            
        print(f"Instagram data fetched: @{profile_data['username']} ({profile_data['name']}) - {profile_data['followers']} followers")
        return profile_data
    except Exception as e:
        print(f"Error fetching Instagram data: {e}")
        return None


def download_image(image_url, filename):
    """Download an image from the given URL and save it to the img directory"""
    if not image_url:
        return None
        
    try:
        # Create img directory if it doesn't exist
        img_dir = "img"
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)
            
        # Create full path for the image
        image_path = os.path.join(img_dir, filename)
        
        # Download the image
        response = requests.get(image_url, stream=True, timeout=10)
        response.raise_for_status()
        
        # Save the image
        with open(image_path, 'wb') as img_file:
            for chunk in response.iter_content(chunk_size=8192):
                img_file.write(chunk)
                
        print(f"Downloaded image: {image_path}")
        return image_path
    except Exception as e:
        print(f"Error downloading image {image_url}: {e}")
        return None


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


def verify_image_accessibility(image_path, fallback_url):
    """Check if the image file exists and is accessible. If not, return the fallback URL."""
    if image_path and os.path.exists(image_path):
        return image_path
    return fallback_url


def is_remote_image_accessible(url):
    """Check if a remote image URL is accessible (returns 200 and is an image)."""
    try:
        resp = requests.head(url, timeout=5, allow_redirects=True)
        if resp.status_code == 200 and 'image' in resp.headers.get('Content-Type', ''):
            return True
    except Exception:
        pass
    return False


def main():
    """Main function to fetch and save social media data"""
    # Fetch new data
    twitter_profile_new = get_twitter_profile()
    if not twitter_profile_new:
        twitter_profile_new = get_twitter_profile_alternative()
        if not twitter_profile_new:
            twitter_profile_new = get_twitter_profile_username()
            if not twitter_profile_new:
                print("Error: Unable to fetch Twitter profile data")
                twitter_profile_new = None

    instagram_profile_new = get_instagram_profile()
    if not instagram_profile_new:
        instagram_profile_new = None

    # Load existing data for fallback and image link comparison
    existing_data = load_existing_data()
    twitter_existing = existing_data.get("twitter", {})
    instagram_existing = existing_data.get("instagram", {})

    # Fallback image URLs (can be local or remote)
    twitter_fallback_img = "img/twitter.png"
    instagram_fallback_img = "img/instagram.png"

    # --- Twitter ---
    twitter_profile = twitter_profile_new.copy() if twitter_profile_new else twitter_existing.copy()
    old_twitter_img = twitter_existing.get("profile_image_url")
    new_twitter_img = twitter_profile_new.get("profile_image_url") if twitter_profile_new else None
    # If old image is accessible, keep it; else use new one (or fallback)
    if old_twitter_img and is_remote_image_accessible(old_twitter_img):
        twitter_profile["profile_image_url"] = old_twitter_img
    elif new_twitter_img:
        twitter_profile["profile_image_url"] = new_twitter_img
    else:
        twitter_profile["profile_image_url"] = twitter_fallback_img

    # --- Instagram ---
    instagram_profile = instagram_profile_new.copy() if instagram_profile_new else instagram_existing.copy()
    old_insta_img = instagram_existing.get("profile_image_url")
    new_insta_img = instagram_profile_new.get("profile_image_url") if instagram_profile_new else None
    if old_insta_img and is_remote_image_accessible(old_insta_img):
        instagram_profile["profile_image_url"] = old_insta_img
    elif new_insta_img:
        instagram_profile["profile_image_url"] = new_insta_img
    else:
        instagram_profile["profile_image_url"] = instagram_fallback_img

    # Save all other new fields from API (except image link logic above)
    data = {
        "twitter": twitter_profile,
        "instagram": instagram_profile
    }
    save_data(data)
    print("Social media data update complete!")


if __name__ == "__main__":
    main()