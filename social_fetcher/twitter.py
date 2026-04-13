"""Twitter/X API profile fetching functions.

NOTE: As of 2024+, the X free API tier no longer supports reading user data.
These functions are retained for future use if the API tier is upgraded.
"""

import requests

from .config import TWITTER_BEARER_TOKEN, TWITTER_USER_ID, TWITTER_USERNAME, SAVE_PROFILE_IMAGES
from .utils import download_image


def fetch_twitter_profile(api_url, api_name="API", data_accessor=None):
    """Generic function to fetch Twitter profile data from various APIs.

    Args:
        api_url: The Twitter API URL to fetch data from.
        api_name: Name of the API for logging purposes.
        data_accessor: Function to extract user data from the response.

    Returns:
        Twitter profile data dictionary or None if fetching failed.
    """
    if not TWITTER_BEARER_TOKEN:
        print("Error: Twitter API credentials not provided")
        return None

    if data_accessor is None:
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

            if profile_data["profile_image_url"]:
                profile_data["profile_image_url"] = profile_data["profile_image_url"].replace("_normal", "_400x400")

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
    """Fetch Twitter profile data via primary API (by user ID)."""
    if not TWITTER_USER_ID:
        print("Error: Twitter user ID not provided")
        return None
    url = f"https://api.x.com/2/users/{TWITTER_USER_ID}?user.fields=name,username,description,profile_image_url,public_metrics"
    return fetch_twitter_profile(url, "primary API")


def get_twitter_profile_alternative():
    """Fetch Twitter profile data via alternative API (by user ID, batch endpoint)."""
    if not TWITTER_USER_ID:
        print("Error: Twitter user ID not provided")
        return None
    url = f"https://api.x.com/2/users?ids={TWITTER_USER_ID}&user.fields=name,username,description,profile_image_url,public_metrics"
    return fetch_twitter_profile(url, "alternative API", lambda d: d["data"][0])


def get_twitter_profile_username():
    """Fetch Twitter profile data via username API."""
    if not TWITTER_USERNAME:
        print("Error: Twitter username not provided")
        return None
    url = f"https://api.x.com/2/users/by/username/{TWITTER_USERNAME}?user.fields=name,username,description,profile_image_url,public_metrics"
    print("NOTE - This API depends on the username not being changed by the user.")
    print("If the username has changed, please update the username or attempt to use the user ID API instead.")
    return fetch_twitter_profile(url, "username API")
