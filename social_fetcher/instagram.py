"""Instagram Graph API profile fetching and token refresh functions."""

import requests
from pathlib import Path

from . import config
from .config import SAVE_PROFILE_IMAGES
from .utils import download_image


def refresh_token():
    """Refresh the Instagram long-lived access token.

    Long-lived tokens expire after 60 days. This function refreshes the token
    and writes the new token to a file so the GitHub Actions workflow can
    persist it back to the repository secrets.

    Returns:
        The new access token string, or None if refresh failed.
    """
    if not config.INSTAGRAM_ACCESS_TOKEN:
        print("Skipping Instagram token refresh: no access token provided")
        return None

    try:
        print("Attempting to refresh Instagram access token...")
        url = (
            "https://graph.instagram.com/refresh_access_token"
            f"?grant_type=ig_refresh_token"
            f"&access_token={config.INSTAGRAM_ACCESS_TOKEN}"
        )
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        new_token = data.get("access_token")
        expires_in = data.get("expires_in", 0)

        if new_token:
            config.INSTAGRAM_ACCESS_TOKEN = new_token
            token_file = Path(".new_ig_token")
            token_file.write_text(new_token)
            days = expires_in // 86400
            print(f"Instagram token refreshed successfully (expires in {days} days)")
            return new_token
        else:
            print(f"Error: Unexpected refresh response: {data}")
            return None
    except Exception as e:
        print(f"Warning: Could not refresh Instagram token: {e}")
        print("The token may have expired. Please generate a new token manually.")
        return None


def get_profile():
    """Fetch comprehensive Instagram profile data.

    Returns:
        Instagram profile data dictionary or None if fetching failed.
    """
    if not config.INSTAGRAM_ACCESS_TOKEN:
        print("Error: Instagram API credentials not provided")
        return None

    try:
        print("Fetching Instagram profile data via API...")
        # Basic profile info
        url = f"https://graph.instagram.com/me?fields=username,name,media_count&access_token={config.INSTAGRAM_ACCESS_TOKEN}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        basic_data = response.json()
        if "username" not in basic_data:
            print(f"Error: Instagram API missing username field: {basic_data}")
            return None

        # Additional fields (followers, bio)
        url = f"https://graph.instagram.com/me?fields=followers_count,follows_count,biography&access_token={config.INSTAGRAM_ACCESS_TOKEN}"
        followers_response = requests.get(url, timeout=10)
        followers_data = {}
        if followers_response.status_code == 200:
            followers_data = followers_response.json()
        else:
            print(f"Warning: Couldn't fetch Instagram follower data: {followers_response.text}")

        profile_data = {
            "username": basic_data.get("username", ""),
            "name": basic_data.get("name", ""),
            "media_count": basic_data.get("media_count", 0),
            "biography": followers_data.get("biography", ""),
            "followers": followers_data.get("followers_count", 0),
            "following": followers_data.get("follows_count", 0)
        }

        # Profile picture
        try:
            pic_url = f"https://graph.instagram.com/me?fields=profile_picture_url&access_token={config.INSTAGRAM_ACCESS_TOKEN}"
            pic_response = requests.get(pic_url, timeout=10)
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
